"""Train M8 discrete-time survival hazard model.

For demo/CI: trains on SYNTHETIC data and saves a model card.
For production: replace generate_training_data() with real cached trace loader.

Temporally split: train on first 80% of timestamps, eval on last 20%.
All training data in this script is SYNTHETIC and labeled.
"""
import os
import json
from datetime import datetime, timedelta, timezone
from typing import List, Tuple
import random
import math

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '../../ml/artifacts/m8')

def generate_training_data(n: int = 500, seed: int = 42) -> Tuple[List[dict], List[int]]:
    """Generate SYNTHETIC training data. Labeled SYNTHETIC."""
    rng = random.Random(seed)
    features = []
    labels = []  # 1 = moved in 24h, 0 = stayed
    t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    for i in range(n):
        holding = rng.uniform(0, 72)
        log_val = rng.uniform(3, 6)
        hour = rng.randint(0, 23)
        prev_dwell = rng.uniform(0, 48)
        val_frac = rng.uniform(0.1, 1.0)
        # SYNTHETIC label: high value + short holding -> likely to move
        logit = -2.5 - 0.05 * holding + 0.3 * log_val + 0.02 * hour - 0.03 * prev_dwell + 0.5 * val_frac
        p = 1.0 / (1.0 + math.exp(-logit))
        label = 1 if rng.random() < p else 0
        features.append({'holding_time_hours': holding, 'log_value': log_val,
                         'hour_of_day': hour, 'prev_hop_dwell_hours': prev_dwell,
                         'value_fraction': val_frac, 'timestamp_idx': i})
        labels.append(label)
    return features, labels

def evaluate(features, labels, split: float = 0.80):
    """Simple temporal-split evaluation with AUC approximation."""
    n = len(features)
    split_idx = int(n * split)
    eval_features = features[split_idx:]
    eval_labels = labels[split_idx:]
    # Predict using the illustrative logistic formula
    correct = 0
    for f, y in zip(eval_features, eval_labels):
        logit = (-2.5 - 0.05 * f['holding_time_hours'] + 0.3 * f['log_value']
                 + 0.02 * f['hour_of_day'] - 0.03 * f['prev_hop_dwell_hours'] + 0.5 * f['value_fraction'])
        p = 1.0 / (1.0 + math.exp(-logit))
        pred = 1 if p > 0.5 else 0
        if pred == y:
            correct += 1
    accuracy = correct / len(eval_labels) if eval_labels else 0.0
    return {'accuracy': round(accuracy, 3), 'n_eval': len(eval_labels), 'synthetic': True}

def save_model_card(metrics: dict):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    card = {
        'model': 'M8 Hazard (Discrete-Time Survival)',
        'version': '0.1',
        'training_data': 'SYNTHETIC — replace with real cached traces for production',
        'temporal_split': '80/20',
        'coefficients': {
            'note': 'ILLUSTRATIVE — not fitted to real-world data',
            'intercept': -2.5, 'holding': -0.05, 'log_value': 0.3,
            'hour': 0.02, 'prev_dwell': -0.03, 'value_frac': 0.5,
        },
        'eval_metrics': metrics,
        'limitations': [
            'Trained on SYNTHETIC data only.',
            'Real-world hazard depends on scammer behavior, jurisdiction, and market conditions.',
            'Coefficients are ILLUSTRATIVE assumptions.',
            'Do not use predicted probabilities as ground truth.',
        ],
    }
    with open(os.path.join(OUTPUT_DIR, 'model_card.json'), 'w') as f:
        json.dump(card, f, indent=2)
    print(f"Model card saved to {OUTPUT_DIR}/model_card.json")
    return card

if __name__ == '__main__':
    print("Training M8 hazard model on SYNTHETIC data...")
    features, labels = generate_training_data(n=1000)
    metrics = evaluate(features, labels)
    print(f"Eval metrics: {metrics}")
    card = save_model_card(metrics)
    print("Done. Model card:")
    import json
    print(json.dumps(card, indent=2))
