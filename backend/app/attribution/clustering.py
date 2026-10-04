from collections import defaultdict
from typing import Dict, List, Tuple

from app.ingest.normalize import Transfer


class DARCluster:
    def __init__(self, tau_seconds: int = 86400 * 7):
        self.tau_seconds = tau_seconds

    def find_deposit_addresses(self, transfers: List[Transfer], known_exchange_addresses: Dict[str, str]) -> List[Tuple[str, str]]:
        # Map address -> list of incoming transfers
        inflows = defaultdict(list)
        # Map address -> list of outgoing transfers
        outflows = defaultdict(list)

        for t in transfers:
            inflows[t.to_addr].append(t)
            outflows[t.from_addr].append(t)

        deposit_addresses = []

        for addr in inflows.keys():
            if addr in known_exchange_addresses:
                continue

            unique_senders = {t.from_addr for t in inflows[addr]}
            if len(unique_senders) < 5:
                continue

            total_in = sum(t.amount for t in inflows[addr])
            if total_in == 0:
                continue

            # find forwards to exchange
            forwarded_to_exchange = 0
            target_exchange = None

            for out_t in outflows.get(addr, []):
                if out_t.to_addr in known_exchange_addresses:
                    target_exchange = known_exchange_addresses[out_t.to_addr]
                    forwarded_to_exchange += out_t.amount

            if forwarded_to_exchange / total_in >= 0.8:
                if target_exchange:
                    deposit_addresses.append((addr, target_exchange))

        return deposit_addresses

class BTCCoSpendCluster:
    def __init__(self):
        self.parent = {}

    def find(self, i):
        if self.parent[i] == i:
            return i
        self.parent[i] = self.find(self.parent[i])
        return self.parent[i]

    def union(self, i, j):
        root_i = self.find(i)
        root_j = self.find(j)
        if root_i != root_j:
            self.parent[root_i] = root_j

    def cluster(self, transfers: List[Transfer]) -> Dict[str, str]:
        # transfers represent individual inputs/outputs
        # We need to group them by tx_hash
        tx_inputs = defaultdict(set)
        tx_outputs = defaultdict(list)

        for t in transfers:
            if t.from_addr: # Assuming from_addr is not empty for inputs
                tx_inputs[t.tx_hash].add(t.from_addr)
            if t.to_addr:
                tx_outputs[t.tx_hash].append(t.amount)

        for inputs in tx_inputs.values():
            for addr in inputs:
                if addr not in self.parent:
                    self.parent[addr] = addr

        for tx_hash, inputs in tx_inputs.items():
            inputs_list = list(inputs)
            if len(inputs_list) > 1:
                # CoinJoin check: many equal outputs
                outputs = tx_outputs.get(tx_hash, [])
                if len(outputs) >= 5 and len(set(outputs)) == 1:
                    continue # Skip CoinJoin

                first = inputs_list[0]
                for other in inputs_list[1:]:
                    self.union(first, other)

        clusters = {}
        for addr in self.parent.keys():
            clusters[addr] = str(self.find(addr))

        return clusters
