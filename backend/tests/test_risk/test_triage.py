from datetime import datetime, timedelta, timezone

from app.risk.triage import TriageEngine


def test_triage_engine():
    engine = TriageEngine()

    now = datetime(2026, 1, 10, 12, 0, 0, tzinfo=timezone.utc)
    # Moving yesterday (1 day ago)
    last_move = now - timedelta(days=1)

    # 1M USD, high probability, 1 day ago -> should be CRITICAL
    urgency = engine.compute_urgency(
        case_id="TEST-01",
        value_at_risk_usd=1000000.0,
        prob_exit=0.9,
        eta_hours=1.0,
        last_move_ts=last_move,
        now_ts=now
    )

    assert urgency.case_id == "TEST-01"
    assert urgency.value_usd == 1000000.0
    assert urgency.severity_level == "CRITICAL"

    # Low value, old move (30 days ago) -> should be LOW/MEDIUM depending on threshold
    old_move = now - timedelta(days=30)
    urgency2 = engine.compute_urgency(
        case_id="TEST-02",
        value_at_risk_usd=1000.0,
        prob_exit=0.5,
        eta_hours=24.0,
        last_move_ts=old_move,
        now_ts=now
    )

    assert urgency2.severity_level in ["LOW", "MEDIUM"]
    assert urgency2.urgency_score < urgency.urgency_score
