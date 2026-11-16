use colored::Colorize;
use std::cmp::Ordering;
use std::fmt;

use super::players::Player;
use super::ranks::Rank;
use super::suits::{Color, Suit};

#[derive(Debug, Clone, Copy)]
pub struct Card {
    rank: Rank,
    suit: Suit,
    player: Player,
    face_up: bool,
    id: u8,
}

// Represents the card rank and suit a an int for hashing / encoding
// Note that player and face_up are not taken into account.
// id goes up to 60 on 6 bits (2 bits for the suite and 4 for the rank)
fn rank_suit_to_id(rank: Rank, suit: Suit) -> u8 {
    ((suit as u8) << 4) | (rank.as_u8() - 1)
}

impl Card {
    pub fn new(rank: Rank, suit: Suit, player: Player) -> Self {
        Card {
            rank,
            suit,
            player,
            face_up: false,
            id: rank_suit_to_id(rank, suit),
        }
    }
    pub fn new_up(rank: Rank, suit: Suit, player: Player) -> Self {
        Card {
            rank,
            suit,
            player,
            face_up: true,
            id: rank_suit_to_id(rank, suit),
        }
    }

    /// Returns the card from a short string representation
    pub fn quick(card_str: &str) -> Self {
        let chars: Vec<char> = card_str.chars().collect();

        // 2 chars, or 3 with the player
        let (rank, suit, player) = match chars[..] {
            [r, s] => (r, s, '0'),
            [r, s, p] => (r, s, p),
            _ => panic!("Invalid card string: {card_str}"),
        };

        Card::new_up(
            Rank::from(rank),
            Suit::from(suit),
            Player::from(player.to_digit(10).expect("Can not parse player") as u8),
        )
    }

    pub fn rank(&self) -> Rank {
        self.rank
    }

    pub fn suit(&self) -> Suit {
        self.suit
    }

    pub fn player(&self) -> Player {
        self.player
    }

    pub fn id(&self) -> u8 {
        self.id
    }

    pub fn is_face_up(&self) -> bool {
        self.face_up
    }

    pub fn set_face_up(&mut self) {
        self.face_up = true;
    }

    pub fn set_face_down(&mut self) {
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
        self.rank.is_above_or_below(other.rank)
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
        Card::quick("Ad0");
        Card::quick("2s1");
        Card::quick("0h0");
        Card::quick("Kc1");
    }

    #[test]
    fn test_eq() {
        let c = Card::quick("Ad0");
        assert_eq!(c, c);
        let cc = Card::quick("Ad0");
        assert_eq!(c, cc);
        let cc = Card::quick("Ad1");
        assert_eq!(c, cc);
        let cc = Card::quick("2s1");
        assert_ne!(c, cc);
    }

    #[test]
    fn test_ord() {
        let c = Card::quick("Ad0");
        assert!(!(c < c));
        assert!(!(c > c));
        assert!(c <= c);
        assert!(c >= c);
        let cc = Card::quick("Ad0");
        assert!(!(c < cc));
        assert!(!(c > cc));
        assert!(c <= cc);
        assert!(c >= cc);
        let cc = Card::quick("Ad1");
        assert!(!(c < cc));
        assert!(!(c > cc));
        assert!(c <= cc);
        assert!(c >= cc);
        let cc = Card::quick("2d0");
        assert!(c < cc);
        assert!(!(c > cc));
        assert!(c <= cc);
        assert!(!(c >= cc));
        let cc = Card::quick("As0");
        assert!(c < cc);
        assert!(!(c > cc));
        assert!(c <= cc);
        assert!(!(c >= cc));
    }
}
