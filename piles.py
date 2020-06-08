from collections import namedtuple

from cards import Card


class _Pile:
    """Defines the Pile interface and some generic methods for all piles"""

    def __init__(self, name):
        self._name = str(name)
        self._cards = []

    def add_card(self, origin, card):
        assert self.can_add_card(origin, card)
        self._cards.append(card)

    def pop_card(self):
        assert self._cards, f"No card to pop in {self._name}"
        return self._cards.pop()

    def can_add_card(self, origin, card):
        raise NotImplementedError

    def can_pop_card(self, player):
        raise NotImplementedError

    def __iter__(self):
        yield from self._cards

    def set_cards(self, cards):
        # TODO: Checks for each pile type
        self._cards = cards

    def num_cards(self):
        return len(self._cards)


class FoundationPile(_Pile):
    """Pile in the center where the suites are build from Ace to King."""

    def __init__(self, suit, foundation_id):
        assert suit in Card.SUITS
        super().__init__(f"Foundation{foundation_id}{suit}")
        self._foundation_id = foundation_id
        self._suit = suit

    def can_add_card(self, origin, card):
        return card.suit == self._suit and card.rank == len(self._cards) + 1

    def can_pop_card(self, player):
        return False

    def is_full(self):
        return len(self._cards) == Card.MAX_RANK


class TableauPile(_Pile):
    """Side piles where cards go from King to Ace with alternate colors"""

    def __init__(self, tableau_id):
        super().__init__(f"Tableau{tableau_id}")
        self._id = tableau_id

    def can_add_card(self, origin, card):
        # Empty pile can accept any card
        if not self._cards:
            return True

        # New card must be 1 rank lower that last card in pile
        if card.rank != self._cards[-1].rank - 1:
            return False

        # Need alternate colors
        return not card.is_same_color(self._cards[-1])

    def can_pop_card(self, player):
        return True


class _PlayerPile(_Pile):
    def __init__(self, player):
        assert player in {0, 1}
        super().__init__(self._name_tpl.format(player=player))
        self._player = player

    def can_pop_card(self, player):
        return player == self._player

    @property
    def player(self):
        return self._player


class StockPile(_PlayerPile):
    """Biggest and lowest priority of the 2 piles a player has to empty"""

    _name_tpl = "StockPlayer{player}"

    def can_add_card(self, origin, card):
        return False


class WastePile(_PlayerPile):
    """Pile where the player throws his card when he can not play anymore."""

    _name_tpl = "WastePlayer{player}"

    def can_add_card(self, origin, card):
        # TODO : depends from where comes the card...
        raise NotImplementedError

    def can_pop_card(self, player):
        return False


class CrapettePile(_PlayerPile):
    """Smallest and high-priorty pile the player has to empty"""

    _name_tpl = "CrapettePlayer{player}"

    def can_add_card(self, origin, card):
        # TODO : depends from where comes the card...
        raise NotImplementedError


PlayerPiles = namedtuple("PlayerPiles", ["stock", "waste", "crapette"])


def player_piles(player):
    return PlayerPiles(StockPile(player), WastePile(player), CrapettePile(player))
