"""Strict JSON and JSONL readers with source-aware error messages."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import DimensionScore, PairwiseVote
from .validation import require_non_empty_string, validate_dimensions, validate_preference, validate_weights


class InputError(ValueError):
    """Raised when an input file or record violates the data contract."""


def _required(row: dict[str, Any], field: str) -> Any:
    if field not in row:
        raise ValueError(f"missing required field: {field}")
    return row[field]


def _read_jsonl_objects(path: str | Path) -> list[tuple[int, dict[str, Any]]]:
    source = Path(path)
    records: list[tuple[int, dict[str, Any]]] = []
    try:
        with source.open("r", encoding="utf-8") as handle:
            for line_number, raw_line in enumerate(handle, start=1):
                if not raw_line.strip():
                    continue
                try:
                    value = json.loads(raw_line)
                except json.JSONDecodeError as exc:
                    raise InputError(f"{source}: line {line_number}: invalid JSON: {exc.msg}") from exc
                if not isinstance(value, dict):
                    raise InputError(f"{source}: line {line_number}: JSON value must be an object")
                records.append((line_number, value))
    except OSError as exc:
        raise InputError(f"{source}: unable to read file: {exc}") from exc
    return records


def read_pairwise_votes(path: str | Path) -> list[PairwiseVote]:
    source = Path(path)
    votes: list[PairwiseVote] = []
    for line_number, row in _read_jsonl_objects(source):
        try:
            model_a = require_non_empty_string(_required(row, "model_a"), "model_a")
            model_b = require_non_empty_string(_required(row, "model_b"), "model_b")
            if model_a == model_b:
                raise ValueError("model_a and model_b must be different")
            votes.append(
                PairwiseVote(
                    item_id=require_non_empty_string(_required(row, "item_id"), "item_id"),
                    model_a=model_a,
                    model_b=model_b,
                    preference=validate_preference(_required(row, "preference")),
                )
            )
        except ValueError as exc:
            raise InputError(f"{source}: line {line_number}: {exc}") from exc
    return votes


def read_dimension_scores(path: str | Path) -> list[DimensionScore]:
    source = Path(path)
    scores: list[DimensionScore] = []
    for line_number, row in _read_jsonl_objects(source):
        try:
            scores.append(
                DimensionScore(
                    item_id=require_non_empty_string(_required(row, "item_id"), "item_id"),
                    model_id=require_non_empty_string(_required(row, "model_id"), "model_id"),
                    annotator_id=require_non_empty_string(_required(row, "annotator_id"), "annotator_id"),
                    dimensions=validate_dimensions(_required(row, "dimensions")),
                )
            )
        except ValueError as exc:
            raise InputError(f"{source}: line {line_number}: {exc}") from exc
    return scores


def read_weights(path: str | Path) -> dict[str, float]:
    source = Path(path)
    try:
        with source.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except json.JSONDecodeError as exc:
        raise InputError(f"{source}: invalid JSON: {exc.msg}") from exc
    except OSError as exc:
        raise InputError(f"{source}: unable to read file: {exc}") from exc
    try:
        return validate_weights(value)
    except ValueError as exc:
        raise InputError(f"{source}: {exc}") from exc
