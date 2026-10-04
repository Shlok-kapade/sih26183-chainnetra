from typing import List

from app.ingest.normalize import Transfer


class BridgeDetector:
    def __init__(self, bridge_contracts: List[str]):
        self.bridge_contracts = set(bridge_contracts)

    def check_bridges(self, transfers: List[Transfer]) -> List[str]:
        # returns list of tx hashes that sent to a bridge
        bridge_exits = []
        for t in transfers:
            if t.to_addr in self.bridge_contracts:
                bridge_exits.append(t.tx_hash)
        return bridge_exits
