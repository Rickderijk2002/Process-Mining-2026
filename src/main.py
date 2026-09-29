"""
Example run command:
  uv run python src/main.py --cutoff 14 --sample 50 --export data/output/enriched_sample.xes
"""

from __future__ import annotations

import argparse
import statistics
from pathlib import Path

from alignment import Aligner, AlignmentBatch, Encoder
from classification import (
    BAD,
    GOOD,
    DeviationTree,
    label_throughput,
    rules_to_case_frame,
    rules_to_frame,
)
from data_kpi import THROUGHPUT_ATTR, DataLoader, ThroughputTimeEnricher

ROOT = Path(__file__).resolve().parents[1]


def main() -> AlignmentBatch:
    args = _parse_args()
    loader = DataLoader()
    enricher = ThroughputTimeEnricher(attribute_name=THROUGHPUT_ATTR)

    log = loader.load_log(_resolve(args.log))
    net, initial_marking, final_marking = loader.load_petri_net(_resolve(args.pnml))

    if args.sample is not None:
        log = loader.sample_log(log, args.sample)

    enricher.enrich(log)

    activities = Encoder.activities_from_model(net)
    alignment_batch = Aligner.align_log(
        log,
        net,
        initial_marking,
        final_marking,
        activities,
    )
    encodings_df = alignment_batch.encodings

    values = [float(trace.attributes[THROUGHPUT_ATTR]) for trace in log]
    print(f"traces:              {len(log)}")
    print(f"petri places/trans:  {len(net.places)}/{len(net.transitions)}")
    print(f"KPI attribute:       {THROUGHPUT_ATTR} (days)")
    print(f"throughput min:      {min(values):.4f}")
    print(f"throughput median:   {statistics.median(values):.4f}")
    print(f"throughput max:      {max(values):.4f}")
    print(f"negative values:     {sum(1 for v in values if v < 0)}")
    print(f"alignment activities: {len(activities)}")
    print(f"encoding features:    {len(activities) * 2}")
    print(f"encodings dataframe:   {encodings_df.head(5)}")

    encodings_path = _resolve(args.export_encodings)
    encodings_path.parent.mkdir(parents=True, exist_ok=True)
    encodings_df.to_csv(encodings_path, index=False)
    print(f"encodings:           {encodings_path} ({len(encodings_df)} rows)")

    if args.export:
        export_path = _resolve(args.export)
        export_path.parent.mkdir(parents=True, exist_ok=True)
        enricher.export_xes(log, str(export_path))
        print(f"exported:            {export_path}")

    _fit_and_store_rules(encodings_df, args)
    return alignment_batch


def _fit_and_store_rules(encodings_df, args: argparse.Namespace) -> None:
    labels = label_throughput(encodings_df[THROUGHPUT_ATTR], args.cutoff)
    result = DeviationTree(
        random_state=args.random_state,
        test_size=args.test_size,
    ).fit(encodings_df, args.cutoff, holdout=True, search=True)

    rules_path = _resolve(args.rules)
    rules_path.parent.mkdir(parents=True, exist_ok=True)
    rules_to_frame(result.rules).to_csv(rules_path, index=False)

    cases_path = _resolve(args.export_cases)
    cases_path.parent.mkdir(parents=True, exist_ok=True)
    rules_to_case_frame(result.rules).to_csv(cases_path, index=False)

    n_good = int((labels == GOOD).sum())
    n_bad = int((labels == BAD).sum())
    print(f"cutoff days:          {args.cutoff}")
    print(f"class balance:        good={n_good} bad={n_bad}")
    print(f"best params:          {result.best_params}")
    print(f"held-out precision:   {result.held_out_precision}")
    print(f"held-out recall:      {result.held_out_recall}")
    print(f"rules:                {len(result.rules)}")
    print(f"wrote rules:          {rules_path}")
    print(f"wrote cases:          {cases_path}")


def _resolve(path: str) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return ROOT / candidate


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Attach throughput time, align traces, fit the deviation tree, "
            "and write the rules."
        )
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
        "--cutoff",
        type=float,
        required=True,
        help="Throughput cutoff in days. Cases at or below are good.",
    )
    parser.add_argument(
        "--export-encodings",
        default="data/output/alignment_encodings.csv",
        help="Path for the alignment encoding table (relative to the project root).",
    )
    parser.add_argument(
        "--rules",
        default="data/output/tree_rules.csv",
        help="Path for the leaf-rule table (relative to the project root).",
    )
    parser.add_argument(
        "--export-cases",
        default="data/output/tree_rule_cases.csv",
        help="Path for rule_id,case_id rows (relative to the project root).",
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.25,
        help="Held-out fraction for evaluation.",
    )
    parser.add_argument(
        "--random-state",
        type=int,
        default=0,
        help="Random seed for the train/test split and the tree.",
    )
    parser.add_argument(
        "--export",
        default=None,
        help="Optional path for the enriched XES (e.g. data/output/enriched_sample.xes).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
