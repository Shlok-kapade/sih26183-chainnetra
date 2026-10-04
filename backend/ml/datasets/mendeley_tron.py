"""
Mendeley TRON Dataset Adapter (v3, CC BY 4.0)

Source: https://data.mendeley.com/datasets/62dmsngtfb/3
DOI: https://doi.org/10.17632/62dmsngtfb.3

Reads all three CSV files from the Mendeley dataset, validates TRON addresses,
maps labels to canonical M1 classes, and emits LabelRecord objects.

ANTI-HALLUCINATION: schema derived from DATA_DICTIONARY.md and actual CSV inspection.
Columns documented here are ONLY those that actually exist in the files.
"""

from __future__ import annotations

import csv
import re
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Iterator

from app.ml.label_mapping import LabelTier, map_label
from app.ml.provenance import LabelRecord
from app.ingest.validators import validate_tron_address

# Regex for real TRON addresses (base58check, starts with T, length 34)
_TRON_RE = re.compile(r"^T[A-HJ-NP-Za-km-z1-9]{33}$")

PROJECT_ROOT = Path(__file__).parents[3]
DATASET_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "dataset-raw"
    / "Judicially Grounded Virtual Asset Address Labels a"
    / "public_release_second_revision2"
)

SOURCE_NAME = "mendeley_tron_2026"
SOURCE_URL = "https://data.mendeley.com/datasets/62dmsngtfb/3"
SOURCE_VERSION = "3"
RETRIEVED_AT = datetime(2026, 9, 30, tzinfo=timezone.utc)


def _parse_date(s: str) -> date | None:
    if not s or not s.strip():
        return None
    try:
        return date.fromisoformat(s.strip())
    except ValueError:
        return None


def _is_real_tron(addr: str) -> bool:
    """True if addr looks like a real TRON base58check address."""
    if not addr or not addr.strip():
        return False
    addr = addr.strip()
    if not _TRON_RE.match(addr):
        return False
    # Use existing validator for checksum verification
    try:
        return validate_tron_address(addr)
    except Exception:
        return False


def load_ground_truth_labels() -> list[LabelRecord]:
    """
    Load judicial_ground_truth_address_labels_public_v2.csv.

    1,150 rows total. Usable: TRON addresses where exact_address_withheld=false.
    All labels: fraud platform, pseudo broker, illegal broker, victim (withheld).
    """
    path = DATASET_DIR / "judicial_ground_truth_address_labels_public_v2.csv"
    records: list[LabelRecord] = []

    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            # Skip withheld victim addresses
            if row["exact_address_withheld"].strip().lower() == "true":
                continue

            addr = row["address"].strip()
            chain = row["blockchain_inferred"].strip()

            # Only TRON addresses for this adapter
            if chain != "TRON":
                continue
            if not _is_real_tron(addr):
                continue

            source_label = row["ground_truth_role_label"].strip()
            canonical, tier, was_mapped = map_label(source_label, source=SOURCE_NAME)

            records.append(
                LabelRecord(
                    chain="TRON",
                    address=addr,
                    address_release_id=row["address_release_id"].strip(),
                    original_label=source_label,
                    original_label_zh=row["ground_truth_role_label_zh"].strip(),
                    canonical_label=canonical,
                    label_tier=tier.value,
                    was_mapped=was_mapped,
                    is_unmapped=not was_mapped,
                    source=SOURCE_NAME,
                    source_url=SOURCE_URL,
                    source_version=SOURCE_VERSION,
                    retrieved_at=RETRIEVED_AT,
                    valid_from=None,   # not in this file
                    valid_to=None,
                    label_basis=row["label_basis"].strip(),
                    pure_label=row["pure_label"].strip().lower() == "true",
                    exact_address_withheld=False,
                    notes="judicial_ground_truth file",
                    dataset_identity="REAL",
                )
            )
    return records


