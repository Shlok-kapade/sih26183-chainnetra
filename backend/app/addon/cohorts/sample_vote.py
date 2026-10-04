import math
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
from datetime import datetime
from app.addon.ports import TransferPort, LabelPort
from app.addon.cohorts.detect import ScatterEvent

@dataclass
class VoteResult:
    destination: str
    votes: int
    value_est: float
    is_cluster: bool
    cluster_entity: Optional[str]
    false_positive_note: Optional[str] = None

async def sample_vote(scatter: ScatterEvent, transfers: TransferPort, labels: LabelPort, chain: str, asset: str, m: int = 300) -> List[VoteResult]:
    # Stratified sampling by amount quantile
    sorted_members = sorted(scatter.members, key=lambda x: x[1])
    n = len(sorted_members)
    
    # Take up to m members. If n <= m, take all
    sample = []
    if n <= m:
        sample = sorted_members
    else:
        # 4 strata
        strata_count = 4
        items_per_stratum_pop = n // strata_count
        items_per_stratum_sample = m // strata_count
        
        for i in range(strata_count):
            start = i * items_per_stratum_pop
            end = n if i == strata_count - 1 else (i + 1) * items_per_stratum_pop
            stratum = sorted_members[start:end]
            
            # just take evenly spaced within stratum or first few
            # for simplicity, take evenly spaced
            step = max(1, len(stratum) // items_per_stratum_sample)
            sample.extend(stratum[::step][:items_per_stratum_sample])
            
        # fill remainder if needed
        while len(sample) < m:
            sample.append(sorted_members[len(sample) % n])
    
    votes_by_dest: Dict[str, int] = {}
    value_by_dest: Dict[str, float] = {}
    
    # we consider destination by cluster or entity if available, else address
    dest_to_entity: Dict[str, str] = {}
    dest_is_cluster: Dict[str, bool] = {}
    
    for member_addr, member_value, member_ts in sample:
        # fetch outgoing transfers
        # we give it a window [member_ts, member_ts + some slack] 
        # but to keep it simple, just get next few transfers
        # we will use max_pages=1 
        async for item in transfers.outgoing(chain, member_addr, asset, since=member_ts, until=None, max_pages=1):
            batch = item if isinstance(item, list) else [item]
            
            # just take first destination to simplify? Or aggregate all?
            # aggregate all in the batch
            # usually it's the first one that matters
            if not batch: continue
            
            for t in batch:
                to_addr = t.to_addr if hasattr(t, 'to_addr') else t.get('to_addr')
                amt = t.amount if hasattr(t, 'amount') else t.get('amount')
                
                # Check entity
                ent = labels.entity_of(chain, to_addr)
                cluster = labels.cluster_of(chain, to_addr)
                
                dest_key = to_addr
                is_clust = False
                ent_name = None
                
                if ent:
                    dest_key = f"entity:{ent.name}"
                    is_clust = True
                    ent_name = ent.name
                elif cluster:
                    dest_key = f"cluster:{cluster.cluster_id}"
                    is_clust = True
                    ent_name = cluster.entity
                
                dest_to_entity[dest_key] = ent_name
                dest_is_cluster[dest_key] = is_clust
                
                votes_by_dest[dest_key] = votes_by_dest.get(dest_key, 0) + 1
                value_by_dest[dest_key] = value_by_dest.get(dest_key, 0.0) + amt
            
            # break after first page for a member to save API calls
            break
            
    # sort by votes
    results = []
    
    # sample expansion factor
    expansion_factor = n / len(sample) if sample else 1.0
    
    for dest, votes in sorted(votes_by_dest.items(), key=lambda x: x[1], reverse=True):
        value_est = value_by_dest[dest] * expansion_factor
        results.append(VoteResult(
            destination=dest,
            votes=votes,
            value_est=value_est,
            is_cluster=dest_is_cluster[dest],
            cluster_entity=dest_to_entity[dest],
            false_positive_note=None
        ))
        
    return results
