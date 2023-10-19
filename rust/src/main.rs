// Disable all warnings about ununsed code
#![allow(dead_code)]

use clap::Parser;

mod core;

#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    /// A predefined seed for the games
    #[arg(short, long)]
    seed: Option<String>,

    /// A predefined game board, for testing purposes
    #[arg(short, long)]
    custom: Option<String>,
}

fn main() {
    let cli = Args::parse();

    let seed = match cli.seed.as_deref() {
        Some(seed) => seed.to_string(),
        None => core::decks::generate_seed(),
    };
    println!("{}", seed);

    let mut board = core::board::Board::new();
    board.new_game(&seed);
    println!("{}", board.to_string());
    println!("{:?}", board.compute_first_player());
}
