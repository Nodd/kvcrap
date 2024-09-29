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

#[derive(Debug, Clone, Copy, Hash)]
pub enum PileType {
    Foundation { id: u8, suit: Suit },
    Tableau { id: u8 },
    Stock { player: Player },
    Waste { player: Player },
    Crape { player: Player },
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

impl fmt::Display for PileType {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            PileType::Foundation { id, suit } => write!(f, "Foundation{}{}", id, suit.symbol()),
            PileType::Tableau { id } => write!(f, "Tableau{}", id),
            PileType::Stock { player } => write!(f, "Stock{}", player),
            PileType::Waste { player } => write!(f, "Waste{}", player),
            PileType::Crape { player } => write!(f, "Crape{}", player),
        }
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
                .map_or("[]".to_string(), |top_card| top_card.str_display(colored)),
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

impl fmt::Display for Pile {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        // TODO: Use a shorter representation that debug for the cards
        write!(f, "{}({:?})", self.kind, self.cards)
    }
}

// Hash is need to store cards (actually, boards containing piles) in a HashSet
// The IA implementation needs to differentiate the kind and cards only
// PileType::Tableau and PileType::Foundation fields can be ignored here
// PileType::Crape, PileType::Stock and PileType::Waste player field could be used
// but it's not needed in practice (at worst it means a few hash misses for the HashSet)
impl Hash for Pile {
    fn hash<H: Hasher>(&self, state: &mut H) {
        discriminant(&self.kind).hash(state);
        self.cards.hash(state);
    }
}

// Eq is need to store cards (actually, boards containing piles) in a HashSet
// Eq implementation can only be done in PartialEq
// Implementing the Eq trait is just an information for the compiler.
impl PartialEq for Pile {
    fn eq(&self, other: &Self) -> bool {
        if discriminant(&self.kind) != discriminant(&other.kind) {
            unreachable!(
                "Two different kinds of piles ({} and {}) cannot be compared",
                self.kind, other.kind
            )
        }
        // Equal if there are the same cards inside
        // Card equality only checks rank and suit, not player nor facing up or down
        self.cards == other.cards
    }
}
impl Eq for Pile {} // Requires PartialEq

// Ord is needed to sort piles
// Ord requires that the type also be PartialOrd and Eq (which requires PartialEq).
// Comparing different kind should never happen, it's an error in Ord
// First the number of cards is compared, then the cards themselves
impl Ord for Pile {
    fn cmp(&self, other: &Self) -> Ordering {
        if discriminant(&self.kind) == discriminant(&other.kind) {
            match self.nb_cards().cmp(&other.nb_cards()) {
                Ordering::Equal => self.cards.cmp(&other.cards),
                ordering => ordering,
            }
        } else {
            // TODO: define an order between PileTypes, just in case ?
            unreachable!(
                "Two different kinds of piles ({} and {}) cannot be compared",
                self.kind, other.kind
            )
        }
    }
}
impl PartialOrd for Pile {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        if discriminant(&self.kind) != discriminant(&other.kind) {
            return None;
        }
        Some(self.cmp(other))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    // #[test]
    // fn test_piletype_eq() {
    //     assert_eq!(PileType::Tableau { id: 0 }, PileType::Tableau { id: 1 });
    // }
}
