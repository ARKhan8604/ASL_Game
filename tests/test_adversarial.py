"""Adversarial regression tests — the "edge cases" that previously leaked through.

These build deliberately-WRONG performances geometrically (right handshape but wrong place, right
place but wrong handshape, too little motion, one hand instead of two, …) and assert the verifier
REJECTS them. They lock the holes found in live testing:

  - WATER / NURSE passing for ANY hand   (handshape scorers were averaged, not strict)
  - DOCTOR / NURSE passing tapping ANYWHERE (OTHER_HAND had no body-height constraint)
  - BREATHE passing with only resting motion (repeated amplitude floor was too low)

If any of these starts passing again, that gate has regressed.
"""
from __future__ import annotations

import math

from core.landmarks import RollingBuffer
from core.verifier import verify
import tools.make_synth_fixtures as M
from signs import WATER, DOCTOR, NURSE, BREATHE, SICK, FEVER, HOSPITAL, DIZZY


def _buf(frames):
    b = RollingBuffer(window_seconds=5.0)
    for f in frames:
        b.add(f)
    return b


def _osc(center_y, amp=22.0, freq=1.5):
    return [center_y + amp * math.sin(2 * math.pi * freq * t) for t in M._ts()]


def _passes(sign, frames) -> bool:
    return verify(_buf(frames), sign).passed


# ----------------------------------------------------------------- WATER (W at the chin)
def test_water_rejects_open_hand_at_chin():
    frames = [M._frame(t, [M.make_hand("Right", [M.CX, y], "open")]) for t, y in zip(M._ts(), _osc(M.Y_CHIN))]
    assert not _passes(WATER, frames), "an OPEN hand must not pass WATER (handshape must be a real W)"


def test_water_rejects_w_hand_off_chin():
    frames = [M._frame(t, [M.make_hand("Right", [M.CX, y], "w")]) for t, y in zip(M._ts(), _osc(M.Y_CHEST))]
    assert not _passes(WATER, frames), "a W hand tapping at the chest (not the chin) must not pass WATER"


# ----------------------------------------------------------------- DOCTOR / NURSE (tap the wrist)
def test_doctor_rejects_tapping_at_the_face():
    frames = [M._frame(t, [M.make_hand("Right", [M.CX + 30, y], "open"),
                           M.make_hand("Left", [M.CX + 30, M.Y_FOREHEAD], "open")])
              for t, y in zip(M._ts(), _osc(M.Y_FOREHEAD))]
    assert not _passes(DOCTOR, frames), "tapping two hands at the forehead must not pass DOCTOR"


def test_doctor_rejects_single_hand():
    frames = [M._frame(t, [M.make_hand("Right", [M.CX, y], "open")]) for t, y in zip(M._ts(), _osc(M.Y_BELLY))]
    assert not _passes(DOCTOR, frames), "one hand alone must not pass the two-handed DOCTOR"


def test_nurse_rejects_open_hand():
    frames = [M._frame(t, [M.make_hand("Right", [M.CX + 50, y], "open"),
                           M.make_hand("Left", [M.CX + 50, M.Y_BELLY + 10], "open")])
              for t, y in zip(M._ts(), _osc(M.Y_BELLY - 10))]
    assert not _passes(NURSE, frames), "an OPEN hand (not a 2-finger N) must not pass NURSE"


# ----------------------------------------------------------------- BREATHE (deliberate out/in)
def test_breathe_rejects_resting_motion():
    frames = [M._frame(t, [M.make_hand("Right", [M.CX + 80 + x, M.Y_CHEST], "open"),
                           M.make_hand("Left", [M.CX - 80, M.Y_CHEST], "open")])
              for t, x in zip(M._ts(), _osc(0.0, amp=8.0))]
    assert not _passes(BREATHE, frames), "small resting motion must not pass BREATHE (needs a big out/in)"


# ----------------------------------------------------------------- SICK / FEVER / HOSPITAL / DIZZY
def test_sick_rejects_open_hands():
    frames = [M._frame(t, [M.make_hand("Right", [M.CX, M.Y_FOREHEAD], "open"),
                           M.make_hand("Left", [M.CX, M.Y_BELLY], "open")]) for t in M._ts()]
    assert not _passes(SICK, frames), "open hands (not middle fingers) must not pass SICK"


def test_fever_rejects_open_hand_at_chest():
    frames = [M._frame(t, [M.make_hand("Right", [x, M.Y_CHEST], "open")])
              for t, x in zip(M._ts(), [(M.CX - 50) + 100 * (i / (M.N - 1)) for i in range(M.N)])]
    assert not _passes(FEVER, frames), "a sweep at the chest (not the forehead) must not pass FEVER"


def test_hospital_rejects_stroke_in_neutral_space():
    # H hand drawing in the centre of the torso, nowhere near a shoulder
    frames = [M._frame(t, [M.make_hand("Right", [M.CX, 200 + 50 * (i / (M.N - 1))], "h"),
                           M.make_hand("Left", [M.CX, 250], "open")])
              for i, t in enumerate(M._ts())]
    assert not _passes(HOSPITAL, frames), "a stroke in neutral space (not near a shoulder) must not pass HOSPITAL"


def test_dizzy_rejects_static_hand_at_face():
    frames = [M._frame(t, [M.make_hand("Right", [M.CX, M.Y_FOREHEAD], "claw")]) for t in M._ts()]
    assert not _passes(DIZZY, frames), "a still clawed hand at the face must not pass DIZZY (needs the circle)"
