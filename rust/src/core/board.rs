use core::panic;
use std::cmp::Ordering;
use std::hash::{Hash, Hasher};

use rand_pcg::Pcg64;

use super::cards::Card;
use super::decks::{new_deck, shuffle, NB_CARDS};
use super::moves::CardAction;
use super::piles::{Pile, PileType, NB_CRAPE_START};
use super::players::{Player, NB_PLAYERS, PLAYERS};
use super::ranks::NB_RANKS;
use super::suits::Suit;

pub const NB_PILES_CENTER: usize = 8;
pub const NB_ROWS: usize = 4;
const NB_PILES_TOTAL: usize = 2 * NB_PILES_CENTER + 3 * NB_PLAYERS;
const PLAYER_SPACE: usize = NB_RANKS * 3;

#[derive(Debug, Clone)]
pub struct Board {
    pub stock: [Pile; NB_PLAYERS],
    pub waste: [Pile; NB_PLAYERS],
    pub crape: [Pile; NB_PLAYERS],
    pub foundation: [Pile; NB_PILES_CENTER],
    pub tableau: [Pile; NB_PILES_CENTER],
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
            foundation: [
                Pile::new_foundation(0, Suit::Diamond),
                Pile::new_foundation(1, Suit::Club),
                Pile::new_foundation(2, Suit::Heart),
                Pile::new_foundation(3, Suit::Spade),
                Pile::new_foundation(4, Suit::Spade),
                Pile::new_foundation(5, Suit::Heart),
                Pile::new_foundation(6, Suit::Club),
                Pile::new_foundation(7, Suit::Diamond),
            ],
            tableau: [
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
            let player = player;

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

    // Quickly fill an empty board from a string of cards
    // See Card::quick
    pub fn quick(&mut self, str: &str) {
        let mut player = Player::Player1;
        for mut s in str.lines() {
            s = s.trim();
            if s.is_empty() {
                continue;
            }
            let (mut pile_code, mut cards) =
                s.split_once(":").expect("Needs a format <type>: cards...");
            pile_code = pile_code.trim();
            cards = cards.trim();
            let mut pile_code_chars = pile_code.chars();
            let code = pile_code_chars.next().expect("Empty pile code");
            let number = pile_code_chars
                .next()
                .expect("Code too short")
                .to_digit(10)
                .expect("Code should be a letter and a number") as usize;
            let pile = match code {
                'X' => &mut self.waste[Player::from(number)],
                'C' => &mut self.crape[Player::from(number)],
                'S' => &mut self.stock[Player::from(number)],
                'T' => &mut self.tableau[number],
                'F' => &mut self.foundation[number],
                _ => panic!("Unknown pile code: {}", pile_code),
            };
            pile.quick(cards);
        }
    }

    fn prepare_deck(&self, player: Player, rng: &mut Pcg64) -> Vec<Card> {
        let mut deck = new_deck(player);
        shuffle(&mut deck, rng);
        deck
    }

    fn fill_crape(&mut self, player: Player, deck: &mut Vec<Card>) {
        let crape = deck.split_off(deck.len() - NB_CRAPE_START);
        self.crape[player].set(crape);
        let card: &mut Card = self.crape[player].top_card_mut().unwrap();
        card.set_face_up();
    }

    fn fill_tableau(&mut self, player: Player, deck: &mut Vec<Card>) {
        let player = player as usize;
        for tp in self.tableau[(NB_ROWS * player)..(NB_ROWS * (player + 1))].iter_mut() {
            tp.clear();
            let mut card = deck.pop().unwrap();
            card.set_face_up();
            tp.add(card);
        }
    }

    fn fill_stock(&mut self, player: Player, deck: Vec<Card>) {
        self.stock[player].set(deck);
    }

    fn clear_foundation(&mut self) {
        for fp in self.foundation.iter_mut() {
            fp.clear();
        }
    }

    fn pile_from_type(&self, pile_type: &PileType) -> &Pile {
        match pile_type {
            PileType::Foundation {
                id: foundation_id, ..
            } => &self.foundation[*foundation_id as usize],
            PileType::Tableau { id: tableau_id } => &self.tableau[*tableau_id as usize],
            PileType::Stock { player } => &self.stock[*player],
            PileType::Waste { player } => &self.waste[*player],
            PileType::Crape { player } => &self.crape[*player],
        }
    }

    fn pile_from_type_mut(&mut self, pile_type: &PileType) -> &mut Pile {
        match pile_type {
            PileType::Foundation {
                id: foundation_id, ..
            } => &mut self.foundation[*foundation_id as usize],
            PileType::Tableau { id: tableau_id } => &mut self.tableau[*tableau_id as usize],
            PileType::Stock { player } => &mut self.stock[*player],
            PileType::Waste { player } => &mut self.waste[*player],
            PileType::Crape { player } => &mut self.crape[*player],
        }
    }

    /// Display the board as a multiline String.
    pub fn to_string(&self, colored: bool) -> String {
        let player_space = " ".repeat(PLAYER_SPACE);

        let mut str_lines = vec![format!(
            "{}{}  {} {}",
            player_space,
            self.crape[1].str_display(colored),
            self.waste[1].str_display(colored),
            self.stock[1].str_display(colored)
        )];

        str_lines.extend((0..NB_ROWS).map(|row| {
            let index_left = row + NB_ROWS;
            let index_right = NB_ROWS - 1 - row;

            let tableau_pile_left = &self.tableau[index_left];
            let tableau_pile_right = &self.tableau[index_right];
            let foundation_pile_left = &self.foundation[index_left];
            let foundation_pile_right = &self.foundation[index_right];

            format!(
                "{}{}{}│ {} {} │ {}",
                "   ".repeat(NB_RANKS - tableau_pile_left.nb_cards()),
                tableau_pile_left.str_display(colored),
                if tableau_pile_left.is_empty() {
                    ""
                } else {
                    " "
                },
                foundation_pile_left.str_display(colored),
                foundation_pile_right.str_display(colored),
                tableau_pile_right.str_display(colored)
            )
        }));

        str_lines.push(format!(
            "{}{} {}  {}",
            player_space,
            self.stock[0].str_display(colored),
            self.waste[0].str_display(colored),
            self.crape[0].str_display(colored)
        ));

        str_lines.join("\n")
    }

    /// Compute the first player at the start of the game.
    ///
    /// It's the player with the highest card on top of their crape pile.
    /// In case of equality, it's the player with the highest card dealt on the tableau.
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
            let max_p0 = self.tableau[..NB_ROWS]
                .iter()
                .map(|pile| pile.top_rank().unwrap())
                .max()
                .unwrap();
            let max_p1 = self.tableau[NB_ROWS..]
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
    ) -> Result<CardAction, &'static str> {
        let origin = self.pile_from_type(origin_type);
        let destination = self.pile_from_type(destination_type);

