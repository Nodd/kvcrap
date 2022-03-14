from collections import namedtuple

Move = namedtuple("Move", ["card", "origin", "destination"])
Flip = namedtuple("Flip", ["card", "pile"])
FlipWaste = namedtuple("FlipWaste", [])


class Moves:
    """Manages a series of moves."""

    MOVE = "move"
    FLIP = "flip"
    WASTE_FLIP = "waste_flip"

    def __init__(self):
        self._prev_moves = []
        self._next_moves = []  # For crapette mode

    def reset(self):
        self._prev_moves = []
        self._next_moves = []

    def record_move(self, card, origin, destination):
        self._prev_moves.append(Move(card, origin, destination))

    def record_flip(self, card, pile):
        self._prev_moves.append(Flip(card, pile))

    def record_waste_flip(self):
        self._prev_moves.append(FlipWaste())

    @property
    def has_prev(self):
        return bool(self._prev_moves)

    @property
    def has_next(self):
        return bool(self._next_moves)

    def prev(self):
        if not self._prev_moves:
            return None
        move = self._prev_moves.pop()
        self._next_moves.append(move)
        return move

    def next(self):
        if not self._next_moves:
            return None
        move = self._next_moves.pop()
        self._prev_moves.append(move)
        return move
