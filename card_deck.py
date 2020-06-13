SUIT_NAME = {"c": "club", "d": "diamond", "h": "heart", "s": "spade"}
RANK_NAME = [
    None,
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "jack",
    "queen",
    "king",
]


def card2img(card):
    if card is None:
        return "images/png/2x/card-base.png"
    elif not card.face_up:
        if card.player == 0:
            return "images/png/2x/back-navy.png"
        else:
            return "images/png/2x/back-red.png"
    else:
        return f"images/png/2x/{SUIT_NAME[card.suit]}_{RANK_NAME[card.rank]}.png"
