"""EMERGENCY — one-handed rapid repeated shake.

ASL EMERGENCY: an "E" handshape (approximated as a "claw" in v1) is held up and **shaken rapidly**
side to side. The defining features are repetition AND speed — a slow wave is not EMERGENCY, and a
motionless raised hand certainly is not.

Movement is `required` with kind="repeated" plus a speed gate (`min_speed_ratio`), so EMERGENCY
fails both when the hand is still and when it merely drifts slowly. One-handed, which distinguishes
it from the two-handed MEDICINE even though both use a "repeated" motion and a "claw" handshape.

Five-parameter declaration:
  handshape   : dominant "claw" (E-hand, approx.); no non-dominant hand
  location    : raised neutral space (not gated — the shake is the identity, not the height)
  movement    : RAPID repeated side-to-side shake                     (required)
  orientation : not gated in v1
  NMM         : (urgent facial expression in real ASL) — placeholder in v1
"""
from __future__ import annotations

from core.schema import HandShapeReq, LocationReq, MovementReq, Sign

EMERGENCY = Sign(
    name="EMERGENCY",
    dominant=HandShapeReq(kind="claw", threshold=0.5),    # "E" hand, coarse bucket
    nondominant=None,                                     # one-handed
    location=LocationReq(anchor="neutral", max_dist_ratio=1.5, required=False),
    movement=MovementReq(
        kind="repeated",
        actor="dominant",
        min_cycles=3,            # several shakes, not one wave
        min_speed_ratio=1.8,     # "rapid": mean hand speed in shoulder widths/sec
        required=True,
        threshold=0.6,
    ),
)
