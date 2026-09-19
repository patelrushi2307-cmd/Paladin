"""Validate the small benign JSONL seed file without generating alerts."""
import json
from pathlib import Path

path = Path(__file__).parents[1] / "data" / "raw" / "benign_flows.jsonl"
records = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
print(f"Loaded {len(records)} benign normalized flow events from {path}")
