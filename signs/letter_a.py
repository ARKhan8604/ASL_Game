"""Fingerspelled letter A — static no-movement control.

A = closed fist with the thumb resting alongside the index finger. Handshape + (loose) location
only; `movement.kind="none"` and `movement.required=False`. This is the control that proves the
*other* half of the contract: a genuinely static sign is allowed to pass while frozen, whereas a
movement-required sign (HELP, PAIN, MEDICINE, EMERGENCY) must not.

It also doubles as a minimal-pair reference: A vs "fist"/S differ only by thumb position, and A is
exactly the dominant handshape HELP uses — so the same classifier work serves both.

Five-parameter declaration:
  handshape   : dominant "A" (thumb-alongside closed fist); no non-dominant hand
  location    : neutral signing space (not gated)
  movement    : none, NOT required  <- the static-control point
  orientation : not gated in v1
  NMM         : none in v1
"""
from __future__ import annotations

from core.schema import HandShapeReq, LocationReq, MovementReq, Sign

LETTER_A = Sign(
    name="A",
    dominant=HandShapeReq(kind="A", threshold=0.55),
    nondominant=None,
    location=LocationReq(anchor="neutral", max_dist_ratio=1.5, required=False),
    movement=MovementReq(kind="none", required=False),  # static: nothing to verify over time
)
