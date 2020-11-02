from collections import namedtuple

from .cards import Card

_DEBUG = False


def debug(*s):
    if _DEBUG:
        print(*s)


class _Pile:
    """Defines the Pile interface and some generic methods for all piles"""

    def __init__(self, name):
        self._name = str(name)
        self._cards = []

    def add_card(self, card):
        """Add a card to the pile"""
        self._cards.append(card)

    def pop_card(self):
        """Take the top card from the pile"""
        assert self._cards, f"No card to pop in {self._name}"
        return self._cards.pop()

    def can_add_card(self, card, origin, player):
        """Ckeck if the card can be added to the pile"""
        raise NotImplementedError

    def can_pop_card(self, player):
        """Ckeck if the top card can be taken from the pile"""
        raise NotImplementedError

    def __iter__(self):
        yield from self._cards

    def __getitem__(self, index):
        """Index pile to get card"""
        return self._cards[index]

    def __len__(self):
        return len(self._cards)

    @property
    def name(self):
        """Name of the pile"""
        return self._name

    @property
    def is_empty(self):
        return not len(self._cards)

    @property
    def top_card(self):
        """topmost card of the pile"""
        try:
            return self._cards[-1]
        except IndexError:
            return None

    @property
    def rank(self):
        """Rank of the topmost card of the pile"""
        return self._cards[-1].rank

    @property
    def suit(self):
        """Suit of the topmost card of the pile"""
        return self._cards[-1].suit

    @property
    def player(self):
        """Initial player of the topmost card of the pile"""
        return self._cards[-1].player

    @property
    def face_up(self):
        """State of the topmost card of the pile"""
        return self._cards[-1].face_up

    @face_up.setter
    def face_up(self, is_face_up):
        """Setter of the state of the topmost card of the pile"""
        self._cards[-1].face_up = is_face_up

    def set_cards(self, cards):
        """Replaces the cards in the pile

        Warning, nothing is checked !
        """
        # TODO: Checks for each pile type
        self._cards = cards

    def clear(self):
        """Empty the pile"""
        self._cards = []


class FoundationPile(_Pile):
    """Pile in the center where the suites are build from Ace to King."""

    def __init__(self, suit, foundation_id):
        assert suit in Card.SUITS
        super().__init__(f"Foundation{foundation_id}{suit}")
        self._foundation_id = foundation_id
        self._suit = suit

    def can_add_card(self, card, origin, player):
        if card.suit != self._suit:
            debug(f"Add {self.name}: Impossible, {card} has not suit {self._suit}")
            return False
        if card.rank != len(self._cards) + 1:
            debug(
                f"Add {self.name}: Impossible, {card} has not rank {len(self._cards) + 1}"
            )
            return False
        debug(f"Add {self.name}: Possible, {card} can be added")
        return True

    def can_pop_card(self, player):
        debug(f"Pop {self.name}: Impossible, it's never possible to pop card from here")
        return False

    @property
    def is_full(self):
        """If the pile is full from Ace to King"""
        return len(self._cards) == Card.MAX_RANK


class TableauPile(_Pile):
    """Side piles where cards go from King to Ace with alternate colors"""

    def __init__(self, tableau_id):
        super().__init__(f"Tableau{tableau_id}")
        self._id = tableau_id

    def can_add_card(self, card, origin, player):
        # Empty pile can accept any card
        if not self._cards:
            debug(
                f"Add {self.name}: Possible, empty pile can accept any card, including {card}"
            )
            return True

        # Need alternate colors
        if card.is_same_color(self.top_card):
            debug(
                f"Add {self.name}: Impossible, {card} has same color as top card {self.top_card}"
            )
            return False

        # New card must be 1 rank lower that last card in pile
        if card.rank != self.top_card.rank - 1:
            debug(
                f"Add {self.name}: Impossible, {card} is not a rank lower than {self.top_card}"
            )
            return False

        debug(f"Add {self.name}: Possible, {card} can go over {self.top_card}")
        return True

    def can_pop_card(self, player):
        debug(f"Pop {self.name}: Possible, can always pop card from here")
        return True


class _PlayerPile(_Pile):
    """Piles specific to the player"""

    def __init__(self, player):
        assert player in {0, 1}
        super().__init__(self._name_tpl.format(player=player))
        self._player = player

    def can_pop_card(self, player):
        if player != self._player:
            debug(
                f"Pop {self.name}: Impossible, only the player can pop cards from its piles"
            )
            return False
        debug(f"Pop {self.name}: Possible, the player can pop cards from its piles")
        return True

    @property
    def player(self):
        return self._player


class StockPile(_PlayerPile):
    """Biggest and lowest priority of the 2 piles a player has to empty"""

    _name_tpl = "StockPlayer{player}"

    def can_add_card(self, card, origin, player):
        debug(f"Add {self.name}: Impossible, it's never allowed to add cards here")
        return False


class WastePile(_PlayerPile):
    """Pile where the player throws his card when he can not play anymore."""

    _name_tpl = "WastePlayer{player}"

    def can_add_card(self, card, origin, player):
        if self._player == player:
            if not isinstance(origin, StockPile) and origin.player == player:
                debug(
                    f"Add {self.name}: Impossible, the player can only put cards here from its stock pile ({card})"
                )
                return False
            debug(
                f"Add {self.name}: Possible, the player can put card {card} here from its stock pile"
            )
            return True
        else:
            if not self:
                debug(
                    f"Add {self.name}: Impossible, the other player can not put card {card} on an empty waste pile"
                )
                return False
            if card.suit != self.top_card.suit:
                debug(
                    f"Add {self.name}: Impossible, the other player can not put card {card} with a different suit than {self.top_card}"
                )
                return False
            rank = self.top_card.rank
            if card.rank not in [rank - 1, rank + 1]:
                debug(
                    f"Add {self.name}: Impossible, the other player can only put card one rank above or below {self.top_card}, not {card}"
                )
                return False
            debug(
                f"Add {self.name}: Possible, the other player can put {card} over {self.top_card}"
            )
            return True

    def can_pop_card(self, player):
        debug(f"Pop {self.name}: Impossible, cards can never be taken from here")
        return False


class CrapePile(_PlayerPile):
    """Smallest and high-priorty pile the player has to empty"""

    _name_tpl = "CrapePlayer{player}"

    def can_add_card(self, card, origin, player):
        if self._player == player:
            debug(
                "Add {self.name}: Impossible, player can never put cards ({card}) on its own crapette pile"
            )
            return False
        else:
            if not self:
                debug(
                    f"Add {self.name}: Impossible, the other player can not put card {card} on an empty crapette pile"
                )
                return False
            if card.suit != self.top_card.suit:
                debug(
                    f"Add {self.name}: Impossible, the other player can not put card {card} with a different suit than {self.top_card}"
                )
                return False
            rank = self.top_card.rank
            if card.rank not in [rank - 1, rank + 1]:
                debug(
                    f"Add {self.name}: Impossible, the other player can only put card one rank above or below {self.top_card}, not {card}"
                )
                return False
            debug(
                f"Add {self.name}: Possible, the other player can put {card} over {self.top_card})"
            )
            return True


# namedtuple for all piles specific to a player
PlayerPiles = namedtuple("PlayerPiles", ["stock", "waste", "crape"])


def player_piles(player):
    """Return a PlayerPiles instance with the 3 piles for a player"""
    return PlayerPiles(StockPile(player), WastePile(player), CrapePile(player))
