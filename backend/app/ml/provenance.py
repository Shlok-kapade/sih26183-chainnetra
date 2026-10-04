"""
LabelRecord: provenance-preserving label structure.

Every imported label MUST become a LabelRecord. The original_label is
NEVER destroyed — canonical_label is a derived field.
"""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Optional


@dataclass
class LabelRecord:
    # Identity
    chain: str
    address: str
    address_release_id: str  # original release-level ID (e.g. ADDR_FP_0001)

    # Raw label from source (NEVER discarded)
    original_label: str
    original_label_zh: str  # keep Chinese label if present

    # Derived canonical label
    canonical_label: str  # one of CANONICAL_CLASSES
    label_tier: str       # CONFIRMED / STRONG / WEAK / UNKNOWN
    was_mapped: bool      # False = fell to personal_or_unknown default
    is_unmapped: bool     # synonym for documentation clarity

    # Source provenance
    source: str           # e.g. mendeley_tron_2026
    source_url: str
    source_version: str
    retrieved_at: datetime

    # Temporal bounds (point-in-time feature window)
    valid_from: Optional[date] = None   # first_tx_date
    valid_to: Optional[date] = None     # last_tx_date (features computed <= this)

    # Quality indicators
    label_basis: str = ""          # e.g. judicially_documented_case_facts
    pure_label: bool = True        # from source: single-role label
    exact_address_withheld: bool = False

    # Extras
    notes: str = ""
    dataset_identity: str = "REAL"  # REAL | SYNTHETIC | MIXED


@dataclass
class FetchRecord:
    """Tracks API fetch status for each address."""
    address: str
    api_source: str
    status: str           # OK | API_FAILURE | RATE_LIMITED | CACHED | NO_TRANSFERS
    n_transfers: int = 0
    n_pages: int = 0
    fetched_at: Optional[datetime] = None
    error_msg: str = ""
    cache_hit: bool = False


def write_provenance_csv(records: list[LabelRecord], path: Path) -> None:
    """Write provenance records to CSV, preserving all fields."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not records:
        return
    fieldnames = list(asdict(records[0]).keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for rec in records:
            row = asdict(rec)
            writer.writerow(row)


def write_fetch_manifest_csv(records: list[FetchRecord], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not records:
        return
    fieldnames = list(asdict(records[0]).keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for rec in records:
            writer.writerow(asdict(rec))
