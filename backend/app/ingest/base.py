"""Ingestion extension point for PCAP, NetFlow, IPFIX, and sFlow."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from . import __name__ as _package_name
from ..schemas.flow import FlowEvent


class TrafficSource(ABC):
    """A receive-only source that emits normalized FlowEvent objects."""

    @abstractmethod
    async def start(self) -> None: ...

    @abstractmethod
    async def stop(self) -> None: ...

    @abstractmethod
    def stream(self) -> AsyncIterator[FlowEvent]: ...

    @abstractmethod
    def health(self) -> dict[str, str]: ...
