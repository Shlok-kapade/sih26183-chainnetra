"""M1 model registry — save/load artifacts with version tracking."""
from __future__ import annotations

import hashlib
import json
import pickle
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ARTIFACTS_ROOT = Path(__file__).parents[3] / "ml" / "artifacts"


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


class ModelRegistry:
    """Load and save versioned model artifacts."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or ARTIFACTS_ROOT

    def _version_dir(self, model_id: str, version: str) -> Path:
        d = self.root / model_id / version
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _resolve_version(self, model_id: str, version: str) -> str:
        if version != "latest":
            return version
        base = self.root / model_id
        if not base.exists():
            raise FileNotFoundError(f"No artifacts for model '{model_id}'")
        versions = sorted(
            [v.name for v in base.iterdir() if v.is_dir() and v.name != "latest"],
            reverse=True,
        )
        if not versions:
            raise FileNotFoundError(f"No versions found for model '{model_id}'")
        return versions[0]

    def save(
        self,
        model_id: str,
        version: str,
        model: Any,
        config: dict,
        metrics: dict,
        data_manifest: dict,
        model_card: str,
        extra_files: dict[str, Any] | None = None,
    ) -> Path:
        d = self._version_dir(model_id, version)

        # Save model binary
        model_path = d / "model.pkl"
        with open(model_path, "wb") as f:
            pickle.dump(model, f)

        # config.yaml (written as JSON for simplicity — yaml superset)
        config["saved_at"] = datetime.now(timezone.utc).isoformat()
        config["version"] = version
        with open(d / "config.json", "w") as f:
            json.dump(config, f, indent=2)

        # metrics.json
        with open(d / "metrics.json", "w") as f:
            json.dump(metrics, f, indent=2)

        # data_manifest.json with file hashes
        data_manifest["model_sha256"] = _sha256_file(model_path)
        with open(d / "data_manifest.json", "w") as f:
            json.dump(data_manifest, f, indent=2)

        # MODEL_CARD.md
        with open(d / "MODEL_CARD.md", "w") as f:
            f.write(model_card)

        # Extra files (e.g. calibrator, feature_names)
        if extra_files:
            for fname, obj in extra_files.items():
                fpath = d / fname
                if fname.endswith(".pkl"):
                    with open(fpath, "wb") as f:
                        pickle.dump(obj, f)
                elif fname.endswith(".json"):
                    with open(fpath, "w") as f2:
                        json.dump(obj, f2, indent=2)
                else:
                    with open(fpath, "w") as f2:
                        f2.write(str(obj))

        # Update latest symlink
        latest = self.root / model_id / "latest"
        if latest.is_symlink() or latest.exists():
            latest.unlink()
        latest.symlink_to(version)

        return d

    def load(self, model_id: str, version: str = "latest") -> dict:
        v = self._resolve_version(model_id, version)
        d = self.root / model_id / v

        with open(d / "model.pkl", "rb") as f:
            model = pickle.load(f)

        with open(d / "config.json") as f:
            config = json.load(f)

        with open(d / "metrics.json") as f:
            metrics = json.load(f)

        result: dict = {"model": model, "config": config, "metrics": metrics, "version": v}

        calibrator_path = d / "calibrator.pkl"
        if calibrator_path.exists():
            with open(calibrator_path, "rb") as f:
                result["calibrator"] = pickle.load(f)

        feature_names_path = d / "feature_names.json"
        if feature_names_path.exists():
            with open(feature_names_path) as f:
                result["feature_names"] = json.load(f)

        return result

    def list_versions(self, model_id: str) -> list[str]:
        base = self.root / model_id
        if not base.exists():
            return []
        return sorted(
            [v.name for v in base.iterdir() if v.is_dir() and v.name != "latest"],
            reverse=True,
        )
