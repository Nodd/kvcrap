"""Manage the widgets interaction on the game board."""

import typing

from kivy.logger import Logger

from .brain.brainforce import BrainForce
from .core.board import Board
from .core.moves import Flip, FlipWaste, Move, Moves
from .core.piles import WastePile

if typing.TYPE_CHECKING:
    from .widgets.board_widget import BoardWidget


class GameManager:
    def __init__(self, app):
        self.app = app
        self.ids = self.app.root.ids

        self.active_player: int = None
        self.crapette_mode: bool = False
        self.board_widget: BoardWidget = self.ids["game_board"]

    def setup(self, custom_new_game=None):
        self.board = Board()
        if custom_new_game is not None:
            custom_new_game(self.board)
        else:
            self.board.new_game()
        self.board_widget.setup(self)

        if custom_new_game is not None:
            self.set_active_player(0)
        else:
            self.set_active_player(self.board_widget.board.compute_first_player())

    def set_active_player(self, player: int):
        """Change the active player and updates the GUI accordingly."""
        assert not self.crapette_mode

        self.moves = Moves()
        self.active_player = player

        self.board_widget.set_active_player(player)

        # Brain(self.board, self.active_player).checks()
        BrainForce(self.board, self.active_player).compute_states()

    def check_end_of_turn(self, pile_widget):
        """End the player turn if conditions are met."""
        assert not self.crapette_mode

        if (
            isinstance(pile_widget.pile, WastePile)
            and pile_widget.pile.player == self.active_player
        ):
            self.set_active_player(1 - self.active_player)

    def check_win(self):
        """End the game if the player has won."""
        if self.board.check_win(self.active_player):
            print(f"Player {self.active_player} wins !!!")

            # Freeze board
            self.active_player = None
            for card_widget in self.card_widgets.values():
                card_widget.do_translation = False
            return True
        return False

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
            Logger.debug("Dropped on an incompatible pile")
            return False

        self.board_widget.move_card(card_widget, pile_widget)

        self.moves.record_move(card_widget, old_pile_widget, pile_widget)
        self.update_prev_next_enabled()

        self.check_win()
        self.check_end_of_turn(pile_widget)

        # Brain(self.board, self.active_player).checks()
        BrainForce(self.board, self.active_player).compute_states()

        return True

    def flip_card_up(self, card_widget):
        """Flips up the card and register the flip as a move."""
        self.board_widget.flip_card_up(card_widget)

        self.moves.record_flip(card_widget, card_widget.pile_widget)
        self.update_prev_next_enabled()

        # Brain(self.board, self.active_player).checks()
        BrainForce(self.board, self.active_player).compute_states()

    def flip_waste_to_stock(self):
        """When the stock is empty, flip the waste back to the stock."""
        self.board_widget.flip_waste_to_stock(self.active_player)

        self.moves.record_waste_flip()
        self.update_prev_next_enabled()

    def toggle_crapette_mode(self):
        self.crapette_mode = not self.crapette_mode

        self.board_widget.set_crapette_mode(self.crapette_mode, self.active_player)
        self.update_prev_next_enabled()

        # If crapette mode cancelled, reset
        if not self.crapette_mode:
            while self.moves.has_next:
                self.crapette_mode_next()

    def update_prev_next_enabled(self):
        """Update enabled state of history buttons."""
        next_button = self.ids[f"player{self.active_player}nextbutton"]
        next_button.disabled = not self.crapette_mode or not self.moves.has_next

        prev_button = self.ids[f"player{self.active_player}prevbutton"]
        prev_button.disabled = not self.crapette_mode or not self.moves.has_prev

    def crapette_mode_prev(self):
        """Rollback one step in crapette mode."""
        move = self.moves.prev_move()
        self.update_prev_next_enabled()

        if isinstance(move, Move):
            self.board_widget.move_card(move.card, move.origin)
        elif isinstance(move, Flip):
            move.card.set_face_down()
        elif isinstance(move, FlipWaste):
            print("FlipWaste")

    def crapette_mode_next(self):
        """'Rollforward' one step in crapette mode."""
        move = self.moves.next_move()
        self.update_prev_next_enabled()

        if isinstance(move, Move):
            self.board_widget.move_card(move.card, move.destination)
        elif isinstance(move, Flip):
            move.card.set_face_up()
        elif isinstance(move, FlipWaste):
            self.board_widget.flip_waste_to_stock(self.active_player)
