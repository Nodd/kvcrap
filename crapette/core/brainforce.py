"""IA for playing the crapette"""

import os
import sys
from pprint import pprint

from .board import Board, Move
from .piles import CrapePile, FoundationPile, TableauPile, WastePile, _PlayerPile

sys.setrecursionlimit(10 ** 5)
_DEBUG = False
if os.name == "nt":
    # Fix utf8 output in console
    sys.stdout = open(1, "w", encoding="utf-8", closefd=False)  # fd 1 is stdout


class BrainForce:
    def __init__(self, board, player):
        self.board = board
        self.player = player

    def compute_states(self):
        if _DEBUG:
            print("*" * 50)
            print(f"compute_states for player {self.player}")

        best_node = BrainDjikstra(self.board, self.player).compute_search()
        print("Conclusion :")
        pprint(best_node.moves)
        print(flush=True)
        return


class BoardNode:
    def __init__(self, board: Board, player: int) -> None:
        self.board = board
        self.player = player

        self.cost = MAX_COST
        self.score = BoardScore(self.board, self.player).score
        self.visited = False
        self.moves = None

    def search_neighbors(self, known_nodes: dict):
        # This one was searched
        self.visited = True

        # If last move was from a player pile, stop here
        if self.moves and isinstance(self.moves[-1].origin, _PlayerPile):
            return

        # Piles to take from
        player_piles = self.board.players_piles[self.player]
        piles_orig = self.board.tableau_piles + [player_piles.crape, player_piles.stock]

        # Piles to push to
        enemy_piles = self.board.players_piles[1 - self.player]
        piles_dest = (
            self.board.foundation_piles
            + self.board.tableau_piles
            + [enemy_piles.crape, enemy_piles.waste]
        )

        # Check all orgin piles
        for pile_orig in piles_orig:
            # Consider top card if available
            if pile_orig.is_empty:
                continue
            if not pile_orig.face_up:
                continue
            card = pile_orig.top_card

            to_empty_tableau_before = False
            # Check all destination piles for each origin pile
            for pile_dest in piles_dest:
                # Skip "no move" move
                if pile_dest is pile_orig:
                    continue

                # Check if the move is possible
                if pile_dest.can_add_card(card, pile_orig, self.player):
                    # Avoid equivalent moves with empty piles on the tableau
                    if (
                        pile_dest.is_empty
                        and isinstance(pile_orig, TableauPile)
                        and isinstance(pile_dest, TableauPile)
                    ):
                        if to_empty_tableau_before:
                            # Avoid trying each empty slot, it's useless
                            continue
                        elif len(pile_orig) == 1:
                            # Woud just swap empty slots
                            continue
                        else:
                            to_empty_tableau_before = True

                    # Instanciate neighbor
                    next_board = self.board.copy()
                    next_board[pile_orig].pop_card()
                    next_board[pile_dest].add_card(card)

                    # Compute the cost
                    move = Move(card, pile_orig, pile_dest)
                    cost = self.cost + (compute_move_cost(move),)
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
                    next_board_node.moves = self.moves + [move]


class BrainDjikstra:
    def __init__(self, board: Board, player: int) -> None:
        self.board = board
        self.player = player

        # Initialize
        first_node = BoardNode(self.board, self.player)
        first_node.cost = ()
        first_node.moves = []
        self.known_nodes = {self.board: first_node}

    def _select_next_node(self) -> BoardNode:
        min_cost = MAX_COST
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
        ) + tuple(self.clean_tableau_score)

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
        empty_slot = 0
        for pile in self.board.tableau_piles:
            if pile.is_empty:
                empty_slot += 1
        return empty_slot

    @property
    def clean_tableau_score(self):
        return sorted((len(pile) for pile in self.board.tableau_piles), reverse=True)


MAX_COST = (float("inf"),)


def compute_move_cost(move: Move):
    if isinstance(move.destination, FoundationPile):
        cost = 0
    else:
        cost = 1
    return cost


def compute_moves_cost(moves):
    return tuple(compute_move_cost(m) for m in moves)
