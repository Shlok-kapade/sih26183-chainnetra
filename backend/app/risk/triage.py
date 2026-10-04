import math
from datetime import datetime, timezone
from pathlib import Path

import yaml
from pydantic import BaseModel

CONFIG_PATH = Path(__file__).parents[3] / "config" / "risk_weights.yaml"

class CaseUrgency(BaseModel):
    case_id: str
    urgency_score: float
    severity_level: str
    value_usd: float
    prob_exit: float
    eta_hours: float
    days_since_last_move: float

class TriageEngine:
    def __init__(self, config_path: str | Path = CONFIG_PATH):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

    def compute_urgency(
        self,
        case_id: str,
        value_at_risk_usd: float,
        prob_exit: float,
        eta_hours: float,
        last_move_ts: datetime,
        now_ts: datetime | None = None
    ) -> CaseUrgency:
        if now_ts is None:
            now_ts = datetime.now(timezone.utc)

        days_since = max(0.0, (now_ts - last_move_ts).total_seconds() / 86400.0)

        w_val = self.config["weights"]["value_at_risk_usd"]
        w_prob = self.config["weights"]["prob_exit_hops"]
        decay_half_life = self.config["weights"]["freshness_decay_days"]

        # freshness = exp(-ln(2) * days / half_life)
        freshness = math.exp(-math.log(2) * days_since / decay_half_life)

        safe_eta = max(eta_hours, 1.0)

        # urgency = value_at_risk_usd * P(exit within k hops) * freshness(t_since_last_move) / max(eta_hours, 1)
        score = (value_at_risk_usd * w_val) * (prob_exit * w_prob) * freshness / safe_eta

        # Map to severity
        severity = "LOW"
        thresholds = self.config.get("severity_thresholds", {})
        for level, thresh in thresholds.items():
            if score >= thresh:
                severity = level
                break

        return CaseUrgency(
            case_id=case_id,
            urgency_score=round(score, 2),
            severity_level=severity,
            value_usd=value_at_risk_usd,
            prob_exit=prob_exit,
            eta_hours=eta_hours,
            days_since_last_move=round(days_since, 2)
        )
