use super::board::Board;
use super::cards::Card;
use super::players::Player;
use super::ranks::{Rank, MAX_RANK, MIN_RANK};
use super::suits::Suit;

pub fn call_custom(name: &str, board: &mut Board) {
    match name {
        "foundation_to_fill" => foundation_to_fill(board),
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
