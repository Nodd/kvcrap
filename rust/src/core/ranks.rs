pub const MIN_RANK: u8 = 1;
pub const MAX_RANK: u8 = 13;
//const RANKS: Vec<u8> = (MIN_RANK..=MAX_RANK).collect::<Vec<u8>>();
pub const NB_RANKS: usize = MAX_RANK as usize;

// TODO: Implement as tuple `pub struct Rank(u8)` ?
#[derive(Debug, Clone, Copy)]
pub struct Rank {
    rank: u8,
}

impl From<u8> for Rank {
    fn from(item: u8) -> Self {
        match item {
            MIN_RANK..=MAX_RANK => Rank { rank: item },
            _ => panic!("Incorrect card rank {item}"),
        }
    }
}

impl Rank {
    pub fn symbol(&self) -> char {
        match self.rank {
            1 => 'A',
            2..=9 => format!("{}", self.rank)
                .chars()
                .next()
                .expect("string is empty"),
            10 => '0',
            11 => 'J',
            12 => 'Q',
            13 => 'K',
            _ => panic!("Incorrect card rank {}", self.rank),
        }
    }

    pub fn name(&self) -> String {
        match self.rank {
            1 => "Ace".to_string(),
            2..=10 => format!("{}", self.rank),
            11 => "Jack".to_string(),
            12 => "Queen".to_string(),
            13 => "King".to_string(),
            _ => panic!("Incorrect card rank {}", self.rank),
        }
    }

    pub fn above(&self) -> Rank {
        Rank::from(self.rank + 1)
    }

    pub fn below(&self) -> Rank {
        Rank::from(self.rank - 1)
    }
}

impl PartialEq for Rank {
    fn eq(&self, other: &Self) -> bool {
        self.rank == other.rank
    }
}
impl Eq for Rank {}

impl PartialEq<usize> for Rank {
    fn eq(&self, other: &usize) -> bool {
        self.rank as usize == *other
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_new_rank() {
        assert_eq!(Rank::from(1), Rank { rank: 1 });
        assert_eq!(Rank::from(13), Rank { rank: 13 });
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
