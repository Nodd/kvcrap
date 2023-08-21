"""IA for playing the crapette."""

import dataclasses
import sys
import timeit
from operator import attrgetter
from pprint import pprint
from typing import TYPE_CHECKING

from kivy.app import App
from kivy.logger import Logger

from crapette.core.board import Board, HashBoard
from crapette.core.cards import Card
from crapette.core.moves import Flip, FlipWaste, Move
from crapette.core.piles import FoundationPile, Pile, TableauPile, _PlayerPile

if TYPE_CHECKING:
    from crapette.game_manager import GameConfig

sys.setrecursionlimit(10**5)

# if os.name == "nt":
#     # Fix utf8 output in console
#     sys.stdout = open(1, "w", encoding="utf-8", closefd=False)  # fd 1 is stdout


class AIError(RuntimeError):
    pass


@dataclasses.dataclass
class BrainConfig:
    shortcut: bool = True
    mono: bool = True
    print_progress: bool = False


MAX_COST = float("inf")


class BrainForce:
    def __init__(self, game_config: "GameConfig"):
        self.game_config = game_config

    def compute_states(self):
        Logger.debug("*" * 50)
        Logger.debug("compute_states for player %s", self.game_config.active_player)

        start_time = timeit.default_timer()
        moves, nb_nodes = BrainDijkstra(self.game_config).compute_search()

        if not moves:
            player_piles = self.game_config.board.players_piles[
                self.game_config.active_player
            ]
            crape = player_piles.crape
            stock = player_piles.stock
            if crape and not crape.top_card.face_up:
                moves = [Flip(crape.top_card, crape)]
            elif not stock:
                moves = [FlipWaste()]
            elif not stock.top_card.face_up:
                moves = [Flip(stock.top_card, stock)]
            else:
                moves = [Move(stock.top_card, stock, player_piles.waste)]
            # TODO: manage the case of an empty stock and non-empty crape

        # elapsed = timeit.default_timer() - start_time
        # Logger.info(
        #     "AI time: %gs for %d possibilities (%.3fms each on avearge)",
        #     elapsed,
        #     nb_nodes,
        #     elapsed / nb_nodes * 1000,
        # )
        # print("Conclusion :")
        # pprint(moves)
        # print(flush=True)
        return moves


