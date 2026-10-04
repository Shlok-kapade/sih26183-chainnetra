from typing import List, Literal, Optional

from app.attribution.label_models import AddressLabel
from app.attribution.tiers import AttributionTier

ExitType = Literal['VASP', 'P2P_OTC_SUSPECTED', 'PRIVATE_WALLET', 'MIXER', 'BRIDGE', 'DEX_SWAP', 'SANCTIONED', 'UNKNOWN']

def resolve_exit_type(
    address: str,
    labels: List[AddressLabel],
    tier: AttributionTier,
    patterns: Optional[dict] = None,
) -> ExitType:
    if not labels and tier == 'UNATTRIBUTED':
        return 'UNKNOWN'

    # Prioritize SANCTIONED
    for label in labels:
        if label.entity_type == 'sanctioned':
            return 'SANCTIONED'

    for label in labels:
        if label.entity_type in ('exchange_hot', 'exchange_cold', 'exchange_deposit'):
            return 'VASP'
        elif label.entity_type == 'mixer':
            return 'MIXER'
        elif label.entity_type == 'bridge':
            return 'BRIDGE'
        elif label.entity_type == 'dex':
            return 'DEX_SWAP'

    if tier == 'PROBABLE' and patterns and patterns.get('is_vasp'):
        return 'VASP'

    return 'UNKNOWN'
