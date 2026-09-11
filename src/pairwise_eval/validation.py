"""Validation helpers shared across readers and algorithms."""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

VALID_PREFERENCES = ("A", "B", "TIE")


def require_non_empty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value


def validate_preference(value: Any) -> str:
    if value not in VALID_PREFERENCES or not isinstance(value, str):
        raise ValueError("preference must be one of: A, B, TIE")
    return value


def validate_finite_number(value: Any, field: str = "score") -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be a finite number (bool is not allowed)")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{field} must be a finite number")
    return result


def validate_tolerance(value: Any) -> float:
    tolerance = validate_finite_number(value, "tie_tolerance")
    if tolerance < 0:
        raise ValueError("tie_tolerance must be non-negative")
    return tolerance


def validate_dimensions(value: Any) -> dict[str, float]:
    if not isinstance(value, Mapping) or not value:
        raise ValueError("dimensions must be a non-empty object")
    result: dict[str, float] = {}
    for name, score in value.items():
        dimension = require_non_empty_string(name, "dimension name")
        result[dimension] = validate_finite_number(score, f"dimensions.{dimension}")
    return result


def validate_weights(value: Any) -> dict[str, float]:
    if not isinstance(value, Mapping) or not value:
        raise ValueError("weights must be a non-empty JSON object")
    result: dict[str, float] = {}
    for name, weight in value.items():
        dimension = require_non_empty_string(name, "weight name")
        numeric = validate_finite_number(weight, f"weights.{dimension}")
        if numeric < 0:
            raise ValueError(f"weights.{dimension} must be non-negative")
        result[dimension] = numeric
    if sum(result.values()) <= 0:
        raise ValueError("weights must have a positive total")
    return result
