use super::cards::Card;
use super::decks::NB_CARDS;
use super::players::Player;
use super::ranks::{Rank, NB_RANKS};
use super::suits::Suit;

pub const NB_CRAPE_START: usize = 13;

#[derive(Debug)]
pub struct Pile {
    pub cards: Vec<Card>,
    pub kind: PileType,
}

#[derive(Debug, Clone, Copy)]
pub enum PileType {
    Foundation {
        foundation_id: u8,
        foundation_suit: Suit,
    },
    Tableau {
        tableau_id: u8,
    },
    Stock {
        player: Player,
    },
    Waste {
        player: Player,
    },
    Crape {
        player: Player,
    },
}

impl Pile {
    pub fn new_foundation(foundation_id: u8, foundation_suit: Suit) -> Self {
        Pile {
            cards: Vec::<Card>::with_capacity(NB_RANKS),
            kind: PileType::Foundation {
                foundation_id,
                foundation_suit,
            },
        }
    }
    pub fn new_tableau(tableau_id: u8) -> Self {
        Pile {
            cards: Vec::<Card>::with_capacity(NB_RANKS),
            kind: PileType::Tableau { tableau_id },
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

    pub fn str_display(&self) -> String {
        match &self.kind {
            PileType::Foundation { .. }
            | PileType::Stock { .. }
            | PileType::Waste { .. }
            | PileType::Crape { .. } => match self.top_card() {
                None => "  ".to_string(),
                Some(top_card) => top_card.str_display(),
            },
            PileType::Tableau { tableau_id: 0..=3 } => {
                // Right side
                let mut result = "".to_string();
                for card in self.cards.iter() {
                    result += &card.str_display();
                    result += " ";
                }
                result
            }
            PileType::Tableau { tableau_id: 4..=7 } => {
                // Left side
                let mut result = "".to_string();
                for card in self.cards.iter().rev() {
                    result += &card.str_display();
                    result += " ";
                }
                result
            }
            PileType::Tableau {
                tableau_id: 8..=u8::MAX,
            } => panic!("PileType::Tableau.tableau_id > 7"),
        }
    }

    pub fn can_add_card(&self, card: &Card, origin: &PileType, player: &Player) -> bool {
        match &self.kind {
            PileType::Foundation {
                foundation_suit, ..
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
