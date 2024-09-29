use log::{debug, error, info, trace, warn};
use std::borrow::Borrow;
use std::cmp::Ordering;
use std::collections::{BTreeSet, HashMap, HashSet};
use std::hash::{Hash, Hasher};
use std::ops::{Deref, DerefMut};
use std::rc::Rc;

use crate::core::moves::{CardAction, CardActions};
use crate::core::{board::Board, piles::Pile, piles::PileType, players::Player, suits::NB_SUITS};

use super::board_score::{BoardScore, WORSE_SCORE};

type Cost = (usize, Vec<[usize; 2]>);

#[derive(Clone)]
pub struct BoardNode {
    pub board: Board,
    active_player: Player,
    // ai_config,
    cost: Cost,
    pub score: BoardScore,
    //score_min,
    pub moves: CardActions,
    pub index: usize,
}

impl BoardNode {
    pub fn new(board: Board, active_player: Player, moves: &CardActions) -> Self {
        BoardNode {
            board: board,
            active_player,
            // ai_config,
            cost: (0, Vec::<[usize; 2]>::new()),
            score: WORSE_SCORE,
            //score_min,
            moves: moves.clone(),
            index: 0,
        }
    }

    pub fn search_neighbors(
        &self,
        known_nodes: &mut HashMap<Board, Rc<BoardNode>>,
        known_unvisited_nodes: &mut BTreeSet<Rc<BoardNode>>,
    ) {
        trace!("search_neighbors: start");
        // If last move was from a player pile, stop here
        if let Some(last_move) = self.moves.last() {
            if let CardAction::Move { origin, .. } = last_move {
                if matches!(origin, PileType::Crape { .. } | PileType::Stock { .. }) {
                    trace!("Last move was from a player pile, stop here");
                    return;
                }
            }
        }

        // Get origin and destination piles
        let piles_orig = self.get_piles_orig();
        let piles_dest = self.get_piles_dest();

        // Check all possible origin piles
        trace!("Check all {} possible origin piles", piles_orig.len());
        for pile_orig in &piles_orig {
            let card = pile_orig.top_card().expect("Pile should be empty");

            // Pre computation
            let is_pile_orig_one_card_tableau =
                pile_orig.nb_cards() == 1 && matches!(pile_orig.kind, PileType::Tableau { .. });

            // Check all possible destination piles
            trace!(
                "  Check all {} possible destination piles for card {} from origin pile {}",
                piles_dest.len(),
                card,
                pile_orig.kind,
            );
            for pile_dest in &piles_dest {
                // Avoid noop move
                if pile_dest.is_same(pile_orig) {
                    trace!(
                        "    Moving to the same pile {}, skipping",
                        pile_dest.kind
                    );
                    continue;
                }

                // Check if the move is possible
                if !pile_dest.can_add_card(card, &pile_orig.kind, &self.active_player) {
                    trace!("    Move to {} is not possible, skipping", pile_dest.kind);
                    continue;
                }

                // Avoid equivalent moves with empty piles on the tableau
                // It's an important optimization when there are multiple empty piles on the tableau
                // TODO: check if checking the known boards later is really slower (comment was from the python implementation)
                if (is_pile_orig_one_card_tableau
                    && pile_dest.is_empty()
                    && matches!(pile_dest.kind, PileType::Tableau { .. }))
                {
                    trace!(
                        "    Move lone card to empty {} is a noop, skipping",
                        pile_dest.kind
                    );
                    continue;
                }

                // Do not undo the previous move
                // TODO: check if checking the known boards later is really slower
                if let Some(CardAction::Move {
                    origin,
                    destination,
                    ..
                }) = self.moves.last()
                {
                    if destination.is_same(&pile_orig.kind) && origin.is_same(&pile_dest.kind) {
                        trace!(
                            "    Move to {} would revert previous move, skipping",
                            pile_dest.kind
                        );
                        continue;
                    }
                }

                trace!(
                    "    Move {} to {} is valid, registering",
                    card,
                    pile_dest.kind
                );
                self.register_next_board(
                    CardAction::Move {
                        card: card.clone(),
                        origin: pile_orig.kind,
                        destination: pile_dest.kind,
                    },
                    known_nodes,
                    known_unvisited_nodes,
                )
            }
        }
    }

