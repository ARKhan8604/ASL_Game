"""HELP — flagship movement-required sign for the hospital scenario.

ASL HELP: the dominant hand makes an "A" (thumb-up closed fist) resting on the open, upward
non-dominant palm; both hands then lift upward together ("lifting someone up").

This is the hospital analog of COFFEE — its defining feature is MOTION, so movement is required.
A learner who freezes the correct two-hand pose MUST fail on movement specifically (the confusor
test in Phase 4 asserts this).

Parameters declared:
  handshape_dominant   : A-hand (thumb-up fist)           [required]
  handshape_nondominant: open/flat palm                   [required]
  location             : dominant hand on/near nondominant [required]
  movement             : dominant rises upward (linear -y) [required]  <- anti-bug gate
  orientation          : nondominant palm faces up         [not gated in v1]
"""
from core.schema import (
    DOMINANT,
    NONDOMINANT,
    Anchor,
    HandShapeReq,
    LocationReq,
    MovementKind,
    MovementReq,
    OrientationReq,
    PalmFacing,
    Sign,
)

HELP = Sign(
    name="HELP",
    two_handed=True,
    dominant=HandShapeReq(kind="a", required=True, min_confidence=0.55),
    nondominant=HandShapeReq(kind="open", required=True, min_confidence=0.55),
    location=LocationReq(
        anchor=Anchor.OTHER_HAND,
        acting_hand=DOMINANT,
        max_dist_ratio=0.45,
        min_dist_ratio=0.0,
        vertical=None,
        required=True,
    ),
    movement=MovementReq(
        kind=MovementKind.LINEAR,
        actor=DOMINANT,
        direction=(0.0, -1.0),           # image-space up (y decreases upward)
        min_displacement_ratio=0.12,
        min_duration_s=0.5,
        required=True,
    ),
    orientation=OrientationReq(hand=NONDOMINANT, facing=PalmFacing.UP, required=False),
)
