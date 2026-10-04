import csv
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from app.attribution.label_models import AddressLabel, EntityType


def load_labels_from_csv(path: str) -> List[AddressLabel]:
    labels = []
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            retrieved_at = row.get('retrieved_at', '')
            dt = datetime.fromisoformat(retrieved_at) if retrieved_at else None

            labels.append(AddressLabel(
                address=row['address'],
                chain=row['chain'],
                entity=row['entity'],
                entity_type=row['entity_type'], # type: ignore
                source=row['source'],
                source_url=row.get('source_url', ''),
                retrieved_at=dt,
                license=row.get('license', ''),
                label_confidence=row.get('label_confidence', 'strong') # type: ignore
            ))
    return labels

class LabelStore:
    def __init__(self):
        # Dict mapping (address, chain) -> list of labels
        self._labels: Dict[Tuple[str, str], List[AddressLabel]] = defaultdict(list)

    def load(self, paths: List[str]):
        for path in paths:
            for label in load_labels_from_csv(path):
                self._labels[(label.address, label.chain)].append(label)

    def lookup(self, address: str, chain: str) -> List[AddressLabel]:
        return self._labels.get((address, chain), [])

    def get_entity(self, address: str, chain: str) -> Optional[Tuple[str, EntityType, str]]:
        labels = self.lookup(address, chain)
        if not labels:
            return None
        # Return the first strong label, or just the first label
        strong_labels = [lbl for lbl in labels if lbl.label_confidence == 'strong']
        best = strong_labels[0] if strong_labels else labels[0]
        return (best.entity, best.entity_type, best.source)

    def all_labels(self) -> List[AddressLabel]:
        return [lbl for labels in self._labels.values() for lbl in labels]

    def stats(self) -> dict:
        sources = defaultdict(int)
        entity_types = defaultdict(int)
        for label in self.all_labels():
            sources[label.source] += 1
            entity_types[label.entity_type] += 1
        return {
            'sources': dict(sources),
            'entity_types': dict(entity_types)
        }
