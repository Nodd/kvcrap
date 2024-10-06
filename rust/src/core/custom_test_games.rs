use super::board::Board;
use super::cards::Card;
use super::players::Player;
use super::ranks::{Rank, MAX_RANK, MIN_RANK};
use super::suits::Suit;

pub fn call_custom(name: &str, board: &mut Board) {
    match name {
        "foundation_to_fill" => foundation_to_fill(board),
        "trivial_move" => trivial_move(board),
        "multiple_moves" => multiple_moves(board),
        "massive_moves" => massive_moves(board),
        _ => panic!("ERROR: Custom game '{name}' unknown"),
    }
}

fn foundation_to_fill(board: &mut Board) {
    board.quick(
        r#"
        F0: Ad 2d 3d 4d 5d 6d 7d 8d 9d 10d Jd Qd
        T0: Kd
    "#,
    )
}

fn trivial_move(board: &mut Board) {
    board.quick(
        r#"
        T0: 5d
        T1: 6c
    "#,
    )
}

fn multiple_moves(board: &mut Board) {
    board.quick(
        r#"
        T0: 5d
        T1: 6c
        T2: 5h
        T3: 6s
    "#,
    )
}

fn massive_moves(board: &mut Board) {
    board.quick(
        r#"
        T0: Ks
        T1: Qh Js 0h 9s 8h 7s 6h 5s 4h 3s 2h As
        T2: 5c 4d 3c 2d
    "#,
        // T2: 13c
        // T3: 12d 11c 10d 9c 8d 7c 6d 5c 4d 3c 2d
    )
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_foundation_to_fill() {
        // Direct call
        let mut board = Board::new();
        foundation_to_fill(&mut board);

        // Dispatched call
        board = Board::new();
        call_custom("foundation_to_fill", &mut board);
    }
}
