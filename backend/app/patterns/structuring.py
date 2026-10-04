from collections import defaultdict
from decimal import Decimal

from app.ingest.normalize import Transfer


class StructuringDetector:
    def __init__(self, min_txs: int = 3, tolerance: Decimal = Decimal('0.05')):
        self.min_txs = min_txs
        self.tolerance = tolerance

    def detect(self, transfers: list[Transfer]) -> list[dict]:
        results = []

        txs_by_addr = defaultdict(list)
        for tx in transfers:
            txs_by_addr[tx.from_addr].append(tx)

        for addr, txs in txs_by_addr.items():
            if len(txs) < self.min_txs:
                continue

            sorted_by_amt = sorted(txs, key=lambda t: t.amount)

            i = 0
            while i <= len(sorted_by_amt) - self.min_txs:
                window_txs = [sorted_by_amt[i]]
                base_amt = sorted_by_amt[i].amount

                j = i + 1
                while j < len(sorted_by_amt):
                    if base_amt > 0:
                        diff = sorted_by_amt[j].amount - base_amt
                        if diff / base_amt <= self.tolerance:
                            window_txs.append(sorted_by_amt[j])
                        else:
                            break
                    else:
                        if sorted_by_amt[j].amount == 0:
                            window_txs.append(sorted_by_amt[j])
                        else:
                            break
                    j += 1

                if len(window_txs) >= self.min_txs:
                    score = min(1.0, len(window_txs) / (self.min_txs * 2.0))
                    results.append({
                        "pattern": "structuring",
                        "score": round(score, 2),
                        "evidence_tx_refs": [t.tx_hash for t in window_txs],
                        "false_positive_note": "Could be recurring payments or DCA strategy"
                    })
                    i = j
                else:
                    i += 1

        return results
