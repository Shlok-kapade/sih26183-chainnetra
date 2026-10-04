from collections import defaultdict
from datetime import timedelta

from app.ingest.normalize import Transfer


class FanOutDetector:
    def __init__(self, min_recipients: int = 5, time_window: timedelta = timedelta(hours=1)):
        self.min_recipients = min_recipients
        self.time_window = time_window

    def detect(self, transfers: list[Transfer]) -> list[dict]:
        sorted_txs = sorted(transfers, key=lambda t: t.ts)
        results = []

        from_groups = defaultdict(list)
        for tx in sorted_txs:
            from_groups[tx.from_addr].append(tx)

        for sender, txs in from_groups.items():
            i = 0
            while i < len(txs):
                start_tx = txs[i]
                end_time = start_tx.ts + self.time_window
                window_txs = []
                recipients = set()

                j = i
                while j < len(txs) and txs[j].ts <= end_time:
                    window_txs.append(txs[j])
                    recipients.add(txs[j].to_addr)
                    j += 1

                if len(recipients) >= self.min_recipients:
                    dur = max(timedelta(seconds=1), window_txs[-1].ts - window_txs[0].ts)
                    compression = max(0.0, 1.0 - (dur / self.time_window))
                    score = min(1.0, (len(recipients) / (self.min_recipients * 2.0)) * 0.5 + compression * 0.5)
                    results.append({
                        "pattern": "fan_out",
                        "score": round(score, 2),
                        "evidence_tx_refs": [t.tx_hash for t in window_txs],
                        "false_positive_note": "Could be payment processor, exchange withdrawal batch, or salary distribution"
                    })
                    i = j
                else:
                    i += 1

        return results
