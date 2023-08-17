"""Kivy application for the crapette game.

Mostly used for initialisation and use of .kv file.
"""
import argparse
import os
import random
from inspect import getmodule
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
from . import (
    custom_test_games,
    widgets,  # ruff: noqa: F401
)
from .core.board import Board
from .game_manager import GameManager
from .images.card_data import CARD_IMG

kivy.require("1.10.0")
kivy.resources.resource_add_path(str(Path(__file__).parent))
kivy.config.Config.set("input", "mouse", "mouse,multitouch_on_demand")
Logger.setLevel(LOG_LEVELS["info"])  # debug, info, warning, error, critical, trace


# main app
class CrapetteApp(App):
    title = "Crapette in Kivy"
    icon = str(Path(__file__).parent / "images/png/2x/suit-spade.png")

    card_width: int = NumericProperty()
    card_height: int = NumericProperty()
    card_overlap: int = NumericProperty()
    wide: bool = BooleanProperty()

    def __init__(self, seed: int, custom: str, mono: bool, fast: bool):
        super().__init__()

        self.seed = seed
        self.custom = custom
        self.mono = mono
        self.fast = fast

    def build(self):
        # Just set the property so that it's available in kv
        self.card_overlap: float = CARD_IMG.OFFSET_FACTOR

        self.game_manager = GameManager(self)

        # Resize callback
        Window.bind(on_resize=self.on_window_resize)

        self._do_resize_event = None

    def on_window_resize(self, _window, width: int, height: int):
        if self._do_resize_event is not None:
            self._do_resize_event.cancel()

        layout_delay_s = 0.1  # s
        self._do_resize_event = Clock.schedule_once(
            lambda _dt: self.do_resize(width, height), layout_delay_s
        )

    def do_resize(self, width: int, height: int):
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

    def set_menu_visible(self, menu_visible: bool):
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

    def new_game(self, player0: str, player1: str):
        self.set_menu_visible(False)

        if self.custom:
            custom_new_game = getattr(custom_test_games, self.custom)
            Logger.info('Custom game: "%s"', self.custom)
        else:
            custom_new_game = None

            if self.seed is None:
                self.seed = int.from_bytes(os.urandom(8), "big")
            Logger.info("Game seed: %d", self.seed)
            random.seed(self.seed)
        self.game_manager.setup(player0, player1, custom_new_game)


def parse_args():
    parser = argparse.ArgumentParser(prog="crapette", description="Play Crapette")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-s",
        "--seed",
        type=int,
        help="Seed for a game, used to replay a given game. The seed of the games are given on game startup.",
    )

    custom_choices = [
        f
        for f in dir(custom_test_games)
        if not f.startswith("_")
        and f.islower()
        and getmodule(getattr(custom_test_games, f)) == custom_test_games
    ]
    group.add_argument(
        "-c",
        "--custom",
        choices=custom_choices,
        help="Name of a predetermined play, for testing purpose.",
    )
    parser.add_argument(
        "--mono",
        action="store_true",
        help="Don't run the AI in a separate process. Warning, this could block the interface in case of lengthy computation.",
    )
    parser.add_argument(
        "-f",
        "--fast",
        action="store_true",
        help="Speed up the AI animations.",
    )

    return parser.parse_args()


def main():
    args = parse_args()
    CrapetteApp(args.seed, args.custom, args.mono, args.fast).run()
