from .core.board import Board
from .widgets import pile_widgets  # Load widgets
from .widgets.card_widget import CardWidget


class BoardManager:
    def __init__(self, app):
        self.app = app

        self.pile_widgets = None
        self.board = None
        self.card_widgets = None

    def new_game(self):
        self.board = Board()
        self.setup_piles()
        self.fill_piles()

        # TODO : use correct first player
        self.set_player_turn(0)

    def setup_piles(self):
        # Setup UI piles with game piles
        ids = self.app.root.ids
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

    def fill_piles(self):
        self.card_widgets = {}
        for pile_widget in self.pile_widgets:
            # print(pile_widget.pile.name)
            for index, card in enumerate(pile_widget.pile):
                # print(pile_widget.card_pos(index), card)
                card_widget = CardWidget(card, self.app)
                card_widget.pile_widget = pile_widget
                card_widget.set_center_pos(pile_widget.card_pos(index))
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

    def move_card(self, card_widget, pile_widget):
        # Remove from previous pile
        old_pile_widget = card_widget.pile_widget
        old_pile_widget.pop_card()

        # Add to new pile
        pile_widget.add_card(card_widget)
        card_widget.pile_widget = pile_widget
        card_widget.set_center_pos(pile_widget.card_pos())