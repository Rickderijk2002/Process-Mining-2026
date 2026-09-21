"""
Entry point for Person A: load data, attach throughput_time, optional XES export.

Example:
  uv run python main.py --sample 50 --export data/raw/enriched_sample.xes
"""

from __future__ import annotations

import argparse
import statistics
from pathlib import Path

from data_kpi import DataLoader, ThroughputTimeEnricher, THROUGHPUT_ATTR


def main() -> None:
    args = _parse_args()
    loader = DataLoader()
    enricher = ThroughputTimeEnricher(attribute_name=THROUGHPUT_ATTR)

    log = loader.load_log(args.log)
    net, initial_marking, final_marking = loader.load_petri_net(args.pnml)

    if args.sample is not None:
        log = loader.sample_log(log, args.sample)

    enricher.enrich(log)

    values = [float(trace.attributes[THROUGHPUT_ATTR]) for trace in log]
    print(f"traces:              {len(log)}")
    print(f"petri places/trans:  {len(net.places)}/{len(net.transitions)}")
    print(f"KPI attribute:       {THROUGHPUT_ATTR} (days)")
    print(f"throughput min:      {min(values):.4f}")
    print(f"throughput median:   {statistics.median(values):.4f}")
    print(f"throughput max:      {max(values):.4f}")
    print(f"negative values:     {sum(1 for v in values if v < 0)}")

    # Spot-check: first case, recompute from raw timestamps.
    first = log[0]
    case_id = first.attributes.get("concept:name", "<unknown>")
    print(f"spot-check case:     {case_id} -> {first.attributes[THROUGHPUT_ATTR]:.4f} days")

    if args.export:
        export_path = Path(args.export)
        export_path.parent.mkdir(parents=True, exist_ok=True)
        enricher.export_xes(log, str(export_path))
        print(f"exported:            {export_path}")

    # Keep markings available so a later stage can import this module without reloading.
    _ = (initial_marking, final_marking)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Person A: attach throughput_time (days) to each trace."
    )
    parser.add_argument(
        "--log",
        default="data/source/BPI2017Denied(3).xes",
        help="Path to the XES event log (relative to the project root).",
    )
    parser.add_argument(
        "--pnml",
        default="data/source/BPI2017Denied_petriNet.pnml",
        help="Path to the PNML Petri net (relative to the project root).",
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=None,
        help="Only use the first N traces (fast path while developing).",
    )
    parser.add_argument(
        "--export",
        default=None,
        help="Optional path for the enriched XES (e.g. data/raw/enriched_sample.xes).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
