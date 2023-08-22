"""Class for pile of cards parameters and methods."""

from typing import NamedTuple

from kivy.logger import LOG_LEVELS, Logger

from .cards import Card

if Logger.isEnabledFor(LOG_LEVELS["debug"]):
    logger_debug = Logger.debug
else:

    def logger_debug(*_args):
        pass


class NotFrozenError(ValueError):
    pass


class FrozenError(ValueError):
    pass


class Pile:
    """Defines the Pile interface and some generic methods for all piles."""

    __slots__ = ["name", "_cards", "_frozen", "_hash_cache"]

    def __init__(self, name):
        self.name = str(name)
        self._cards: list[Card] = []
        self._frozen = False
        self._hash_cache = None

    def _new(self):
        raise NotImplementedError

    def copy(self, cards: list[Card] | None = None) -> "Pile":
        """Return a copy of the pile, with a new list of cards if given."""
        new = self._new()
        if cards is None:
            cards = [*self._cards]
        new._cards = cards
        if self._frozen:
            new.freeze()
        return new

    def add_card(self, card):
        """Add a card to the pile."""
        if self._frozen:
            raise FrozenError(f"Can not add card to frozen {self}.")
        self._cards.append(card)

    def pop_card(self):
        """Take the top card from the pile.

        No check is done here, see `can_pop_card`.
        """
        if self._frozen:
            raise FrozenError(f"Can not pop card from frozen {self}.")
        assert self._cards, f"No card to pop in {self.name}"
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
        return f"{self.name}[{' '.join(c.str_rank_suit for c in self if c.face_up)}]"

    def __repr__(self):
        return self.__str__()

    def __lt__(self, other):
        assert type(self) == type(other)
        if len(self) == len(other):
            return self._cards < other._cards
        return len(self) < len(other)

    def __eq__(self, other):
        return type(self) == type(other) and self._cards == other._cards

    def freeze(self):
        self._frozen = True
        self._hash_cache = self._compute_hash()

    def _compute_hash(self):
        return hash(tuple(self._cards))

    def __hash__(self):
        if not self._frozen:
            raise NotFrozenError(f"{self} is not hashable (not frozen)")
        return self._hash_cache

    @property
    def is_empty(self):
        return not bool(self._cards)

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
        if self._frozen:
            raise FrozenError(f"Can not pop card from frozen {self}.")
        self._cards = cards

    def clear(self):
        """Empty the pile."""
        self._cards = []


class FoundationPile(Pile):
    """Pile in the center where the suites are build from Ace to King."""

    __slots__ = ["foundation_id", "foundation_suit"]

    def __init__(self, suit, foundation_id):
        assert suit in Card.SUITS
        super().__init__(f"Foundation{foundation_id}{suit}")
        self.foundation_id = foundation_id
        self.foundation_suit = suit

    def _new(self):
        return FoundationPile(self.foundation_suit, self.foundation_id)

    def copy(self, cards: list[Card] | None = None) -> "FoundationPile":
        """Return a copy of the pile, with a new set of cards."""
        new = super().copy(cards)
        new.foundation_suit = self.foundation_suit
        return new

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

    # __eq__ is redefined, need to redefine __hash__ too
    __hash__ = Pile.__hash__

    def _compute_hash(self):
        return hash((self.foundation_suit, len(self._cards)))


class TableauPile(Pile):
    """Side piles where cards go from King to Ace with alternate colors."""

    __slots__ = ["tableau_id"]

    def __init__(self, tableau_id):
        super().__init__(f"Tableau{tableau_id}")
        self.tableau_id = tableau_id

    def _new(self):
        return TableauPile(self.tableau_id)

    def can_add_card(self, card, origin, player):
        """Check if the card can be added to the pile.

        True if either the pile is empty or the color from the top card is
        different from the card color and the rank is just below.
        """
        return not self._cards or (
            card.rank == self.top_card.rank - 1
            and not card.is_same_color(self.top_card)
        )

    def can_pop_card(self, player):
        return True


class _PlayerPile(Pile):
    """Piles specific to the player."""

    _name_tpl = "_PilePlayer{player}"

    __slots__ = ["_player"]

    def __init__(self, player):
        assert player in {0, 1}
        super().__init__(self._name_tpl.format(player=player))
        self._player = player

    def _new(self):
        return self.__class__(self._player)

    def copy(self, cards: list[Card] | None = None) -> "_PlayerPile":
        """Return a copy of the pile, with a new set of cards."""
        new = super().copy(cards)
        new._player = self._player
        return new

    def can_pop_card(self, player):
        return player == self._player

    @property
    def player(self):
        return self._player

    def __eq__(self, other):
        """Doesn't check if cards face up or down."""
        return super().__eq__(other) and self.name == other.name

    # __eq__ is redefined, need to redefine __hash__ too
    __hash__ = Pile.__hash__


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

        if self.is_empty or card.suit != self.top_card.suit:
            return False

        # Faster than card.rank in [rank - 1, rank + 1]
        return abs(card.rank - self.top_card.rank) == 1

    def can_pop_card(self, player):
        return False


class CrapePile(_PlayerPile):
    """Smallest and high-priorty pile the player has to empty."""

    _name_tpl = "CrapePlayer{player}"
    NB_CARDS_START = 13

    __slots__ = []

    def can_add_card(self, card, origin, player):
        """Check if the card can be added to the pile."""
        return (
            self._player != player
            and self._cards
            and (top_card := self.top_card).face_up
            and card.suit == top_card.suit
            # Faster than card.rank in [rank - 1, rank + 1]
            and abs(card.rank - top_card.rank) == 1
        )


class PlayerPiles(NamedTuple):
    """NamedTuple for all piles specific to a player."""

    stock: StockPile
    waste: WastePile
    crape: CrapePile


def player_piles(player):
    """Return a PlayerPiles instance with the 3 piles for a player."""
    return PlayerPiles(StockPile(player), WastePile(player), CrapePile(player))
