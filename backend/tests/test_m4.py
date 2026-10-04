import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from scripts.synth_laundering import generate_benign_processor, generate_exchange_deposit_funnel, generate_peel_chain

from app.ml.m4_anomaly import M4AnomalyDetector, TraceFeatureExtractor


def test_m4_detector():
    detector = M4AnomalyDetector(contamination=0.1)

    anom = generate_peel_chain(seed=999)
    benign = generate_benign_processor(seed=999)

    print("Anom features:", TraceFeatureExtractor.extract(anom))
    print("Benign features:", TraceFeatureExtractor.extract(benign))

    # Just fit on different dataset types
    benign_traces = [generate_benign_processor(seed=i) for i in range(100)] + \
                    [generate_exchange_deposit_funnel(seed=i) for i in range(100)]
    anomalous_traces = [generate_peel_chain(seed=i) for i in range(25)]

    detector.fit(benign_traces + anomalous_traces)

    print("Anom score:", detector.predict(anom))
    print("Benign score:", detector.predict(benign))

    # Ensure it predicts correctly
    assert detector.predict(anom) < detector.predict(benign)

