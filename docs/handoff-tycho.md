# Handoff for Tycho

The pipeline is built and has been run on all 3,093 denied applications. What is left is to understand it, review the classification code, and interpret the output: which cutoff counts as a fast denial, what the scores mean, and what the rules say about the loan process. The short paper is a later group decision and is not part of this handoff.

Read these first, in this order:

1. [pipeline.md](pipeline.md): what the five steps compute.
2. [dataset.md](dataset.md): what the activity names mean.
3. [toy.md](toy.md): the five-trace example, the counts you can fill in by hand, and the rule the tree recovers.
4. [architecture.md](architecture.md): which file does which step.

`docs/Report/Report-process-Mining.qmd` is behind the code. It still describes the tree and the rules as pending.

## What already runs

```bash
uv run python src/main.py --cutoff 14
```

That command reads `data/source/BPI2017Denied(3).xes` and `data/source/BPI2017Denied_petriNet.pnml`, then:

1. Sets `throughput_time` on each case: last timestamp minus first, in days. Lower is better.
2. Aligns each case to the Petri net. For each activity it counts model moves (the net required the step and the log skipped it) and log moves (the log did the step and the net does not allow it). Synchronous moves are ignored. Silent transitions are not activities.
3. Labels a case `good` when throughput is at or below the cutoff, and `bad` when it is above.
4. Holds out 25% of cases (`random_state=0`). On the other 75%, a grid search tries depth 2 to 5 and minimum leaf size 5, 10, and 20. It keeps the tree with the best F1 on the class `bad`.
5. Writes three files.

| File | What it is |
|---|---|
| `data/output/alignment_encodings.csv` | One row per application: case id, throughput, move counts. 3,093 rows. This file does not depend on the cutoff. |
| `data/output/tree_rules.csv` | One row per leaf: the conditions, the predicted class, and how many cases are good or bad. The current file has 24 leaves. |
| `data/output/tree_rule_cases.csv` | `rule_id` and `case_id` for every application. |

Do not re-align the log to try another cutoff. Refit only the tree:

```bash
uv run python scripts/fit_tree.py --cutoff 14 --export-cases data/output/tree_rule_cases.csv
```

That overwrites `tree_rules.csv` and, with `--export-cases`, the case list. The throughput distribution, which you need before locking a cutoff, comes from:

```bash
uv run python scripts/inspect_throughput.py
```

## Scores on the holdout, rules on the whole log

This split is intentional.

The assignment asks for two outputs: the rules, and for each rule the applications from the original log that match it. `extract_leaf_rules` in `src/classification/model.py` therefore walks every row. The printed precision and recall answer a different question: on the 25% the tree was not fitted on, how often the predicted class `bad` matches a throughput above the cutoff. The grid search fits on the other 75% only. That same tree is then applied to all 3,093 cases, so the held-out applications still appear under a rule.

`n_cases`, `n_good`, `n_bad`, and `share_bad` are those full-log counts. They will not equal the printed precision and recall. `share_bad` says how slow the applications in that leaf actually are. The held-out scores say how well the tree predicts the cutoff on cases it did not see.

On five toy rows the holdout is turned off. That script checks that a planted rule comes back. It is not a prediction test. See [toy.md](toy.md).

```bash
uv run python scripts/align_toy.py
uv run python scripts/check_toy_rules.py
```

`align_toy.py` prints the move-count table. Compare it to the hand table in `toy.md`. It does not print precision and recall, and the events have no timestamps, so `throughput_time` is empty. `check_toy_rules.py` plants the days, fits a tree of depth 1, and prints precision and recall against cases `t3` and `t4`. Those scores show the script recovers a rule you wrote yourself. They say nothing about the bank.

## What to review

The code to read carefully is `src/classification/model.py`. The rest of `src/` already runs and does not need a redesign.

- `label_throughput` marks `good` at or below the cutoff and `bad` above it.
- `DeviationTree.fit` does the holdout, the grid search, the held-out precision and recall of `bad`, and then the full-log rules.
- `extract_leaf_rules` turns each leaf into conditions and case ids.
- `scripts/fit_tree.py` is the refit entry point. `src/main.py` is the full pipeline.

## What to decide and interpret

**Lock the cutoff.** The notes describe throughput as about two weeks. `scripts/inspect_throughput.py` prints the minimum, median, and maximum and saves `data/output/throughput_hist.png`. A median split makes the two classes about equal. A cutoff of 14 days means "faster than two weeks," and the class balance follows whatever share of applications finish by then. Precision and recall move when the balance moves, so keep the printed `good=` and `bad=` next to the scores.

The current `tree_rules.csv` does not store the cutoff that produced it. `docs/architecture.md` shows `--cutoff 14` as the example command. Confirm that this file came from that command before interpreting the 24 rules. If that is uncertain, refit and treat the new printout as the result. Write the chosen cutoff down once and then leave it alone.

**Read a condition as a count.** The counts are integers, so the printed cuts mean:

- `<= 0.5` means zero times
- `> 0.5` means at least once
- `> 1.5` means at least twice
- `> 2.5` means at least three times

A log move is an activity the net does not allow at that point. A model move is an activity the net required and the log skipped. [dataset.md](dataset.md) is the glossary. The duration differences sit in the work items: calls and validations that are suspended, resumed, or aborted, and offers that are created, returned, or refused more than once.

**Read `predicted_class` and `share_bad` as two different facts.** `predicted_class` is the label the tree assigns to the leaf. `share_bad` is the real share of slow cases in that leaf on the full log. They can disagree. In the current file, rule 7 is predicted `bad` while 9 of its 14 cases are `good` (`share_bad` 0.36). That leaf is a place where the tree is wrong, not a slow pattern.

Rule 8 is the mass of the log: 1,108 applications, predicted `bad`, `share_bad` 0.55, because of at least one log move on `W-Call-after-offers-suspend`. That is a weak separation on a huge group. It may be the common path, slightly slower than the rest, rather than a deviation worth singling out. Leaves with 7 to 15 cases exist because `min_samples_leaf` goes down to 5. Do not rest an interpretation on those.

The case ids for a rule are the matching `rule_id` in `tree_rule_cases.csv`.

## Knobs, if the rules are unreadable

Change one of these only to make the rules something you can explain, and keep a note of the setting you actually used.

- `--cutoff`, the one that must be chosen
- `--test-size` (0.25) and `--random-state` (0) on `fit_tree.py` and `main.py`
- `DEFAULT_PARAM_GRID` in `src/classification/model.py`: depth 2 to 5 and leaf size 5, 10, 20

A shallower tree, or a larger minimum leaf, will usually score a bit worse and be easier to explain. The grid search optimises F1 of `bad`, while the printout reports precision and recall of `bad`. If you change the grid, the printed scores are for the new setting.

Leave the encoding, the throughput formula, and the file loaders as they are.
