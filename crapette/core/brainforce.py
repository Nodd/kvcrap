# importing the sys module
from crapette.core.piles import TableauPile
import sys

# the setrecursionlimit function is
# used to modify the default recursion
# limit set by python. Using this,
# we can increase the recursion limit
# to satisfy our needs

sys.setrecursionlimit(10 ** 5)

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
        # Start recursive state modifications
        self._recurse_states({}, self.board, [], "")

    def _recurse_states(self, states: dict, board: Board, moves: list, alinea):
        debug(f"{alinea}recurse_states: {len(states)} states, {len(moves)} moves")
        # Check if this board was already taken into account
        if board in states:
            # Keep shortest path
            # TODO : add another metric for same length paths ?
            if len(states[board]) > len(moves):
                debug(f"{alinea}  board known but path shorter")
                states[board] = moves
            else:
                debug(f"{alinea}  board already known")
            return

        # Register this new board
        debug(f"{alinea}  register board")
        states[board] = moves
        # for b in states:
        #     print("-", hash(b))

        # Try possible moves fom this board
        for pile_orig in board.piles:
            if pile_orig.is_empty:
                # print(f"{alinea}  {pile_orig.name} is empty")
                continue
            if not pile_orig.can_pop_card(self.player):
                # print(f"{alinea}  {pile_orig.name} not poppable")
                continue
            if not pile_orig.face_up:
                # print(f"{alinea}  {pile_orig.name} not flipped")
                continue

            card = pile_orig.top_card
            # print(f"{alinea}  take {card} from {pile_orig.name}")

            to_empty_tableau_before = False
            for pile_dest in board.piles:
                if (
                    pile_dest == pile_orig
                    or pile_dest.name == f"WastePlayer{self.player}"
                ):
                    continue
                if pile_dest.can_add_card(card, pile_orig, self.player):
                    if pile_dest.is_empty:
                        if isinstance(pile_dest, TableauPile):
                            # Avoid trying each empty slot, it's useless
                            if to_empty_tableau_before:
                                print(
                                    f"{alinea}    skip move {card} from {pile_orig.name} to empty {pile_dest.name}: move to empty already done"
                                )
                                continue
                            elif (
                                isinstance(pile_orig, TableauPile)
                                and len(pile_orig) == 1
                            ):
                                print(
                                    f"{alinea}    skip move {card} from {pile_orig.name} to empty {pile_dest.name}: would just swap empty slots"
                                )
                                continue
                            else:
                                to_empty_tableau_before = True
                        print(
                            f"{alinea}    move {card} from {pile_orig.name} to empty {pile_dest.name} and recurse"
                        )
                    else:
                        print(
                            f"{alinea}    move {card} from {pile_orig.name} to {pile_dest.name} over {pile_dest.top_card} and recurse"
                        )

                    # Board copy
                    next_board = board.copy()

                    # Get and move the card
                    next_board[pile_orig].pop_card()
                    next_board[pile_dest].add_card(card)

                    # Record the move
                    move = Move(card, pile_orig.name, pile_dest.name)
                    next_moves = moves + [move]

                    # Recurse the hell out of it
                    self._recurse_states(states, next_board, next_moves, "_" + alinea)
