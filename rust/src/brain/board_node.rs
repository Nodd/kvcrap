use std::cmp::Ordering;
use std::hash::{Hash, Hasher};

use crate::{core::moves::Move, Board, Player};

use super::board_score::{BoardScore, WORSE_SCORE};

pub struct BoardNode {
    board: Board,
    player: Player,
    // ai_config,
    cost: Vec<usize>,
    pub score: BoardScore,
    //score_min,
    pub visited: bool,
    moves: Vec<Move>,
    pub index: usize,
}

impl BoardNode {
    pub fn new(board: Board, player: Player) -> Self {
        BoardNode {
            board: board,
            player: player,
            // ai_config,
            cost: vec![0],
            score: WORSE_SCORE,
            //score_min,
            visited: false,
            moves: vec![],
            index: 0,
        }
    }
}

impl PartialEq for BoardNode {
    fn eq(&self, other: &Self) -> bool {
        self.board == other.board
    }
}
impl Eq for BoardNode {}

impl Ord for BoardNode {
    fn cmp(&self, other: &Self) -> Ordering {
        if self.cost == other.cost {
            return self.score.cmp(&other.score);
        } else {
            return self.cost.cmp(&other.cost);
        }
    }
}
impl PartialOrd for BoardNode {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl Hash for BoardNode {
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.board.crape.hash(state);
        self.board.waste.hash(state);
        self.board.stock.hash(state);
        self.board.tableau.hash(state);
        self.board.foundation.hash(state);
    }
}
