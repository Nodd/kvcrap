use regex::Regex;

use super::players::Player;
use super::ranks::Rank;
use super::suits::{Color, Suit};

#[derive(Debug)]
pub struct Card {
    rank: Rank,
    suit: Suit,
    player: Player,
    pub face_up: bool,
}

impl Card {
    pub fn new(rank: Rank, suit: Suit, player: Player) -> Self {
        Card {
            rank,
            suit,
            player,
            face_up: false,
        }
    }

    pub fn quick(card_str: &str) -> Self {
        let re: regex::Regex = Regex::new(r"^(?<rank>\d+)(?<suit>\w)(?<player>\d)$").unwrap();
        let (_full, [rank_str, suit_str, player_str]) = re.captures(card_str).unwrap().extract();
        let rank: u8 = rank_str.parse::<u8>().unwrap();
        let suit: char = suit_str.chars().next().expect("string is empty");
        let player: u8 = player_str.parse::<u8>().unwrap();
        Card::new(Rank::from(rank), Suit::from(suit), Player::from(player))
    }

    pub fn rank(&self) -> &Rank {
        &self.rank
    }

    pub fn suit(&self) -> &Suit {
        &self.suit
    }

    pub fn player(&self) -> &Player {
        &self.player
    }

    pub fn set_face_up(&mut self) {
        self.face_up = true;
    }

    pub fn set_face_down(mut self) {
        self.face_up = false;
    }

    /// Returns the symbol associated with the suit
    pub fn suit_symbol(&self) -> char {
        self.suit.symbol()
    }

    /// Returns the color of the card
    pub fn color(&self) -> Color {
        self.suit.color()
    }

    /// Check if the color is the same as another Card
    pub fn is_same_color(&self, other: &Card) -> bool {
        self.suit.color() == other.suit.color()
    }

    pub fn str_rank_suit(&self) -> String {
        format!("{}{}", self.rank.symbol(), self.suit.symbol())
    }

    pub fn str_display(&self) -> String {
        if self.face_up {
            format!("{}{}", self.rank.symbol(), self.suit.symbol())
        } else {
            "##".to_string()
        }
    }
}

impl PartialEq for Card {
    fn eq(&self, other: &Self) -> bool {
        self.rank == other.rank && self.suit == other.suit && self.player == other.player
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_new_card() {
        Card::new(Rank::from(1), Suit::Diamond, Player::Player0);
    }

    #[test]
    fn test_quick() {
        Card::quick("1d0");
        Card::quick("2s1");
        Card::quick("10h0");
        Card::quick("13c1");
    }

    #[test]
    fn test_equal() {
        let c1 = Card::quick("1d0");
        let c2 = Card::quick("1d0");
        assert_eq!(c1, c2);
        let c3 = Card::quick("2s1");
        assert_ne!(c1, c3);
    }
}
