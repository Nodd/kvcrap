use super::cards::Card;
use super::piles::Pile;

pub enum Move {
    Move {
        card: &Card,
        origin: &Pile,
        destination: &Pile,
    },
    Flip {
        card: &Card,
        pile: &Pile,
    },
    FlipWaste,
}
