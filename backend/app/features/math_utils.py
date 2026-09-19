"""Pure, JSON-safe streaming feature math."""

from collections import Counter
from math import isfinite, log2, sqrt
from statistics import median
from typing import Any


def finite(value: Any) -> Any:
    if isinstance(value, float) and not isfinite(value):
        return None
    return value


def shannon_entropy(values: list[Any] | tuple[Any, ...]) -> float | None:
    if not values:
        return None
    counts = Counter(values)
    total = len(values)
    return finite(-sum((count / total) * log2(count / total) for count in counts.values()))


def mean(values: list[float]) -> float | None:
    return finite(sum(values) / len(values)) if values else None


def standard_deviation(values: list[float]) -> float | None:
    if not values:
        return None
    average = sum(values) / len(values)
    return finite(sqrt(sum((value - average) ** 2 for value in values) / len(values)))


def coefficient_of_variation(values: list[float]) -> float | None:
    average = mean(values)
    deviation = standard_deviation(values)
    return finite(deviation / average) if average and deviation is not None else None


def periodicity_score(intervals: list[float]) -> float | None:
    if len(intervals) < 2:
        return None
    cv = coefficient_of_variation(intervals)
    if cv is None:
        return None
    return finite(max(0.0, min(1.0, 1.0 / (1.0 + cv))))


def safe_ratio(numerator: float, denominator: float) -> float | None:
    return finite(numerator / denominator) if denominator else None


def numeric_summary(values: list[float]) -> dict[str, float | None]:
    if not values:
        return {"mean": None, "std": None, "min": None, "max": None, "median": None}
    return {"mean": mean(values), "std": standard_deviation(values), "min": min(values), "max": max(values), "median": finite(median(values))}
