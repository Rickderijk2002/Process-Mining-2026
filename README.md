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

A run creates these files; the repository only holds the locked cutoff 14 result under versioned names (`tree_rules_cutoff14_pruned_2026-10-06.csv` and its two companions, see [docs/results.md](docs/results.md)).

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

## Reproducing the reported results

One command runs the whole chain and checks it against the stored results:

```bash
python scripts/reproduce_all.py
```

It takes several minutes, mostly the alignment of all 3,093 traces and the cutoff comparison. It writes everything to `data/output/reproduced/` (not tracked by git), so the stored results are never overwritten. At the end it compares each new file with the stored one and prints `identical` or `DIFFERENT` per file. [docs/results.md](docs/results.md) lists the numbers the files should contain.

| Option | Effect |
|---|---|
| `--skip-align` | Reuse the stored `data/output/alignment_encodings.csv` instead of aligning again (much faster). |
| `--sample 50` | Quick check: align the first 50 traces and fit one tree. Nothing is compared. |
| `--toys` | Also run both toy validations of the section above. |
| `--out-dir PATH` | Write the new files somewhere else. |

The steps, in order, and the script behind each:

1. Align every trace and fit the first tree: `src/main.py --cutoff 14`
2. Refit the locked cutoff 14 result, seed 0: `scripts/fit_tree.py`
3. Stability over the seeds 0 to 3: `scripts/check_tree_stability.py`
4. Cutoff comparison 14, 18 and 21: `scripts/compare_cutoffs.py`
5. Lifecycle merge, pause and execution: `scripts/compare_cutoffs.py --merge`
6. Lifecycle merge, one column per task: `scripts/compare_cutoffs_merge_all.py`
7. The F1 per cutoff figure of the report: `scripts/plot_cutoff_comparison.py`

Each script can also be run on its own, with its own options (`--help`).

**Aligning again can change a few traces.** The reported results are defined by the stored `data/output/alignment_encodings.csv`. With `--skip-align`, steps 2 to 7 reproduce every stored result file exactly (checked: 13 of 13 files identical). If you align again (the default), about 14 of the 3,093 traces (0.5%) can come out differently: for those traces the Petri net allows several optimal alignments of equal cost, the solver picks one of them, and repeated runs may pick another. The total number of moves stays the same, but a few downstream numbers shift (for example the seed 1 tree of the stability check, or the mean number of rules in the cutoff comparison). The stored encoding is the reference for the report.

## Which script is for what

| Script | Purpose | In `reproduce_all.py` |
|---|---|---|
| `src/main.py` | The pipeline itself: throughput, alignments, encoding, tree, rules | step 1 |
| `scripts/fit_tree.py` | Refit the tree for a cutoff from the saved encoding table | step 2 |
| `scripts/check_tree_stability.py` | Fixed-grid cutoff 14 search over several seeds (report, stability table) | step 3 |
| `scripts/compare_cutoffs.py` | Cutoff, seed and class-weight comparison (report, results tables); `--merge` for the lifecycle merge | steps 4 and 5 |
| `scripts/compare_cutoffs_merge_all.py` | Lifecycle merge into one column per task (report appendix) | step 6 |
| `scripts/plot_cutoff_comparison.py` | F1 per cutoff figure of the report | step 7 |
| `scripts/make_toy.py`, `align_toy.py`, `check_toy_rules.py` | Linear toy: write it, align it, recover the planted rule | with `--toys` |
| `scripts/make_toy_parallel.py`, `align_toy_parallel.py`, `check_toy_parallel_rules.py` | Parallel toy with a choice, same three steps | with `--toys` |
| `scripts/evaluate_toy_alignments.py` | Alignments of either toy against the hand-written gold standard | with `--toys` |
| `scripts/make_gold_appendix.py` | Builds the toy nets figure and the gold table for the report appendix | no, it writes into `docs/Report/` |
| `scripts/inspect_log.py`, `scripts/inspect_throughput.py` | Look at the log and the throughput distribution (histograms) | no, inspection only |
| `scripts/spike_simpn_export.py` | Experiment: can SimPN export an event log for the parallel toy? See [docs/toy_parallel.md](docs/toy_parallel.md) | no, a one-off spike |
| `docs/poster/build_poster_v7.py` | Builds the poster HTML from the encoding table | no, see below |

## Report and poster

The short paper is `docs/Report/Report-process-Mining-2026-11-06.qmd`, with the rendered PDF next to it. Rendering needs [Quarto](https://quarto.org) and a LaTeX distribution; `before-body.tex` and `toc.tex` in the same folder are part of the build. The Python environment above is not needed for rendering.

The poster is `docs/poster/Poster_Group8_v7.pdf`. `docs/poster/build_poster_v7.py` rebuilds `poster_v7.html` from `data/output/alignment_encodings.csv`, so run step 1 above first.

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
docs/                    method notes (architecture, pipeline, dataset, toys) and results.md
docs/Report/             short paper: Quarto source, PDF, bibliography, figures
docs/poster/             poster: PDF, HTML, build script, figures
```

[docs/architecture.md](docs/architecture.md) describes every file in more detail.

## Data

`data/source/` holds the BPI Challenge 2017 (Denied) subset provided with the assignment:
`BPI2017Denied(3).xes` (the event log, 3,093 traces), `BPI2017Denied_petriNet.pnml` (the normative
model) and `Log Description.pdf`. Background: https://www.win.tue.nl/bpi/2017/challenge.html.
