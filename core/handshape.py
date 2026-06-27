"""Geometric handshape predicates over a single hand's 21 landmarks.

Pure 2D geometry, orientation-tolerant. Each handshape is a per-finger pattern of extended (1) /
curled (0) states; `handshape_confidence` scores how well a hand matches the requested pattern.
The verifier smooths these across recent frames (median) so one noisy frame can't flip a result.

Supported kinds: fist/s, open/b/5, a, point/1, v, l, y. Thresholds are a tuned-by-eye first pass;
the live demo exists to calibrate them on real hands.
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

# (tip, mcp) per non-thumb finger
_FINGER_LM = {
    "index": (INDEX_TIP, INDEX_MCP),
    "middle": (MIDDLE_TIP, MIDDLE_MCP),
    "ring": (RING_TIP, RING_MCP),
    "pinky": (PINKY_TIP, PINKY_MCP),
}


def _xy(hand: Hand, idx: int) -> np.ndarray:
    return hand.points[idx, :2]


def _hand_scale(hand: Hand) -> float:
    s = float(np.linalg.norm(_xy(hand, MIDDLE_MCP) - _xy(hand, WRIST)))
    return s if s > 1e-6 else 1.0


def _finger_curl(hand: Hand, tip: int, mcp: int) -> float:
    """1.0 = curled (tip folded toward palm), 0.0 = extended."""
    tip_d = float(np.linalg.norm(_xy(hand, tip) - _xy(hand, WRIST)))
    mcp_d = float(np.linalg.norm(_xy(hand, mcp) - _xy(hand, WRIST)))
    r = tip_d / max(mcp_d, 1e-6)
    return float(np.clip((1.6 - r) / (1.6 - 1.0), 0.0, 1.0))


def _thumb_extended(hand: Hand) -> float:
    """1.0 = thumb sticking out alongside the hand, 0.0 = tucked/across the palm."""
    d = float(np.linalg.norm(_xy(hand, THUMB_TIP) - _xy(hand, INDEX_MCP))) / _hand_scale(hand)
    return float(np.clip((d - 0.5) / (1.2 - 0.5), 0.0, 1.0))


def extensions(hand: Hand) -> dict:
    """Per-digit extension in [0,1] (1 = extended, 0 = curled)."""
    ext = {name: 1.0 - _finger_curl(hand, tip, mcp) for name, (tip, mcp) in _FINGER_LM.items()}
    ext["thumb"] = _thumb_extended(hand)
    return ext


# per-finger target patterns: 1 = must be extended, 0 = must be curled, absent = don't care
_PATTERNS = {
    "fist": dict(index=0, middle=0, ring=0, pinky=0),
    "s": dict(index=0, middle=0, ring=0, pinky=0),
    "open": dict(index=1, middle=1, ring=1, pinky=1),
    "b": dict(index=1, middle=1, ring=1, pinky=1),
    "5": dict(index=1, middle=1, ring=1, pinky=1),
    "point": dict(index=1, middle=0, ring=0, pinky=0),
    "1": dict(index=1, middle=0, ring=0, pinky=0),
    "v": dict(index=1, middle=1, ring=0, pinky=0),
    "l": dict(thumb=1, index=1, middle=0, ring=0, pinky=0),
    "y": dict(thumb=1, index=0, middle=0, ring=0, pinky=1),
}


def fist_confidence(hand: Hand) -> float:
    return _match(hand, _PATTERNS["fist"])


def open_confidence(hand: Hand) -> float:
    return _match(hand, _PATTERNS["open"])


def a_confidence(hand: Hand) -> float:
    """Letter A: four fingers curled AND thumb alongside (distinct from a plain fist)."""
    return float(min(fist_confidence(hand), _thumb_extended(hand)))


def _match(hand: Hand, pattern: dict) -> float:
    ext = extensions(hand)
    scores = [ext[f] if target == 1 else 1.0 - ext[f] for f, target in pattern.items()]
    return float(min(scores)) if scores else 0.0


def handshape_confidence(hand: Hand, kind: str) -> float:
    """Confidence in [0,1] that `hand` forms handshape `kind`. Unknown kinds score 0."""
    kind = kind.lower()
    if kind == "a":
        return a_confidence(hand)
    pattern = _PATTERNS.get(kind)
    return _match(hand, pattern) if pattern is not None else 0.0
