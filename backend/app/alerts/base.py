"""Alert publication boundary."""

from abc import ABC, abstractmethod
from ..schemas.alert import Alert


class AlertSink(ABC):
    @abstractmethod
    async def publish(self, alert: Alert) -> None: ...
