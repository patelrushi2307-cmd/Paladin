"""Threat detector extension point."""

from abc import ABC, abstractmethod
from typing import Any
from ..schemas.feature import FeatureVector
from ..schemas.detector import DetectorResult


class ThreatDetector(ABC):
    name: str
    version: str = "1.0.0"
    scopes: tuple[str, ...] = ("FLOW", "SOURCE_WINDOW", "DESTINATION_WINDOW", "PAIR_WINDOW", "GLOBAL_WINDOW")

    def supports_scope(self, scope: str) -> bool:
        return scope in self.scopes

    @abstractmethod
    def initialize(self) -> None: ...

    @abstractmethod
    def detect(self, feature_vector: FeatureVector, context: dict[str, Any]) -> list[DetectorResult]: ...

    @abstractmethod
    def health(self) -> dict[str, str]: ...
