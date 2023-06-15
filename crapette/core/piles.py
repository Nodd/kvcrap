"""Class for pile of cards parameters and methods."""

from typing import NamedTuple

from kivy.logger import Logger

from .cards import Card


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

    __slots__ = ["_foundation_id", "_suit"]

    def __init__(self, suit, foundation_id):
        assert suit in Card.SUITS
        super().__init__(f"Foundation{foundation_id}{suit}")
        self._foundation_id = foundation_id
        self._suit = suit

    def can_add_card(self, card, origin, player):
        """Check if the card can be added to the pile.

        Card can be added if it has the same suit as the pile, and a rank just above the last card.
        """
        if card.suit != self._suit:
            Logger.debug(
                "Add %s: Impossible, %s has not suit %s", self.name, card, self._suit
            )
            return False
        if card.rank != len(self._cards) + 1:
            Logger.debug(
                "Add %s: Impossible, %s has not rank %s",
                self.name,
                card,
                len(self._cards) + 1,
            )
            return False
        Logger.debug("Add %s: Possible, %s can be added", self.name, card)
        return True

    def can_pop_card(self, player):
        """Cards can never be removed from here.

        Note: except when rolling back in crapette mode, but that's not maanged here
        """
        Logger.debug(
            "Pop %s: Impossible, it's never possible to pop card from here", self.name
        )
        return False

    @property
    def is_full(self):
        """If the pile is full from Ace to King."""
        return len(self._cards) == Card.MAX_RANK

    def __eq__(self, other):
        """Doesn't check if cards face up or down."""
        return (
            isinstance(other, FoundationPile)
            and self._suit == other._suit
            and self._cards == other._cards
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
        # Empty pile can accept any card
        if not self._cards:
            Logger.debug(
                "Add %s: Possible, empty pile can accept any card, including %s",
                self.name,
                card,
            )
            return True

        # Need alternate colors
        if card.is_same_color(self.top_card):
            Logger.debug(
                "Add %s: Impossible, %s has same color as top card %s",
                self.name,
                card,
                self.top_card,
            )
            return False

        # New card must be 1 rank lower that last card in pile
        if card.rank != self.top_card.rank - 1:
            Logger.debug(
                "Add %s: Impossible, %s is not a rank lower than %s",
                self.name,
                card,
                self.top_card,
            )
            return False

        Logger.debug(
            "Add %s: Possible, %s can go over %s", self.name, card, self.top_card
        )
        return True

    def can_pop_card(self, player):
        Logger.debug("Pop %s: Possible, can always pop card from here", self.name)
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
        if player != self._player:
            Logger.debug(
                "Pop %s: Impossible, only the player can pop cards from its piles",
                self.name,
            )
            return False
        Logger.debug(
            "Pop %s: Possible, the player can pop cards from its piles", self.name
        )
        return True

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
        Logger.debug(
            "Add %s: Impossible, it's never allowed to add cards here", self.name
        )
        return False


class WastePile(_PlayerPile):
    """Pile where the player throws his card when he can not play anymore."""

    _name_tpl = "WastePlayer{player}"

    __slots__ = []

    def can_add_card(self, card: Card, origin, player):
        """Check if the card can be added to the pile."""
        if self._player == player:
            if not isinstance(origin, StockPile) and origin.player == player:
                Logger.debug(
                    "Add %s: Impossible, the player can only put cards here from its stock pile (%s)",
                    self.name,
                    card,
                )
                return False
            Logger.debug(
                "Add %s: Possible, the player can put card %s here from its stock pile",
                self.name,
                card,
            )
        else:
            if self.is_empty:
                Logger.debug(
                    "Add %s: Impossible, the other player can not put card %s on an empty waste pile",
                    self.name,
                    card,
                )
                return False
            if card.suit != self.top_card.suit:
                Logger.debug(
                    "Add %s: Impossible, the other player can not put card %s with a different suit than %s",
                    self.name,
                    card,
                    self.top_card,
                )
                return False
            rank = self.top_card.rank
            if card.rank not in [rank - 1, rank + 1]:
                Logger.debug(
                    "Add %s: Impossible, the other player can only put card one rank above or below %s, not %s",
                    self.name,
                    self.top_card,
                    card,
                )
                return False
            Logger.debug(
                "Add %s: Possible, the other player can put %s over %s",
                self.name,
                card,
                self.top_card,
            )
        return True

    def can_pop_card(self, player):
        Logger.debug(
            "Pop %s: Impossible, cards can never be taken from here", self.name
        )
        return False


class CrapePile(_PlayerPile):
    """Smallest and high-priorty pile the player has to empty."""

    _name_tpl = "CrapePlayer{player}"
    NB_CARDS_START = 13

    __slots__ = []

    def can_add_card(self, card, origin, player):
        """Check if the card can be added to the pile."""
        if self._player == player:
            Logger.debug(
                "Add %s: Impossible, player can never put cards (%s) on its own crapette pile",
                self.name,
                card,
            )
            return False
        if not self:
            Logger.debug(
                "Add %s: Impossible, the other player can not put card %s on an empty crapette pile",
                self.name,
                card,
            )
            return False
        assert self.top_card is not None
        if card.suit != self.top_card.suit:
            Logger.debug(
                "Add %s: Impossible, the other player can not put card %s with a different suit than %s",
                self.name,
                card,
                self.top_card,
            )
            return False
        rank = self.top_card.rank
        if card.rank not in [rank - 1, rank + 1]:
            Logger.debug(
                "Add %s: Impossible, the other player can only put card one rank above or below %s, not %s",
                self.name,
                self.top_card,
                card,
            )
            return False
        Logger.debug(
            "Add %s: Possible, the other player can put %s over %s)",
            self.name,
            card,
            self.top_card,
        )
        return True


class PlayerPiles(NamedTuple):
    """NamedTuple for all piles specific to a player."""

    stock: StockPile
    waste: WastePile
    crape: CrapePile


def player_piles(player):
    """Return a PlayerPiles instance with the 3 piles for a player."""
    return PlayerPiles(StockPile(player), WastePile(player), CrapePile(player))
