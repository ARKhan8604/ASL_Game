"""Shared sign definitions (pure data) — reused across all scenarios.

Import a sign directly (``from signs.coffee import COFFEE``) or look it up by name in the
SIGNS registry (handy for scenarios that drive prompts by sign name).
"""
from signs.coffee import COFFEE
from signs.hello import HELLO
from signs.letter_a import LETTER_A
from signs.letter_b import LETTER_B
from signs.letter_l import LETTER_L
from signs.letter_v import LETTER_V
from signs.letter_y import LETTER_Y
from signs.please import PLEASE
from signs.thank_you import THANK_YOU
from signs.want import WANT
from signs.yes import YES
from signs.you import YOU

SIGNS = {s.name: s for s in (
    COFFEE, PLEASE, THANK_YOU, HELLO, WANT, YES,
    LETTER_A, LETTER_B, LETTER_L, LETTER_V, LETTER_Y, YOU,
)}

__all__ = [
    "COFFEE", "PLEASE", "THANK_YOU", "HELLO", "WANT", "YES",
    "LETTER_A", "LETTER_B", "LETTER_L", "LETTER_V", "LETTER_Y", "YOU",
    "SIGNS",
]
