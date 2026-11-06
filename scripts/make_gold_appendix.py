"""Build the gold-standard appendix material for the report.

Aligns both toy logs, compares the move counts with the hand-written gold CSVs,
recovers the planted rule with a depth-1 tree, and writes
  docs/Report/gold_table.md      (table included by the report appendix)
  docs/Report/figures/toy_nets.png  (both nets side by side)

Usage (from the repo root):
    uv run python scripts/make_gold_appendix.py
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.image as mpimg  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
import pm4py  # noqa: E402
from pm4py.visualization.petri_net import visualizer as vis  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import check_toy_parallel_rules as parallel_rules  # noqa: E402
import check_toy_rules as linear_rules  # noqa: E402
from alignment import Aligner, Encoder  # noqa: E402
from classification import DeviationTree, bad_case_ids, case_set_scores  # noqa: E402
from data_kpi import DataLoader  # noqa: E402

REPORT = ROOT / "docs" / "Report"

# What is wrong with each trace, in the words of docs/toy.md and docs/toy_parallel.md.
TOYS = {
    "linear": {
        "stem": "toy",
        "gold": "toy_alignment_gold.csv",
        "rules": linear_rules,
        "trace": {"t1": "A B C", "t2": "A C", "t3": "A B B C", "t4": "A B B B C", "t5": "A A C"},
        "issue": {"t1": "fits", "t2": "B missing", "t3": "extra B", "t4": "two extra B", "t5": "extra A, B missing"},
    },
    "parallel": {
        "stem": "toy_parallel",
        "gold": "toy_parallel_alignment_gold.csv",
        "rules": parallel_rules,
        "trace": {"p1": "A B C D F", "p2": "A C B E F", "p3": "A B D F", "p4": "A B B C D F", "p5": "A B C D", "p6": "A A B C E F"},
        "issue": {"p1": "fits", "p2": "fits (C before B, branch E)", "p3": "C missing", "p4": "extra B", "p5": "F missing", "p6": "extra A"},
    },
}


def run_toy(spec: dict) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    loader = DataLoader()
    log = loader.load_log(ROOT / "data" / "raw" / f"{spec['stem']}.xes")
    net, im, fm = loader.load_petri_net(ROOT / "data" / "raw" / f"{spec['stem']}.pnml")
    pred = Aligner.align_log(log, net, im, fm, Encoder.activities_from_model(net)).encodings
    gold = pd.read_csv(ROOT / "data" / "gold" / spec["gold"])
    cols = [c for c in gold.columns if c != "case_id"]
    pred = pred.set_index("case_id").loc[gold["case_id"], cols].reset_index()
    assert (gold[cols].to_numpy() == pred[cols].to_numpy()).all(), "aligner differs from gold"

    rules = spec["rules"]
    enc = Aligner.align_log(log, net, im, fm, Encoder.activities_from_model(net)).encodings
    enc["throughput_time"] = enc["case_id"].map(rules.THROUGHPUT)
    tree = DeviationTree().fit(enc, rules.CUTOFF, holdout=False, search=False, max_depth=1)
    scores = case_set_scores(bad_case_ids(tree.rules), rules.EXPECTED_BAD)
    return gold, pred, {"rules": tree.rules, "scores": scores, "spec_rules": rules}


def moves(row: pd.Series) -> str:
    out = [f"{c.split('_')[0]} move {c.split('_')[-1]}" + (f" ×{int(v)}" if v > 1 else "") for c, v in row.items() if v > 0]
    return ", ".join(out) if out else "none"


rows = []
rule_notes = []
for name, spec in TOYS.items():
    gold, pred, res = run_toy(spec)
    rules = res["spec_rules"]
    cols = [c for c in gold.columns if c != "case_id"]
    for _, g in gold.iterrows():
        cid = g["case_id"]
        rows.append({
            "Toy": name,
            "Trace": f"{cid}: {spec['trace'][cid]}",
            "Deviation": spec["issue"][cid],
            "Gold = aligner": moves(g[cols]),
            "Days": f"{rules.THROUGHPUT[cid]:g}",
            "Slow": "yes" if cid in rules.EXPECTED_BAD else "no",
        })
    s = res["scores"]
    rule_notes.append(f"{name}: planted slow = {sorted(rules.EXPECTED_BAD)}, recovered = {sorted(bad_case_ids(res['rules']))}, "
                      f"precision {s['precision']:.1f}, recall {s['recall']:.1f}")

table = pd.DataFrame(rows)
t = table.drop(columns="Toy")
md = "\n".join(
    ["| " + " | ".join(t.columns) + " |", "|" + "|".join(":--" for _ in t.columns) + "|"]
    + ["| " + " | ".join(r) + " |" for r in t.astype(str).itertuples(index=False)]
)
(REPORT / "gold_table.md").write_text(md + "\n")
print(md)
print("\n".join(rule_notes))

# nets side by side
fig, axes = plt.subplots(2, 1, figsize=(7.2, 2.2), gridspec_kw={"height_ratios": [0.55, 1]})
with tempfile.TemporaryDirectory() as tmp:
    for ax, (name, spec), title in zip(axes, TOYS.items(), ("(a) Linear toy", "(b) Parallel and choice toy")):
        net, im, fm = pm4py.read_pnml(str(ROOT / "data" / "raw" / f"{spec['stem']}.pnml"))
        g = vis.apply(net, im, fm, parameters={"format": "png", "rankdir": "LR", "bgcolor": "white"})
        p = Path(tmp) / f"{name}.png"
        vis.save(g, str(p))
        ax.imshow(mpimg.imread(p)); ax.axis("off"); ax.set_title(title, fontsize=8)
fig.subplots_adjust(hspace=0.15, left=0, right=1, top=0.94, bottom=0)
fig.savefig(REPORT / "figures" / "toy_nets.png", dpi=250, bbox_inches="tight", pad_inches=0.02)
print("saved")
