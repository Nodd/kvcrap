import random

from kivy.uix.scatterlayout import ScatterLayout
from kivy.properties import StringProperty
from kivy.animation import Animation

from ..images.card_deck import card2img

MAX_RANDOM_ANGLE = 5  # °


class CardWidget(ScatterLayout):
    source = StringProperty()

    def __init__(self, card, app):
        super().__init__()
        self.card = card
        self.app = app
        self.source = card2img(card)

        self.pile_widget = None
        self._moving = False
        self._flipping = False
        self._rotation_error = 0

    def set_center_pos(self, pos, animate=True):
        x, y = pos
        x -= self.app.card_width / 2
        y -= self.app.card_height / 2
        if animate:
            animation = Animation(x=x, y=y, duration=0.1, transition="out_quad")
            animation.start(self)
        else:
            self.pos = x, y

    def update_image(self):
        self.source = card2img(self.card)

    def _random_rotation_animation(self):
        angle = random.triangular(-MAX_RANDOM_ANGLE, MAX_RANDOM_ANGLE)
        if self.rotation > 180:
            angle += 360
        return Animation(rotation=angle, duration=0.1, transition="out_sine")

    def apply_random_rotation(self):
        self._random_rotation_animation().start(self)

    @property
    def is_top(self):
        return self.card == self.pile_widget.pile.top_card

    def on_touch_down(self, touch):
        if not self.collide_point(touch.x, touch.y):
            return False

        if not self.is_top:
            return False

        if touch.is_double_tap:
            print("DOUBLE TOUCH DOWN", self.card)
            return True

        if self.app.board_manager.active_player is None:
            print("End of game")
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
            return super().on_touch_down(touch)
        else:
            self._flipping = True
            return True

    def on_touch_up(self, touch):
        super().on_touch_up(touch)

        if self.app.board_manager.active_player is None:
            print("End of game")
            return True

        if not self._moving:
            if self._flipping:
                if self.collide_point(touch.x, touch.y):
                    # Do the flip
                    self.card.face_up = True
                    height = self.height
                    animation = Animation(
                        height=0, duration=0.25, transition="out_sine"
                    )
                    animation.on_complete = lambda *args: self.update_image()
                    animation += (
                        Animation(height=height, duration=0.1, transition="in_sine")
                        & self._random_rotation_animation()
                    )
                    animation.start(self)
                else:
                    print("Cancel flip")
                self._flipping = False
                return True
            else:
                return False

        self.apply_random_rotation()

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
            self.set_center_pos(self.pile_widget.card_pos())
        elif pile_widget == self.pile_widget:
            print(f"{self.card} dropped on same pile, return it")
            self.set_center_pos(self.pile_widget.card_pos())
        else:
            moved = self.app.board_manager.move_card(self, pile_widget)
            if not moved:
                self.set_center_pos(self.pile_widget.card_pos())

        return True
