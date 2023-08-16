"""Kivy application for the crapette game.

Mostly used for initialisation and use of .kv file.
"""

import os
import random
import sys
from pathlib import Path

import kivy
import kivy.config
import kivy.resources
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.logger import LOG_LEVELS, Logger
from kivy.properties import BooleanProperty, NumericProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image

# Load all widgets
from . import widgets  # ruff: noqa: F401
from .core.board import Board
from .game_manager import GameManager
from .images.card_data import CARD_IMG

kivy.require("1.10.0")
kivy.resources.resource_add_path(str(Path(__file__).parent))
kivy.config.Config.set("input", "mouse", "mouse,multitouch_on_demand")
Logger.setLevel(LOG_LEVELS["info"])  # debug, info, warning, error, critical, trace


class BackGround(FloatLayout):
    pass


class CardImage(Image):
    pass


# main app
class CrapetteApp(App):
    title = "Crapette in Kivy"
    icon = str(Path(__file__).parent / "images/png/2x/suit-spade.png")

    card_width: int = NumericProperty()
    card_height: int = NumericProperty()
    card_overlap: int = NumericProperty()
    wide: bool = BooleanProperty()

    def build(self):
        # Just set the property so that it's available in kv
        self.card_overlap: float = CARD_IMG.OFFSET_FACTOR

        self.game_manager = GameManager(self)

        # Resize callback
        Window.bind(on_resize=self.on_window_resize)

        self._do_resize_event = None

    def on_window_resize(self, _window, width, height):
        if self._do_resize_event is not None:
            self._do_resize_event.cancel()

        layout_delay_s = 0.1  # s
        self._do_resize_event = Clock.schedule_once(
            lambda _dt: self.do_resize(width, height), layout_delay_s
        )

    def do_resize(self, width, height):
        """Delay the layout computing to avoid visual lag."""
        self.card_height = height / Board.NB_ROWS
        self.card_width = self.card_height * CARD_IMG.RATIO

        game_width_max = 2 * (
            self.card_height + self.card_width * (1 + 12 * self.card_overlap)
        )
        # game_width_min = 2 * (
        #     self.card_width + self.card_width * (1 + 12 * self.card_overlap)
        # )
        game_height = self.card_height * Board.NB_ROWS
        self.wide = width / height > game_width_max / game_height

    def set_menu_visible(self, menu_visible):
        ids = self.root.ids

        menu = ids["menu"]
        menu.opacity = float(menu_visible)
        menu.disabled = not menu_visible
        menu.size_hint = (None, None) if menu_visible else (0, 0)
        if menu_visible:
            # Menu on top
            self.root.remove_widget(menu)
            self.root.add_widget(menu)
        menu.size = self.root.size

        menu_button = ids["menu_button"]
        menu_button.opacity = float(not menu_visible)
        menu_button.disabled = menu_visible

        game_board = ids["game_board"]
        game_board.disabled = menu_visible

    def new_game(self):
        self.set_menu_visible(False)

        custom_new_game = None
        seed = None

        if len(sys.argv) >= 2:
            arg = sys.argv[1]
            try:
                seed = int(arg)
            except ValueError:
                from crapette import custom_test_games

                custom_new_game = getattr(custom_test_games, arg)

        if seed is None:
            seed = int.from_bytes(os.urandom(8), "big")
            Logger.info("Game seed: %d", seed)
        random.seed(seed)
        self.game_manager.setup(custom_new_game)


def main():
    CrapetteApp().run()
