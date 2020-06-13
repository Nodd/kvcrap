import kivy

kivy.require("1.11.0")
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.image import Image
from kivy.properties import StringProperty, BooleanProperty, NumericProperty

from board import Board
from card_deck import card2img


class BackGround(FloatLayout):
    pass


class CardImage(Image):
    pass


class PileWidget(RelativeLayout):
    def set_pile(self, pile):
        self.pile = pile

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            if self.pile.is_empty:
                top_card = "Empty"
            else:
                top_card = self.pile.top_card
            print(self.pile.name, top_card)


class SquaredPileWidget(PileWidget):
    image = StringProperty()
    is_empty = BooleanProperty()

    def redraw(self):
        self.image = card2img(self.pile.top_card)
        self.is_empty = self.pile.is_empty


class FoundationPileWidget(SquaredPileWidget):
    pass


class PlayerPileWidget(SquaredPileWidget):
    pass


class TableauPileWidget(PileWidget):
    @property
    def pos_offset_factor(self):
        app = App.get_running_app()
        return app.card_overlap / (1 + 12 * app.card_overlap)

    def build(self):
        self.card_images = []
        for i_card in range(13):
            card_image = CardImage()
            card_image.opacity = 1
            card_image.pos_hint = {
                self.anchor: self.pos_anchor(i_card),
                "center_y": 0.5,
            }
            card_image.source = card2img(None)
            self.add_widget(card_image)
            self.card_images.append(card_image)

    def redraw(self):
        for card, card_image in zip(self.pile, self.card_images):
            card_image.source = card2img(card)
            card_image.opacity = 1
        for card_image in self.card_images[len(self.pile) :]:
            card_image.source = card2img(None)
            card_image.opacity = 0


class TableauLeftPileWidget(TableauPileWidget):
    anchor = "right"

    def pos_anchor(self, i_card):
        return 1 - (self.pos_offset_factor * i_card)


class TableauRightPileWidget(TableauPileWidget):
    anchor = "x"

    def pos_anchor(self, i_card):
        return self.pos_offset_factor * i_card


# main app
class CrapetteApp(App):
    title = "Crapette in Kivy"
    icon = "images/png/2x/suit-spade.png"

    card_ratio = NumericProperty()
    card_overlap = NumericProperty()

    def build(self):
        self.board = Board()
        ids = self.root.ids

        card_x = 338
        card_y = 498

        self.card_ratio = card_x / card_y
        self.card_overlap = 0.15

        for player, player_piles in enumerate(self.board.players_piles):
            ids[f"player{player}stock"].set_pile(player_piles.stock)
            ids[f"player{player}waste"].set_pile(player_piles.waste)
            ids[f"player{player}crape"].set_pile(player_piles.crape)
        for tableau, tableau_pile in enumerate(self.board.tableau_piles):
            ids[f"tableau{tableau}"].set_pile(tableau_pile)
            ids[f"tableau{tableau}"].build()
        for foundation, foundation_pile in enumerate(self.board.foundation_piles):
            ids[f"foundation{foundation}"].set_pile(foundation_pile)

        self.draw()

    def draw(self):
        ids = self.root.ids
        for player, player_piles in enumerate(self.board.players_piles):
            ids[f"player{player}stock"].redraw()
            ids[f"player{player}waste"].redraw()
            ids[f"player{player}crape"].redraw()
        for tableau, tableau_pile in enumerate(self.board.tableau_piles):
            ids[f"tableau{tableau}"].redraw()
        for foundation, foundation_pile in enumerate(self.board.foundation_piles):
            ids[f"foundation{foundation}"].redraw()


if __name__ == "__main__":
    CrapetteApp().run()
