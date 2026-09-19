"""Inspect a local dataset without changing it."""
import argparse, json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1] / "backend"))
from app.ml.dataset import adapter_for, inspect_records
parser = argparse.ArgumentParser(); parser.add_argument("path", type=Path); parser.add_argument("--output", type=Path)
args = parser.parse_args(); report = inspect_records(list(adapter_for(args.path).records())); print(json.dumps(report, indent=2));
if args.output: args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
