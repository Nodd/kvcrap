"""
Widget representing the place of the piles of cards on the board.

It's mostly used for positionning the cards on the board.
"""

from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import StringProperty, NumericProperty
from kivy.app import App
from kivy.input.motionevent import MotionEvent

from ..crapette import CrapetteApp
from ..images.card_deck import CARD_IMG
from ..core.piles import StockPile, _Pile
from .card_widget import CardWidget


class PileWidget(RelativeLayout):
    """Parent widget for all pile types"""

    rotation = NumericProperty()

    def __repr__(self):
        try:
            return f"PileWidget({self.pile!r})"
        except AttributeError:
            return "PileWidget()"

    def set_pile(self, pile: _Pile):
        self.pile = pile

    def card_pos(self, index: int = None) -> tuple[float, float]:
        """Position of the center of the index-th card.

        If no index is given, the position for the top card is returned.
        """
        # Default implementation, all cards in the center of the pile
        center: tuple[float, float] = self.center
        return center

    def pop_card(self):
        self.pile.pop_card()

    def add_card(self, card_widget: CardWidget):
        self.pile.add_card(card_widget.card)


class FoundationPileWidget(PileWidget):
    """Piles for foundations

    Left and right foundations should be different, because the rotation is not
    the same.
    """

    background = StringProperty()


class PlayerPileWidget(PileWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._flipping = False

    def on_touch_down(self, touch: MotionEvent) -> bool:
        # Initialize flip on empty stock pile
        if not self.collide_point(touch.x, touch.y):
            return False

        if not hasattr(self, "pile"):  # No game has started yet
            return False

        if not isinstance(self.pile, StockPile):
            return False

        if not self.pile.is_empty:
            return False

        game_manager = App.get_running_app().game_manager
        player = game_manager.active_player
        if player != self.pile.player:
            return False

        self._flipping = True
        return True

    def on_touch_up(self, touch: MotionEvent) -> bool:
        # Finalize flip on empty stock pile if still inside the pile
        if not self._flipping:
            return False
        self._flipping = False

        if not self.collide_point(touch.x, touch.y):
            return False

        game_manager = App.get_running_app().game_manager
        game_manager.flip_waste_to_stock()
        return True


class TableauPileWidget(PileWidget):
    @property
    def pos_offset_factor(self) -> float:
        app: CrapetteApp = App.get_running_app()
        return app.card_overlap / (1 + 12 * app.card_overlap)

    def position_offset(self, index: int | None) -> float:
        if index is None:
            index = len(self.pile) - 1
        assert index >= 0

        app: CrapetteApp = App.get_running_app()
        OFFSET_FACTOR: float = CARD_IMG.OFFSET_FACTOR
        return app.card_width * (0.5 + OFFSET_FACTOR * index)


class TableauLeftPileWidget(TableauPileWidget):
    def pos_anchor(self, i_card: int) -> float:
        return 1 - (self.pos_offset_factor * i_card)

    def card_pos(self, index: int = None):
        """Position of the center of the index-th card.

        If no index is given, the position for the top card is returned.
        """
        return self.right - self.position_offset(index), self.center_y


class TableauRightPileWidget(TableauPileWidget):
    def pos_anchor(self, i_card: int) -> float:
        return self.pos_offset_factor * i_card

    def card_pos(self, index: int = None) -> tuple[float, float]:
        """Position of the center of the index-th card.

        If no index is given, the position for the top card is returned.
        """
        return self.x + self.position_offset(index), self.center_y
