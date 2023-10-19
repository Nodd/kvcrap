use std::cmp::max;

use super::cards::*;
use super::decks::*;
use super::piles::*;
use super::players::*;
use super::suits::*;

const NB_PILES: usize = 8;

#[derive(Debug)]
pub struct Board {
    stock: [Pile; NB_PLAYERS],
    waste: [Pile; NB_PLAYERS],
    crape: [Pile; NB_PLAYERS],
    foundation_piles: [Pile; NB_PILES],
    tableau_piles: [Pile; NB_PILES],
}

impl Board {
    pub fn new() -> Self {
        let board = Board {
            waste: [
                Pile::new_waste(Player::Player0),
                Pile::new_waste(Player::Player1),
            ],
            crape: [
                Pile::new_crape(Player::Player0),
                Pile::new_crape(Player::Player1),
            ],
            stock: [
                Pile::new_stock(Player::Player0),
                Pile::new_stock(Player::Player1),
            ],
            foundation_piles: [
                Pile::new_foundation(0, Suit::Diamond),
                Pile::new_foundation(1, Suit::Club),
                Pile::new_foundation(2, Suit::Heart),
                Pile::new_foundation(3, Suit::Spade),
                Pile::new_foundation(4, Suit::Spade),
                Pile::new_foundation(5, Suit::Heart),
                Pile::new_foundation(6, Suit::Club),
                Pile::new_foundation(7, Suit::Diamond),
            ],
            tableau_piles: [
                Pile::new_tableau(0),
                Pile::new_tableau(1),
                Pile::new_tableau(2),
                Pile::new_tableau(3),
                Pile::new_tableau(4),
                Pile::new_tableau(5),
                Pile::new_tableau(6),
                Pile::new_tableau(7),
            ],
        };
        board
    }

    pub fn new_game(&mut self, seed: &str) {
        let mut rng = new_rng(seed.to_string());

        for player in PLAYERS {
            let mut deck = new_deck(player);
            shuffle(&mut deck, &mut rng);

            let card = &mut deck[0];
            card.set_face_up();

            let player = player as usize;

            // Fill crape pile
            let crape = deck.split_off(deck.len() - NB_CRAPE_START);
            self.crape[player].set(crape);
            let card: &mut Card = self.crape[player].top_card_mut();
            card.set_face_up();

            // Fill tableau
            for tp in self.tableau_piles[(4 * player)..(4 * player + 4)].iter_mut() {
                tp.clear();
                let mut card = deck.pop().unwrap();
                card.set_face_up();
                tp.add(card);
            }

            // Fill stock
            self.stock[player].set(deck);

            // Clear waste
            self.waste[player].clear();
        }

        // Clear foundation
        for fp in self.foundation_piles.iter_mut() {
            fp.clear();
        }
    }

    pub fn to_string(&self) -> String {
        let mut str_lines = [
            "".to_string(),
            "".to_string(),
            "".to_string(),
            "".to_string(),
            "".to_string(),
            "".to_string(),
        ];

        let player_space_left = " ".repeat(13 * 3).to_string();
        str_lines[0] = player_space_left.clone()
            + &self.crape[1].str_display()
            + "  "
            + &self.waste[1].str_display()
            + " "
            + &self.stock[1].str_display();

        str_lines[5] = player_space_left
            + &self.stock[0].str_display()
            + " "
            + &self.waste[0].str_display()
            + "  "
            + &self.crape[0].str_display();

        for row in 0..4 {
            let index_left = row + 4; // 4, 5, 6, 7
            let index_right = 3 - row; // 3, 2, 1, 0

            let tableau_pile_left = &self.tableau_piles[index_left];
            let tableau_pile_right = &self.tableau_piles[index_right];
            let foundation_pile_left = &self.foundation_piles[index_left];
            let foundation_pile_right = &self.foundation_piles[index_right];

            let mut line: String = "   ".repeat(13 - tableau_pile_left.nb_cards()).to_string();
            line += &tableau_pile_left.str_display();
            line += "| ";
            line += &foundation_pile_left.str_display();
            line += " ";
            line += &foundation_pile_right.str_display();
            line += " | ";
            line += &tableau_pile_right.str_display();
            str_lines[row + 1] = line;
        }

        str_lines.join("\n")
    }

    pub fn compute_first_player(&self) -> Player {
        if self.crape[0].top_card().rank() > self.crape[1].top_card().rank() {
            Player::Player0
        } else if self.crape[0].top_card().rank() < self.crape[1].top_card().rank() {
            Player::Player1
        } else {
            let mut max_p0 = self.tableau_piles[0].top_card().rank();
            let mut max_p1 = self.tableau_piles[4].top_card().rank();
            for row in 1..=3 {
                max_p0 = max(max_p0, self.tableau_piles[row].top_card().rank());
                max_p1 = max(max_p1, self.tableau_piles[4 + row].top_card().rank());
            }
            if max_p0 > max_p1 {
                Player::Player0
            } else {
                Player::Player1
            }
        }
    }

    pub fn check_win(&self, player: Player) -> bool {
        self.stock[player as usize].is_empty()
            && self.waste[player as usize].is_empty()
            && self.crape[player as usize].is_empty()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_new_game() {
        let mut board = Board::new();
        board.new_game("test");
        for p in 0..=1 {
            assert_eq!(board.stock[p].nb_cards(), 52 - 13 - 4);
            assert_eq!(board.waste[p].nb_cards(), 0);
            assert_eq!(board.crape[p].nb_cards(), 13);
            assert_eq!(board.crape[p].top_card().face_up, true);
        }
        for tp in board.tableau_piles.iter() {
            assert_eq!(tp.nb_cards(), 1);
        }
        for tp in board.foundation_piles.iter() {
            assert_eq!(tp.nb_cards(), 0);
        }
    }

    #[test]
    fn test_new_game_clear() {
        let mut board = Board::new();
        board.new_game("test1");
        board.new_game("test2");
        for p in 0..=1 {
            assert_eq!(board.crape[p].nb_cards(), 13);
            assert_eq!(board.stock[p].nb_cards(), 52 - 13 - 4);
            assert_eq!(board.waste[p].nb_cards(), 0);
        }
        for tp in board.tableau_piles.iter() {
            assert_eq!(tp.nb_cards(), 1);
        }
        for tp in board.foundation_piles.iter() {
            assert_eq!(tp.nb_cards(), 0);
        }
    }

    #[test]
    fn test_check_win() {
        let mut board = Board::new();
        assert_eq!(board.check_win(Player::Player0), true);
        assert_eq!(board.check_win(Player::Player1), true);
        board.new_game("test");
        assert_eq!(board.check_win(Player::Player0), false);
        assert_eq!(board.check_win(Player::Player1), false);
    }
}
