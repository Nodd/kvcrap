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

    __slots__ = [
        "rank",
        "suit",
        "player",
        "_face_up",
        "_color",
        "_hash_cache",
        "suit_symbol",
        "rank_symbol",
        "rank_name",
        "str_rank_suit",
    ]

    def __init__(self, rank, suit, player):
        assert rank in self.RANKS
        assert suit in self.SUITS
        assert player in self.PLAYERS
        self.rank = rank
        self.suit = suit
        self.player = player
        self._face_up = False
        self._color = "r" if suit in self.RED else "b"
        self._hash_cache = hash((self.rank, self.suit))

        self.suit_symbol = self.SUIT_SYMBOL[self.suit]
        self.rank_symbol = self.RANK_SYMBOL.get(self.rank, self.rank)
        self.rank_name = self.RANK_NAME.get(self.rank, str(self.rank))
        self.str_rank_suit = f"{self.rank_symbol}{self.suit_symbol}"

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

    def __repr__(self):
        # return f"Card(rank={self.rank}, suit={self.suit}, player={self.player}, face_up={self.face_up})"
        return self.__str__()

    def __hash__(self):
        return self._hash_cache

    def __eq__(self, other):
        return (
            self.rank == other.rank
            and self.suit == other.suit
            and self.player == other.player
        )

    def __lt__(self, other):
        if self.rank == other.rank:
            if self.suit == other.suit:
                return self.player < other.player
            return self.suit < other.suit
        return self.rank < other.rank


def new_deck(player, shuffle=True):
    """Build a new shuffled deck.

    A deck is simply a list of Card instances.
    """
    assert player in (0, 1)
    cards = [Card(r, s, player) for s in Card.SUITS for r in Card.RANKS]
    if shuffle:
        random.shuffle(cards)
    return cards
