// Disable all warnings about unused code
#![allow(dead_code)]

use clap::Parser;

use crate::core::game_manager::GameManager;

mod core;

mod brain;
use brain::djikstra::compute_states;

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

    let seed = cli.seed.as_deref();
    let custom = cli.custom.as_deref();

    let game_manager = GameManager::new(seed, custom);
    println!("Seed: {}", game_manager.config.seed);
    if let Some(custom_game) = custom {
        println!("Custom game: {}", custom_game);
    }
    println!("{}", game_manager.board.to_string(true));
    println!(
        "{:?}",
        game_manager
            .config
            .active_player
            .expect("Active player should be set")
    );

    compute_states(
        &game_manager.board,
        game_manager.config.active_player.unwrap(),
        false,
        "",
    );
}
