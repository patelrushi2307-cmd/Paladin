"""Passive DNS query feature helpers. No resolver is used."""

from collections import Counter
import ipaddress
import re
from .math_utils import shannon_entropy

_LABEL_RE = re.compile(r"^[A-Za-z0-9_-]+$")


def normalize_query(query: str | None) -> tuple[str | None, list[str]]:
    if not query or not isinstance(query, str):
        return None, []
    value = query.strip().lower().rstrip(".")
    try:
        ipaddress.ip_address(value)
        return None, []
    except ValueError:
        pass
    labels = [label for label in value.split(".") if label]
    if not labels or any(not _LABEL_RE.match(label) for label in labels):
        return None, []
    return ".".join(labels), labels


def dns_features(query: str | None, record_type: str | None) -> tuple[dict[str, object], dict[str, bool]]:
    normalized, labels = normalize_query(query)
    if normalized is None:
        return {"dns_query_length": None, "dns_query_entropy": None, "digit_ratio": None, "alphabetic_ratio": None, "numeric_ratio": None, "special_character_ratio": None, "character_diversity": None, "label_count": None, "subdomain_depth": None, "record_type": record_type, "txt_record": None, "ngram_score": None}, {"dns_query_length": False, "dns_query_entropy": False, "digit_ratio": False, "alphabetic_ratio": False, "numeric_ratio": False, "special_character_ratio": False, "character_diversity": False, "label_count": False, "subdomain_depth": False, "record_type": record_type is not None, "txt_record": record_type is not None, "ngram_score": False}
    chars = "".join(labels)
    total = len(chars)
    counts = Counter(chars)
    record = record_type.upper() if record_type else None
    values = {
        "dns_query_length": len(normalized),
        "dns_query_entropy": shannon_entropy(list(chars)),
        "digit_ratio": sum(char.isdigit() for char in chars) / total if total else None,
        "alphabetic_ratio": sum(char.isalpha() for char in chars) / total if total else None,
        "numeric_ratio": sum(char.isnumeric() for char in chars) / total if total else None,
        "special_character_ratio": sum(not char.isalnum() for char in chars) / total if total else None,
        "character_diversity": len(counts) / total if total else None,
        "label_count": len(labels),
        "subdomain_depth": max(0, len(labels) - 2),
        "record_type": record,
        "txt_record": record == "TXT" if record else None,
        "ngram_score": None,
    }
    return values, {name: value is not None for name, value in values.items()}
