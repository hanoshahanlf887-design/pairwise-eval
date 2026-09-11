"""Annotator mean-shift normalization."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable

from .models import NormalizationStats
from .validation import require_non_empty_string, validate_finite_number


def mean_shift_normalize(
    records: Iterable[dict[str, object]],
    *,
    score_field: str = "score",
    annotator_field: str = "annotator_id",
    output_field: str = "normalized_score",
) -> tuple[list[dict[str, object]], NormalizationStats]:
    rows = [dict(record) for record in records]
    if not rows:
        raise ValueError("normalization requires at least one record")
    scores_by_annotator: dict[str, list[float]] = defaultdict(list)
    checked: list[tuple[str, float]] = []
    for index, row in enumerate(rows):
        if annotator_field not in row:
            raise ValueError(f"record {index}: missing required field: {annotator_field}")
        if score_field not in row:
            raise ValueError(f"record {index}: missing required field: {score_field}")
        annotator = require_non_empty_string(row[annotator_field], annotator_field)
        score = validate_finite_number(row[score_field], score_field)
        scores_by_annotator[annotator].append(score)
        checked.append((annotator, score))
    annotator_means = {
        annotator: sum(values) / len(values)
        for annotator, values in sorted(scores_by_annotator.items())
    }
    global_mean = sum(score for _, score in checked) / len(checked)
    for row, (annotator, score) in zip(rows, checked):
        row[output_field] = score - annotator_means[annotator] + global_mean
    return rows, NormalizationStats(global_mean=global_mean, annotator_means=annotator_means)
