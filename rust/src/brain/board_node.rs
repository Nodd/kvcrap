use std::borrow::Borrow;
use std::cmp::Ordering;
use std::collections::{BTreeSet, HashMap, HashSet};
use std::hash::{Hash, Hasher};
use std::rc::Rc;

use crate::core::moves::CardAction;
use crate::{Board, Pile, PileType, Player, NB_SUITS};

use super::board_score::{BoardScore, WORSE_SCORE};

type Cost = (usize, Vec<[usize; 2]>);

pub struct BoardNode {
    board: Board,
    player: Player,
    // ai_config,
    cost: Cost,
    pub score: BoardScore,
    //score_min,
    moves: Vec<CardAction>,
    pub index: usize,
}

impl BoardNode {
    pub fn new(board: Board, player: Player) -> Self {
        BoardNode {
            board: board,
            player: player,
            // ai_config,
            cost: (0, Vec::<[usize; 2]>::new()),
            score: WORSE_SCORE,
            //score_min,
            moves: vec![],
            index: 0,
        }
    }

    pub fn search_neighbors(
        &mut self,
        known_nodes: &mut HashMap<Board, Rc<BoardNode>>,
        known_unvisited_nodes: &mut BTreeSet<Rc<BoardNode>>,
    ) {
        // If last move was from a player pile, stop here
        if let Some(last_move) = self.moves.last() {
            if let CardAction::Move { origin, .. } = last_move {
                if matches!(origin, PileType::Crape { .. } | PileType::Stock { .. }) {
                    return;
                }
            }
        }

        let piles_orig = self.get_piles_orig();
        let piles_dest = self.get_piles_dest();

        // Check all possible origin piles
        for pile_orig in &piles_orig {
            let card = pile_orig.top_card().unwrap();

            // Precomputation
            let is_pile_orig_one_card_tableau =
                pile_orig.nb_cards() == 1 && matches!(pile_orig.kind, PileType::Tableau { .. });

            // Check all possible destination piles
            for pile_dest in &piles_dest {
                // Check if the move is possible
                if !pile_dest.can_add_card(card, &pile_orig.kind, &self.player) {
                    continue;
                }

                // Avoid noop move
                if pile_dest.is_same(pile_orig) {
                    continue;
                }

                // Avoid equivalent moves with empty piles on the tableau
                // It's an important optimization when there are multiple empty piles on the tableau
                if (is_pile_orig_one_card_tableau
                    && pile_dest.is_empty()
                    && matches!(pile_dest.kind, PileType::Tableau { .. }))
                {
                    continue;
                }

                // Do not undo the previous move
                if let Some(CardAction::Move {
                    origin,
                    destination,
                    ..
                }) = self.moves.last()
                {
                    if destination.is_same(&pile_orig.kind) && origin.is_same(&pile_dest.kind) {
                        continue;
                    }
                }

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
            // Known board, check if a lower cost was found
            // Skip if cost is higher or equal
            if cost >= next_board_node.cost {
                return;
            }
            known_unvisited_nodes.remove(Rc::as_ref(&next_board_node));
            known_nodes.remove(&next_board);
        }

        // Unknown board or new one in replacement
        let mut next_board_node = BoardNode::new(next_board.clone(), self.player);
        next_board_node.moves = self.moves.clone();
        next_board_node.moves.push(r#move);
        next_board_node.cost = cost;

        let next_board_node_rc = Rc::new(next_board_node);
        known_nodes.insert(next_board, next_board_node_rc.clone());
        known_unvisited_nodes.insert(next_board_node_rc);
    }

    fn get_piles_orig(&self) -> Vec<&Pile> {
        let mut piles = Vec::with_capacity(8 + 2);

        // Tableau piles
        // Remove duplicate Piles
        let unique_tableau_piles = self.board.tableau.iter().collect::<HashSet<&Pile>>();
        piles.extend(unique_tableau_piles.iter().filter(|pile| !pile.is_empty()));

        // TODO : optimize by filter out the piles where cards can't go anywhere ?

        // Player piles
        if let Some(card) = self.board.crape[self.player].top_card() {
            if card.face_up {
                piles.push(&self.board.crape[self.player]);
            }
        }
        if let Some(card) = self.board.stock[self.player].top_card() {
            if card.face_up {
                piles.push(&self.board.stock[self.player]);
            }
        }
        piles
    }

    fn get_piles_dest(&self) -> Vec<&Pile> {
        let mut piles_dest = Vec::with_capacity(8 + 8 + 2);

        // Tableau piles
        // Remove duplicate Piles
        let unique_tableau_piles = self.board.tableau.iter().collect::<HashSet<&Pile>>();
        piles_dest.extend(unique_tableau_piles);

        // Foundation piles
        piles_dest.extend(
            &self.board.foundation[0..4]
                .iter()
                .filter(|pile| !pile.is_full())
                .collect::<Vec<_>>(),
        );
        for i in 0..4 {
            let pile1 = &self.board.foundation[i];
            let pile2 = &self.board.foundation[NB_SUITS - 1 - i];
            if pile2.nb_cards() != pile1.nb_cards() && !pile2.is_full() {
                piles_dest.push(pile2);
            }
        }

        // Opponent piles
        let opponent_piles = [
            &self.board.crape[self.player.other()],
            &self.board.waste[self.player.other()],
        ];
        piles_dest.extend(opponent_piles.iter().filter(|pile| !pile.is_empty()));

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
        self.board.hash(state);
    }
}
