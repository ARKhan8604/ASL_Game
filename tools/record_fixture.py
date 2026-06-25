"""CLI: record a few seconds of live landmarks to a JSON fixture.

Usage:
    python -m tools.record_fixture --name coffee_correct --seconds 3
    python -m tools.record_fixture --name coffee_confusor --seconds 3 --sign COFFEE

Output goes to tests/fixtures/<name>.json. The fixture is a JSON file containing a list of
serialized Frames that the verifier can replay.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from core.recorder import record


def main() -> None:
    ap = argparse.ArgumentParser(description="Record landmark frames to a test fixture.")
    ap.add_argument("--name", required=True, help="fixture name (becomes the filename)")
    ap.add_argument("--seconds", type=float, default=3.0, help="recording duration (default 3)")
    ap.add_argument("--camera", type=int, default=0, help="webcam index")
    ap.add_argument("--sign", default="", help="sign name (for labeling)")
    ap.add_argument("--outdir", default="tests/fixtures", help="output directory")
    args = ap.parse_args()

    out = Path(args.outdir) / f"{args.name}.json"
    record(out, seconds=args.seconds, camera_index=args.camera, sign_name=args.sign)


if __name__ == "__main__":
    main()
