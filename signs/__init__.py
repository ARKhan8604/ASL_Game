"""Shared sign definitions (pure data) — reused across all scenarios.

Import a sign directly or look it up by name in the SIGNS registry (handy for scenarios that
drive prompts by sign name). Coffee-shop signs and hospital signs all live here so both scenarios
share the same verifier without duplicating logic.
"""
from signs.coffee import COFFEE
from signs.letter_a import LETTER_A

# Hospital scenario signs (Phase 2+)
from signs.help import HELP
from signs.pain import PAIN
from signs.medicine import MEDICINE
from signs.emergency import EMERGENCY

SIGNS = {
    COFFEE.name: COFFEE,
    LETTER_A.name: LETTER_A,
    HELP.name: HELP,
    PAIN.name: PAIN,
    MEDICINE.name: MEDICINE,
    EMERGENCY.name: EMERGENCY,
}

__all__ = ["COFFEE", "LETTER_A", "HELP", "PAIN", "MEDICINE", "EMERGENCY", "SIGNS"]
