import random

from kivy.uix.scatterlayout import ScatterLayout
from kivy.properties import StringProperty
from kivy.animation import Animation

from ..images.card_deck import card2img

MAX_RANDOM_ANGLE = 5  # °

_DEBUG = False


def debug(*s):
    if _DEBUG:
        print(*s)


class CardWidget(ScatterLayout):
    source = StringProperty()

    def __init__(self, card, board_manager):
        super().__init__()
        self.card = card
        self.board_manager = board_manager
        self.source = card2img(card)

        self.pile_widget = None
        self._moving = False
        self._flipping = False
        self.main_rotation = 0

    def set_center_animated(self, pos):
        animation = Animation(center=pos, duration=0.1, transition="out_quad")
        animation.start(self)

    def update_image(self):
        self.source = card2img(self.card)

    def _random_rotation_animation(self):
        angle = self.main_rotation
        angle += random.triangular(-MAX_RANDOM_ANGLE, MAX_RANDOM_ANGLE)
        if self.rotation > 180:
            angle += 360
        return Animation(rotation=angle, duration=0.1, transition="out_sine")

    def apply_random_rotation(self):
        self._random_rotation_animation().start(self)

    def set_face_up(self):
        self.card.face_up = True
        self.flip_animation()

    def flip_animation(self):
        height = self.height
        animation = Animation(height=0, duration=0.25, transition="out_sine")
        animation.on_complete = lambda *args: self.update_image()
        animation += (
            Animation(height=height, duration=0.1, transition="in_sine")
            & self._random_rotation_animation()
        )
        animation.start(self)

    @property
    def is_top(self):
        return self.card == self.pile_widget.pile.top_card

    def on_touch_down(self, touch):
        if not self.collide_point(touch.x, touch.y):
            return False

        if not self.is_top:
            return False

        if self.board_manager.active_player is None:
            debug("End of game")
            return True

        debug("TOUCH DOWN", self.card)
        can_pop = self.pile_widget.pile.can_pop_card(self.board_manager.active_player)
        assert can_pop in (True, False), can_pop
        if not can_pop:
            return True

        if self.card.face_up:
            self._moving = True
            return super().on_touch_down(touch)
        else:
            self._flipping = True
            return True

    def on_touch_up(self, touch):
        super().on_touch_up(touch)

        if self.board_manager.active_player is None:
            debug("End of game")
            return True

        if not self._moving:
            if self._flipping:
                if self.collide_point(touch.x, touch.y):
                    self.board_manager.flip_card_up(self)
                else:
                    debug("Cancel flip")
                self._flipping = False
                return True
            else:
                return False

        debug("TOUCH UP", self.card)
        self._moving = False

        # Look for the pile the card was dropped on
        pile_widget = None
        for pile_widget in self.board_manager.pile_widgets:
            if pile_widget.collide_point(*self.center):
                break

        if pile_widget is None:
            debug(f"{self.card} not dropped on a pile, return it")
            self.set_center_animated(self.pile_widget.card_pos())
        elif pile_widget == self.pile_widget:
            debug(f"{self.card} dropped on same pile, return it")
            self.set_center_animated(self.pile_widget.card_pos())
        else:
            moved = self.board_manager.move_card(self, pile_widget)
            if not moved:
                self.set_center_animated(self.pile_widget.card_pos())

        self.apply_random_rotation()

        return True
