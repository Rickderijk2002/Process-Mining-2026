"""Run the whole reproducible chain with one command and check it against the stored results.

Steps, in order (each one calls the script named in brackets):
  1. align every trace and fit the first tree           (src/main.py, cutoff 14)
  2. refit the locked cutoff 14 result, seed 0           (scripts/fit_tree.py)
  3. stability check over the seeds 0 to 3               (scripts/check_tree_stability.py)
  4. cutoff comparison 14, 18, 21                        (scripts/compare_cutoffs.py)
  5. lifecycle merge: pause and execution                (scripts/compare_cutoffs.py --merge)
  6. lifecycle merge: one column per task                (scripts/compare_cutoffs_merge_all.py)
  7. the F1 per cutoff figure                            (scripts/plot_cutoff_comparison.py)
  8. with --toys: both toy validations                   (make_toy*, align_toy*, evaluate_toy_alignments, check_toy*_rules)

Everything is written to --out-dir (default data/output/reproduced/), so the stored
results in data/output/ and docs/Report/figures/ are never overwritten. At the end every new
file is compared with its stored counterpart and reported as identical or different.

Usage (from the repo root):
    uv run python scripts/reproduce_all.py                 # full chain, several minutes
    uv run python scripts/reproduce_all.py --skip-align    # reuse data/output/alignment_encodings.csv
    uv run python scripts/reproduce_all.py --sample 50     # quick check: align 50 traces, fit one tree
    uv run python scripts/reproduce_all.py --toys          # also run both toy validations

With --sample only steps 1 and 2 run and nothing is compared, because a sample gives
different numbers by design.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STORED = ROOT / "data" / "output"
STORED_FIGURE = ROOT / "docs" / "Report" / "figures" / "f1_by_cutoff.png"
LOCKED = "cutoff14_pruned_2026-10-06"


def main() -> int:
    args = _parse_args()
    out = args.out_dir if args.out_dir.is_absolute() else ROOT / args.out_dir
    out.mkdir(parents=True, exist_ok=True)
    py = [sys.executable]
    started = time.time()

    if args.skip_align:
        encodings = STORED / "alignment_encodings.csv"
    else:
        encodings = out / "alignment_encodings.csv"
        step(
            "1. align all traces, fit the first tree",
            py + ["src/main.py", "--cutoff", "14"]
            + (["--sample", str(args.sample)] if args.sample else [])
            + ["--export-encodings", rel(encodings),
               "--rules", rel(out / "tree_rules.csv"),
               "--export-cases", rel(out / "tree_rule_cases.csv")],
        )

    step(
        "2. refit the locked cutoff 14 result (seed 0)",
        py + ["scripts/fit_tree.py", "--encodings", rel(encodings), "--cutoff", "14",
              "--random-state", "0",
              "--output", rel(out / f"tree_rules_{LOCKED}.csv"),
              "--export-cases", rel(out / f"tree_rule_cases_{LOCKED}.csv")],
    )

    if not args.sample:
        stability = out / f"tree_stability_{LOCKED}.csv"
        stability.unlink(missing_ok=True)  # the script refuses to overwrite
        step(
            "3. stability over the seeds 0 to 3",
            py + ["scripts/check_tree_stability.py", "--encodings", rel(encodings),
                  "--cutoff", "14", "--seeds", "0", "1", "2", "3",
                  "--output", rel(stability)],
        )
        step(
            "4. cutoff comparison 14, 18, 21",
            py + ["scripts/compare_cutoffs.py", "--data", rel(encodings),
                  "--out", rel(out / "cutoff_comparison.csv")],
        )
        step(
            "5. lifecycle merge: pause and execution",
            py + ["scripts/compare_cutoffs.py", "--data", rel(encodings), "--merge",
                  "--out", rel(out / "cutoff_comparison_merged.csv")],
        )
        step(
            "6. lifecycle merge: one column per task",
            py + ["scripts/compare_cutoffs_merge_all.py", "--data", rel(encodings),
                  "--out", rel(out / "cutoff_comparison_merged_all.csv")],
        )
        step(
            "7. F1 per cutoff figure",
            py + ["scripts/plot_cutoff_comparison.py",
                  "--data", rel(out / "cutoff_comparison.csv"),
                  "--out", rel(out / "f1_by_cutoff.png")],
        )

    if args.toys:
        step("8a. linear toy: write log and net", py + ["scripts/make_toy.py"])
        step("8b. linear toy: align", py + ["scripts/align_toy.py"])
        step(
            "8c. linear toy: alignments against the gold standard",
            py + ["scripts/evaluate_toy_alignments.py",
                  "--plot", rel(out / "toy_alignment_gold_vs_pred.png")],
        )
        step("8d. linear toy: planted rule", py + ["scripts/check_toy_rules.py"])
        step("8e. parallel toy: write log and net", py + ["scripts/make_toy_parallel.py"])
        step("8f. parallel toy: align", py + ["scripts/align_toy_parallel.py"])
        step(
            "8g. parallel toy: alignments against the gold standard",
            py + ["scripts/evaluate_toy_alignments.py",
                  "--gold", "data/gold/toy_parallel_alignment_gold.csv",
                  "--log", "data/raw/toy_parallel.xes",
                  "--pnml", "data/raw/toy_parallel.pnml",
                  "--plot", rel(out / "toy_parallel_alignment_gold_vs_pred.png"),
                  "--title", "Parallel toy: gold vs predicted"],
        )
        step("8h. parallel toy: planted rule", py + ["scripts/check_toy_parallel_rules.py"])

    minutes = (time.time() - started) / 60
    print(f"\nAll steps finished in {minutes:.1f} minutes. Outputs: {rel(out)}")
    if args.sample:
        print("Sample run: nothing compared with the stored results.")
        return 0
    return 0 if compare(out, args.skip_align) else 1


def step(title: str, command: list[str]) -> None:
    print(f"\n=== {title}", flush=True)
    result = subprocess.run(command, cwd=ROOT)
    if result.returncode != 0:
        sys.exit(f"Step failed ({result.returncode}): {' '.join(command)}")


def compare(out: Path, skip_align: bool) -> bool:
    pairs: list[tuple[Path, Path]] = []
    if not skip_align:
        pairs.append((out / "alignment_encodings.csv", STORED / "alignment_encodings.csv"))
    for name in (
        f"tree_rules_{LOCKED}.csv",
        f"tree_rule_cases_{LOCKED}.csv",
        f"tree_stability_{LOCKED}.csv",
    ):
        pairs.append((out / name, STORED / name))
    for stem in ("cutoff_comparison", "cutoff_comparison_merged", "cutoff_comparison_merged_all"):
        for suffix in ("", "_seeds", "_rules"):
            pairs.append((out / f"{stem}{suffix}.csv", STORED / f"{stem}{suffix}.csv"))
    pairs.append((out / "f1_by_cutoff.png", STORED_FIGURE))

    print("\n=== Comparison with the stored results")
    all_same = True
    for new, stored in pairs:
        if not new.exists() or not stored.exists():
            print(f"  MISSING    {rel(new)}  (stored: {rel(stored)})")
            all_same = False
        elif same_content(new, stored):
            print(f"  identical  {rel(new)}")
        else:
            print(f"  DIFFERENT  {rel(new)}  (stored: {rel(stored)})")
            all_same = False
    print("\nResult:", "everything reproduces exactly." if all_same else "differences found, see above.")
    return all_same


def same_content(a: Path, b: Path) -> bool:
    first, second = a.read_bytes(), b.read_bytes()
    if a.suffix == ".csv":  # ignore line-ending differences between Windows and Linux
        first, second = first.replace(b"\r\n", b"\n"), second.replace(b"\r\n", b"\n")
    return first == second


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out-dir", type=Path, default=Path("data/output/reproduced"),
                        help="where the new files go (default: data/output/reproduced)")
    parser.add_argument("--skip-align", action="store_true",
                        help="reuse data/output/alignment_encodings.csv instead of aligning again")
    parser.add_argument("--sample", type=int, default=None,
                        help="quick check: align only the first N traces and fit one tree")
    parser.add_argument("--toys", action="store_true", help="also run both toy validations")
    args = parser.parse_args()
    if args.sample and args.skip_align:
        parser.error("--sample and --skip-align cannot be combined")
    return args


if __name__ == "__main__":
    sys.exit(main())
