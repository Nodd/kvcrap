from kivy.uix.scatterlayout import ScatterLayout
from kivy.properties import StringProperty

from ..images.card_deck import card2img


class CardWidget(ScatterLayout):
    source = StringProperty()

    def __init__(self, card, app):
        super().__init__()
        self._card = card
        self._app = app
        self.source = card2img(card)

        self._last_pos = None

    def set_center_pos(self, x, y):
        self.pos = (x - self._app.card_width / 2, y - self._app.card_height / 2)

    def on_touch_down(self, touch):
        if not self.collide_point(touch.x, touch.y):
            return

        if touch.is_double_tap:
            print("DOUBLE TOUCH DOWN", self._card)
            return True

        print("TOUCH DOWN", self._card)

        self._last_pos = self.pos

        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        super().on_touch_up(touch)
        if touch.grab_current is not None:
            return
        if not self.collide_point(touch.x, touch.y):
            return

        # Look for the pile the card was dropped
        pile_widget = None
        for pile_widget in self._app.pile_widgets:
            if pile_widget.collide_point(touch.x, touch.y):
                print(pile_widget.pile.name)
                break

        if pile_widget is None:
            print("Not dropped on a pile")
            if self._last_pos:  # Just in case...
                self.pos = self._last_pos
        elif not pile_widget.pile.can_add_card(..., self._card):
            print("Dropped on an incompatible pile")
            if self._last_pos:  # Just in case...
                self.pos = self._last_pos
        else:
            self.set_center_pos(*pile_widget.card_pos(len(pile_widget.pile)))

        self._last_pos = None

        print("TOUCH UP", touch.grab_current, self._card)
        return False
