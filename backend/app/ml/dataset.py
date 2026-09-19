"""Local dataset adapters and quality inspection."""
from __future__ import annotations
from dataclasses import dataclass
import csv, hashlib, json
from pathlib import Path
from typing import Any, Iterable

CANONICAL_LABELS = ["BENIGN", "DDOS", "RECON", "C2_BEACON", "DATA_EXFILTRATION", "DGA_DNS_TUNNEL", "ENCRYPTED_MALWARE"]

@dataclass
class DatasetRecord:
    values: dict[str, Any]
    label: str | None
    group: str

class DatasetAdapter:
    def records(self) -> Iterable[DatasetRecord]: raise NotImplementedError

class JsonlDatasetAdapter(DatasetAdapter):
    def __init__(self, path: Path, label_field: str = "label", group_field: str = "scenario") -> None: self.path, self.label_field, self.group_field = path, label_field, group_field
    def records(self):
        with self.path.open(encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    data = json.loads(line); yield DatasetRecord(data, data.get(self.label_field), str(data.get(self.group_field, self.path.stem)))

class FlowCsvDatasetAdapter(DatasetAdapter):
    def __init__(self, path: Path, label_field: str = "label", group_field: str = "scenario") -> None: self.path, self.label_field, self.group_field = path, label_field, group_field
    def records(self):
        with self.path.open(newline="", encoding="utf-8") as handle:
            for data in csv.DictReader(handle): yield DatasetRecord(data, data.get(self.label_field), str(data.get(self.group_field, self.path.stem)))

class PcapDatasetAdapter(DatasetAdapter):
    def __init__(self, path: Path): self.path = path
    def records(self):
        # PCAP parsing belongs to passive ingest; training adapters should map prepared flow exports.
        raise NotImplementedError("Prepare PCAP through the passive flow pipeline before training")

def adapter_for(path: Path) -> DatasetAdapter:
    if path.suffix.lower() in {".jsonl", ".json"}: return JsonlDatasetAdapter(path)
    if path.suffix.lower() == ".csv": return FlowCsvDatasetAdapter(path)
    if path.suffix.lower() in {".pcap", ".pcapng"}: return PcapDatasetAdapter(path)
    raise ValueError(f"Unsupported dataset format: {path.suffix}")

def inspect_records(records: list[DatasetRecord]) -> dict[str, Any]:
    keys = sorted({key for record in records for key in record.values})
    hashes = [hashlib.sha256(json.dumps(record.values, sort_keys=True, default=str).encode()).hexdigest() for record in records]
    labels: dict[str, int] = {}
    for record in records: labels[record.label or "MISSING"] = labels.get(record.label or "MISSING", 0) + 1
    missing = {key: sum(record.values.get(key) in (None, "") for record in records) for key in keys}
    invalid = {key: sum(str(record.values.get(key)).lower() in {"nan", "inf", "-inf", "infinity", "-infinity"} for record in records) for key in keys}
    return {"row_count": len(records), "feature_count": len(keys), "features": keys, "missing_by_feature": missing, "missing_label_count": labels.get("MISSING", 0), "duplicate_count": len(hashes) - len(set(hashes)), "class_distribution": labels, "invalid_values": invalid, "groups": sorted({record.group for record in records})}
