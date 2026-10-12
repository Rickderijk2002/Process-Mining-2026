"""Compare classification trees across throughput cutoffs and seeds.

Variants:
  unweighted  class_weight fixed to None
  balanced    class_weight fixed to "balanced"
  searched    grid search chooses class_weight in {None, "balanced"}

Each cutoff is compared with its own all-bad baseline (precision = slow share,
recall = 1, F1 = 2p / (1 + p)). Scores are hold-out scores, reported as mean
and standard deviation over seeds.

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
sys.path.insert(0, str(ROOT / "src"))

from classification.model import DEFAULT_PARAM_GRID, DeviationTree  # noqa: E402

VARIANTS = {
    "unweighted": {**DEFAULT_PARAM_GRID, "class_weight": [None]},
    "balanced": {**DEFAULT_PARAM_GRID, "class_weight": ["balanced"]},
    "searched": {**DEFAULT_PARAM_GRID, "class_weight": [None, "balanced"]},
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data",
        type=Path,
        default=ROOT / "data" / "output" / "alignment_encodings.csv",
    )
    parser.add_argument("--cutoffs", type=float, nargs="+", default=[14, 18, 21])
    parser.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 3])
    parser.add_argument("--rules", action="store_true", help="print leaf rules")
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "data" / "output" / "cutoff_comparison.csv",
        help="summary CSV; per-seed and rules CSVs are written next to it",
    )
    return parser.parse_args()


def f1(precision: float, recall: float) -> float:
    total = precision + recall
    return 2 * precision * recall / total if total else 0.0


def main() -> None:
    args = parse_args()
    frame = pd.read_csv(args.data)
    first_seed = args.seeds[0]

    seed_rows = []
    rule_rows = []
    slow_share = {
        cutoff: float((frame["throughput_time"] > cutoff).mean())
        for cutoff in args.cutoffs
    }

    for variant, grid in VARIANTS.items():
        for cutoff in args.cutoffs:
            for seed in args.seeds:
                print(f"{variant:<11} cutoff {cutoff:g}  seed {seed} ...", flush=True)
                result = DeviationTree(random_state=seed, param_grid=grid).fit(
                    frame, cutoff
                )
                precision = result.held_out_precision
                recall = result.held_out_recall
                params = result.best_params
                seed_rows.append(
                    {
                        "variant": variant,
                        "cutoff": cutoff,
                        "seed": seed,
                        "class_weight": params.get("class_weight"),
                        "ccp_alpha": params.get("ccp_alpha"),
                        "max_depth": params.get("max_depth"),
                        "min_samples_leaf": params.get("min_samples_leaf"),
                        "rules": len(result.rules),
                        "slow_rules": sum(
                            r.predicted_class == "bad" for r in result.rules
                        ),
                        "precision": precision,
                        "recall": recall,
                        "f1": f1(precision, recall),
                    }
                )
                if seed == first_seed:
                    for rule in result.rules:
                        rule_rows.append(
                            {"variant": variant, "cutoff": cutoff, **rule.as_row()}
                        )
                    if args.rules:
                        print(f"\n=== {variant}, cutoff {cutoff:g}, seed {seed} ===")
                        for rule in result.rules:
                            print(rule.as_row())
                        print()

    per_seed = pd.DataFrame(seed_rows)
    summary = (
        per_seed.groupby(["variant", "cutoff"], sort=False)
        .agg(
            prec_mean=("precision", "mean"),
            prec_sd=("precision", "std"),
            rec_mean=("recall", "mean"),
            rec_sd=("recall", "std"),
            f1_mean=("f1", "mean"),
            f1_sd=("f1", "std"),
            rules_mean=("rules", "mean"),
            rules_min=("rules", "min"),
            rules_max=("rules", "max"),
            balanced_picked=("class_weight", lambda s: int((s == "balanced").sum())),
        )
        .reset_index()
    )
    summary.insert(2, "slow_share", summary["cutoff"].map(slow_share))
    summary.insert(3, "baseline_prec", summary["slow_share"])
    summary.insert(
        4, "baseline_f1", summary["slow_share"].map(lambda p: 2 * p / (1 + p))
    )
    summary.insert(5, "n_seeds", len(args.seeds))
    summary = summary.fillna(0.0).round(3)

    pd.set_option("display.width", 250, "display.max_columns", 30)
    print(f"\nSeeds: {args.seeds}\n")
    print(summary.to_string(index=False))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    seeds_path = args.out.with_name(args.out.stem + "_seeds.csv")
    rules_path = args.out.with_name(args.out.stem + "_rules.csv")
    summary.to_csv(args.out, index=False)
    per_seed.round(3).to_csv(seeds_path, index=False)
    pd.DataFrame(rule_rows).to_csv(rules_path, index=False)
    print(f"\nSaved {args.out}\nSaved {seeds_path}\nSaved {rules_path}")


if __name__ == "__main__":
    main()