from crapette.core.board import Board
from crapette.core.cards import Card, new_deck


def foundation_to_fill(board: Board):
    """Set the game to check a foundation fill."""
    deck = new_deck(player=0, shuffle=False)
    for card in deck[: Card.NB_RANKS]:
        card.face_up = True

    # Diamonds Ace to Queen on Diamonds foundation pile
    board.foundation_piles[0].set_cards(deck[: Card.NB_RANKS - 1])

    # Diamonds King on a tableau pile
    board.tableau_piles[0].set_cards(deck[Card.NB_RANKS - 1 : Card.NB_RANKS])


def empty_stock(board: Board):
    """Set the game to check for empty stock and waste."""
    deck = new_deck(player=0, shuffle=False)
    for card in deck:
        card.face_up = True

    # Fill waste with Diamonds
    board.players_piles[0].waste.set_cards(deck[:13])


def empty_stock_and_waste(board: Board):
    """Set the game to check for empty stock and waste."""
    deck = new_deck(player=0, shuffle=False)
    for card in deck[: board.NB_PILES + 2]:
        card.face_up = True

    # Fill tableau with Diamonds 2 to 8
    for index, pile in enumerate(board.tableau_piles[:-1]):
        pile.set_cards(deck[index + 1 : index + 2])

    # Fill crape with Diamonds 9 and 10
    board.players_piles[0].crape.set_cards(
        deck[board.NB_PILES + 1 : board.NB_PILES - 1 : -1]
    )

    # TODO: The game should not be locked, add a button to end the turn


def brain_combination(board: Board):
    deck = new_deck(player=0, shuffle=False)
    diamonds = deck[: Card.NB_RANKS]
    clubs = deck[2 * Card.NB_RANKS : 3 * Card.NB_RANKS]

    n = 9
    for i in range(n - 1):
        card = diamonds.pop()
        card.face_up = True
        board.tableau_piles[i % 2].add_card(card)
        card = clubs.pop()
        card.face_up = True
        board.tableau_piles[1 - i % 2].add_card(card)

    board.players_piles[0].crape.add_card(diamonds[0])
