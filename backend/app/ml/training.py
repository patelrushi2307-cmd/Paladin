"""Reproducible lightweight tabular training helpers."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
import numpy as np

DEFAULT_FEATURES = {
    "ddos": ["packets_per_sec", "bytes_per_sec", "flows_per_sec", "unique_src_count", "source_ip_entropy", "destination_concentration", "syn_ratio", "ack_ratio", "udp_ratio"],
    "recon": ["fanout_hosts", "fanout_ports", "scan_velocity", "unique_dst_hosts", "unique_dst_ports", "syn_ratio", "destination_ip_entropy"],
    "c2": ["iat_mean", "iat_std", "iat_cv", "periodicity_score", "repeated_destination_ratio", "destination_concentration", "flow_duration"],
    "exfil": ["outbound_bytes", "inbound_bytes", "outbound_rate", "outbound_inbound_ratio", "flow_duration", "bytes_total", "destination_concentration"],
    "dga": ["dns_query_entropy", "dns_query_length", "digit_ratio", "character_diversity", "label_count", "subdomain_depth"],
    "dns_tunnel": ["dns_query_length", "dns_query_entropy", "dns_query_count", "unique_dns_query_count", "unique_dns_query_ratio", "subdomain_depth"],
    "encrypted": ["packet_size_mean", "packet_size_std", "iat_mean", "iat_std", "iat_cv", "periodicity_score", "flow_duration", "bytes_total", "packets_total"],
}

def prepare_matrix(records: list[dict[str, Any]], features: list[str]) -> tuple[np.ndarray, np.ndarray]:
    rows, labels = [], []
    for record in records:
        rows.append([float(record.get(feature, 0) or 0) for feature in features]); labels.append(record.get("label", "BENIGN"))
    return np.asarray(rows, dtype=float), np.asarray(labels)

def train_tabular(records: list[dict[str, Any]], threat_class: str, output: Path, seed: int = 42) -> dict[str, Any]:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import Pipeline
    from sklearn.model_selection import GroupShuffleSplit
    from sklearn.metrics import classification_report, confusion_matrix
    features = DEFAULT_FEATURES[threat_class]; x, y = prepare_matrix(records, features); groups = np.asarray([record.get("scenario", "default") for record in records])
    if len(set(y)) < 2: raise ValueError("Training requires at least two label classes")
    splitter = GroupShuffleSplit(n_splits=1, test_size=.2, random_state=seed); train_idx, test_idx = next(splitter.split(x, y, groups))
    pipeline = Pipeline([("imputer", SimpleImputer(strategy="median")), ("model", RandomForestClassifier(n_estimators=100, random_state=seed, class_weight="balanced"))]); pipeline.fit(x[train_idx], y[train_idx]); predictions = pipeline.predict(x[test_idx])
    metrics = classification_report(y[test_idx], predictions, output_dict=True, zero_division=0)
    output.mkdir(parents=True, exist_ok=True); artifact = output / f"{threat_class}-rf-1.0.0.joblib"; import joblib; joblib.dump(pipeline, artifact)
    metadata = {"model_id": f"{threat_class}-rf-1.0.0", "threat_class": threat_class, "algorithm": "RandomForestClassifier", "feature_list": features, "feature_schema_version": "1.0", "calibration_status": "NOT_CALIBRATED", "random_seed": seed, "split_strategy": "grouped scenario split", "metrics": metrics, "confusion_matrix": confusion_matrix(y[test_idx], predictions).tolist(), "artifact_path": str(artifact)}
    (output / "metadata.json").write_text(json.dumps(metadata, indent=2, default=str), encoding="utf-8"); return metadata
