"""Pairwise consistency predicates and summaries."""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Iterable
from typing import Any

from .models import ConsistencySummary
from .relations import relation
from .validation import VALID_PREFERENCES, validate_finite_number, validate_preference, validate_tolerance


def strict_consistent(preference: str, score_a: float, score_b: float) -> bool:
    label = validate_preference(preference)
    return relation(score_a, score_b) == label


def tolerance_consistent(
    preference: str,
    score_a: float,
    score_b: float,
    tie_tolerance: float,
) -> bool:
    label = validate_preference(preference)
    left = validate_finite_number(score_a, "score_a")
    right = validate_finite_number(score_b, "score_b")
    tolerance = validate_tolerance(tie_tolerance)
    if label == "TIE":
        difference = abs(left - right)
        return difference <= tolerance or math.isclose(
            difference,
            tolerance,
            rel_tol=1e-12,
            abs_tol=1e-12,
        )
    return relation(left, right) == label


def summarize_consistency(
    matched_rows: Iterable[dict[str, Any]],
    total_pair_count: int,
    tie_tolerance: float,
) -> ConsistencySummary:
    tolerance = validate_tolerance(tie_tolerance)
    rows = list(matched_rows)
    if isinstance(total_pair_count, bool) or not isinstance(total_pair_count, int) or total_pair_count < len(rows):
        raise ValueError("total_pair_count must be an integer not smaller than matched rows")

    label_counts = Counter({label: 0 for label in VALID_PREFERENCES})
    strict_hits = Counter({label: 0 for label in VALID_PREFERENCES})
    tolerance_hits = Counter({label: 0 for label in VALID_PREFERENCES})
    for row in rows:
        label = validate_preference(row["preference"])
        left = validate_finite_number(row["score_a"], "score_a")
        right = validate_finite_number(row["score_b"], "score_b")
        label_counts[label] += 1
        strict_hits[label] += int(strict_consistent(label, left, right))
        tolerance_hits[label] += int(tolerance_consistent(label, left, right, tolerance))

    matched = len(rows)
    per_label = {}
    for label in VALID_PREFERENCES:
        count = label_counts[label]
        per_label[label] = {
            "count": count,
            "strict_rate": strict_hits[label] / count if count else None,
            "tolerance_rate": tolerance_hits[label] / count if count else None,
        }
    return ConsistencySummary(
        total_pair_count=total_pair_count,
        matched_pair_count=matched,
        unmatched_pair_count=total_pair_count - matched,
        label_counts=dict(label_counts),
        strict_consistency_rate=sum(strict_hits.values()) / matched if matched else None,
        tolerance_consistency_rate=sum(tolerance_hits.values()) / matched if matched else None,
        per_label_consistency=per_label,
    )
