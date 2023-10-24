use rand_pcg::Pcg64;

use super::cards::Card;
use super::decks::{new_deck, shuffle};
use super::moves::Move;
use super::piles::{Pile, PileType, NB_CRAPE_START};
use super::players::{Player, NB_PLAYERS, PLAYERS};
use super::ranks::NB_RANKS;
use super::suits::Suit;

const NB_PILES: usize = 8;
pub const NB_ROWS: usize = 4;
const PLAYER_SPACE: usize = NB_RANKS * 3;

#[derive(Debug)]
pub struct Board {
    pub stock: [Pile; NB_PLAYERS],
    pub waste: [Pile; NB_PLAYERS],
    pub crape: [Pile; NB_PLAYERS],
    pub foundation_piles: [Pile; NB_PILES],
    pub tableau_piles: [Pile; NB_PILES],
}

impl Board {
    /// Create an empty board.
    pub fn new() -> Self {
        Board {
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
        }
    }

    /// Create a new game with a standard card deal.
    pub fn new_game(&mut self, mut rng: &mut Pcg64) {
        for player in PLAYERS {
            let mut deck = self.prepare_deck(player, &mut rng);
            let player = player as usize;

            // Fill game components
            self.fill_crape(player, &mut deck);
            self.fill_tableau(player, &mut deck);
            self.fill_stock(player, deck);

            // Clear waste
            self.waste[player].clear();
        }

        // Clear foundation
        self.clear_foundation();
    }

    fn prepare_deck(&self, player: Player, rng: &mut Pcg64) -> Vec<Card> {
        let mut deck = new_deck(player);
        shuffle(&mut deck, rng);
        deck
    }

    fn fill_crape(&mut self, player: usize, deck: &mut Vec<Card>) {
        let crape = deck.split_off(deck.len() - NB_CRAPE_START);
        self.crape[player].set(crape);
        let card: &mut Card = self.crape[player].top_card_mut().unwrap();
        card.set_face_up();
    }

    fn fill_tableau(&mut self, player: usize, deck: &mut Vec<Card>) {
        for tp in self.tableau_piles[(NB_ROWS * player)..(NB_ROWS * (player + 1))].iter_mut() {
            tp.clear();
            let mut card = deck.pop().unwrap();
            card.set_face_up();
            tp.add(card);
        }
    }

    fn fill_stock(&mut self, player: usize, deck: Vec<Card>) {
        self.stock[player].set(deck);
    }

    fn clear_foundation(&mut self) {
        for fp in self.foundation_piles.iter_mut() {
            fp.clear();
        }
    }

    fn pile_from_type(&self, pile_type: &PileType) -> &Pile {
        match pile_type {
            PileType::Foundation { foundation_id, .. } => {
                &self.foundation_piles[*foundation_id as usize]
            }
            PileType::Tableau { tableau_id } => &self.tableau_piles[*tableau_id as usize],
            PileType::Stock { player } => &self.stock[*player as usize],
            PileType::Waste { player } => &self.waste[*player as usize],
            PileType::Crape { player } => &self.crape[*player as usize],
        }
    }

    fn pile_from_type_mut(&mut self, pile_type: &PileType) -> &mut Pile {
        match pile_type {
            PileType::Foundation { foundation_id, .. } => {
                &mut self.foundation_piles[*foundation_id as usize]
            }
            PileType::Tableau { tableau_id } => &mut self.tableau_piles[*tableau_id as usize],
            PileType::Stock { player } => &mut self.stock[*player as usize],
            PileType::Waste { player } => &mut self.waste[*player as usize],
            PileType::Crape { player } => &mut self.crape[*player as usize],
        }
    }

    /// Display the board as a multiline String.
    pub fn to_string(&self) -> String {
        let player_space = " ".repeat(PLAYER_SPACE);

        let mut str_lines = vec![format!(
            "{}{}  {} {}",
            player_space,
            self.crape[1].str_display(),
            self.waste[1].str_display(),
            self.stock[1].str_display()
        )];

        str_lines.extend((0..NB_ROWS).map(|row| {
            let index_left = row + NB_ROWS;
            let index_right = NB_ROWS - 1 - row;

            let tableau_pile_left = &self.tableau_piles[index_left];
            let tableau_pile_right = &self.tableau_piles[index_right];
            let foundation_pile_left = &self.foundation_piles[index_left];
            let foundation_pile_right = &self.foundation_piles[index_right];

            format!(
                "{}{}| {} {} | {}",
                "   ".repeat(NB_RANKS - tableau_pile_left.nb_cards()),
                tableau_pile_left.str_display(),
                foundation_pile_left.str_display(),
                foundation_pile_right.str_display(),
                tableau_pile_right.str_display()
            )
        }));

        str_lines.push(format!(
            "{}{}  {} {}",
            player_space,
            self.stock[0].str_display(),
            self.waste[0].str_display(),
            self.crape[0].str_display()
        ));

        str_lines.join("\n")
    }

