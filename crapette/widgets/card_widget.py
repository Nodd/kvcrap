from kivy.uix.scatterlayout import ScatterLayout
from kivy.properties import StringProperty

from ..images.card_deck import card2img


class CardWidget(ScatterLayout):
    source = StringProperty()

    def __init__(self, card, app):
        super().__init__()
        self.card = card
        self.app = app
        self.source = card2img(card)

        self.pile_widget = None
        self._last_pos = None
        self._moving = False

    def set_center_pos(self, pos):
        x, y = pos
        self.pos = (x - self.app.card_width / 2, y - self.app.card_height / 2)

    @property
    def is_top(self):
        return self.card == self.pile_widget.pile.top_card

    def on_touch_down(self, touch):
        if not self.collide_point(touch.x, touch.y):
            return

        if not self.is_top:
            print("Card not on top of its pile")
            return

        if touch.is_double_tap:
            print("DOUBLE TOUCH DOWN", self.card)
            return True

        print("TOUCH DOWN", self.card)
        self._moving = True
        self._last_pos = self.pos

        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        super().on_touch_up(touch)
        if not self._moving:
            return
        if touch.grab_current is not None:
            return
        if not self.collide_point(touch.x, touch.y):
            return

        self._moving = False

        # Look for the pile the card was dropped on
        pile_widget = None
        for pile_widget in self.app.board_manager.pile_widgets:
            if pile_widget.collide_point(touch.x, touch.y):
                print(pile_widget.pile.name)
                break

        if pile_widget is None:
            print("Not dropped on a pile")
            if self._last_pos:  # Just in case...
                self.pos = self._last_pos
        elif pile_widget == self.pile_widget:
            print("Dropped on origin pile")
            if self._last_pos:  # Just in case...
                self.pos = self._last_pos
        elif not pile_widget.pile.can_add_card(..., self.card):
            print("Dropped on an incompatible pile")
            if self._last_pos:  # Just in case...
                self.pos = self._last_pos
        else:
            self.app.board_manager.move_card(self, pile_widget)

        self._last_pos = None

        print("TOUCH UP", touch.grab_current, self.card)
        return False
