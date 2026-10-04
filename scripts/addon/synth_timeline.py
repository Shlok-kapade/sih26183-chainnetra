"""SYNTHETIC FOT timeline generator. All data labeled SYNTHETIC."""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from app.addon.fot.replay import ReplayEvent

def generate_d9_timeline(
    seed_amount: Decimal = Decimal('50000'),
    dormancy_hours: float = 4.0,
) -> list:
    """SYNTHETIC D9: funds sit dormant then move toward exchange. Labeled SYNTHETIC."""
    t0 = datetime(2026, 1, 1, 8, 0, 0, tzinfo=timezone.utc)
    events = [
        ReplayEvent(ts=t0, event_type='case_start', address='TSYNTH_VICTIM', detail={'amount': float(seed_amount)}),
        ReplayEvent(ts=t0 + timedelta(hours=0.5), event_type='new_trace', address='TSYNTH_HOP1', detail={}),
        # Dormancy period
        ReplayEvent(ts=t0 + timedelta(hours=dormancy_hours), event_type='movement', address='TSYNTH_HOP1',
                    detail={'to': 'TSYNTH_HOP2', 'amount': float(seed_amount * Decimal('0.98'))}),
        ReplayEvent(ts=t0 + timedelta(hours=dormancy_hours + 0.5), event_type='movement', address='TSYNTH_HOP2',
                    detail={'to': 'TSYNTH_EXCHANGE_DEPOSIT', 'amount': float(seed_amount * Decimal('0.97'))}),
    ]
    return events

def generate_rapid_exit_timeline(
    seed_amount: Decimal = Decimal('100000'),
) -> list:
    """SYNTHETIC: funds move rapidly through 3 hops to exchange. SYNTHETIC."""
    t0 = datetime(2026, 1, 2, 10, 0, 0, tzinfo=timezone.utc)
    return [
        ReplayEvent(ts=t0, event_type='case_start', address='TSYNTH_VICTIM2', detail={'amount': float(seed_amount)}),
        ReplayEvent(ts=t0 + timedelta(minutes=10), event_type='movement', address='TSYNTH_HOP_A',
                    detail={'to': 'TSYNTH_HOP_B', 'amount': float(seed_amount * Decimal('0.99'))}),
        ReplayEvent(ts=t0 + timedelta(minutes=20), event_type='movement', address='TSYNTH_HOP_B',
                    detail={'to': 'TSYNTH_EXCHANGE_HOT', 'amount': float(seed_amount * Decimal('0.98'))}),
    ]
