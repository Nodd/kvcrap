use colored::{ColoredString, Colorize};
use std::cmp::Ordering;
use std::fmt;
use std::hash::{Hash, Hasher};
use std::mem::discriminant;

use super::cards::Card;
use super::decks::NB_CARDS;
use super::players::Player;
use super::ranks::{Rank, NB_RANKS};
use super::suits::Suit;

pub const NB_CRAPE_START: usize = 13;

#[derive(Debug, Clone, Copy)]
pub enum PileType {
    Foundation { id: u8, suit: Suit },
    Tableau { id: u8 },
    Stock { player: Player },
    Waste { player: Player },
    Crape { player: Player },
}

impl fmt::Display for PileType {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(
            f,
            "{}",
            match self {
                PileType::Foundation { id, suit } => format!("Foundation{}{}", id, suit.symbol()),
                PileType::Tableau { id } => format!("Tableau{}", id),
                PileType::Stock { player } => format!("Stock{}", player),
                PileType::Waste { player } => format!("Waste{}", player),
                PileType::Crape { player } => format!("Crape{}", player),
            }
        )
    }
}

#[derive(Debug, Clone)]
pub struct Pile {
    pub cards: Vec<Card>,
    pub kind: PileType,
}

impl Pile {
    pub fn new_foundation(foundation_id: u8, foundation_suit: Suit) -> Self {
        Pile {
            cards: Vec::<Card>::with_capacity(NB_RANKS),
            kind: PileType::Foundation {
                id: foundation_id,
                suit: foundation_suit,
            },
        }
    }
    pub fn new_tableau(tableau_id: u8) -> Self {
        Pile {
            cards: Vec::<Card>::with_capacity(NB_RANKS),
            kind: PileType::Tableau { id: tableau_id },
        }
    }
    pub fn new_stock(player: Player) -> Self {
        Pile {
            cards: Vec::<Card>::with_capacity(NB_CARDS - NB_CRAPE_START),
            kind: PileType::Stock { player },
        }
    }
    pub fn new_waste(player: Player) -> Self {
        Pile {
            cards: Vec::<Card>::with_capacity(NB_CARDS - NB_CRAPE_START),
            kind: PileType::Waste { player },
        }
    }
    pub fn new_crape(player: Player) -> Self {
        Pile {
            cards: Vec::<Card>::with_capacity(NB_CRAPE_START),
            kind: PileType::Crape { player },
        }
    }

    pub fn str_display(&self, colored: bool) -> String {
        match &self.kind {
            PileType::Foundation { .. }
            | PileType::Stock { .. }
            | PileType::Waste { .. }
            | PileType::Crape { .. } => self
                .top_card()
                .map_or("  ".to_string(), |top_card| top_card.str_display(colored)),
            PileType::Tableau { id: 0..=3 } => {
                // Right side
                self.join_cards(&self.cards.iter().collect::<Vec<_>>(), colored)
            }
            PileType::Tableau { id: 4..=7 } => {
                // Left side
                self.join_cards(&self.cards.iter().rev().collect::<Vec<_>>(), colored)
            }
            PileType::Tableau { id: 8..=u8::MAX } => panic!("PileType::Tableau.tableau_id > 7"),
        }
    }

    fn join_cards(&self, cards: &Vec<&Card>, colored: bool) -> String {
        cards
            .iter()
            .map(|card| card.str_display(colored))
            .collect::<Vec<_>>()
            .join(" ")
    }

    pub fn can_add_card(&self, card: &Card, origin: &PileType, player: &Player) -> bool {
        match &self.kind {
            PileType::Foundation {
                suit: foundation_suit,
                ..
            } => card.suit() == foundation_suit && card.rank() == &(self.nb_cards() + 1),
            PileType::Tableau { .. } => match self.top_card() {
                None => true,
                Some(top_card) => {
                    card.rank().is_below(top_card.rank()) && !card.is_same_color(top_card)
                }
            },
            PileType::Stock { .. } => false,
            PileType::Waste {
                player: self_player,
            } => {
                if self_player == player {
                    // TODO : not in crapette mode
                    match origin {
                        PileType::Stock {
                            player: origin_player,
                        } => origin_player == player,
                        _ => false,
                    }
                } else {
                    match self.top_card() {
                        None => false,
                        Some(top_card) => {
                            card.suit() == top_card.suit() && card.is_above_or_below(top_card)
                        }
                    }
                }
            }
            PileType::Crape {
                player: self_player,
            } => {
                self_player != player
                    && match self.top_card() {
                        None => false,
                        Some(top_card) => top_card.face_up && card.is_above_or_below(top_card),
                    }
            }
        }
    }

