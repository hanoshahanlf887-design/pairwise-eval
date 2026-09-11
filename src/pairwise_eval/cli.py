"""Command-line interface for pairwise-eval."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from typing import Any

from .analysis import analyze_consistency, prepare_scores
from .elo import compute_elo
from .io import InputError, read_dimension_scores, read_pairwise_votes, read_weights


def _add_common_score_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--weights", help="JSON file mapping every dimension name to a non-negative weight")
    parser.add_argument("--normalize-annotators", action="store_true", help="Apply annotator mean-shift before item/model aggregation")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Print machine-readable JSON")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pairwise-eval", description="Analyze pairwise preferences and multidimensional scores.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    rank = subparsers.add_parser("rank", help="Rank models from pairwise votes with sequential Elo")
    rank.add_argument("votes", help="Pairwise vote JSONL file")
    rank.add_argument("--initial-rating", type=float, default=1000.0)
    rank.add_argument("--k-factor", type=float, default=32.0)
    rank.add_argument("--json", action="store_true", dest="json_output")

    aggregate = subparsers.add_parser("aggregate", help="Aggregate multidimensional score records")
    aggregate.add_argument("scores", help="Dimension score JSONL file")
    _add_common_score_options(aggregate)

    consistency = subparsers.add_parser("consistency", help="Compare pairwise votes with aggregated numerical scores")
    consistency.add_argument("votes", help="Pairwise vote JSONL file")
    consistency.add_argument("scores", help="Dimension score JSONL file")
    consistency.add_argument("--tie-tolerance", type=float, default=0.0, help="Non-negative tolerance used only for TIE labels")
    _add_common_score_options(consistency)
    return parser


def _print_json(value: Any) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def _run_rank(args: argparse.Namespace) -> None:
    votes = read_pairwise_votes(args.votes)
    entries = compute_elo(votes, initial_rating=args.initial_rating, k_factor=args.k_factor)
    result = {
        "vote_count": len(votes),
        "initial_rating": args.initial_rating,
        "k_factor": args.k_factor,
        "ranking": [asdict(entry) for entry in entries],
    }
    if args.json_output:
        _print_json(result)
        return
    print(f"Votes: {len(votes)} | Initial rating: {args.initial_rating:g} | K-factor: {args.k_factor:g}")
    print("Rank  Model                 Rating")
    for entry in entries:
        print(f"{entry.rank:>4}  {entry.model_id:<20}  {entry.rating:>8.2f}")


def _run_aggregate(args: argparse.Namespace) -> None:
    records = read_dimension_scores(args.scores)
    weights = read_weights(args.weights) if args.weights else None
    rows, normalization = prepare_scores(records, weights=weights, normalize_annotators=args.normalize_annotators)
    result = {
        "input_record_count": len(records),
        "output_group_count": len(rows),
        "aggregation": "weighted" if weights is not None else "mean",
        "annotator_normalization": args.normalize_annotators,
        "scores": rows,
    }
    if normalization is not None:
        result["normalization"] = normalization
    if args.json_output:
        _print_json(result)
        return
    print(f"Input records: {len(records)} | Output groups: {len(rows)}")
    print(f"Aggregation: {result['aggregation']} | Annotator normalization: {args.normalize_annotators}")
    print("Item          Model                 Score  Records")
    for row in rows:
        print(f"{row['item_id']:<13} {row['model_id']:<20} {row['score']:>7.3f} {row['record_count']:>8}")


def _rate(value: float | None) -> str:
    return "N/A" if value is None else f"{value:.3f}"


def _run_consistency(args: argparse.Namespace) -> None:
    votes = read_pairwise_votes(args.votes)
    scores = read_dimension_scores(args.scores)
    weights = read_weights(args.weights) if args.weights else None
    result = analyze_consistency(
        votes,
        scores,
        weights=weights,
        normalize_annotators=args.normalize_annotators,
        tie_tolerance=args.tie_tolerance,
    )
    if args.json_output:
        _print_json(result)
        return
    print(f"Pairs: {result['total_pair_count']} total, {result['matched_pair_count']} matched, {result['unmatched_pair_count']} unmatched")
    counts = result["label_counts"]
    print(f"Labels: A={counts['A']} B={counts['B']} TIE={counts['TIE']}")
    print(f"Strict consistency: {_rate(result['strict_consistency_rate'])}")
    print(f"Tolerance consistency: {_rate(result['tolerance_consistency_rate'])} (tie tolerance={args.tie_tolerance:g})")
    for label, details in result["per_label_consistency"].items():
        print(f"  {label}: count={details['count']} strict={_rate(details['strict_rate'])} tolerance={_rate(details['tolerance_rate'])}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
        if args.command == "rank":
            _run_rank(args)
        elif args.command == "aggregate":
            _run_aggregate(args)
        else:
            _run_consistency(args)
    except (InputError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0
