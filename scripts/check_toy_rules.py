"""Plant a throughput rule on the toy encodings and recover it with the tree."""

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
    "t1": 5.0,
    "t2": 8.0,
    "t3": 20.0,
    "t4": 30.0,
    "t5": 6.0,
}
EXPECTED_BAD = {"t3", "t4"}


def main() -> None:
    loader = DataLoader()
    log = loader.load_log(ROOT / "data" / "raw" / "toy.xes")
    net, initial_marking, final_marking = loader.load_petri_net(
        ROOT / "data" / "raw" / "toy.pnml"
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
        missing = encodings.loc[
            encodings["throughput_time"].isna(), "case_id"
        ].tolist()
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


if __name__ == "__main__":
    main()
