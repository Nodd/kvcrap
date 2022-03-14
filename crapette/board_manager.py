"""
Manage the widgets interaction on the game board
"""
from pprint import pprint

from kivy.animation import Animation

from .core.board import Board
from .core.piles import WastePile, FoundationPile
from .core.moves import Moves, Move, Flip, FlipWaste
from .widgets.pile_widgets import PlayerPileWidget
from .widgets.card_widget import CardWidget

from .brain.brain import Brain
from .brain.brainforce import BrainForce


_DEBUG = False

TRANSITION_DURATION = 0.5


def debug(*s):
    if _DEBUG:
        print(*s)


class BoardManager:
    def __init__(self, app):
        self.app = app

        self.board = None
        self.pile_widgets = None
        self.card_widgets = None
        self.active_player = None
        ids = self.app.root.ids
        self.background_halo = ids["background_halo"]
        self.background_crapette = ids["background_crapette"]

    def new_game(self):
        """Prepare and initialize the board for a new game"""
        self.board = Board()
        self.setup_piles()
        self.add_card_widgets()
        self.place_cards()
        self.update_counts()

        self.set_player_turn(self.board.compute_first_player())

    def setup_piles(self):
        """Configures the piles.

        Configures the relation between the pile widgets and the backend piles, and
        updates the `pile_widgets` list."""
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
        """Creates and add a widget for every card.

        Updates the `card_widgets` list.

        The cards are not placed on the board, see `place_cards`.
        """
        # Remove previous card widgets
        if self.card_widgets:
            for card_widget in self.card_widgets.values():
                self.app.root.remove_widget(card_widget)

        # Add all card widgets
        self.card_widgets = {}
        for pile_widget in self.pile_widgets:
            for card in pile_widget.pile:
                card_widget = CardWidget(card, self)
                card_widget.pile_widget = pile_widget
                self.card_widgets[card] = card_widget
                self.app.root.add_widget(card_widget)

    def place_cards(self):
        """Resets the card widget positions in the piles and the halo position."""
        if not self.pile_widgets:
            return
        for pile_widget in self.pile_widgets:
            for index, card in enumerate(pile_widget.pile):
                card_widget = self.card_widgets[card]
                card_widget.center = pile_widget.card_pos(index)
        self.background_halo.y = 0 if self.active_player == 0 else self.app.root.height

    def set_player_turn(self, player):
        """Changes the active player and updates the GUI accordingly"""
        self.active_player = player
        self.crapette_mode = False
        self.moves = Moves()
        ids = self.app.root.ids

        next_player_btn = ids[f"player{player}crapebutton"]
        next_player_btn.disabled = False
        Animation(
            opacity=1, duration=TRANSITION_DURATION, transition="out_cubic"
        ).start(next_player_btn)

        prev_player_btn = ids[f"player{1 - player}crapebutton"]
        prev_player_btn.disabled = True
        Animation(
            opacity=0, duration=TRANSITION_DURATION, transition="out_cubic"
        ).start(prev_player_btn)

        Animation(
            y=0 if player == 0 else self.app.root.height,
            duration=TRANSITION_DURATION,
            transition="in_out_expo",
        ).start(self.background_halo)

        # Brain(self.board, self.active_player).checks()
        BrainForce(self.board, self.active_player).compute_states()

    def update_counts(self):
        """Update displayed card counts"""
        ids = self.app.root.ids
        for player in range(self.board.NB_PLAYERS):
            stock_pile = ids[f"player{player}stock"].pile
            crape_pile = ids[f"player{player}crape"].pile
            stock_label = ids[f"player{player}stockcount"]
            crape_label = ids[f"player{player}crapecount"]
            stock_label.text = str(len(stock_pile)) if stock_pile else ""
            crape_label.text = str(len(crape_pile)) if crape_pile else ""

    def move_card(self, card_widget, pile_widget):
        """Move a card to another pile and register the move.

        Returns True if the card was moved, or False if the move is not possible.
        It only checks the destination, not if the card was movable by the player.
        """
        old_pile_widget = card_widget.pile_widget

        can_add = pile_widget.pile.can_add_card(
            card_widget.card, old_pile_widget.pile, self.active_player
        )
        assert can_add in (True, False), can_add
        if not can_add:
            debug("Dropped on an incompatible pile")
            return False

        self._move_card(card_widget, pile_widget)

        self.update_counts()
        self.moves.record_move(card_widget, old_pile_widget, pile_widget)
        self.update_prev_next_enabled()

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

    def check_win(self):
        """End the game if the player has won"""
        if self.board.check_win(self.active_player):
            print(f"Player {self.active_player} wins !!!")

            # Freeze board
            self.active_player = None
            for card_widget in self.card_widgets.values():
                card_widget.do_translation = False
            return True
        return False

    def check_end_of_turn(self, pile_widget):
        """End the player turn if conditions are met."""
        if (
            isinstance(pile_widget.pile, WastePile)
            and pile_widget.pile.player == self.active_player
        ):
            self.set_player_turn(1 - self.active_player)

    def flip_card_up(self, card_widget):
        """Flips up the card and register the flip as a move"""
        card_widget.set_face_up()
        self.moves.record_flip(card_widget, card_widget.pile_widget)
        self.update_prev_next_enabled()

        #  Brain(self.board, self.active_player).checks()
        BrainForce(self.board, self.active_player).compute_states()

    def flip_waste_to_stock(self):
        """When the stock is empty, flip the waste back to the stock"""
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

        self.moves.record_waste_flip()
        self.update_prev_next_enabled()

    def toggle_crapette_mode(self):
        """Toggles the crapette mode."""
        player = self.active_player
        ids = self.app.root.ids
        crapette_button = ids[f"player{player}crapebutton"]

        self.crapette_mode = not self.crapette_mode

        self.background_crapette.opacity = 1 if self.crapette_mode else 0
        crapette_button.text = (
            "Cancel ! (Sorry...)" if self.crapette_mode else "Crapette !"
        )

        prev_next_buttons = [
            ids[f"player{player}nextbutton"],
            ids[f"player{player}prevbutton"],
        ]
        self.update_prev_next_enabled()
        for btn in prev_next_buttons:
            Animation(
                opacity=1 if self.crapette_mode else 0,
                duration=TRANSITION_DURATION,
                transition="out_cubic",
            ).start(btn)

    def _move_card(self, card_widget, pile_widget):
        # Remove from previous pile
        card_widget.pile_widget.pop_card()

        # Add to new pile
        pile_widget.add_card(card_widget)
        card_widget.pile_widget = pile_widget
        card_widget.set_center_animated(pile_widget.card_pos())
        card_widget.apply_random_rotation()
        card_widget.main_rotation = pile_widget.rotation

    def update_prev_next_enabled(self):
        player = self.active_player
        ids = self.app.root.ids

        next_button = ids[f"player{player}nextbutton"]
        next_button.disabled = not self.crapette_mode or not self.moves.has_next

        prev_button = ids[f"player{player}prevbutton"]
        prev_button.disabled = not self.crapette_mode or not self.moves.has_prev

    def crapette_mode_prev(self):
        """Rollback one step in crapette mode"""
        move = self.moves.prev()
        self.update_prev_next_enabled()

        if isinstance(move, Move):
            self.do_move(move.card, move.origin)
        elif isinstance(move, Flip):
            print("Flip")
        elif isinstance(move, FlipWaste):
            print("FlipWaste")

    def crapette_mode_next(self):
        """Rollback one step in crapette mode"""
        move = self.moves.next()
        self.update_prev_next_enabled()

        if isinstance(move, Move):
            self.do_move(move.card, move.destination)
        elif isinstance(move, Flip):
            print("Flip")
        elif isinstance(move, FlipWaste):
            print("FlipWaste")