    pub fn can_pop_card(&self, player: &Player) -> bool {
        match &self.kind {
            PileType::Foundation { .. } | PileType::Waste { .. } => false,
            PileType::Tableau { .. } => true,
            PileType::Stock {
                player: self_player,
            }
            | PileType::Crape {
                player: self_player,
            } => player == self_player,
        }
    }

    pub fn can_flip_card_up(&self, player: &Player) -> bool {
        match &self.kind {
            PileType::Stock {
                player: self_player,
            }
            | PileType::Crape {
                player: self_player,
            } if player == self_player => {
                if let Some(card) = self.top_card() {
                    !card.face_up
                } else {
                    false
                }
            }
            _ => false,
        }
    }

    pub fn add(&mut self, card: Card) {
        self.cards.push(card);
    }

    pub fn pop(&mut self) -> Option<Card> {
        self.cards.pop()
    }

    pub fn set(&mut self, cards: Vec<Card>) {
        self.cards.clear();
        self.cards.extend(cards);
    }

    pub fn clear(&mut self) {
        self.cards.clear();
    }

    pub fn is_empty(&self) -> bool {
        self.cards.is_empty()
    }

    pub fn is_full(&self) -> bool {
        match self.kind {
            PileType::Foundation { .. } | PileType::Tableau { .. } => self.nb_cards() == NB_RANKS,
            _ => false,
        }
    }

    pub fn is_same(&self, other: &Pile) -> bool {
        self.kind.is_same(&other.kind)
    }

    pub fn nb_cards(&self) -> usize {
        self.cards.len()
    }

    pub fn top_card(&self) -> Option<&Card> {
        self.cards.last()
    }

    pub fn top_card_mut(&mut self) -> Option<&mut Card> {
        self.cards.last_mut()
    }

    pub fn top_rank(&self) -> Option<&Rank> {
        self.cards.last().map(|card| card.rank())
    }
}

impl PartialEq for Pile {
    fn eq(&self, other: &Self) -> bool {
        // Equal if same kind of pile and same cards inside
        // Card equality only checks rank and suit; not player nor facing up or down
        discriminant(&self.kind) == discriminant(&other.kind) && self.cards == other.cards
    }
}
impl Eq for Pile {}

impl PartialOrd for Pile {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        if discriminant(&self.kind) != discriminant(&other.kind) {
            return None;
        }
        Some(self.cmp(other))
    }
}
impl Ord for Pile {
    fn cmp(&self, other: &Self) -> Ordering {
        if discriminant(&self.kind) != discriminant(&other.kind) {
            panic!("Sorting Piles of different kind");
        }
        if self.nb_cards() == other.nb_cards() {
            return self.cards.cmp(&other.cards);
        }
        return self.nb_cards().cmp(&other.nb_cards());
    }
}

impl Hash for Pile {
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.cards.hash(state);
    }
}

impl PileType {
    pub fn is_same(&self, other: &PileType) -> bool {
        if let (PileType::Crape { player: p1 }, PileType::Crape { player: p2 })
        | (PileType::Waste { player: p1 }, PileType::Waste { player: p2 })
        | (PileType::Stock { player: p1 }, PileType::Stock { player: p2 }) = (&self, &other)
        {
            return p1 == p2;
        }

        if let (PileType::Foundation { id: id1, .. }, PileType::Foundation { id: id2, .. })
        | (PileType::Tableau { id: id1, .. }, PileType::Tableau { id: id2, .. }) =
            (&self, &other)
        {
            return id1 == id2;
        }

        false
    }
}
