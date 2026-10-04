import statistics
from dataclasses import dataclass
from typing import List, Tuple, Optional
from datetime import datetime
from app.addon.ports import TransferPort

@dataclass
class ScatterEvent:
    origin: str
    n: int
    s_total: float
    amount_median: float
    amount_cv: float
    t_start: datetime
    t_end: datetime
    layer: int
    truncated: bool
    kind: str
    members: List[Tuple[str, float, datetime]]  # (addr, value, ts)
    false_positive_note: Optional[str] = None

async def detect_scatter(transfers: TransferPort, chain: str, origin: str, asset: str, since: Optional[datetime], until: Optional[datetime], k_scatter: int = 50, n_max: int = 200_000, layer: int = 0) -> Optional[ScatterEvent]:
    members = []
    s_total = 0.0
    t_start = None
    t_end = None
    truncated = False
    
    count = 0
    async for item in transfers.outgoing(chain, origin, asset, since, until, max_pages=n_max // 200 + 1):
        # item could be a page or a single transfer
        batch = item if isinstance(item, list) else [item]
        for t in batch:
            if count >= n_max:
                truncated = True
                break
            
            # handle dict or object
            to_addr = t.to_addr if hasattr(t, 'to_addr') else t.get('to_addr')
            amount = t.amount if hasattr(t, 'amount') else t.get('amount')
            ts = t.ts if hasattr(t, 'ts') else t.get('ts')
            
            members.append((to_addr, amount, ts))
            s_total += amount
            
            if t_start is None or ts < t_start:
                t_start = ts
            if t_end is None or ts > t_end:
                t_end = ts
                
            count += 1
            
        if truncated:
            break
            
    # filter out duplicates if needed, but for scatter we assume distinct recipients
    unique_recipients = set(m[0] for m in members)
    if len(unique_recipients) < k_scatter:
        return None
        
    amounts = [m[1] for m in members]
    amount_median = statistics.median(amounts) if amounts else 0.0
    mean_amount = statistics.mean(amounts) if amounts else 0.0
    stdev_amount = statistics.stdev(amounts) if len(amounts) > 1 else 0.0
    amount_cv = (stdev_amount / mean_amount) if mean_amount > 0 else 0.0
    
    # Dust dispersal check
    kind = 'scatter'
    fp_note = None
    if all(a < 1.0 for a in amounts):
        kind = 'dust_dispersal'
        fp_note = 'All transfer amounts are tiny, indicating potential dust attack or airdrop farming'
        
    return ScatterEvent(
        origin=origin,
        n=len(unique_recipients),
        s_total=s_total,
        amount_median=amount_median,
        amount_cv=amount_cv,
        t_start=t_start,
        t_end=t_end,
        layer=layer,
        truncated=truncated,
        kind=kind,
        members=members,
        false_positive_note=fp_note
    )
