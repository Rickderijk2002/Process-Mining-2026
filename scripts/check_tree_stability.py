"""Run the fixed-grid cutoff-14 tree search over multiple random splits."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd

from classification import BAD, GOOD, DeviationTree, label_throughput


def main() -> None:
    args = _parse_args()
    encodings_path = _resolve(args.encodings)
    output_path = _resolve(args.output)
    if output_path.exists():
        raise FileExistsError(f"refusing to overwrite existing results: {output_path}")

    frame = pd.read_csv(encodings_path)
    labels = label_throughput(frame["throughput_time"], args.cutoff)
    rows: list[dict[str, object]] = []

    for seed in args.seeds:
        result = DeviationTree(
            random_state=seed,
            test_size=args.test_size,
        ).fit(frame, args.cutoff, holdout=True, search=True)
        precision = result.held_out_precision
        recall = result.held_out_recall
        if precision is None or recall is None:
            raise RuntimeError("holdout scores were not produced")
        f1 = (
            0.0
            if precision + recall == 0
            else 2 * precision * recall / (precision + recall)
        )
        rows.append(
            {
                "seed": seed,
                "cutoff_days": args.cutoff,
                "rows": len(frame),
                "good": int((labels == GOOD).sum()),
                "bad": int((labels == BAD).sum()),
                "precision_bad": precision,
                "recall_bad": recall,
                "f1_bad": f1,
                "rules": len(result.rules),
                "best_params": json.dumps(result.best_params, sort_keys=True),
            }
        )

    results = pd.DataFrame(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("x", newline="", encoding="utf-8") as output_file:
        results.to_csv(output_file, index=False)
    print(results.to_string(index=False))
    print(
        "mean: "
        f"precision={results['precision_bad'].mean():.3f}, "
        f"recall={results['recall_bad'].mean():.3f}, "
        f"f1={results['f1_bad'].mean():.3f}, "
        f"rules={results['rules'].mean():.2f}"
    )
    print(
        "range: "
        f"precision={results['precision_bad'].min():.3f}-"
        f"{results['precision_bad'].max():.3f}, "
        f"recall={results['recall_bad'].min():.3f}-{results['recall_bad'].max():.3f}, "
        f"f1={results['f1_bad'].min():.3f}-{results['f1_bad'].max():.3f}, "
        f"rules={results['rules'].min()}-{results['rules'].max()}"
    )
    print(f"wrote stability results: {output_path}")


def _resolve(path: str) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return ROOT / candidate


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check tree stability using the fixed classification grid."
    )
    parser.add_argument(
        "--encodings",
        default="data/output/alignment_encodings.csv",
        help="Path to the alignment encoding table (relative to the project root).",
    )
    parser.add_argument("--cutoff", type=float, default=14.0)
    parser.add_argument("--test-size", type=float, default=0.25)
    parser.add_argument(
        "--seeds",
        type=int,
        nargs="+",
        default=[0, 1, 2, 3],
        help="Random states to check; defaults to the locked seed and three variants.",
    )
    parser.add_argument(
        "--output",
        default="data/output/tree_stability_cutoff14_pruned_2026-10-06.csv",
        help="New CSV path for stability results; existing files are never replaced.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
