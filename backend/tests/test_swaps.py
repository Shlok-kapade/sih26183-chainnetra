from datetime import datetime, timezone
from decimal import Decimal

from app.ingest.normalize import Transfer
from app.trace.swaps import SwapDetector


def test_swap_detector():
    detector = SwapDetector(["router1"])
    transfers = [
        Transfer(chain="ETH", tx_hash="tx1", ts=datetime.now(timezone.utc), from_addr="user", to_addr="router1", asset="ETH", amount=Decimal("1"), kind="native", block=1),
        Transfer(chain="ETH", tx_hash="tx1", ts=datetime.now(timezone.utc), from_addr="router1", to_addr="user", asset="USDC", amount=Decimal("2000"), kind="token", block=1)
    ]
    swaps = detector.detect_swaps(transfers)
    assert len(swaps) == 1
    assert swaps[0]["tx_hash"] == "tx1"
