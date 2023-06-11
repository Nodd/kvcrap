from crapette.core.board import Board
from crapette.core.cards import Card, new_deck


def foundation_to_fill(board: Board):
    """Set the game to check a foundation fill."""
    # Player 0
    deck = new_deck(0, shuffle=False)
    for card in deck[: Card.NB_RANKS]:
        card.face_up = True
    print(deck)
    board.foundation_piles[0].set_cards(deck[: Card.NB_RANKS - 1])
    board.tableau_piles[0].set_cards(deck[Card.NB_RANKS - 1 : Card.NB_RANKS])
    board.players_piles[0].stock.set_cards(deck[Card.NB_RANKS :])

    # Player 1
    deck = new_deck(1)
    board.players_piles[1].stock.set_cards(deck)
