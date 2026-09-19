"""Explicit model input selection utilities."""

from ..schemas.feature import FeatureVector


def get_available_features(feature_vector: FeatureVector) -> list[str]:
    return sorted(name for name, available in feature_vector.availability.items() if available)


def get_feature_value(feature_vector: FeatureVector, feature_name: str):
    return feature_vector.values.get(feature_name)


def to_model_vector(feature_vector: FeatureVector, feature_list: list[str]) -> list[float | int | bool]:
    missing = [name for name in feature_list if not feature_vector.availability.get(name, False)]
    if missing:
        raise ValueError(f"Missing required features: {', '.join(missing)}")
    return [feature_vector.values[name] for name in feature_list]
