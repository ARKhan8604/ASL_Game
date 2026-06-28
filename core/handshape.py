"""Geometric handshape predicates over a single hand's 21 landmarks.

Pure 2D geometry, orientation-tolerant where possible. Each predicate returns a confidence in
[0, 1]. The verifier smooths these across recent frames (median) so one noisy frame can't flip a
result.

Shapes supported:
  fist / s — four fingers curled, thumb unconstrained (S-hand / plain fist)
  a         — four fingers curled AND thumb extended alongside (letter A)
  index     — index extended, other three curled (pointing / "1" hand)
  open      — all four fingers extended (flat palm / B-hand)
  claw      — fingers clearly curled but not fully closed (E-hand / bent-5)

Minimal-pair note: A vs S vs plain fist are all "four fingers curled"; they differ only by thumb
position. index vs open differ by how many fingers are extended.
"""
from __future__ import annotations

import numpy as np

from core.landmarks import (
    Hand,
    WRIST,
    THUMB_TIP,
    INDEX_MCP,
    INDEX_TIP,
    MIDDLE_MCP,
    MIDDLE_TIP,
    RING_MCP,
    RING_TIP,
    PINKY_MCP,
    PINKY_TIP,
)

_FINGERS = (
    (INDEX_TIP, INDEX_MCP),
    (MIDDLE_TIP, MIDDLE_MCP),
    (RING_TIP, RING_MCP),
    (PINKY_TIP, PINKY_MCP),
)


def _xy(hand: Hand, idx: int) -> np.ndarray:
    return hand.points[idx, :2]


def _hand_scale(hand: Hand) -> float:
    """Stable within-hand length: wrist -> middle-finger MCP."""
    s = float(np.linalg.norm(_xy(hand, MIDDLE_MCP) - _xy(hand, WRIST)))
    return s if s > 1e-6 else 1.0


def _finger_curl(hand: Hand, tip: int, mcp: int) -> float:
    """1.0 = curled (tip folded toward palm), 0.0 = extended.

    Uses the ratio of (tip->wrist) to (mcp->wrist): an extended finger puts its tip far past the
    knuckle (ratio ~1.6+); a curled finger folds the tip back (ratio drops to ~1.0 or below).
    Calibrated on real hands in Phase 3.
    """
    tip_d = float(np.linalg.norm(_xy(hand, tip) - _xy(hand, WRIST)))
    mcp_d = float(np.linalg.norm(_xy(hand, mcp) - _xy(hand, WRIST)))
    r = tip_d / max(mcp_d, 1e-6)
    return float(np.clip((1.6 - r) / (1.6 - 1.0), 0.0, 1.0))


def _all_curls(hand: Hand) -> list[float]:
    return [_finger_curl(hand, t, m) for t, m in _FINGERS]


def _thumb_extended(hand: Hand) -> float:
    """1.0 = thumb sticking out alongside the hand, 0.0 = tucked/across the palm."""
    d = float(np.linalg.norm(_xy(hand, THUMB_TIP) - _xy(hand, INDEX_MCP))) / _hand_scale(hand)
    return float(np.clip((d - 0.5) / (1.2 - 0.5), 0.0, 1.0))


# ---------------------------------------------------------------------------
# Public classifiers
# ---------------------------------------------------------------------------

def fist_confidence(hand: Hand) -> float:
    """Four fingers curled (thumb unconstrained). Covers fist and S-handshape."""
    return float(np.mean(_all_curls(hand)))


def a_confidence(hand: Hand) -> float:
    """Letter A: four fingers curled AND thumb extended alongside (not wrapped across)."""
    return float(min(fist_confidence(hand), _thumb_extended(hand)))


def index_confidence(hand: Hand) -> float:
    """Index finger extended, the other three curled (1-hand / D / pointing)."""
    curls = _all_curls(hand)
    index_extended = 1.0 - curls[0]
    rest_curled = float(np.mean(curls[1:]))
    return float(np.clip(index_extended * 0.5 + rest_curled * 0.5, 0.0, 1.0))


def open_confidence(hand: Hand) -> float:
    """Open / flat hand: all four fingers extended (B-hand / flat palm / 5)."""
    curls = _all_curls(hand)
    return float(np.clip(1.0 - float(np.mean(curls)), 0.0, 1.0))


def claw_confidence(hand: Hand) -> float:
    """Fingers clearly curled but not fully closed (E-hand / bent-5 approximation).

    Used for MEDICINE and EMERGENCY. Generously scored: any meaningfully-curled hand that isn't
    flat or pointing passes. The motion detector (repeated) carries the discriminating weight for
    these two signs; the handshape only needs to confirm the hand is closed-ish.
    """
    curls = _all_curls(hand)
    m = float(np.mean(curls))
    base = float(np.clip((m - 0.25) / 0.35, 0.0, 1.0))   # 0 at flat, saturates ~0.60
    # A claw has ALL fingers similarly (partly) curled. A wide SPREAD of curls means some fingers
    # are fully out and some fully in — that's a finger-counting shape (n / w / index), not a claw.
    # Penalising spread stops a 2-finger "n" hand (mean curl ~0.5) from reading as a claw.
    spread = float(np.std(curls))
    penalty = float(np.clip(1.0 - max(0.0, spread - 0.15) / 0.35, 0.0, 1.0))
    return float(base * penalty)


def n_confidence(hand: Hand) -> float:
    """Two fingers (index + middle) extended, ring + pinky curled (the "N"/"U"/"H" family).

    v1 approximation: the real N/H thumb details aren't reliably detectable, so we recognise these
    by FINGER COUNT — exactly two extended fingers. NURSE and HOSPITAL use this; it is a minimal
    pair with DOCTOR (a flat hand), distinguished by how many fingers are extended.
    """
    c = _all_curls(hand)
    return float(np.clip(np.mean([1.0 - c[0], 1.0 - c[1], c[2], c[3]]), 0.0, 1.0))


def w_confidence(hand: Hand) -> float:
    """Three fingers (index + middle + ring) extended, pinky curled (the "W" / 3-hand). WATER."""
    c = _all_curls(hand)
    return float(np.clip(np.mean([1.0 - c[0], 1.0 - c[1], 1.0 - c[2], c[3]]), 0.0, 1.0))


def middle_confidence(hand: Hand) -> float:
    """Middle finger extended, the other three curled — the SICK "agony" handshape (v1 approx)."""
    c = _all_curls(hand)
    return float(np.clip(np.mean([c[0], 1.0 - c[1], c[2], c[3]]), 0.0, 1.0))


# ---------------------------------------------------------------------------
# Dispatch — matches the `kind` strings used in HandShapeReq
# ---------------------------------------------------------------------------

_DISPATCH = {
    "fist": fist_confidence,
    "s": fist_confidence,
    "a": a_confidence,
    "index": index_confidence,
    "open": open_confidence,
    "b": open_confidence,           # Saad's PLEASE/THANK_YOU use "b" / "5" — same shape as open
    "5": open_confidence,
    "claw": claw_confidence,
    "n": n_confidence,              # 2 fingers — NURSE
    "h": n_confidence,              # H is the same 2-finger shape — HOSPITAL
    "u": n_confidence,              # alias
    "w": w_confidence,              # 3 fingers — WATER
    "middle": middle_confidence,    # SICK
}


def handshape_confidence(hand: Hand, kind: str) -> float:
    """Confidence in [0, 1] that `hand` forms handshape `kind`. Unknown kinds score 0."""
    fn = _DISPATCH.get(kind.lower())
    return fn(hand) if fn is not None else 0.0
