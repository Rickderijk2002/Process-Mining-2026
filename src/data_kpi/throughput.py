"""
Throughput-time KPI (Person A).

Locked definition (2026-09-21):
  attribute name: throughput_time
  formula:        last event timestamp - first event timestamp (per case)
  unit:           days (float), seconds / 86400
  lower is better
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from pm4py.objects.log.obj import EventLog, Trace

THROUGHPUT_ATTR = "throughput_time"
SECONDS_PER_DAY = 86400.0


class ThroughputTimeEnricher:
    """Compute per-trace throughput time and attach it as a case attribute."""

    def __init__(self, attribute_name: str = THROUGHPUT_ATTR) -> None:
        self.attribute_name = attribute_name

    def throughput_days(self, trace: Trace) -> float:
        if len(trace) == 0:
            raise ValueError("Cannot compute throughput time for an empty trace.")

        timestamps = [_event_timestamp(event, index=i) for i, event in enumerate(trace)]
        # Paper: last event timestamp minus first event timestamp.
        # Use min/max so a mis-ordered case still measures wall-clock span.
        delta = max(timestamps) - min(timestamps)
        return delta.total_seconds() / SECONDS_PER_DAY

    def enrich(self, log: EventLog) -> EventLog:
        """Attach throughput_time to every trace. Mutates and returns the same log."""
        for trace in log:
            trace.attributes[self.attribute_name] = self.throughput_days(trace)
        return log

    def export_xes(self, log: EventLog, path: str) -> None:
        xes_exporter.apply(log, path)


def _event_timestamp(event: dict[str, Any], index: int) -> datetime:
    if "time:timestamp" not in event:
        raise ValueError(
            f"Event at index {index} has no time:timestamp; cannot compute throughput."
        )
    ts = event["time:timestamp"]
    if ts is None:
        raise ValueError(
            f"Event at index {index} has a missing time:timestamp; cannot compute throughput."
        )
    if not isinstance(ts, datetime):
        raise TypeError(
            f"Event at index {index}: expected datetime for time:timestamp, got {type(ts)}."
        )
    # Drop tzinfo for subtraction when mixed aware/naive values appear.
    if ts.tzinfo is not None:
        return ts.replace(tzinfo=None)
    return ts
