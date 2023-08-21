"""Widget representing a card on the board."""

import random
import typing

from kivy.animation import Animation
from kivy.app import App
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.properties import StringProperty
from kivy.uix.scatterlayout import ScatterLayout

from crapette.core.cards import Card
from crapette.images.card_data import card2img

if typing.TYPE_CHECKING:
    from .pile_widgets import PileWidget

MAX_RANDOM_ANGLE = 5  # °
DEFAULT_MOVE_DURATION = 0.1  # s
DEFAULT_FLIP_DURATION = 0.3  # s


class CardWidget(ScatterLayout):
    """Widget representing a card on the board."""

    source = StringProperty()

    def __init__(self, card: Card, game_manager):
        self.card = card
        self.source = card2img(card)
        self.game_manager = game_manager
        self.game_config = game_manager.game_config

        self.pile_widget: PileWidget | None = None
        self._moving = False
        self._flipping = False
        self.main_rotation = 0

        # At the end so that repr() works in the kivy initalization
        super().__init__()

    def __repr__(self):
        return f"CardWidget({self.card!r})"

    def animate_move_to_pile(self, duration=DEFAULT_MOVE_DURATION):
        """Animate a card on the board to move to its pile.

        It also applies a random rotation error, as if the card was put manually.

        This is only a visual effect, this function doesn't change
        the state of the game.
        """
        animation = Animation(
            center=self.pile_widget.card_pos(),
            duration=duration,
            transition="out_quad",
        )
        animation &= self.random_rotation_animation_factory(duration)
        animation.start(self)

    def update_image(self):
        """Show the correct image for the card.

        It can be the face or the back, depending on the card state.

        This is only a visual effect, this function doesn't change
        the state of the game.
        """
        self.source = card2img(self.card)

    def random_rotation_animation_factory(self, duration=DEFAULT_MOVE_DURATION):
        """Create an Animation to display the card with a random rotation error.

        It's just for fun, to make it look like the card was placed by hand on the board,
        not perfectly aligned.

        This is only a visual effect, this function doesn't change
        the state of the game.
        """
        angle = self.pile_widget.rotation
        angle += random.triangular(-MAX_RANDOM_ANGLE, MAX_RANDOM_ANGLE)
        if self.rotation > 180:
            angle += 360
        return Animation(rotation=angle, duration=duration, transition="out_sine")

    def set_face_up(self, duration=DEFAULT_FLIP_DURATION):
        """Flip the card so that the face is up.

        This changes the underlying card model accordingly.
        """
        self.card.face_up = True
        self.flip_animation(duration)

    def set_face_down(self, duration=DEFAULT_FLIP_DURATION):
        """Flip the card so that the face is down.

        This changes the underlying card model accordingly.
        """
        self.card.face_up = False
        self.flip_animation(duration)

    def flip_animation(self, duration=DEFAULT_FLIP_DURATION):
        """Animate a card flip.

        This is only a visual effect, this function doesn't change
        the state of the game.
        """
        # Save state
        height = self.height
        center = self.center

        # Fade out by reducing the height and compensing the position so that the center doesn't change
        duration_out = duration * 2 / 3
        animation = Animation(height=0, duration=duration_out, transition="out_sine")
        animation &= Animation(
            center=center, duration=duration_out, transition="out_sine"
        )

        # Update the image after the first animation
        animation.on_complete = lambda *args: self.update_image()

        # Fade in by restoring the height and the position, while adding a small rotation error
        duration_in = duration / 3
        animation += (
            Animation(height=height, duration=duration_in, transition="in_sine")
            & Animation(center=center, duration=duration_in, transition="in_sine")
            & self.random_rotation_animation_factory(DEFAULT_FLIP_DURATION)
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
        if self.game_config.active_player is None:
            Logger.debug("End of game")
            return True

        # Check if the card can be moved by the player
        # TODO: avoid using self.pile_widget, how ?
        Logger.debug("TOUCH DOWN %s", self.card)
        can_pop = self.pile_widget.pile.can_pop_card(self.game_config.active_player)
        assert can_pop in (True, False), can_pop
        if not can_pop:
            return True

        if self.card.face_up:
            self._moving = True
            self.start_moving_animation()
            return super().on_touch_down(touch)

        self._flipping = True
        return True

    def on_touch_up(self, touch):
        super().on_touch_up(touch)

        if self.game_config.active_player is None:
            Logger.debug("End of game")
            return True

        if not self._moving:
            if not self._flipping:
                return False

            if self.collide_point(touch.x, touch.y):
                self.game_manager.flip_card_up(self)
            else:
                Logger.debug("Cancel flip")
            self._flipping = False
            return True
        Logger.debug("TOUCH UP %s", self.card)
        self._moving = False
        self.finish_moving_animation()

        # Look for the pile the card was dropped on
        pile_widget = None
        for pile_widget in self.game_manager.board_widget.pile_widgets:
            if pile_widget.collide_point(*self.center):
                break

        if pile_widget is None:
            Logger.debug("%s not dropped on a pile, return it", self.card)
            self.animate_move_to_pile()
        elif pile_widget == self.pile_widget:
            Logger.debug("%s dropped on same pile, return it", self.card)
            self.animate_move_to_pile()
        else:
            self.game_manager.move_card(self, pile_widget)

        return True

    def abort_moving(self):
        """Brutaly cancel the card movement.

        Used when crapette mode starts.
        """
        if self._moving:
            self._moving = False
            self.animate_move_to_pile()

    def start_moving_animation(self):
        Window.show_cursor = False
        app = App.get_running_app()
        zoom_factor = 1.1
        animation = Animation(
            height=app.card_height * zoom_factor,
            duration=DEFAULT_MOVE_DURATION,
            transition="out_sine",
        )
        animation &= Animation(
            width=app.card_width * zoom_factor,
            duration=DEFAULT_MOVE_DURATION,
            transition="out_sine",
        )
        animation &= self.random_rotation_animation_factory()
        animation.start(self)

    def finish_moving_animation(self):
        Window.show_cursor = True
        app = App.get_running_app()
        animation = Animation(
            height=app.card_height,
            duration=DEFAULT_MOVE_DURATION,
            transition="out_sine",
        )
        animation &= Animation(
            width=app.card_width, duration=DEFAULT_MOVE_DURATION, transition="out_sine"
        )
        animation.start(self)
