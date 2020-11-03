from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivy.app import App

from ..images.card_deck import CARD_IMG
from ..core.piles import StockPile


class PileWidget(RelativeLayout):
    """Parent widget for all pile types"""

    def set_pile(self, pile):
        self.pile = pile

    def card_pos(self, index=None):
        """Position of the center of the index-th card.

        If no index is given, the position for the top card is returned.
        """
        # Default implementation, all cards in the center of the pile
        return self.pos[0] + self.width / 2, self.pos[1] + self.height / 2

    def card_rot(self):
        """Rotation of the cards in the deck in degrees"""
        return 0

    def pop_card(self):
        self.pile.pop_card()

    def add_card(self, card_widget):
        self.pile.add_card(card_widget.card)


class FoundationPileWidget(PileWidget):
    """Piles for fondations

    Left and right foundations sould be different, because the rotation is not
    the same.
    """

    background = StringProperty()
    rotation = NumericProperty()

    def card_rot(self):
        """Rotation of the cards in the deck in degrees"""
        return 90


class PlayerPileWidget(PileWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._flipping = False

    def on_touch_down(self, touch):
        # Initialize flip on empty stock pile
        if not self.collide_point(touch.x, touch.y):
            return False

        if not hasattr(self, "pile"):  # No game has started yet
            return False

        if not isinstance(self.pile, StockPile):
            return False

        if not self.pile.is_empty:
            return False

        board_manager = App.get_running_app().board_manager
        player = board_manager.active_player
        if player != self.pile.player:
            return False

        self._flipping = True
        return True

    def on_touch_up(self, touch):
        # Finalize flip on empty stock pile if still inside the pile
        if not self._flipping:
            return False
        self._flipping = False

        if not self.collide_point(touch.x, touch.y):
            return False

        board_manager = App.get_running_app().board_manager
        board_manager.flip_waste_to_stock()
        return True


class TableauPileWidget(PileWidget):
    @property
    def pos_offset_factor(self):
        app = App.get_running_app()
        return app.card_overlap / (1 + 12 * app.card_overlap)


class TableauLeftPileWidget(TableauPileWidget):
    anchor = "right"

    def pos_anchor(self, i_card):
        return 1 - (self.pos_offset_factor * i_card)

    def card_pos(self, index=None):
        """Position of the center of the index-th card.

        If no index is given, the position for the top card is returned.
        """
        if index is None:
            index = len(self.pile) - 1
        assert index >= 0

        offset = App.get_running_app().card_width * (
            0.5 + CARD_IMG.OFFSET_FACTOR * index
        )
        return (self.pos[0] + self.width - offset, self.pos[1] + self.height / 2)


class TableauRightPileWidget(TableauPileWidget):
    anchor = "x"

    def pos_anchor(self, i_card):
        return self.pos_offset_factor * i_card

    def card_pos(self, index=None):
        """Position of the center of the index-th card.

        If no index is given, the position for the top card is returned.
        """
        if index is None:
            index = len(self.pile) - 1
        assert index >= 0

        offset = App.get_running_app().card_width * (
            0.5 + CARD_IMG.OFFSET_FACTOR * index
        )
        return (self.pos[0] + offset, self.pos[1] + self.height / 2)
