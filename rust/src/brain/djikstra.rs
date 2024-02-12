use std::collections::{BinaryHeap, HashMap};
use std::time::Instant;

use crate::core::board::Board;
use crate::core::moves::CardAction;
use crate::core::players::Player;

use super::board_node::BoardNode;
use super::board_score::{board_score, WORSE_SCORE};

pub struct RustBrainConfig {
    shortcut: bool,
    filter_piles_orig: bool,
    filter_piles_orig_aggressive: bool,
    mono: bool,
    print_progress: bool,
    reproducible: bool,
}

pub fn compute_states(board: &Board, active_player: Player, crapette_mode: bool, log_path: &str) {
    let start_time = Instant::now();

    //let moves, nb_nodes_visited = brain_dijkstra(board, active_player, crapette_mode, log_path);

    /*
    if not moves:
    player_piles = self.game_config.board.players_piles[
        self.game_config.active_player
    ]
    crape = player_piles.crape
    stock = player_piles.stock
    if crape and not crape.top_card.face_up:
        moves = [Flip(crape.top_card, crape)]
    elif not stock:
        moves = [FlipWaste()]
    elif not stock.top_card.face_up:
        moves = [Flip(stock.top_card, stock)]
    else:
        moves = [Move(stock.top_card, stock, player_piles.waste)]
    # TODO: manage the case of an empty stock and non-empty crape
    */

    println!("{:#?}", start_time.elapsed())
}

pub struct BrainDijkstra {
    known_nodes: HashMap<Board, BoardNode>,
    known_nodes_unvisited: BinaryHeap<BoardNode>,
}
/*
impl BrainDijkstra {
    pub fn new(board: Board, player: Player) -> Self {
        let mut brain_djikstra = BrainDijkstra {
            known_nodes: HashMap::new {},
            known_nodes_unvisited: BinaryHeap::<BoardNode>::new {},
        };
        let first_node = BoardNode::new(board, player);
        brain_djikstra.known_nodes[&board] = first_node;
        brain_djikstra.known_nodes_unvisited.push(first_node);
        return brain_djikstra;
    }

    fn select_next_node(&mut self) -> Option<BoardNode> {
        let board_node: Option<BoardNode>;
        let visited = true;
        while visited {
            board_node = &self.known_nodes_unvisited.pop();
            match board_node {
                None => return None,
                Some(bn) => {
                    if !bn.visited {
                        return board_node;
                    }
                }
            }
        }
        return None;
    }

    pub fn search(&mut self) -> (Vec<Move>, usize) {
        let mut max_score = WORSE_SCORE;
        let moves: Vec<Move> = Vec::new();
        let nb_nodes_visited = 0;
        loop {
            match self.select_next_node() {
                None => {
                    break;
                }
                Some(next_node) => {
                    nb_nodes_visited += 1;
                    next_node.search_neighbors(&self.known_nodes, &self.known_nodes_unvisited);
                    next_node.index = nb_nodes_visited;
                    if next_node.score > max_score {
                        max_score = next_node.score;
                        best_node = next_node;
                    }
                }
            }
        }

        return (moves, nb_nodes_visited);
    }
}
*/
