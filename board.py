import random

from cards import new_deck
from piles import FoundationPile, TableauPile, player_piles

NB_PLAYERS = 2


class Board:
    NB_PILES = 8
    FOUNDATION_SUITES = "dchsshcd"
    assert len(FOUNDATION_SUITES) == NB_PILES

    def __init__(self):
        self._setup_piles()
        self._setup_decks()

    def _setup_piles(self):
        """Setup the piles on the board.

        Should be called only once.
        """
        self._player_piles = [player_piles(p) for p in range(NB_PLAYERS)]
        self._foundation_piles = [
            # Diamonds, Clubs, Hearts, Spades and reverse
            FoundationPile(s, i)
            for i, s in enumerate(self.FOUNDATION_SUITES)
        ]
        self._tableau_piles = [TableauPile(i) for i in range(self.NB_PILES)]

    def _setup_decks(self):
        """Reset the board and distribute the cards for a new game"""
        for player, player_piles in enumerate(self._player_piles):
            # Create deck
            deck = new_deck(player)

            # Fill crapette
            player_piles.crapette.set_cards(deck[0:13])
            player_piles.crapette[-1].face_up = True

            # Fill tableau
            for index, tableau_index in enumerate(range(player * 4, player * 4 + 4)):
                card = deck[13 + index]
                card.face_up = True
                self._tableau_piles[tableau_index].set_cards([card])

            # Fill stock
            player_piles.stock.set_cards(deck[17:])

            # Empty waste
            player_piles.waste.clear()

            # Check number of cards
            assert len(player_piles.crapette) == 13
            assert len(player_piles.waste) == 0
            assert len(player_piles.stock) == 35

        # Check tableau
        for tableau_pile in self._tableau_piles:
            assert (
                len(tableau_pile) == 1
            ), f"{tableau_pile.name} should have exactly 1 card"

        # Empty foundation
        for foundation_pile in self._foundation_piles:
            foundation_pile.clear()
            assert len(foundation_pile) == 0

    def compute_first_player(self):
        """Compute the starting player.

        It should be only called on a new game.
        """
        # Player with highest crapette goes first
        player0_crapette_rank = self._player_piles[0].crapette.rank
        player1_crapette_rank = self._player_piles[1].crapette.rank
        if player0_crapette_rank > player1_crapette_rank:
            return 0
        elif player0_crapette_rank < player1_crapette_rank:
            return 1

        # Player with highest tableau goes first
        player0_tableau_rank = sorted(
            (p.rank for p in self._tableau_piles[:4]), reverse=True
        )
        player1_tableau_rank = sorted(
            (p.rank for p in self._tableau_piles[4:]), reverse=True
        )
        if player0_tableau_rank > player1_tableau_rank:
            return 0
        elif player0_tableau_rank < player1_tableau_rank:
            return 1
        else:
            # Extreme measures
            return random.randint(0, 1)


if __name__ == "__main__":
    b = Board()
    print(b.compute_first_player())
