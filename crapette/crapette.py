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

from .core.board import Board
from .images.card_deck import CARD_IMG
from .widgets import pile_widgets  # Load widgets
from .widgets.board_widgets import BoardWidget


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

    def build(self):
        self.board = Board()

        # Just set the property so that it's available in kv
        self.card_overlap = CARD_IMG.OFFSET_FACTOR

        # Resize callback
        self.on_window_resize(Window, *Window.size)
        Window.bind(on_resize=self.on_window_resize)

        # Setup UI piles with game piles
        ids = self.root.ids
        self.pile_widgets = []
        for player, player_piles in enumerate(self.board.players_piles):
            self.pile_widgets.append(ids[f"player{player}stock"])
            self.pile_widgets.append(ids[f"player{player}waste"])
            self.pile_widgets.append(ids[f"player{player}crape"])
            ids[f"player{player}stock"].set_pile(player_piles.stock)
            ids[f"player{player}waste"].set_pile(player_piles.waste)
            ids[f"player{player}crape"].set_pile(player_piles.crape)
        for tableau, tableau_pile in enumerate(self.board.tableau_piles):
            self.pile_widgets.append(ids[f"tableau{tableau}"])
            ids[f"tableau{tableau}"].set_pile(tableau_pile)
        for foundation, foundation_pile in enumerate(self.board.foundation_piles):
            self.pile_widgets.append(ids[f"foundation{foundation}"])
            ids[f"foundation{foundation}"].set_pile(foundation_pile)

        # self.draw()

    def test(self):
        self.board_widget = BoardWidget(self.board, self)
        self.board_widget.build()
        self.board_widget.set_player_turn(0)

    def draw(self):
        for pile in self.pile_widgets:
            pile.redraw()

    def on_window_resize(self, window, width, height):
        self.card_height = height / self.board.NB_ROWS
        self.card_width = self.card_height * CARD_IMG.RATIO


if __name__ == "__main__":
    CrapetteApp().run()
