"""Class for pile of cards parameters and methods."""

from typing import NamedTuple

from kivy.logger import LOG_LEVELS, Logger

from .cards import Card


if Logger.isEnabledFor(LOG_LEVELS["debug"]):
    logger_debug = Logger.debug
else:

    def logger_debug(*_args):
        pass


class Pile:
    """Defines the Pile interface and some generic methods for all piles."""

    __slots__ = ["_name", "_cards"]

    def __init__(self, name):
        self._name = str(name)
        self._cards: list[Card] = []

    def add_card(self, card):
        """Add a card to the pile."""
        self._cards.append(card)

    def pop_card(self):
        """Take the top card from the pile.

        No check is done here, see `can_pop_card`.
        """
        assert self._cards, f"No card to pop in {self._name}"
        return self._cards.pop()

    def can_add_card(self, card: Card, origin, player: int):
        """Check if the card can be added to the pile."""
        raise NotImplementedError

    def can_pop_card(self, player: int):
        """Check if the top card can be taken from the pile."""
        raise NotImplementedError

    def __iter__(self):
        yield from self._cards

    def __getitem__(self, index):
        """Index pile to get card."""
        return self._cards[index]

    def __len__(self):
        return len(self._cards)

    def __str__(self):
        return f"{self.name}[{' '.join(str(c) for c in self)}]"

    def __repr__(self):
        return self.__str__()

    def __lt__(self, other):
        assert type(self) == type(other)
        return self._cards < other._cards

    def __eq__(self, other):
        raise NotImplementedError

    @property
    def name(self):
        """Name of the pile."""
        return self._name

    @property
    def is_empty(self):
        return not len(self._cards)

    @property
    def top_card(self) -> Card | None:
        """Topmost card of the pile, or None if pile is empty."""
        try:
            return self._cards[-1]
        except IndexError:
            return None

    @property
    def rank(self):
        """Rank of the topmost card of the pile."""
        return self._cards[-1].rank

    @property
    def suit(self):
        """Suit of the topmost card of the pile."""
        return self._cards[-1].suit

    @property
    def player(self):
        """Initial player of the topmost card of the pile."""
        return self._cards[-1].player

    @property
    def face_up(self):
        """State of the topmost card of the pile."""
        return self._cards[-1].face_up

    @face_up.setter
    def face_up(self, is_face_up):
        """Setter of the state of the topmost card of the pile."""
        self._cards[-1].face_up = is_face_up

    def set_cards(self, cards):
        """Replace the cards in the pile.

        Warning, nothing is checked !
        """
        # TODO: Checks for each pile type
        self._cards = cards

    def clear(self):
        """Empty the pile."""
        self._cards = []

    def cards_ids(self):
        # It's a bit faster to create an intermediate list comprehension than a generator
        return tuple(c.id for c in self._cards)


class FoundationPile(Pile):
    """Pile in the center where the suites are build from Ace to King."""

    __slots__ = ["_foundation_id", "foundation_suit"]

    def __init__(self, suit, foundation_id):
        assert suit in Card.SUITS
        super().__init__(f"Foundation{foundation_id}{suit}")
        self._foundation_id = foundation_id
        self.foundation_suit = suit

    def can_add_card(self, card, origin, player):
        """Check if the card can be added to the pile.

        Card can be added if it has the same suit as the pile, and a rank just above the last card.
        """
        return card.suit == self.foundation_suit and card.rank == len(self._cards) + 1

    def can_pop_card(self, player):
        """Cards can never be removed from here.

        Note: except when rolling back in crapette mode, but that's not managed here.
        """
        return False

    @property
    def is_full(self):
        """If the pile is full from Ace to King."""
        return len(self._cards) == Card.MAX_RANK

    def __eq__(self, other):
        """Doesn't check if cards face up or down."""
        return (
            isinstance(other, FoundationPile)
            and self.foundation_suit == other.foundation_suit
            and len(self._cards) == len(other._cards)
        )


class TableauPile(Pile):
    """Side piles where cards go from King to Ace with alternate colors."""

    __slots__ = ["_id"]

    def __init__(self, tableau_id):
        super().__init__(f"Tableau{tableau_id}")
        self._id = tableau_id

    def can_add_card(self, card, origin, player):
        """Check if the card can be added to the pile.

        True if either the pile is empty or the color from the top card is
        different from the card color and the rank is just below.
        """
        return not self._cards or (
            not card.is_same_color(self.top_card)
            and card.rank == self.top_card.rank - 1
        )

    def can_pop_card(self, player):
        return True

    def __eq__(self, other):
        return isinstance(other, TableauPile) and self._cards == other._cards


class _PlayerPile(Pile):
    """Piles specific to the player."""

    _name_tpl = "_PilePlayer{player}"

    __slots__ = ["_player"]

    def __init__(self, player):
        assert player in {0, 1}
        super().__init__(self._name_tpl.format(player=player))
        self._player = player

    def can_pop_card(self, player):
        return player == self._player

    @property
    def player(self):
        return self._player

    def __eq__(self, other):
        """Doesn't check if cards face up or down."""
        return (
            isinstance(other, self.__class__)
            and self._name == other._name
            and self._cards == other._cards
        )


class StockPile(_PlayerPile):
    """Biggest and lowest priority of the 2 piles a player has to empty."""

    _name_tpl = "StockPlayer{player}"

    __slots__ = []

    def can_add_card(self, card, origin, player):
        """Check if the card can be added to the pile."""
        return False


class WastePile(_PlayerPile):
    """Pile where the player throws his card when he can not play anymore."""

    _name_tpl = "WastePlayer{player}"

    __slots__ = []

    def can_add_card(self, card: Card, origin, player):
        """Check if the card can be added to the pile."""
        if self._player == player:
            # Last move of the turn, the player puts the card from his stock to his waste
            return isinstance(origin, StockPile) and origin.player == player

        if self.is_empty:
            return False
        if card.suit != self.top_card.suit:
            return False
        rank = self.top_card.rank
        return card.rank in [rank - 1, rank + 1]

    def can_pop_card(self, player):
        return False


class CrapePile(_PlayerPile):
    """Smallest and high-priorty pile the player has to empty."""

    _name_tpl = "CrapePlayer{player}"
    NB_CARDS_START = 13

    __slots__ = []

    def can_add_card(self, card, origin, player):
        """Check if the card can be added to the pile."""
        if (
            self._player == player
            or self.is_empty
            or not self.top_card.face_up
            or card.suit != self.top_card.suit
        ):
            return False
        rank = self.top_card.rank
        return card.rank in [rank - 1, rank + 1]


class PlayerPiles(NamedTuple):
    """NamedTuple for all piles specific to a player."""

    stock: StockPile
    waste: WastePile
    crape: CrapePile


def player_piles(player):
    """Return a PlayerPiles instance with the 3 piles for a player."""
    return PlayerPiles(StockPile(player), WastePile(player), CrapePile(player))
