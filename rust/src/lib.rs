mod core;
use core::board::*;
use core::cards::*;
use core::piles::*;
use core::players::*;
use core::ranks::*;
use core::suits::*;

use pyo3::prelude::*;

pub struct GameConfig<'a> {
    pub active_player: usize,
    pub crapette_mode: bool,
    pub log_path: &'a str,
}

#[derive(FromPyObject, Debug)]
struct RustyCard {
    rank: u8,
    suit: char,
    player: u8,
    _face_up: bool,
}
#[derive(FromPyObject, Debug)]
struct RustyPile {
    // name: String,
    _cards: Vec<RustyCard>,
}

#[derive(FromPyObject, Debug)]
struct RustyBoard {
    players_piles: Vec<Vec<RustyPile>>, //Vec<Vec<Vec<RustyCard>>>,
    foundation_piles: Vec<RustyPile>,   //Vec<Vec<RustyCard>>,
    tableau_piles: Vec<RustyPile>,      //Vec<Vec<RustyCard>>,
}

fn fill_pile(pile: &mut Pile, py_pile: &RustyPile) {
    for py_card in py_pile._cards.iter() {
        let mut card = Card::new(
            Rank::from(py_card.rank),
            Suit::from(py_card.suit),
            Player::from(py_card.player),
        );
        card.face_up = py_card._face_up;
        pile.add(card)
    }
}

fn parse_python_board(py_board: &PyAny) -> Board {
    let mut board = Board::new();

    let rusty_board: RustyBoard = py_board.extract().expect("Invalid Board from Python");

    // TODO : vérifier que les 2 itérateurs font bien la même taille
    for player in PLAYERS {
        fill_pile(
            &mut board.stock[player as usize],
            &rusty_board.players_piles[player as usize][0],
        );
        fill_pile(
            &mut board.waste[player as usize],
            &rusty_board.players_piles[player as usize][1],
        );
        fill_pile(
            &mut board.crape[player as usize],
            &rusty_board.players_piles[player as usize][2],
        );
    }
    let it = board
        .foundation_piles
        .iter_mut()
        .zip(rusty_board.foundation_piles.iter());
    for (pile, py_pile) in it {
        fill_pile(pile, py_pile)
    }
    let it = board
        .tableau_piles
        .iter_mut()
        .zip(rusty_board.tableau_piles.iter());
    for (pile, py_pile) in it {
        fill_pile(pile, py_pile)
    }

    return board;
}

/// Compute the best series of moves given a game state
#[pyfunction]
fn compute(
    board: &PyAny,
    active_player: usize,
    crapette_mode: bool,
    log_path: &str,
) -> PyResult<String> {
    let game_config = GameConfig {
        active_player: active_player,
        crapette_mode: crapette_mode,
        log_path: log_path,
    };

    let board = parse_python_board(board);
    println!("{}", board.to_string());
    Ok("toto".to_string())
}

/// A Python module implemented in Rust.
#[pymodule]
fn rust_brain(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(compute, m)?)?;
    Ok(())
}
