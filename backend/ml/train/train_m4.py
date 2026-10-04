import sys
import os
import json
from pathlib import Path

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.ml.m4_anomaly import M4AnomalyDetector

# Import synthetic generators
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../scripts')))
from synth_laundering import (
    generate_layering, generate_peel_chain, generate_rapid_forwarding,
    generate_dormancy_burst, generate_structuring, generate_round_trip,
    generate_exchange_deposit_funnel, generate_benign_processor, generate_benign_market_maker
)

def main():
    print("Generating synthetic data for M4 training...")
    
    # Generate benign traces (inliers)
    benign_traces = []
    for i in range(100):
        benign_traces.append(generate_benign_processor(seed=i))
        benign_traces.append(generate_benign_market_maker(seed=i))
        benign_traces.append(generate_exchange_deposit_funnel(seed=i))
        
    # Generate anomalous traces (outliers)
    anomalous_traces = []
    for i in range(20):
        anomalous_traces.append(generate_layering(seed=i))
        anomalous_traces.append(generate_peel_chain(seed=i))
        anomalous_traces.append(generate_rapid_forwarding(seed=i))
        anomalous_traces.append(generate_dormancy_burst(seed=i))
        anomalous_traces.append(generate_structuring(seed=i))
        anomalous_traces.append(generate_round_trip(seed=i))

    # Train data: mix of benign and anomalous, but mostly benign
    train_traces = benign_traces + anomalous_traces[:30] # contamination roughly 10%
    
    detector = M4AnomalyDetector(contamination=0.1)
    print("Training IsolationForest...")
    detector.fit(train_traces)
    
    # Evaluate
    print("Evaluating...")
    benign_scores = [detector.predict(t) for t in benign_traces]
    anomalous_scores = [detector.predict(t) for t in anomalous_traces]
    
    avg_benign = sum(benign_scores) / len(benign_scores)
    avg_anomalous = sum(anomalous_scores) / len(anomalous_scores)
    
    benign_flagged = sum(1 for t in benign_traces if detector.is_anomalous(t))
    anomalous_flagged = sum(1 for t in anomalous_traces if detector.is_anomalous(t))
    
    print(f"Benign Avg Score: {avg_benign:.3f}")
    print(f"Anomalous Avg Score: {avg_anomalous:.3f}")
    print(f"False Positives: {benign_flagged} / {len(benign_traces)}")
    print(f"True Positives: {anomalous_flagged} / {len(anomalous_traces)}")
    
    # Save model
    artifact_dir = Path(__file__).parent.parent.parent / "app" / "ml" / "artifacts" / "m4_anomaly" / "v1"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    
    model_path = artifact_dir / "model.pkl"
    detector.save(str(model_path))
    
    metrics = {
        "avg_benign_score": avg_benign,
        "avg_anomalous_score": avg_anomalous,
        "false_positive_rate": benign_flagged / len(benign_traces),
        "true_positive_rate": anomalous_flagged / len(anomalous_traces)
    }
    
    with open(artifact_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
        
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    main()
