# Architecture

One command reads the denied-loan log and its Petri net, and writes the move-count table, the leaf rules, and the applications that match each rule. The story of the data is in [dataset.md](dataset.md). The five steps are in [pipeline.md](pipeline.md). This note is where those steps live in the repo.

`src/` is not an installed package. `uv run python src/main.py` puts `src/` on the path because that is the script's directory. The scripts under `scripts/` insert `src/` themselves.

## How a run moves

```text
data/source/BPI2017Denied(3).xes
data/source/BPI2017Denied_petriNet.pnml
        |
        v
src/main.py
        |
        +-- data_kpi/        load the log and the net, attach throughput_time
        +-- alignment/       align each case, count model moves and log moves
        +-- classification/  label good/bad from --cutoff, fit the tree, read the leaves
        |
        v
data/output/alignment_encodings.csv
data/output/tree_rules.csv
data/output/tree_rule_cases.csv
```

```bash
uv run python src/main.py --cutoff 14
```

`--sample N` keeps the first N applications. `--export` also writes the log with `throughput_time` stored on each case. `scripts/fit_tree.py` repeats only the tree on a saved encoding table, so a new cutoff does not align the log again.

## `src/`

| Path | What it does |
|---|---|
| `src/main.py` | Runs the whole pipeline and writes the three output tables. |
| `src/data_kpi/loader.py` | `DataLoader` reads an XES log and a PNML net, and can take the first N traces. |
| `src/data_kpi/throughput.py` | `ThroughputTimeEnricher` sets `throughput_time` to the last timestamp minus the first, in days. |
| `src/alignment/alignment_encoding.py` | `Aligner` computes an optimal alignment per case. `Encoder` turns it into `model_move_*` and `log_move_*` counts. Synchronous moves are dropped. Silent transitions are not activities. |
| `src/classification/model.py` | `DeviationTree` splits off a holdout, searches tree depth and leaf size, and scores precision and recall on the bad class. `extract_leaf_rules` turns each leaf into a rule and the case ids that match it. |

Each package's `__init__.py` re-exports that public surface. `main.py` and the scripts import from `data_kpi`, `alignment`, and `classification`, not from the modules underneath.

## `scripts/`

These check a stage, inspect the log, or run the experiments of the report. They are not on the path of `src/main.py`.

| Path | What it does |
|---|---|
| `scripts/reproduce_all.py` | Runs the whole chain (alignment, locked result, stability, cutoff comparison, merge variants, figure, optionally the toys) into `data/output/reproduced/` and compares every file with the stored result. |
| `scripts/inspect_log.py` | Prints the size, the activity families, and the share of applications that contain each activity. Saves a histogram of events per application. |
| `scripts/inspect_throughput.py` | Prints min, median, and max throughput in days. Saves a histogram and a boxplot. |
| `scripts/fit_tree.py` | Fits the tree from `data/output/alignment_encodings.csv` for a cutoff you pass in. |
| `scripts/check_tree_stability.py` | Repeats the fixed-grid cutoff 14 search over several random splits. Refuses to overwrite an existing output file. |
| `scripts/compare_cutoffs.py` | Compares trees across cutoffs, seeds and class-weight variants. With `--merge` it merges the lifecycle variants first. |
| `scripts/compare_cutoffs_merge_all.py` | Experiment: merges every lifecycle variant of a task into one column per move kind. |
| `scripts/plot_cutoff_comparison.py` | Draws the F1 per cutoff against the all-slow baseline from the comparison summary. |
| `scripts/make_toy.py` | Writes a tiny net and five short traces to `data/raw/toy.pnml` and `data/raw/toy.xes`. |
| `scripts/align_toy.py` | Aligns that toy and prints the move-count table, so the counts can be checked by hand. |
| `scripts/check_toy_rules.py` | Plants a throughput on those traces, fits a depth-1 tree, and prints precision and recall against the two cases that should come out bad. |
| `scripts/make_toy_parallel.py` | Writes the toy with a parallel block and an exclusive choice to `data/raw/toy_parallel.pnml` and `.xes`. |
| `scripts/align_toy_parallel.py` | Aligns the parallel toy and prints the move-count table. |
| `scripts/check_toy_parallel_rules.py` | Plants a throughput rule on the parallel toy and recovers it with a depth-1 tree. |
| `scripts/evaluate_toy_alignments.py` | Compares the aligner with the hand-written gold CSV in `data/gold/` and plots gold against predicted. |
| `scripts/make_gold_appendix.py` | Builds the gold-standard material for the report appendix (the toy nets figure and a gold table). |
| `scripts/spike_simpn_export.py` | Spike: checks whether SimPN can export an event log for the parallel toy. Result in [toy_parallel.md](toy_parallel.md). The only user of `simpn`. |

## `data/`

| Path | What it is |
|---|---|
| `data/source/BPI2017Denied(3).xes` | The 3,093 denied applications. |
| `data/source/BPI2017Denied_petriNet.pnml` | The normative net those applications are aligned to. |
| `data/source/Log Description.pdf` | Short description of the loan process and the `A_`, `O_`, and `W_` event types. |
| `data/source/M_dL_M@COOPIS17.pdf` | Dees, de Leoni and Mannhardt (2017), the paper this pipeline implements. |
| `data/raw/` | The toy logs and toy nets, written by `scripts/make_toy.py` and `scripts/make_toy_parallel.py`. Not tracked in git. |
| `data/gold/` | The hand-written gold move counts of both toys, the answer key of `scripts/evaluate_toy_alignments.py`. |
| `data/output/alignment_encodings.csv` | One row per application: case id, throughput, move counts. Input to the tree. |
| `data/output/tree_rules.csv` | One row per leaf: the conditions, the predicted class, and how many cases are good or bad. |
| `data/output/tree_rule_cases.csv` | `rule_id` and `case_id` for every application that falls in a leaf. |
| `data/output/*_cutoff14_pruned_2026-10-06.csv` | The locked cutoff 14 result: rules, case assignments and the seed stability table. See [results.md](results.md). |
| `data/output/cutoff_comparison*.csv` | Results of `scripts/compare_cutoffs.py` and the merge variants, one summary, one per-seed and one rules file each. |
| `data/output/*.png`, `data/output/*.svg` | Histograms and drawings of the nets. Inspection output, not an input to the pipeline. |

## `docs/`

| Path | What it is |
|---|---|
| `docs/dataset.md` | What the denied-loan log contains. |
| `docs/pipeline.md` | What the five steps compute. |
| `docs/architecture.md` | This map. |
| `docs/toy.md` | The five-trace example: the hand counts and the recovered rule. |
| `docs/toy_parallel.md` | The second toy, with a parallel block and an exclusive choice, and the SimPN spike. |
| `docs/results.md` | The locked cutoff 14 result, its rules, the cutoff comparison and the lifecycle merge experiment. |
| `docs/Report/` | The short paper (Quarto source, PDF, bibliography, figures). |
| `docs/poster/` | The poster (HTML, PDF, the script that builds the HTML, figures). |

`pyproject.toml` lists the libraries: pm4py for the log, the net, and the alignments; pandas and numpy for the encoding table; scikit-learn for the tree; matplotlib for the figures; simpn for the toy spike only.
