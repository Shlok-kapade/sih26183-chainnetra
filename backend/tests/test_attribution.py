from app.attribution.exit_resolver import resolve_exit_type
from app.attribution.label_models import AddressLabel
from app.attribution.tiers import assign_tier


def test_confirmed_tier():
    label = AddressLabel(
        address="0x123", chain="eth", entity="ExchangeA",
        entity_type="exchange_hot", source="por",
        retrieved_at=None, license="", label_confidence="strong"
    )
    tier, conf, ev = assign_tier(label_match=label)
    assert tier == 'CONFIRMED'
    assert conf == 1.0
    assert ev[0]['type'] == 'label'

def test_unattributed():
    tier, conf, ev = assign_tier()
    assert tier == 'UNATTRIBUTED'
    assert conf == 0.0

def test_exit_type_vasp():
    label = AddressLabel(
        address="0x123", chain="eth", entity="ExchangeA",
        entity_type="exchange_hot", source="por"
    )
    exit_type = resolve_exit_type("0x123", [label], 'CONFIRMED')
    assert exit_type == 'VASP'

def test_exit_type_mixer():
    label = AddressLabel(
        address="0x123", chain="eth", entity="Tornado",
        entity_type="mixer", source="community"
    )
    exit_type = resolve_exit_type("0x123", [label], 'CONFIRMED')
    assert exit_type == 'MIXER'

def test_exit_type_sanctioned():
    label = AddressLabel(
        address="0x123", chain="eth", entity="Lazarus",
        entity_type="sanctioned", source="ofac"
    )
    exit_type = resolve_exit_type("0x123", [label], 'CONFIRMED')
    assert exit_type == 'SANCTIONED'
