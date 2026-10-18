# Conformance Checking for Process Improvement

JM0211 Process Mining, group 8. The artefact implements the deviation analysis step of Dees,
de Leoni and Mannhardt (2017), *Enhancing Process Models to Improve Business Performance*, on the
BPI Challenge 2017 (Denied) log.

Given an event log (XES) and a Petri net (PNML), the program

1. computes the throughput time of every trace and stores it as the case attribute `throughput_time` (days),
2. computes an optimal alignment for every trace and counts, per activity, the model moves and the log moves,
3. fits a classification tree on these counts, with a grid search over the tree settings, to separate fast from slow traces,
4. extracts one rule per leaf and lists the traces that satisfy each rule.

## Setup

Python 3.12 or later is required. Run all commands from the project root.

With [uv](https://docs.astral.sh/uv/):

```bash
uv sync
```

With pip:

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

The examples below use `python`. With uv, write `uv run python` instead.

## Run

The full pipeline on the provided log, with a 14 day cutoff between fast and slow traces:

```bash
python src/main.py --cutoff 14
```

Aligning all 3,093 traces takes several minutes. For a quick check, use a sample of the first 50 traces:

```bash
python src/main.py --cutoff 14 --sample 50
```

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `--cutoff` | required | Throughput time in days. Traces at or below it are fast, traces above it are slow. |
| `--sample` | all traces | Use only the first N traces, for development. |
| `--test-size` | 0.25 | Fraction of the traces held out for evaluation. |
| `--random-state` | 0 | Random seed of the split and the tree. |
| `--log` | `data/source/BPI2017Denied(3).xes` | Event log. |
| `--pnml` | `data/source/BPI2017Denied_petriNet.pnml` | Normative Petri net. |
| `--export` | none | Also write the log enriched with `throughput_time` as XES. |
| `--export-encodings` | `data/output/alignment_encodings.csv` | Output path of the encoding table. |
| `--rules` | `data/output/tree_rules.csv` | Output path of the rule table. |
| `--export-cases` | `data/output/tree_rule_cases.csv` | Output path of the rule-to-trace assignments. |

All paths are relative to the project root.

A sample run overwrites the default output files with sample results. To keep the full-log results in
`data/output/`, pass other output paths to the sample run, for example `--export-encodings
data/output/sample_encodings.csv --rules data/output/sample_rules.csv --export-cases
data/output/sample_cases.csv`.

### Output

- `alignment_encodings.csv`: one row per trace with its case id, `throughput_time`, and the columns `model_move_<activity>` and `log_move_<activity>`.
- `tree_rules.csv`: one row per leaf with the conditions, the predicted class and the number of fast and slow traces.
- `tree_rule_cases.csv`: one row per trace with the id of the rule it satisfies.

The program also prints the class balance, the selected tree settings and the precision and recall of the slow class on the held-out traces.

To fit the tree again for another cutoff without repeating the alignments, use the saved encoding table:

```bash
python scripts/fit_tree.py --cutoff 14 --export-cases data/output/tree_rule_cases.csv
```

## Validation on hand-built toy logs

The correct move counts of two small logs were derived by hand. The scripts below run the artefact on them and compare the result with these gold standards.

Linear toy (5 traces):

```bash
python scripts/make_toy.py
python scripts/align_toy.py
python scripts/evaluate_toy_alignments.py
python scripts/check_toy_rules.py
```

Toy with a parallel block and an exclusive choice (6 traces):

```bash
python scripts/make_toy_parallel.py
python scripts/align_toy_parallel.py
python scripts/evaluate_toy_alignments.py --gold data/gold/toy_parallel_alignment_gold.csv --log data/raw/toy_parallel.xes --pnml data/raw/toy_parallel.pnml --plot data/output/toy_parallel_alignment_gold_vs_pred.png --title "Parallel toy: gold vs predicted"
python scripts/check_toy_parallel_rules.py
```

The gold standards are `data/gold/toy_alignment_gold.csv` and `data/gold/toy_parallel_alignment_gold.csv`. The design of both toys is described in `docs/toy.md` and `docs/toy_parallel.md`.

<!-- TODO (after the group decides the headline result): section "Reproducing the reported results" with the exact commands for the cutoff 14 result, the seed stability check (scripts/check_tree_stability.py) and the cutoff comparison (scripts/compare_cutoffs.py). -->

## Project layout

```text
src/main.py              entry point of the pipeline
src/data_kpi/            loading the log and net, throughput time
src/alignment/           alignments and move-count encoding
src/classification/      tree, grid search, rule extraction
scripts/                 toy validation, stability check, cutoff comparison, inspection
data/source/             event log, Petri net, log description, Dees et al. (2017)
data/gold/               hand-written gold standards
data/output/             generated tables and figures
docs/                    method notes, results records, short paper (docs/Report)
```

## Data

`data/source/` holds the BPI Challenge 2017 (Denied) subset provided with the assignment:
`BPI2017Denied(3).xes` (the event log, 3,093 traces), `BPI2017Denied_petriNet.pnml` (the normative
model) and `Log Description.pdf`. Background: https://www.win.tue.nl/bpi/2017/challenge.html.
