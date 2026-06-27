"""COFFEE confusor regression test.

Replays two fixtures through the verifier:
  - coffee_correct.json  -> must PASS, with movement confidence clearing threshold.
  - coffee_confusor.json -> must FAIL, specifically because the MOVEMENT parameter is below
    threshold (not because of a handshape or location failure).

This is the real prevention mechanism for the original single-frame bug: it fails loudly if
anyone later weakens the movement check or the schema guard.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.landmarks import Frame, RollingBuffer
from core.verifier import verify
from signs import COFFEE

FIXTURES = Path(__file__).parent / "fixtures"


def _load_buffer(fixture_name: str) -> RollingBuffer:
    path = FIXTURES / f"{fixture_name}.json"
    with open(path) as fh:
        data = json.load(fh)
    buf = RollingBuffer(window_seconds=5.0)
    for fd in data["frames"]:
        buf.add(Frame.from_dict(fd))
    return buf


class TestCoffeeCorrect:
    """The correct COFFEE sign (circling fist over a held fist) must pass."""

    def test_overall_pass(self):
        result = verify(_load_buffer("coffee_correct"), COFFEE)
        assert result.passed, (
            f"Correct COFFEE should pass but failed on: {result.failing_required}"
        )

    def test_movement_clears_threshold(self):
        result = verify(_load_buffer("coffee_correct"), COFFEE)
        m = result.get("movement")
        assert m is not None
        assert m.score >= m.threshold, (
            f"Movement should clear threshold: {m.score:.2f} < {m.threshold:.2f}"
        )

    def test_handshape_clears(self):
        result = verify(_load_buffer("coffee_correct"), COFFEE)
        for name in ("handshape_dominant", "handshape_nondominant"):
            p = result.get(name)
            assert p is not None and p.cleared, f"{name} should clear: {p.score:.2f}"


class TestCoffeeConfusor:
    """Two motionless fists — the exact pose that caused the original bug.

    Must FAIL, and must fail specifically on the MOVEMENT parameter. Handshape and location
    should still score well (that's the whole point: a great static pose can't bypass the
    movement gate).
    """

    def test_overall_fail(self):
        result = verify(_load_buffer("coffee_confusor"), COFFEE)
        assert not result.passed, "Static confusor must NOT pass"

    def test_fails_on_movement(self):
        result = verify(_load_buffer("coffee_confusor"), COFFEE)
        assert "movement" in result.failing_required, (
            f"Confusor should fail on movement, but failing_required={result.failing_required}"
        )

    def test_movement_below_threshold(self):
        result = verify(_load_buffer("coffee_confusor"), COFFEE)
        m = result.get("movement")
        assert m is not None
        assert m.score < m.threshold, (
            f"Confusor movement should be below threshold: {m.score:.2f} >= {m.threshold:.2f}"
        )

    def test_handshape_still_good(self):
        """The confusor has correct handshape — it fails ONLY because of movement."""
        result = verify(_load_buffer("coffee_confusor"), COFFEE)
        for name in ("handshape_dominant", "handshape_nondominant"):
            p = result.get(name)
            assert p is not None and p.cleared, (
                f"Confusor {name} should still be good: {p.score:.2f}"
            )
