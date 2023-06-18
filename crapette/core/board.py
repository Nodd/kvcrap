"""Initialization and data for a crapette game board backend."""

import random

from .cards import Card, new_deck
from .piles import FoundationPile, TableauPile, player_piles


class Board:
    NB_PILES = 8
    NB_ROWS = 6  # 4 foundations + 2 players
    PLAYERS = (0, 1)
    NB_PLAYERS = len(PLAYERS)
    FOUNDATION_SUITES = "dchsshcd"
    assert len(FOUNDATION_SUITES) == NB_PILES
    FOUNDATIONS_PER_PLAYER = 4

    __slots__ = [
        "players_piles",
        "foundation_piles",
        "tableau_piles",
        "_pile_by_names_cache",
    ]

    def __init__(self):
        # Setup the piles on the board
        self.players_piles = [player_piles(p) for p in self.PLAYERS]
        self.foundation_piles = [
            # Diamonds, Clubs, Hearts, Spades and reverse
            FoundationPile(s, i)
            for i, s in enumerate(self.FOUNDATION_SUITES)
        ]
        self.tableau_piles = [TableauPile(i) for i in range(self.NB_PILES)]
        self._pile_by_names_cache = None

    @property
    def piles(self):
        return (
            list(self.players_piles[0])
            + list(self.players_piles[1])
            + self.foundation_piles
            + self.tableau_piles
        )

    def __getitem__(self, name):
        """Can take a pile name or a pile object (not necessarily from this board)."""
        if hasattr(name, "name"):
            name = name.name
        if self._pile_by_names_cache is None:
            self._pile_by_names_cache = {p.name: p for p in self.piles}
        return self._pile_by_names_cache[name]

    def __repr__(self):
        return f"Board:{id(self)}"

    def __str__(self):
        return self.__repr__()

    def new_game(self):
        """Reset the board and distribute the cards for a new game."""
        for player, player_piles_ in enumerate(self.players_piles):
            # Create deck
            deck = new_deck(player)

            # Fill crape
            player_piles_.crape.set_cards(deck[: player_piles_.crape.NB_CARDS_START])
            deck = deck[player_piles_.crape.NB_CARDS_START :]
            player_piles_.crape.face_up = True

            # Fill tableau
            for index, tableau_index in enumerate(
                range(
                    player * self.FOUNDATIONS_PER_PLAYER,
                    player * self.FOUNDATIONS_PER_PLAYER + self.FOUNDATIONS_PER_PLAYER,
                )
            ):
                card = deck[index]
                card.face_up = True
                self.tableau_piles[tableau_index].set_cards([card])
            deck = deck[self.FOUNDATIONS_PER_PLAYER :]

            # Fill stock
            player_piles_.stock.set_cards(deck)

            # Empty waste
            player_piles_.waste.clear()

            # Check number of cards
            assert len(player_piles_.crape) == 13
            assert len(player_piles_.waste) == 0
            assert len(player_piles_.stock) == 35

        # Check tableau
        for tableau_pile in self.tableau_piles:
            assert (
                len(tableau_pile) == 1
            ), f"{tableau_pile.name} should have exactly 1 card, not {len(tableau_pile)}"

        # Empty foundation
        for foundation_pile in self.foundation_piles:
            foundation_pile.clear()
            assert len(foundation_pile) == 0

    def compute_first_player(self):
        """Compute the starting player.

        It should be only called on a new game.
        """
        # Player with highest crape goes first
        player0_crape_rank = self.players_piles[0].crape.rank
        player1_crape_rank = self.players_piles[1].crape.rank
        if player0_crape_rank > player1_crape_rank:
            return 0
        if player0_crape_rank < player1_crape_rank:
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
        if player0_tableau_rank < player1_tableau_rank:
            return 1

        # Extreme measures
        return random.randint(0, 1)

    def check_win(self, player):
        players_piles = self.players_piles[player]
        return (
            not players_piles.stock
            and not players_piles.waste
            and not players_piles.crape
        )


class HashBoard(Board):
    """Create a hashable version of a Board.

    Warning, Board objects are mutable in general !
    This is only used in AI computations where boards are "frozen".
    """

    __slots__ = ["_hash_cache"]

    def __init__(self, board: Board):
        super().__init__()

        # The piles will be new objects, but will contain the same card objects
        # as the current board, don't modify their state.
        for pile, pile_orig in zip(self.piles, board.piles, strict=True):
            pile._cards = [*pile_orig._cards]  # A bit faster than .copy()

        self._hash_cache = None

    def sorted_foundation_piles_indexed(self, suit_index: int):
        return sorted(
            (
                self.foundation_piles[suit_index],
                self.foundation_piles[2 * Card.NB_SUITS - suit_index - 1],
            )
        )

    def __eq__(self, other: "HashBoard"):
        """Compute equivalence (not strict equality) between HashBoard instances."""
        # Check player piles equality for both players
        # Note: Card deck origin could be ignored for optimization,
        # but the expected speedup would be negligible
        if self.players_piles != other.players_piles:
            return False

        # Check foundation
        # Inversion between same suit piles doesn't matter
        if any(
            self.sorted_foundation_piles_indexed(i_suit)
            != other.sorted_foundation_piles_indexed(i_suit)
            for i_suit in range(Card.NB_SUITS)
        ):
            return False

        # Check tableau piles, order doesn't matter
        self_tableau = sorted(self.tableau_piles, reverse=True)
        other_tableau = sorted(other.tableau_piles, reverse=True)
        return self_tableau == other_tableau

    def __hash__(self):
        """Compute a hash for the board.

        Doesn't differ if cards face up or down
        """
        if self._hash_cache is None:
            # Player piles
            piles = list(self.players_piles[0]) + list(self.players_piles[1])

            # Foundation, inversion between same suit piles doesn't matter
            for i_suit in range(Card.NB_SUITS):
                piles += self.sorted_foundation_piles_indexed(i_suit)
            piles += sorted(self.tableau_piles, reverse=True)

            self._hash_cache = hash(tuple(p.cards_ids() for p in piles))
        return self._hash_cache
