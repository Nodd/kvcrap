from kivy.uix.scatterlayout import ScatterLayout
from kivy.properties import StringProperty, BooleanProperty, NumericProperty

from ..images.card_deck import card2img


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
                card_widget = MovingCard(card)
                card_widget.pos = pile.card_pos(index)
                self.card_widgets[card] = card_widget
                self.app.root.add_widget(card_widget)


class MovingCard(ScatterLayout):
    source = StringProperty()

    def __init__(self, card):
        super().__init__()
        self._card = card
        self.source = card2img(card)

    def on_touch_down(self, touch):
        if not self.collide_point(touch.x, touch.y):
            return

        if touch.is_double_tap:
            print("double tap")
            return True

        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        super().on_touch_up(touch)
        if touch.grab_current is not None:
            return
        if not self.collide_point(touch.x, touch.y):
            return
        print("UP UP UP", touch, touch.grab_current)
        return False