def load_behavioral_subset() -> list[LabelRecord]:
    """
    Load tron_trc20_usdt_behavioral_analysis_subset_v2.csv.

    1,024 rows. Usable: 638 real TRON addresses (victim rows withheld).
    Adds first_tx_date / last_tx_date for point-in-time feature cutoffs.
    """
    path = DATASET_DIR / "tron_trc20_usdt_behavioral_analysis_subset_v2.csv"
    records: list[LabelRecord] = []

    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if row["exact_address_withheld"].strip().lower() == "true":
                continue

            addr = row["address"].strip()
            if not _is_real_tron(addr):
                continue

            source_label = row["ground_truth_role_label"].strip()
            canonical, tier, was_mapped = map_label(source_label, source=SOURCE_NAME)

            records.append(
                LabelRecord(
                    chain="TRON",
                    address=addr,
                    address_release_id=row["address_release_id"].strip(),
                    original_label=source_label,
                    original_label_zh=row["ground_truth_role_label_zh"].strip(),
                    canonical_label=canonical,
                    label_tier=tier.value,
                    was_mapped=was_mapped,
                    is_unmapped=not was_mapped,
                    source=SOURCE_NAME,
                    source_url=SOURCE_URL,
                    source_version=SOURCE_VERSION,
                    retrieved_at=RETRIEVED_AT,
                    valid_from=_parse_date(row["first_tx_date"]),
                    valid_to=_parse_date(row["last_tx_date"]),
                    label_basis=row["label_basis"].strip(),
                    pure_label=row["pure_label"].strip().lower() == "true",
                    exact_address_withheld=False,
                    notes=(
                        f"behavioral_subset; active_days={row['active_days']}; "
                        f"total_tx={row['total_transactions']}; "
                        f"wallet_lifetime={row['wallet_lifetime']}d"
                    ),
                    dataset_identity="REAL",
                )
            )
    return records


def load_grouped_classification_subset() -> list[LabelRecord]:
    """
    Load tron_trc20_usdt_single_case_grouped_classification_subset_v2.csv.

    Same schema as behavioral subset + validation_group_id.
    Used for entity-disjoint (group-level) evaluation splits.
    """
    path = DATASET_DIR / "tron_trc20_usdt_single_case_grouped_classification_subset_v2.csv"
    records: list[LabelRecord] = []

    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if row["exact_address_withheld"].strip().lower() == "true":
                continue

            addr = row["address"].strip()
            if not _is_real_tron(addr):
                continue

            source_label = row["ground_truth_role_label"].strip()
            canonical, tier, was_mapped = map_label(source_label, source=SOURCE_NAME)

            records.append(
                LabelRecord(
                    chain="TRON",
                    address=addr,
                    address_release_id=row["address_release_id"].strip(),
                    original_label=source_label,
                    original_label_zh=row["ground_truth_role_label_zh"].strip(),
                    canonical_label=canonical,
                    label_tier=tier.value,
                    was_mapped=was_mapped,
                    is_unmapped=not was_mapped,
                    source=SOURCE_NAME,
                    source_url=SOURCE_URL,
                    source_version=SOURCE_VERSION,
                    retrieved_at=RETRIEVED_AT,
                    valid_from=_parse_date(row["first_tx_date"]),
                    valid_to=_parse_date(row["last_tx_date"]),
                    label_basis=row["label_basis"].strip(),
                    pure_label=row["pure_label"].strip().lower() == "true",
                    exact_address_withheld=False,
                    notes=(
                        f"grouped_subset; group={row['validation_group_id']}; "
                        f"active_days={row['active_days']}; "
                        f"total_tx={row['total_transactions']}"
                    ),
                    dataset_identity="REAL",
                )
            )
    return records


def load_all_mendeley_tron(
    dedup: bool = True,
) -> tuple[list[LabelRecord], dict[str, str]]:
    """
    Load and merge all three Mendeley files, preferring behavioral subset
    (which has first/last tx dates) over the ground-truth-only file.

    Returns:
        (records, group_ids) where group_ids maps address → validation_group_id
        (available for addresses in the grouped subset only).
    """
    # Load grouped subset first (has group IDs for entity-disjoint split)
    grouped = load_grouped_classification_subset()
    grouped_addrs = {r.address for r in grouped}

    # Group IDs from grouped subset
    group_ids: dict[str, str] = {}
    path = DATASET_DIR / "tron_trc20_usdt_single_case_grouped_classification_subset_v2.csv"
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            addr = row["address"].strip()
            gid = row.get("validation_group_id", "").strip()
            if addr and gid:
                group_ids[addr] = gid

    # Load behavioral subset (has dates, superset of grouped)
    behavioral = load_behavioral_subset()
    behavioral_addrs = {r.address for r in behavioral}

    # Load ground truth (all chains, filter TRON, no dates)
    gt = load_ground_truth_labels()

    # Merge: prefer behavioral > grouped > gt (behavioral has dates)
    seen: set[str] = set()
    merged: list[LabelRecord] = []

    for rec in behavioral:
        if rec.address not in seen:
            seen.add(rec.address)
            merged.append(rec)

    for rec in gt:
        if rec.address not in seen:
            seen.add(rec.address)
            merged.append(rec)

    return merged, group_ids
