"""Manage the widgets interaction on the game board."""

import dataclasses
import multiprocessing
import os
import random
import typing
from datetime import datetime
from pathlib import Path

from kivy.clock import Clock
from kivy.logger import Logger

from . import custom_test_games
from .brain.brainforce import BrainForce
from .core.board import Board
from .core.moves import Flip, FlipWaste, Move
from .core.piles import WastePile
from .widgets.card_widget import (
    DEFAULT_FLIP_DURATION,
    DEFAULT_MOVE_DURATION,
    CardWidget,
)
from .widgets.pile_widgets import FoundationPileWidget, PileWidget, PlayerPileWidget

if typing.TYPE_CHECKING:
    from .widgets.board_widget import BoardWidget


@dataclasses.dataclass
class GameConfig:
    player_types: tuple[str] = ("player", "player")
    seed: int | None = None
    custom_game: str | None = None
    active_player: int = 0
    step: int = 0
    last_move: None | Move | FlipWaste = None
    crapette_mode: bool = False
    start_time: datetime | None = None
    log_path: Path = Path(__file__).parent / "log"
    board: Board = dataclasses.field(default_factory=Board)

    def generate_seed(self):
        self.seed = int.from_bytes(os.urandom(8), "big")

    @property
    def current_seed(self) -> int | str | None:
        return self.custom_game or self.seed

    def register(self):
        if self.seed is None:
            raise RuntimeError("No seed configured")
        self.start_time = datetime.now()
        log_parent_dir = Path(__file__).parent / "log"
        log_parent_dir.mkdir(parents=True, exist_ok=True)
        self.log_path = log_parent_dir / f"{self.seed}_{self.start_time}.txt"


class GameManager:
    def __init__(self, app):
        self.app = app
        self.ids = self.app.root.ids
        self.board_widget: BoardWidget = self.ids["game_board"]

        self._brain_process = None

    def setup(self, player0: str, player1: str, seed=None, custom_game=None):
        self.game_config = GameConfig(
            player_types=(player0, player1), seed=seed, custom_game=custom_game
        )
        if custom_game:
            custom_new_game = getattr(custom_test_games, custom_game)
            Logger.info('Custom game: "%s"', custom_game)
        else:
            if seed is None:
                self.game_config.generate_seed()
            Logger.info("Game seed: %d", self.game_config.seed)
            random.seed(self.game_config.seed)
        self.game_config.board = Board()
        self.game_config.register()

        self.game_config.board = Board()
        if custom_game:
            custom_new_game(self.game_config.board)
        else:
            self.game_config.board.new_game()
        self.board_widget.setup(self)

        self.set_active_player(
            self.board_widget.board.compute_first_player() if custom_game is None else 0
        )

        self.check_moves()

    def set_active_player(self, player: int):
        """Change the active player and updates the GUI accordingly."""
        assert not self.game_config.crapette_mode

        self.game_config.last_move = None
        self.game_config.active_player = player

        self.board_widget.set_active_player(player)

    def check_end_of_turn(self, pile_widget):
        """End the player turn if conditions are met."""
        assert not self.game_config.crapette_mode

        if (
            isinstance(pile_widget.pile, WastePile)
            and pile_widget.pile.player == self.game_config.active_player
        ):
            self.set_active_player(1 - self.game_config.active_player)

    def check_win(self):
        """End the game if the player has won."""
        if self.game_config.board.check_win(self.game_config.active_player):
            print(f"Player {self.game_config.active_player} wins !!!")

            # Freeze board
            self.game_config.active_player = None
            for card_widget in self.board_widget.card_widgets.values():
                card_widget.do_translation = False
            return True
        return False

    def move_card(
        self,
        card_widget: CardWidget,
        pile_widget: PileWidget,
        duration=DEFAULT_MOVE_DURATION,
        check_moves=True,
    ):
        """Move a card to another pile and register the move.

        It only checks the destination, not if the card was movable by the player.
        """
        old_pile_widget = card_widget.pile_widget

        can_add = pile_widget.pile.can_add_card(
            card_widget.card, old_pile_widget.pile, self.game_config.active_player
        )
        assert can_add in (True, False), can_add
        if not can_add:
            Logger.debug("Dropped on an incompatible pile")
            card_widget.animate_move_to_pile()
            return

        self.board_widget.move_card(card_widget, pile_widget, duration=duration)

        self.log_game_step(
            f"move {card_widget.card.str_rank_suit} from {old_pile_widget.pile.name} to {pile_widget.pile.name}"
        )

        if self.check_win():
            return

        if isinstance(old_pile_widget, PlayerPileWidget) or isinstance(
            pile_widget, FoundationPileWidget
        ):
            self.game_config.last_move = Move(card_widget, old_pile_widget, pile_widget)
        else:
            self.game_config.last_move = None

        self.check_end_of_turn(pile_widget)
        if check_moves:
            self.check_moves()

    def flip_card_up(
        self, card_widget: CardWidget, duration=DEFAULT_FLIP_DURATION, check_moves=True
    ):
        """Flips up the card and register the flip as a move."""
        self.board_widget.flip_card_up(card_widget, duration)

        self.log_game_step(f"flip card up in {card_widget.pile_widget.pile.name}")

        self.game_config.last_move = Flip(card_widget, card_widget.pile_widget)

        if check_moves:
            self.check_moves()

    def flip_waste_to_stock(self):
        """When the stock is empty, flip the waste back to the stock."""
        self.board_widget.flip_waste_to_stock(self.game_config.active_player)

        self.log_game_step("flip waste to stock")

        self.game_config.last_move = FlipWaste()

    def toggle_crapette_mode(self):
        self.game_config.crapette_mode = not self.game_config.crapette_mode

        self.board_widget.set_crapette_mode(
            self.game_config.crapette_mode, self.game_config.active_player
        )

        if self.game_config.crapette_mode:
            for card_widget in self.board_widget.card_widgets.values():
                card_widget.abort_moving()
            if isinstance(self.game_config.last_move, Move):
                self.board_widget.move_card(
                    self.game_config.last_move.card, self.game_config.last_move.origin
                )
        else:
            # If crapette mode cancelled, reset
            # TODO: Cancel all actions done while in crapette mode
            if isinstance(self.game_config.last_move, Move):
                self.board_widget.move_card(
                    self.game_config.last_move.card,
                    self.game_config.last_move.destination,
                )

    def check_moves(self):
        if self.game_config.active_player is None:
            return  # End of game
        if self.game_config.player_types[self.game_config.active_player] == "ai":
            brain = BrainForce(self.game_config)
            if self.app.app_config.ai.mono:
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
                0.2 if self.app.app_config.fast_animations else random.triangular(1, 3),
            )

    def ai_play(self, moves: list):
        move = moves.pop(0)
        print("ai_play", self.game_config.step + 1, move)
        duration = (
            0.1 if self.app.app_config.fast_animations else random.triangular(0.3, 0.7)
        )
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
            duration = 0.1 if self.app.app_config.fast_animations else 1
        if moves:
            duration += (
                0.1
                if self.app.app_config.fast_animations
                else random.triangular(0.5, 0.9)
            )
            Clock.schedule_once(lambda _dt: self.ai_play(moves), duration)
        else:
            Clock.schedule_once(lambda _dt: self.check_moves(), 0.2)

    def log_game_step(self, action):
        self.game_config.step += 1

        with self.game_config.log_path.open("a") as f:
            f.write(
                f"\n\n*** {self.game_config.step} ***\nPlayer {self.game_config.active_player}: {action}\n"
            )
            f.write(self.game_config.board.to_text())
