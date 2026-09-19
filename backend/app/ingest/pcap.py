"""Incremental offline PCAP parser. It never opens or transmits on a network interface."""

from collections.abc import AsyncIterator
from datetime import datetime, timezone
import logging
from pathlib import Path

from .base import TrafficSource
from .flow_aggregator import FlowAggregator
from ..schemas.flow import FlowEvent

logger = logging.getLogger("paladin.ingest")


class PcapTrafficSource(TrafficSource):
    source_type = "pcap"

    def __init__(self, path: Path, idle_timeout: float = 30, max_duration: float = 300) -> None:
        self.path = path
        self.aggregator = FlowAggregator(idle_timeout, max_duration, "pcap")
        self.malformed = 0
        self.unsupported = 0
        self._stopped = False

    async def start(self) -> None:
        self._stopped = False

    async def stop(self) -> None:
        self._stopped = True

    async def stream(self) -> AsyncIterator[FlowEvent]:
        try:
            from scapy.layers.inet import ICMP, IP, TCP, UDP
            from scapy.layers.inet6 import IPv6
            from scapy.utils import PcapReader
        except ImportError as exc:
            raise RuntimeError("Scapy is required for PCAP replay") from exc

        logger.info("[INGEST] PCAP_OPEN path=%s", self.path)
        try:
            with PcapReader(str(self.path)) as reader:
                for packet in reader:
                    if self._stopped:
                        return
                    try:
                        network = packet.getlayer(IP) or packet.getlayer(IPv6)
                        if network is None:
                            self.unsupported += 1
                            continue
                        timestamp = datetime.fromtimestamp(float(packet.time), timezone.utc)
                        transport = packet.getlayer(TCP) or packet.getlayer(UDP) or packet.getlayer(ICMP)
                        if transport is None:
                            self.unsupported += 1
                            continue
                        protocol = transport.name.upper()
                        src_port = getattr(transport, "sport", None)
                        dst_port = getattr(transport, "dport", None)
                        flags = str(getattr(transport, "flags", "")) if protocol == "TCP" else None
                        for event in self.aggregator.add_packet(
                            timestamp=timestamp,
                            src_ip=network.src,
                            dst_ip=network.dst,
                            src_port=src_port,
                            dst_port=dst_port,
                            protocol=protocol,
                            packet_bytes=len(packet),
                            tcp_flags=flags,
                        ):
                            yield event
                    except (AttributeError, TypeError, ValueError, OverflowError) as exc:
                        self.malformed += 1
                        logger.warning("[INGEST] malformed packet error=%s", exc)
        except OSError as exc:
            raise RuntimeError(f"Unable to read PCAP: {exc}") from exc
        for event in self.aggregator.flush():
            yield event
        logger.info("[INGEST] PCAP_COMPLETE path=%s", self.path)

    def health(self) -> dict[str, str]:
        return {"status": "stopped" if self._stopped else "ready", "source": str(self.path)}
