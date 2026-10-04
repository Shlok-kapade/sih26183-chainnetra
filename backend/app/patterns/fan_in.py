from collections import defaultdict
from datetime import timedelta

from app.ingest.normalize import Transfer


class FanInDetector:
    def __init__(self, min_senders: int = 5, time_window: timedelta = timedelta(hours=1)):
        self.min_senders = min_senders
        self.time_window = time_window

    def detect(self, transfers: list[Transfer]) -> list[dict]:
        sorted_txs = sorted(transfers, key=lambda t: t.ts)
        results = []

        to_groups = defaultdict(list)
        for tx in sorted_txs:
            to_groups[tx.to_addr].append(tx)

        for recipient, txs in to_groups.items():
            i = 0
            while i < len(txs):
                start_tx = txs[i]
                end_time = start_tx.ts + self.time_window
                window_txs = []
                senders = set()

                j = i
                while j < len(txs) and txs[j].ts <= end_time:
                    window_txs.append(txs[j])
                    senders.add(txs[j].from_addr)
                    j += 1

                if len(senders) >= self.min_senders:
                    dur = max(timedelta(seconds=1), window_txs[-1].ts - window_txs[0].ts)
                    compression = max(0.0, 1.0 - (dur / self.time_window))
                    score = min(1.0, (len(senders) / (self.min_senders * 2.0)) * 0.5 + compression * 0.5)
                    results.append({
                        "pattern": "fan_in",
                        "score": round(score, 2),
                        "evidence_tx_refs": [t.tx_hash for t in window_txs],
                        "false_positive_note": "Could be exchange deposit collection or payment aggregator"
                    })
                    i = j
                else:
                    i += 1

        return results
