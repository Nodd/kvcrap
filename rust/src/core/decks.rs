use rand::distributions::Alphanumeric;
use rand::seq::SliceRandom; // Needed for Vec<>.shuffle()
use rand::Rng; // Needed for sample_iter()
use rand_pcg::Pcg64;
use rand_seeder::Seeder;

use super::cards::Card;
use super::players::Player;
use super::ranks::{Rank, MAX_RANK, MIN_RANK, NB_RANKS};
use super::suits::{Suit, NB_SUITS};

pub const NB_CARDS: usize = NB_RANKS * NB_SUITS;

/// Creates a fresh, sorted, deck of Cards.
///
/// Use shuffle() to shuffle the deck.
pub fn new_deck(player: Player) -> Vec<Card> {
    let mut deck = Vec::new();
    for suit in Suit::into_iter() {
        for rank in MIN_RANK..=MAX_RANK {
            deck.push(Card::new(Rank::from(rank), suit, player))
        }
    }
    deck
}

/// Shuffle a deck of cards with a given random generator.
///
/// The generator is typically created with `new_rng()`.
pub fn shuffle(deck: &mut Vec<Card>, rng: &mut Pcg64) {
    deck.shuffle(rng);
}

/// Create a random generator from a given String seed.
pub fn new_rng(seed: String) -> Pcg64 {
    Seeder::from(seed).make_rng()
}

/// Generate a random String to be used as a seed in `new_rng()`.
pub fn generate_seed() -> String {
    // There is 2^(2*52) card distributions
    // There is 26+26+10 characters in Alphanumeric (a-zA-Z0-9)
    // The string needs to be at least log(2^(2*52))/log(26+26+10) = 17.5
    // characters long to cover all possibilities

    rand::thread_rng()
        .sample_iter(&Alphanumeric)
        .take(20)
        .map(char::from)
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_nb_cards() {
        assert_eq!(NB_CARDS, 52);
    }

    #[test]
    fn test_new_deck() {
        let deck = new_deck(Player::Player0);
        assert_eq!(deck[0], Card::quick("1d0"));
        assert_eq!(deck.len(), NB_CARDS);
    }
    #[test]
    fn test_new_shuffled_deck() {
        let deck1 = new_deck(Player::Player0);
        let mut deck2 = new_deck(Player::Player0);
        let mut rng = new_rng("test".to_string());
        shuffle(&mut deck2, &mut rng);
        assert_ne!(deck1, deck2);
        assert_eq!(deck2.len(), NB_CARDS);
    }
}
