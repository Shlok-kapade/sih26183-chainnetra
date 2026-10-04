from typing import Dict, List

from app.ingest.normalize import Transfer


class SwapDetector:
    def __init__(self, dex_routers: List[str]):
        self.dex_routers = set(dex_routers)

    def detect_swaps(self, transfers: List[Transfer]) -> List[Dict]:
        swaps = []
        # Group by tx_hash
        tx_groups = {}
        for t in transfers:
            if t.tx_hash not in tx_groups:
                tx_groups[t.tx_hash] = []
            tx_groups[t.tx_hash].append(t)

        for tx, tx_transfers in tx_groups.items():
            # A simplistic heuristic: if transfer involves a router, and multiple assets are swapped
            routers_in_tx = [t for t in tx_transfers if t.to_addr in self.dex_routers or t.from_addr in self.dex_routers]
            if len(routers_in_tx) >= 2:
                # Potential swap
                swaps.append({"tx_hash": tx, "transfers": tx_transfers})

        return swaps
