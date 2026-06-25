"""Sign Definition Schema — every sign declared as data.

This is the heart of the anti-bug design. Each ASL sign is a `Sign` dataclass that declares its
five linguistic parameters across typed fields:

  - handshape   (dominant, and optional non-dominant)   -> HandShapeReq
  - location    (spatial relation, normalized to shoulder width) -> LocationReq
  - movement    (none / linear / circular / repeated / converge) -> MovementReq
  - orientation (palm facing) -> OrientationReq  (placeholder in v1; only gated if required)
  - non-manual markers (NMM)  -> placeholder in v1

Every requirement carries two things the verifier (Phase 3) relies on:

  * `required: bool`  — whether this parameter must individually pass for the sign to pass.
  * `threshold: float` in [0,1] — the confidence cutoff this parameter must clear.

The overall pass rule is enforced in `core/verifier.py`: a sign passes **iff every parameter
marked required individually clears its threshold** — there is no averaging. The single most
important contract lives here in `MovementReq.__post_init__`: a *required* movement can never be
`kind="none"`. That makes the original COFFEE-class bug — approving a movement sign from a frozen
pose — structurally impossible to declare, let alone verify.

Distances are always expressed as **ratios of shoulder width** (see core/landmarks.py), never raw
pixels, so thresholds hold regardless of how close the signer sits to the camera.

Roles vs. physical hands: signs declare "dominant" / "nondominant" *roles*. Mapping a role to an
actual detected Left/Right hand happens at verify time (Phase 3), not here.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

# The four parameters the verifier scores and gates on. (NMM is a v1 placeholder, not yet scored.)
PARAMETERS: tuple[str, ...] = ("handshape", "location", "movement", "orientation")

# Movement vocabulary. Adding a kind here is a deliberate act: the verifier must implement a
# detector for it (core/movement.py) before any sign may declare it as required.
MovementKind = Literal["none", "linear", "circular", "repeated", "converge"]


@dataclass
class HandShapeReq:
    """A required handshape for one hand.

    `kind` is a coarse geometric bucket the Phase 3 classifier can decide from landmarks alone:
      "fist"  — closed fist, thumb wrapped across (a.k.a. S).
      "A"     — closed fist, thumb alongside/up the index (minimal pair with "fist").
      "index" — index finger extended, the rest curled (a.k.a. "1"/"D").
      "open"  — fingers extended/spread (flat hand or "5").
      "claw"  — fingers curled but not closed (used to approximate E / the medicine hand in v1).
    """

    kind: str
    required: bool = True
    threshold: float = 0.6


@dataclass
class LocationReq:
    """Where the acting hand must be, relative to a body/hand anchor.

    `anchor` is a semantic location resolved to landmarks by the verifier, e.g.:
      "nondominant_palm" — on/over the non-dominant hand (HELP, MEDICINE).
      "neutral"          — neutral signing space in front of the torso (PAIN, EMERGENCY).
    `max_dist_ratio` is the largest allowed distance from that anchor, in shoulder widths.
    """

    anchor: str
    max_dist_ratio: float = 0.6
    required: bool = True
    threshold: float = 0.6


@dataclass
class MovementReq:
    """The motion the sign requires over the rolling window (~1.5–2s).

    Only the fields relevant to `kind` are read by the matching detector; the rest stay at their
    defaults. This is the parameter that the old single-frame checker ignored — here it is a
    first-class, typed, *gateable* requirement.
    """

    kind: MovementKind = "none"
    actor: str = "dominant"               # which hand(s) move: "dominant" | "nondominant" | "both"
    reference: Optional[str] = None       # pivot/anchor for circular & repeated, e.g. "nondominant_center"

    # --- linear ---
    direction: Optional[tuple[float, float]] = None  # image-space unit vector; up = (0, -1)
    min_displacement_ratio: float = 0.0              # net displacement along `direction`, shoulder widths

    # --- circular ---
    min_total_rotation_deg: float = 300.0            # summed unwrapped rotation about `reference`
    radius_tolerance_ratio: float = 0.4              # reject wandering: radius must stay within this band

    # --- repeated ---
    min_cycles: int = 0                              # number of back-and-forth oscillations
    min_speed_ratio: float = 0.0                     # mean hand speed gate (shoulder widths/sec) for "rapid"

    # --- converge ---
    min_approach_ratio: float = 0.0                  # how much inter-hand distance must shrink, shoulder widths

    required: bool = True
    threshold: float = 0.6

    def __post_init__(self) -> None:
        # THE non-negotiable contract: you cannot require movement that is "none".
        if self.required and self.kind == "none":
            raise ValueError(
                "MovementReq: a required movement cannot have kind='none'. A movement-defined "
                "sign must declare a real motion (linear/circular/repeated/converge), or set "
                "required=False for a genuinely static sign."
            )
        # Catch authoring mistakes early: a required linear move needs a direction to test against.
        if self.required and self.kind == "linear" and self.direction is None:
            raise ValueError("MovementReq(kind='linear', required=True) needs a `direction`.")


@dataclass
class OrientationReq:
    """Palm-facing requirement. Declared in v1 but only gated when `required=True`."""

    facing: str                            # "up" | "down" | "in" | "out" | "left" | "right"
    hand: str = "dominant"                 # "dominant" | "nondominant"
    required: bool = False
    threshold: float = 0.6


@dataclass
class Sign:
    """A complete sign definition: pure data, no detection logic.

    `dominant` + optional `nondominant` give the handshape; `movement`, `location`, and optional
    `palm_orientation` give the rest. `nmm` is a v1 placeholder. The verifier reads exactly these
    fields — there is no sign-specific code path anywhere.
    """

    name: str
    dominant: HandShapeReq
    movement: MovementReq
    location: LocationReq
    nondominant: Optional[HandShapeReq] = None
    palm_orientation: Optional[OrientationReq] = None
    nmm: None = None                       # placeholder for v1; declared so the field exists

    @property
    def two_handed(self) -> bool:
        return self.nondominant is not None

    def required_parameters(self) -> tuple[str, ...]:
        """Which of PARAMETERS must individually pass for this sign — the gating set.

        `handshape` is gated if either hand's shape is required. The others follow their own flag.
        This is what the verifier iterates over; nothing outside this set can fail the sign.
        """
        req: list[str] = []
        handshape_required = self.dominant.required or (
            self.nondominant is not None and self.nondominant.required
        )
        if handshape_required:
            req.append("handshape")
        if self.location.required:
            req.append("location")
        if self.movement.required:
            req.append("movement")
        if self.palm_orientation is not None and self.palm_orientation.required:
            req.append("orientation")
        return tuple(req)
