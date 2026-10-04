from datetime import timedelta
from collections import defaultdict
from app.ingest.normalize import Transfer

class RapidForwardingDetector:
    def __init__(self, max_dwell_time: timedelta = timedelta(minutes=10), min_hops: int = 3):
        self.max_dwell_time = max_dwell_time
        self.min_hops = min_hops

    def detect(self, transfers: list[Transfer]) -> list[dict]:
        sorted_txs = sorted(transfers, key=lambda t: t.ts)
        
        tx_by_sender = defaultdict(list)
        for tx in sorted_txs:
            tx_by_sender[tx.from_addr].append(tx)
            
        adj = defaultdict(list)
        has_incoming = set()
        for tx in sorted_txs:
            for next_tx in tx_by_sender[tx.to_addr]:
                dwell = next_tx.ts - tx.ts
                if timedelta(0) <= dwell <= self.max_dwell_time:
                    adj[tx.tx_hash].append(next_tx.tx_hash)
                    has_incoming.add(next_tx.tx_hash)
                    
        def dfs(tx_hash, path):
            best_path = path
            for nxt in adj[tx_hash]:
                if nxt not in path:
                    sub_path = dfs(nxt, path + [nxt])
                    if len(sub_path) > len(best_path):
                        best_path = sub_path
            return best_path
            
        results = []
        for tx in sorted_txs:
            if tx.tx_hash not in has_incoming and tx.tx_hash in adj:
                path = dfs(tx.tx_hash, [tx.tx_hash])
                if len(path) >= self.min_hops:
                    # Score by length of chain and median dwell time
                    dwells = []
                    for i in range(len(path)-1):
                        t1 = next(t for t in sorted_txs if t.tx_hash == path[i]).ts
                        t2 = next(t for t in sorted_txs if t.tx_hash == path[i+1]).ts
                        dwells.append((t2 - t1).total_seconds())
                    
                    if dwells:
                        median_dwell = sorted(dwells)[len(dwells)//2]
                        # lower dwell = higher score
                        time_score = max(0.0, 1.0 - (median_dwell / self.max_dwell_time.total_seconds()))
                    else:
                        time_score = 1.0
                        
                    len_score = min(1.0, len(path) / (self.min_hops * 2.0))
                    score = (len_score * 0.5) + (time_score * 0.5)
                    
                    results.append({
                        "pattern": "rapid_forwarding",
                        "score": round(score, 2),
                        "evidence_tx_refs": path,
                        "false_positive_note": "Could be automated sweep or relay service"
                    })
                    
        return results
