use crate::core::piles::PileType;

use super::board::Board;
use super::moves::Move;
use super::piles::Pile;
use super::players::{Player, PlayerType, NB_PLAYER};

pub struct GameConfig {
    player_types: [PlayerType; NB_PLAYER],
    seed: Option<u64>,
    custom_game: Option<String>,
    active_player: Option<Player>,
    step: usize,
    last_move: Option<Move>,
    crapette_mode: bool,
    start_time: Option<String>,
    log_path: String,
    board: Board,
}

impl GameConfig {
    fn new() -> Self {
        GameConfig {
            player_types: [PlayerType::Player, PlayerType::Player],
            seed: None,
            custom_game: None,
            active_player: None,
            step: 0,
            last_move: None,
            crapette_mode: false,
            start_time: None,
            log_path: "".to_string(), // Path(__file__).parent / "log"
            board: Board::new(),
        }
    }

    fn generate_seed(&mut self) {
        self.seed = Some(0); // TODO
    }

    fn is_player_ai(&self) -> bool {
        match self.active_player {
            None => false,
            Some(player) => self.player_types[player as usize] == PlayerType::AI,
        }
    }

    fn is_opponent_ai(&self) -> bool {
        match self.active_player {
            None => false,
            Some(player) => self.player_types[player.other() as usize] == PlayerType::AI,
        }
    }
}

struct GameManager {
    game_config: GameConfig,
}

impl GameManager {
    pub fn new() -> Self {
        Self {
            game_config: GameConfig::new(),
        }
    }

    /// Change the active player.
    // and updates the GUI accordingly.
    pub fn set_active_player(&mut self, player: Option<Player>) {
        self.set_crapette_last_move(None);
        self.game_config.active_player = player;
        //TODO: callback
    }

    /// End the player turn if conditions are met.
    pub fn check_and_apply_end_of_turn(&mut self, pile: &Pile) -> bool {
        assert!(!self.game_config.crapette_mode);

        match pile.kind {
            PileType::Waste { player } => match self.game_config.active_player {
                Some(active_player) => {
                    if player == active_player {
                        self.set_active_player(Some(active_player.other()));
                        true
                    } else {
                        false
                    }
                }
                None => false,
            },
            _ => false,
        }
    }

    /// End the game if the current player has won.
    pub fn check_and_apply_win(&mut self) -> bool {
        match self.game_config.active_player {
            Some(active_player) => {
                if self.game_config.board.check_win(active_player) {
                    println!("Player {:?} wins !!!", active_player);

                    // Callback GUI
                    // label.text = "Player {active_player} wins !!!"

                    // Freeze board
                    self.game_config.active_player = None;
                    //for card_widget in self.board_widget.card_widgets.values():
                    //    card_widget.do_translation = False
                    //self.board_widget.update_crapette_button_status()
                    true
                } else {
                    false
                }
            }
            None => false,
        }
    }

    pub fn set_crapette_last_move(&mut self, r#move: Option<Move>) {
        if self.game_config.crapette_mode {
            return;
        }
        self.game_config.last_move = r#move;

        // Update GUI
        //self.board_widget.update_crapette_button_status();
    }
}
