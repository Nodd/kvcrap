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
        self._flipping = False

    def set_center_pos(self, pos):
        x, y = pos
        self.pos = (x - self.app.card_width / 2, y - self.app.card_height / 2)

    def update_image(self):
        self.source = card2img(self.card)

    @property
    def is_top(self):
        return self.card == self.pile_widget.pile.top_card

    def on_touch_down(self, touch):
        if not self.collide_point(touch.x, touch.y):
            return False

        if not self.is_top:
            # print("Card not on top of its pile")
            return False

        if touch.is_double_tap:
            print("DOUBLE TOUCH DOWN", self.card)
            return True

        print("TOUCH DOWN", self.card)
        can_pop = self.pile_widget.pile.can_pop_card(
            self.app.board_manager.active_player
        )
        assert can_pop in (True, False), can_pop
        if not can_pop:
            return True

        if self.card.face_up:
            self._moving = True
            self._last_pos = self.pos

            return super().on_touch_down(touch)
        else:
            # TODO: test flippable by player
            self._flipping = True
            return True

    def on_touch_up(self, touch):
        super().on_touch_up(touch)
        if not self._moving:
            if self._flipping:
                if self.collide_point(touch.x, touch.y):
                    # Do the flip
                    self.card.face_up = True
                    self.update_image()
                else:
                    print("Cancel flip")
                self._flipping = False
                return True
            else:
                return False

        print("TOUCH UP", self.card)
        self._moving = False

        # Look for the pile the card was dropped on
        pile_widget = None
        for pile_widget in self.app.board_manager.pile_widgets:
            if pile_widget.collide_point(touch.x, touch.y):
                # print(pile_widget.pile.name)
                break

        if pile_widget is None:
            print(f"{self.card} not dropped on a pile, return it")
            if self._last_pos:  # Just in case...
                self.pos = self._last_pos
        elif pile_widget == self.pile_widget:
            print(f"{self.card} dropped on same pile, return it")
            if self._last_pos:  # Just in case...
                self.pos = self._last_pos
        else:
            moved = self.app.board_manager.move_card(self, pile_widget)
            if not moved and self._last_pos:  # Just in case...
                self.pos = self._last_pos

        self._last_pos = None
        return True
