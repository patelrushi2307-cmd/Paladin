"""Optional model adapters. No model artifact is required for rule mode."""

from pathlib import Path
from typing import Any


class OptionalModelAdapter:
    def __init__(self, artifact_path: str | None = None) -> None:
        self.artifact_path = Path(artifact_path) if artifact_path else None
        self.model: Any = None
        if self.artifact_path and self.artifact_path.is_file():
            # Loading is intentionally opt-in and kept outside the hot path.
            import joblib
            self.model = joblib.load(self.artifact_path)

    @property
    def available(self) -> bool:
        return self.model is not None

    def score(self, features: list[Any]) -> float | None:
        if self.model is None:
            return None
        prediction = self.model.predict_proba([features])
        return float(prediction[0][-1])


class DDoSModelAdapter(OptionalModelAdapter): pass
class ReconModelAdapter(OptionalModelAdapter): pass
class C2ModelAdapter(OptionalModelAdapter): pass
class ExfiltrationModelAdapter(OptionalModelAdapter): pass
class DgaModelAdapter(OptionalModelAdapter): pass
class EncryptedTrafficModelAdapter(OptionalModelAdapter): pass
