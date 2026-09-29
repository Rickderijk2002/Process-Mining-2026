"""Fit a classification tree on a saved alignment encoding table."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd

from classification import (
    BAD,
    GOOD,
    DeviationTree,
    label_throughput,
    rules_to_case_frame,
    rules_to_frame,
)


def main() -> None:
    args = _parse_args()
    encodings_path = _resolve(args.encodings)
    output_path = _resolve(args.output)

    frame = pd.read_csv(encodings_path)
    labels = label_throughput(frame["throughput_time"], args.cutoff)
    result = DeviationTree(
        random_state=args.random_state,
        test_size=args.test_size,
    ).fit(frame, args.cutoff, holdout=True, search=True)

    rules_frame = rules_to_frame(result.rules)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rules_frame.to_csv(output_path, index=False)

    n_good = int((labels == GOOD).sum())
    n_bad = int((labels == BAD).sum())

    print(f"rows:                 {len(frame)}")
    print(f"cutoff days:          {args.cutoff}")
    print(f"class balance:        good={n_good} bad={n_bad}")
    print(f"best params:          {result.best_params}")
    print(f"held-out precision:   {result.held_out_precision}")
    print(f"held-out recall:      {result.held_out_recall}")
    print(f"rules:                {len(result.rules)}")
    print(f"wrote rules:          {output_path}")

    if args.export_cases:
        cases_path = _resolve(args.export_cases)
        cases_path.parent.mkdir(parents=True, exist_ok=True)
        rules_to_case_frame(result.rules).to_csv(cases_path, index=False)
        print(f"wrote cases:          {cases_path}")


def _resolve(path: str) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return ROOT / candidate


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fit a deviation classification tree on an encoding CSV."
    )
    parser.add_argument(
        "--encodings",
        default="data/output/alignment_encodings.csv",
        help="Path to the alignment encoding table (relative to the project root).",
    )
    parser.add_argument(
        "--cutoff",
        type=float,
        required=True,
        help="Throughput cutoff in days. Cases at or below are good.",
    )
    parser.add_argument(
        "--output",
        default="data/output/tree_rules.csv",
        help="Path for the leaf-rule table (relative to the project root).",
    )
    parser.add_argument(
        "--export-cases",
        default=None,
        help=(
            "Optional path for rule_id,case_id rows "
            "(e.g. data/output/tree_rule_cases.csv)."
        ),
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.25,
        help="Held-out fraction for evaluation.",
    )
    parser.add_argument(
        "--random-state",
        type=int,
        default=0,
        help="Random seed for the train/test split and the tree.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
