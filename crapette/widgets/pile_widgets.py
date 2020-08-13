from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivy.app import App

from .board_widgets import BoardWidget


class PileWidget(RelativeLayout):
    def set_pile(self, pile):
        self.pile = pile

    def card_pos(self, index):
        assert index >= 0

        # Default implementation
        return self.pos

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
    source = StringProperty()
    is_empty = BooleanProperty()

    def redraw(self):
        self.source = card2img(self.pile.top_card)
        self.is_empty = self.pile.is_empty


class PlayerPileWidget(PileWidget):
    source = StringProperty()
    is_empty = BooleanProperty()

    def redraw(self):
        if self.pile.is_empty:
            self.is_empty = True
            return
        self.is_empty = False

        if not self.pile[-1].face_up:
            self.source = card2img(self.pile[-1])
            return

        if len(self.pile) > 1:
            self.source = card2img(self.pile[-2])

        self.moving_card = MovingCard(self.pile[-1])
        app = App.get_running_app()
        app.root.add_widget(self.moving_card)
        self.moving_card.pos = self.to_parent(*self.pos)
        print(
            self.pile.name,
            self.pos,
            self.to_parent(*self.pos),
            self.to_parent(*self.pos, relative=True),
            self.to_window(*self.pos, relative=False),
            self.to_window(*self.pos, relative=True),
        )


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


class TableauRightPileWidget(TableauPileWidget):
    anchor = "x"

    def pos_anchor(self, i_card):
        return self.pos_offset_factor * i_card
