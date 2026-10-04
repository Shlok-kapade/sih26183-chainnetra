"""
Phase 5 ML tests — features, registry, dataset builder, calibration utils.
All tests use deterministic synthetic data; no fabricated metrics.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import numpy as np
import pytest

from app.ingest.normalize import Transfer
from app.ml.features import (
    ROLE_CLASSES,
    ROLE_TO_IDX,
    compute_features,
    features_to_df,
)
from app.ml.registry import ModelRegistry
from app.ml.utils import expected_calibration_error, per_class_pr_auc

# ---- helpers ----

def _make_t(from_addr: str, to_addr: str, amount: float = 100.0,
            minutes_ago: int = 0, chain: str = "ethereum") -> Transfer:
    ts = datetime.now(timezone.utc) - timedelta(minutes=minutes_ago)
    return Transfer(
        chain=chain,
        tx_hash=f"tx_{from_addr}_{to_addr}_{minutes_ago}",
        ts=ts,
        from_addr=from_addr,
        to_addr=to_addr,
        asset="USDT",
        amount=Decimal(str(amount)),
        kind="token",
        block=1000,
    )


# Module-level picklable stubs — pickle requires top-level classes
class _DummyModel:
    def predict(self, X):
        return [0]


class _TrivialModel:
    pass


# =========================================================================
# Feature tests
# =========================================================================

class TestComputeFeatures:
    def test_returns_dict_of_floats(self):
        addr = "0xABC"
        transfers = [_make_t("0xSender", addr, 100.0)]
        w = datetime.now(timezone.utc)
        feats = compute_features(addr, transfers, w)
        assert isinstance(feats, dict)
        for k, v in feats.items():
            assert isinstance(v, float), f"Feature {k} is {type(v)}, expected float"

    def test_point_in_time_excludes_future(self):
        addr = "0xAddr"
        past = _make_t("0xSender", addr, 100.0, minutes_ago=10)
        future = Transfer(
            chain="ethereum",
            tx_hash="tx_future",
            ts=datetime.now(timezone.utc) + timedelta(hours=1),
            from_addr="0xFuture",
            to_addr=addr,
            asset="USDT",
            amount=Decimal("999"),
            kind="token",
            block=2000,
        )
        w = datetime.now(timezone.utc)
        feats = compute_features(addr, [past, future], w)
        # Only past transfer should count
        assert feats["n_in_tx"] == 1.0

    def test_no_transfers_gives_zero_features(self):
        addr = "0xEmpty"
        w = datetime.now(timezone.utc)
        feats = compute_features(addr, [], w)
        assert feats["n_in_tx"] == 0.0
        assert feats["n_out_tx"] == 0.0
        assert feats["log_total_in"] == 0.0

    def test_forward_ratio_10m(self):
        addr = "0xRelay"
        transfers = [
            _make_t("0xSender", addr, 100.0, minutes_ago=15),   # inflow 15m ago
            _make_t(addr, "0xDest", 95.0, minutes_ago=10),       # outflow 10m ago (5m after inflow)
        ]
        w = datetime.now(timezone.utc)
        feats = compute_features(addr, transfers, w)
        # delta = 5 min = 300s < 600s → fwd_ratio_10m > 0
        assert feats["fwd_ratio_10m"] > 0.0
        assert feats["fwd_ratio_1h"] > 0.0

    def test_fan_in_ratio(self):
        addr = "0xCenter"
        transfers = [_make_t(f"0xS{i}", addr, 10.0, minutes_ago=60) for i in range(5)]
        transfers.append(_make_t(addr, "0xDest", 45.0, minutes_ago=30))
        w = datetime.now(timezone.utc)
        feats = compute_features(addr, transfers, w)
        assert feats["n_in_cp"] == 5.0
        assert feats["n_out_cp"] == 1.0
        assert feats["fan_in_ratio"] == 5.0

    def test_hour_entropy_24_7(self):
        """Address active all 24 hours should have high entropy."""
        addr = "0xExchange"
        base = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        transfers = []
        for h in range(24):
            ts = base - timedelta(hours=h)
            transfers.append(Transfer(
                chain="ethereum", tx_hash=f"tx_{h}", ts=ts,
                from_addr="0xS", to_addr=addr, asset="ETH",
                amount=Decimal("1"), kind="native", block=h,
            ))
        w = datetime.now(timezone.utc)
        feats = compute_features(addr, transfers, w)
        assert feats["hour_entropy"] > 2.5  # max entropy for 24 hours ≈ 3.18

    def test_chain_id_encoding(self):
        addr = "0xA"
        w = datetime.now(timezone.utc)
        feats_eth = compute_features(addr, [], w, chain="ethereum")
        feats_tron = compute_features(addr, [], w, chain="tron")
        assert feats_eth["chain_id"] != feats_tron["chain_id"]

    def test_neighbor_label_proximity(self):
        addr = "0xAddr"
        neighbor = "0xMixer"
        transfers = [_make_t(neighbor, addr, 100.0)]
        w = datetime.now(timezone.utc)
        neighbor_labels = {neighbor: "mixer"}
        feats = compute_features(addr, transfers, w, neighbor_labels=neighbor_labels)
        assert feats["nb_share_mixer"] > 0.0

    def test_features_to_df_consistent_columns(self):
        addr = "0xA"
        w = datetime.now(timezone.utc)
        f1 = compute_features(addr, [_make_t("0xS", addr)], w)
        f2 = compute_features(addr, [], w)
        df = features_to_df([f1, f2])
        assert list(df.columns) == list(f1.keys())
        assert len(df) == 2
        assert not df.isnull().any().any()

    def test_round_amount_share(self):
        addr = "0xAddr"
        transfers = [
            _make_t("0xS", addr, 100.0),   # round
            _make_t("0xS2", addr, 137.5),  # not round
        ]
        w = datetime.now(timezone.utc)
        feats = compute_features(addr, transfers, w)
        assert 0.0 <= feats["round_amount_share"] <= 1.0


# =========================================================================
# Registry tests (module-level models for picklability)
# =========================================================================

class TestModelRegistry:
    def test_save_and_load(self, tmp_path):
        registry = ModelRegistry(root=tmp_path)
        config = {"model_type": "dummy", "classes": ["a", "b"]}
        metrics = {"accuracy": 0.99}
        manifest = {"label_files": [], "dataset_sha256": "abc123"}
        card = "# Dummy Model Card"

        saved = registry.save(
            model_id="test_model",
            version="v0.0",
            model=_DummyModel(),
            config=config,
            metrics=metrics,
            data_manifest=manifest,
            model_card=card,
        )
        assert (saved / "model.pkl").exists()
        assert (saved / "metrics.json").exists()
        assert (saved / "MODEL_CARD.md").exists()
        assert (saved / "data_manifest.json").exists()

        loaded = registry.load("test_model", "v0.0")
        assert loaded["metrics"]["accuracy"] == 0.99
        assert loaded["config"]["model_type"] == "dummy"
        assert loaded["version"] == "v0.0"

    def test_latest_resolves(self, tmp_path):
        registry = ModelRegistry(root=tmp_path)
        registry.save("m", "v0.1", _TrivialModel(), {"x": 1}, {"score": 0.5}, {}, "card")
        registry.save("m", "v0.2", _TrivialModel(), {"x": 2}, {"score": 0.8}, {}, "card")
        loaded = registry.load("m", "latest")
        assert loaded["version"] == "v0.2"

    def test_extra_files_saved(self, tmp_path):
        registry = ModelRegistry(root=tmp_path)
        registry.save(
            "m2", "v1.0", _TrivialModel(), {}, {}, {}, "card",
            extra_files={"feature_names.json": ["f1", "f2", "f3"]}
        )
        loaded = registry.load("m2", "v1.0")
        assert loaded["feature_names"] == ["f1", "f2", "f3"]

    def test_list_versions(self, tmp_path):
        registry = ModelRegistry(root=tmp_path)
        registry.save("mx", "v1.0", _TrivialModel(), {}, {}, {}, "c")
        registry.save("mx", "v2.0", _TrivialModel(), {}, {}, {}, "c")
        versions = registry.list_versions("mx")
        assert "v2.0" in versions
        assert "v1.0" in versions

    def test_missing_model_raises(self, tmp_path):
        registry = ModelRegistry(root=tmp_path)
        with pytest.raises(FileNotFoundError):
            registry.load("nonexistent")


# =========================================================================
# Dataset builder tests
# =========================================================================

class TestDatasetBuilder:
    def test_build_synthetic_small(self):
        from app.ml.datasets import build_synthetic_dataset
        X, y, addrs = build_synthetic_dataset(n_per_class=5, seed=1)
        assert len(X) > 0
        assert len(X) == len(y) == len(addrs)
        assert y.min() >= 0
        assert y.max() < len(ROLE_CLASSES)
        assert not X.isnull().any().any()

    def test_synthetic_class_balance(self):
        from app.ml.datasets import build_synthetic_dataset
        X, y, _ = build_synthetic_dataset(n_per_class=10, seed=2)
        # Should have multiple distinct classes
        assert len(np.unique(y)) >= 4

    def test_build_from_real_labels_empty(self):
        from app.ml.datasets import build_dataset_from_labels_and_synthetics
        X, y, addrs = build_dataset_from_labels_and_synthetics(
            labels=[], synthetic_transfers_by_address={}
        )
        assert len(X) == 0
        assert len(y) == 0

    def test_build_from_real_labels(self):
        from app.ml.datasets import build_dataset_from_labels_and_synthetics
        labels = [
            {"address": "0xABC", "chain": "ethereum", "entity": "Tornado Cash",
             "entity_type": "mixer", "source": "ofac_sdn", "source_url": "",
             "retrieved_at": "2026-01-01", "license": "public", "label_confidence": "strong"},
            {"address": "0xDEF", "chain": "ethereum", "entity": "Binance",
             "entity_type": "exchange_hot", "source": "por", "source_url": "",
             "retrieved_at": "2026-01-01", "license": "public", "label_confidence": "strong"},
        ]
        X, y, addrs = build_dataset_from_labels_and_synthetics(labels=labels)
        assert len(X) == 2
        assert len(y) == 2
        assert ROLE_TO_IDX["mixer"] in y
        assert ROLE_TO_IDX["exchange_hot_or_collection"] in y


# =========================================================================
# ECE / calibration utility tests (imported from app.ml.utils)
# =========================================================================

class TestECE:
    def test_perfect_calibration(self):
        """Perfect predictions → ECE ≈ 0."""
        n = 100
        y_true = np.array([0] * 50 + [1] * 50)
        y_prob = np.zeros((n, 2))
        for i, cls in enumerate(y_true):
            y_prob[i, cls] = 1.0
        ece = expected_calibration_error(y_prob, y_true)
        assert ece < 0.05

    def test_overconfident_wrong(self):
        """All predictions wrong but confident → ECE ≈ 1.0."""
        n = 100
        y_true = np.zeros(n, dtype=int)
        y_prob = np.zeros((n, 2))
        y_prob[:, 1] = 1.0  # always predicts class 1, true is 0
        ece = expected_calibration_error(y_prob, y_true)
        assert ece > 0.8

    def test_per_class_pr_auc_binary(self):
        """Perfect binary predictor → PR-AUC = 1.0."""
        n = 100
        y_true = np.array([0] * 50 + [1] * 50)
        y_prob = np.zeros((n, 2))
        for i, cls in enumerate(y_true):
            y_prob[i, cls] = 1.0
        aucs = per_class_pr_auc(y_prob, y_true, ["neg", "pos"])
        assert aucs["pos"] == pytest.approx(1.0)

    def test_per_class_pr_auc_missing_class(self):
        """Class with zero support returns nan."""
        n = 10
        y_true = np.zeros(n, dtype=int)
        y_prob = np.zeros((n, 2))
        y_prob[:, 0] = 1.0
        aucs = per_class_pr_auc(y_prob, y_true, ["neg", "pos"])
        assert aucs["pos"] != aucs["pos"]  # nan check
