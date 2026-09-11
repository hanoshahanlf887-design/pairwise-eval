"""Convert two numerical scores into an A/B/TIE relation."""

from __future__ import annotations

from .validation import validate_finite_number


def relation(score_a: float, score_b: float) -> str:
    left = validate_finite_number(score_a, "score_a")
    right = validate_finite_number(score_b, "score_b")
    if left > right:
        return "A"
    if right > left:
        return "B"
    return "TIE"