        let card = *origin
            .top_card()
            .ok_or("Unable to take a card from empty pile")?;

        if !card.face_up {
            return Err("Unable to move a card which faces down");
        }

        if !origin.can_pop_card(&player) {
            return Err("Unable to take card from origin");
        }

        if !destination.can_add_card(&card, &origin_type, &player) {
            return Err("Unable to move card from origin to destination");
        }

        self.move_card(origin_type, destination_type);
        Ok(CardAction::Move {
            card: card,
            origin: *origin_type,
            destination: *destination_type,
        })
    }

    /// Move a card on the board, from one pile to another
    ///
    /// This is a low level move, nothing is checked:
    ///   - the origin pile must not be empty, otherwise it panics
    ///   - game-wise, the move may be valid or not
    fn move_card(&mut self, origin_type: &PileType, destination_type: &PileType) {
        // Actually apply the move
        let card = self
            .pile_from_type_mut(origin_type)
            .pop()
            .expect("Pile must not be empty");
        self.pile_from_type_mut(destination_type).add(card);
    }

    pub fn flip_card_up(&mut self, pile_type: &PileType, player: &Player) {
        let pile = self.pile_from_type_mut(pile_type);
        if pile.can_flip_card_up(player) {
            if let Some(card) = pile.top_card_mut() {
                card.set_face_up();
            }
        }
    }

    pub fn flip_waste_to_stock(&mut self, player: &Player) {
        let waste = &mut self.waste[*player];
        let stock = &mut self.stock[*player];
        while !waste.is_empty() {
            let card = waste.pop().unwrap();
            card.set_face_down();
            stock.add(card);
        }
    }

    /// Check if the player has won the game, i.e. their piles are empty.
    pub fn check_win(&self, player: Player) -> bool {
        self.stock[player].is_empty()
            && self.waste[player].is_empty()
            && self.crape[player].is_empty()
    }

    pub fn apply_action(&mut self, action: &CardAction) {
        match action {
            CardAction::Move {
                origin,
                destination,
                ..
            } => self.move_card(origin, destination),
            CardAction::Flip { pile } => self.flip_card_up(pile, &Player::Player0),
            CardAction::FlipWaste => self.flip_waste_to_stock(&Player::Player0),
        }
    }

    pub fn copy_with_action(&self, action: &CardAction) -> Self {
        let mut new_board = self.clone();
        new_board.apply_action(&action);
        new_board
    }

    pub fn encode(&self) -> Vec<u8> {
        // An encoding contains each card and each pile size
        // The capacity should be constant
        let mut data = Vec::with_capacity(NB_PILES_TOTAL + 2 * NB_CARDS);
        for pile in &self.stock {
            pile.encode(&mut data);
        }
        for pile in &self.waste {
            pile.encode(&mut data);
        }
        for pile in &self.crape {
            pile.encode(&mut data);
        }

        // The IA implementation needs to not differentiate the order of tableau and foundation
        // so they are sorted first
        // TODO: sort the encodings rather than the piles if it is equivalent ?
        let mut tableau = self.tableau.clone();
        tableau.sort();
        for pile in &tableau {
            pile.encode(&mut data);
        }
        let mut foundation = self.foundation.clone();
        foundation.sort();
        for pile in &foundation {
            pile.encode(&mut data);
        }
        data
    }
}

