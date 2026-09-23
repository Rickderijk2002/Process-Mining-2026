"""Generate Petri-net alignments and deviation encodings."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

import pandas as pd
from pm4py.algo.conformance.alignments.petri_net import algorithm
from pm4py.objects.log.obj import EventLog
from pm4py.objects.petri_net.obj import PetriNet


SKIP = ">>"


@dataclass
class AlignmentBatch:
    """Raw alignments and encodings for a complete log."""

    alignments: list[dict[str, Any]]
    encodings: pd.DataFrame


class Aligner:
    """Computes an optimal alignment for one event-log trace."""

    @staticmethod
    def align_trace(trace, net, initial_marking, final_marking) -> dict[str, Any]:
        """Computes a single alignment"""
        result = algorithm.apply(trace, net, initial_marking, final_marking)
        if not isinstance(result, dict) or "alignment" not in result:
            raise ValueError("pm4py returned an alignment without an 'alignment' field")
        return result

    @staticmethod
    def align_log(log: EventLog, net: PetriNet, initial_marking, final_marking, activities: Iterable[str], *, 
                  case_id_attribute: str = "concept:name", kpi_attribute: str = "throughput_time",) -> AlignmentBatch:
        """Align every trace and combine with its metadata for the output dataframe"""
        activities = tuple(activities)
        alignments = []
        rows = []

        for index, trace in enumerate(log):
            case_id = trace.attributes.get(case_id_attribute, index)
            try:
                alignment = Aligner.align_trace(
                    trace, net, initial_marking, final_marking
                )
                encoding = Encoder.encode_trace(alignment, activities)
            except (KeyError, TypeError, ValueError) as error:
                raise ValueError(f"Could not align trace {case_id!r}") from error

            alignments.append(alignment)
            rows.append({
                "case_id": case_id,
                kpi_attribute: trace.attributes.get(kpi_attribute),
                **encoding,
            })

        return AlignmentBatch(alignments, pd.DataFrame(rows))



class Encoder:
    """Encodes alignment moves into model-move and log-move counts."""

    @staticmethod
    def activities_from_model(net: PetriNet) -> tuple[str, ...]:
        """Return visible transition labels in stable order."""
        return tuple(sorted({transition.label for transition in net.transitions if transition.label}))

    @staticmethod
    def encode_trace(alignment: dict[str, Any], activities: Iterable[str]) -> dict[str, int]:
        activities = tuple(activities)
        encoded = {
            f"model_move_{activity}": 0
            for activity in activities
        }
        encoded.update({
            f"log_move_{activity}": 0
            for activity in activities
        })

        # Note that this only tracks non-synchronous moves. That is, moves that happen in both the log and model are ignored.
        moves = alignment.get("alignment") if isinstance(alignment, dict) else None
        if moves is None:
            raise ValueError("alignment must contain an 'alignment' move list")

        for log_label, model_label in moves:
            if model_label == SKIP and log_label in activities:
                encoded[f"log_move_{log_label}"] += 1
            elif log_label == SKIP and model_label in activities:
                encoded[f"model_move_{model_label}"] += 1

        return encoded

