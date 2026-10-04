from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from app.addon.ports import TransferPort, LabelPort, TracePort, BudgetPort
from app.addon.cohorts.detect import detect_scatter, ScatterEvent
from app.addon.cohorts.sample_vote import sample_vote
from app.addon.cohorts.verify import verify_collectors
from app.addon.cohorts.score import score_collectors, ConvergenceResult

@dataclass
class CohortReport:
    case_id: str
    analysis_type: str
    origin_address: str
    analysis_time_ms: int
    notes: List[str]
    scatter_event: Optional[ScatterEvent]
    collectors: List[ConvergenceResult]
    unaccounted_mass: float
    api_calls_used: int
    estimated_not_verified: bool

async def process_cohort(
    case_id: str,
    chain: str,
    origin: str,
    asset: str,
    since: Optional[datetime],
    until: Optional[datetime],
    transfers: TransferPort,
    labels: LabelPort,
    trace: TracePort,
    budget: BudgetPort,
    k_scatter: int = 50,
    m_sample: int = 300,
    k_verify: int = 10
) -> CohortReport:
    start_calls = getattr(transfers, 'call_count', 0)
    
    # 1. Detect
    scatter = await detect_scatter(transfers, chain, origin, asset, since, until, k_scatter=k_scatter)
    if not scatter:
        end_calls = getattr(transfers, 'call_count', 0)
        return CohortReport(
            case_id=case_id,
            analysis_type="scatter_gather",
            origin_address=origin,
            analysis_time_ms=0,
            notes=["No scatter event detected."],
            scatter_event=None,
            collectors=[],
            unaccounted_mass=1.0,
            api_calls_used=end_calls - start_calls,
            estimated_not_verified=False
        )
        
    # 2. Check Dust Dispersal
    if scatter.kind == 'dust_dispersal':
        end_calls = getattr(transfers, 'call_count', 0)
        return CohortReport(
            case_id=case_id,
            analysis_type="scatter_gather",
            origin_address=origin,
            analysis_time_ms=0,
            notes=["Dust dispersal detected, skipping convergence."],
            scatter_event=scatter,
            collectors=[],
            unaccounted_mass=1.0,
            api_calls_used=end_calls - start_calls,
            estimated_not_verified=False
        )
        
    # 3. Sample & Vote
    candidates = await sample_vote(scatter, transfers, labels, chain, asset, m=m_sample)
    
    # 4. Verify
    verifications = await verify_collectors(scatter, candidates, transfers, labels, chain, asset, k=k_verify)
    
    # 5. Score
    collectors = score_collectors(verifications, verified=True)
    
    # 6. Unaccounted mass & Expansion
    total_coverage = sum(c.coverage_value for c in collectors if c.tier in ('CONVERGENCE_CONFIRMED', 'CONVERGENCE_PROBABLE'))
    unaccounted_mass = max(0.0, 1.0 - total_coverage)
    
    for c in collectors:
        if c.tier == 'CONVERGENCE_CONFIRMED':
            # use destination directly
            await trace.enqueue_expand(case_id, c.collector, priority=1.0, budget=100)
            
    end_calls = getattr(transfers, 'call_count', 0)
    
    return CohortReport(
        case_id=case_id,
        analysis_type="scatter_gather",
        origin_address=origin,
        analysis_time_ms=0,
        notes=[],
        scatter_event=scatter,
        collectors=collectors,
        unaccounted_mass=unaccounted_mass,
        api_calls_used=end_calls - start_calls,
        estimated_not_verified=False
    )