    /// Compute the first player at the start of the game.
    ///
    /// It's the player with the highest card on top of their crape pile.
    /// In case of equality, it's the player with the highest card dealed on the tableau.
    /// In case of equality, it's just player 0...
    ///
    /// Warning: this function panics if crape or tableau piles are empty
    pub fn compute_first_player(&self) -> Player {
        let crape_rank_p0 = self.crape[0]
            .top_rank()
            .expect("Crape should not be empty on start");
        let crape_rank_p1 = self.crape[1]
            .top_rank()
            .expect("Crape should not be empty on start");

        if crape_rank_p0 > crape_rank_p1 {
            Player::Player0
        } else if crape_rank_p0 < crape_rank_p1 {
            Player::Player1
        } else {
            let max_p0 = self.tableau_piles[..NB_ROWS]
                .iter()
                .map(|pile| pile.top_rank().unwrap())
                .max()
                .unwrap();
            let max_p1 = self.tableau_piles[NB_ROWS..]
                .iter()
                .map(|pile| pile.top_rank().unwrap())
                .max()
                .unwrap();
            if max_p0 > max_p1 {
                Player::Player0
            } else {
                Player::Player1
            }
        }
    }

    /// Move a card on the board, from one pile to another
    ///
    /// All checks are done to ensure that the move is valid.
    pub fn move_card_checked(
        &mut self,
        origin_type: &PileType,
        destination_type: &PileType,
        player: Player,
    ) -> Result<Move, &'static str> {
        let origin = self.pile_from_type(origin_type);
        let destination = self.pile_from_type(destination_type);

        let card = origin
            .top_card()
            .ok_or("Unable to take a card from empty pile")?;

        if !card.face_up {
            return Err("Unable to move a card which faces down");
        }

        if !origin.can_pop_card(&player) {
            return Err("Unable to take card from origin");
        }

        if !destination.can_add_card(card, &origin_type, &player) {
            return Err("Unable to move card from origin to destination");
        }

        self.move_card(origin_type, destination_type)
            .ok_or("Unable to move card")
    }

    /// Move a card on the board, from one pile to another
    ///
    /// This is a low level move, nothing is checked:
    ///   - the origin pile must not be empty, otherwise it panics
    ///   - game-wise, the move may be valid or not
    fn move_card(&mut self, origin_type: &PileType, destination_type: &PileType) -> Option<Move> {
        // Actually apply the move
        let card = self
            .pile_from_type_mut(origin_type)
            .pop()
            .expect("Pile must not be empty");
        self.pile_from_type_mut(destination_type).add(card);
        Some(Move::Move {
            card: card,
            origin: *origin_type,
            destination: *destination_type,
        })
    }

    pub fn flip_card_up(&mut self, pile_type: &PileType, player: &Player) {
        let pile = self.pile_from_type_mut(pile_type);
        if pile.can_flip_card_up(player) {
            if let Some(card) = pile.top_card_mut() {
                card.set_face_up();
            }
        }
    }

    /// Check if the player has won the game, i.e. their piles are empty.
    pub fn check_win(&self, player: Player) -> bool {
        self.stock[player as usize].is_empty()
            && self.waste[player as usize].is_empty()
            && self.crape[player as usize].is_empty()
    }
}

#[cfg(test)]
mod tests {
    use crate::core::decks::new_rng;

    use super::*;

    #[test]
    fn test_new_game() {
        let mut board = Board::new();
        let mut rng = new_rng("test");
        board.new_game(&mut rng);
        for p in 0..=1 {
            assert_eq!(board.stock[p].nb_cards(), 52 - 13 - 4);
            assert_eq!(board.waste[p].nb_cards(), 0);
            assert_eq!(board.crape[p].nb_cards(), 13);
            assert_eq!(board.crape[p].top_card().unwrap().face_up, true);
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
        let mut rng = new_rng("test");
        board.new_game(&mut rng);
        board.new_game(&mut rng);
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
        let mut rng = new_rng("test");
        board.new_game(&mut rng);
        assert_eq!(board.check_win(Player::Player0), false);
        assert_eq!(board.check_win(Player::Player1), false);
    }
}
