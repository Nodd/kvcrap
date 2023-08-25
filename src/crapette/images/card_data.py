"""Data for using card artworks.

This version uses cars provided for free (LGPL-2.1) on
https://github.com/htdebeer/SVG-cards.
"""

import types
from pathlib import Path

from kivy.core.image import Image as CoreImage

CARD_IMG = types.SimpleNamespace(
    SUIT_NAME={"c": "club", "d": "diamond", "h": "heart", "s": "spade"},
    RANK_NAME=[
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
    ],
    PATH=Path(__file__).parent / "png" / "2x",
)


def card2img(card):
    if card is None:
        img = "card-base.png"
    elif not card.face_up:
        img = "back-navy.png" if card.player == 0 else "back-red.png"
    else:
        img =f"{CARD_IMG.SUIT_NAME[card.suit]}_{CARD_IMG.RANK_NAME[card.rank]}.png"
    print(img)
    return str(CARD_IMG.PATH / img)


CARD_IMG.SIZE = CoreImage(card2img(None)).size
CARD_IMG.WIDTH, CARD_IMG.HEIGHT = CARD_IMG.SIZE
CARD_IMG.RATIO = CARD_IMG.WIDTH / CARD_IMG.HEIGHT
CARD_IMG.OFFSET_FACTOR = 0.2  # %
