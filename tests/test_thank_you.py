"""THANK YOU confusor regression test.

THANK YOU = an open hand moving downward (chin -> out/down). The confusor is an open hand held
still — same handshape, no movement — and must fail specifically on movement. This is also the
first sign exercising the LINEAR movement detector in the test suite.
"""
from __future__ import annotations

import json
from pathlib import Path

from core.landmarks import Frame, RollingBuffer
from core.verifier import verify
from signs import THANK_YOU

FIXTURES = Path(__file__).parent / "fixtures"


def _load_buffer(name: str) -> RollingBuffer:
    with open(FIXTURES / f"{name}.json") as fh:
        data = json.load(fh)
    buf = RollingBuffer(window_seconds=5.0)
    for fd in data["frames"]:
        buf.add(Frame.from_dict(fd))
    return buf


class TestThankYouCorrect:
    def test_overall_pass(self):
        result = verify(_load_buffer("thankyou_correct"), THANK_YOU)
        assert result.passed, f"Correct THANK YOU should pass; failing={result.failing_required}"

    def test_movement_clears(self):
        m = verify(_load_buffer("thankyou_correct"), THANK_YOU).get("movement")
        assert m.score >= m.threshold, f"linear movement {m.score:.2f} < {m.threshold:.2f}"


class TestThankYouConfusor:
    def test_overall_fail(self):
        assert not verify(_load_buffer("thankyou_confusor"), THANK_YOU).passed

    def test_fails_on_movement(self):
        result = verify(_load_buffer("thankyou_confusor"), THANK_YOU)
        assert "movement" in result.failing_required, (
            f"still open hand should fail on movement; failing={result.failing_required}"
        )

    def test_handshape_still_good(self):
        p = verify(_load_buffer("thankyou_confusor"), THANK_YOU).get("handshape_dominant")
        assert p.cleared, f"confusor handshape should still be good: {p.score:.2f}"


class TestThankYouWrongLocation:
    """An open hand moving down but starting BELOW the chin must fail on location.

    THANK YOU starts at the chin; a downward open-hand move that never reaches chin height is not
    THANK YOU. Correct handshape + correct (downward) movement must not bypass the location.
    """

    def test_lowstart_fails_on_location(self):
        result = verify(_load_buffer("thankyou_lowstart"), THANK_YOU)
        assert not result.passed, "down-from-chest must not pass as THANK YOU"
        assert "location" in result.failing_required, (
            f"low start should fail on location; failing={result.failing_required}"
        )

    def test_hand_on_head_fails_location(self):
        """The reported bug: a hand up on the head (above the mouth) must NOT score location.

        Anchoring to the real mouth landmark (not a guessed offset) makes this robust to camera
        position — the head is above the mouth, so it's excluded from the chin check.
        """
        loc = verify(_load_buffer("thankyou_onhead"), THANK_YOU).get("location")
        assert loc.score < loc.threshold, f"hand on head must fail location: {loc.score:.2f}"
