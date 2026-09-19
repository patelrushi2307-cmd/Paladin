"""Local project health check."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1] / "backend"))
from app.config import settings
from app.dependencies import get_alert_repository, get_alert_service
from app.detectors.engine import detection_engine
from app.features.registry import feature_registry
from app.ml.registry import ModelRegistry
checks = {"configuration": settings.event_queue_maxsize > 0, "database": get_alert_repository().database_path.parent.exists(), "feature_registry": bool(feature_registry()), "detectors": len(detection_engine.detectors) == 6, "alert_service": get_alert_service() is not None, "model_registry": ModelRegistry().root.exists(), "scenarios": (Path(__file__).parents[1] / "data" / "raw" / "scenarios").exists()}
for name, passed in checks.items(): print(f"{name}: {'PASS' if passed else 'FAIL'}")
sys.exit(0 if all(checks.values()) else 1)
