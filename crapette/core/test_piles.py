from .piles import TableauPile
from .cards import Card


def test_tableau_equal():
    pile = TableauPile(0)
    assert pile == TableauPile(0)
    assert pile == TableauPile(1)

    pile.add_card(Card(1, "s", 0))
    pile2 = TableauPile(0)
    pile2.add_card(Card(1, "s", 0))
    assert pile == pile2


def test_tableau_not_equal():
    pile = TableauPile(0)
    pile.add_card(Card(1, "s", 0))
    pile2 = TableauPile(0)
    pile2.add_card(Card(2, "s", 0))
    assert pile != pile2

    pile2 = TableauPile(0)
    pile2.add_card(Card(2, "s", 0))
    pile2.add_card(Card(3, "s", 0))
    assert pile != pile2
