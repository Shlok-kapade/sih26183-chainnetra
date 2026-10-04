import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle
import os

# Create dummy training data (graph features -> label)
# Features: [in_degree, out_degree, total_volume_usd, avg_time_between_txs_sec, unique_counterparties]
# Labels: 0 = Benign, 1 = Exchange, 2 = Mixer

data = [
    [1, 10, 500, 3600, 10, 0],  # Benign payment
    [5, 2, 100, 86400, 3, 0],   # Benign retail
    [100, 200, 5000000, 10, 250, 1], # Exchange (huge volume, many parties, fast)
    [500, 500, 10000000, 5, 800, 1], # Exchange
    [50, 50, 20000, 300, 50, 2],    # Mixer (balanced in/out, medium time)
    [100, 100, 50000, 150, 100, 2], # Mixer
]

df = pd.DataFrame(data, columns=['in_degree', 'out_degree', 'volume', 'avg_time', 'unique_peers', 'label'])
X = df.drop('label', axis=1)
y = df['label']

model = RandomForestClassifier(n_estimators=10, random_state=42)
model.fit(X, y)

os.makedirs('app/ml', exist_ok=True)
with open('app/ml/m3_model.pkl', 'wb') as f:
    pickle.dump(model, f)
print("Model trained and saved to app/ml/m3_model.pkl")
