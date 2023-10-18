use rand::seq::SliceRandom;

use super::cards::*;
use super::players::*;
use super::ranks::*;
use super::suits::*;

pub const NB_CARDS: usize = NB_RANKS * NB_SUITS;

pub fn new_deck(player: Player) -> Vec<Card> {
    let mut deck = Vec::new();
    for suit in Suit::into_iter() {
        for rank in MIN_RANK..=MAX_RANK {
            deck.push(Card::new(Rank::from(rank), suit, player))
        }
    }
    deck
}

pub fn shuffle(deck: &mut Vec<Card>) {
    let mut rng = rand::thread_rng();
    deck.shuffle(&mut rng);
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
        shuffle(&mut deck2);
        assert_ne!(deck1, deck2);
        assert_eq!(deck2.len(), NB_CARDS);
    }
}
