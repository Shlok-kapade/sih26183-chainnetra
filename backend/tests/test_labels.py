import os
import tempfile

from app.attribution.labels import LabelStore, load_labels_from_csv


def test_load_csv():
    content = """address,chain,entity,entity_type,source,source_url,retrieved_at,license,label_confidence
0x123,ethereum,TestEntity,sanctioned,ofac,http://example.com,2026-01-01,public,strong
"""
    with tempfile.NamedTemporaryFile('w', delete=False) as f:
        f.write(content)
        temp_path = f.name

    try:
        labels = load_labels_from_csv(temp_path)
        assert len(labels) == 1
        assert labels[0].address == "0x123"
        assert labels[0].chain == "ethereum"
        assert labels[0].entity == "TestEntity"
        assert labels[0].entity_type == "sanctioned"
        assert labels[0].source == "ofac"
        assert labels[0].source_url == "http://example.com"
        assert labels[0].license == "public"
        assert labels[0].label_confidence == "strong"
    finally:
        os.remove(temp_path)

def test_lookup():
    store = LabelStore()
    content = """address,chain,entity,entity_type,source,source_url,retrieved_at,license,label_confidence
0x123,ethereum,TestEntity,sanctioned,ofac,http://example.com,2026-01-01,public,strong
"""
    with tempfile.NamedTemporaryFile('w', delete=False) as f:
        f.write(content)
        temp_path = f.name

    try:
        store.load([temp_path])
        labels = store.lookup("0x123", "ethereum")
        assert len(labels) == 1
        assert labels[0].entity == "TestEntity"

        assert len(store.lookup("0x999", "ethereum")) == 0
    finally:
        os.remove(temp_path)

def test_stats():
    store = LabelStore()
    content = """address,chain,entity,entity_type,source,source_url,retrieved_at,license,label_confidence
0x123,ethereum,Entity1,sanctioned,ofac,http://example.com,2026-01-01,public,strong
0x456,ethereum,Entity2,exchange_hot,por,http://example.com,2026-01-01,public,strong
"""
    with tempfile.NamedTemporaryFile('w', delete=False) as f:
        f.write(content)
        temp_path = f.name

    try:
        store.load([temp_path])
        stats = store.stats()
        assert stats['sources']['ofac'] == 1
        assert stats['sources']['por'] == 1
        assert stats['entity_types']['sanctioned'] == 1
        assert stats['entity_types']['exchange_hot'] == 1
    finally:
        os.remove(temp_path)
