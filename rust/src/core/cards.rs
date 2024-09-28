use colored::{ColoredString, Colorize};
use regex::Regex;
use std::cmp::Ordering;
use std::hash::{Hash, Hasher};

use super::players::Player;
use super::ranks::Rank;
use super::suits::{Color, Suit};

#[derive(Debug, Clone, Copy)]
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
    pub fn new_up(rank: Rank, suit: Suit, player: Player) -> Self {
        Card {
            rank,
            suit,
            player,
            face_up: true,
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

    /// Check if the rank is above or below the other card's rank
    pub fn is_above_or_below(&self, other: &Card) -> bool {
        self.rank.is_above_or_below(&other.rank)
    }

    pub fn str_rank_suit(&self, colored: bool) -> String {
        let mut str = format!("{}{}", self.rank.symbol(), self.suit.symbol());
        if colored {
            str = match self.suit.color() {
                Color::Red => str.red(),
                Color::Black => str.black(),
            }
            .on_white()
            .to_string();
        }
        str
    }

    pub fn str_display(&self, colored: bool) -> String {
        if self.face_up {
            self.str_rank_suit(colored)
        } else {
            let base = "##";
            if colored {
                match self.player {
                    Player::Player0 => base.bright_green().on_green(),
                    Player::Player1 => base.bright_blue().on_blue(),
                }
                .to_string()
            } else {
                base.to_string()
            }
        }
    }
}

impl PartialEq for Card {
    fn eq(&self, other: &Self) -> bool {
        // Only check rank and suit
        // Player and face up/down are mostly visual and seldom needed
        self.rank == other.rank && self.suit == other.suit
    }
}
impl Eq for Card {}

impl Ord for Card {
    fn cmp(&self, other: &Self) -> Ordering {
        if self.rank == other.rank {
            return self.suit.cmp(&other.suit);
        } else {
            return self.rank.cmp(&other.rank);
        }
    }
}
impl PartialOrd for Card {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl Hash for Card {
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.rank.hash(state);
        self.suit.hash(state);
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
    fn test_eq() {
        let c = Card::quick("1d0");
        assert_eq!(c, c);
        let cc = Card::quick("1d0");
        assert_eq!(c, cc);
        let cc = Card::quick("1d1");
        assert_eq!(c, cc);
        let cc = Card::quick("2s1");
        assert_ne!(c, cc);
    }

    #[test]
    fn test_ord() {
        let c = Card::quick("1d0");
        assert_eq!(c < c, false);
        assert_eq!(c > c, false);
        assert_eq!(c <= c, true);
        assert_eq!(c >= c, true);
        let cc = Card::quick("1d0");
        assert_eq!(c < cc, false);
        assert_eq!(c > cc, false);
        assert_eq!(c <= cc, true);
        assert_eq!(c >= cc, true);
        let cc = Card::quick("1d1");
        assert_eq!(c < cc, false);
        assert_eq!(c > cc, false);
        assert_eq!(c <= cc, true);
        assert_eq!(c >= cc, true);
        let cc = Card::quick("2d0");
        assert_eq!(c < cc, true);
        assert_eq!(c > cc, false);
        assert_eq!(c <= cc, true);
        assert_eq!(c >= cc, false);
        let cc = Card::quick("1s0");
        assert_eq!(c < cc, true);
        assert_eq!(c > cc, false);
        assert_eq!(c <= cc, true);
        assert_eq!(c >= cc, false);
    }
}
