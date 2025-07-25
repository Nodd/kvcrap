use colored::{ColoredString, Colorize};
use regex::Regex;
use std::cmp::Ordering;
use std::fmt;
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
    id: u8,
}

// Represents the card rank and suit a an int for hashing / encoding
// Note that player and face_up are not taken into account.
fn rank_suit_to_id(&rank: &Rank, &suit: &Suit) -> u8 {
    (rank.as_u8() & 0x0F) | ((suit as u8 & 0x03) << 4)
}

impl Card {
    // hash goes up to 4*12+4 = 52
    pub fn new(rank: Rank, suit: Suit, player: Player) -> Self {
        Card {
            rank,
            suit,
            player,
            face_up: false,
            id: rank_suit_to_id(&rank, &suit),
        }
    }
    pub fn new_up(rank: Rank, suit: Suit, player: Player) -> Self {
        Card {
            rank,
            suit,
            player,
            face_up: true,
            id: rank_suit_to_id(&rank, &suit),
        }
    }

    pub fn quick(card_str: &str) -> Self {
        // (?<rank>\w+?) : mandatory, non greedy (1 or more letters)
        // (?<suit>\w) : mandatory (1 letter)
        // (?<player>\d?) : optional (1 letter)
        let re: regex::Regex = Regex::new(r"^(?<rank>\w+?)(?<suit>\w)(?<player>\d?)$").unwrap();
        let (_full, [rank_str, suit_str, player_str]) = re.captures(card_str).unwrap().extract();
        let suit: char = suit_str.chars().next().expect("string is empty");
        let player: u8 = if player_str.is_empty() {
            0
        } else {
            player_str.parse::<u8>().expect("Can not parse player")
        };
        Card::new_up(Rank::from(rank_str), Suit::from(suit), Player::from(player))
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

    pub fn id(&self) -> u8 {
        self.id
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
            let base = "▒▒";
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

impl fmt::Display for Card {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "{}", self.str_rank_suit(false))
    }
}

// TODO: is it still needed ?
// Eq is need to store cards (actually, boards containing piles containing cards) in a HashSet
// Eq implementation can only be done in PartialEq
// Implementing the Eq trait is just an information for the compiler.
impl PartialEq for Card {
    fn eq(&self, other: &Self) -> bool {
        self.rank == other.rank && self.suit == other.suit
    }
}
impl Eq for Card {} // Requires PartialEq

// Ord is needed to sort piles of cards
// Ord requires that the type also be PartialOrd and Eq (which requires PartialEq).
// Rank is the most important field
// Suit is only used do resolve ties and is needed to be coherent with Eq
// but otherwise has no real meaning
impl Ord for Card {
    fn cmp(&self, other: &Self) -> Ordering {
        match self.rank.cmp(&other.rank) {
            Ordering::Equal => self.suit.cmp(&other.suit),
            ordering => ordering,
        }
    }
}
impl PartialOrd for Card {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
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
