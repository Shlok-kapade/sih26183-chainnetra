import hashlib
import json

from .manifest import EvidenceManifest


class ManifestVerifier:
    @staticmethod
    def compute_hash(manifest: EvidenceManifest) -> str:
        """
        Computes a SHA-256 hash of the manifest, EXCLUDING the manifest_hash field itself.
        """
        # Create a copy of the dump to avoid mutating the original object
        data = manifest.model_dump(exclude={"manifest_hash"})
        # Sort keys to ensure deterministic JSON serialization
        canonical_json = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()

    @staticmethod
    def sign_manifest(manifest: EvidenceManifest) -> EvidenceManifest:
        manifest.manifest_hash = ManifestVerifier.compute_hash(manifest)
        return manifest

    @staticmethod
    def verify(manifest: EvidenceManifest) -> bool:
        if not manifest.manifest_hash:
            return False
        expected = ManifestVerifier.compute_hash(manifest)
        return manifest.manifest_hash == expected

    @staticmethod
    def verify_json(json_str: str) -> bool:
        manifest = EvidenceManifest.model_validate_json(json_str)
        return ManifestVerifier.verify(manifest)
