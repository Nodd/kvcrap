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
    SUIT_SYMBOL = {"c": "\u2663", "d": "\u2666", "h": "\u2665", "s": "\u2660"}
    RANK_SYMBOL = {1: "A", 11: "J", 12: "Q", 13: "K"}

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
        """Rank of the card, between MIN_RANK (1) and MAX_RANK (13)"""
        return self._rank

    @property
    def suit(self):
        """Caracter representing the suit of the card

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
    def player(self):
        """Original player for the card

        Useful to get the decoration on the back of the card.
        """
        return self._player

    @property
    def face_up(self):
        """State of the card, facing up (True) or down (False)"""
        return self._face_up

    @face_up.setter
    def face_up(self, is_face_up):
        """Setter for the satate of the card"""
        self._face_up = bool(is_face_up)

    def is_same_color(self, other):
        """Check if this card has the same color (red or black) as another card
        """
        return self._is_red == other._is_red

    def __str__(self):
        """Sting representation of the card"""
        txt = f"{self.rank_symbol}{self.suit_symbol}"
        if self._face_up:
            txt += " up"
        return txt

    def __repr__(self):
        return f"Card(rank={self.rank}, suit={self.suit}, player={self.player}, face_up={self.face_up})"

    def image(self):
        """Returns the image file for the card

        The returne image depends on the facing of the card.
        """
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
