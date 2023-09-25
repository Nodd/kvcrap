#[derive(PartialEq, Debug, Clone, Copy)]
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

impl Player {
    /// Returns the other player.
    pub fn other(&self) -> Self {
        match self {
            Player::Player0 => Player::Player1,
            Player::Player1 => Player::Player0,
        }
    }
}
