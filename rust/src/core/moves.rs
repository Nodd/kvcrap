use std::fmt;
use std::ops::{Deref, DerefMut};

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
            CardAction::Flip { pile } => write!(f, "Flip {} top card", pile),
            CardAction::FlipWaste => write!(f, "Flip waste"),
        }
    }
}

#[derive(Clone)]
pub struct CardActions {
    actions: Vec<CardAction>,
}

impl CardActions {
    pub fn new() -> Self {
        CardActions {
            actions: Vec::<CardAction>::new(),
        }
    }
}

impl Deref for CardActions {
    type Target = Vec<CardAction>;

    fn deref(&self) -> &Self::Target {
        &self.actions
    }
}

impl DerefMut for CardActions {
    fn deref_mut(&mut self) -> &mut Self::Target {
        &mut self.actions
    }
}

impl fmt::Display for CardActions {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self.actions.len() {
            0 => write!(f, "No action"),
            1 => write!(f, "1 action: {}", self.actions[0]),
            _ => write!(
                f,
                "{} actions: {}, ...",
                self.actions.len(),
                self.actions[0]
            ),
        }
    }
}

impl fmt::Debug for CardActions {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self.actions.len() {
            0 => write!(f, "No action"),
            1 => write!(f, "1 action:\n  {}", self.actions[0]),
            _ => {
                write!(f, "{} actions:", self.actions.len())?;
                for action in self.actions.iter() {
                    write!(f, "\n  {}", action)?;
                }
                Ok(())
            }
        }
    }
}
