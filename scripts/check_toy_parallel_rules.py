"""Plant a throughput rule on the parallel toy and recover it with the tree.

Same idea as check_toy_rules.py, but on AND + XOR encodings.
Planted story (hand):
  Cutoff 10 days. Extra B (log_move_B) is the slow signal — same *kind* of
  rule as the linear toy, so you can compare the two scripts.
  p4 is the only case with an extra B, so it is the only planted bad case.
  p3 still misses C, but we make it fast on purpose: not every deviation is bad.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from alignment import Aligner, Encoder
from classification import (
    DeviationTree,
    bad_case_ids,
    case_set_scores,
    rules_to_frame,
)
from data_kpi import DataLoader

CUTOFF = 10.0
THROUGHPUT = {
    "p1": 5.0,   # perfect, fast
    "p2": 6.0,   # perfect (other order/branch), fast
    "p3": 8.0,   # missing C, but still fast (deviation ≠ bad)
    "p4": 25.0,  # extra B, slow  ← planted bad
    "p5": 7.0,   # missing F, fast
    "p6": 9.0,   # extra A, fast
}
EXPECTED_BAD = {"p4"}


def main() -> None:
    loader = DataLoader()
    log = loader.load_log(ROOT / "data" / "raw" / "toy_parallel.xes")
    net, initial_marking, final_marking = loader.load_petri_net(
        ROOT / "data" / "raw" / "toy_parallel.pnml"
    )

    activities = Encoder.activities_from_model(net)
    encodings = Aligner.align_log(
        log,
        net,
        initial_marking,
        final_marking,
        activities,
    ).encodings

    encodings["throughput_time"] = encodings["case_id"].map(THROUGHPUT)
    if encodings["throughput_time"].isna().any():
        missing = encodings.loc[encodings["throughput_time"].isna(), "case_id"].tolist()
        raise ValueError(f"missing planted throughput for cases: {missing}")

    result = DeviationTree().fit(
        encodings,
        CUTOFF,
        holdout=False,
        search=False,
        max_depth=1,
    )

    predicted_bad = bad_case_ids(result.rules)
    scores = case_set_scores(predicted_bad, EXPECTED_BAD)

    print("cutoff days:          ", CUTOFF)
    print("planted throughput:   ", THROUGHPUT)
    print("expected bad cases:   ", sorted(EXPECTED_BAD))
    print("predicted bad cases:  ", sorted(predicted_bad))
    print("rule precision:       ", scores["precision"])
    print("rule recall:          ", scores["recall"])
    print("best params:          ", result.best_params)
    print(rules_to_frame(result.rules).to_string(index=False))
    print()
    print("planted rule (hand):  log_move_B at least once -> bad")


if __name__ == "__main__":
    main()
