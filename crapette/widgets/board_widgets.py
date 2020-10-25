from .card_widget import CardWidget


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
                card_widget = CardWidget(card, self.app)
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
