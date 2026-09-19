"""Feature engine status and bounded inspection API."""

from fastapi import APIRouter, HTTPException, Query
from ..features.engine import feature_engine
from ..features.registry import registry_as_dicts
from ..schemas.feature import FeatureStatus, FeatureVector

router = APIRouter(prefix="/api/features", tags=["features"])


@router.get("/status", response_model=FeatureStatus)
def feature_status() -> FeatureStatus:
    return FeatureStatus.model_validate(feature_engine.status())


@router.get("/recent", response_model=list[FeatureVector])
def recent_features(flow_id: str | None = Query(default=None), scope: str | None = Query(default=None)) -> list[FeatureVector]:
    return feature_engine.recent_features(flow_id, scope)


@router.get("/registry")
def feature_registry() -> list[dict[str, str]]:
    return registry_as_dicts()


@router.get("/{feature_id}", response_model=FeatureVector)
def feature_by_id(feature_id: str) -> FeatureVector:
    for vector in feature_engine.recent:
        if vector.feature_id == feature_id:
            return vector
    raise HTTPException(status_code=404, detail="Feature vector not found")
