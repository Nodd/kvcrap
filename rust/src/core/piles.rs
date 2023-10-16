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

pub trait Pile {
    fn cards(&self) -> &Vec<Card>;
    fn cards_mut(&mut self) -> &mut Vec<Card>;

    fn add(&mut self, card: Card) {
        self.cards_mut().push(card);
    }

    fn pop(&mut self) -> Option<Card> {
        self.cards_mut().pop()
    }

    fn set(&mut self, cards: Vec<Card>) {
        self.cards_mut().clear();
        self.cards_mut().extend(cards);
    }

    fn clear(&mut self) {
        self.cards_mut().clear();
    }

    fn is_empty(&self) -> bool {
        self.cards().is_empty()
    }

    fn nb_cards(&self) -> usize {
        self.cards().len()
    }

    fn top_card(&self) -> &Card {
        // TODO: Check if is empty
        let card_index = self.cards().len() - 1;
        &self.cards()[card_index]
    }

    fn top_card_mut(&mut self) -> &mut Card {
        // TODO: Check if is empty
        let card_index = self.cards().len() - 1;
        &mut self.cards_mut()[card_index]
    }

    fn can_add_card(&self, card: Card, origin: PileTypes, player: Player) -> bool {
        // TODO: implement everywhere, remove default implementation
        false
    }
    fn can_pop_card(&self, player: Player) -> bool {
        // TODO: implement everywhere, remove default implementation
        false
    }
}

#[derive(Debug)]
pub struct FoundationPile {
    cards: Vec<Card>,
    foundation_id: u8,
    foundation_suit: Suit,
}

impl Pile for FoundationPile {
    fn cards(&self) -> &Vec<Card> {
        &self.cards
    }

    fn cards_mut(&mut self) -> &mut Vec<Card> {
        &mut self.cards
    }
}

impl FoundationPile {
    pub fn new(foundation_id: u8, foundation_suit: Suit) -> Self {
        FoundationPile {
            cards: Vec::<Card>::with_capacity(NB_RANKS),
            foundation_id,
            foundation_suit,
        }
    }

    pub fn str_display(&self) -> String {
        if self.cards.is_empty() {
            "  ".to_string()
        } else {
            self.top_card().str_display()
        }
    }
}

#[derive(Debug)]
pub struct TableauPile {
    cards: Vec<Card>,
    tableau_id: u8,
}

impl Pile for TableauPile {
    fn cards(&self) -> &Vec<Card> {
        &self.cards
    }

    fn cards_mut(&mut self) -> &mut Vec<Card> {
        &mut self.cards
    }
}

impl TableauPile {
    pub fn new(tableau_id: u8) -> Self {
        TableauPile {
            cards: Vec::<Card>::with_capacity(NB_RANKS),
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
    cards: Vec<Card>,
    player: Player,
}

impl Pile for StockPile {
    fn cards(&self) -> &Vec<Card> {
        &self.cards
    }

    fn cards_mut(&mut self) -> &mut Vec<Card> {
        &mut self.cards
    }
}

impl StockPile {
    pub fn new(player: Player) -> Self {
        StockPile {
            cards: Vec::<Card>::with_capacity(NB_CARDS),
            player,
        }
    }

    pub fn str_display(&self) -> String {
        if self.cards.is_empty() {
            "  ".to_string()
        } else {
            self.top_card().str_display()
        }
    }
}

#[derive(Debug)]
pub struct WastePile {
    cards: Vec<Card>,
    player: Player,
}

impl Pile for WastePile {
    fn cards(&self) -> &Vec<Card> {
        &self.cards
    }

    fn cards_mut(&mut self) -> &mut Vec<Card> {
        &mut self.cards
    }
}

impl WastePile {
    pub fn new(player: Player) -> Self {
        WastePile {
            cards: Vec::<Card>::with_capacity(NB_CARDS),
            player,
        }
    }

    pub fn str_display(&self) -> String {
        if self.cards.is_empty() {
            "  ".to_string()
        } else {
            self.top_card().str_display()
        }
    }
}

#[derive(Debug)]
pub struct CrapePile {
    cards: Vec<Card>,
    player: Player,
}

impl Pile for CrapePile {
    fn cards(&self) -> &Vec<Card> {
        &self.cards
    }

    fn cards_mut(&mut self) -> &mut Vec<Card> {
        &mut self.cards
    }
}

impl CrapePile {
    pub fn new(player: Player) -> Self {
        CrapePile {
            cards: Vec::<Card>::with_capacity(NB_CARDS),
            player,
        }
    }

    pub fn str_display(&self) -> String {
        if self.cards.is_empty() {
            "  ".to_string()
        } else {
            self.top_card().str_display()
        }
    }
}
