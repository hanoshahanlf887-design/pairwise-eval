"""Utilities for pairwise evaluation analysis."""

from .aggregation import mean_dimensions, weighted_dimensions
from .consistency import strict_consistent, tolerance_consistent
from .elo import compute_elo
from .normalization import mean_shift_normalize
from .relations import relation

__all__ = [
    "compute_elo",
    "mean_dimensions",
    "mean_shift_normalize",
    "relation",
    "strict_consistent",
    "tolerance_consistent",
    "weighted_dimensions",
]

__version__ = "0.1.0"
