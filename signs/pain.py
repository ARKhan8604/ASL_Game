"""PAIN (HURT) — two-handed converging movement.

ASL PAIN: two "1"/index hands, fingertips pointing toward each other, are brought together (often
with a small twist) near the body part that hurts. The recognizable, verifiable feature for a
rule-based v1 is the **convergence**: the two index hands start apart and the gap between them
shrinks over the rolling window.

Movement is `required` with kind="converge", so holding two index fingers motionless apart fails
on movement — the same anti-bug guarantee as HELP, expressed with a different motion type.

Five-parameter declaration:
  handshape   : both hands "index" (index extended, rest curled)
  location    : neutral signing space (not gated — PAIN is signed at the painful area, which varies)
  movement    : the two hands CONVERGE (inter-hand distance shrinks)  (required)
  orientation : not gated in v1
  NMM         : (real PAIN often carries a pained facial expression) — placeholder in v1
"""
from __future__ import annotations

from core.schema import HandShapeReq, LocationReq, MovementReq, Sign

PAIN = Sign(
    name="PAIN",
    dominant=HandShapeReq(kind="index", threshold=0.55),
    nondominant=HandShapeReq(kind="index", threshold=0.55),
    location=LocationReq(anchor="neutral", max_dist_ratio=1.5, required=False),
    movement=MovementReq(
        kind="converge",
        actor="both",
        min_approach_ratio=0.15,   # the gap must close by ~0.15 shoulder widths over the window
        required=True,
        threshold=0.6,
    ),
)
