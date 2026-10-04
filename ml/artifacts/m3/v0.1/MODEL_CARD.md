# M3 Model Card — Guided Tracing Policy

## Intended Use
Priority function for best-first search over blockchain transaction graphs.
Predicts P(labeled VASP reachable within remaining hop budget) for a frontier node.
Used to rank which node to expand next, minimizing API calls needed to find exits.

## Training Data
- **Source**: Synthetic graphs from `scripts/synth_laundering.py`
- **Size**: 990 node observations from 120 trace graphs
- **Features**: 16 (path features + M1 role probs + label proximity)
- **Split**: Group-based by seed_id; no seed in both train and test

## ⚠️ Ground-Truth Bias (MUST READ)
Ground truth only includes exits to **labeled** VASPs (exchange addresses in
`data/labels/*.csv`). Unlabeled exchanges are invisible to the evaluation.
Published recall metrics are **lower bounds** on true coverage. In production,
the engine will find more exits than the metrics suggest — but those extra exits
cannot be verified against ground truth without broader labeling.

## Metrics (synthetic test set)
| Metric | Value |
|--------|-------|
| PR-AUC | 1.0000 |
| ROC-AUC | 1.0000 |
| F1 @ threshold=0.5 | 1.0000 |
| ECE | 0.0000 |

## Top SHAP Features
- taint_share: 5.7100
- dwell_so_far_hours: 2.6868
- value_trend_log: 0.3853
- hops_so_far: 0.0000
- fan_out_width: 0.0000

## Failure Modes
- Synthetic distribution differs from real-world (sparse, heterogeneous) graphs
- M1 role probs injected as uniform (M1 not integrated at dataset build time)
- LOEO not applicable here (group split by trace seed serves same purpose)
- Assumes labeled VASP addresses are in `data/labels/`; fresh VASPs invisible

## Version
v0.1 | seed=42
