use super::cards::Card;
use super::players::Player;
use super::suits::Suit;

use super::decks::NB_CARDS;
use super::ranks::NB_RANKS;

pub const NB_CRAPE_START: usize = 13;

#[derive(Debug)]
pub struct Pile {
    pub cards: Vec<Card>,
    pub kind: PileType,
}

#[derive(Debug)]
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
            | PileType::Crape { .. } => {
                if self.cards.is_empty() {
                    "  ".to_string()
                } else {
                    self.top_card().str_display()
                }
            }
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
            PileType::Tableau { .. } => {
                if self.is_empty() {
                    true
                } else {
                    card.rank() == &self.top_card().rank().below()
                        && !card.is_same_color(self.top_card())
                }
            }
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
                } else if self.is_empty() || card.suit() != self.top_card().suit() {
                    false
                } else {
                    card.rank() == &self.top_card().rank().above()
                        || card.rank() == &self.top_card().rank().below()
                }
            }
            PileType::Crape {
                player: self_player,
            } => {
                self_player != player
                    && !self.is_empty()
                    && self.top_card().face_up
                    && card.suit() == self.top_card().suit()
                    && (card.rank() == &self.top_card().rank().above()
                        || card.rank() == &self.top_card().rank().below())
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

    pub fn top_card(&self) -> &Card {
        // TODO: Check if is empty
        let card_index = self.cards.len() - 1;
        &self.cards[card_index]
    }

    pub fn top_card_mut(&mut self) -> &mut Card {
        // TODO: Check if is empty
        let card_index = self.cards.len() - 1;
        &mut self.cards[card_index]
    }
}
