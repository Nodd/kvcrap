from .board import Board, HashBoard
from .cards import Card


def test_equal():
    board = HashBoard(Board())
    assert board == HashBoard(Board())

    board2 = HashBoard(Board())
    card = Card(1, "s", 0)
    board.tableau_piles[0].add_card(card)
    board2.tableau_piles[0].add_card(card)
    assert board == board2


def test_equal_different_order():
    board = HashBoard(Board())
    board2 = HashBoard(Board())
    card = Card(1, "s", 0)
    board.tableau_piles[0].add_card(card)
    board2.tableau_piles[1].add_card(card)
    assert board == board2


def test_not_equal():
    board = HashBoard(Board())
    board2 = HashBoard(Board())
    card1 = Card(1, "s", 0)
    card2 = Card(2, "s", 0)

    board.tableau_piles[0].add_card(card1)
    board2.tableau_piles[0].add_card(card2)

    assert board != board2


def test_hash_equal():
    board = HashBoard(Board())
    assert hash(board) == hash(HashBoard(Board()))

    board = HashBoard(Board())  # Reinitialize to avoid caching
    board2 = HashBoard(Board())
    card = Card(1, "s", 0)
    board.tableau_piles[0].add_card(card)
    board2.tableau_piles[0].add_card(card)
    assert hash(board) == hash(board2)


def test_hash_equal_different_order():
    board = HashBoard(Board())
    board2 = HashBoard(Board())
    card = Card(1, "s", 0)
    board.tableau_piles[0].add_card(card)
    board2.tableau_piles[1].add_card(card)
    assert hash(board) == hash(board2)


def test_hash_not_equal():
    board = HashBoard(Board())
    board2 = HashBoard(Board())
    card1 = Card(1, "s", 0)
    card2 = Card(2, "s", 0)

    board.tableau_piles[0].add_card(card1)
    board2.tableau_piles[0].add_card(card2)

    assert hash(board) != hash(board2)
