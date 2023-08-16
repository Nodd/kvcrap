from crapette.core.cards import Card


def test_equal():
    card = Card(1, "s", 0)
    assert card == Card(1, "s", 0)


def test_not_equal():
    card = Card(1, "s", 0)
    assert card != Card(2, "s", 0)
    assert card != Card(1, "h", 0)
    assert card != Card(1, "s", 1)


def test_hash_equal():
    card_hash = hash(Card(1, "s", 0))
    assert card_hash == hash(Card(1, "s", 0))


def test_hash_not_equal():
    card_hash = hash(Card(1, "s", 0))
    assert card_hash != hash(Card(2, "s", 0))
    assert card_hash != hash(Card(1, "h", 0))
    assert card_hash != hash(Card(1, "s", 1))
