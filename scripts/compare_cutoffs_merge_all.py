"""Variant of compare_cutoffs.py: merge ALL lifecycle variants of a W- task.

Produces the "all merged" rows of the lifecycle merge table in the report
appendix (step 6 of scripts/reproduce_all.py). Nothing else imports this file,
and the results go to their own files (cutoff_comparison_merged_all*.csv).

compare_cutoffs.py --merge keeps two features per task and move kind
(pause = suspend + resume, execution = schedule + start + complete).
Here every lifecycle variant of a task is summed into ONE column per move kind:

    log_move_W-Validate-application-{schedule,start,suspend,resume,complete,
                                     ate-abort,withdraw}  ->  log_move_W-Validate-application
    model_move_... likewise

The alignments are not recomputed, only the counting changes. A- and O-
activities and start/end have no lifecycle suffix and stay as they are.

Usage (from the repo root):
    uv run python scripts/compare_cutoffs_merge_all.py
    uv run python scripts/compare_cutoffs_merge_all.py --rules
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import compare_cutoffs as cc  # noqa: E402

PATTERN = re.compile(
    r"^(log_move|model_move)_(W-.+)-(suspend|resume|schedule|start|complete|ate-abort|withdraw)$"
)


def merge_all(frame: pd.DataFrame) -> pd.DataFrame:
    """Sum all lifecycle columns of a W- task into one column per move kind."""
    merged: dict[str, list[str]] = {}
    keep: list[str] = []
    for column in frame.columns:
        match = PATTERN.match(column)
        if match:
            kind, task, _suffix = match.groups()
            merged.setdefault(f"{kind}_{task}", []).append(column)
        else:
            keep.append(column)  # case_id, throughput_time, A-/O-/start/end moves
    out = frame[keep].copy()
    for new_column, columns in merged.items():
        out[new_column] = frame[columns].sum(axis=1)
    return out


# Reuse the whole pipeline of compare_cutoffs.py, but with this merge function.
cc.merge_lifecycle = merge_all

if __name__ == "__main__":
    if "--merge" not in sys.argv:
        sys.argv.append("--merge")
    if "--out" not in sys.argv:
        out = cc.ROOT / "data" / "output" / "cutoff_comparison_merged_all.csv"
        sys.argv += ["--out", str(out)]
    cc.main()
