"""HELP — flagship movement-required sign for the hospital scenario.

ASL HELP: the dominant hand makes an "A" (thumb-up closed fist) and rests on the open, upward
non-dominant palm; both hands then lift **upward** together (you are "lifting someone up").

This is the hospital analog of COFFEE: its defining feature is MOTION, so movement is `required`.
A learner who simply freezes the correct two-hand pose MUST fail — the confusor test (Phase 4)
asserts the failing parameter is specifically `movement`, not handshape or location.

Five-parameter declaration:
  handshape   : dominant "A" (thumb-up fist) on non-dominant "open" (flat palm)
  location    : dominant hand on/over the non-dominant palm  (required)
  movement    : both hands translate UP together             (required)  <- the anti-bug gate
  orientation : non-dominant palm faces up                   (declared, not gated in v1)
  NMM         : none in v1
"""
from __future__ import annotations

from core.schema import HandShapeReq, LocationReq, MovementReq, OrientationReq, Sign

HELP = Sign(
    name="HELP",
    dominant=HandShapeReq(kind="A", threshold=0.55),       # thumb-up fist; minimal pair with "fist"/"S"
    nondominant=HandShapeReq(kind="open", threshold=0.55), # flat supporting palm
    location=LocationReq(anchor="nondominant_palm", max_dist_ratio=0.30, required=True),
    movement=MovementReq(
        kind="linear",
        actor="both",                 # the supported hand and the platform palm rise together
        direction=(0.0, -1.0),        # image space: up is -y
        min_displacement_ratio=0.12,  # must rise ~0.12 shoulder widths over the window
        required=True,
        threshold=0.6,
    ),
    palm_orientation=OrientationReq(facing="up", hand="nondominant", required=False),
)
