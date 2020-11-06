from .piles import _Pile
from .cards import Card


def test_equal():
    pile = _Pile("test")
    assert pile == _Pile("test")

    pile.add_card(Card(1, "s", 0))
    pile2 = _Pile("test")
    pile2.add_card(Card(1, "s", 0))
    assert pile == pile2


def test_not_equal():
    pile = _Pile("test")
    assert pile != _Pile("test2")

    pile.add_card(Card(1, "s", 0))
    pile2 = _Pile("test")
    pile2.add_card(Card(2, "s", 0))
    assert pile != pile2

    pile2 = _Pile("test")
    pile2.add_card(Card(2, "s", 0))
    pile2.add_card(Card(3, "s", 0))
    assert pile != pile2
