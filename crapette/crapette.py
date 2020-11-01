from pathlib import Path

import kivy

kivy.require("1.10.0")
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.image import Image
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivy.core.window import Window

import kivy.resources

kivy.resources.resource_add_path(str(Path(__file__).parent))
print(str(Path(__file__).parent / "crapette"))

from .images.card_deck import CARD_IMG
from .board_manager import BoardManager
from .core.board import Board


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

    def new_game(self):
        self.board_manager.new_game()

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


if __name__ == "__main__":
    CrapetteApp().run()
