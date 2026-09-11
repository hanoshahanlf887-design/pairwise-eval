"""Typed records used by the public API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PairwiseVote:
    item_id: str
    model_a: str
    model_b: str
    preference: str


@dataclass(frozen=True)
class DimensionScore:
    item_id: str
    model_id: str
    annotator_id: str
    dimensions: dict[str, float]


@dataclass(frozen=True)
class NormalizationStats:
    global_mean: float
    annotator_means: dict[str, float]


@dataclass(frozen=True)
class EloEntry:
    model_id: str
    rating: float
    rank: int


@dataclass(frozen=True)
class ConsistencySummary:
    total_pair_count: int
    matched_pair_count: int
    unmatched_pair_count: int
    label_counts: dict[str, int]
    strict_consistency_rate: float | None
    tolerance_consistency_rate: float | None
    per_label_consistency: dict[str, dict[str, Any]]