// TODO: still needed ?
// TODO: if needed, implement with encode ?
// Eq is need to store boards in a HashSet
// Eq implementation can only be done in PartialEq
// Implementing the Eq trait is just an information for the compiler.
// The IA implementation needs to not differentiate the order of tableau and foundation
// so they are sorted first
impl PartialEq for Board {
    fn eq(&self, other: &Self) -> bool {
        self.crape == other.crape
            && self.waste == other.waste
            && self.stock == other.stock
            && sorted_eq(&self.tableau, &other.tableau)
            && sorted_eq(&self.foundation, &other.foundation)
    }
}
impl Eq for Board {} // Requires PartialEq
fn sorted_eq(piles: &[Pile; 8], piles_other: &[Pile; 8]) -> bool {
    let mut piles = piles.clone();
    let mut piles_other = piles_other.clone();
    piles.sort();
    piles_other.sort();
    piles == piles_other
}

impl Ord for Board {
    fn cmp(&self, other: &Self) -> Ordering {
        // It could be implemented with tuples comparison but it would not short circuit :(
        // (self.crape, self.waste, self.stock, sorted(&self.tableau), sorted(&self.foundation))
        //    .cmp(&(other.crape, other.waste, other.stock, sorted(&other.tableau), sorted(&other.foundation)))
        match self.crape.cmp(&other.crape) {
            Ordering::Equal => match self.waste.cmp(&other.waste) {
                Ordering::Equal => match self.stock.cmp(&other.stock) {
                    Ordering::Equal => match sorted_cmp(&self.tableau, &other.tableau) {
                        Ordering::Equal => sorted_cmp(&self.foundation, &other.foundation),
                        ordering => ordering,
                    },
                    ordering => ordering,
                },
                ordering => ordering,
            },
            ordering => ordering,
        }
    }
}
impl PartialOrd for Board {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}
fn sorted_cmp(piles: &[Pile; 8], piles_other: &[Pile; 8]) -> Ordering {
    let mut piles = piles.clone();
    let mut piles_other = piles_other.clone();
    piles.sort();
    piles_other.sort();
    piles.cmp(&piles_other)
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
        for tp in board.tableau.iter() {
            assert_eq!(tp.nb_cards(), 1);
        }
        for tp in board.foundation.iter() {
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
        for tp in board.tableau.iter() {
            assert_eq!(tp.nb_cards(), 1);
        }
        for tp in board.foundation.iter() {
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
