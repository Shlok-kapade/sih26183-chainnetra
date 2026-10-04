import csv
import os

LABELS_FILE = os.path.join(os.path.dirname(__file__), '../data/labels.csv')

def load_labels():
    labels = {}
    try:
        with open(LABELS_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                labels[row['address']] = row
    except Exception as e:
        print(f"Failed to load labels: {e}")
    return labels

GLOBAL_LABELS = load_labels()

def get_entity_for_address(address: str):
    return GLOBAL_LABELS.get(address)
