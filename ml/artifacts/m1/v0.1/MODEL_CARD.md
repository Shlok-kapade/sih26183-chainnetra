# MODEL_CARD — M1 Address Role Classifier

## Intended Use
Classify blockchain addresses into one of 7 roles to support
investigative leads for law enforcement. **Outputs are investigative leads, not
proof of wrongdoing.**

## Classes
- exchange_hot_or_collection
- exchange_deposit
- mixer
- bridge
- dex_or_contract
- illicit
- personal_or_unknown

## Training Data
- **Real labels**: 4 rows from data/labels/ (OFAC SDN, PoR disclosures)
- **Synthetic data**: 300 samples/class from scripts/synth_laundering.py (seed=42)
- **WARNING**: Model is currently trained primarily on synthetic data due to
  insufficient real labeled addresses. Metrics below are on synthetic test data and
  will NOT generalize to real-world performance. Real-world performance is unknown
  until real labeled data is added.

## Splits
- Temporal: 80% train / 10% calibration / 20% test (by generation index)
- Leave-one-class-out: see metrics.json

## Metrics (synthetic test set — see warning above)
- Macro-F1 (LightGBM, calibrated): 1.000
- Macro-F1 (LogReg baseline): 1.000
- Macro-F1 (Rules baseline): 0.036
- ECE (before cal): 0.0000 | ECE (after cal): 0.0000

## Calibration
Isotonic calibration on held-out calibration fold. Abstain (→ UNATTRIBUTED)
when max probability < 0.4.

## Failure Modes
- Payment processors look like exchange_hot (FP)
- OTC desks look like exchange_deposit (FP)
- Shared deposit addresses across users reduce precision
- Stale labels (VASP changes custodian) cause misclassification
- Synthetic training → real-world distribution shift is unknown

## Label Bias
Labels biased to large exchanges (Binance PoR), OFAC-listed addresses.
Under-represents DeFi, DEX, regional exchanges.

## Fairness / Harms Note
Misattribution risk: model may incorrectly flag legitimate personal wallets
as illicit. All outputs must be reviewed by a human analyst before any action.

## Version
v0.1 — see config.json
