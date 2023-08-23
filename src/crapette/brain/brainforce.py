"""IA for playing the crapette."""

import dataclasses
import heapq
import sys
import timeit
from pprint import pprint
from typing import TYPE_CHECKING

from kivy.app import App
from kivy.logger import Logger
from line_profiler import profile

from crapette.core.board import Board, HashBoard
from crapette.core.cards import Card
from crapette.core.moves import Flip, FlipWaste, Move
from crapette.core.piles import (
    CrapePile,
    FoundationPile,
    Pile,
    StockPile,
    TableauPile,
    WastePile,
    _PlayerPile,
)

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
    filter_piles_orig: bool = True
    filter_piles_orig_aggressive: bool = True
    mono: bool = True
    print_progress: bool = False
    reproducible: bool = True


class BrainForce:
    def __init__(self, game_config: "GameConfig"):
        self.game_config = game_config

    def compute_states(self):
        Logger.debug("*" * 50)
        Logger.debug("compute_states for player %s", self.game_config.active_player)

        start_time = timeit.default_timer()
        moves, nb_nodes_visited = BrainDijkstra(self.game_config).compute_search()

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

        elapsed = timeit.default_timer() - start_time
        Logger.info(
            "AI time #%d: %gs for %d possibilities (%.3fms each on avearge)",
            self.game_config.step,
            elapsed,
            nb_nodes_visited,
            elapsed / nb_nodes_visited * 1000,
        )
        # print("Conclusion :")
        # pprint(moves)
        print(flush=True)
        return moves


class BoardNode:
    __slots__ = [
        "board",
        "player",
        "ai_config",
        "cost",
        "score",
        "score_min",
        "visited",
        "moves",
        "index",
    ]

    def __init__(self, board: HashBoard, player: int, ai_config) -> None:
        self.board = board
        self.player = player
        self.ai_config = ai_config

        self.cost: list[int] = [0, []]
        self.score = BoardScore(self.board, self.player).score
        self.score_min = tuple(-s for s in self.score)
        self.visited: bool = False
        self.moves: list[Move] = []

    def __lt__(self, other):
        """Compute the node cost.

        This is used in heapq to find the next node with a minimum distance.
        """
        return (
            self.score_min < other.score_min
            if self.cost == other.cost
            else self.cost < other.cost
        )

    @profile
    def search_neighbors(
        self,
        known_nodes: dict[HashBoard, "BoardNode"],
        known_nodes_unvisited: list["BoardNode"],  # Actually a heapq
    ):
        # This one was searched
        # Note: already popped from known_nodes_unvisited
        self.visited = True

        # If last move was from a player pile, stop here
        if self.moves and isinstance(self.moves[-1].origin, _PlayerPile):
            return

        foundation_dest, tableau_dest, enemy_dest = self.piles_dest()
        piles_dest = foundation_dest + tableau_dest + enemy_dest
        piles_orig = self.piles_orig(foundation_dest, tableau_dest, enemy_dest)

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

    @profile
    def register_next_board(self, move: Move, known_nodes, known_nodes_unvisited):
        # Instantiate neighbor
        next_board = HashBoard(self.board, move)

        cost = self.move_cost(move)
        try:
            next_board_node = known_nodes[next_board]
        except KeyError:
            pass
        else:
            # Known board, check if a lower cost was found
            # Skip if cost is higher or equal
            if next_board_node.visited or cost >= next_board_node.cost:
                return

            # Mark old BoardNode as visited instead of removing it from the heap, which is slow
            next_board_node.visited = True

        # Unknown board or new one in replacement
        next_board_node = BoardNode(next_board, self.player, self.ai_config)
        next_board_node.moves = [*self.moves, move]
        next_board_node.cost = cost
        known_nodes[next_board] = next_board_node
        heapq.heappush(known_nodes_unvisited, next_board_node)

    cost_destination_dict = {
        FoundationPile: 0,
        CrapePile: 1,
        WastePile: 2,
        TableauPile: 3,
    }
    cost_origin_dict = {
        TableauPile: 0,
        CrapePile: 1,
        StockPile: 2,
    }

    def move_cost(self, move):
        return [
            # The lowest the number of moves, the better
            len(self.moves),
            # Cost of previous moves, minus the number of moves
            *self.cost[1:],
            # Cost of this move
            (
                self.cost_destination_dict[type(move.destination)],
                self.cost_origin_dict[type(move.origin)],
            ),
        ]

    @profile
    def piles_orig(
        self,
        foundation_dest: list[FoundationPile],
        tableau_dest: list[TableauPile],
        enemy_dest: list[_PlayerPile],
    ) -> list[Pile]:
        """Piles to take cards from."""
        tableau_piles = [p for p in self.board.tableau_piles if not p.is_empty]

        if (
            self.ai_config.filter_piles_orig
            or self.ai_config.filter_piles_orig_aggressive
        ):
            # Look for potential interesting moves
            # Don't consider empty enemy or tableau piles as useful move
            tableau_dest = [p for p in tableau_dest if not p.is_empty]

            # Keeps only tableau piles containing card that could go elsewhere
            piles_accum = []
            if self.ai_config.filter_piles_orig_aggressive:
                non_tableau_dest = foundation_dest + enemy_dest
                for tableau_pile in tableau_piles:
                    for other_tableau_pile in tableau_dest:
                        if other_tableau_pile.can_add_card(
                            tableau_pile[0], tableau_pile, self.player
                        ):
                            piles_accum.append(tableau_pile)
                            break
                    else:
                        self._any_card_can_move(
                            tableau_pile, non_tableau_dest, piles_accum
                        )
            else:
                piles_dest = foundation_dest + enemy_dest + tableau_piles
                for tableau_pile in tableau_piles:
                    self._any_card_can_move(tableau_pile, piles_dest, piles_accum)

        else:
            piles_accum = tableau_piles

        # Add only player piles with top card available
        player_piles = self.board.players_piles[self.player]
        if not player_piles.crape.is_empty and player_piles.crape.face_up:
            piles_accum.append(player_piles.crape)
        if not player_piles.stock.is_empty and player_piles.stock.face_up:
            piles_accum.append(player_piles.stock)

        return piles_accum

    @profile
    def _any_card_can_move(
        self,
        tableau_pile: TableauPile,
        non_tableau_dest: list[Pile],
        piles_accum: list[Pile],
    ):
        for card in tableau_pile:
            for pile in non_tableau_dest:
                if pile.can_add_card(card, tableau_pile, self.player):
                    piles_accum.append(tableau_pile)
                    return

    @profile
    def piles_dest(self) -> tuple[list[Pile]]:
        """Piles to put cards to."""
        enemy_piles = self.board.players_piles[1 - self.player]
        tableau_piles = self.board.tableau_piles

        # Check only unique piles in tableau
        # An important case is multiple empty piles
        tableau_piles = set(tableau_piles)
        if self.ai_config.reproducible:
            tableau_piles = sorted(tableau_piles)
        else:
            tableau_piles = [*tableau_piles]

        # If both fondations are the same, keep only one
        foundation_piles_filtered = self.board.foundation_piles[: Card.NB_SUITS]
        for p1, p2 in zip(
            self.board.foundation_piles[Card.NB_SUITS :],
            self.board.foundation_piles[Card.NB_SUITS - 1 :: -1],
            strict=True,
        ):
            if len(p1) != len(p2):
                foundation_piles_filtered.append(p1)

        enemy_piles = [
            enemy_piles.crape,
            enemy_piles.waste,
        ]
        enemy_piles = [p for p in enemy_piles if not p.is_empty]

        return (
            foundation_piles_filtered,
            tableau_piles,
            enemy_piles,
        )


