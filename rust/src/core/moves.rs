use std::fmt;

use super::cards::Card;
use super::piles::PileType;

#[derive(Debug, Clone, Copy)]
pub enum CardAction {
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

impl fmt::Display for CardAction {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            CardAction::Move {
                card,
                origin,
                destination,
            } => write!(f, "Move {} from {} to {}", card, origin, destination),
            CardAction::Flip { card, pile } => write!(f, "Flip {} in {}", card, pile),
            CardAction::FlipWaste => write!(f, "FlipWaste"),
        }
    }
}
