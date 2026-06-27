"""Shared sign definitions (pure data) — reused across all scenarios.

Import a sign directly (``from signs.coffee import COFFEE``) or look it up by name in the
SIGNS registry (handy for scenarios that drive prompts by sign name).
"""
from signs.coffee import COFFEE
from signs.letter_a import LETTER_A
from signs.please import PLEASE

SIGNS = {
    COFFEE.name: COFFEE,
    LETTER_A.name: LETTER_A,
    PLEASE.name: PLEASE,
}

__all__ = ["COFFEE", "LETTER_A", "PLEASE", "SIGNS"]
