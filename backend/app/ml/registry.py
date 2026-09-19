"""Trusted local model metadata registry."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

class ModelRegistry:
    def __init__(self, root: Path | None = None) -> None:
        self.root = (root or Path(__file__).parents[3] / "models" / "trained").resolve(); self.root.mkdir(parents=True, exist_ok=True)
    def register(self, metadata: dict[str, Any], artifact: Path | None = None) -> Path:
        model_id = metadata["model_id"]; target = self.root / metadata["threat_class"] / model_id; target.mkdir(parents=True, exist_ok=True)
        if artifact:
            artifact = artifact.resolve()
            if self.root not in artifact.parents: raise ValueError("Model artifact must remain under models/trained")
        (target / "metadata.json").write_text(json.dumps(metadata, indent=2, default=str), encoding="utf-8")
        return target
    def list(self) -> list[dict[str, Any]]:
        values = []
        for metadata in self.root.glob("*/**/metadata.json"):
            values.append(json.loads(metadata.read_text(encoding="utf-8")))
        return values
    def status(self) -> list[dict[str, Any]]:
        return [{"threat_class": item.get("threat_class"), "model_id": item.get("model_id"), "algorithm": item.get("algorithm"), "feature_schema_version": item.get("feature_schema_version"), "calibration_status": item.get("calibration_status", "NOT_CALIBRATED"), "loaded": False, "model_available": False} for item in self.list()]
