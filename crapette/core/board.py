"""
Initialisation and data for a crapette game board backend.
"""

import random
from collections import namedtuple

from .cards import new_deck, Card
from .piles import FoundationPile, TableauPile, player_piles

Move = namedtuple("Move", ["card", "origin", "destination"])
Flip = namedtuple("Flip", ["card", "pile"])
FlipWaste = namedtuple("FlipWaste", [])


class Board:
    NB_PILES = 8
    NB_ROWS = 6  # 4 foundations + 2 players
    NB_PLAYERS = 2
    FOUNDATION_SUITES = "dchsshcd"
    assert len(FOUNDATION_SUITES) == NB_PILES

    def __init__(self, new_game=True):
        # Setup the piles on the board
        self.players_piles = [player_piles(p) for p in range(self.NB_PLAYERS)]
        self.foundation_piles = [
            # Diamonds, Clubs, Hearts, Spades and reverse
            FoundationPile(s, i)
            for i, s in enumerate(self.FOUNDATION_SUITES)
        ]
        self.tableau_piles = [TableauPile(i) for i in range(self.NB_PILES)]

        self._pile_by_names = {p.name: p for p in self.piles}

        self._hash_cache = None

        if new_game:
            self.new_game()

    @property
    def piles(self):
        return (
            list(self.players_piles[0])
            + list(self.players_piles[1])
            + self.foundation_piles
            + self.tableau_piles
        )

    def __getitem__(self, name):
        """Can take a pile name or a pile obkect (not necesserally from this board)"""
        if hasattr(name, "name"):
            name = name.name
        return self._pile_by_names[name]

    def __repr__(self):
        return f"Board:{id(self)}"

    def __str__(self):
        return self.__repr__()

    def new_game(self):
        """Reset the board and distribute the cards for a new game"""
        for player, player_piles in enumerate(self.players_piles):
            # Create deck
            deck = new_deck(player)

            # Fill crape
            player_piles.crape.set_cards(deck[0:13])
            player_piles.crape[-1].face_up = True

            # Fill tableau
            for index, tableau_index in enumerate(range(player * 4, player * 4 + 4)):
                card = deck[13 + index]
                card.face_up = True
                self.tableau_piles[tableau_index].set_cards([card])

            # Fill stock
            player_piles.stock.set_cards(deck[17:])

            # Empty waste
            player_piles.waste.clear()

            # Check number of cards
            assert len(player_piles.crape) == 13
            assert len(player_piles.waste) == 0
            assert len(player_piles.stock) == 35

        # Check tableau
        for tableau_pile in self.tableau_piles:
            assert (
                len(tableau_pile) == 1
            ), f"{tableau_pile.name} should have exactly 1 card"

        # Empty foundation
        for foundation_pile in self.foundation_piles:
            foundation_pile.clear()
            assert len(foundation_pile) == 0

    def copy(self):
        """Create a copy of the board

        The piles will be new objects, but will contain the same card objects
        as the current board, don't modify their state.
        """
        board = Board(new_game=False)
        for pile, pile_copy in zip(self.piles, board.piles):
            pile_copy._cards = pile._cards.copy()

        return board

    def compute_first_player(self):
        """Compute the starting player.

        It should be only called on a new game.
        """
        # Player with highest crape goes first
        player0_crape_rank = self.players_piles[0].crape.rank
        player1_crape_rank = self.players_piles[1].crape.rank
        if player0_crape_rank > player1_crape_rank:
            return 0
        elif player0_crape_rank < player1_crape_rank:
            return 1

        # Player with highest tableau goes first
        player0_tableau_rank = sorted(
            (p.rank for p in self.tableau_piles[:4]), reverse=True
        )
        player1_tableau_rank = sorted(
            (p.rank for p in self.tableau_piles[4:]), reverse=True
        )
        if player0_tableau_rank > player1_tableau_rank:
            return 0
        elif player0_tableau_rank < player1_tableau_rank:
            return 1
        else:
            # Extreme measures
            return random.randint(0, 1)

    def __eq__(self, other):
        """Doesn't check if cards face up or down"""
        # Check player piles for both players
        for player in range(Board.NB_PLAYERS):
            for pile, pile_other in zip(self.players_piles[0], other.players_piles[0]):
                if pile != pile_other:
                    return False

        # Check foundation, inversion between same suit piles doesn't matter
        for i in range(Card.NB_SUITS):
            self_foundation_pile_right = self.foundation_piles[i]
            other_foundation_pile_right = other.foundation_piles[i]
            self_foundation_pile_left = self.foundation_piles[Card.NB_SUITS - i - 1]
            other_foundation_pile_left = other.foundation_piles[Card.NB_SUITS - i - 1]
            if not (
                (
                    self_foundation_pile_right == other_foundation_pile_right
                    and self_foundation_pile_left == other_foundation_pile_left
                )
                or (
                    self_foundation_pile_right == other_foundation_pile_left
                    and self_foundation_pile_left == other_foundation_pile_right
                )
            ):
                return False

        # Check tableau piles, order doesn't matter
        self_tableau = sorted(self.tableau_piles, reverse=True)
        other_tableau = sorted(other.tableau_piles, reverse=True)
        for pile, pile_other in zip(self_tableau, other_tableau):
            if pile != pile_other:
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        """
        Warning, boards are mutable in general !
        This is only used in AI computations where boards are frozen.

        Doesn't differ if cards face up or down
        """
        if self._hash_cache is None:
            # Player piles
            piles = [p for p in self.players_piles[0] + self.players_piles[1]]

            # Foundation, inversion between same suit piles doesn't matter
            for i in range(Card.NB_SUITS):
                piles += sorted(
                    [
                        self.foundation_piles[i],
                        self.foundation_piles[Card.NB_SUITS - i - 1],
                    ]
                )
            piles += sorted(self.tableau_piles, reverse=True)
            self._hash_cache = hash(tuple(p.cards_ids() for p in piles))
        return self._hash_cache
