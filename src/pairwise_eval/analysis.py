"""End-to-end aggregation and pair matching."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import asdict

from .aggregation import aggregate_records, mean_dimensions, weighted_dimensions
from .consistency import summarize_consistency
from .models import DimensionScore, PairwiseVote
from .normalization import mean_shift_normalize


def prepare_scores(
    records: Iterable[DimensionScore],
    *,
    weights: Mapping[str, float] | None = None,
    normalize_annotators: bool = False,
) -> tuple[list[dict[str, object]], dict[str, object] | None]:
    records_list = list(records)
    scalar_rows = []
    for record in records_list:
        score = mean_dimensions(record.dimensions) if weights is None else weighted_dimensions(record.dimensions, weights)
        scalar_rows.append(
            {
                "item_id": record.item_id,
                "model_id": record.model_id,
                "annotator_id": record.annotator_id,
                "score": score,
            }
        )
    stats = None
    if normalize_annotators and scalar_rows:
        normalized, normalization_stats = mean_shift_normalize(scalar_rows)
        scalar_rows = [{**row, "score": row["normalized_score"]} for row in normalized]
        stats = asdict(normalization_stats)
    synthetic_records = [
        DimensionScore(
            item_id=str(row["item_id"]),
            model_id=str(row["model_id"]),
            annotator_id=str(row["annotator_id"]),
            dimensions={"aggregated_score": float(row["score"])},
        )
        for row in scalar_rows
    ]
    return aggregate_records(synthetic_records), stats


def analyze_consistency(
    votes: Iterable[PairwiseVote],
    scores: Iterable[DimensionScore],
    *,
    weights: Mapping[str, float] | None = None,
    normalize_annotators: bool = False,
    tie_tolerance: float = 0.0,
) -> dict[str, object]:
    vote_list = list(votes)
    aggregated, normalization = prepare_scores(
        scores,
        weights=weights,
        normalize_annotators=normalize_annotators,
    )
    score_index = {(row["item_id"], row["model_id"]): row["score"] for row in aggregated}
    matched = []
    for vote in vote_list:
        left = score_index.get((vote.item_id, vote.model_a))
        right = score_index.get((vote.item_id, vote.model_b))
        if left is None or right is None:
            continue
        matched.append({"preference": vote.preference, "score_a": left, "score_b": right})
    summary = summarize_consistency(matched, len(vote_list), tie_tolerance)
    result = asdict(summary)
    result["tie_tolerance"] = tie_tolerance
    result["aggregation"] = "weighted" if weights is not None else "mean"
    if normalization is not None:
        result["normalization"] = normalization
    return result
