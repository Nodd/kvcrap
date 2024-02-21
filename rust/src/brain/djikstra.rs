use std::collections::{BTreeSet, BinaryHeap, HashMap};
use std::rc::Rc;
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
    known_nodes: HashMap<Board, Rc<BoardNode>>,
    known_unvisited_nodes: BTreeSet<Rc<BoardNode>>,
}
impl BrainDijkstra {
    pub fn new(board: Board, player: Player) -> Self {
        let mut brain_djikstra = BrainDijkstra {
            known_nodes: HashMap::new(),
            known_unvisited_nodes: BTreeSet::new(),
        };
        let first_node = BoardNode::new(board, player);
        let first_node_rc = Rc::new(first_node);
        brain_djikstra
            .known_nodes
            .insert(board, first_node_rc.clone());
        brain_djikstra.known_unvisited_nodes.insert(first_node_rc);

        brain_djikstra
    }

    fn select_next_node(&mut self) -> Option<Rc<BoardNode>> {
        self.known_unvisited_nodes
            .take(&self.known_unvisited_nodes.first().unwrap().clone())
    }

    pub fn search(&mut self) -> (Vec<crate::brain::djikstra::CardAction>, usize) {
        let mut max_score = WORSE_SCORE;
        let moves: Vec<CardAction> = Vec::new();
        let mut nb_nodes_visited = 0;
        let mut best_node: Rc<BoardNode>;
        loop {
            match self.select_next_node() {
                None => {
                    break;
                }
                Some(mut next_node) => {
                    nb_nodes_visited += 1;
                    next_node
                        .search_neighbors(&mut self.known_nodes, &mut self.known_unvisited_nodes);
                    next_node.index = nb_nodes_visited;
                    if next_node.score > max_score {
                        max_score = next_node.score;
                        best_node = next_node;
                    }
                }
            }
        }

        (moves, nb_nodes_visited)
    }
}
