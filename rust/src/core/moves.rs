use super::cards::Card;
use super::piles::PileType;

#[derive(Debug, Clone, Copy)]
pub enum Move {
    Move {
        card: Card,
        origin: PileType,
        destination: PileType,
    },
    Flip {
        card: Card,
        pile: PileType,
    },
    FlipWaste,
}
