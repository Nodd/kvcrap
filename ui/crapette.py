import kivy

kivy.require("1.11.0")
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.image import Image
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivy.core.window import Window

from board import Board
from card_deck import CardDeck


class BackGround(FloatLayout):
    pass


class CardImage(Image):
    pass


class PileWidget(RelativeLayout):
    def set_pile(self, pile):
        self.pile = pile

    # def on_touch_down(self, touch):
    #     if not self.collide_point(touch.x, touch.y):
    #         return

    #     if self.pile.is_empty:
    #         print("DOWN", self.pile.name, "Empty")
    #         return

    #     top_card = self.pile.top_card
    #     print("DOWN", self.pile.name, top_card)

    # def on_touch_up(self, touch):
    #     if not self.collide_point(touch.x, touch.y):
    #         return

    #     if self.pile.is_empty:
    #         top_card = "Empty"
    #     else:
    #         top_card = self.pile.top_card
    #     print("UP", self.pile.name, top_card)


class FoundationPileWidget(PileWidget):
    source = StringProperty()
    is_empty = BooleanProperty()

    def redraw(self):
        self.source = card2img(self.pile.top_card)
        self.is_empty = self.pile.is_empty


class PlayerPileWidget(PileWidget):
    source = StringProperty()
    is_empty = BooleanProperty()

    def redraw(self):
        if self.pile.is_empty:
            self.is_empty = True
            return
        self.is_empty = False

        if not self.pile[-1].face_up:
            self.source = card2img(self.pile[-1])
            return

        if len(self.pile) > 1:
            self.source = card2img(self.pile[-2])

        self.moving_card = MovingCard(self.pile[-1])
        app = App.get_running_app()
        app.root.add_widget(self.moving_card)
        self.moving_card.pos = self.to_parent(*self.pos)
        print(
            self.pile.name,
            self.pos,
            self.to_parent(*self.pos),
            self.to_parent(*self.pos, relative=True),
            self.to_window(*self.pos, relative=False),
            self.to_window(*self.pos, relative=True),
        )


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


class MovingCard(ScatterLayout):
    source = StringProperty()

    def __init__(self, card):
        super().__init__()
        self._card = card
        self.source = card2img(card)

    def on_touch_down(self, touch):
        if not self.collide_point(touch.x, touch.y):
            return

        if touch.is_double_tap:
            print("double tap")
            return True

        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        super().on_touch_up(touch)
        if touch.grab_current is not None:
            return
        print("UP UP UP", touch, touch.grab_current)
        return False


# main app
class CrapetteApp(App):
    title = "Crapette in Kivy"
    icon = "images/png/2x/suit-spade.png"

    card_width = NumericProperty()
    card_height = NumericProperty()
    card_overlap = NumericProperty()

    def build(self):
        self.board = Board()
        self.cards_deck = CardDeck()

        # Just set the property so that it's available in kv
        self.card_overlap = self.cards_deck.overlap

        # Resize callback
        self.on_window_resize(Window, *Window.size)
        Window.bind(on_resize=self.on_window_resize)

        # Setup UI piles with game piles
        ids = self.root.ids
        for player, player_piles in enumerate(self.board.players_piles):
            ids[f"player{player}stock"].set_pile(player_piles.stock)
            ids[f"player{player}waste"].set_pile(player_piles.waste)
            ids[f"player{player}crape"].set_pile(player_piles.crape)
        for tableau, tableau_pile in enumerate(self.board.tableau_piles):
            ids[f"tableau{tableau}"].set_pile(tableau_pile)
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

    def on_window_resize(self, window, width, height):
        self.card_height = height / self.board.NB_ROWS
        self.card_width = self.card_height * self.cards_deck.ratio


if __name__ == "__main__":
    CrapetteApp().run()
