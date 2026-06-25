"""Phase 1 demo: live landmarks + normalized inter-hand distance.

Proves capture + normalization + the rolling buffer work end-to-end before any sign logic
exists. Opens the webcam, draws hand landmarks (green), each palm center (red), and the
shoulders (blue), and prints the inter-hand distance measured in SHOULDER WIDTHS — the
scale-invariant unit every threshold will use.

Run (with the venv active and models downloaded):
    python -m tools.demo_landmarks
Press 'q' to quit.
"""
from __future__ import annotations

import time

import cv2

from core.capture import Capture
from core.landmarks import RollingBuffer, normalized_distance


def main(camera_index: int = 0, window_seconds: float = 2.0) -> None:
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open webcam (index {camera_index}).")

    buffer = RollingBuffer(window_seconds=window_seconds)
    t0 = time.monotonic()

    with Capture() as capture:
        while True:
            ok, bgr = cap.read()
            if not ok:
                break
            bgr = cv2.flip(bgr, 1)  # mirror so movement feels natural
            t = time.monotonic() - t0
            frame = capture.process(bgr, timestamp_ms=int(t * 1000), t_seconds=t)
            buffer.add(frame)

            # hand landmarks (green) + palm centers (red)
            for hand in frame.hands:
                for x, y, _z in hand.points:
                    cv2.circle(bgr, (int(x), int(y)), 3, (0, 255, 0), -1)
                cx, cy = hand.center
                cv2.circle(bgr, (int(cx), int(cy)), 6, (0, 0, 255), -1)

            # shoulders (blue) — the scale reference
            if frame.left_shoulder is not None and frame.right_shoulder is not None:
                for sx, sy in (frame.left_shoulder, frame.right_shoulder):
                    cv2.circle(bgr, (int(sx), int(sy)), 6, (255, 0, 0), -1)

            # readout
            if frame.is_complete:
                d = normalized_distance(frame.hands[0].center, frame.hands[1].center, frame.shoulder_width)
                line = f"inter-hand: {d:.2f} shoulder-widths   buffer: {len(buffer)} frames / {buffer.duration:.1f}s"
            else:
                line = f"hands: {len(frame.hands)}   shoulders: {'yes' if frame.shoulder_width else 'no'}   (need both hands + shoulders)"
            cv2.putText(bgr, line, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)

            cv2.imshow("ASL_Game - Phase 1 landmark demo (q to quit)", bgr)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
