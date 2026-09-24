import pm4py
from pm4py.objects.log.obj import Event, EventLog, Trace
from pm4py.objects.petri_net.obj import Marking, PetriNet
from pm4py.objects.petri_net.utils import petri_utils

net = PetriNet("toy")
place_names = ("source", "p1", "p2", "p3", "sink")
places = {name: PetriNet.Place(name) for name in place_names}
for place in places.values():
    net.places.add(place)


def add_transition(name, label, source, target):
    transition = PetriNet.Transition(name, label)
    net.transitions.add(transition)
    petri_utils.add_arc_from_to(places[source], transition, net)
    petri_utils.add_arc_from_to(transition, places[target], net)


add_transition("A", "A", "source", "p1")
add_transition("B", "B", "p1", "p2")
add_transition("tau", None, "p2", "p3")
add_transition("C", "C", "p3", "sink")

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
        make_trace("t1", ["A", "B", "C"]),
        make_trace("t2", ["A", "C"]),
        make_trace("t3", ["A", "B", "B", "C"]),
        make_trace("t4", ["A", "B", "B", "B", "C"]),
        make_trace("t5", ["A", "A", "C"]),
    ]
)

pm4py.write_pnml(net, initial_marking, final_marking, "data/raw/toy.pnml")
pm4py.write_xes(log, "data/raw/toy.xes")
