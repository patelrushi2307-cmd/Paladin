"""Future score fusion boundary."""

from abc import ABC, abstractmethod
from typing import Any


class ThreatScorer(ABC):
    @abstractmethod
    def score(self, detector_results: list[dict[str, Any]], context: dict[str, Any]) -> list[dict[str, Any]]: ...
