"""Combine available measured reports without creating placeholder metrics."""
import json
from pathlib import Path
root = Path("reports"); output = root / "final"; output.mkdir(parents=True, exist_ok=True); payload = {}
for path in root.glob("**/*.json"):
    if output not in path.parents:
        try: payload[str(path)] = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError: pass
(output / "metrics.json").write_text(json.dumps(payload, indent=2), encoding="utf-8"); (output / "technical_summary.md").write_text("# Paladin experiment summary\n\nThis report contains only locally generated or explicitly imported measurements. Missing experiments remain absent rather than represented by fabricated values.\n", encoding="utf-8"); print(f"Generated {output}")
