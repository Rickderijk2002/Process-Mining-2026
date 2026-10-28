"""Write the per-seed results table of the report appendix.

Reads data/output/cutoff_comparison_seeds.csv (from scripts/compare_cutoffs.py)
and writes docs/Report/seed_table.md: the tree at 14 days, and the balanced
tree at 18 and 21 days, one row per seed with the selected parameters.

Usage (from the repo root):
    uv run python scripts/make_seed_table.py
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
seeds = pd.read_csv(ROOT / "data" / "output" / "cutoff_comparison_seeds.csv")

keep = seeds[
    ((seeds.cutoff == 14) & (seeds.variant == "unweighted"))
    | ((seeds.cutoff.isin([18, 21])) & (seeds.variant == "balanced"))
].sort_values(["cutoff", "seed"])

header = ["Cutoff", "Seed", "Depth", "Leaf", "$\\alpha$", "Rules", "Precision", "Recall", "F1"]
lines = ["| " + " | ".join(header) + " |", "|" + "|".join(":" + "-" * 10 for _ in header) + "|"]
for r in keep.itertuples():
    lines.append(
        f"| {r.cutoff} days | {r.seed} | {r.max_depth} | {r.min_samples_leaf} | {r.ccp_alpha:g} "
        f"| {r.rules} | {r.precision:.3f} | {r.recall:.3f} | {r.f1:.3f} |"
    )
(ROOT / "docs" / "Report" / "seed_table.md").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
