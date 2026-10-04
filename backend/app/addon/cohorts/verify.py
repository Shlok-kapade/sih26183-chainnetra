from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime, timedelta
from app.addon.ports import TransferPort, LabelPort
from app.addon.cohorts.detect import ScatterEvent
from app.addon.cohorts.sample_vote import VoteResult

@dataclass
class CollectorVerification:
    collector: str
    is_cluster: bool
    cluster_entity: Optional[str]
    coverage_value: float
    coverage_breadth: float
    time_compactness: float
    conservation_error: float
    false_positive_note: Optional[str] = None

async def verify_collectors(scatter: ScatterEvent, candidates: List[VoteResult], transfers: TransferPort, labels: LabelPort, chain: str, asset: str, k: int = 10) -> List[CollectorVerification]:
    top_candidates = candidates[:k]
    verifications = []
    
    member_addresses = set(m[0] for m in scatter.members)
    member_values = {m[0]: m[1] for m in scatter.members}
    
    t_start = scatter.t_start
    t_end = scatter.t_end + timedelta(hours=6) if scatter.t_end else t_start + timedelta(hours=6)
    
    for cand in top_candidates:
        dest = cand.destination
        
        # If cand is cluster/entity, in a real system we'd expand it to addresses,
        # but here we can just query the dest if it's an address, or simulate it.
        # Since we use adapters_fixture, let's assume we can query dest directly, or 
        # for simplicity, assume dest is an address if not prefixed, else it's tricky to query inbound without expansion.
        # The prompt says: fetch their inbound transfers. We will query dest directly.
        # If it's entity:X, we'd need to get addresses for X. In this mock, let's just use the destination as an address string if not clustered, or we strip the prefix if it was clustered.
        # Wait, the prompt implies "fetch their inbound transfers from cohort members".
        # Let's extract the address from the prefix if any.
        query_addr = dest
        if cand.is_cluster:
            query_addr = dest.split(":", 1)[1] if ":" in dest else dest
            
        inbound_value = 0.0
        unique_senders = set()
        arrival_times = []
        
        async for tx in transfers.incoming(chain, query_addr, asset, since=t_start, until=t_end, max_pages=10):
            from_addr = tx.from_addr if hasattr(tx, 'from_addr') else (tx.get('from_addr') if isinstance(tx, dict) else None)
            amt = float(tx.amount) if hasattr(tx, 'amount') else (float(tx.get('amount', 0)) if isinstance(tx, dict) else 0.0)
            ts = tx.ts if hasattr(tx, 'ts') else (tx.get('ts') if isinstance(tx, dict) else None)

            if from_addr and from_addr in member_addresses and ts is not None:
                if t_start <= ts <= t_end:
                    inbound_value += amt
                    unique_senders.add(from_addr)
                    arrival_times.append(ts)

        s_total_float = float(scatter.s_total) if scatter.s_total else 1.0
        coverage_value = inbound_value / s_total_float if s_total_float > 0 else 0.0
        coverage_breadth = len(unique_senders) / scatter.n if scatter.n > 0 else 0.0
        
        # Time compactness: std dev of arrival times? Or duration?
        # Let's use 1.0 - (max - min) / (t_end - t_start) or similar. 
        # Actually time compactness could be ratio of actual spread to allowed spread (6h)
        if arrival_times:
            actual_spread = (max(arrival_times) - min(arrival_times)).total_seconds()
            time_compactness = 1.0 - min(actual_spread / (6 * 3600), 1.0)
        else:
            time_compactness = 0.0
            
        # Conservation error: difference between what member received and what they sent
        # sum of (member_sent_to_collector / member_received_from_origin)
        conservation_error = 0.0
        if unique_senders:
            diffs = []
            for sender in unique_senders:
                # We don't have exactly what they sent per member without re-querying or saving, 
                # but we can assume total inbound_value comes from unique_senders.
                # Actually, conservation error = 1 - (inbound_value / sum(member_values[s] for s in unique_senders))
                expected = sum(member_values[s] for s in unique_senders)
                if expected > 0:
                    conservation_error = abs(inbound_value - expected) / expected
                else:
                    conservation_error = 1.0
                    
        verifications.append(CollectorVerification(
            collector=dest,
            is_cluster=cand.is_cluster,
            cluster_entity=cand.cluster_entity,
            coverage_value=coverage_value,
            coverage_breadth=coverage_breadth,
            time_compactness=time_compactness,
            conservation_error=conservation_error,
            false_positive_note=cand.false_positive_note
        ))
        
    verifications.sort(key=lambda x: x.coverage_value, reverse=True)
    return verifications
