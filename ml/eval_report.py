"""Per-class metrics (precision / recall / F1 / support) for a trained run.

Loads a saved run's model + the cache it was trained on, predicts on the held-out TEST split
(falls back to val if no test), and prints a classification report plus macro/weighted averages
and overall accuracy. Pure numpy — no sklearn dependency.

    python -m ml.eval_report --run ml/runs/model_v4 --cache data/cache_merged.npz
"""
from __future__ import annotations

import os
os.environ.setdefault("TF_USE_LEGACY_KERAS", "1")

import argparse
import json
from pathlib import Path

import numpy as np

from ml.dataset import SEQ_LEN  # noqa: F401  (kept for parity / sanity)


def per_class_metrics(y_true, y_pred, n_classes):
    """Return arrays (precision, recall, f1, support) indexed by class id."""
    prec = np.zeros(n_classes)
    rec = np.zeros(n_classes)
    f1 = np.zeros(n_classes)
    sup = np.zeros(n_classes, dtype=int)
    for c in range(n_classes):
        tp = int(np.sum((y_pred == c) & (y_true == c)))
        fp = int(np.sum((y_pred == c) & (y_true != c)))
        fn = int(np.sum((y_pred != c) & (y_true == c)))
        sup[c] = int(np.sum(y_true == c))
        prec[c] = tp / (tp + fp) if (tp + fp) else 0.0
        rec[c] = tp / (tp + fn) if (tp + fn) else 0.0
        f1[c] = (2 * prec[c] * rec[c] / (prec[c] + rec[c])) if (prec[c] + rec[c]) else 0.0
    return prec, rec, f1, sup


def main() -> None:
    ap = argparse.ArgumentParser(description="Per-class precision/recall/F1 for a run.")
    ap.add_argument("--run", default="ml/runs/model_v4")
    ap.add_argument("--cache", default="data/cache_merged.npz")
    args = ap.parse_args()

    run = Path(args.run)
    classes = json.loads((run / "classes.json").read_text(encoding="utf-8"))

    data = np.load(args.cache, allow_pickle=True)
    X, y, split = data["X"], data["y"], data["split"]
    mask = (split == "test")
    split_name = "test"
    if mask.sum() == 0:
        mask = (split == "val")
        split_name = "val"

    import tensorflow as tf  # noqa: F401
    from tensorflow.keras.models import load_model
    model = load_model(run / "model.keras")

    yp = model.predict(X[mask], verbose=0).argmax(1)
    yt = y[mask]
    n = len(classes)

    prec, rec, f1, sup = per_class_metrics(yt, yp, n)
    acc = float((yp == yt).mean())

    print(f"\n=== {run.name} — per-class metrics on {split_name} split "
          f"({int(mask.sum())} clips) ===\n")
    print(f"{'sign':<12} {'precision':>9} {'recall':>7} {'f1':>6} {'support':>8}")
    order = np.argsort(-sup)  # most-supported first
    for c in order:
        print(f"{classes[c]:<12} {prec[c]:>9.3f} {rec[c]:>7.3f} {f1[c]:>6.3f} {sup[c]:>8d}")

    # Macro = unweighted mean over classes; weighted = support-weighted.
    w = sup / sup.sum()
    print("\n" + "-" * 46)
    print(f"{'accuracy':<12} {'':>9} {'':>7} {acc:>6.3f} {int(sup.sum()):>8d}")
    print(f"{'macro avg':<12} {prec.mean():>9.3f} {rec.mean():>7.3f} {f1.mean():>6.3f} "
          f"{int(sup.sum()):>8d}")
    print(f"{'weighted avg':<12} {float((prec*w).sum()):>9.3f} {float((rec*w).sum()):>7.3f} "
          f"{float((f1*w).sum()):>6.3f} {int(sup.sum()):>8d}")

    # Persist alongside the run for the record.
    report = {
        "split": split_name, "n_clips": int(mask.sum()), "accuracy": acc,
        "macro_f1": float(f1.mean()),
        "weighted_f1": float((f1 * w).sum()),
        "per_class": {classes[c]: {"precision": float(prec[c]), "recall": float(rec[c]),
                                   "f1": float(f1[c]), "support": int(sup[c])}
                      for c in range(n)},
    }
    (run / "class_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nsaved -> {run / 'class_report.json'}")


if __name__ == "__main__":
    main()
