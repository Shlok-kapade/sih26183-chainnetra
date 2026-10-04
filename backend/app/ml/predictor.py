"""M1 predictor — load model and predict with SHAP explanations."""
from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import shap

from app.ingest.normalize import Transfer
from app.ml.features import ROLE_CLASSES, compute_features, features_to_df
from app.ml.registry import ModelRegistry

ABSTAIN_THRESHOLD = 0.4


class M1Predictor:
    """Loads M1 from registry and predicts address roles with SHAP."""

    def __init__(self, version: str = "latest") -> None:
        registry = ModelRegistry()
        artifact = registry.load("m1", version=version)
        self.model = artifact["model"]
        self.calibrator = artifact.get("calibrator")
        self.feature_names: list[str] = artifact.get("feature_names", [])
        self.version = artifact["version"]
        self._explainer: shap.TreeExplainer | None = None

    def _get_explainer(self) -> shap.TreeExplainer:
        if self._explainer is None:
            self._explainer = shap.TreeExplainer(self.model)
        return self._explainer

    def predict(
        self,
        address: str,
        transfers: list[Transfer],
        window_end: datetime | None = None,
        neighbor_labels: dict[str, str] | None = None,
        chain: str | None = None,
        top_k_shap: int = 10,
    ) -> dict:
        """
        Predict role for a single address.

        Returns:
        {
            "address": str,
            "probs": {class: float},          # calibrated probabilities
            "predicted_class": str | None,     # None = abstain
            "abstained": bool,
            "confidence": float,
            "shap_top_features": {feat: float},
            "model_version": str,
        }
        """
        if window_end is None:
            window_end = datetime.now(timezone.utc)

        feats = compute_features(
            address=address,
            all_transfers=transfers,
            window_end=window_end,
            neighbor_labels=neighbor_labels,
            chain=chain,
        )
        X = features_to_df([feats])

        # Align columns to training feature names
        if self.feature_names:
            for col in self.feature_names:
                if col not in X.columns:
                    X[col] = 0.0
            X = X[self.feature_names]

        # Calibrated prediction
        predictor = self.calibrator if self.calibrator is not None else self.model
        prob_arr = predictor.predict_proba(X)[0]
        max_prob = float(prob_arr.max())
        pred_idx = int(prob_arr.argmax())
        abstained = max_prob < ABSTAIN_THRESHOLD

        probs = {cls: float(prob_arr[i]) for i, cls in enumerate(ROLE_CLASSES)}

        # SHAP explanation (on raw model, not calibrator)
        shap_features: dict[str, float] = {}
        try:
            explainer = self._get_explainer()
            shap_vals = explainer.shap_values(X)
            if isinstance(shap_vals, list):
                # One array per class — use predicted class
                cls_shap = shap_vals[pred_idx][0]
            else:
                cls_shap = shap_vals[0]
            top_idx = np.argsort(np.abs(cls_shap))[::-1][:top_k_shap]
            cols = list(X.columns)
            shap_features = {cols[i]: float(cls_shap[i]) for i in top_idx}
        except Exception:
            pass

        return {
            "address": address,
            "probs": probs,
            "predicted_class": None if abstained else ROLE_CLASSES[pred_idx],
            "abstained": abstained,
            "confidence": max_prob,
            "shap_top_features": shap_features,
            "model_version": self.version,
        }
