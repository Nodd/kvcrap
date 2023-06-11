from crapette.core.board import Board
from crapette.core.cards import Card, new_deck


def foundation_to_fill(board: Board):
    """Set the game to check a foundation fill."""
    deck = new_deck(player=0, shuffle=False)
    for card in deck[: Card.NB_RANKS]:
        card.face_up = True
    board.foundation_piles[0].set_cards(deck[: Card.NB_RANKS - 1])
    board.tableau_piles[0].set_cards(deck[Card.NB_RANKS - 1 : Card.NB_RANKS])
