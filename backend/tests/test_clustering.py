"""Tests for DAR and BTC co-spend clustering (Phase 3)."""
from datetime import datetime, timezone
from decimal import Decimal

from app.attribution.clustering import BTCCoSpendCluster, DARCluster
from app.ingest.normalize import Transfer


def _make_transfer(
    from_addr: str,
    to_addr: str,
    amount: Decimal = Decimal("100"),
    tx_hash: str | None = None,
    chain: str = "ETH",
    block: int = 1000,
) -> Transfer:
    return Transfer(
        chain=chain,
        tx_hash=tx_hash or f"tx_{from_addr}_{to_addr}",
        ts=datetime.now(timezone.utc),
        from_addr=from_addr,
        to_addr=to_addr,
        asset="ETH",
        amount=amount,
        kind="native",
        block=block,
    )


class TestDARCluster:
    """Deposit-Address-Reuse heuristic tests."""

    def test_dar_simple_detection(self):
        """Address forwarding >=80% from >=5 unique senders to known exchange → deposit."""
        exchange_addr = "0xExchange"
        deposit_addr = "0xDeposit"
        known = {exchange_addr: "Binance"}

        # 6 unique senders → deposit_addr
        transfers = [
            _make_transfer(f"0xSender{i}", deposit_addr, Decimal("10"))
            for i in range(6)
        ]
        # deposit_addr → exchange (90% of inflow)
        transfers.append(_make_transfer(deposit_addr, exchange_addr, Decimal("54")))

        dar = DARCluster()
        result = dar.find_deposit_addresses(transfers, known)

        assert len(result) == 1
        addr, entity = result[0]
        assert addr == deposit_addr
        assert entity == "Binance"

    def test_dar_below_sender_threshold(self):
        """Only 2 unique senders → not detected as deposit address."""
        exchange_addr = "0xExchange"
        deposit_addr = "0xDeposit2"
        known = {exchange_addr: "Binance"}

        transfers = [
            _make_transfer(f"0xSender{i}", deposit_addr, Decimal("10"))
            for i in range(2)  # only 2 senders
        ]
        transfers.append(_make_transfer(deposit_addr, exchange_addr, Decimal("18")))

        dar = DARCluster()
        result = dar.find_deposit_addresses(transfers, known)
        assert result == []

    def test_dar_below_forward_ratio(self):
        """Forwards <80% to exchange → not a deposit address."""
        exchange_addr = "0xExchange"
        deposit_addr = "0xDeposit3"
        known = {exchange_addr: "Binance"}

        transfers = [
            _make_transfer(f"0xSender{i}", deposit_addr, Decimal("10"))
            for i in range(6)
        ]
        # Only forwards 30% (18 out of 60)
        transfers.append(_make_transfer(deposit_addr, exchange_addr, Decimal("18")))
        transfers.append(_make_transfer(deposit_addr, "0xOther", Decimal("42")))

        dar = DARCluster()
        result = dar.find_deposit_addresses(transfers, known)
        assert result == []

    def test_dar_skips_known_exchange_address(self):
        """Known exchange addresses are skipped (not classified as deposit)."""
        exchange_addr = "0xExchange"
        known = {exchange_addr: "Binance"}

        # Even if exchange_addr receives from many senders, it's excluded
        transfers = [
            _make_transfer(f"0xSender{i}", exchange_addr, Decimal("10"))
            for i in range(8)
        ]

        dar = DARCluster()
        result = dar.find_deposit_addresses(transfers, known)
        assert result == []


class TestBTCCoSpendCluster:
    """BTC common-input-ownership heuristic tests."""

    def test_cospend_clusters_shared_inputs(self):
        """Two addresses used as inputs in same tx → same cluster."""
        addr_a = "1AddrA"
        addr_b = "1AddrB"
        dest = "1Dest"

        transfers = [
            _make_transfer(addr_a, dest, Decimal("0.5"), tx_hash="txAB", chain="bitcoin"),
            _make_transfer(addr_b, dest, Decimal("0.5"), tx_hash="txAB", chain="bitcoin"),
        ]

        clusterer = BTCCoSpendCluster()
        clusters = clusterer.cluster(transfers)

        assert addr_a in clusters
        assert addr_b in clusters
        # Both should have the same cluster root
        assert clusters[addr_a] == clusters[addr_b]

    def test_cospend_separate_txs_different_clusters(self):
        """Addresses in separate txs stay in different clusters."""
        addr_a = "1AddrA"
        addr_b = "1AddrB"
        dest = "1Dest"

        transfers = [
            _make_transfer(addr_a, dest, Decimal("1"), tx_hash="txA", chain="bitcoin"),
            _make_transfer(addr_b, dest, Decimal("1"), tx_hash="txB", chain="bitcoin"),
        ]

        clusterer = BTCCoSpendCluster()
        clusters = clusterer.cluster(transfers)

        assert clusters[addr_a] != clusters[addr_b]

    def test_cospend_coinjoin_guard(self):
        """CoinJoin-like tx (>=5 equal outputs) is skipped — inputs NOT clustered."""
        inputs = [f"1Addr{i}" for i in range(3)]
        dest = "1Dest"
        coinjoin_tx = "txCJ"

        # 3 inputs, 5 equal outputs (simulated as equal amounts)
        transfers = [
            _make_transfer(addr, dest, Decimal("1"), tx_hash=coinjoin_tx, chain="bitcoin")
            for addr in inputs
        ]
        # Add 4 more equal-amount outputs (same tx, different 'inputs' here)
        # Simulate 5 outputs with same amount to same tx
        extra_outputs = [
            Transfer(
                chain="bitcoin",
                tx_hash=coinjoin_tx,
                ts=datetime.now(timezone.utc),
                from_addr=f"1Out{i}",
                to_addr=dest,
                asset="BTC",
                amount=Decimal("1"),
                kind="native",
                block=700000,
            )
            for i in range(5)
        ]
        all_transfers = transfers + extra_outputs

        clusterer = BTCCoSpendCluster()
        clusters = clusterer.cluster(all_transfers)

        # All inputs should be in separate clusters (CoinJoin skipped)
        cluster_ids = [clusters.get(addr) for addr in inputs if addr in clusters]
        # Each should be its own cluster (no merging occurred)
        assert len(set(cluster_ids)) == len(cluster_ids)

    def test_cospend_transitivity(self):
        """If A+B share tx1, B+C share tx2 → A,B,C all in same cluster."""
        addr_a, addr_b, addr_c = "1A", "1B", "1C"
        dest = "1Dest"

        transfers = [
            _make_transfer(addr_a, dest, Decimal("1"), tx_hash="tx1", chain="bitcoin"),
            _make_transfer(addr_b, dest, Decimal("1"), tx_hash="tx1", chain="bitcoin"),
            _make_transfer(addr_b, dest, Decimal("1"), tx_hash="tx2", chain="bitcoin"),
            _make_transfer(addr_c, dest, Decimal("1"), tx_hash="tx2", chain="bitcoin"),
        ]

        clusterer = BTCCoSpendCluster()
        clusters = clusterer.cluster(transfers)

        assert clusters[addr_a] == clusters[addr_b] == clusters[addr_c]
