"""Initialization and data for a crapette game board backend."""

from line_profiler import profile

from .cards import Card, new_deck
from .moves import Move
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
    ]

    def __init__(self):
        # Setup the piles on the board
        self.players_piles = [player_piles(0), player_piles(1)]
        self.foundation_piles = [
            # Diamonds, Clubs, Hearts, Spades and reverse
            FoundationPile(s, i)
            for i, s in enumerate(self.FOUNDATION_SUITES)
        ]
        self.tableau_piles = [TableauPile(i) for i in range(self.NB_PILES)]

    @property
    def piles(self):
        return [
            *self.players_piles[0],
            *self.players_piles[1],
            *self.foundation_piles,
            *self.tableau_piles,
        ]

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

        # In case of a tie, player with highest tableau goes first
        player0_tableau_rank = sorted(
            (p.rank for p in self.tableau_piles[:4]), reverse=True
        )
        player1_tableau_rank = sorted(
            (p.rank for p in self.tableau_piles[4:]), reverse=True
        )
        return 1 if player0_tableau_rank < player1_tableau_rank else 0

    def check_win(self, player):
        players_piles = self.players_piles[player]
        return (
            not players_piles.stock
            and not players_piles.waste
            and not players_piles.crape
        )

    def to_text(self):
        str_lines = []
        player_space_left = " " * (13 * 3)

        def _player_pile_str(pile):
            if not pile:
                return "  "
            card = pile.top_card
            return card.str_rank_suit if card.face_up else "##"

        player_piles = self.players_piles[1]
        line = [
            player_space_left,
            _player_pile_str(player_piles.crape),
            "  ",
            _player_pile_str(player_piles.waste),
            " ",
            _player_pile_str(player_piles.stock),
        ]
        str_lines.append("".join(line))

        for tableau_row in range(self.FOUNDATIONS_PER_PLAYER):
            index_left = tableau_row + 4  # 4, 5, 6, 7
            index_right = 3 - tableau_row  # 3, 2, 1, 0

            tableau_pile_left = self.tableau_piles[index_left]
            tableau_pile_right = self.tableau_piles[index_right]
            foundation_pile_left = self.foundation_piles[index_left]
            foundation_pile_right = self.foundation_piles[index_right]

            space_left = ["  "] * (13 - len(tableau_pile_left))
            tableau_left = [c.str_rank_suit for c in tableau_pile_left[::-1]]
            tableau_right = [c.str_rank_suit for c in tableau_pile_right]
            if foundation_pile_left:
                foundation_left = foundation_pile_left.top_card.str_rank_suit
            else:
                foundation_left = "  "
            if foundation_pile_right:
                foundation_right = foundation_pile_right.top_card.str_rank_suit
            else:
                foundation_right = "  "
            separator = ["|"]
            str_line = " ".join(
                space_left
                + tableau_left
                + separator
                + [foundation_left]
                + [foundation_right]
                + separator
                + tableau_right
            )
            str_lines.append(str_line)

        player_piles = self.players_piles[0]
        line = [
            player_space_left,
            _player_pile_str(player_piles.stock),
            " ",
            _player_pile_str(player_piles.waste),
            "  ",
            _player_pile_str(player_piles.crape),
        ]
        str_lines.append("".join(line))

        str_lines = ["⌄" * 88, *str_lines, "⌃" * 88]
        return "\n".join(str_lines)


class HashBoard(Board):
    """Create a hashable version of a Board.

    Warning, Board objects are mutable in general !
    This is only used in AI computations where boards are "frozen".
    """

    __slots__ = ["_hash_cache"]

    @profile
    def __init__(self, board: Board, move: Move | None = None):
        super().__init__()

        origin_name = move.origin.name if move else None
        destination_name = move.destination.name if move else None

        # Pass pile content by reference
        # They should not be modified, except in `HashBoard.with_move()`
        for pile, board_pile in zip(self.piles, board.piles, strict=True):
            if pile.name == origin_name:
                pile._cards = board_pile._cards[:-1]
            elif pile.name == destination_name:
                pile._cards = [*board_pile._cards, move.card]
            else:
                pile._cards = board_pile._cards
            pile.freeze()

        self._hash_cache = self._compute_hash()

    def sorted_foundation_piles_indexed(self, suit_index: int):
        pile_a = self.foundation_piles[suit_index]
        pile_b = self.foundation_piles[2 * Card.NB_SUITS - suit_index - 1]
        return (pile_a, pile_b) if len(pile_a) < len(pile_b) else (pile_b, pile_a)

    def __hash__(self):
        return self._hash_cache

    @profile
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
        return set(self.tableau_piles) == set(other.tableau_piles)

    @profile
    def _compute_hash(self):
        """Compute and cache a hash for the board.

        Doesn't differ if cards face up or down.
        """
        # Player piles
        piles = list(self.players_piles[0]) + list(self.players_piles[1])
        piles = [*self.players_piles[0], *self.players_piles[1]]

        # Foundation, inversion between same suit piles doesn't matter
        for i_suit in range(Card.NB_SUITS):
            piles += self.sorted_foundation_piles_indexed(i_suit)
        piles += sorted(self.tableau_piles, reverse=True)

        return hash(tuple(piles))
