# pairwise-eval

`pairwise-eval` is a small, dependency-free Python toolkit for comparing pairwise human preferences with numerical evaluation scores. It provides strict and TIE-tolerant consistency metrics, multidimensional score aggregation, annotator mean-shift normalization, and classic Elo ranking.

The project is designed for evaluation practitioners who need a transparent analysis pipeline without adopting a large evaluation framework.

## What problem does it solve?

Evaluation datasets often contain two complementary signals:

- **Pairwise preferences**, where an annotator chooses response A, response B, or TIE.
- **Absolute scores**, where each response receives one or more numerical dimension scores.

This toolkit aggregates the numerical scores, matches them to the two models named in each pairwise vote, and measures whether both signals imply the same ordering.

## Methods

### Pairwise relation and strict consistency

For two numerical scores, the derived relation is `A` when A is higher, `B` when B is higher, and `TIE` when they are equal. Strict consistency requires the derived relation to exactly equal the human preference.

### TIE tolerance consistency

Tolerance changes only human `TIE` labels. A TIE is consistent when:

```text
abs(score_a - score_b) <= tie_tolerance
```

Human `A` and `B` labels still require the correct strict direction. The default tolerance is `0.0`; choose a value appropriate for your score scale.

### Multidimensional aggregation

Mean aggregation averages every dimension in a record. Weighted aggregation computes:

```text
sum(score_i * weight_i) / sum(weight_i)
```

Dimension names are unrestricted. In weighted mode, every record must contain exactly the same dimension names as the weights file. Weights must be finite and non-negative, with a positive total.

Multiple records for the same `(item_id, model_id)` are averaged after each record has been reduced to one scalar score.

### Annotator mean-shift normalization

For each annotation record, the dimension scores are first reduced to one scalar using the selected mean or weighted aggregation. Optional normalization then adjusts these record-level scalar scores before they are averaged at the `(item_id, model_id)` level:

```text
normalized_score = raw_scalar_score - annotator_mean + global_mean
```

The normalization population is all valid dimension-score records supplied to that command. The global mean and every annotator mean are computed from the resulting scalar scores in that same population. These statistics are specific to the selected aggregation: mean and weighted aggregation each compute their own annotator and global means from their own scalar scores. This is mean-shift normalization, which adjusts annotator-level mean offsets but does not normalize variance or model nonlinear annotator bias. Annotator means can be unstable when an annotator has few records.

### Elo ranking

Pairwise outcomes are scored as A win `1.0`, B win `0.0`, and TIE `0.5`. Initial rating and K-factor are configurable. This is classic sequential Elo, so ratings are sensitive to input order.

## Installation

Python 3.10 or newer is required. Runtime has no third-party dependencies.

```bash
python -m venv .venv
python -m pip install -e .
```

You can then use `pairwise-eval`. During development, commands can also be run without installation by setting `PYTHONPATH=src` and using `python -m pairwise_eval`.

## Quick start

```bash
pairwise-eval rank examples/pairwise_votes.jsonl
pairwise-eval aggregate examples/dimension_scores.jsonl
pairwise-eval aggregate examples/dimension_scores.jsonl --weights examples/weights.json --normalize-annotators
pairwise-eval consistency examples/pairwise_votes.jsonl examples/dimension_scores.jsonl --normalize-annotators --tie-tolerance 0.25
```

Add `--json` to any command for structured JSON output.

## Example output

```text
Pairs: 5 total, 4 matched, 1 unmatched
Labels: A=2 B=1 TIE=1
Strict consistency: 0.750
Tolerance consistency: 1.000 (tie tolerance=0.25)
```

Unmatched votes are included in the total and unmatched counts, but consistency rates use matched votes only. Per-label counts also refer to matched votes.

## Data formats

Pairwise votes are JSONL objects:

```json
{"item_id":"item_001","model_a":"model_alpha","model_b":"model_beta","preference":"A"}
```

Dimension scores are JSONL objects:

```json
{"item_id":"item_001","model_id":"model_alpha","annotator_id":"annotator_01","dimensions":{"quality_1":4.2,"quality_2":3.8}}
```

Weights are one JSON object:

```json
{"quality_1":1.0,"quality_2":1.0}
```

JSONL validation is strict and fail-fast. Errors identify the file and line number. Empty lines are ignored; missing fields, invalid labels, booleans, NaN, infinity, and malformed values are rejected.

## Matching contract

The `consistency` command first produces one score for every `(item_id, model_id)`. It then matches a vote only when scores exist for both `(item_id, model_a)` and `(item_id, model_b)`. No category mapping or fallback matching is performed.

## Project structure

```text
src/pairwise_eval/   library and CLI implementation
examples/            fully synthetic input files
tests/               standard-library unittest suite
```

## Run tests

```bash
python -m unittest discover -s tests -v
```

## Methodological limitations

- Consistency measures agreement between two signals; it does not establish correctness.
- Tolerance is scale-dependent and must be chosen deliberately.
- Mean-shift normalization assumes an additive annotator effect and needs adequate observations per annotator.
- Aggregation can hide disagreement between dimensions or annotators.
- Sequential Elo depends on vote order and does not provide uncertainty estimates.
- Missing pairs are reported but excluded from consistency-rate denominators.

## License

MIT
