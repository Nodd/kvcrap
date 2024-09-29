use log::{debug, error, info, trace, warn};
use std::collections::{BTreeSet, BinaryHeap, HashMap};
use std::io::stdin;
use std::rc::Rc;
use std::time::Instant;

use crate::core::board::Board;
use crate::core::moves::{CardAction, CardActions};
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

    let mut brain_dijkstra = BrainDijkstra::new(board, active_player);
    let (moves, nb_nodes_visited) = brain_dijkstra.search();
    println!("nb_nodes_visited: {}", nb_nodes_visited);
    println!("{:?}", moves);

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
    pub fn new(board: &Board, player: Player) -> Self {
        println!("BrainDijkstra.new");
        let mut brain_djikstra = BrainDijkstra {
            known_nodes: HashMap::new(),
            known_unvisited_nodes: BTreeSet::new(),
        };
        let moves = CardActions::new();
        let first_node = BoardNode::new(board.clone(), player, &moves);
        let first_node_rc = Rc::new(first_node);
        brain_djikstra
            .known_nodes
            .insert(board.clone(), first_node_rc.clone());
        brain_djikstra.known_unvisited_nodes.insert(first_node_rc);

        brain_djikstra
    }

    fn select_next_node(&mut self) -> Option<Rc<BoardNode>> {
        // println!("BrainDijkstra.select_next_node");
        trace!("BrainDijkstra.select_next_node");
        debug!("{} nodes to visit", self.known_unvisited_nodes.len());
        self.known_unvisited_nodes.pop_first()
    }

    pub fn search(&mut self) -> (Option<CardActions>, usize) {
        trace!("BrainDijkstra.search");
        let mut max_score = WORSE_SCORE;
        let mut moves: Option<CardActions> = None;
        let mut nb_nodes_visited = 0;
        let mut best_node: Rc<BoardNode>;
        loop {
            match self.select_next_node() {
                None => {
                    break;
                }
                Some(mut next_node) => {
                    debug!("Current moves:\n{:?}", next_node.moves);
                    debug!("Current board:\n{}", next_node.board.to_string(true));

                    nb_nodes_visited += 1;
                    next_node
                        .search_neighbors(&mut self.known_nodes, &mut self.known_unvisited_nodes);
                    Rc::make_mut(&mut next_node).index = nb_nodes_visited;
                    debug!("Score: {:?}", next_node.score);
                    if next_node.score > max_score {
                        debug!("New best score: {:?}", next_node.score);
                        max_score = next_node.score;
                        best_node = next_node;
                        moves = Some(best_node.moves.clone());
                    }
                }
            }
        }

        (moves, nb_nodes_visited)
    }
}
