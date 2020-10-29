import random

from .cards import Card


def new_deck(player):
    """Build a new shuffled deck

    A deck is simply a list of cards.
    """
    assert player in [0, 1]
    cards = [Card(r, s, player) for s in Card.SUITS for r in Card.RANKS]
    random.shuffle(cards)
    random.shuffle(cards)  # Twice because it didn't seem random enough :/
    return cards