    fn register_next_board<'a>(
        &self,
        r#move: CardAction,
        known_nodes: &mut HashMap<Board, Rc<BoardNode>>,
        known_unvisited_nodes: &mut BTreeSet<Rc<BoardNode>>,
    ) {
        // Instantiate neighbor
        let next_board: Board = self.board.copy_with_action(&r#move);
        let cost = self.compute_move_cost(&r#move);

        if let Some(next_board_node) = known_nodes.get(&next_board) {
            // Known board
            trace!("      Next board already known");



            // Check if a lower cost was found
            // Skip if cost is higher or equal
            if cost >= next_board_node.cost {
                trace!("      Cost is higher or equal, skipping");
                return;
            }
            trace!("      Cost is lower, replacing");
            known_unvisited_nodes.remove(Rc::as_ref(&next_board_node));
            known_nodes.remove(&next_board);
        }
        else {
            trace!("      Next board not known");
        }

        // Unknown board or new one in replacement
        trace!("      Registering next board");
        let mut next_board_node =
            BoardNode::new(next_board.clone(), self.active_player, &self.moves);
        next_board_node.moves.push(r#move);
        next_board_node.cost = cost;

        let next_board_node_rc = Rc::new(next_board_node);
        known_nodes.insert(next_board, next_board_node_rc.clone());
        known_unvisited_nodes.insert(next_board_node_rc);
    }

    fn get_piles_orig(&self) -> Vec<&Pile> {
        trace!("get_piles_orig: start, looking for origin pile candidates");
        let mut piles = Vec::with_capacity(8 + 2);

        // Tableau piles
        // Remove duplicate Piles while keeping the order
        let mut unique_tableau_piles = HashSet::new();
        piles.extend(
            self.board
                .tableau
                .iter()
                .filter(|pile| !pile.is_empty())
                .filter(|&pile| unique_tableau_piles.insert(pile)),
        );
        trace!(
            "  {} unique non empty Tableau piles added to origin pile candidates",
            piles.len()
        );

        // TODO : optimize by filter out the piles where cards can't go anywhere ?

        // Player piles
        if let Some(card) = self.board.crape[self.active_player].top_card() {
            if card.face_up {
                piles.push(&self.board.crape[self.active_player]);
                trace!("  Player Crape is not empty and top card is face up, added to origin pile candidates");
            } else {
                trace!("  Player Crape is not empty but top card is face down, pile skipped from origin pile candidates");
            }
        } else {
            trace!("  Player Crape is empty, pile skipped from origin pile candidates")
        }
        if let Some(card) = self.board.stock[self.active_player].top_card() {
            if card.face_up {
                piles.push(&self.board.stock[self.active_player]);
                trace!("  Player Stock is not empty and top card is face up, added to origin pile candidates");
            } else {
                trace!("  Player Stock is not empty but top card is face down, pile skipped from origin pile candidates");
            }
        } else {
            trace!("  Player Stock is empty, pile skipped from origin pile candidates")
        }

        trace!(
            "get_piles_orig: end, {} origin pile candidates found",
            piles.len()
        );
        piles
    }

    fn get_piles_dest(&self) -> Vec<&Pile> {
        trace!("get_piles_dest: start, looking for destination pile candidates");
        let mut piles_dest = Vec::with_capacity(8 + 8 + 2);

        // Tableau piles
        // Remove duplicate Piles while keeping the order
        // Notably keep at most one empty pile
        let mut unique_tableau_piles = HashSet::new();
        piles_dest.extend(
            self.board
                .tableau
                .iter()
                .filter(|&pile| unique_tableau_piles.insert(pile)),
        );
        trace!(
            "  {} unique Tableau piles added to destination pile candidates",
            piles_dest.len()
        );

        // Foundation piles
        piles_dest.extend(
            &self.board.foundation[0..4]
                .iter()
                .filter(|pile| !pile.is_full())
                .collect::<Vec<_>>(),
        );
        trace!("  4 Foundation piles initially added to destination pile candidates",);
        for i in 0..4 {
            let pile1 = &self.board.foundation[i];
            let pile2 = &self.board.foundation[NB_SUITS - 1 - i];
            if pile2.nb_cards() != pile1.nb_cards() && !pile2.is_full() {
                piles_dest.push(pile2);
                trace!("  {} also added to destination pile candidates", pile2.kind);
            } else {
                trace!("  {} is either identical to {} or full, pile skipped from destination pile candidates", pile2.kind, pile1.kind);
            }
        }

        // Opponent piles
        let opponent_piles = [
            &self.board.crape[self.active_player.other()],
            &self.board.waste[self.active_player.other()],
        ];
        piles_dest.extend(opponent_piles.iter().filter(|pile| !pile.is_empty()));
        trace!("  Checked opponent piles as destination pile candidates");

        trace!(
            "get_piles_dest: end, {} destination pile candidates found",
            piles_dest.len()
        );
        piles_dest
    }

    fn compute_move_cost(&self, r#move: &CardAction) -> Cost {
        let mut move_costs = Vec::<[usize; 2]>::with_capacity(self.moves.len());

        // Cost of previous moves, excluding the number of moves
        move_costs.extend(&self.cost.1);

        // Cost of this move
        if let CardAction::Move {
            destination,
            origin,
            ..
        } = r#move
        {
            let dest_cost = match destination {
                PileType::Foundation { .. } => 0,
                PileType::Crape { .. } => 1,
                PileType::Waste { .. } => 2,
                PileType::Tableau { .. } => 3,
                PileType::Stock { .. } => panic!("Stock can never be a destination pile"),
            };
            let orig_cost = match origin {
                PileType::Tableau { .. } => 0,
                PileType::Crape { .. } => 1,
                PileType::Stock { .. } => 2,
                PileType::Waste { .. } => panic!("Waste can never be an origin pile"),
                PileType::Foundation { .. } => panic!("Foundation can never be an origin pile"),
            };
            move_costs.push([dest_cost, orig_cost]);
        } else {
            panic!("AI can only move cards")
        }

        // The lowest the number of moves, the better
        let cost: Cost = (self.moves.len(), move_costs);

        cost
    }
}

impl Hash for BoardNode {
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.board.hash(state);
    }
}

impl PartialEq for BoardNode {
    fn eq(&self, other: &Self) -> bool {
        self.board == other.board
    }
}
impl Eq for BoardNode {}

// Compare cost first, then score, the board itself
// Comparison with the board is needed so that the behavior
// is coherent with Eq
impl Ord for BoardNode {
    fn cmp(&self, other: &Self) -> Ordering {
        match self.cost.cmp(&other.cost) {
            Ordering::Equal => match self.score.cmp(&other.score) {
                Ordering::Equal => self.board.cmp(&other.board),
                ordering => ordering,
            },
            ordering => ordering,
        }
    }
}
impl PartialOrd for BoardNode {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}
