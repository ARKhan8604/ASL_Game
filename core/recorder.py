"""Record live normalized frames to a JSON fixture for the confusor test suite.

Each fixture is a list of Frame.to_dict() snapshots captured over a few seconds. The verifier
replays these the same way it reads a live buffer — no special fixture format, just the same
Frame model serialized to JSON.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import cv2

from core.capture import Capture
from core.landmarks import Frame


def record(
    output_path: str | Path,
    seconds: float = 3.0,
    camera_index: int = 0,
    sign_name: str = "",
) -> list[Frame]:
    """Record `seconds` of landmarks from the webcam and write to a JSON file.

    Shows a live preview with a countdown. Returns the recorded frames.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open webcam (index {camera_index}).")

    frames: list[Frame] = []

    win = f"Recording: {sign_name or output_path.stem} ({seconds:.0f}s)"
    cv2.namedWindow(win, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(win, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # MediaPipe's VIDEO mode requires timestamps that increase monotonically for the LIFETIME of
    # the detector. We therefore feed it one continuous clock (`session_t0`) across BOTH the warmup
    # and the recording — never resetting it. The recording-relative time we store on each Frame
    # (`t_seconds`) is a separate clock that starts at 0 when recording begins, which is all the
    # movement math needs. (The previous version reset capture._last_ts_ms after warmup, which sent
    # a timestamp backwards into MediaPipe and crashed/froze the window right after "GET READY".)
    session_t0 = time.monotonic()

    with Capture() as capture:
        # Warmup: run capture.process() so the hand + pose models are fully initialized before
        # recording starts. Without this, the first ~1s of recording gets zero hands.
        warmup_end = time.monotonic() + 2.0
        while time.monotonic() < warmup_end:
            ok, bgr = cap.read()
            if not ok:
                continue
            bgr = cv2.flip(bgr, 1)
            ts_ms = int((time.monotonic() - session_t0) * 1000)
            capture.process(bgr, timestamp_ms=ts_ms, t_seconds=0.0)
            remaining_w = warmup_end - time.monotonic()
            cv2.putText(bgr, f"GET READY  {remaining_w:.1f}s", (15, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 0), 2, cv2.LINE_AA)
            label = sign_name or output_path.stem
            cv2.putText(bgr, f"Sign: {label}", (15, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.imshow(win, bgr)
            cv2.waitKey(1)

        t0 = time.monotonic()
        while True:
            ok, bgr = cap.read()
            if not ok:
                continue
            bgr = cv2.flip(bgr, 1)
            elapsed = time.monotonic() - t0
            remaining = seconds - elapsed
            if remaining <= 0:
                break

            # MediaPipe gets the continuous session clock (monotonic); the Frame stores the
            # recording-relative time (starts at 0) that the verifier/movement math uses.
            ts_ms = int((time.monotonic() - session_t0) * 1000)
            frame = capture.process(bgr, timestamp_ms=ts_ms, t_seconds=elapsed)
            frames.append(frame)

            for hand in frame.hands:
                for px, py, _z in hand.points:
                    cv2.circle(bgr, (int(px), int(py)), 3, (0, 255, 0), -1)

            color = (0, 0, 255) if remaining > 1.0 else (0, 165, 255)
            cv2.putText(bgr, f"RECORDING  {remaining:.1f}s", (15, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2, cv2.LINE_AA)
            label = sign_name or output_path.stem
            cv2.putText(bgr, f"Sign: {label}", (15, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.imshow(win, bgr)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()

    if not frames:
        print(f"WARNING: no frames captured — camera may not be available. File not written.")
        return frames

    data = {
        "sign_name": sign_name,
        "frames": [f.to_dict() for f in frames],
    }
    with open(output_path, "w") as fh:
        json.dump(data, fh)

    print(f"Recorded {len(frames)} frames ({frames[-1].t - frames[0].t:.1f}s) -> {output_path}")
    return frames
