"""FOT Replay harness: simulates trace decisions over a recorded timeline."""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, Callable
import logging

from app.addon.ports import TracePort, ExitPolicyPort, LabelPort, ClockPort, BudgetPort, NotifyPort
from app.addon.fot.mass_map import build_mass_map, MassMap
from app.addon.fot.levers import get_lever_options
from app.addon.fot.planner import greedy_plan, ActionPlan
from app.addon.fot.voi import voi_priority, should_act_now

log = logging.getLogger(__name__)

@dataclass
class ReplayEvent:
    """One event in a synthetic timeline."""
    ts: datetime
    event_type: str  # 'movement', 'new_trace', 'case_start'
    address: str
    detail: dict = field(default_factory=dict)

@dataclass
class ReplayResult:
    """Outcome of a replay run."""
    case_id: str
    baseline_name: str
    time_to_first_action_hours: Optional[float]
    api_calls_used: int
    plans_computed: int
    final_ev_total: Decimal
    act_now_triggered: bool
    illustrative_note: str = "All EV values use ILLUSTRATIVE priors — not real-world freeze rates."

class ReplayRunner:
    """Runs FOT decision loop against a fixture timeline."""

    def __init__(
        self,
        case_id: str,
        events: list,  # list[ReplayEvent] sorted by ts
        trace: TracePort,
        clock: 'FixtureClockPort',  # from adapters_fixture
        budget: BudgetPort,
        notify: NotifyPort,
        seed_amount: Decimal,
        K: int = 5,
        exit_policy=None,
        labels=None,
    ):
        self.case_id = case_id
        self.events = sorted(events, key=lambda e: e.ts)
        self.trace = trace
        self.clock = clock
        self.budget = budget
        self.notify = notify
        self.seed_amount = seed_amount
        self.K = K
        self.exit_policy = exit_policy
        self.labels = labels
        self._plans: list = []
        self._first_action_ts: Optional[datetime] = None
        self._start_ts: Optional[datetime] = None

    async def run(self, baseline: str = 'FOT') -> ReplayResult:
        """Replay all events and compute plan at each step."""
        self._start_ts = self.events[0].ts if self.events else self.clock.now()
        act_now_triggered = False

        for event in self.events:
            # Advance simulated clock to event time
            if hasattr(self.clock, 'set_time'):
                self.clock.set_time(event.ts)

            # Recompute mass map + plan at each event
            graph = self.trace.get_case_graph(self.case_id)
            t = self.clock.now()
            mass_map = build_mass_map(self.case_id, t, graph, self.seed_amount)
            levers = get_lever_options(mass_map)
            plan = greedy_plan(self.case_id, levers, self.K)
            self._plans.append(plan)

            if self._first_action_ts is None and plan.actions:
                self._first_action_ts = t

            # VOI: check if we should act now
            if plan.ev_total > 0:
                unresolved = mass_map.unresolved_total
                best_voi = voi_priority(
                    '_unresolved', unresolved,
                    p_resolve_to_lever=0.5,  # prior
                    lever_gain=plan.ev_total,
                    api_cost=1,
                )
                if should_act_now(plan.ev_total, best_voi, expected_delay_seconds=300):
                    act_now_triggered = True
                    await self.notify.emit(self.case_id, 'act_now', {
                        'ev_total': float(plan.ev_total),
                        'illustrative': True,
                    })

            self.budget.charge(1)

        final_plan = self._plans[-1] if self._plans else None
        time_to_action = None
        if self._first_action_ts and self._start_ts:
            time_to_action = (self._first_action_ts - self._start_ts).total_seconds() / 3600

        return ReplayResult(
            case_id=self.case_id,
            baseline_name=baseline,
            time_to_first_action_hours=time_to_action,
            api_calls_used=self.budget.calls_used(self.case_id),
            plans_computed=len(self._plans),
            final_ev_total=final_plan.ev_total if final_plan else Decimal('0'),
            act_now_triggered=act_now_triggered,
        )
