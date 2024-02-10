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
#[derive(PartialEq, Eq, Debug, Clone)]
pub enum Color {
    Red,
    Black,
}

impl From<char> for Suit {
    fn from(item: char) -> Self {
        match item {
            'c' => Suit::Club,
            'd' => Suit::Diamond,
            'h' => Suit::Heart,
            's' => Suit::Spade,
            /*
            '\u{2663}' => Suit::Club,
            '\u{2666}' => Suit::Diamond,
            '\u{2665}' => Suit::Heart,
            '\u{2660}' => Suit::Spade,
             */
            _ => panic!("Incorrect letter {item} for suit"),
        }
    }
}

impl Suit {
    /// Returns the symbol associated with the suit
    pub fn symbol(&self) -> char {
        match self {
            Suit::Club => '\u{2663}',
            Suit::Diamond => '\u{2666}',
            Suit::Heart => '\u{2665}',
            Suit::Spade => '\u{2660}',
        }
    }
    /// Returns the letter associated with the suit
    pub fn letter(&self) -> char {
        match self {
            Suit::Club => 'c',
            Suit::Diamond => 'd',
            Suit::Heart => 'h',
            Suit::Spade => 's',
        }
    }

    /// Returns the color of the suit
    pub fn color(&self) -> Color {
        match self {
            Suit::Club => Color::Black,
            Suit::Diamond => Color::Red,
            Suit::Heart => Color::Red,
            Suit::Spade => Color::Black,
        }
    }

    pub fn into_iter() -> core::array::IntoIter<Self, NB_SUITS> {
        [Suit::Club, Suit::Diamond, Suit::Heart, Suit::Spade].into_iter()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_suit_from_char() {
        assert_eq!(Suit::from('d'), Suit::Diamond);
    }

    #[test]
    fn test_suit_symbol() {
        // let letter :char = Suit::Diamond.into()
        // assert_eq!(letter, 'd');
        assert_eq!(Suit::Diamond.symbol(), '♦');
    }

    #[test]
    fn test_ord() {
        assert_eq!(Suit::Club < Suit::Diamond, true);
        assert_eq!(Suit::Diamond < Suit::Heart, true);
        assert_eq!(Suit::Heart < Suit::Spade, true);
    }
}
