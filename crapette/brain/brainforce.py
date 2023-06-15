"""IA for playing the crapette."""

import functools
import sys
from pprint import pprint

from kivy.logger import Logger

from crapette.core.board import Board, HashBoard
from crapette.core.moves import Move
from crapette.core.piles import FoundationPile, TableauPile, _PlayerPile

sys.setrecursionlimit(10**5)

# if os.name == "nt":
#     # Fix utf8 output in console
#     sys.stdout = open(1, "w", encoding="utf-8", closefd=False)  # fd 1 is stdout


class BrainForce:
    def __init__(self, board, player):
        self.board = board
        self.player = player

    def compute_states(self):
        Logger.debug("*" * 50)
        Logger.debug(f"compute_states for player {self.player}")

        best_node = BrainDijkstra(self.board, self.player).compute_search()
        print("Conclusion :")
        pprint(best_node.moves)
        print(flush=True)


class BoardNode:
    def __init__(self, board: HashBoard, player: int) -> None:
        self.board = board
        self.player = player

        self.cost: tuple = MAX_COST
        self.score = BoardScore(self.board, self.player).score
        self.visited: bool = False
        self.moves: list = []

    def search_neighbors(self, known_nodes: dict):
        # This one was searched
        self.visited = True

        # If last move was from a player pile, stop here
        if self.moves and isinstance(self.moves[-1].origin, _PlayerPile):
            return

        # Check all possible origin piles
        for pile_orig in self._piles_orig:
            card = pile_orig.top_card

            to_empty_tableau_before = False
            # Check all possible destination piles for each possible origin pile
            for pile_dest in self._piles_dest:
                # Skip "no move" move
                if pile_dest is pile_orig:
                    continue

                # Check if the move is possible
                if not pile_dest.can_add_card(card, pile_orig, self.player):
                    continue

                # Avoid equivalent moves with empty piles on the tableau
                if (
                    pile_dest.is_empty
                    and isinstance(pile_orig, TableauPile)
                    and isinstance(pile_dest, TableauPile)
                ):
                    if to_empty_tableau_before or len(pile_orig) == 1:
                        # Avoid trying each empty slot or swap empty slots
                        continue
                    to_empty_tableau_before = True

                # Instantiate neighbor
                next_board = HashBoard(self.board)
                next_board[pile_orig].pop_card()
                next_board[pile_dest].add_card(card)

                # Compute the cost
                move = Move(card, pile_orig, pile_dest)
                cost = (*self.cost, compute_move_cost(move))
                try:
                    next_board_node = known_nodes[next_board]
                except KeyError:
                    # Add this unknown new board
                    next_board_node = BoardNode(next_board, self.player)
                    known_nodes[next_board] = next_board_node
                else:
                    # Skip if cost is higher
                    if next_board_node.visited or cost > next_board_node.cost:
                        continue
                next_board_node.cost = cost
                next_board_node.moves = [*self.moves, move]

    @functools.cached_property
    def _piles_orig(self):
        """Piles to take cards from."""
        player_piles = self.board.players_piles[self.player]
        piles_orig = *self.board.tableau_piles, player_piles.crape, player_piles.stock

        # Return only piles with top card available
        return [p for p in piles_orig if not p.is_empty and p.face_up]

    @functools.cached_property
    def _piles_dest(self):
        """Piles to put cards to."""
        enemy_piles = self.board.players_piles[1 - self.player]
        return (
            self.board.foundation_piles
            + self.board.tableau_piles
            + [enemy_piles.crape, enemy_piles.waste]
        )


class BrainDijkstra:
    def __init__(self, board: Board, player: int) -> None:
        self.board = HashBoard(board)
        self.player = player

        # Initialize
        first_node = BoardNode(self.board, self.player)
        first_node.cost = ()
        first_node.moves = []
        self.known_nodes = {self.board: first_node}

    def _select_next_node(self) -> BoardNode | None:
        min_cost: tuple = MAX_COST
        next_node = None
        for node in self.known_nodes.values():
            if node.visited:
                continue
            if node.cost < min_cost:
                min_cost = node.cost
                next_node = node
        return next_node

    def compute_search(self):
        max_score = BoardScore.WORSE
        best_node = None

        next_node = self._select_next_node()
        while next_node is not None:
            next_node.search_neighbors(self.known_nodes)
            if next_node.score > max_score:
                max_score = next_node.score
                best_node = next_node

            next_node = self._select_next_node()
        return best_node


class BoardScore:
    WORSE = (-float("inf"),) * 11

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
