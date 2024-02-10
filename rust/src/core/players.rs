use std::ops::Index;

#[derive(PartialEq, Debug, Clone, Copy, Hash)]
pub enum Player {
    Player0 = 0,
    Player1 = 1,
}

pub const NB_PLAYERS: usize = 2;
pub const PLAYERS: [Player; NB_PLAYERS] = [Player::Player0, Player::Player1];

impl From<u8> for Player {
    fn from(item: u8) -> Self {
        match item {
            0 => Player::Player0,
            1 => Player::Player1,
            _ => panic!("Incorrect number {item} for player"),
        }
    }
}

// Index 2-element arrays with the Player enum
impl<T> Index<Player> for [T; NB_PLAYERS] {
    type Output = T;

    fn index(&self, player: Player) -> &Self::Output {
        &self[player as usize]
    }
}

impl Player {
    /// Returns the other player.
    pub fn other(&self) -> Self {
        match self {
            Player::Player0 => Player::Player1,
            Player::Player1 => Player::Player0,
        }
    }
}

#[derive(Debug, PartialEq)]
pub enum PlayerType {
    Player,
    AI,
    // remote,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_player_values() {
        assert_eq!(Player::Player0 as usize, 0);
        assert_eq!(Player::Player1 as usize, 1);
    }
}
