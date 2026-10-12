"""Compare classification trees across throughput cutoffs.

Runs the DeviationTree for each cutoff, with and without class balancing, and
prints one summary table plus the leaf rules. Each cutoff is scored against
its own all-bad baseline (precision = share of slow cases, recall = 1).

Usage (from the repo root):
    uv run python scripts/compare_cutoffs.py
    uv run python scripts/compare_cutoffs.py --cutoffs 14 18 21 --seeds 0 1 2 3 4
    uv run python scripts/compare_cutoffs.py --rules
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))  # change if model.py lives elsewhere

from classification.model import DEFAULT_PARAM_GRID, DeviationTree  # noqa: E402

VARIANTS = {
    "unweighted": DEFAULT_PARAM_GRID,
    "balanced": {**DEFAULT_PARAM_GRID, "class_weight": ["balanced"]},
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data", type=Path, default=ROOT / "data" / "output" / "alignment_encodings.csv"
    )
    parser.add_argument("--cutoffs", type=float, nargs="+", default=[14, 18, 21])
    parser.add_argument("--seeds", type=int, nargs="+", default=[0])
    parser.add_argument("--rules", action="store_true", help="print leaf rules")
    parser.add_argument(
        "--out", type=Path, default=ROOT / "data" / "output" / "cutoff_comparison.csv"
    )
    return parser.parse_args()


def f1(precision: float, recall: float) -> float:
    total = precision + recall
    return 2 * precision * recall / total if total else 0.0


def main() -> None:
    args = parse_args()
    frame = pd.read_csv(args.data)
    rows = []
    rule_rows = []

    for variant, grid in VARIANTS.items():
        for cutoff in args.cutoffs:
            slow_share = float((frame["throughput_time"] > cutoff).mean())
            runs = []
            for seed in args.seeds:
                result = DeviationTree(random_state=seed, param_grid=grid).fit(
                    frame, cutoff
                )
                runs.append(result)
                if seed == args.seeds[0]:
                    for rule in result.rules:
                        rule_rows.append(
                            {"variant": variant, "cutoff": cutoff, **rule.as_row()}
                        )
                if args.rules and seed == args.seeds[0]:
                    print(f"\n=== {variant}, cutoff {cutoff:g}, seed {seed} ===")
                    for rule in result.rules:
                        print(rule.as_row())

            precisions = [r.held_out_precision for r in runs]
            recalls = [r.held_out_recall for r in runs]
            first = runs[0]
            rows.append(
                {
                    "variant": variant,
                    "cutoff": cutoff,
                    "slow_share": round(slow_share, 3),
                    "baseline_prec": round(slow_share, 3),
                    "params": first.best_params,
                    "depth": first.estimator.get_depth(),
                    "rules": len(first.rules),
                    "slow_rules": sum(r.predicted_class == "bad" for r in first.rules),
                    "test_prec": round(sum(precisions) / len(precisions), 3),
                    "test_rec": round(sum(recalls) / len(recalls), 3),
                    "test_f1": round(
                        sum(f1(p, r) for p, r in zip(precisions, recalls))
                        / len(runs),
                        3,
                    ),
                }
            )

    table = pd.DataFrame(rows)
    pd.set_option("display.width", 250, "display.max_colwidth", 80)
    print(f"\nSeeds: {args.seeds} (scores averaged; params and rules from first seed)\n")
    print(table.to_string(index=False))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(args.out, index=False)
    rules_path = args.out.with_name(args.out.stem + "_rules.csv")
    pd.DataFrame(rule_rows).to_csv(rules_path, index=False)
    print(f"\nSaved {args.out}\nSaved {rules_path}")


if __name__ == "__main__":
    main()