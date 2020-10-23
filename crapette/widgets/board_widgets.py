from kivy.uix.scatterlayout import ScatterLayout
from kivy.properties import StringProperty, BooleanProperty, NumericProperty

from ..images.card_deck import card2img, CARD_IMG


class BoardWidget:
    def __init__(self, board, app):
        self.board = board
        self.app = app

        self.pile_widgets = self.app.pile_widgets

        self.card_widgets = {}

    def build(self):
        for pile_widget in self.pile_widgets:
            # print(pile_widget.pile.name)
            for index, card in enumerate(pile_widget.pile):
                # print(pile_widget.card_pos(index), card)
                card_widget = MovingCard(card, self.app)
                card_widget.set_center_pos(*pile_widget.card_pos(index))
                card_widget.do_translation = False
                self.card_widgets[card] = card_widget
                self.app.root.add_widget(card_widget)

    def set_player_turn(self, player):
        self.active_player = player
        for pile_widget in self.pile_widgets:
            pile = pile_widget.pile
            print(pile.name, len(pile))
            if pile:
                print(pile.can_pop_card(player))
                self.card_widgets[pile[-1]].do_translation = pile.can_pop_card(player)


class MovingCard(ScatterLayout):
    source = StringProperty()

    def __init__(self, card, app):
        super().__init__()
        self._card = card
        self._app = app
        self.source = card2img(card)

    def set_center_pos(self, x, y):
        self.pos = (x - self._app.card_width / 2, y - self._app.card_height / 2)

    def on_touch_down(self, touch):
        if not self.collide_point(touch.x, touch.y):
            return

        if touch.is_double_tap:
            print("DOUBLE TOUCH DOWN", self._card)
            return True

        print("TOUCH DOWN", self._card)

        self._last_pos = self.pos

        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        super().on_touch_up(touch)
        if touch.grab_current is not None:
            return
        if not self.collide_point(touch.x, touch.y):
            return

        # Look for the pile the card was dropped
        for pile in self._app.pile_widgets:
            if pile.collide_point(touch.x, touch.y):
                print(pile.pile.name)
                break
        else:
            print("Not dropped on a pile")
            if self._last_pos:  # Just in case...
                self.pos = self._last_pos
        self._last_pos = None

        print("TOUCH UP", touch.grab_current, self._card)
        return False
