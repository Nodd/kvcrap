"""Widget representing a card on the board."""

import random

from kivy.animation import Animation
from kivy.properties import StringProperty
from kivy.uix.scatterlayout import ScatterLayout

from crapette.images.card_data import card2img

MAX_RANDOM_ANGLE = 5  # °

_DEBUG = False


def debug(*s):
    if _DEBUG:
        print(*s)


class CardWidget(ScatterLayout):
    """Widget representing a card on the board."""

    source = StringProperty()

    def __init__(self, card, game_manager):
        self.card = card
        self.source = card2img(card)
        self.game_manager = game_manager

        self.pile_widget = None
        self._moving = False
        self._flipping = False
        self.main_rotation = 0

        # At the end so that repr() works in the kivy initalization
        super().__init__()

    def __repr__(self):
        return f"CardWidget({self.card!r})"

    def set_center_animated(self, pos):
        """Animate a card move on the board.

        `pos` is the new coordinates of the car center.

        This is only a visual effect, this function doesn't change
        the state of the game.
        """
        animation = Animation(center=pos, duration=0.1, transition="out_quad")
        animation.start(self)

    def update_image(self):
        """Show the correct image for the card.

        It can be the face or the back, depending on the card state.

        This is only a visual effect, this function doesn't change
        the state of the game.
        """
        self.source = card2img(self.card)

    def random_rotation_animation_factory(self, duration=0.1):
        """Create an Animation to display the card with a random rotation error.

        It's just for fun, to make it look like the card was placed by hand on the board,
        not perfectly aligned.

        This is only a visual effect, this function doesn't change
        the state of the game.
        """
        angle = self.main_rotation
        angle += random.triangular(-MAX_RANDOM_ANGLE, MAX_RANDOM_ANGLE)
        if self.rotation > 180:
            angle += 360
        return Animation(rotation=angle, duration=duration, transition="out_sine")

    def apply_random_rotation(self, main_rotation: float = None):
        """Apply a random rotation error.

        Optionally change the global rotation of the card, for example on the foundation piles.

        This is only a visual effect, this function doesn't change
        the state of the game.
        """
        if main_rotation is not None:
            self.main_rotation = main_rotation
        self.random_rotation_animation_factory().start(self)

    def set_face_up(self):
        """Flip the card so that the face is up.

        This changes the underlying card model accordingly.
        """
        self.card.face_up = True
        self.flip_animation()

    def set_face_down(self):
        """Flip the card so that the face is down.

        This changes the underlying card model accordingly.
        """
        self.card.face_up = False
        self.flip_animation()

    def flip_animation(self):
        """Animate a card flip.

        This is only a visual effect, this function doesn't change
        the state of the game.
        """
        # Save state
        height = self.height
        y = self.y

        # Fade out by reducing the height and compensing the position so that the center doesn't change
        duration_out = 0.2
        animation = Animation(height=0, duration=duration_out, transition="out_sine")
        animation &= Animation(
            y=y + height / 2, duration=duration_out, transition="out_sine"
        )

        # Update the image after the first animation
        animation.on_complete = lambda *args: self.update_image()

        # Fade in by restoring the height and the position, while adding a small rotation error
        duration_in = 0.1
        animation += (
            Animation(height=height, duration=duration_in, transition="in_sine")
            & Animation(y=y, duration=duration_in, transition="in_sine")
            & self.random_rotation_animation_factory()
        )
        animation.start(self)

    @property
    def is_top(self):
        """Check if the card is on the top of its pile.

        This is only an information return, this property doesn't change
        the state of the game.
        """
        # TODO: avoid using a reference to the pile widget, but how ?
        return self.card == self.pile_widget.pile.top_card

    def on_touch_down(self, touch):
        """Start a movement when the card is pressed down, if the current player has the right to do it.

        Return `False` to continue event propagation, or `True` to stop it.
        """
        # All objects receive all events, manage only when the touch event is on the card
        if not self.collide_point(touch.x, touch.y):
            return False

        # If there are other cards on top, the player can do nothing with it.
        if not self.is_top:
            return False

        # Stop the event if this is the end of the game.
        if self.game_manager.active_player is None:
            debug("End of game")
            return True

        # Check if the card can be moved by the player
        # TODO: avoid using self.pile_widget and self.game_manager, how ?
        debug("TOUCH DOWN", self.card)
        can_pop = self.pile_widget.pile.can_pop_card(self.game_manager.active_player)
        assert can_pop in (True, False), can_pop
        if not can_pop:
            return True

        if self.card.face_up:
            self._moving = True
            return super().on_touch_down(touch)

        self._flipping = True
        return True

    def on_touch_up(self, touch):
        super().on_touch_up(touch)

        if self.game_manager.active_player is None:
            debug("End of game")
            return True

        if not self._moving:
            if not self._flipping:
                return False

            if self.collide_point(touch.x, touch.y):
                self.game_manager.flip_card_up(self)
            else:
                debug("Cancel flip")
            self._flipping = False
            return True
        debug("TOUCH UP", self.card)
        self._moving = False

        # Look for the pile the card was dropped on
        pile_widget = None
        for pile_widget in self.game_manager.board_widget.pile_widgets:
            if pile_widget.collide_point(*self.center):
                break

        if pile_widget is None:
            debug(f"{self.card} not dropped on a pile, return it")
            self.set_center_animated(self.pile_widget.card_pos())
        elif pile_widget == self.pile_widget:
            debug(f"{self.card} dropped on same pile, return it")
            self.set_center_animated(self.pile_widget.card_pos())
        else:
            moved = self.game_manager.move_card(self, pile_widget)
            if not moved:
                self.set_center_animated(self.pile_widget.card_pos())

        self.apply_random_rotation()

        return True
