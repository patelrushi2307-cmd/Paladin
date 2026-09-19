"""Central registry for model-ready feature definitions."""

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class FeatureDefinition:
    name: str
    group: str
    data_type: str
    description: str
    method: str
    scope: str
    availability: str
    units: str = ""
    consumers: str = "future detectors"


_NAMES = {
    "packets_total": ("traffic", "int", "Packets observed in the window", "sum(flow.packets)"),
    "bytes_total": ("traffic", "int", "Bytes observed in the window", "sum(flow.bytes)"),
    "packets_per_sec": ("traffic", "float", "Observed packet rate", "packets_total/window_seconds"),
    "bytes_per_sec": ("traffic", "float", "Observed byte rate", "bytes_total/window_seconds"),
    "flows_per_sec": ("traffic", "float", "Observed flow rate", "flow_count/window_seconds"),
    "source_ip_entropy": ("diversity", "float", "Shannon entropy of source IPs", "-sum(p*log2(p))"),
    "destination_concentration": ("diversity", "float", "Largest destination share of bytes", "max(destination_bytes)/total_bytes"),
    "iat_mean": ("temporal", "float", "Mean inter-arrival time", "mean(sorted timestamps delta)"),
    "iat_cv": ("temporal", "float", "Inter-arrival coefficient of variation", "std(iat)/mean(iat)"),
    "periodicity_score": ("temporal", "float", "Behavioral timing regularity indicator", "1/(1+CV)"),
    "dns_query_entropy": ("dns", "float", "Character entropy of normalized query labels", "Shannon entropy"),
    "ngram_score": ("dns", "float", "Reserved n-gram anomaly score", "unavailable until a model is provided"),
    "tls_metadata_available": ("tls", "bool", "Observed TLS metadata exists", "metadata presence"),
    "packet_size_mean": ("tls", "float", "Mean observed packet size", "mean(packet sizes)"),
    "fanout_hosts": ("recon", "int", "Distinct destinations from source", "count(unique destinations)"),
    "fanout_ports": ("recon", "int", "Distinct destination ports from source", "count(unique ports)"),
    "outbound_inbound_ratio": ("direction", "float", "Outbound bytes divided by inbound bytes", "outbound/inbound"),
}


def feature_registry() -> list[FeatureDefinition]:
    return [FeatureDefinition(name, group, data_type, description, method, "FLOW/WINDOW", "source metadata or event timestamps") for name, (group, data_type, description, method) in _NAMES.items()]


def registry_as_dicts() -> list[dict[str, str]]:
    return [asdict(item) for item in feature_registry()]
