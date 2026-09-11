"""Mean and user-configured weighted aggregation."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Mapping

from .models import DimensionScore
from .validation import validate_dimensions, validate_weights


def mean_dimensions(dimensions: Mapping[str, float]) -> float:
    values = validate_dimensions(dimensions)
    return sum(values.values()) / len(values)


def weighted_dimensions(dimensions: Mapping[str, float], weights: Mapping[str, float]) -> float:
    values = validate_dimensions(dimensions)
    checked_weights = validate_weights(weights)
    value_names = set(values)
    weight_names = set(checked_weights)
    if value_names != weight_names:
        missing = sorted(weight_names - value_names)
        unexpected = sorted(value_names - weight_names)
        details = []
        if missing:
            details.append(f"missing dimensions: {', '.join(missing)}")
        if unexpected:
            details.append(f"dimensions without weights: {', '.join(unexpected)}")
        raise ValueError("dimension and weight names must match; " + "; ".join(details))
    total_weight = sum(checked_weights.values())
    return sum(values[name] * checked_weights[name] for name in checked_weights) / total_weight


def aggregate_records(records: Iterable[DimensionScore], weights: Mapping[str, float] | None = None) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[float]] = defaultdict(list)
    counts: dict[tuple[str, str], int] = defaultdict(int)
    for record in records:
        value = mean_dimensions(record.dimensions) if weights is None else weighted_dimensions(record.dimensions, weights)
        key = (record.item_id, record.model_id)
        grouped[key].append(value)
        counts[key] += 1
    return [
        {
            "item_id": item_id,
            "model_id": model_id,
            "score": sum(grouped[(item_id, model_id)]) / len(grouped[(item_id, model_id)]),
            "record_count": counts[(item_id, model_id)],
        }
        for item_id, model_id in sorted(grouped)
    ]
