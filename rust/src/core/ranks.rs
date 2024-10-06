use std::cmp::Ordering;

pub const MIN_RANK: u8 = 1;
pub const MAX_RANK: u8 = 13;
pub const NB_RANKS: usize = MAX_RANK as usize;

const SYMBOLS: [char; NB_RANKS] = [
    'A', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'J', 'Q', 'K',
];
const NAMES: [&str; NB_RANKS] = [
    "Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King",
];

#[derive(Debug, Clone, Copy, Hash)]
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
        match item.parse::<u8>() {
            Ok(0) => Rank(10),
            Ok(i) => Rank(i),
            Err(_) => {
                if item.len() == 1 {
                let c = item.chars().next().unwrap();
                match SYMBOLS.iter().position(|x| *x == c) {
                    Some(pos) => Rank(pos as u8 + 1),
                    None => panic!("Incorrect card rank {item}"),
                    }
                } else {
                    match NAMES.iter().position(|x| *x == item) {
                        Some(pos) => Rank(pos as u8 + 1),
                        None => panic!("Incorrect card rank {item}"),
                    }
                }
            }
        }
    }
}

impl Rank {
    pub fn symbol(&self) -> char {
        SYMBOLS[(self.0 - 1) as usize]
    }

    pub fn name(&self) -> &'static str {
        NAMES[(self.0 - 1) as usize]
    }

    /// Check if the rank is just above or just below the other rank
    pub fn is_above_or_below(&self, other: &Rank) -> bool {
        self.0 == &other.0 - 1 || self.0 == &other.0 + 1
    }

    pub fn is_above(&self, other: &Rank) -> bool {
        self.0 == &other.0 + 1
    }

    pub fn is_below(&self, other: &Rank) -> bool {
        self.0 == &other.0 - 1
    }
}

impl PartialEq for Rank {
    fn eq(&self, other: &Self) -> bool {
        self.0 == other.0
    }
}
impl PartialEq<usize> for Rank {
    fn eq(&self, other: &usize) -> bool {
        self.0 as usize == *other
    }
}
impl Eq for Rank {}

impl PartialOrd for Rank {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        self.0.partial_cmp(&other.0)
    }
}
impl Ord for Rank {
    fn cmp(&self, other: &Self) -> std::cmp::Ordering {
        self.0.cmp(&other.0)
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
}
