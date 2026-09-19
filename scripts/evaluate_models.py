"""Summarize registered model metadata; evaluation metrics are never invented."""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1] / "backend"))
from app.ml.registry import ModelRegistry
report = ModelRegistry().list(); Path("reports/models").mkdir(parents=True, exist_ok=True); Path("reports/models/summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8"); print(json.dumps(report, indent=2))
