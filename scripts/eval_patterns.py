import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))
from synth_laundering import (
    generate_benign_market_maker,
    generate_benign_processor,
    generate_dormancy_burst,
    generate_exchange_deposit_funnel,
    generate_layering,
    generate_peel_chain,
    generate_rapid_forwarding,
    generate_round_trip,
    generate_structuring,
)

from app.patterns.registry import PatternRegistry


def evaluate():
    patterns = {
        "Layering (Fan Out/In)": generate_layering(),
        "Peel Chain": generate_peel_chain(),
        "Rapid Forwarding": generate_rapid_forwarding(),
        "Dormancy Burst": generate_dormancy_burst(),
        "Structuring": generate_structuring(),
        "Round Trip": generate_round_trip(),
        "Benign Processor": generate_benign_processor(),
        "Exchange Deposit": generate_exchange_deposit_funnel(),
        "Benign Market Maker": generate_benign_market_maker()
    }

    registry = PatternRegistry()

    for name, txs in patterns.items():
        print(f"--- Evaluating {name} ---")
        results = registry.detect_all(txs)
        if not results:
            print("No patterns detected.")
        for r in results:
            print(f"Detected: {r['pattern']} (score: {r['score']}) - Note: {r['false_positive_note']}")

if __name__ == "__main__":
    evaluate()
