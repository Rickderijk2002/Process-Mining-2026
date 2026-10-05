"""Build the parallel + XOR toy net and log (Step 1).

Writes data/raw/toy_parallel.pnml and data/raw/toy_parallel.xes from the
hand design in docs/toy_parallel.md. Same pattern as make_toy.py (pm4py).
SimPN can replace the log generator later; the gold counts stay fixed.
"""

from pathlib import Path

import pm4py
from pm4py.objects.log.obj import Event, EventLog, Trace
from pm4py.objects.petri_net.obj import Marking, PetriNet
from pm4py.objects.petri_net.utils import petri_utils

ROOT = Path(__file__).resolve().parents[1]
OUT_PNML = ROOT / "data" / "raw" / "toy_parallel.pnml"
OUT_XES = ROOT / "data" / "raw" / "toy_parallel.xes"

net = PetriNet("toy_parallel")
place_names = (
    "source",
    "p1",
    "pB",
    "pB2",
    "pC",
    "pC2",
    "p2",
    "p3",
    "sink",
)
places = {name: PetriNet.Place(name) for name in place_names}
for place in places.values():
    net.places.add(place)


def add_transition(name, label, sources: list[str], targets: list[str]):
    transition = PetriNet.Transition(name, label)
    net.transitions.add(transition)
    for source in sources:
        petri_utils.add_arc_from_to(places[source], transition, net)
    for target in targets:
        petri_utils.add_arc_from_to(transition, places[target], net)


add_transition("A", "A", ["source"], ["p1"])
add_transition("tau_and_split", None, ["p1"], ["pB", "pC"])
add_transition("B", "B", ["pB"], ["pB2"])
add_transition("C", "C", ["pC"], ["pC2"])
add_transition("tau_and_join", None, ["pB2", "pC2"], ["p2"])
add_transition("D", "D", ["p2"], ["p3"])
add_transition("E", "E", ["p2"], ["p3"])
add_transition("F", "F", ["p3"], ["sink"])

initial_marking = Marking()
initial_marking[places["source"]] = 1
final_marking = Marking()
final_marking[places["sink"]] = 1


def make_trace(case_id, activities):
    trace = Trace(attributes={"concept:name": case_id})
    for activity in activities:
        trace.append(Event({"concept:name": activity}))
    return trace


log = EventLog(
    [
        make_trace("p1", ["A", "B", "C", "D", "F"]),
        make_trace("p2", ["A", "C", "B", "E", "F"]),
        make_trace("p3", ["A", "B", "D", "F"]),
        make_trace("p4", ["A", "B", "B", "C", "D", "F"]),
        make_trace("p5", ["A", "B", "C", "D"]),
        make_trace("p6", ["A", "A", "B", "C", "E", "F"]),
    ]
)

OUT_PNML.parent.mkdir(parents=True, exist_ok=True)
pm4py.write_pnml(net, initial_marking, final_marking, str(OUT_PNML))
pm4py.write_xes(log, str(OUT_XES))
print(f"wrote {OUT_PNML}")
print(f"wrote {OUT_XES}")