class BoardNode:
    __slots__ = [
        "board",
        "player",
        "cost",
        "score",
        "score_min",
        "visited",
        "moves",
        "index",
    ]

    def __init__(self, board: HashBoard, player: int) -> None:
        self.board = board
        self.player = player

        self.cost = MAX_COST
        self.score = BoardScore(self.board, self.player).score
        self.score_min = tuple(-s for s in self.score)
        self.visited: bool = False
        self.moves: list[Move] = []

    def search_neighbors(
        self,
        known_nodes: dict[HashBoard, "BoardNode"],
        known_nodes_unvisited: dict[HashBoard, "BoardNode"],
    ):
        # This one was searched
        self.visited = True
        del known_nodes_unvisited[self.board]

        # If last move was from a player pile, stop here
        if self.moves and isinstance(self.moves[-1].origin, _PlayerPile):
            return

        foundation_dest, other_dest = self.piles_dest()
        piles_dest = foundation_dest + other_dest
        piles_orig = self.piles_orig(foundation_dest, other_dest)

        # Check all possible origin piles
        for pile_orig in piles_orig:
            card = pile_orig.top_card

            # Precomputations
            is_pile_orig_one_card_tableau = len(pile_orig) == 1 and isinstance(
                pile_orig, TableauPile
            )

            # Check all possible destination piles for each possible origin pile
            for pile_dest in piles_dest:
                # Check if the move is possible
                if not pile_dest.can_add_card(card, pile_orig, self.player):
                    continue

                # Avoid noop move
                if pile_dest.name == pile_orig.name:
                    continue

                # Avoid equivalent moves with empty piles on the tableau
                # It's an important optimization when there are multiple empty piles on the tableau
                if (
                    is_pile_orig_one_card_tableau
                    and pile_dest.is_empty
                    and isinstance(pile_dest, TableauPile)
                ):
                    continue

                # Do not undo the previous move
                if (
                    self.moves
                    and self.moves[-1].destination.name == pile_orig.name
                    and self.moves[-1].origin.name == pile_dest.name
                ):
                    continue

                self.register_next_board(
                    Move(card, pile_orig, pile_dest), known_nodes, known_nodes_unvisited
                )

    def register_next_board(self, move: Move, known_nodes, known_nodes_unvisited):
        # Instantiate neighbor
        next_board = self.board.with_move(move)
        hash(next_board)

        # Compute the cost
        cost = self.cost + (0 if isinstance(move.destination, FoundationPile) else 1)
        try:
            next_board_node = known_nodes[next_board]
        except KeyError:
            # Add this unknown new board
            next_board_node = BoardNode(next_board, self.player)
            known_nodes[next_board] = next_board_node
            known_nodes_unvisited[next_board] = next_board_node
        else:
            # Skip if cost is higher or equal (best moves are tried first)
            if next_board_node.visited or cost >= next_board_node.cost:
                return
        next_board_node.cost = cost
        next_board_node.moves = [*self.moves, move]
        next_board_node.board = next_board  # Keep board synchronized with moves, to avoid conflicts between equivalenrt but different boards

    def piles_orig(self, foundation_dest: list[FoundationPile], other_dest: list[Pile]):
        """Piles to take cards from."""
        # Look for potential interesting moves
        # Don't consider empty enemy or tableau piles as useful move
        other_dest = [p for p in other_dest if not p.is_empty]
        piles_dest = foundation_dest + other_dest
        tableau_piles = [p for p in self.board.tableau_piles if not p.is_empty]

        # Keeps only tableau piles containing card that could go elsewhere
        piles_accum = []
        for tableau_pile in tableau_piles:
            self._any_card_can_move(tableau_pile, piles_dest, piles_accum)

        # Consider first the piles where the card can go on the foundation,
        # then the smallest piles
        piles_accum.sort(
            key=lambda pile: (
                any(
                    not p.can_add_card(pile.top_card, pile, self.player)
                    for p in foundation_dest
                ),
                len(pile),
            ),
        )

        # Add only player piles with top card available
        player_piles = self.board.players_piles[self.player]
        if not player_piles.crape.is_empty and player_piles.crape.face_up:
            piles_accum.append(player_piles.crape)
        if not player_piles.stock.is_empty and player_piles.stock.face_up:
            piles_accum.append(player_piles.stock)

        return piles_accum

    def _any_card_can_move(
        self, tableau_pile: TableauPile, piles_dest: list[Pile], piles_accum: list[Pile]
    ):
        for card in tableau_pile:
            for pile in piles_dest:
                if pile.can_add_card(card, tableau_pile, self.player):
                    piles_accum.append(tableau_pile)
                    return

    def piles_dest(self):
        """Piles to put cards to."""
        enemy_piles = self.board.players_piles[1 - self.player]
        tableau_piles = self.board.tableau_piles

        # Check only unique piles in tableau
        # An important case is multiple empty piles
        tableau_piles_filtered = []
        for p in tableau_piles:
            for p2 in tableau_piles_filtered:
                if p._cards == p2._cards:
                    break
            else:
                tableau_piles_filtered.append(p)
        tableau_piles_filtered.sort(key=len, reverse=True)  # Try big piles first

        # If both fondations are the same, keep only one
        foundation_piles_filtered = self.board.foundation_piles[: Card.NB_SUITS]
        for p1, p2 in zip(
            self.board.foundation_piles[Card.NB_SUITS :],
            self.board.foundation_piles[Card.NB_SUITS - 1 :: -1],
            strict=True,
        ):
            if p1 != p2:
                foundation_piles_filtered.append(p1)

        return foundation_piles_filtered, [
            *tableau_piles_filtered,
            enemy_piles.crape,
            enemy_piles.waste,
        ]


