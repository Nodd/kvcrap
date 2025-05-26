use crate::core::{board::Board, board::NB_PILES_CENTER, players::Player};

const NB_SCORE_VALUES: usize = 12;

// TODO: use a new type ?
// cf https://doc.rust-lang.org/book/ch19-03-advanced-traits.html#using-the-newtype-pattern-to-implement-external-traits-on-external-types
pub type BoardScore = [i32; NB_SCORE_VALUES];
pub const WORSE_SCORE: BoardScore = [i32::MIN; NB_SCORE_VALUES];

pub fn board_score(board: &Board, active_player: Player) -> BoardScore {
    let mut sorted_tableau = board.tableau.clone();
    sorted_tableau.sort();
    sorted_tableau.reverse();

    [
        // More cards in foundation is the priority
        board
            .foundation
            .iter()
            .map(|pile| pile.nb_cards() as i32)
            .sum(),
        // Emptying crapette is the second priority
        -(board.crape[active_player].nb_cards() as i32),
        // Having less cards in stock is the way to win
        -(board.stock[active_player].nb_cards() as i32),
        // Having more empty tableau piles is better
        board
            .tableau
            .iter()
            .map(|pile| if pile.is_empty() { 1 } else { 0 })
            .sum(),
        // Having longer suits in tableau piles is better
        sorted_tableau[0].nb_cards() as i32,
        sorted_tableau[1].nb_cards() as i32,
        sorted_tableau[2].nb_cards() as i32,
        sorted_tableau[3].nb_cards() as i32,
        sorted_tableau[4].nb_cards() as i32,
        sorted_tableau[5].nb_cards() as i32,
        sorted_tableau[6].nb_cards() as i32,
        sorted_tableau[7].nb_cards() as i32,
    ]
}
