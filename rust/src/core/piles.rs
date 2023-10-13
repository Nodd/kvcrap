use std::ops::Deref;

use crate::core::cards::Card;
use crate::core::players::Player;
use crate::core::suits::Suit;

use super::decks::NB_CARDS;
use super::ranks::NB_RANKS;

pub enum PileTypes {
    FoundationPile,
    TableauPile,
    StockPile,
    WastePile,
    CrapePile,
}
pub enum PlayerPileTypes {
    StockPile,
    WastePile,
    CrapePile,
}

#[derive(Debug)]
pub struct Pile {
    cards: Vec<Card>,
}

impl Deref for Pile {
    type Target = Vec<Card>;

    fn deref(&self) -> &Self::Target {
        &self.cards
    }
}

impl Pile {
    pub fn new(capacity: usize) -> Self {
        Pile {
            cards: Vec::<Card>::with_capacity(capacity),
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

#[derive(Debug)]
pub struct FoundationPile {
    pub cards: Pile,
    foundation_id: u8,
    foundation_suit: Suit,
}

impl FoundationPile {
    pub fn new(foundation_id: u8, foundation_suit: Suit) -> Self {
        FoundationPile {
            cards: Pile::new(NB_RANKS),
            foundation_id,
            foundation_suit,
        }
    }

    pub fn str_display(&self) -> String {
        if self.cards.is_empty() {
            "  ".to_string()
        } else {
            self.cards.top_card().str_display()
        }
    }
}

#[derive(Debug)]
pub struct TableauPile {
    pub cards: Pile,
    tableau_id: u8,
}

impl TableauPile {
    pub fn new(tableau_id: u8) -> Self {
        TableauPile {
            cards: Pile::new(NB_RANKS),
            tableau_id,
        }
    }

    pub fn str_display_right(&self) -> String {
        let mut result = "".to_string();
        for card in self.cards.iter() {
            result += &card.str_display();
            result += " ";
        }
        result
    }

    pub fn str_display_left(&self) -> String {
        let mut result = "".to_string();
        for card in self.cards.iter().rev() {
            result += &card.str_display();
            result += " ";
        }
        result
    }
}

#[derive(Debug)]
pub struct StockPile {
    pub cards: Pile,
    player: Player,
}
impl StockPile {
    pub fn new(player: Player) -> Self {
        StockPile {
            cards: Pile::new(NB_CARDS),
            player,
        }
    }

    pub fn str_display(&self) -> String {
        if self.cards.is_empty() {
            "  ".to_string()
        } else {
            self.cards.top_card().str_display()
        }
    }
}

#[derive(Debug)]
pub struct WastePile {
    pub cards: Pile,
    player: Player,
}
impl WastePile {
    pub fn new(player: Player) -> Self {
        WastePile {
            cards: Pile::new(NB_CARDS),
            player,
        }
    }

    pub fn str_display(&self) -> String {
        if self.cards.is_empty() {
            "  ".to_string()
        } else {
            self.cards.top_card().str_display()
        }
    }
}

#[derive(Debug)]
pub struct CrapePile {
    pub cards: Pile,
    player: Player,
}

impl CrapePile {
    pub fn new(player: Player) -> Self {
        CrapePile {
            cards: Pile::new(NB_CARDS),
            player,
        }
    }

    pub fn str_display(&self) -> String {
        if self.cards.is_empty() {
            "  ".to_string()
        } else {
            self.cards.top_card().str_display()
        }
    }
}

/*
trait PileTrait {
    fn add_card<T>(&T, card: Card) {
        self.cards.push(card);
    }

    fn pop_card(&self) -> Option<Card> {
        self.cards.pop()
    }

    fn is_empty(&self) -> bool {
        self.cards.is_empty()
    }

    fn top_card(&self) -> &Card {
        // TODO: Check if is empty ?
        &self.cards[self.cards.len() - 1]
    }

    fn can_add_card(&self, card: Card, origin: Pile, player: Player) -> bool;
    fn can_pop_card(&self, player: Player) -> bool {
        false
    }
}
 */
