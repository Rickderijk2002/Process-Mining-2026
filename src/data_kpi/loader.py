"""Load the assignment inputs: XES event log and PNML Petri net."""

from __future__ import annotations

from pathlib import Path

from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.petri_net.importer import importer as pnml_importer
from pm4py.objects.log.obj import EventLog
from pm4py.objects.petri_net.obj import PetriNet, Marking


class DataLoader:
    """Load relative-path XES and PNML files for the deviation-analysis pipeline."""

    def load_log(self, path: str | Path) -> EventLog:
        log_path = Path(path)
        if not log_path.is_file():
            raise FileNotFoundError(f"Event log not found: {log_path}")
        return xes_importer.apply(str(log_path))

    def load_petri_net(
        self, path: str | Path
    ) -> tuple[PetriNet, Marking, Marking]:
        net_path = Path(path)
        if not net_path.is_file():
            raise FileNotFoundError(f"Petri net not found: {net_path}")
        return pnml_importer.apply(str(net_path))

    def sample_log(self, log: EventLog, n: int) -> EventLog:
        """Return the first n traces. Used while developing so B is not blocked."""
        if n < 0:
            raise ValueError(f"sample size must be non-negative, got {n}")
        if n >= len(log):
            return log
        return EventLog(list(log)[:n])
