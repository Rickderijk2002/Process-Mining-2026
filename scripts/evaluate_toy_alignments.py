"""Score toy aligner encodings against a hand gold CSV.

Defaults: linear toy. For the parallel toy:

    uv run python scripts/evaluate_toy_alignments.py \\
      --gold data/gold/toy_parallel_alignment_gold.csv \\
      --log data/raw/toy_parallel.xes \\
      --pnml data/raw/toy_parallel.pnml \\
      --plot data/output/toy_parallel_alignment_gold_vs_pred.png
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from alignment import Aligner, Encoder
from data_kpi import DataLoader

MOVE_PREFIXES = ("model_move_", "log_move_")


def move_columns(frame: pd.DataFrame) -> list[str]:
    return [c for c in frame.columns if c.startswith(MOVE_PREFIXES)]


def count_scores(gold: pd.DataFrame, pred: pd.DataFrame, cols: list[str]) -> dict[str, float]:
    """Micro precision/recall treating each move count as tokens.

    For every case and every move column:
    TP += min(gold, pred), FP += max(pred - gold, 0), FN += max(gold - pred, 0).
    """
    true_positive = 0
    false_positive = 0
    false_negative = 0
    for col in cols:
        g = gold[col].to_numpy(dtype=int)
        p = pred[col].to_numpy(dtype=int)
        true_positive += int(np.minimum(g, p).sum())
        false_positive += int(np.maximum(p - g, 0).sum())
        false_negative += int(np.maximum(g - p, 0).sum())

    precision = (
        true_positive / (true_positive + false_positive)
        if true_positive + false_positive
        else 1.0
    )
    recall = (
        true_positive / (true_positive + false_negative)
        if true_positive + false_negative
        else 1.0
    )
    return {
        "true_positive": float(true_positive),
        "false_positive": float(false_positive),
        "false_negative": float(false_negative),
        "precision": precision,
        "recall": recall,
    }


def plot_side_by_side(
    gold: pd.DataFrame,
    pred: pd.DataFrame,
    cols: list[str],
    path: Path,
    title: str = "Toy alignment: gold vs predicted move counts",
) -> None:
    cases = gold["case_id"].tolist()
    g_mat = gold[cols].to_numpy(dtype=float)
    p_mat = pred[cols].to_numpy(dtype=float)

    fig, axes = plt.subplots(1, 2, figsize=(12, 3.8), sharey=True, layout="constrained")
    for ax, mat, panel in (
        (axes[0], g_mat, "Gold (hand)"),
        (axes[1], p_mat, "Predicted (aligner)"),
    ):
        im = ax.imshow(mat, aspect="auto", cmap="Blues", vmin=0, vmax=max(2, mat.max()))
        ax.set_title(panel)
        ax.set_xticks(range(len(cols)))
        ax.set_xticklabels(cols, rotation=45, ha="right", fontsize=7)
        ax.set_yticks(range(len(cases)))
        ax.set_yticklabels(cases)
        for i in range(mat.shape[0]):
            for j in range(mat.shape[1]):
                ax.text(j, i, int(mat[i, j]), ha="center", va="center", color="black")

    fig.colorbar(im, ax=axes.ravel().tolist(), shrink=0.8, label="move count")
    fig.suptitle(title, fontsize=12)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--gold",
        type=Path,
        default=ROOT / "data" / "gold" / "toy_alignment_gold.csv",
    )
    parser.add_argument(
        "--log",
        type=Path,
        default=ROOT / "data" / "raw" / "toy.xes",
    )
    parser.add_argument(
        "--pnml",
        type=Path,
        default=ROOT / "data" / "raw" / "toy.pnml",
    )
    parser.add_argument(
        "--plot",
        type=Path,
        default=ROOT / "data" / "output" / "toy_alignment_gold_vs_pred.png",
    )
    parser.add_argument(
        "--title",
        default="Toy alignment: gold vs predicted move counts",
    )
    args = parser.parse_args()

    gold_path = args.gold if args.gold.is_absolute() else ROOT / args.gold
    log_path = args.log if args.log.is_absolute() else ROOT / args.log
    pnml_path = args.pnml if args.pnml.is_absolute() else ROOT / args.pnml
    plot_path = args.plot if args.plot.is_absolute() else ROOT / args.plot

    gold = pd.read_csv(gold_path)
    if "case_id" not in gold.columns:
        raise ValueError(f"gold CSV must have case_id: {gold_path}")

    loader = DataLoader()
    log = loader.load_log(log_path)
    net, initial_marking, final_marking = loader.load_petri_net(pnml_path)
    activities = Encoder.activities_from_model(net)
    pred = Aligner.align_log(
        log, net, initial_marking, final_marking, activities
    ).encodings

    cols = move_columns(gold)
    missing = [c for c in cols if c not in pred.columns]
    if missing:
        raise ValueError(f"predicted encodings missing columns: {missing}")

    gold = gold.sort_values("case_id").reset_index(drop=True)
    pred = (
        pred[["case_id", *cols]]
        .sort_values("case_id")
        .reset_index(drop=True)
    )
    if list(gold["case_id"]) != list(pred["case_id"]):
        raise ValueError(
            f"case_id mismatch\ngold={list(gold['case_id'])}\npred={list(pred['case_id'])}"
        )

    match = (gold[cols].to_numpy() == pred[cols].to_numpy()).all(axis=1)
    scores = count_scores(gold, pred, cols)
    plot_side_by_side(gold, pred, cols, plot_path, title=args.title)

    print("gold path:            ", gold_path)
    print("cases exact match:    ", int(match.sum()), "/", len(match))
    print("mismatched cases:     ", gold.loc[~match, "case_id"].tolist() or "none")
    print("count TP / FP / FN:   ", scores["true_positive"], scores["false_positive"], scores["false_negative"])
    print("alignment precision:  ", scores["precision"])
    print("alignment recall:     ", scores["recall"])
    print("plot saved:           ", plot_path)
    print()
    print("gold:")
    print(gold[["case_id", *cols]].to_string(index=False))
    print()
    print("predicted:")
    print(pred[["case_id", *cols]].to_string(index=False))


if __name__ == "__main__":
    main()
