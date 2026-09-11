"""Classic sequential Elo ranking for A/B/TIE votes."""

from __future__ import annotations

from collections.abc import Iterable

from .models import EloEntry, PairwiseVote
from .validation import validate_finite_number, validate_preference


def compute_elo(
    votes: Iterable[PairwiseVote],
    *,
    initial_rating: float = 1000.0,
    k_factor: float = 32.0,
) -> list[EloEntry]:
    initial = validate_finite_number(initial_rating, "initial_rating")
    k = validate_finite_number(k_factor, "k_factor")
    if k <= 0:
        raise ValueError("k_factor must be positive")
    ratings: dict[str, float] = {}
    outcomes = {"A": 1.0, "B": 0.0, "TIE": 0.5}
    for vote in votes:
        label = validate_preference(vote.preference)
        left = ratings.setdefault(vote.model_a, initial)
        right = ratings.setdefault(vote.model_b, initial)
        expected_left = 1.0 / (1.0 + 10.0 ** ((right - left) / 400.0))
        actual_left = outcomes[label]
        ratings[vote.model_a] = left + k * (actual_left - expected_left)
        ratings[vote.model_b] = right + k * ((1.0 - actual_left) - (1.0 - expected_left))
    ordered = sorted(ratings.items(), key=lambda pair: (-pair[1], pair[0]))
    return [EloEntry(model_id=model, rating=rating, rank=index) for index, (model, rating) in enumerate(ordered, start=1)]
