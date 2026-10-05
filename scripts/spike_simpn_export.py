"""Spike: can SimPN export a mineable event log for our parallel+XOR toy?

Findings target (written to stdout and docs/toy_parallel.md after a green run):
- EventLogReporter -> CSV (yes, official path).
- PNML from SimPN (no API found; keep pm4py PNML as model gold).
- Optional: CSV -> XES via pm4py for our aligner.
"""

from __future__ import annotations

import random
from pathlib import Path

import pandas as pd
import pm4py
from pm4py.objects.conversion.log import converter as log_converter
from simpn.reporters import EventLogReporter
from simpn.simulator import SimProblem, SimToken
import simpn.prototypes as prototype

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "output"
CSV_PATH = OUT_DIR / "simpn_spike_events.csv"
XES_PATH = OUT_DIR / "simpn_spike_events.xes"


def build_model() -> SimProblem:
    """A, then B||C, then XOR D/E, then F. Same shape as docs/toy_parallel.md."""
    model = SimProblem()

    # Two resources so B and C can run "in parallel" without strict serialisation.
    resource = model.add_place("resource")
    resource.put("r1")
    resource.put("r2")

    after_start = prototype.BPMNFlow(model, "after_start")
    after_a = prototype.BPMNFlow(model, "after_a")
    to_b = prototype.BPMNFlow(model, "to_b")
    to_c = prototype.BPMNFlow(model, "to_c")
    after_b = prototype.BPMNFlow(model, "after_b")
    after_c = prototype.BPMNFlow(model, "after_c")
    after_join = prototype.BPMNFlow(model, "after_join")
    to_d = prototype.BPMNFlow(model, "to_d")
    to_e = prototype.BPMNFlow(model, "to_e")
    after_d = prototype.BPMNFlow(model, "after_d")
    after_e = prototype.BPMNFlow(model, "after_e")
    after_xor = prototype.BPMNFlow(model, "after_xor")
    after_f = prototype.BPMNFlow(model, "after_f")

    prototype.BPMNStartEvent(model, [], [after_start], "start", lambda: 1.0)

    def task(c, r):
        return [SimToken((c, r), delay=0.1)]

    prototype.BPMNTask(model, [after_start, resource], [after_a, resource], "A", task)
    prototype.BPMNParallelSplitGateway(model, [after_a], [to_b, to_c], "and_split")
    prototype.BPMNTask(model, [to_b, resource], [after_b, resource], "B", task)
    prototype.BPMNTask(model, [to_c, resource], [after_c, resource], "C", task)
    prototype.BPMNParallelJoinGateway(model, [after_b, after_c], [after_join], "and_join")

    def xor_choice(c):
        if random.random() < 0.5:
            return [SimToken(c), None]
        return [None, SimToken(c)]

    prototype.BPMNExclusiveSplitGateway(
        model, [after_join], [to_d, to_e], "xor_split", xor_choice
    )
    prototype.BPMNTask(model, [to_d, resource], [after_d, resource], "D", task)
    prototype.BPMNTask(model, [to_e, resource], [after_e, resource], "E", task)
    prototype.BPMNExclusiveJoinGateway(
        model, [after_d, after_e], [after_xor], "xor_join"
    )
    prototype.BPMNTask(model, [after_xor, resource], [after_f, resource], "F", task)
    prototype.BPMNEndEvent(model, [after_f], [], name="end")
    return model


def csv_to_xes(csv_path: Path, xes_path: Path) -> int:
    """Convert SimPN EventLogReporter CSV to XES. Returns number of cases."""
    frame = pd.read_csv(csv_path, sep=",")
    if frame.shape[1] == 1:
        frame = pd.read_csv(csv_path, sep=";")

    print("CSV columns:", list(frame.columns))
    print("CSV head:\n", frame.head(12).to_string(index=False))

    required = {"case_id", "task", "completion_time"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"CSV missing {missing}; got {list(frame.columns)}")

    # Keep labelled tasks only (drop BPMN start/end markers for alignment features).
    activities = {"A", "B", "C", "D", "E", "F"}
    mapped = frame.loc[frame["task"].isin(activities), ["case_id", "task", "completion_time"]].copy()
    mapped = mapped.rename(
        columns={
            "case_id": "case:concept:name",
            "task": "concept:name",
            "completion_time": "time:timestamp",
        }
    )
    mapped["time:timestamp"] = pd.to_datetime(mapped["time:timestamp"])
    event_log = log_converter.apply(
        mapped, variant=log_converter.Variants.TO_EVENT_LOG
    )
    pm4py.write_xes(event_log, str(xes_path))
    return len(event_log)


def main() -> None:
    random.seed(0)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if CSV_PATH.exists():
        CSV_PATH.unlink()

    model = build_model()
    # SimPN docs often use ';'; we use ',' for pandas friendliness.
    reporter = EventLogReporter(str(CSV_PATH), separator=",")
    model.simulate(20, reporter)

    if not CSV_PATH.exists() or CSV_PATH.stat().st_size == 0:
        raise SystemExit(f"no CSV written at {CSV_PATH}")

    n_cases = csv_to_xes(CSV_PATH, XES_PATH)
    print()
    print("SimPN spike OK")
    print("  event log CSV:", CSV_PATH)
    print("  converted XES:", XES_PATH, f"({n_cases} cases)")
    print("  PNML export:   not available from SimPN (use pm4py net as now)")


if __name__ == "__main__":
    main()
