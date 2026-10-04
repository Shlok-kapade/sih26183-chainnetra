from collections import defaultdict
from app.ingest.normalize import Transfer

class RoundTripDetector:
    def __init__(self, min_hops: int = 2):
        self.min_hops = min_hops

    def detect(self, transfers: list[Transfer]) -> list[dict]:
        results = []
        
        adj = defaultdict(list)
        for tx in transfers:
            adj[tx.from_addr].append(tx)
            
        visited_paths = set()
        
        for start_node in list(adj.keys()):
            stack = [(start_node, [start_node], [])]
            
            while stack:
                curr, path_nodes, path_txs = stack.pop()
                
                for tx in adj[curr]:
                    if path_txs and tx.ts < path_txs[-1].ts:
                        continue
                        
                    next_node = tx.to_addr
                    new_path_nodes = path_nodes + [next_node]
                    new_path_txs = path_txs + [tx]
                    
                    if next_node == start_node:
                        if len(new_path_txs) >= self.min_hops:
                            tx_refs = tuple([t.tx_hash for t in new_path_txs])
                            if tx_refs not in visited_paths:
                                visited_paths.add(tx_refs)
                                score = 0.8
                                results.append({
                                    "pattern": "round_trip",
                                    "score": score,
                                    "evidence_tx_refs": list(tx_refs),
                                    "false_positive_note": "Could be self-transfer for wallet management"
                                })
                    elif next_node not in path_nodes:
                        stack.append((next_node, new_path_nodes, new_path_txs))
                        
        return results
