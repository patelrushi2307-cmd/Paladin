"""Feature extraction extension point."""

from abc import ABC, abstractmethod
from typing import Any
from ..schemas.feature import FeatureVector
from ..schemas.flow import FlowEvent


class FeatureExtractor(ABC):
    @abstractmethod
    def extract(self, flow_event: FlowEvent, stream_context: dict[str, Any]) -> FeatureVector: ...
