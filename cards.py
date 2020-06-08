import random


class Card:
    """Card information"""

    MIN_RANK = 1
    MAX_RANK = 13
    RANKS = list(range(MIN_RANK, MAX_RANK + 1))
    SUITS = "cdhs"  # Clubs, Diamonds, Hearts, Spades
    RED = "dh"  # Clubs, Diamonds, Hearts, Spades
    BLACK = "cs"  # Clubs, Diamonds, Hearts, Spades
    PLAYERS = [0, 1]

    def __init__(self, rank, suit, player, face_up=False):
        assert rank in self.RANKS
        assert suit in self.SUITS
        assert player in self.PLAYERS
        self._rank = rank
        self._suit = suit
        self._player = player
        self._face_up = bool(face_up)
        self._is_red = suit in self.RED

    @property
    def rank(self):
        return self._rank

    @property
    def suit(self):
        return self._suit

    @property
    def player(self):
        return self._player

    @property
    def face_up(self):
        return self._face_up

    @face_up.setter
    def face_up(self, is_face_up):
        self._face_up = bool(is_face_up)

    def is_same_color(self, other):
        return self._is_red == other._is_red

    def __str__(self):
        txt = f"{self._rank}{self._suit}"
        if self._face_up:
            txt += " up"
        return txt

    def image(self):
        # TODO: Customize cards
        if self._face_up:
            return f"images/face_{self._rank}{self._suit}.png"
        else:
            return f"images/deck{self._player}.png"


def new_deck(player):
    """Build a new shuffled deck"""
    assert player in [0, 1]
    cards = [Card(r, s, player) for s in Card.SUITS for r in Card.RANKS]
    random.shuffle(cards)
    return cards
