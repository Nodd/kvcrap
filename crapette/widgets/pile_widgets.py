from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivy.app import App

from ..images.card_deck import CARD_IMG


class PileWidget(RelativeLayout):
    """Parent widget for all pile types"""

    is_empty = BooleanProperty()

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

    def redraw(self):
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

    def card_pos(self, index=None):
        """Position of the center of the index-th card.
        
        If no index is given, the position for the top card is returned.
        """
        if index is None:
            index = len(self.pile) - 1
        assert index >= 0

        offset = App.get_running_app().card_width * (0.5 + CARD_IMG.OFFSET_FACTOR * index)
        return (
            self.pos[0] + self.width - offset,
            self.pos[1] + self.height / 2,
        )


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

        # TODO : card width instead of widget width
        
        offset = App.get_running_app().card_width * (0.5 + CARD_IMG.OFFSET_FACTOR * index)
        return (
            self.pos[0] + offset,
            self.pos[1] + self.height / 2,
        )
