"""Strip training-only artifacts from a TF.js model.json so it loads in the browser.

TF.js's LayersModel deserializer rejects some Keras configs that are irrelevant at inference:
  * weight regularizers (kernel/recurrent/bias_regularizer) — they only shape the TRAINING
    loss; at predict time they do nothing. Newer Keras serializes L2 as class_name "L2",
    which TF.js doesn't recognize ("Unknown regularizer: L2").
Removing them changes the model's OUTPUTS by exactly zero. This rewrites model.json in place.

    python -m ml.sanitize_tfjs web/public/models/signs/model.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REG_KEYS = ("kernel_regularizer", "recurrent_regularizer", "bias_regularizer",
            "activity_regularizer")


def strip_regularizers(obj):
    """Recursively set any *_regularizer config entry to null."""
    n = 0
    if isinstance(obj, dict):
        for k in list(obj.keys()):
            if k in REG_KEYS and obj[k] is not None:
                obj[k] = None
                n += 1
            else:
                n += strip_regularizers(obj[k])
    elif isinstance(obj, list):
        for item in obj:
            n += strip_regularizers(item)
    return n


def sanitize(path: str) -> None:
    p = Path(path)
    model = json.loads(p.read_text(encoding="utf-8"))
    n = strip_regularizers(model)
    p.write_text(json.dumps(model), encoding="utf-8")
    print(f"sanitized {p}: nulled {n} regularizer entries")


if __name__ == "__main__":
    targets = sys.argv[1:] or ["web/public/models/signs/model.json"]
    for t in targets:
        sanitize(t)
