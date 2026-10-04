from collections import defaultdict
from datetime import timedelta

from app.ingest.normalize import Transfer


class DormancyBurstDetector:
    def __init__(self, min_dormant_days: int = 30, max_burst_hours: int = 24, min_burst_txs: int = 3):
        self.min_dormant_days = timedelta(days=min_dormant_days)
        self.max_burst_hours = timedelta(hours=max_burst_hours)
        self.min_burst_txs = min_burst_txs

    def detect(self, transfers: list[Transfer]) -> list[dict]:
        sorted_txs = sorted(transfers, key=lambda t: t.ts)

        txs_by_addr = defaultdict(lambda: {"in": [], "out": []})
        for tx in sorted_txs:
            txs_by_addr[tx.from_addr]["out"].append(tx)
            txs_by_addr[tx.to_addr]["in"].append(tx)

        results = []

        for addr, data in txs_by_addr.items():
            in_txs = data["in"]
            out_txs = data["out"]
            if not in_txs or not out_txs:
                continue

            i = 0
            while i < len(out_txs):
                first_out = out_txs[i]

                last_active = None
                for t in reversed(in_txs):
                    if t.ts < first_out.ts:
                        last_active = t.ts
                        break

                if i > 0:
                    prev_out_ts = out_txs[i-1].ts
                    if last_active is None or prev_out_ts > last_active:
                        last_active = prev_out_ts

                if last_active and (first_out.ts - last_active) >= self.min_dormant_days:
                    end_burst_time = first_out.ts + self.max_burst_hours
                    burst_txs = []
                    j = i
                    while j < len(out_txs) and out_txs[j].ts <= end_burst_time:
                        burst_txs.append(out_txs[j])
                        j += 1

                    if len(burst_txs) >= self.min_burst_txs:
                        dormant_days = (first_out.ts - last_active).days
                        score = min(1.0, (dormant_days / max(1, self.min_dormant_days.days * 2.0)) * 0.5 + (len(burst_txs) / (self.min_burst_txs * 2.0)) * 0.5)

                        results.append({
                            "pattern": "dormancy_burst",
                            "score": round(score, 2),
                            "evidence_tx_refs": [t.tx_hash for t in burst_txs],
                            "false_positive_note": "Could be reactivated legitimate wallet"
                        })
                        i = j
                        continue

                i += 1

        return results
