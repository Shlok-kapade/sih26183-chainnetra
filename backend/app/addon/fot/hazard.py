"""M8 Hazard model: P(mass moves within next Δt).

Features (point-in-time only — no future leakage):
  holding_time_hours: how long funds have been at this address
  log_value: log10 of held value
  hour_of_day: 0-23
  prev_hop_dwell_hours: dwell time at previous hop (0 if unknown)
  value_fraction: fraction of seed amount at this position

Training: temporal split (train on earlier cases, eval on later).
Baseline: constant hazard = default_daily_rate / 24.

For demo mode: uses a simple logistic model with illustrative coefficients.
For production: train via ml/addon/train_m8_hazard.py on real cached traces.
"""
from dataclasses import dataclass
from typing import Optional
import math

ILLUSTRATIVE_NOTE = "M8 hazard model uses ILLUSTRATIVE coefficients — train on real data for production use."

@dataclass
class HazardFeatures:
    holding_time_hours: float    # time since last receipt
    log_value: float             # log10(value_usd)
    hour_of_day: int             # 0-23 UTC
    prev_hop_dwell_hours: float  # previous hop dwell time, 0 if unknown
    value_fraction: float        # value / seed_amount

@dataclass
class HazardEstimate:
    p_move_next_hour: float      # P(moves in next 1h)
    p_move_next_6h: float
    p_move_next_24h: float
    baseline_p_24h: float        # constant-hazard baseline
    illustrative: bool = True
    note: str = ILLUSTRATIVE_NOTE

# ILLUSTRATIVE coefficients — not fitted to real data
_INTERCEPT = -2.5          # ILLUSTRATIVE
_COEF_HOLDING = -0.05      # longer holding -> lower hazard (ILLUSTRATIVE)
_COEF_LOG_VALUE = 0.3      # larger value -> slightly higher hazard (ILLUSTRATIVE)
_COEF_HOUR = 0.02          # mild time-of-day effect (ILLUSTRATIVE)
_COEF_PREV_DWELL = -0.03   # ILLUSTRATIVE
_COEF_VALUE_FRAC = 0.5     # ILLUSTRATIVE

def _logistic(x: float) -> float:
    """Numerically stable logistic function."""
    if x >= 0:
        return 1.0 / (1.0 + math.exp(-x))
    exp_x = math.exp(x)
    return exp_x / (1.0 + exp_x)

def predict_hazard(features: HazardFeatures, default_daily_rate: float = 0.30) -> HazardEstimate:
    """Predict P(moves) for next 1h, 6h, 24h using ILLUSTRATIVE logistic model."""
    logit = (
        _INTERCEPT
        + _COEF_HOLDING * features.holding_time_hours
        + _COEF_LOG_VALUE * features.log_value
        + _COEF_HOUR * features.hour_of_day
        + _COEF_PREV_DWELL * features.prev_hop_dwell_hours
        + _COEF_VALUE_FRAC * features.value_fraction
    )
    # Convert per-period probability to multi-period survival
    p_1h = _logistic(logit)
    # Approximate: P(moves in k hours) = 1 - (1-p_1h)^k
    p_6h = 1.0 - (1.0 - p_1h) ** 6
    p_24h = 1.0 - (1.0 - p_1h) ** 24
    baseline = 1.0 - math.exp(-default_daily_rate)
    return HazardEstimate(
        p_move_next_hour=round(p_1h, 4),
        p_move_next_6h=round(p_6h, 4),
        p_move_next_24h=round(p_24h, 4),
        baseline_p_24h=round(baseline, 4),
    )

def hazard_poll_interval(estimate: HazardEstimate, config: dict = None) -> int:
    """Return polling interval in seconds. Shorter when hazard is high."""
    cfg = config or {}
    high_interval = cfg.get('high_hazard_interval_seconds', 60)
    default_interval = cfg.get('poll_interval_seconds', 300)
    if estimate.p_move_next_hour > 0.20:
        return high_interval
    return default_interval
