from typing import Dict, List, Literal, Optional, Tuple

from app.attribution.label_models import AddressLabel

AttributionTier = Literal['CONFIRMED', 'PROBABLE', 'POSSIBLE', 'UNATTRIBUTED']

def assign_tier(
    label_match: Optional[AddressLabel] = None,
    m1_probs: Optional[Dict[str, float]] = None,
    dar_cluster_entity: Optional[str] = None,
    deposit_funnel_evidence: Optional[dict] = None,
) -> Tuple[AttributionTier, float, List[dict]]:
    """Returns (tier, confidence, evidence_list)"""
    evidence_list = []

    if label_match:
        evidence_list.append({"type": "label", "source": label_match.source, "entity": label_match.entity})
        return ('CONFIRMED', 1.0, evidence_list)

    if dar_cluster_entity:
        evidence_list.append({"type": "dar_cluster", "entity": dar_cluster_entity})
        return ('PROBABLE', 0.9, evidence_list)

    if deposit_funnel_evidence:
        # Check condition for probable deposit funnel
        # forwards >=80% within tau to CONFIRMED VASP, from >=5 senders, M1 p(exchange)>=0.8
        forwards_pct = deposit_funnel_evidence.get('forwards_pct', 0.0)
        senders_count = deposit_funnel_evidence.get('senders_count', 0)
        m1_prob_exchange = m1_probs.get('exchange', 0.0) if m1_probs else 0.0

        evidence_list.append({
            "type": "deposit_funnel",
            "forwards_pct": forwards_pct,
            "senders_count": senders_count,
            "m1_prob_exchange": m1_prob_exchange
        })

        if forwards_pct >= 0.8 and senders_count >= 5 and m1_prob_exchange >= 0.8:
            return ('PROBABLE', 0.85, evidence_list)

    if m1_probs:
        max_prob = max(m1_probs.values()) if m1_probs else 0.0
        if 0.5 <= max_prob <= 0.8:
            evidence_list.append({"type": "m1_model", "prob": max_prob})
            return ('POSSIBLE', max_prob, evidence_list)

    if len(evidence_list) == 1 and not label_match and not dar_cluster_entity:
        return ('POSSIBLE', 0.5, evidence_list)

    return ('UNATTRIBUTED', 0.0, evidence_list)
