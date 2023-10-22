pub const NB_SUITS: usize = 4;

#[derive(PartialEq, Debug, Clone, Copy, Hash)]
pub enum Suit {
    Diamond,
    Heart,
    Club,
    Spade,
}
#[derive(PartialEq)]
pub enum Color {
    Red,
    Black,
}

impl From<char> for Suit {
    fn from(item: char) -> Self {
        match item {
            'd' => Suit::Diamond,
            'h' => Suit::Heart,
            'c' => Suit::Club,
            's' => Suit::Spade,
            /*
            '\u{2666}' => Suit::Diamond,
            '\u{2665}' => Suit::Heart,
            '\u{2663}' => Suit::Club,
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
            Suit::Diamond => '\u{2666}',
            Suit::Heart => '\u{2665}',
            Suit::Club => '\u{2663}',
            Suit::Spade => '\u{2660}',
        }
    }
    /// Returns the letter associated with the suit
    pub fn letter(&self) -> char {
        match self {
            Suit::Diamond => 'd',
            Suit::Heart => 'h',
            Suit::Club => 'c',
            Suit::Spade => 's',
        }
    }

    /// Returns the color of the suit
    pub fn color(&self) -> Color {
        match self {
            Suit::Diamond => Color::Red,
            Suit::Heart => Color::Red,
            Suit::Club => Color::Black,
            Suit::Spade => Color::Black,
        }
    }

    pub fn into_iter() -> core::array::IntoIter<Self, NB_SUITS> {
        [Suit::Diamond, Suit::Heart, Suit::Club, Suit::Spade].into_iter()
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
}
