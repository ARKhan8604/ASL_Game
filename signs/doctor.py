"""DOCTOR sign definition.

ASL DOCTOR: the dominant hand (a flat "D" / bent-finger hand) taps the fingertips on the inside
of the opposite wrist (the pulse point), twice.

v1 approximation (documented, like HELP=fist): the precise "D" handshape isn't reliably
detectable, so the dominant hand is gated as a flat/open hand; the non-dominant hand stands in for
the wrist/forearm and is only required to be PRESENT (its handshape isn't gated). DOCTOR is a
minimal pair with NURSE — same location and motion, distinguished only by handshape (flat vs the
two-finger "N"). That's exactly where rule-based detection is fragile; flagged for the future
learned classifier.

Parameters:
  handshape (dominant): open / flat          [required]
  handshape (non-dom):  the wrist/arm        [present but NOT gated]
  location: near the non-dominant hand/wrist [required]
  movement: repeated taps toward the wrist   [required]
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

DOCTOR = Sign(
    name="DOCTOR",
    two_handed=True,
    dominant=HandShapeReq(kind="open", required=True, min_confidence=0.55),
    nondominant=HandShapeReq(kind="open", required=False),   # the wrist/arm — present, not gated
    location=LocationReq(
        anchor=Anchor.OTHER_HAND,
        acting_hand=DOMINANT,
        max_dist_ratio=0.4,         # the tapping hand stays close to the non-dominant wrist
        below="mouth",              # ...and in the torso, not up at the face
        required=True,
    ),
    movement=MovementReq(
        kind=MovementKind.REPEATED,
        actor=DOMINANT,
        min_cycles=2,                # two taps
        min_duration_s=0.5,
        required=True,
    ),
)
