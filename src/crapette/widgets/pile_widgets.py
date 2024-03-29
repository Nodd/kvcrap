"""Widget representing the place of the piles of cards on the board.

It's mostly used for positionning the cards on the board.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from kivy.app import App
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.relativelayout import RelativeLayout

from crapette.core.piles import FoundationPile, Pile, StockPile
from crapette.images.card_data import CARD_IMG

if TYPE_CHECKING:
    from kivy.input.motionevent import MotionEvent

    from crapette import crapette

    from .card_widget import CardWidget


class PileWidget(RelativeLayout):
    """Parent widget for all pile types."""

    rotation = NumericProperty()

    def __repr__(self):
        try:
            return f"{self.__class__.__name__}({self.pile!r})"
        except AttributeError:
            return f"{self.__class__.__name__}()"

    def set_pile(self, pile: Pile):
        """Set the underlying Pile backend.

        This should be used for game initalization only.
        """
        self.pile = pile

    def card_pos(self, index: int = -1) -> tuple[float, float]:
        """Position of the center of the index-th card.

        If no index is given, the position for the top card is returned.
        """
        # In the default implementation, all cards are in the center of the pile.
        center: tuple[float, float] = self.center
        return center

    def pop_card(self):
        """Remove a card from the top of pile."""
        self.pile.pop_card()

    def add_card_widget(self, card_widget: CardWidget):
        self.pile.add_card(card_widget.card)
        card_widget.pile_widget = self


class FoundationPileWidget(PileWidget):
    """Piles for foundations.

    Left and right foundations should be different, because the rotation is not
    the same.
    """

    background = StringProperty()

    def add_card_widget(self, card_widget: CardWidget):
        super().add_card_widget(card_widget)

        # Flip foundation pile if full
        pile: FoundationPile = self.pile  # type: ignore[assignment]
        if pile.is_full:
            game_manager = App.get_running_app().game_manager
            game_manager.board_widget.flip_pile(self)


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
        player = game_manager.game_config.active_player
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
        app: crapette.CrapetteApp = App.get_running_app()
        return app.card_overlap / (1 + 12 * app.card_overlap)

    def position_offset(self, index: int) -> float:
        if index < 0:
            index += len(self.pile)
        assert index >= 0

        app: crapette.CrapetteApp = App.get_running_app()
        return app.card_width * (0.5 + CARD_IMG.OFFSET_FACTOR * index)


class TableauLeftPileWidget(TableauPileWidget):
    def pos_anchor(self, i_card: int) -> float:
        return 1 - (self.pos_offset_factor * i_card)

    def card_pos(self, index: int = -1) -> tuple[float, float]:
        """Position of the center of the index-th card.

        If no index is given, the position for the top card is returned.
        """
        return self.right - self.position_offset(index), self.center_y


class TableauRightPileWidget(TableauPileWidget):
    def pos_anchor(self, i_card: int) -> float:
        return self.pos_offset_factor * i_card

    def card_pos(self, index: int = -1) -> tuple[float, float]:
        """Position of the center of the index-th card.

        If no index is given, the position for the top card is returned.
        """
        return self.x + self.position_offset(index), self.center_y