class BrainDijkstra:
    def __init__(self, game_config: "GameConfig") -> None:
        self.game_config = game_config
        hash_board = HashBoard(self.game_config.board)

        # Initialize
        first_node = BoardNode(hash_board, self.game_config.active_player)
        first_node.cost = 0
        first_node.moves = []
        self.known_nodes = {hash_board: first_node}
        self.known_nodes_unvisited = {hash_board: first_node}

    def _select_next_node(self) -> BoardNode | None:
        return min(
            self.known_nodes_unvisited.values(),
            default=None,
            key=attrgetter("cost", "score_min"),
        )

    def compute_search(self):
        app_config = App.get_running_app().app_config
        max_score = BoardScore.WORSE
        best_node = None

        path = self.game_config.log_path.with_suffix("")
        path.mkdir(parents=True, exist_ok=True)
        path = path / f"log_{self.game_config.step:04d}.txt"

        next_node = self._select_next_node()
        nb_nodes = 0
        with path.open("w") as f:
            while next_node is not None:
                nb_nodes += 1
                next_node.search_neighbors(self.known_nodes, self.known_nodes_unvisited)
                next_node.index = nb_nodes
                if next_node.score > max_score:
                    max_score = next_node.score
                    best_node = next_node

                # print(next_node.board.to_text())
                f.write(f"{nb_nodes}\n")
                f.write(next_node.board.to_text())
                f.write(
                    f"\n{len(self.known_nodes)} known nodes\n{len(self.known_nodes_unvisited)} unvisited\n\n***\n\n"
                )

                if app_config.ai.print_progress:
                    print(
                        f"#{nb_nodes}: {len(self.known_nodes)} known nodes, {len(self.known_nodes_unvisited)} unvisited, {len(next_node.moves)} moves (best: #{best_node.index}, {len(best_node.moves)} moves)",
                        end="\r",
                        flush=True,
                    )

                if app_config.ai.shortcut:
                    for board_node in self.known_nodes_unvisited.values():
                        if (
                            not best_node.moves
                            or board_node.moves[0] != best_node.moves[0]
                        ):
                            break
                    else:
                        break

                next_node = self._select_next_node()

            if app_config.ai.print_progress:
                print(" " * 80, end="\r")

            # Shortcut from app_config.ai.shortcut
            if self.known_nodes_unvisited:
                moves = [best_node.moves[0]]
                for index, move in enumerate(best_node.moves[1:]):
                    index += 1  # noqa: PLW2901
                    if all(
                        len(board_node.moves) > index
                        and board_node.moves[index] == move
                        for board_node in self.known_nodes_unvisited.values()
                    ):
                        moves.append(move)
                print("shortcut:", len(moves))
                f.write(f"shortcut: {len(moves)}\n")
            else:
                moves = best_node.moves

            f.write("\n")
            f.write("\n".join(str(move) for move in moves))
            f.write("\n\n")

        return best_node.moves, nb_nodes


class BoardScore:
    WORSE = (-float("inf"),) * 12
    __slots__ = ["board", "player"]

    def __init__(self, board: Board, player: int):
        self.board = board
        self.player = player

    @property
    def score(self):
        return (
            self.foundation_score,
            self.crapette_score,
            self.stock_score,
            self.empty_tableau_score,
            *self.clean_tableau_score,
        )

    @property
    def foundation_score(self):
        return sum(len(pile) for pile in self.board.foundation_piles)

    @property
    def crapette_score(self):
        return -len(self.board.players_piles[self.player].crape)

    @property
    def stock_score(self):
        return -len(self.board.players_piles[self.player].stock)

    @property
    def empty_tableau_score(self):
        return sum(pile.is_empty for pile in self.board.tableau_piles)

    @property
    def clean_tableau_score(self):
        return sorted((len(pile) for pile in self.board.tableau_piles), reverse=True)
