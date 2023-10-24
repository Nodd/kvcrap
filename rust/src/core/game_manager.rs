use rand_pcg::Pcg64;

use super::board::Board;
use super::custom_test_games::call_custom;
use super::decks::{generate_seed, new_rng};
use super::moves::Move;
use super::piles::PileType;
use super::players::{Player, PlayerType, NB_PLAYER};

pub struct GameConfig {
    pub player_types: [PlayerType; NB_PLAYER],
    pub seed: String,
    pub rng: Pcg64,
    pub custom_game: Option<String>,
    pub active_player: Option<Player>,
    step: usize,
    last_move: Option<Move>,
    crapette_mode: bool,
    start_time: Option<String>,
    log_path: String,
}

impl GameConfig {
    fn new(seed: String) -> Self {
        let rng = new_rng(&seed);
        GameConfig {
            player_types: [PlayerType::Player, PlayerType::Player],
            seed,
            rng,
            custom_game: None,
            active_player: None,
            step: 0,
            last_move: None,
            crapette_mode: false,
            start_time: None,
            log_path: "".to_string(), // Path(__file__).parent / "log"
        }
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

pub struct GameManager {
    pub config: GameConfig,
    pub board: Board,
}

impl GameManager {
    pub fn new(seed: Option<&str>, custom: Option<&str>) -> Self {
        let seed = match seed {
            Some(seed) => seed.to_string(),
            None => generate_seed(),
        };

        let mut game_manager = Self {
            config: GameConfig::new(seed),
            board: Board::new(),
        };

        match custom {
            None => {
                game_manager.board.new_game(&mut game_manager.config.rng);
                game_manager.set_active_player(Some(game_manager.board.compute_first_player()));
            }
            Some(custom) => {
                call_custom(custom, &mut game_manager.board);
                game_manager.set_active_player(Some(Player::Player0));
            }
        };
        game_manager
    }

    /// Change the active player.
    // and updates the GUI accordingly.
    pub fn set_active_player(&mut self, player: Option<Player>) {
        self.set_crapette_last_move(None);
        self.config.active_player = player;
        //TODO: callback
    }

    /// End the player turn if conditions are met when moving a card on a pile.
    pub fn check_and_apply_end_of_turn(&mut self, pile: &PileType) -> bool {
        assert!(!self.config.crapette_mode);

        if let PileType::Waste { player } = pile {
            if let Some(active_player) = self.config.active_player {
                if player == &active_player {
                    self.set_active_player(Some(active_player.other()));
                    return true;
                }
            }
        }
        false
    }

    /// End the game if the current player has won.
    pub fn check_and_apply_win(&mut self) -> bool {
        match self.config.active_player {
            Some(active_player) => {
                if self.board.check_win(active_player) {
                    println!("Player {:?} wins !!!", active_player);

                    // Callback GUI
                    // label.text = "Player {active_player} wins !!!"

                    // Freeze board
                    self.set_active_player(None);
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

    pub fn set_crapette_last_move(&mut self, card_move: Option<Move>) {
        if self.config.crapette_mode {
            return;
        }
        self.config.last_move = card_move;

        // Update GUI
        //self.board_widget.update_crapette_button_status();
    }

    pub fn move_card(
        &mut self,
        origin_type: &PileType,
        destination_type: &PileType,
    ) -> Result<Move, &'static str> {
        let card_move = self.board.move_card_checked(
            origin_type,
            destination_type,
            self.config
                .active_player
                .expect("Active player should be set"),
        );
        match card_move {
            Ok(card_move) => {
                if !self.config.crapette_mode {
                    self.set_crapette_last_move(match &origin_type {
                        PileType::Crape { .. } | PileType::Stock { .. } => Some(card_move),
                        _ => None,
                    });

                    let _end = self.check_and_apply_end_of_turn(&destination_type);
                    // TODO: AI moves
                }
            }
            Err(e) => println!("Error: {}", e),
        }
        card_move
    }

    pub fn flip_card_up(&mut self, pile_type: &PileType) {
        if self.config.crapette_mode {
            // TODO
        }

        self.board.flip_card_up(
            pile_type,
            &self.config.active_player.expect("No active player"),
        );

        // TODO Crapette checks
    }

    pub fn flip_waste_to_stock(&mut self) {
        self.board
            .flip_waste_to_stock(&self.config.active_player.expect("No active player"))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_move_card() {
        let mut game_manager = GameManager::new(None, Some("foundation_to_fill"));
        let tableau0 = PileType::Tableau { tableau_id: 0 };
        let tableau1 = PileType::Tableau { tableau_id: 1 };
        let result = game_manager.move_card(&tableau0, &tableau1);
        result.unwrap();
        assert_eq!(game_manager.board.tableau_piles[0].nb_cards(), 0);
        assert_eq!(game_manager.board.tableau_piles[1].nb_cards(), 1);
    }

    #[test]
    fn test_move_card_invalid() {
        let mut game_manager = GameManager::new(None, Some("foundation_to_fill"));
        let tableau0 = PileType::Tableau { tableau_id: 2 };
        let tableau1 = PileType::Tableau { tableau_id: 1 };
        let card_move = game_manager.move_card(&tableau0, &tableau1);
        assert_eq!(card_move.is_err(), true);
    }

    #[test]
    fn test_flip_card() {
        let mut game_manager = GameManager::new(None, Some("foundation_to_fill"));
        let crape = PileType::Crape {
            player: Player::Player0,
        };
        game_manager.flip_card_up(&crape);
    }
}
