pub const NB_SUITS: usize = 4;

#[derive(PartialEq, Eq, PartialOrd, Ord, Debug, Clone, Copy, Hash)]
pub enum Suit {
    // The declaration order determines the suit ordering
    // spade > heart > diamond > club
    Club,
    Diamond,
    Heart,
    Spade,
}
#[derive(PartialEq, Eq, Debug, Clone, Copy)]
pub enum Color {
    Red,
    Black,
}

impl From<char> for Suit {
    fn from(item: char) -> Self {
        match item {
            'c' | '♣' => Suit::Club,
            'd' | '♦' => Suit::Diamond,
            'h' | '♥' => Suit::Heart,
            's' | '♠' => Suit::Spade,
            _ => panic!("Incorrect letter {item} for suit"),
        }
    }
}

impl Suit {
    /// All suits, in declaration order
    pub const ALL: [Suit; NB_SUITS] = [Suit::Club, Suit::Diamond, Suit::Heart, Suit::Spade];

    /// Returns the symbol associated with the suit
    pub fn symbol(self) -> char {
        match self {
            Suit::Club => '♣',
            Suit::Diamond => '♦',
            Suit::Heart => '♥',
            Suit::Spade => '♠',
        }
    }
    /// Returns the letter associated with the suit
    pub fn letter(self) -> char {
        match self {
            Suit::Club => 'c',
            Suit::Diamond => 'd',
            Suit::Heart => 'h',
            Suit::Spade => 's',
        }
    }

    /// Returns the color of the suit
    pub fn color(self) -> Color {
        match self {
            Suit::Diamond | Suit::Heart => Color::Red,
            Suit::Club | Suit::Spade => Color::Black,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_suit_from_char() {
        assert_eq!(Suit::from('c'), Suit::Club);
        assert_eq!(Suit::from('d'), Suit::Diamond);
        assert_eq!(Suit::from('h'), Suit::Heart);
        assert_eq!(Suit::from('s'), Suit::Spade);
    }

    #[test]
    fn test_all_is_complete() {
        assert_eq!(Suit::ALL.len(), NB_SUITS);
        for (i, a) in Suit::ALL.iter().enumerate() {
            for b in &Suit::ALL[i + 1..] {
                assert_ne!(a, b);
            }
        }
    }

    #[test]
    fn test_letter_roundtrip() {
        // Pour chaque couleur, lettre -> couleur doit redonner la couleur de départ
        for suit in Suit::ALL {
            assert_eq!(Suit::from(suit.letter()), suit);
        }
    }

    #[test]
    fn test_symbol() {
        assert_eq!(Suit::Club.symbol(), '♣');
        assert_eq!(Suit::Diamond.symbol(), '♦');
        assert_eq!(Suit::Heart.symbol(), '♥');
        assert_eq!(Suit::Spade.symbol(), '♠');
    }

    #[test]
    fn test_color() {
        assert_eq!(Suit::Club.color(), Color::Black);
        assert_eq!(Suit::Diamond.color(), Color::Red);
        assert_eq!(Suit::Heart.color(), Color::Red);
        assert_eq!(Suit::Spade.color(), Color::Black);
    }

    #[test]
    fn test_ord() {
        assert!(Suit::Club < Suit::Diamond);
        assert!(Suit::Diamond < Suit::Heart);
        assert!(Suit::Heart < Suit::Spade);
    }
}
