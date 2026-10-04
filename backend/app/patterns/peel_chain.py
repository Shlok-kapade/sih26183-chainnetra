from collections import defaultdict

from app.ingest.normalize import Transfer


class PeelChainDetector:
    def __init__(self, min_peels: int = 3):
        self.min_peels = min_peels

    def detect(self, transfers: list[Transfer]) -> list[dict]:
        sorted_txs = sorted(transfers, key=lambda t: t.ts)

        groups = defaultdict(list)
        for tx in sorted_txs:
            groups[(tx.from_addr, tx.ts)].append(tx)

        peels_by_from = {}
        for (frm, ts), txs in groups.items():
            if len(txs) == 2:
                t1, t2 = txs[0], txs[1]
                if t1.amount > t2.amount:
                    peels_by_from[frm] = {"remainder": t1, "peeled": t2}
                elif t2.amount > t1.amount:
                    peels_by_from[frm] = {"remainder": t2, "peeled": t1}

        results = []
        visited = set()

        # To find only maximal chains, we should find roots (nodes with no incoming remainder)
        has_incoming = set()
        for p in peels_by_from.values():
            has_incoming.add(p["remainder"].to_addr)

        for frm, peel in peels_by_from.items():
            if frm not in has_incoming and frm not in visited:
                chain = []
                curr = frm
                while curr in peels_by_from:
                    p = peels_by_from[curr]
                    chain.append(p)
                    visited.add(curr)
                    curr = p["remainder"].to_addr

                if len(chain) >= self.min_peels:
                    refs = []
                    for p in chain:
                        refs.append(p["remainder"].tx_hash)
                        refs.append(p["peeled"].tx_hash)

                    score = min(1.0, len(chain) / (self.min_peels * 2.0))
                    results.append({
                        "pattern": "peel_chain",
                        "score": round(score, 2),
                        "evidence_tx_refs": refs,
                        "false_positive_note": "Could be change addresses in normal Bitcoin transactions"
                    })

        return results
