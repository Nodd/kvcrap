from cards import new_deck
from piles import FoundationPile, TableauPile, player_piles


class Board:
    NB_PILES = 8
    FOUNDATION_SUITES = "dchsshcd"

    def __init__(self):
        self._players = [0, 1]
        self._setup_piles()
        self._setup_decks()

    def _setup_piles(self):
        self._player_piles = [player_piles(p) for p in self._players]
        self._foundation_piles = [
            # Diamonds, Clubs, Hearts, Spades and reverse
            FoundationPile(s, i)
            for i, s in enumerate(self.FOUNDATION_SUITES)
        ]
        self._tableau_piles = [TableauPile(i) for i in range(self.NB_PILES)]

    def _setup_decks(self):
        for player, player_piles in enumerate(self._player_piles):
            # Create deck
            deck = new_deck(player)

            # Fill crapette
            player_piles.crapette.set_cards(deck[0:13])

            # Fill tableau
            for index, tableau_index in enumerate(range(player * 4, player * 4 + 4)):
                self._tableau_piles[tableau_index].set_cards([deck[13 + index]])

            # Fill stock
            player_piles.stock.set_cards(deck[17:])

            # Check number of cards
            assert player_piles.crapette.num_cards() == 13
            assert player_piles.waste.num_cards() == 0
            assert player_piles.stock.num_cards() == 35

        # Check tableau
        for tableau_pile in self._tableau_piles:
            assert (
                tableau_pile.num_cards() == 1
            ), f"{tableau_pile.name} should have exactly 1 card"


if __name__ == "__main__":
    b = Board()
