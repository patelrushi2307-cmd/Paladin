"""Train one threat model from prepared local JSONL records."""
import argparse, json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1] / "backend"))
from app.ml.training import train_tabular
parser = argparse.ArgumentParser(); parser.add_argument("threat_class"); parser.add_argument("dataset", type=Path); parser.add_argument("--output", type=Path); parser.add_argument("--seed", type=int, default=42); args = parser.parse_args(); records = [json.loads(line) for line in args.dataset.read_text(encoding="utf-8").splitlines() if line.strip()]; output = args.output or Path("models/trained") / args.threat_class; print(json.dumps(train_tabular(records, args.threat_class, output, args.seed), indent=2))
