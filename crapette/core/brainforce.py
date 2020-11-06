# importing the sys module
from crapette.core.piles import (
    CrapePile,
    FoundationPile,
    TableauPile,
    WastePile,
    _PlayerPile,
)
import sys

# the setrecursionlimit function is
# used to modify the default recursion
# limit set by python. Using this,
# we can increase the recursion limit
# to satisfy our needs

sys.setrecursionlimit(10 ** 5)

from pprint import pprint

from .board import Board, Move

_DEBUG = True


def debug(*s):
    if _DEBUG:
        print(*s)


class BrainForce:
    def __init__(self, board, player):
        self.board = board
        self.player = player

    def compute_states(self):
        debug("*" * 50)
        debug(f"compute_states for player {self.player}")
        # Recursive state modifications
        states = {}
        self._recurse_states(states, self.board, [], "")
        print("states")
        pprint(states)

        # Score for each state
        scores = {b: BoardScore(b, self.player).score for b in states}
        print("scores")
        pprint(scores)
        max_score = max(scores.values())
        print("max score", max_score)

        # Boards with max score
        max_boards = [b for b, s in scores.items() if s == max_score]
        print("max boards")
        pprint(max_boards)

        # Boards with max score and less moves
        max_moves = [states[b] for b in max_boards]
        print("max moves")
        pprint(max_moves)
        nb_min_moves = min(len(m) for m in max_moves)
        print("max moves")
        bests_moves = [m for m in max_moves if len(m) == nb_min_moves]
        pprint(bests_moves)

        # Move with max score
        moves_score = MovesScore(bests_moves[0]).score
        best_moves = bests_moves[0]
        for moves in bests_moves[1:]:
            if MovesScore(moves).score > moves_score:
                best_moves = moves
        print("best moves")
        pprint(best_moves)
        print(flush=True)

    def _recurse_states(self, states: dict, board: Board, moves: list, alinea):
        debug(f"{alinea} recurse_states: {len(states)} states, {len(moves)} moves")
        # Check if this board was already taken into account
        try:
            # Keep shortest path and best score
            prev_moves = states[board]
        except KeyError:
            pass
        else:
            if len(moves) < len(prev_moves):
                debug(f"{alinea} board known but new path is shorter, rediscover paths")
            elif (
                len(moves) == len(prev_moves)
                and MovesScore(moves).score > MovesScore(prev_moves).score
            ):
                debug(
                    f"{alinea} board known but new path has better score, rediscover paths"
                )
            else:
                debug(f"{alinea} board already known with better move")
                return

        # Register this new board
        debug(f"{alinea} register board")
        states[board] = moves

        # Player move stops the recursion
        if moves and isinstance(moves[-1].origin, _PlayerPile):
            debug(f"{alinea} Player move, stop regression")
            return

        # Try possible moves fom this board
        piles_orig = board.tableau_piles + list(board.players_piles[self.player])
        piles_dest = (
            board.foundation_piles
            + board.tableau_piles
            + list(board.players_piles[1 - self.player])
        )
        for pile_orig in piles_orig:
            if pile_orig.is_empty:
                continue
            if not pile_orig.can_pop_card(self.player):
                continue
            if not pile_orig.face_up:
                continue

            card = pile_orig.top_card

            to_empty_tableau_before = False
            for pile_dest in piles_dest:
                if pile_dest == pile_orig:
                    continue
                if pile_dest.can_add_card(card, pile_orig, self.player):
                    if pile_dest.is_empty:
                        if isinstance(pile_orig, TableauPile) and isinstance(
                            pile_dest, TableauPile
                        ):
                            # Avoid trying each empty slot, it's useless
                            if to_empty_tableau_before:
                                debug(
                                    f"{alinea} skip move {card} from {pile_orig.name} to empty {pile_dest.name}: move to empty already done"
                                )
                                continue
                            elif len(pile_orig) == 1:
                                debug(
                                    f"{alinea} skip move {card} from {pile_orig.name} to empty {pile_dest.name}: would just swap empty slots"
                                )
                                continue
                            else:
                                to_empty_tableau_before = True
                        debug(
                            f"{alinea} move {card} from {pile_orig.name} to empty {pile_dest.name} and recurse"
                        )
                    else:
                        debug(
                            f"{alinea} move {card} from {pile_orig.name} to {pile_dest.name} over {pile_dest.top_card} and recurse"
                        )

                    # Board copy
                    next_board = board.copy()

                    # Get and move the card
                    next_board[pile_orig].pop_card()
                    next_board[pile_dest].add_card(card)

                    # Record the move
                    move = Move(card, pile_orig, pile_dest)
                    next_moves = moves + [move]

                    # Recurse the hell out of it
                    self._recurse_states(states, next_board, next_moves, "_" + alinea)


class BoardScore:
    WORSE = (float("inf"),) * 11

    def __init__(self, board: Board, player: int):
        self.board = board
        self.player = player

    @property
    def score(self):
        return (
            self.foundation_score,
            self.crapette_score,
            self.empty_tableau_score,
        ) + tuple(self.clean_tableau_score)

    @property
    def foundation_score(self):
        return sum(len(pile) for pile in self.board.foundation_piles)

    @property
    def crapette_score(self):
        return -len(self.board.players_piles[self.player].crape)

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


class MovesScore:
    def __init__(self, moves: list):
        self.moves = moves

    @property
    def score(self):
        return tuple(self.move_score(m) for m in self.moves)

    @staticmethod
    def move_score(move: Move):
        if isinstance(move.destination, FoundationPile):
            return move.destination._foundation_id + 8
        elif isinstance(move.destination, TableauPile):
            return move.destination._id
        elif isinstance(move.destination, WastePile):
            return -1
        elif isinstance(move.destination, CrapePile):
            return -2
