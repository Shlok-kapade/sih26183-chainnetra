"""
Label mapping: source dataset labels → canonical M1 classes.

Every label is grounded in config/label_mapping.yaml.
Never invent mappings — if a source label is not in the YAML, it falls
to personal_or_unknown and is flagged as UNMAPPED.
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Optional

import yaml


class LabelTier(str, Enum):
    CONFIRMED = "CONFIRMED"  # judicially documented / OFAC
    STRONG = "STRONG"        # peer-reviewed academic dataset
    WEAK = "WEAK"            # community / PoR with limited verification
    UNKNOWN = "UNKNOWN"      # no reliable provenance


# Canonical M1 class names (must match training code)
CANONICAL_CLASSES = [
    "illicit",
    "exchange_hot_or_collection",
    "exchange_deposit",
    "mixer",
    "bridge",
    "dex_or_contract",
    "personal_or_unknown",
]

_CONFIG_PATH = Path(__file__).parents[3] / "config" / "label_mapping.yaml"

_mapping_cache: Optional[dict] = None


def _load_raw() -> dict:
    global _mapping_cache
    if _mapping_cache is None:
        with open(_CONFIG_PATH) as f:
            _mapping_cache = yaml.safe_load(f)
    return _mapping_cache


def _build_reverse_map(raw: dict) -> dict[str, str]:
    """Build {source_label_lower: canonical_class} reverse lookup."""
    reverse: dict[str, str] = {}
    for canonical, sources in raw.get("mappings", {}).items():
        for src in sources:
            reverse[src.lower().strip()] = canonical
    return reverse


def map_label(
    source_label: str,
    source: str = "",
) -> tuple[str, LabelTier, bool]:
    """
    Map a source label to a canonical class.

    Returns:
        (canonical_class, LabelTier, was_mapped)
        was_mapped=False means the label fell to the unmapped_action default.
    """
    raw = _load_raw()
    reverse = _build_reverse_map(raw)

    normalized = source_label.lower().strip()
    canonical = reverse.get(normalized)
    was_mapped = canonical is not None

    if not was_mapped:
        canonical = raw.get("unmapped_action", "personal_or_unknown")

    # Determine tier
    source_tiers: dict[str, str] = raw.get("source_tiers", {})
    if source and source in source_tiers:
        tier = LabelTier(source_tiers[source])
    elif was_mapped:
        tier = LabelTier.STRONG
    else:
        tier = LabelTier(raw.get("unmapped_tier", "UNKNOWN"))

    assert canonical in CANONICAL_CLASSES, f"BUG: unmapped canonical class {canonical!r}"
    return canonical, tier, was_mapped


def load_label_mapping() -> dict:
    """Return the raw YAML config (for inspection / logging)."""
    return _load_raw()
