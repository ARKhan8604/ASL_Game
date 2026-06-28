"""Shared sign definitions (pure data) — reused across all scenarios.

Import a sign directly or look it up by name in the SIGNS registry (handy for scenarios that
drive prompts by sign name). Coffee-shop signs and hospital signs all live here so both scenarios
share the same verifier without duplicating logic.
"""
from signs.coffee import COFFEE
from signs.letter_a import LETTER_A
from signs.please import PLEASE
from signs.thank_you import THANK_YOU

# Hospital scenario signs
from signs.help import HELP
from signs.pain import PAIN
from signs.medicine import MEDICINE
from signs.emergency import EMERGENCY
from signs.doctor import DOCTOR
from signs.nurse import NURSE
from signs.sick import SICK
from signs.fever import FEVER
from signs.water import WATER
from signs.breathe import BREATHE
from signs.hospital import HOSPITAL
from signs.dizzy import DIZZY

# Hospital vocabulary, in a teaching-ish order (used by the scenario's patient queue).
HOSPITAL_SIGNS = (
    HELP, PAIN, MEDICINE, EMERGENCY,
    DOCTOR, NURSE, SICK, FEVER, WATER, BREATHE, HOSPITAL, DIZZY,
)

SIGNS = {
    COFFEE.name: COFFEE,
    LETTER_A.name: LETTER_A,
    PLEASE.name: PLEASE,
    THANK_YOU.name: THANK_YOU,
    **{s.name: s for s in HOSPITAL_SIGNS},
}

__all__ = [
    "COFFEE", "LETTER_A", "PLEASE", "THANK_YOU",
    "HELP", "PAIN", "MEDICINE", "EMERGENCY",
    "DOCTOR", "NURSE", "SICK", "FEVER", "WATER", "BREATHE", "HOSPITAL", "DIZZY",
    "HOSPITAL_SIGNS", "SIGNS",
]
