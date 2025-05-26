use log::{debug, error, info, trace, warn};
use std::collections::{BTreeSet, BinaryHeap, HashMap};
use std::io::stdin;
use std::time::Instant;

use crate::core::board::Board;
use crate::core::moves::{self, CardAction, CardActions};
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

pub fn compute_states(
    board: &Board,
    active_player: Player,
    crapette_mode: bool,
    log_path: &str,
) -> CardActions {
    let start_time = Instant::now();

    let (moves, nb_nodes_visited) = brain_djikstra(board, active_player);

    let duration = start_time.elapsed();
    println!("nb_nodes_visited: {}", nb_nodes_visited);
    println!("duration: {:#?}", duration);
    println!(
        "duration per node: {:#?}/node",
        duration / nb_nodes_visited as u32
    );
    moves
}

pub fn brain_djikstra(board: &Board, active_player: Player) -> (CardActions, usize) {
    trace!("BrainDijkstra.search");

    // Create tables
    let mut known_nodes = HashMap::<Vec<u8>, BoardNode>::new();
    let mut known_unvisited_nodes = BTreeSet::<Vec<u8>>::new();

    // Fill tables with first node
    let first_node = BoardNode::new(board.clone(), active_player, &CardActions::new());
    let encoding = board.encode();
    known_unvisited_nodes.insert(encoding.clone());
    known_nodes.insert(encoding, first_node.clone());

    // Initialize the loop
    let mut max_score = WORSE_SCORE;
    let mut nb_nodes_visited = 0;
    let mut best_node = first_node.clone();

    // Look for the best attainable node
    loop {
        debug!("{} nodes to visit", known_unvisited_nodes.len());
        match known_unvisited_nodes.pop_first() {
            None => {
                break;
            }
            Some(next_node_encoding) => {
                nb_nodes_visited += 1;

                // Get node to process
                let next_node = known_nodes[&next_node_encoding].clone();
                debug!("Current moves:\n{:?}", next_node.moves);
                debug!("Current board:\n{}", next_node.board.to_string(true));

                // Update node tables
                next_node.search_neighbors(&mut known_nodes, &mut known_unvisited_nodes);

                let mut next_node_mut = known_nodes
                    .get_mut(&next_node_encoding)
                    .expect("BoardNode disappeard from known_nodes!");
                next_node_mut.index = nb_nodes_visited;
                debug!("Score: {:?}", next_node_mut.score);
                if next_node_mut.score > max_score {
                    debug!("New best score: {:?}", next_node_mut.score);
                    max_score = next_node_mut.score;
                    best_node = next_node;
                }
            }
        }
    }

    let moves = finalize_moves(best_node.moves, &best_node.board, active_player);

    info!("{:?}", moves);
    info!("Initial board:\n{}", board.to_string(true));
    info!("Final board:\n{}", best_node.board.to_string(true));

    (moves, nb_nodes_visited)
}

// moves can be empty if the stock is empty and not the crape
// In this case the turn should end without any move.
fn finalize_moves(mut moves: CardActions, board: &Board, active_player: Player) -> CardActions {
    trace!("Finalize moves");
    let crape = &board.crape[active_player];
    let stock = &board.stock[active_player];
    let waste = &board.waste[active_player];

    if let Some(card) = board.crape[active_player].top_card() {
        if (!card.face_up) {
            moves.push(CardAction::Flip { pile: crape.kind });
            return moves;
        }
    }

    if let Some(card) = stock.top_card() {
        if !card.face_up {
            moves.push(CardAction::Flip { pile: stock.kind });
        } else {
            moves.push(CardAction::Move {
                card: card.clone(),
                origin: stock.kind,
                destination: board.waste[active_player].kind,
            });
        }
    } else if !waste.is_empty() {
        moves.push(CardAction::FlipWaste {});
    }
    // else: no cards left, win, nothing to do
    moves
}
