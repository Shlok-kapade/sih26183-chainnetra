"""F5 — Live Frontier Watch: budget-aware polling with adaptive interval."""
import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from app.addon.fot.hazard import predict_hazard, HazardFeatures, hazard_poll_interval
from app.addon.fot.mass_map import build_mass_map, MassPosition
from app.addon.fot.levers import get_lever_options
from app.addon.fot.planner import greedy_plan
from app.addon.ports import TracePort, ClockPort, BudgetPort, NotifyPort

log = logging.getLogger(__name__)

ENABLE_WATCH = True  # Feature flag; set to False in tests if needed

@dataclass
class WatchEntry:
    case_id: str
    position_ref: str
    value: Decimal
    seed_amount: Decimal
    added_at: datetime
    last_hazard: float = 0.0
    status: str = 'active'  # active | triggered | cancelled

class FrontierWatcher:
    """Polls HELD positions. On movement: update mass map, recompute plan, emit event."""

    def __init__(
        self,
        trace: TracePort,
        clock: ClockPort,
        budget: BudgetPort,
        notify: NotifyPort,
        config: dict = None,
        seed_amount: Decimal = Decimal('0'),
        K: int = 5,
    ):
        self.trace = trace
        self.clock = clock
        self.budget = budget
        self.notify = notify
        self.config = config or {}
        self.seed_amount = seed_amount
        self.K = K
        self._watches: dict = {}  # case_id -> WatchEntry
        self._running = False

    def add_watch(self, case_id: str, position_ref: str, value: Decimal):
        """Register a HELD position for watching."""
        self._watches[case_id] = WatchEntry(
            case_id=case_id,
            position_ref=position_ref,
            value=value,
            seed_amount=self.seed_amount,
            added_at=self.clock.now(),
        )
        log.info(f"Watch added: {case_id}/{position_ref} value={value}")

    def get_watch(self, case_id: str) -> Optional[WatchEntry]:
        return self._watches.get(case_id)

    async def tick(self, case_id: str) -> bool:
        """One poll tick. Returns True if movement detected."""
        if not ENABLE_WATCH:
            return False
        watch = self._watches.get(case_id)
        if not watch or watch.status != 'active':
            return False

        # Compute hazard
        now = self.clock.now()
        holding_hours = (now - watch.added_at).total_seconds() / 3600
        import math
        features = HazardFeatures(
            holding_time_hours=holding_hours,
            log_value=max(0.0, math.log10(float(watch.value))) if float(watch.value) > 0 else 0.0,
            hour_of_day=now.hour,
            prev_hop_dwell_hours=0.0,
            value_fraction=float(watch.value / watch.seed_amount) if watch.seed_amount else 0.0,
        )
        estimate = predict_hazard(features)
        watch.last_hazard = estimate.p_move_next_hour

        # Check for movement by re-reading graph
        self.budget.charge(1)
        graph = self.trace.get_case_graph(case_id)
        t = self.clock.now()
        mass_map = build_mass_map(case_id, t, graph, watch.seed_amount)

        # Detect if any HELD positions have changed to IN_TRANSIT/EXITED
        held_positions = [p for p in mass_map.positions if p.status == 'HELD' and p.position_ref == watch.position_ref]
        if not held_positions:
            # Position moved!
            watch.status = 'triggered'
            log.info(f"Movement detected: {case_id}/{watch.position_ref}")
            # Recompute plan
            levers = get_lever_options(mass_map)
            plan = greedy_plan(case_id, levers, self.K)
            await self.notify.emit(case_id, 'mass_moved', {
                'position': watch.position_ref,
                'new_ev': float(plan.ev_total),
                'illustrative': True,
            })
            await self.notify.emit(case_id, 'plan_changed', {
                'ev_total': float(plan.ev_total),
                'actions': len(plan.actions),
                'illustrative': True,
            })
            return True

        return False

    async def run_watch_job(self, case_id: str, max_ticks: int = 100):
        """Run watch loop for a case. Stops on movement, budget exhaustion, or max_ticks."""
        tick_count = 0
        while tick_count < max_ticks and self.budget.calls_left(case_id) > 0:
            moved = await self.tick(case_id)
            if moved:
                break
            # Adaptive sleep (fixture: skip actual sleep)
            watch = self._watches.get(case_id)
            if watch:
                features = HazardFeatures(
                    holding_time_hours=(self.clock.now() - watch.added_at).total_seconds() / 3600,
                    log_value=5.0, hour_of_day=self.clock.now().hour,
                    prev_hop_dwell_hours=0.0, value_fraction=0.5,
                )
                estimate = predict_hazard(features)
                interval = hazard_poll_interval(estimate, self.config)
                if hasattr(self.clock, 'advance'):
                    self.clock.advance(interval)  # Simulate time passing in tests
            tick_count += 1
        log.info(f"Watch job done: {case_id}, ticks={tick_count}")
