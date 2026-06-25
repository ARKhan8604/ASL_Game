"""Fingerspelled letter A — static control (no movement).

A = a closed fist with the thumb resting alongside the index finger (thumb up the side, not
across the front). One hand, held in neutral signing space, no motion. It is the no-movement
control that proves static signs still work, and a minimal-pair example: A vs S vs a plain fist
are all "closed fist" shapes distinguished only by thumb position — exactly the kind of subtle
distinction the handshape scorer (Phase 3) must handle.

Parameters declared:
  - handshape (dominant): A             [required]
  - location: neutral signing space     [required]
  - movement: NONE                      [not required]
"""
from core.schema import (
    DOMINANT,
    Anchor,
    HandShapeReq,
    LocationReq,
    MovementKind,
    MovementReq,
    Sign,
)

LETTER_A = Sign(
    name="LETTER_A",
    two_handed=False,
    dominant=HandShapeReq(kind="A", required=True),
    nondominant=None,
    location=LocationReq(
        anchor=Anchor.NEUTRAL_SPACE,
        acting_hand=DOMINANT,
        max_dist_ratio=1.5,      # generous: anywhere in the signing space in front of the torso
        required=True,
    ),
    movement=MovementReq(kind=MovementKind.NONE, required=False),
)
