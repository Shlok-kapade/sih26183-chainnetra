from datetime import datetime, timezone

from app.reports.freeze import FreezeRequestGenerator
from app.reports.generator import ReportGenerator
from app.reports.manifest import EvidenceManifest, EvidenceRecord, LabelRecord
from app.reports.verify import ManifestVerifier


def test_manifest_hashing():
    manifest = EvidenceManifest(
        case_id="CASE-123",
        generated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        target_address="0xabc",
        target_chain="ethereum",
        traces=[
            EvidenceRecord(
                tx_hash="0xdef",
                chain="ethereum",
                from_address="0x111",
                to_address="0xabc",
                asset="USDT",
                amount="1000",
                timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
                evidence_type="deposit"
            )
        ]
    )

    # Sign it
    signed = ManifestVerifier.sign_manifest(manifest)
    assert signed.manifest_hash is not None

    # Verify it
    assert ManifestVerifier.verify(signed) is True

    # Tamper with it
    signed.traces[0].amount = "9999"
    assert ManifestVerifier.verify(signed) is False

def test_report_generation():
    manifest = EvidenceManifest(
        case_id="CASE-123",
        generated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        target_address="0xabc",
        target_chain="ethereum",
        traces=[
            EvidenceRecord(
                tx_hash="0xdef",
                chain="ethereum",
                from_address="0x111",
                to_address="0xabc",
                asset="USDT",
                amount="1000",
                timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
                evidence_type="deposit"
            )
        ],
        labels=[
            LabelRecord(
                address="0xabc",
                chain="ethereum",
                label="Binance",
                confidence="High",
                source="OFAC"
            )
        ],
        severity_level="HIGH",
        urgency_score=75000.0,
        manifest_hash="dummyhash"
    )

    md = ReportGenerator.to_markdown(manifest)
    assert "CASE-123" in md
    assert "0xdef" in md
    assert "Binance" in md
    assert "dummyhash" in md

    csv_str = ReportGenerator.to_csv(manifest)
    assert "CASE-123" in csv_str
    assert "1000" in csv_str

def test_freeze_generator():
    letter = FreezeRequestGenerator.generate(
        vasp_name="Binance",
        case_id="CASE-123",
        deposit_address="0xabc",
        chain="Ethereum",
        asset="USDT",
        evidence_txs=[{"tx_hash": "0xdef", "amount": "1000"}]
    )

    assert "Binance" in letter
    assert "CASE-123" in letter
    assert "0xabc" in letter
    assert "0xdef" in letter
