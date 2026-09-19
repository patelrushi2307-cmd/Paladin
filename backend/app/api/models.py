"""Model registry status API."""
from fastapi import APIRouter
from ..ml.registry import ModelRegistry
router = APIRouter(prefix="/api/models", tags=["models"])
_registry = ModelRegistry()
@router.get("/status")
def model_status(): return _registry.status()
