use crate::core::cards::*;
use crate::core::decks::*;
use crate::core::piles::*;
use crate::core::players::*;
use crate::core::suits::*;

const NB_PILES: usize = 8;

#[derive(Debug)]
pub struct Board {
    stock: [StockPile; NB_PLAYERS],
    waste: [WastePile; NB_PLAYERS],
    crape: [CrapePile; NB_PLAYERS],
    foundation_piles: [FoundationPile; NB_PILES],
    tableau_piles: [TableauPile; NB_PILES],
}

impl Board {
    pub fn new() -> Self {
        let board = Board {
            waste: [
                WastePile::new(Player::Player0),
                WastePile::new(Player::Player1),
            ],
            crape: [
                CrapePile::new(Player::Player0),
                CrapePile::new(Player::Player1),
            ],
            stock: [
                StockPile::new(Player::Player0),
                StockPile::new(Player::Player1),
            ],
            foundation_piles: [
                FoundationPile::new(1, Suit::Diamond),
                FoundationPile::new(2, Suit::Club),
                FoundationPile::new(3, Suit::Heart),
                FoundationPile::new(4, Suit::Spade),
                FoundationPile::new(5, Suit::Spade),
                FoundationPile::new(6, Suit::Heart),
                FoundationPile::new(7, Suit::Club),
                FoundationPile::new(8, Suit::Diamond),
            ],
            tableau_piles: [
                TableauPile::new(1),
                TableauPile::new(2),
                TableauPile::new(3),
                TableauPile::new(4),
                TableauPile::new(5),
                TableauPile::new(6),
                TableauPile::new(7),
                TableauPile::new(8),
            ],
        };
        board
    }

    pub fn new_game(&mut self) {
        for player in PLAYERS {
            let mut deck = new_deck(player);
            shuffle(&mut deck);

            let card = &mut deck[0];
            card.set_face_up();

            let player = player as usize;

            // Fill crape pile
            let crape = deck.split_off(deck.len() - 13);
            self.crape[player].cards.set(crape);
            let card: &mut Card = self.crape[player].cards.top_card_mut();
            card.set_face_up();
            //assert_eq!(card.face_up, true);

            // Fill tableau
            for tp in self.tableau_piles[(4 * player)..(4 * player + 4)].iter_mut() {
                tp.cards.clear();
                let mut card = deck.pop().unwrap();
                card.set_face_up();
                tp.cards.add(card);
            }

            // Fill stock
            self.stock[player].cards.set(deck);

            // Clear waste
            self.waste[player].cards.clear();
        }

        // Clear foundation
        for fp in self.foundation_piles.iter_mut() {
            fp.cards.clear();
        }
    }

    pub fn to_string(self) -> String {
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

            let mut line: String = "   "
                .repeat(13 - tableau_pile_left.cards.nb_cards())
                .to_string();
            line += &tableau_pile_left.str_display_left();
            line += "| ";
            line += &foundation_pile_left.str_display();
            line += " ";
            line += &foundation_pile_right.str_display();
            line += " | ";
            line += &tableau_pile_right.str_display_right();
            str_lines[row + 1] = line;
        }

        str_lines.join("\n")
    }

    pub fn check_win(&self, player: Player) -> bool {
        self.stock[player as usize].cards.is_empty()
            && self.waste[player as usize].cards.is_empty()
            && self.crape[player as usize].cards.is_empty()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_new_game() {
        let mut board = Board::new();
        board.new_game();
        for p in 0..=1 {
            assert_eq!(board.stock[p].cards.nb_cards(), 52 - 13 - 4);
            assert_eq!(board.waste[p].cards.nb_cards(), 0);
            assert_eq!(board.crape[p].cards.nb_cards(), 13);
            assert_eq!(board.crape[p].cards.top_card().face_up, true);
        }
        for tp in board.tableau_piles.iter() {
            assert_eq!(tp.cards.nb_cards(), 1);
        }
        for tp in board.foundation_piles.iter() {
            assert_eq!(tp.cards.nb_cards(), 0);
        }
    }

    #[test]
    fn test_new_game_clear() {
        let mut board = Board::new();
        board.new_game();
        board.new_game();
        for p in 0..=1 {
            assert_eq!(board.crape[p].cards.nb_cards(), 13);
            assert_eq!(board.stock[p].cards.nb_cards(), 52 - 13 - 4);
            assert_eq!(board.waste[p].cards.nb_cards(), 0);
        }
        for tp in board.tableau_piles.iter() {
            assert_eq!(tp.cards.nb_cards(), 1);
        }
        for tp in board.foundation_piles.iter() {
            assert_eq!(tp.cards.nb_cards(), 0);
        }
    }

    #[test]
    fn test_check_win() {
        let mut board = Board::new();
        board.new_game();
        assert_eq!(board.check_win(Player::Player0), false);
        assert_eq!(board.check_win(Player::Player1), false);
    }
}
