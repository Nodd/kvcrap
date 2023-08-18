"""IA for playing the crapette."""

import sys
import timeit
from datetime import datetime
from operator import attrgetter
from pathlib import Path
from pprint import pprint

from kivy.app import App
from kivy.logger import Logger

from crapette.core.board import Board, HashBoard
from crapette.core.cards import Card
from crapette.core.moves import Flip, FlipWaste, Move
from crapette.core.piles import FoundationPile, Pile, TableauPile, _PlayerPile

sys.setrecursionlimit(10**5)

# if os.name == "nt":
#     # Fix utf8 output in console
#     sys.stdout = open(1, "w", encoding="utf-8", closefd=False)  # fd 1 is stdout


class BrainForce:
    def __init__(self, board: Board, player: int):
        self.board = board
        self.player = player

    def compute_states(self):
        Logger.debug("*" * 50)
        Logger.debug("compute_states for player %s", self.player)

        start_time = timeit.default_timer()
        best_node, nb_nodes = BrainDijkstra(self.board, self.player).compute_search()
        moves = best_node.moves

        if not moves:
            player_piles = self.board.players_piles[self.player]
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
            "AI time: %gs for %d possibilities (%.3fms each on avearge)",
            elapsed,
            nb_nodes,
            elapsed / nb_nodes * 1000,
        )
        print("Conclusion :")
        pprint(moves)
        print(flush=True)
        return moves


class BoardNode:
    __slots__ = ["board", "player", "cost", "score", "visited", "moves"]

    def __init__(self, board: HashBoard, player: int) -> None:
        self.board = board
        self.player = player

        self.cost: tuple = MAX_COST
        self.score = BoardScore(self.board, self.player).score
        self.visited: bool = False
        self.moves: list = []

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

        piles_dest = self.piles_dest()
        piles_orig = self.piles_orig(piles_dest)

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

    def register_next_board(self, move, known_nodes, known_nodes_unvisited):
        # Instantiate neighbor
        next_board = self.board.with_move(move)
        hash(next_board)

        # Compute the cost
        cost = (*self.cost, compute_move_cost(move))
        try:
            next_board_node = known_nodes[next_board]
        except KeyError:
            # Add this unknown new board
            next_board_node = BoardNode(next_board, self.player)
            known_nodes[next_board] = next_board_node
            known_nodes_unvisited[next_board] = next_board_node
        else:
            # Skip if cost is higher
            if next_board_node.visited or cost > next_board_node.cost:
                return
        next_board_node.cost = cost
        next_board_node.moves = [*self.moves, move]

    def piles_orig(self, piles_dest: list[Pile]):
        """Piles to take cards from."""
        # Consider only tableau piles containing card that could go elsewhere
        piles_dest = [p for p in piles_dest if not p.is_empty]
        tableau_piles = (p for p in self.board.tableau_piles if not p.is_empty)
        piles_orig = []

        for tableau_pile in tableau_piles:
            self._any_card_can_move(tableau_pile, piles_dest, piles_orig)

        # Add only player piles with top card available
        player_piles = self.board.players_piles[self.player]
        if not player_piles.crape.is_empty and player_piles.crape.face_up:
            piles_orig.append(player_piles.crape)
        if not player_piles.stock.is_empty and player_piles.stock.face_up:
            piles_orig.append(player_piles.stock)

        return piles_orig

    def _any_card_can_move(self, tableau_pile, piles_dest, piles_orig):
        for card in tableau_pile:
            for pile in piles_dest:
                if pile.can_add_card(card, tableau_pile, self.player):
                    piles_orig.append(tableau_pile)
                    return

    def piles_dest(self):
        """Piles to put cards to."""
        enemy_piles = self.board.players_piles[1 - self.player]
        tableau_piles = self.board.tableau_piles

        # Check only one empty pile in tableau since all empty piles are equivalent
        tableau_piles_filtered = []
        has_empty = False
        for p in tableau_piles:
            if p.is_empty:
                if has_empty:
                    continue
                has_empty = True
            tableau_piles_filtered.append(p)

        # If both fondations are the same, keep only one
        foundation_piles_filtered = self.board.foundation_piles[: Card.NB_SUITS]
        for p1, p2 in zip(
            self.board.foundation_piles[Card.NB_SUITS :],
            self.board.foundation_piles[Card.NB_SUITS - 1 :: -1],
            strict=True,
        ):
            if p1 != p2:
                foundation_piles_filtered.append(p1)

        return [
            *foundation_piles_filtered,
            *tableau_piles_filtered,
            enemy_piles.crape,
            enemy_piles.waste,
        ]


class BrainDijkstra:
    def __init__(self, board: Board, player: int) -> None:
        hash_board = HashBoard(board)

        # Initialize
        first_node = BoardNode(hash_board, player)
        first_node.cost = ()
        first_node.moves = []
        self.known_nodes = {hash_board: first_node}
        self.known_nodes_unvisited = {hash_board: first_node}

    def _select_next_node(self) -> BoardNode | None:
        return min(
            self.known_nodes_unvisited.values(), default=None, key=attrgetter("cost")
        )

    def compute_search(self):
        max_score = BoardScore.WORSE
        best_node = None

        app = App.get_running_app()
        path = Path(__file__).parent / "log" / str(app.current_seed)
        path.mkdir(parents=True, exist_ok=True)
        path = path / f"log_{datetime.now()}.txt"

        next_node = self._select_next_node()
        nb_nodes = 0
        with path.open("w") as f:
            while next_node is not None:
                # print(next_node.board.to_text())
                f.write(f"{nb_nodes}\n")
                f.write(next_node.board.to_text())
                f.write("\n\n***\n\n")
                next_node.search_neighbors(self.known_nodes, self.known_nodes_unvisited)
                if next_node.score > max_score:
                    max_score = next_node.score
                    best_node = next_node

                next_node = self._select_next_node()
                nb_nodes += 1
        return best_node, nb_nodes


class BoardScore:
    WORSE = (-float("inf"),) * 11
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


MAX_COST = (float("inf"),)


def compute_move_cost(move: Move):
    return 0 if isinstance(move.destination, FoundationPile) else 1


def compute_moves_cost(moves):
    return tuple(compute_move_cost(m) for m in moves)
