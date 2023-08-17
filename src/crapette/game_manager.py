"""Manage the widgets interaction on the game board."""

import multiprocessing
import random
import typing

from kivy.clock import Clock
from kivy.logger import Logger

from .brain.brainforce import BrainForce
from .core.board import Board
from .core.moves import Flip, FlipWaste, Move
from .core.piles import WastePile
from .widgets.card_widget import DEFAULT_FLIP_DURATION, DEFAULT_MOVE_DURATION
from .widgets.pile_widgets import FoundationPileWidget, PlayerPileWidget

if typing.TYPE_CHECKING:
    from .widgets.board_widget import BoardWidget


class GameManager:
    def __init__(self, app):
        self.app = app
        self.ids = self.app.root.ids

        self.active_player: int = None
        self.crapette_mode: bool = False
        self.board_widget: BoardWidget = self.ids["game_board"]

        self._brain_process = None

    def setup(self, player0: str, player1: str, custom_new_game=None):
        assert player0 in {"player", "ai"}
        assert player1 in {"player", "remote", "ai"}

        self.player_types = (player0, player1)

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

        self.check_moves()

    def set_active_player(self, player: int):
        """Change the active player and updates the GUI accordingly."""
        assert not self.crapette_mode

        self.last_move: None | Move | FlipWaste = None
        self.active_player = player

        self.board_widget.set_active_player(player)

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
            for card_widget in self.board_widget.card_widgets.values():
                card_widget.do_translation = False
            return True
        return False

    def move_card(
        self, card_widget, pile_widget, duration=DEFAULT_MOVE_DURATION, check_moves=True
    ):
        """Move a card to another pile and register the move.

        It only checks the destination, not if the card was movable by the player.
        """
        old_pile_widget = card_widget.pile_widget

        can_add = pile_widget.pile.can_add_card(
            card_widget.card, old_pile_widget.pile, self.active_player
        )
        assert can_add in (True, False), can_add
        if not can_add:
            Logger.debug("Dropped on an incompatible pile")
            card_widget.animate_move_to_pile()
            return

        self.board_widget.move_card(card_widget, pile_widget, duration=duration)

        if self.check_win():
            return

        if isinstance(old_pile_widget, PlayerPileWidget) or isinstance(
            pile_widget, FoundationPileWidget
        ):
            self.last_move = Move(card_widget, old_pile_widget, pile_widget)
        else:
            self.last_move = None

        self.check_end_of_turn(pile_widget)
        if check_moves:
            self.check_moves()

    def flip_card_up(
        self, card_widget, duration=DEFAULT_FLIP_DURATION, check_moves=True
    ):
        """Flips up the card and register the flip as a move."""
        self.board_widget.flip_card_up(card_widget, duration)

        self.last_move = Flip(card_widget, card_widget.pile_widget)

        if check_moves:
            self.check_moves()

    def flip_waste_to_stock(self):
        """When the stock is empty, flip the waste back to the stock."""
        self.board_widget.flip_waste_to_stock(self.active_player)

        self.last_move = FlipWaste()

    def toggle_crapette_mode(self):
        self.crapette_mode = not self.crapette_mode

        self.board_widget.set_crapette_mode(self.crapette_mode, self.active_player)

        if self.crapette_mode:
            for card_widget in self.board_widget.card_widgets.values():
                card_widget.abort_moving()
            if isinstance(self.last_move, Move):
                self.board_widget.move_card(self.last_move.card, self.last_move.origin)
        else:
            # If crapette mode cancelled, reset
            # TODO: Cancel all actions done while in crapette mode
            if isinstance(self.last_move, Move):
                self.board_widget.move_card(
                    self.last_move.card, self.last_move.destination
                )

    def check_moves(self):
        if self.active_player is None:
            return  # End of game
        if self.player_types[self.active_player] == "ai":
            brain = BrainForce(self.board, self.active_player)
            if self.app.mono:
                moves = brain.compute_states()
            else:
                if self._brain_process is not None:
                    if self._brain_process.is_alive():
                        self._brain_process.kill()
                        self._brain_process.join()
                    self._brain_process.close()

                self._brain_process = multiprocessing.Process(
                    target=brain.compute_states, daemon=True
                )
                self._brain_process.start()

            Clock.schedule_once(
                lambda _dt: self.ai_play(moves),
                0.2 if self.app.fast else random.triangular(1, 3),
            )

    def ai_play(self, moves: list):
        move = moves.pop(0)
        print("ai_play", move)
        duration = 0.1 if self.app.fast else random.triangular(0.3, 0.7)
        if isinstance(move, Move):
            self.move_card(
                self.board_widget.card_widgets[move.card],
                self.board_widget.widget_from_pile(move.destination),
                duration=duration,
                check_moves=False,
            )
        elif isinstance(move, Flip):
            self.flip_card_up(
                self.board_widget.card_widgets[move.card],
                duration=duration,
                check_moves=False,
            )
        elif isinstance(move, FlipWaste):
            self.flip_waste_to_stock()
            duration = 0.1 if self.app.fast else 1
        if moves:
            Clock.schedule_once(
                lambda _dt: self.ai_play(moves),
                duration + 0.1 if self.app.fast else random.triangular(0.5, 0.9),
            )
        else:
            Clock.schedule_once(lambda _dt: self.check_moves(), 0.2)
