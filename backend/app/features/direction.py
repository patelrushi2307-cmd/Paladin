"""Local-only internal/external direction classification."""

import ipaddress
from collections.abc import Iterable


def parse_networks(value: str | Iterable[str]) -> list[ipaddress._BaseNetwork]:
    entries = value.split(",") if isinstance(value, str) else value
    networks = []
    for entry in entries:
        try:
            networks.append(ipaddress.ip_network(entry.strip()))
        except (ValueError, TypeError):
            continue
    return networks


def is_internal_ip(address: str, networks: list[ipaddress._BaseNetwork]) -> bool | None:
    try:
        ip = ipaddress.ip_address(address)
    except ValueError:
        return None
    return any(ip in network for network in networks)


def classify_direction(src_ip: str, dst_ip: str, networks: list[ipaddress._BaseNetwork]) -> str:
    source_internal = is_internal_ip(src_ip, networks)
    destination_internal = is_internal_ip(dst_ip, networks)
    if source_internal is None or destination_internal is None:
        return "UNKNOWN"
    if source_internal and destination_internal:
        return "INTERNAL_INTERNAL"
    if not source_internal and not destination_internal:
        return "EXTERNAL_EXTERNAL"
    return "OUTBOUND" if source_internal else "INBOUND"