class BrainDijkstra:
    def __init__(self, game_config: "GameConfig") -> None:
        self.game_config = game_config
        self.app_config = App.get_running_app().app_config
        hash_board = HashBoard(self.game_config.board)

        # Initialize
        first_node = BoardNode(
            hash_board, self.game_config.active_player, self.app_config.ai
        )
        self.known_nodes = {hash_board: first_node}
        self.known_nodes_unvisited = []
        heapq.heappush(self.known_nodes_unvisited, first_node)

    def _select_next_node(self) -> BoardNode | None:
        try:
            while (board_node := heapq.heappop(self.known_nodes_unvisited)).visited:
                pass
        except IndexError:
            return None
        else:
            return board_node

    @profile
    def compute_search(self):
        max_score = BoardScore.WORSE
        best_node = None

        path = self.game_config.log_path.with_suffix("")
        path.mkdir(parents=True, exist_ok=True)
        path = path / f"log_{self.game_config.step:04d}.txt"

        # Optimize using local vars out of `while`
        do_shortcut = self.app_config.ai.shortcut
        print_progress = self.app_config.ai.print_progress
        known_nodes = self.known_nodes
        known_nodes_unvisited = self.known_nodes_unvisited

        next_node = self._select_next_node()
        nb_nodes_visited = 0
        with path.open("w") as f:
            while next_node is not None:
                nb_nodes_visited += 1
                next_node.search_neighbors(known_nodes, known_nodes_unvisited)
                next_node.index = nb_nodes_visited
                if next_node.score > max_score:
                    max_score = next_node.score
                    best_node = next_node

                if print_progress:
                    # print(next_node.board.to_text())
                    f.write(f"{nb_nodes_visited}\n")
                    f.write(next_node.board.to_text())
                    f.write(
                        f"\n{len(known_nodes)} known nodes\n{len(known_nodes_unvisited)} unvisited\n\n***\n\n"
                    )

                    print(
                        f"#{nb_nodes_visited}: {len(known_nodes)} known nodes, {len(known_nodes_unvisited)} unvisited, {len(next_node.moves)} moves (best: #{best_node.index}, {len(best_node.moves)} moves)",
                        end="\r",
                        flush=True,
                    )

                if do_shortcut:
                    for board_node in known_nodes_unvisited:
                        if not best_node.moves or (
                            not board_node.visited
                            and board_node.moves[0] != best_node.moves[0]
                        ):
                            break  # Break out of shortcut check loop
                    else:
                        break  # Break out of main loop if shortcut found

                next_node = self._select_next_node()

            if print_progress:
                print(" " * 80, end="\r")

            # Shortcut from app_config.ai.shortcut
            if known_nodes_unvisited:
                moves = [best_node.moves[0]]
                for index, move in enumerate(best_node.moves[1:]):
                    index += 1  # noqa: PLW2901
                    if all(
                        len(board_node.moves) > index
                        and board_node.moves[index] == move
                        for board_node in known_nodes_unvisited
                    ):
                        moves.append(move)
                    else:
                        break
                print("shortcut:", len(moves))
                f.write(f"shortcut: {len(moves)}\n")
            else:
                moves = best_node.moves

            f.write("\n")
            f.write("\n".join(str(move) for move in moves))
            f.write("\n\n")

        return moves, nb_nodes_visited


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
