"""
Kivy application for the crapette game

Mostly used for initialisation and use of .kv file.
"""

from pathlib import Path

import kivy
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.properties import BooleanProperty, NumericProperty
from kivy.core.window import Window
import kivy.config
import kivy.resources

kivy.require("1.10.0")
kivy.resources.resource_add_path(str(Path(__file__).parent))
kivy.config.Config.set("input", "mouse", "mouse,multitouch_on_demand")

from .images.card_deck import CARD_IMG
from .board_manager import BoardManager
from .core.board import Board
from .widgets import pile_widgets  # Load widgets


class BackGround(FloatLayout):
    pass


class CardImage(Image):
    pass


# main app
class CrapetteApp(App):
    title = "Crapette in Kivy"
    icon = str(Path(__file__).parent / "images/png/2x/suit-spade.png")

    card_width = NumericProperty()
    card_height = NumericProperty()
    card_overlap = NumericProperty()
    wide = BooleanProperty()

    def build(self):
        # Just set the property so that it's available in kv
        self.card_overlap = CARD_IMG.OFFSET_FACTOR

        self.board_manager = BoardManager(self)

        # Resize callback
        self.on_window_resize(Window, *Window.size)
        Window.bind(on_resize=self.on_window_resize)

    def on_window_resize(self, window, width, height):
        self.card_height = height / Board.NB_ROWS
        self.card_width = self.card_height * CARD_IMG.RATIO

        game_width_max = 2 * (
            self.card_height + self.card_width * (1 + 12 * self.card_overlap)
        )
        game_width_min = 2 * (
            self.card_width + self.card_width * (1 + 12 * self.card_overlap)
        )
        game_height = self.card_height * Board.NB_ROWS
        self.wide = width / height > game_width_max / game_height

        self.board_manager.place_cards()

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
        self.board_manager.new_game()


def main():
    CrapetteApp().run()
