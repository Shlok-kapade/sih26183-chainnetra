"""Shared ML utilities — ECE, PR-AUC helpers."""
from __future__ import annotations

import numpy as np
from sklearn.metrics import average_precision_score


def expected_calibration_error(
    y_prob: np.ndarray, y_true: np.ndarray, n_bins: int = 10
) -> float:
    """Compute Expected Calibration Error (multiclass, confidence-based)."""
    confidences = y_prob.max(axis=1)
    predictions = y_prob.argmax(axis=1)
    correct = (predictions == y_true).astype(float)
    bin_edges = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    n = len(y_true)
    for i in range(n_bins):
        lo, hi = bin_edges[i], bin_edges[i + 1]
        if i == n_bins - 1:
            mask = (confidences >= lo) & (confidences <= hi)  # include 1.0
        else:
            mask = (confidences >= lo) & (confidences < hi)
        if mask.sum() == 0:
            continue
        acc = correct[mask].mean()
        conf = confidences[mask].mean()
        ece += (mask.sum() / n) * abs(acc - conf)
    return float(ece)


def per_class_pr_auc(
    y_prob: np.ndarray, y_true: np.ndarray, class_names: list[str]
) -> dict[str, float]:
    """Per-class PR-AUC using one-vs-rest."""
    aucs: dict[str, float] = {}
    for i, cls in enumerate(class_names):
        # Binary label: 1 if true class == i, else 0
        y_bin_i = (y_true == i).astype(int)
        if y_bin_i.sum() == 0:
            aucs[cls] = float("nan")
        else:
            aucs[cls] = float(average_precision_score(y_bin_i, y_prob[:, i]))
    return aucs
