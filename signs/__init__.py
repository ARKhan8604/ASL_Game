"""Shared sign definitions (pure data) — reused across all scenarios.

Importing this package pulls in only `core.schema` (pure stdlib), so it is safe to import in
tooling and tests without MediaPipe/OpenCV present. The coffee-shop sign(s) live alongside these
but are intentionally not imported here.
"""
from signs.emergency import EMERGENCY
from signs.help import HELP
from signs.letter_a import LETTER_A
from signs.medicine import MEDICINE
from signs.pain import PAIN

# The hospital scenario's v1 vocabulary, in teaching order. LETTER_A is the static control.
HOSPITAL_SIGNS = (HELP, PAIN, MEDICINE, EMERGENCY)

# Lookup by name (e.g. "HELP") for scenario prompts and the verifier harness.
SIGNS_BY_NAME = {s.name: s for s in (*HOSPITAL_SIGNS, LETTER_A)}

__all__ = ["HELP", "PAIN", "MEDICINE", "EMERGENCY", "LETTER_A", "HOSPITAL_SIGNS", "SIGNS_BY_NAME"]
