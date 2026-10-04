import os
import pickle

import numpy as np
from sklearn.ensemble import IsolationForest


class TraceFeatureExtractor:
    @staticmethod
    def extract(transfers):
        if not transfers:
            return np.zeros(6)

        # hop count
        senders = set(t.from_addr for t in transfers)
        receivers = set(t.to_addr for t in transfers)
        hop_count = len(senders.union(receivers))

        # split ratio (avg out_degree)
        out_degrees = {}
        for t in transfers:
            out_degrees[t.from_addr] = out_degrees.get(t.from_addr, 0) + 1
        split_ratio = np.mean(list(out_degrees.values())) if out_degrees else 0

        # timing regularity (std dev of time differences)
        times = sorted([t.ts.timestamp() for t in transfers])
        if len(times) > 1:
            diffs = np.diff(times)
            timing_regularity = np.std(diffs)
        else:
            timing_regularity = 0

        # round-amount share
        amounts = [float(t.amount) for t in transfers]
        round_amts = sum(1 for a in amounts if a % 10 == 0 or a % 100 == 0)
        round_amount_share = round_amts / len(amounts) if amounts else 0

        # revisit rate
        all_addrs = [t.from_addr for t in transfers] + [t.to_addr for t in transfers]
        unique_addrs = set(all_addrs)
        revisit_rate = len(all_addrs) / len(unique_addrs) if unique_addrs else 0

        # avg amount
        avg_amt = np.mean(amounts) if amounts else 0

        return np.array([hop_count, split_ratio, timing_regularity, round_amount_share, revisit_rate, avg_amt])

class M4AnomalyDetector:
    def __init__(self, contamination=0.1):
        self.model = IsolationForest(contamination=contamination, random_state=42)

    def fit(self, traces):
        """traces is a list of lists of Transfers"""
        X = [TraceFeatureExtractor.extract(trace) for trace in traces]
        self.model.fit(X)

    def predict(self, trace):
        """Returns anomaly score (lower is more anomalous, standard IsolationForest)"""
        x = TraceFeatureExtractor.extract(trace).reshape(1, -1)
        score = self.model.decision_function(x)[0]
        return float(score)

    def is_anomalous(self, trace):
        x = TraceFeatureExtractor.extract(trace).reshape(1, -1)
        return self.model.predict(x)[0] == -1

    def save(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump(self.model, f)

    def load(self, path):
        with open(path, 'rb') as f:
            self.model = pickle.load(f)
