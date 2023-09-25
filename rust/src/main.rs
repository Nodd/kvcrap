mod core;

fn main() {
    let mut board = core::board::Board::new();
    board.new_game();
    println!("{}", board.to_string());
}
