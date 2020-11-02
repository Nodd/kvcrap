from collections import namedtuple

from .core.board import Board
from .core.piles import WastePile, FoundationPile
from .widgets import pile_widgets  # Load widgets
from .widgets.card_widget import CardWidget

Move = namedtuple("Move", ["card", "origin", "destination"])
Flip = namedtuple("Flip", ["card"])
FlipWaste = namedtuple("FlipWaste", [])

_DEBUG = False


def debug(*s):
    if _DEBUG:
        print(*s)


class BoardManager:
    def __init__(self, app):
        self.app = app

        self.pile_widgets = None
        self.board = None
        self.card_widgets = None

    def new_game(self):
        self.board = Board()
        self.setup_piles()
        self.add_card_widgets()
        self.place_cards()
        self.update_counts()

        self.set_player_turn(self.board.compute_first_player())

    def setup_piles(self):
        # Setup UI piles with game piles
        ids = self.app.root.ids
        self.pile_widgets = []
        for player, player_piles in enumerate(self.board.players_piles):
            self.pile_widgets.append(ids[f"player{player}stock"])
            self.pile_widgets.append(ids[f"player{player}waste"])
            self.pile_widgets.append(ids[f"player{player}crape"])
            ids[f"player{player}stock"].set_pile(player_piles.stock)
            ids[f"player{player}waste"].set_pile(player_piles.waste)
            ids[f"player{player}crape"].set_pile(player_piles.crape)
        for tableau, tableau_pile in enumerate(self.board.tableau_piles):
            self.pile_widgets.append(ids[f"tableau{tableau}"])
            ids[f"tableau{tableau}"].set_pile(tableau_pile)
        for foundation, foundation_pile in enumerate(self.board.foundation_piles):
            self.pile_widgets.append(ids[f"foundation{foundation}"])
            ids[f"foundation{foundation}"].set_pile(foundation_pile)

    def add_card_widgets(self):
        if self.card_widgets:
            for card_widget in self.card_widgets.values():
                self.app.root.remove_widget(card_widget)
        self.card_widgets = {}
        for pile_widget in self.pile_widgets:
            for card in pile_widget.pile:
                card_widget = CardWidget(card, self)
                card_widget.pile_widget = pile_widget
                self.card_widgets[card] = card_widget
                self.app.root.add_widget(card_widget)

    def place_cards(self):
        if not self.pile_widgets:
            return
        for pile_widget in self.pile_widgets:
            for index, card in enumerate(pile_widget.pile):
                card_widget = self.card_widgets[card]
                card_widget.center = pile_widget.card_pos(index)

    def set_player_turn(self, player):
        self.active_player = player
        self.app.root.background = f"images/background-player{player}.png"
        self.moves = []

    def update_counts(self):
        ids = self.app.root.ids
        for player in range(self.board.NB_PLAYERS):
            stock_pile = ids[f"player{player}stock"].pile
            crape_pile = ids[f"player{player}crape"].pile
            stock_label = ids[f"player{player}stockcount"]
            crape_label = ids[f"player{player}crapecount"]
            stock_label.text = str(len(stock_pile)) if stock_pile else ""
            crape_label.text = str(len(crape_pile)) if crape_pile else ""

    def move_card(self, card_widget, pile_widget):
        """Move a card to another pile.

        Return True if the card was moved, or False if the move is not possible.
        """
        old_pile_widget = card_widget.pile_widget

        can_add = pile_widget.pile.can_add_card(
            card_widget.card, old_pile_widget.pile, self.active_player
        )
        assert can_add in (True, False), can_add
        if not can_add:
            debug("Dropped on an incompatible pile")
            return False

        # Remove from previous pile
        old_pile_widget.pop_card()

        # Add to new pile
        pile_widget.add_card(card_widget)
        card_widget.pile_widget = pile_widget
        card_widget.set_center_animated(pile_widget.card_pos())
        self.update_counts()
        self.moves.append(Move(card_widget, old_pile_widget, pile_widget))

        # Special case for foundation
        if isinstance(pile_widget.pile, FoundationPile):
            card_widget.main_rotation = pile_widget.rotation

            # Flip foundation pile if full
            if pile_widget.pile.is_full:
                for card in pile_widget.pile:
                    card.face_up = False
                    self.card_widgets[card].update_image()

        self.check_win()
        self.check_end_of_turn(pile_widget)

        # Check end of player turn

        return True

    def check_win(self):
        ids = self.app.root.ids
        stock_widget = ids[f"player{self.active_player}stock"]
        waste_widget = ids[f"player{self.active_player}waste"]
        crape_widget = ids[f"player{self.active_player}crape"]
        if not stock_widget.pile and not waste_widget.pile and not crape_widget.pile:
            print(f"Player {self.active_player} wins !!!")
            self.active_player = None
            for card_widget in self.card_widgets.values():
                card_widget.do_translation = False
            return True

    def check_end_of_turn(self, pile_widget):
        if (
            isinstance(pile_widget.pile, WastePile)
            and pile_widget.pile.player == self.active_player
        ):
            self.set_player_turn(1 - self.active_player)

    def flip_card_up(self, card_widget):
        card_widget.set_face_up()
        self.moves.append(Flip(card_widget))

    def flip_waste_to_stock(self):
        ids = self.app.root.ids
        stock_widget = ids[f"player{self.active_player}stock"]
        waste_widget = ids[f"player{self.active_player}waste"]

        # Update model
        stock_widget.pile.set_cards(waste_widget.pile[::-1])
        waste_widget.pile.clear()

        # Update cards
        for index, card in enumerate(stock_widget.pile):
            card.face_up = False
            card_widget = self.card_widgets[card]
            card_widget.update_image()
            card_widget.pile_widget = stock_widget
            card_widget.set_center_animated(stock_widget.card_pos(index))

            # Re-add widget for correct order
            self.app.root.remove_widget(card_widget)
            self.app.root.add_widget(card_widget)
        self.update_counts()

        self.moves.append(FlipWaste())
