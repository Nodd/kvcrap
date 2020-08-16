from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivy.app import App

from .board_widgets import BoardWidget
from ..images.card_deck import CARD_IMG


class PileWidget(RelativeLayout):
    """Parent widget for all pile types"""

    source = StringProperty()
    is_empty = BooleanProperty()

    def set_pile(self, pile):
        self.pile = pile

    def card_pos(self, index):
        """Position of the center of the index-th card."""
        assert index >= 0

        # Default implementation
        return self.pos[0] + self.width / 2, self.pos[1] + self.height / 2

    def card_rot(self):
        """Rotation of the cards in the deck in degrees"""
        return 0

    # def on_touch_down(self, touch):
    #     if not self.collide_point(touch.x, touch.y):
    #         return

    #     if self.pile.is_empty:
    #         print("DOWN", self.pile.name, "Empty")
    #         return

    #     top_card = self.pile.top_card
    #     print("DOWN", self.pile.name, top_card)

    # def on_touch_up(self, touch):
    #     if not self.collide_point(touch.x, touch.y):
    #         return

    #     if self.pile.is_empty:
    #         top_card = "Empty"
    #     else:
    #         top_card = self.pile.top_card
    #     print("UP", self.pile.name, top_card)


class FoundationPileWidget(PileWidget):
    """Piles for fondations

    Left and right foundations sould be different, because the rotation is not
    the same.
    """

    def redraw(self):
        self.source = card2img(self.pile.top_card)
        self.is_empty = self.pile.is_empty

    def card_rot(self):
        """Rotation of the cards in the deck in degrees"""
        return 90


class PlayerPileWidget(PileWidget):
    ...


class TableauPileWidget(PileWidget):
    @property
    def pos_offset_factor(self):
        app = App.get_running_app()
        return app.card_overlap / (1 + 12 * app.card_overlap)

    def build(self):
        self.card_images = []
        for i_card in range(13):
            card_image = CardImage()
            card_image.opacity = 1
            card_image.pos_hint = {
                self.anchor: self.pos_anchor(i_card),
                "center_y": 0.5,
            }
            card_image.source = card2img(None)
            self.add_widget(card_image)
            self.card_images.append(card_image)

    def redraw(self):
        for card, card_image in zip(self.pile, self.card_images):
            card_image.source = card2img(card)
            card_image.opacity = 1
        for card_image in self.card_images[len(self.pile) :]:
            card_image.source = card2img(None)
            card_image.opacity = 0


class TableauLeftPileWidget(TableauPileWidget):
    anchor = "right"

    def pos_anchor(self, i_card):
        return 1 - (self.pos_offset_factor * i_card)

    def card_pos(self, index):
        """Position of the center of the index-th card."""
        assert index >= 0

        return self.pos[0] + self.width / 2, self.pos[1] + self.height / 2


class TableauRightPileWidget(TableauPileWidget):
    anchor = "x"

    def pos_anchor(self, i_card):
        return self.pos_offset_factor * i_card

    def card_pos(self, index):
        """Position of the center of the index-th card."""
        assert index >= 0

        # TODO : card width instead of widget width
        return (
            self.pos[0] + self.width * (0.5 + CARD_IMG.OFFSET_FACTOR * index),
            self.pos[1] + self.height / 2,
        )
