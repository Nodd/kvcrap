"""
Manage the widgets interaction on the game board
"""

from kivy.animation import Animation

from .core.board import Board, Move, Flip, FlipWaste
from .core.piles import WastePile, FoundationPile
from .widgets.pile_widgets import PlayerPileWidget
from .widgets.card_widget import CardWidget

from .brain.brain import Brain
from .brain.brainforce import BrainForce


_DEBUG = False


def debug(*s):
    if _DEBUG:
        print(*s)


class BoardManager:
    def __init__(self, app):
        self.app = app

        self.pile_widgets = None
        self.board = None
        self.card_widgets = None
        self.active_player = None
        ids = self.app.root.ids
        self.background_halo = ids["background_halo"]
        self.background_crapette = ids["background_crapette"]

    def new_game(self):
        self.board = Board()
        self.setup_piles()
        self.add_card_widgets()
        self.place_cards()
        self.update_counts()

        self.set_player_turn(self.board.compute_first_player())

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

    def add_card_widgets(self):
        if self.card_widgets:
            for card_widget in self.card_widgets.values():
                self.app.root.remove_widget(card_widget)
        self.card_widgets = {}
        for pile_widget in self.pile_widgets:
            for card in pile_widget.pile:
                card_widget = CardWidget(card, self)
                card_widget.pile_widget = pile_widget
                self.card_widgets[card] = card_widget
                self.app.root.add_widget(card_widget)

    def place_cards(self):
        if not self.pile_widgets:
            return
        for pile_widget in self.pile_widgets:
            for index, card in enumerate(pile_widget.pile):
                card_widget = self.card_widgets[card]
                card_widget.center = pile_widget.card_pos(index)
        self.background_halo.y = 0 if self.active_player == 0 else self.app.root.height

    def set_player_turn(self, player):
        duration = 0.5
        self.active_player = player
        self.crapette_mode = False
        self.moves = []
        ids = self.app.root.ids
        next_player_btn = ids[f"player{player}crapebutton"]
        prev_player_btn = ids[f"player{1 - player}crapebutton"]
        next_player_btn.disabled = False
        prev_player_btn.disabled = True

        Animation(opacity=0, duration=duration, transition="out_cubic").start(
            prev_player_btn
        )

        Animation(opacity=1, duration=duration, transition="out_cubic").start(
            next_player_btn
        )

        Animation(
            y=0 if player == 0 else self.app.root.height,
            duration=duration,
            transition="in_out_expo",
        ).start(self.background_halo)

        # Brain(self.board, self.active_player).checks()
        BrainForce(self.board, self.active_player).compute_states()

    def update_counts(self):
        ids = self.app.root.ids
        for player in range(self.board.NB_PLAYERS):
            stock_pile = ids[f"player{player}stock"].pile
            crape_pile = ids[f"player{player}crape"].pile
            stock_label = ids[f"player{player}stockcount"]
            crape_label = ids[f"player{player}crapecount"]
            stock_label.text = str(len(stock_pile)) if stock_pile else ""
            crape_label.text = str(len(crape_pile)) if crape_pile else ""

    def move_card(self, card_widget, pile_widget):
        """Move a card to another pile.

        Return True if the card was moved, or False if the move is not possible.
        """
        old_pile_widget = card_widget.pile_widget

        can_add = pile_widget.pile.can_add_card(
            card_widget.card, old_pile_widget.pile, self.active_player
        )
        assert can_add in (True, False), can_add
        if not can_add:
            debug("Dropped on an incompatible pile")
            return False

        # Remove from previous pile
        old_pile_widget.pop_card()

        # Add to new pile
        pile_widget.add_card(card_widget)
        card_widget.pile_widget = pile_widget
        card_widget.set_center_animated(pile_widget.card_pos())
        self.update_counts()
        self.store_player_move(Move(card_widget, old_pile_widget, pile_widget))

        # Special case for foundation
        if isinstance(pile_widget.pile, FoundationPile):
            card_widget.main_rotation = pile_widget.rotation

            # Flip foundation pile if full
            if pile_widget.pile.is_full:
                for card in pile_widget.pile:
                    card.face_up = False
                    self.card_widgets[card].update_image()

        self.check_win()
        self.check_end_of_turn(pile_widget)

        #  Brain(self.board, self.active_player).checks()
        BrainForce(self.board, self.active_player).compute_states()

        return True

    def store_player_move(self, move):
        # UNFINISHED

        if isinstance(move, Flip):
            # Too late for preceeding crapettes, reset history
            self.moves = [move]
        elif isinstance(move, Move):
            if (
                isinstance(move.destination, PlayerPileWidget)
                and move.destination.pile.player != self.active_player
            ):
                # Too late for preceeding crapettes, reset history
                self.moves = [move]
            elif self.moves:
                self.moves.append(move)
            else:
                pass
        elif isinstance(move, FlipWaste):
            self.moves.append(move)

    def check_win(self):
        ids = self.app.root.ids
        stock_widget = ids[f"player{self.active_player}stock"]
        waste_widget = ids[f"player{self.active_player}waste"]
        crape_widget = ids[f"player{self.active_player}crape"]
        if not stock_widget.pile and not waste_widget.pile and not crape_widget.pile:
            print(f"Player {self.active_player} wins !!!")
            self.active_player = None
            for card_widget in self.card_widgets.values():
                card_widget.do_translation = False
            return True

    def check_end_of_turn(self, pile_widget):
        if (
            isinstance(pile_widget.pile, WastePile)
            and pile_widget.pile.player == self.active_player
        ):
            self.set_player_turn(1 - self.active_player)

    def flip_card_up(self, card_widget):
        card_widget.set_face_up()
        self.store_player_move(Flip(card_widget, card_widget.pile_widget))

        #  Brain(self.board, self.active_player).checks()
        BrainForce(self.board, self.active_player).compute_states()

    def flip_waste_to_stock(self):
        ids = self.app.root.ids
        stock_widget = ids[f"player{self.active_player}stock"]
        waste_widget = ids[f"player{self.active_player}waste"]

        # Update model
        stock_widget.pile.set_cards(waste_widget.pile[::-1])
        waste_widget.pile.clear()

        # Update cards
        for index, card in enumerate(stock_widget.pile):
            card.face_up = False
            card_widget = self.card_widgets[card]
            card_widget.update_image()
            card_widget.pile_widget = stock_widget
            card_widget.set_center_animated(stock_widget.card_pos(index))

            # Re-add widget for correct order
            self.app.root.remove_widget(card_widget)
            self.app.root.add_widget(card_widget)
        self.update_counts()

        self.store_player_move(FlipWaste())

    def on_crapette(self):
        ids = self.app.root.ids
        crapette_button = ids[f"player{self.active_player}crapebutton"]

        self.crapette_mode = not self.crapette_mode

        self.background_crapette.opacity = 1 if self.crapette_mode else 0
        crapette_button.text = (
            "Cancel ! (Sorry...)" if self.crapette_mode else "Crapette !"
        )
