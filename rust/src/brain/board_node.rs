use std::cmp::Ordering;
use std::collections::{BinaryHeap, HashMap, HashSet};
use std::hash::{Hash, Hasher};

use crate::{core::moves::Move, Board, Player};
use crate::{Pile, PileType};

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

    pub fn search_neighbors(
        &mut self,
        known_nodes: HashMap<Board, BoardNode>,
        known_nodes_unvisited: BinaryHeap<BoardNode>,
    ) {
        // This one was searched
        // Note: already popped from known_nodes_unvisited
        self.visited = true;

        // If last move was from a player pile, stop here
        if let Some(last_move) = self.moves.last() {
            if let Move::Move { origin, .. } = last_move {
                if matches!(origin, PileType::Crape { .. } | PileType::Stock { .. }) {
                    return;
                }
            }
        }
    }

    fn piles_dest(&self) {
        // Player piles
        let mut piles: Vec<&Pile> = vec![
            &self.board.crape[self.player.other()],
            &self.board.waste[self.player.other()],
        ];
        // Filter empty piles
        piles.retain(|pile| !pile.is_empty());

        // Tableau piles
        // Remove duplicate Piles
        let tableau_piles_unique = self.board.tableau.iter().collect::<HashSet<&Pile>>();
        let mut sorted_tableau_piles: Vec<&Pile> = tableau_piles_unique.into_iter().collect();
        sorted_tableau_piles.sort();

        // Foundation piles
        let mut foundation_piles = self.board.foundation[0..4].to_vec();
        foundation_piles.retain(|pile| !pile.is_full());
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
