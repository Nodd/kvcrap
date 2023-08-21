"""Class for card parameters and methods."""

import random


class Card:
    """Card information."""

    MIN_RANK = 1
    MAX_RANK = 13
    RANKS = list(range(MIN_RANK, MAX_RANK + 1))
    NB_RANKS = len(RANKS)
    RED = "dh"  # Diamonds, Hearts
    BLACK = "cs"  # Clubs, Spades
    SUITS = RED + BLACK
    NB_SUITS = len(SUITS)
    PLAYERS = (0, 1)
    SUIT_SYMBOL = {"c": "\u2663", "d": "\u2666", "h": "\u2665", "s": "\u2660"}
    RANK_SYMBOL = {1: "A", 10: "0", 11: "J", 12: "Q", 13: "K"}
    RANK_NAME = {1: "Ace", 11: "Jack", 12: "Queen", 13: "King"}

    __slots__ = ["_rank", "_suit", "_player", "_face_up", "_color", "_hash", "id"]

    def __init__(self, rank, suit, player):
        assert rank in self.RANKS
        assert suit in self.SUITS
        assert player in self.PLAYERS
        self._rank = rank
        self._suit = suit
        self._player = player
        self._face_up = False
        self._color = "r" if suit in self.RED else "b"
        self._hash = hash((self._rank, self._suit, self._player))
        # Like a hash, but uses only suit and rank
        self.id = ord(self._suit) * 100 + self._rank

    @property
    def rank(self):
        """Rank of the card, between MIN_RANK (1) and MAX_RANK (13)."""
        return self._rank

    @property
    def suit(self):
        """Caracter representing the suit of the card.

        - c: Clubs
        - d: Diamonds
        - h: Hearts
        - s: Spades
        """
        return self._suit

    @property
    def suit_symbol(self):
        return self.SUIT_SYMBOL[self._suit]

    @property
    def rank_symbol(self):
        try:
            return self.RANK_SYMBOL[self._rank]
        except KeyError:
            return str(self._rank)

    @property
    def rank_name(self):
        try:
            return self.RANK_NAME[self._rank]
        except KeyError:
            return str(self._rank)

    @property
    def player(self):
        """Original player for the card.

        Useful to get the decoration on the back of the card.
        """
        return self._player

    @property
    def face_up(self):
        """State of the card, facing up (True) or down (False)."""
        return self._face_up

    @face_up.setter
    def face_up(self, is_face_up):
        """Setter for the satate of the card."""
        self._face_up = bool(is_face_up)

    def is_same_color(self, other):
        """Check if this card has the same color (red or black) as another card."""
        return self._color == other._color

    def __str__(self):
        """Represent the card as a string."""
        return f"{self.rank_symbol}{self.suit_symbol}{'^' if self._face_up else 'v'}"

    @property
    def str_rank_suit(self):
        """Represent the card as a string with only symbol and suit."""
        return f"{self.rank_symbol}{self.suit_symbol}"

    def __repr__(self):
        # return f"Card(rank={self.rank}, suit={self.suit}, player={self.player}, face_up={self.face_up})"
        return self.__str__()

    def __eq__(self, other):
        return (
            self._rank == other._rank
            and self._suit == other._suit
            and self._player == other._player
        )

    def __lt__(self, other):
        if self._rank == other._rank:
            if self._suit == other._suit:
                return self._player < other._player
            return self._suit < other._suit
        return self._rank < other._rank

    def __hash__(self):
        return self._hash


def new_deck(player, shuffle=True):
    """Build a new shuffled deck.

    A deck is simply a list of Card instances.
    """
    assert player in (0, 1)
    cards = [Card(r, s, player) for s in Card.SUITS for r in Card.RANKS]
    if shuffle:
        random.shuffle(cards)
    return cards
