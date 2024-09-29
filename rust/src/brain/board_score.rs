use crate::core::{board::Board, players::Player};

// TODO: use a new type ?
// cf https://doc.rust-lang.org/book/ch19-03-advanced-traits.html#using-the-newtype-pattern-to-implement-external-traits-on-external-types
pub type BoardScore = [i32; NB_SCORE_VALUES];

const NB_SCORE_VALUES: usize = 12;
pub const WORSE_SCORE: BoardScore = [i32::MAX; NB_SCORE_VALUES];

pub fn board_score(board: Board, player: Player) -> BoardScore {
    let mut score: BoardScore = [
        board
            .foundation
            .iter()
            .map(|pile| pile.nb_cards() as i32)
            .sum(),
        -(board.crape[player].nb_cards() as i32),
        -(board.stock[player].nb_cards() as i32),
        board
            .tableau
            .iter()
            .map(|pile| if pile.is_empty() { 1 } else { 0 })
            .sum(),
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
    ];
    let mut sorted_tableau = board.tableau.clone();
    sorted_tableau.sort();
    sorted_tableau.reverse();
    for i in 0..=8 {
        score[i + 4] = sorted_tableau[i].nb_cards() as i32;
    }
    score
}
