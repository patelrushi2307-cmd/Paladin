"""Prepare a local JSONL/CSV dataset into explicit JSON records."""
import argparse, json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1] / "backend"))
from app.ml.dataset import adapter_for
parser = argparse.ArgumentParser(); parser.add_argument("path", type=Path); parser.add_argument("--output", type=Path, required=True); args = parser.parse_args(); records = list(adapter_for(args.path).records()); args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text("\n".join(json.dumps({**item.values, "label": item.label, "scenario": item.group}) for item in records), encoding="utf-8"); print(f"Prepared {len(records)} records at {args.output}")
