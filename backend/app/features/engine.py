"""Incremental feature engine consuming normalized FlowEvents."""

from collections import Counter, deque
from datetime import datetime, timezone
import asyncio
import time
from uuid import NAMESPACE_URL, uuid5

from ..config import settings
from ..schemas.feature import FeatureVector
from ..schemas.flow import FlowEvent
from .direction import classify_direction, parse_networks
from .dns import dns_features
from .math_utils import coefficient_of_variation, mean, numeric_summary, periodicity_score, safe_ratio, shannon_entropy, standard_deviation
from .state import StreamingStateManager, WindowManager


class FeatureEngine:
    """Observation-only incremental feature processor with bounded state and output."""

    def __init__(self) -> None:
        self.state = StreamingStateManager()
        self.windows = WindowManager()
        self.feature_queue: asyncio.Queue[FeatureVector] = asyncio.Queue(maxsize=settings.event_queue_maxsize)
        self.recent: deque[FeatureVector] = deque(maxlen=1000)
        self.errors = 0
        self.dropped = 0
        self.processed = 0
        self.latencies_ms: deque[float] = deque(maxlen=1000)
        self.baseline: dict[str, float] = {}
        self.networks = parse_networks("10.0.0.0/8,172.16.0.0/12,192.168.0.0/16")
        self.running = True

    def process(self, event: FlowEvent) -> FeatureVector:
        started = time.perf_counter()
        try:
            self.state.update(event)
            window_events = self.state.window_events(event.timestamp, 5)
            values, availability, groups = self._calculate(event, window_events)
            feature_id = str(uuid5(NAMESPACE_URL, f"{event.event_id}:SOURCE_WINDOW:{event.timestamp.isoformat()}"))
            vector = FeatureVector(
                feature_id=feature_id,
                flow_id=event.event_id,
                timestamp=event.timestamp,
                window_start=event.timestamp.replace(microsecond=0),
                window_end=event.timestamp,
                scope="SOURCE_WINDOW",
                source_type=event.source_type,
                values=values,
                groups=groups,
                availability=availability,
            )
            self.recent.append(vector)
            try:
                self.feature_queue.put_nowait(vector)
            except asyncio.QueueFull:
                self.dropped += 1
            self.processed += 1
            self.latencies_ms.append((time.perf_counter() - started) * 1000)
            return vector
        except Exception:
            self.errors += 1
            raise

    def _calculate(self, event: FlowEvent, events: list[FlowEvent]) -> tuple[dict[str, object], dict[str, bool], dict[str, dict[str, object]]]:
        duration = max((max(item.timestamp for item in events) - min(item.timestamp for item in events)).total_seconds(), 1.0) if events else 1.0
        packets = sum(item.packets for item in events)
        bytes_total = sum(item.bytes for item in events)
        flow_bytes = [item.bytes for item in events]
        flow_packets = [item.packets for item in events]
        flow_durations = [item.duration for item in events]
        timestamps = sorted(item.timestamp.timestamp() for item in events)
        intervals = [right - left for left, right in zip(timestamps, timestamps[1:]) if right >= left]
        destinations = [item.dst_ip for item in events]
        sources = [item.src_ip for item in events]
        ports = [item.dst_port for item in events if item.dst_port is not None]
        destination_bytes = Counter()
        for item in events:
            destination_bytes[item.dst_ip] += item.bytes
        tcp_events = [item for item in events if item.protocol.upper() == "TCP"]
        udp_events = [item for item in events if item.protocol.upper() == "UDP"]
        protocol_count = len(events)
        flag_count = lambda flag: sum(flag in (item.tcp_flags or "").upper() for item in tcp_events)
        tcp_count = len(tcp_events)
        dns_values, dns_available = dns_features(event.dns_query, event.dns_record_type)
        event_sizes = event.packet_size_summary or {}
        packet_sizes = [float(item.packet_size_summary["mean"]) for item in events if item.packet_size_summary and "mean" in item.packet_size_summary]
        ps_summary = numeric_summary(packet_sizes)
        ps_mean = float(event_sizes["mean"]) if "mean" in event_sizes else ps_summary["mean"]
        ps_std = float(event_sizes["std"]) if "std" in event_sizes else ps_summary["std"]
        ps_min = float(event_sizes["min"]) if "min" in event_sizes else ps_summary["min"]
        ps_max = float(event_sizes["max"]) if "max" in event_sizes else ps_summary["max"]
        direction_values = self._directional(events)
        current_flows = len(events)
        current_destinations = len(set(destinations))
        baseline_values = {
            "current_bytes_vs_baseline": self._baseline_deviation("bytes_total", bytes_total),
            "current_flows_vs_baseline": self._baseline_deviation("flows_total", current_flows),
            "current_unique_destinations_vs_baseline": self._baseline_deviation("unique_dst_hosts", current_destinations),
        }
        values: dict[str, object] = {
            "packets_total": packets, "bytes_total": bytes_total, "flows_total": len(events),
            "packets_per_sec": safe_ratio(packets, duration), "bytes_per_sec": safe_ratio(bytes_total, duration), "flows_per_sec": safe_ratio(len(events), duration),
            "average_flow_bytes": mean(flow_bytes), "average_flow_packets": mean(flow_packets), "average_flow_duration": mean(flow_durations),
            "median_flow_bytes": numeric_summary(flow_bytes)["median"], "std_flow_bytes": standard_deviation([float(item) for item in flow_bytes]),
            "flow_duration": event.duration, "packet_count": event.packets, "byte_count": event.bytes, "packets_per_second": safe_ratio(event.packets, max(event.duration, 1e-9)), "bytes_per_second": safe_ratio(event.bytes, max(event.duration, 1e-9)),
            "packets_per_byte_ratio": safe_ratio(event.packets, event.bytes), "tcp_flag_summary": event.tcp_flags,
            "syn_ratio": safe_ratio(flag_count("S"), tcp_count), "ack_ratio": safe_ratio(flag_count("A"), tcp_count), "rst_ratio": safe_ratio(flag_count("R"), tcp_count), "fin_ratio": safe_ratio(flag_count("F"), tcp_count), "tcp_ratio": safe_ratio(len(tcp_events), protocol_count), "udp_ratio": safe_ratio(len(udp_events), protocol_count),
            "unique_src_count": len(set(sources)), "unique_dst_count": len(set(destinations)), "unique_dst_hosts": len(set(destinations)), "unique_dst_ports": len(set(ports)), "unique_src_ports": len({item.src_port for item in events if item.src_port is not None}),
            "source_ip_entropy": shannon_entropy(sources), "destination_ip_entropy": shannon_entropy(destinations), "destination_port_entropy": shannon_entropy(ports), "destination_concentration": safe_ratio(max(destination_bytes.values(), default=0), bytes_total),
            "iat_mean": mean(intervals), "iat_std": standard_deviation(intervals), "iat_min": min(intervals) if intervals else None, "iat_max": max(intervals) if intervals else None, "iat_cv": coefficient_of_variation(intervals), "periodicity_score": periodicity_score(intervals),
            "burst_packets_per_sec": safe_ratio(max((item.packets for item in events), default=0), 1), "burst_bytes_per_sec": safe_ratio(max((item.bytes for item in events), default=0), 1), "peak_packets_per_sec": safe_ratio(max((item.packets for item in events), default=0), 1), "peak_bytes_per_sec": safe_ratio(max((item.bytes for item in events), default=0), 1),
            "fanout_hosts": len(set(destinations)), "fanout_ports": len(set(ports)), "scan_velocity": safe_ratio(len(set(destinations)) + len(set(ports)), duration), "unique_destination_count": len(set(destinations)), "unique_port_count": len(set(ports)),
            "packet_size_mean": ps_mean, "packet_size_std": ps_std, "packet_size_min": ps_min, "packet_size_max": ps_max, "packet_size_median": ps_summary["median"],
            "tls_metadata_available": any(item.tls_version or item.tls_ja3 or item.tls_ja4 or item.tls_sni for item in events), "tls_version": event.tls_version, "tls_sni_present": event.tls_sni is not None, "tls_fingerprint": event.tls_ja4 or event.tls_ja3 or event.tls_ja3s, "tls_ja3": event.tls_ja3, "tls_ja3s": event.tls_ja3s, "tls_ja4": event.tls_ja4, "alpn": event.alpn, "tls_fingerprint_frequency": sum(1 for item in events if item.tls_ja4 or item.tls_ja3 or item.tls_ja3s), "unique_tls_fingerprint_count": len({item.tls_ja4 or item.tls_ja3 or item.tls_ja3s for item in events if item.tls_ja4 or item.tls_ja3 or item.tls_ja3s}),
            "direction_class": classify_direction(event.src_ip, event.dst_ip, self.networks),
            **direction_values, **dns_values, **baseline_values, "dns_query_count": sum(item.dns_query is not None for item in events), "unique_dns_query_count": len({item.dns_query for item in events if item.dns_query}), "unique_domain_count": len({tuple(item.dns_query.rsplit('.', 2)[-2:]) if item.dns_query and '.' in item.dns_query else item.dns_query for item in events if item.dns_query}), "unique_dns_query_ratio": safe_ratio(len({item.dns_query for item in events if item.dns_query}), sum(item.dns_query is not None for item in events)), "repeated_destination_ratio": safe_ratio(max(Counter(destinations).values(), default=0), len(destinations)),
            "protocol": event.protocol.upper(), "well_known_dst_port": event.dst_port is not None and event.dst_port < 1024, "ephemeral_src_port": event.src_port is not None and event.src_port >= 49152,
        }
        availability = {name: value is not None for name, value in values.items()}
        for name, available in dns_available.items():
            availability[name] = available
        availability.update({"syn_ratio": tcp_count > 0, "ack_ratio": tcp_count > 0, "rst_ratio": tcp_count > 0, "fin_ratio": tcp_count > 0, "ngram_score": False})
        groups = {group: {name: value for name, value in values.items() if name in names} for group, names in {"traffic": {"packets_total", "bytes_total", "packets_per_sec", "bytes_per_sec", "flows_per_sec"}, "flow": {"flow_duration", "packet_count", "byte_count", "tcp_flag_summary"}, "diversity": {"unique_src_count", "unique_dst_count", "source_ip_entropy", "destination_concentration"}, "temporal": {"iat_mean", "iat_std", "iat_cv", "periodicity_score"}, "dns": set(dns_values), "tls": {"tls_metadata_available", "tls_version", "tls_sni_present", "tls_fingerprint", "tls_ja3", "tls_ja3s", "tls_ja4", "alpn", "packet_size_mean", "packet_size_std"}, "recon": {"fanout_hosts", "fanout_ports", "scan_velocity"}, "direction": {"direction_class", "outbound_bytes", "inbound_bytes", "outbound_inbound_ratio"}}.items()}
        return values, availability, groups

    def _baseline_deviation(self, name: str, current: float) -> float:
        previous = self.baseline.get(name, current)
        self.baseline[name] = (0.8 * previous) + (0.2 * current)
        return current - previous

    @staticmethod
    def _directional(events: list[FlowEvent]) -> dict[str, object]:
        outbound_bytes = sum(item.bytes for item in events if item.direction == "outbound")
        inbound_bytes = sum(item.bytes for item in events if item.direction == "inbound")
        outbound_packets = sum(item.packets for item in events if item.direction == "outbound")
        inbound_packets = sum(item.packets for item in events if item.direction == "inbound")
        return {"outbound_bytes": outbound_bytes if outbound_bytes else None, "inbound_bytes": inbound_bytes if inbound_bytes else None, "outbound_packets": outbound_packets if outbound_packets else None, "inbound_packets": inbound_packets if inbound_packets else None, "outbound_rate": outbound_bytes / 5 if outbound_bytes else None, "inbound_rate": inbound_bytes / 5 if inbound_bytes else None, "outbound_inbound_ratio": safe_ratio(outbound_bytes, inbound_bytes)}

    def status(self) -> dict[str, object]:
        state_counts = self.state.counts()
        average = sum(self.latencies_ms) / len(self.latencies_ms) if self.latencies_ms else 0
        return {"feature_engine_status": "running" if self.running else "stopped", "feature_vectors_per_sec": self.processed, "feature_processing_latency_ms": average, "feature_processing_latency_max_ms": max(self.latencies_ms, default=0), "feature_events_dropped": self.dropped, "feature_errors": self.errors, "recent_feature_vectors": len(self.recent), "feature_queue_size": self.feature_queue.qsize(), "feature_queue_maxsize": settings.event_queue_maxsize, **state_counts, "window_count": len(self.windows.windows)}

    def recent_features(self, flow_id: str | None = None, scope: str | None = None) -> list[FeatureVector]:
        values = list(reversed(self.recent))
        return [item for item in values if (flow_id is None or item.flow_id == flow_id) and (scope is None or item.scope == scope)]


feature_engine = FeatureEngine()
