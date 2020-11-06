from .board import Board
from .cards import Card


def test_equal():
    board = Board(new_game=False)
    assert board == Board(new_game=False)

    board2 = Board(new_game=False)
    card = Card(1, "s", 0)
    board.tableau_piles[0].add_card(card)
    board2.tableau_piles[0].add_card(card)
    assert board == board2


def test_not_equal():
    board = Board(new_game=False)
    board2 = Board(new_game=False)
    board3 = Board(new_game=False)
    card1 = Card(1, "s", 0)
    card2 = Card(2, "s", 0)

    board.tableau_piles[0].add_card(card1)
    board2.tableau_piles[0].add_card(card2)
    board3.tableau_piles[1].add_card(card1)

    assert board != board2
    assert board != board3


def test_hash_equal():
    board = Board(new_game=False)
    assert hash(board) == hash(Board(new_game=False))

    board2 = Board(new_game=False)
    card = Card(1, "s", 0)
    board.tableau_piles[0].add_card(card)
    board2.tableau_piles[0].add_card(card)
    assert hash(board) == hash(board2)


def test_hash_not_equal():
    board = Board(new_game=False)
    board2 = Board(new_game=False)
    board3 = Board(new_game=False)
    card1 = Card(1, "s", 0)
    card2 = Card(2, "s", 0)

    board.tableau_piles[0].add_card(card1)
    board2.tableau_piles[0].add_card(card2)
    assert hash(board) != hash(board2)

    board.tableau_piles[0].add_card(card1)
    board3.tableau_piles[1].add_card(card1)
    assert hash(board) != hash(board3)
