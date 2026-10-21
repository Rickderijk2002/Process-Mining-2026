"""Plot the F1 of the slow class per cutoff against the all-slow baseline.

Reads the summary written by scripts/compare_cutoffs.py and draws grouped bars:
the all-slow baseline, the tree with uniform class weights and the tree with
balanced class weights. Error bars are one standard deviation over seeds.

Usage (from the repo root):
    uv run python scripts/plot_cutoff_comparison.py
    uv run python scripts/plot_cutoff_comparison.py --data data/output/cutoff_comparison.csv --out docs/figures/f1_by_cutoff.png
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
GRID = "#e4e3df"
BASELINE = "#a9a8a3"  # neutral grey: the reference, not a model
UNWEIGHTED = "#2a78d6"  # categorical slot 1
BALANCED = "#eb6834"  # categorical slot 2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data", type=Path, default=ROOT / "data" / "output" / "cutoff_comparison.csv"
    )
    parser.add_argument(
        "--out", type=Path, default=ROOT / "docs" / "Report" / "figures" / "f1_by_cutoff.png"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    table = pd.read_csv(args.data)
    cutoffs = sorted(table["cutoff"].unique())

    unweighted = table[table["variant"] == "unweighted"].set_index("cutoff").loc[cutoffs]
    balanced = table[table["variant"] == "balanced"].set_index("cutoff").loc[cutoffs]
    baseline = unweighted["baseline_f1"].to_numpy()

    x = np.arange(len(cutoffs))
    width = 0.26
    fig, ax = plt.subplots(figsize=(6.5, 3.1), dpi=200)
    fig.patch.set_facecolor("white")

    ax.bar(x - width, baseline, width, color=BASELINE, label="All slow (baseline)", zorder=3)
    ax.bar(
        x, unweighted["f1_mean"], width, color=UNWEIGHTED, label="Tree, uniform weights",
        yerr=unweighted["f1_sd"], error_kw={"ecolor": INK, "elinewidth": 1, "capsize": 3},
        zorder=3,
    )
    ax.bar(
        x + width, balanced["f1_mean"], width, color=BALANCED, label="Tree, balanced weights",
        yerr=balanced["f1_sd"], error_kw={"ecolor": INK, "elinewidth": 1, "capsize": 3},
        hatch="///", edgecolor="white", linewidth=0, zorder=3,
    )

    ax.set_xticks(x)
    ax.set_xticklabels([f"{c:g} days" for c in cutoffs], color=INK)
    ax.set_ylabel("F1 of the slow class (hold-out)", color=INK_SECONDARY)
    ax.set_ylim(0, 0.9)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(INK_SECONDARY)
    ax.tick_params(axis="y", length=0, colors=INK_SECONDARY)
    ax.tick_params(axis="x", length=0)
    ax.legend(frameon=False, loc="upper right", ncol=3, fontsize=8, bbox_to_anchor=(1.0, 1.12))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(args.out, facecolor="white")
    print(f"Saved {args.out}")


if __name__ == "__main__":
    main()
