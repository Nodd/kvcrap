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
    let mut card: Card;
    // Diamond Ace to Queen on Diamonds foundation pile
    for rank in MIN_RANK..=MAX_RANK - 1 {
        card = Card::new_up(Rank::from(rank), Suit::Diamond, Player::Player0);
        board.foundation[0].add(card);
    }

    // Diamond King on a tableau pile
    card = Card::new_up(Rank::from(MAX_RANK), Suit::Diamond, Player::Player0);
    board.tableau[0].add(card)
}

fn trivial_move(board: &mut Board) {
    let mut card: Card;
    card = Card::quick("5d0");
    board.tableau[0].add(card);
    card = Card::quick("6c0");
    board.tableau[1].add(card);
}

fn multiple_moves(board: &mut Board) {
    trivial_move(board);

    let mut card: Card;

    card = Card::quick("5h0");
    board.tableau[2].add(card);
    card = Card::quick("6s0");
    board.tableau[3].add(card);
}

fn massive_moves(board: &mut Board) {
    board.quick(
        r#"
        T0: 13s
        T1: 12h 11s 10h 9s 8h 7s 6h 5s 4h 3s 2h
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
