pub const MIN_RANK: u8 = 1;
pub const MAX_RANK: u8 = 13;
pub const NB_RANKS: usize = MAX_RANK as usize;

const RANK_TEXTS: [(char, &str); NB_RANKS] = [
    ('A', "Ace"),
    ('2', "2"),
    ('3', "3"),
    ('4', "4"),
    ('5', "5"),
    ('6', "6"),
    ('7', "7"),
    ('8', "8"),
    ('9', "9"),
    ('0', "10"),
    ('J', "Jack"),
    ('Q', "Queen"),
    ('K', "King"),
];

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct Rank(u8);

impl From<u8> for Rank {
    fn from(item: u8) -> Self {
        match item {
            MIN_RANK..=MAX_RANK => Rank(item),
            _ => panic!("Incorrect card rank {item}"),
        }
    }
}

impl From<&str> for Rank {
    fn from(item: &str) -> Self {
        let index = RANK_TEXTS
            .iter()
            .position(|&(symbol, name)| name == item || item.chars().eq([symbol]))
            .unwrap_or_else(|| panic!("Incorrect card rank {item}"));

        Rank(index as u8 + 1)
    }
}

impl From<char> for Rank {
    fn from(item: char) -> Self {
        Rank::from(item.to_string().as_str())
    }
}

impl Rank {
    pub fn symbol(self) -> char {
        RANK_TEXTS[(self.0 - 1) as usize].0
    }

    pub fn name(self) -> &'static str {
        RANK_TEXTS[(self.0 - 1) as usize].1
    }

    /// Check if the rank is just above or just below the other rank
    pub fn is_above_or_below(self, other: Rank) -> bool {
        self.0.abs_diff(other.0) == 1
    }

    pub fn is_above(self, other: Rank) -> bool {
        self.0 == other.0 + 1
    }

    pub fn is_below(self, other: Rank) -> bool {
        self.0 == other.0 - 1
    }

    pub fn as_u8(self) -> u8 {
        self.0
    }
}

impl PartialEq<usize> for Rank {
    fn eq(&self, other: &usize) -> bool {
        self.0 as usize == *other
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_new_rank() {
        assert_eq!(Rank::from(1), Rank(1));
        assert_eq!(Rank::from(13), Rank(13));
    }

    #[test]
    #[should_panic]
    fn test_new_rank_invalid0() {
        let _ = Rank::from(0);
    }

    #[test]
    #[should_panic]
    fn test_new_rank_invalid14() {
        let _ = Rank::from(14);
    }

    #[test]
    fn test_symbol() {
        assert_eq!(Rank::from(1).symbol(), 'A');
        assert_eq!(Rank::from(2).symbol(), '2');
        assert_eq!(Rank::from(10).symbol(), '0');
        assert_eq!(Rank::from(11).symbol(), 'J');
        assert_eq!(Rank::from(12).symbol(), 'Q');
        assert_eq!(Rank::from(13).symbol(), 'K');
    }

    #[test]
    fn test_name() {
        assert_eq!(Rank::from(1).name(), "Ace");
        assert_eq!(Rank::from(2).name(), "2");
        assert_eq!(Rank::from(10).name(), "10");
        assert_eq!(Rank::from(11).name(), "Jack");
        assert_eq!(Rank::from(12).name(), "Queen");
        assert_eq!(Rank::from(13).name(), "King");
    }

    #[test]
    fn test_from_str() {
        assert_eq!(Rank::from("A"), Rank(1));
        assert_eq!(Rank::from("2"), Rank(2));
        assert_eq!(Rank::from("0"), Rank(10));
        assert_eq!(Rank::from("K"), Rank(13));
    }
}
