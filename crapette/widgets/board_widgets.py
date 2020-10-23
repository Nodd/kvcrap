from kivy.uix.scatterlayout import ScatterLayout
from kivy.properties import StringProperty, BooleanProperty, NumericProperty

from ..images.card_deck import card2img, CARD_IMG


class BoardWidget:
    def __init__(self, board, app):
        self.board = board
        self.app = app

        self.card_widgets = {}

    def build(self):
        for pile in self.app.piles:
            print(pile.pile.name)
            for index, card in enumerate(pile.pile):
                print(pile.card_pos(index), card)
                card_widget = MovingCard(card, self.app)
                card_center_pos = pile.card_pos(index)
                card_widget.pos = (
                    card_center_pos[0] - self.app.card_width / 2,
                    card_center_pos[1] - self.app.card_height / 2,
                )
                self.card_widgets[card] = card_widget
                self.app.root.add_widget(card_widget)


class MovingCard(ScatterLayout):
    source = StringProperty()

    def __init__(self, card, app):
        super().__init__()
        self._card = card
        self._app = app
        self.source = card2img(card)

    def on_touch_down(self, touch):
        if not self.collide_point(touch.x, touch.y):
            return

        if touch.is_double_tap:
            print("double tap")
            return True

        print("tap", self._card)
        self._last_pos = self.pos

        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        super().on_touch_up(touch)
        if touch.grab_current is not None:
            return
        if not self.collide_point(touch.x, touch.y):
            return

        # Look for the pile the card was dropped
        for pile in self._app.piles:
            if pile.collide_point(touch.x, touch.y):
                print(pile.pile.name)
                break
        else:
            print("Not dropped on a pile")
            if self._last_pos:  # Just in case...
                self.pos = self._last_pos
            return False

        print("UP UP UP", touch, touch.grab_current, self._card)
        return False
