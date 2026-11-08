# Results

This note records the results of the classification step on the BPIC 2017 Denied log (3,093 traces): the locked result at a cutoff of 14 days, the rules of that fit, and the comparison across cutoffs. A trace is `bad` (slow, the positive class) when its throughput time is above the cutoff, otherwise `good` (fast). The method is in [pipeline.md](pipeline.md), the data in [dataset.md](dataset.md).

All commands run from the project root. With pip instead of uv, write `python` instead of `uv run python`.

All numbers in this note come from the stored encoding table `data/output/alignment_encodings.csv`. `python scripts/reproduce_all.py --skip-align` regenerates every result file from it and reports them as identical. A fresh alignment can differ on about 14 of the 3,093 traces, because a trace can have several optimal alignments of equal cost (see the README), and that shifts some of the numbers below slightly.

## 1. Locked result at cutoff 14

### Cutoff and fixed search protocol

**Cutoff: 14 days.** A denied application with throughput time at or below 14 days is `good` (fast denial); one above 14 days is `bad` (slow denial). The cutoff is close to the all-log median of 14.43 days and was selected before fitting the tree.

Before looking at scores for this run, the search grid was fixed at 48 combinations:

| Parameter | Candidates |
|---|---|
| `max_depth` | 2, 3, 4, 5 |
| `min_samples_leaf` | 5, 10, 20 |
| `ccp_alpha` | 0, 0.001, 0.01, 0.1 |

`class_weight` is not searched: the classes are nearly balanced at this cutoff, so class weighting was excluded to keep the search focused. Grid search maximizes five-fold cross-validated F1 for `bad`, using only the 75% training partition. The locked evaluation uses the remaining 25%, `random_state=0`, and test size 0.25. The random seed is 0 for every run, unless specified otherwise.

### Data distribution

| Item | Value |
|---|---:|
| Applications | 3,093 |
| Good (at or below 14 days) | 1,501 (48.5%) |
| Bad (above 14 days) | 1,592 (51.5%) |
| Throughput minimum | 0.0058 days |
| Throughput median | 14.43 days |
| Throughput mean | 17.0 days |
| Throughput maximum | 259.89 days |

### Locked result

| Item | Value |
|---|---:|
| Best parameters | `max_depth=2`, `min_samples_leaf=5`, `ccp_alpha=0.01` |
| Held-out precision (`bad`) | 0.563 |
| Held-out recall (`bad`) | 0.970 |
| Held-out F1 (`bad`) | 0.712 |
| Rules (leaves) | 2 |

Precision and recall are calculated on the held-out 25%. The rule conditions are from the fitted estimator, and their case counts are calculated over all 3,093 applications, including the training and held-out partitions.

The all-`bad` baseline has precision 0.515, recall 1.000, and F1 about 0.680. The locked tree has substantially higher F1 and recall, though its precision is only slightly above the class base rate.

### Stability check (random seeds 0 to 3)

The grid, cutoff, and test size were kept fixed. The locked result remains seed 0; the other seeds measure split sensitivity, not alternatives from which to select a better headline.

| Seed | Best parameters (`depth`, `leaf`, `ccp_alpha`) | Precision | Recall | F1 | Rules |
|---:|---|---:|---:|---:|---:|
| 0 (locked) | 2, 5, 0.01 | 0.563 | 0.970 | 0.712 | 2 |
| 1 | 5, 5, 0.001 | 0.600 | 0.736 | 0.661 | 11 |
| 2 | 4, 20, 0 | 0.597 | 0.744 | 0.662 | 14 |
| 3 | 2, 5, 0.01 | 0.568 | 0.970 | 0.716 | 2 |
| **Mean** | | **0.582** | **0.855** | **0.688** | **7.25** |
| **Range** | | **0.563 to 0.600** | **0.736 to 0.970** | **0.661 to 0.716** | **2 to 14** |

Testing across seeds shows differing optimal parameters and differing numbers of leaves. Seeds 0 and 3 show a highly pruned two-rule tree, seeds 1 and 2 select much larger trees. The pruned tree (as used in seed 0) has substantially higher recall but lower precision. There is significant instability in the classification process.

### Result files

- `data/output/tree_rules_cutoff14_pruned_2026-10-06.csv`: two full-log leaf summaries and conditions.
- `data/output/tree_rule_cases_cutoff14_pruned_2026-10-06.csv`: full-log case-to-rule assignment.
- `data/output/tree_stability_cutoff14_pruned_2026-10-06.csv`: per-seed scores and selected parameters.
- `data/output/alignment_encodings.csv`: independent of the cutoff, reused by every refit.

Reproduce the locked fit into fresh files:

```bash
uv run python scripts/fit_tree.py --cutoff 14 --random-state 0 --output data/output/tree_rules_cutoff14_pruned_rerun.csv --export-cases data/output/tree_rule_cases_cutoff14_pruned_rerun.csv
```

Rerun the stability check to a fresh output path (the script refuses to overwrite an existing file):

```bash
uv run python scripts/check_tree_stability.py --cutoff 14 --seeds 0 1 2 3 --output data/output/tree_stability_cutoff14_pruned_rerun.csv
```

## 2. The derived rule set (cutoff 14, pruned grid)

`LM` means a log move and `MM` a model move, per activity.

### Provenance

| Item | Value |
|---|---|
| Rules source | `data/output/tree_rules_cutoff14_pruned_2026-10-06.csv` |
| Case assignments | `data/output/tree_rule_cases_cutoff14_pruned_2026-10-06.csv` |
| Cutoff | 14 days: at or below is `good`, above is `bad` |
| Class balance | good = 1,501, bad = 1,592 |
| Tree | `max_depth=2`, `min_samples_leaf=5`, `ccp_alpha=0.01` |
| Held-out scores (`bad`) | precision 0.563, recall 0.970, F1 0.712 |
| Rules | 2 leaves |

The estimator is fit on 75% of the data. Precision, recall and F1 are measured on the held-out 25%; rule counts below are calculated over the full 3,093-case encoding table. The two outputs therefore describe different evaluation sets.

### Integrity checks

The two rules cover 3,093 cases exactly once. Their counts sum to 1,501 good and 1,592 bad cases, matching the full-data class balance. For each rule, `n_good + n_bad = n_cases`, `share_bad = n_bad / n_cases`, and the predicted class agrees with the majority class.

### The two rules

| Rule | Predicted | Cases | Good | Bad | Share bad | Conditions |
|---:|---|---:|---:|---:|---:|---|
| 0 | good | 389 | 327 | 62 | 0.1594 | `LM W-Call-after-offers-suspend <= 0.5` |
| 1 | bad | 2,704 | 1,174 | 1,530 | 0.5658 | `LM W-Call-after-offers-suspend > 0.5` |

Move counts are integers: `<= 0.5` means no log move on this activity; `> 0.5` means at least one. Based on the Petri-net structure, which allows one `W-Call-after-offers` suspend, a log move on that suspend indicates an additional suspend. The tree associates that pattern with a 56.6% slow-case share, versus 15.9% when the additional-suspend log move is absent.

The split is easy to explain, but the larger leaf contains 87.4% of all cases and its bad share is only 5.1 percentage points above the overall 51.5% base rate. Treat it as a modest association, not a precise characterization of every case in the group.

### Interpretation and limits

- **Association is not causation.** Throughput is elapsed time, so repeated suspensions can both signal and contribute to longer cases.
- **The pattern is common.** 2,704 of 3,093 cases have the additional-suspend log move. This may indicate a Petri net that is too strict about the number of suspensions, rather than an exceptional deviation.
- **Held-out recall is high, precision is modest.** The tree identifies almost all slow cases in the locked holdout but produces false positives. Its F1 (0.712) is above the all-`bad` baseline (about 0.680), though the improvement should be read alongside split instability.
- **The tree shape is not stable across splits.** The fixed-grid stability run selected 2, 11, 14 and 2 leaves for seeds 0 to 3. The two-rule structure is therefore not established as a stable process explanation.
- **Model interpretation has limits.** The additional-suspend reading follows from the Petri-net structure; this result does not establish why those cases take longer.

## 3. Cutoff comparison: 14, 18 and 21 days (seeds 0 to 3)

Produced by `scripts/compare_cutoffs.py`. Output files in `data/output/`:

- `cutoff_comparison.csv`: mean and sd per variant and cutoff
- `cutoff_comparison_seeds.csv`: one row per seed
- `cutoff_comparison_rules.csv`: leaf rules, seed 0 only

```bash
uv run python scripts/compare_cutoffs.py
uv run python scripts/plot_cutoff_comparison.py
```

### Setup

- **Model:** `DeviationTree` with GridSearchCV (5-fold, scoring = F1 on slow). Grid: `max_depth` [2, 3, 4, 5], `min_samples_leaf` [5, 10, 20], `ccp_alpha` [0, 0.001, 0.01, 0.1] (cost-complexity pruning).
- **Evaluation:** stratified 25% hold-out, seeds 0, 1, 2, 3 (the same seeds as the stability check at cutoff 14). Scores are the mean ± sd over seeds. The sd measures sensitivity to the random split, not independent samples, because all seeds use the same 3,093 traces.
- **Baseline:** each cutoff is compared with its own all-slow predictor: precision = slow share, recall = 1, F1 = 2p / (1 + p).
- **Class-weight variants:**
  - *unweighted*: `class_weight` fixed to None.
  - *balanced*: `class_weight` fixed to `"balanced"`.
  - *searched*: the grid search chooses between the two.

### Why we test this

- **Several cutoffs:** the slow/fast label is our choice, so we check that the findings do not depend on it. 14 days is the median of the data (14.43); 18 and 21 test rarer, longer delays. The class balance changes with the cutoff (51%, 33%, 25% slow), so each cutoff gets its own baseline.
- **Several seeds:** one random split can mislead. At cutoff 14 the selected tree has between 2 and 14 rules depending on the seed.
- **Class-weight variants:** at 18 and 21 days the slow class is a minority and trees tend to ignore minority classes. We show the unweighted tree, the forced balanced tree and the cross-validated choice, so the precision/recall trade-off is visible.
- **Pruning and cross-validated search:** `ccp_alpha`, depth and leaf size keep rule sets readable (an unpruned tree gave 22 rules at 18 days). They are tuned on training data only, so the hold-out stays untouched.
- **All-slow baseline:** a trivial predictor with recall 1 is hard to beat on F1, and a high recall alone says little.

### Results (hold-out, mean ± sd over 4 seeds)

| Cutoff | Slow share | Variant | Precision | Recall | F1 | Rules, mean (min to max) |
|---|---|---|---|---|---|---|
| 14 | 51.5% | baseline | 0.515 | 1.000 | 0.680 | none |
| 14 | | unweighted | 0.582 ± 0.019 | 0.855 ± 0.133 | 0.688 ± 0.030 | 7.3 (2 to 14) |
| 14 | | balanced | 0.584 ± 0.023 | 0.848 ± 0.141 | 0.687 ± 0.032 | 7.0 (2 to 13) |
| 14 | | searched | 0.584 ± 0.023 | 0.848 ± 0.141 | 0.687 ± 0.032 | 7.0 (2 to 13) |
| 18 | 33.4% | baseline | 0.334 | 1.000 | 0.501 | none |
| 18 | | unweighted | 0.483 ± 0.104 | 0.171 ± 0.046 | 0.247 ± 0.042 | 12.3 (4 to 22) |
| 18 | | balanced | 0.403 ± 0.016 | 0.826 ± 0.106 | 0.540 ± 0.009 | 8.0 (2 to 12) |
| 18 | | searched | 0.403 ± 0.016 | 0.826 ± 0.106 | 0.540 ± 0.009 | 8.0 (2 to 12) |
| 21 | 24.8% | baseline | 0.248 | 1.000 | 0.397 | none |
| 21 | | unweighted | 0.608 ± 0.021 | 0.133 ± 0.020 | 0.217 ± 0.027 | 11.0 (8 to 18) |
| 21 | | balanced | 0.320 ± 0.014 | 0.814 ± 0.030 | 0.460 ± 0.018 | 12.3 (11 to 14) |
| 21 | | searched | 0.320 ± 0.014 | 0.814 ± 0.030 | 0.460 ± 0.018 | 12.3 (11 to 14) |

The *searched* variant picked `balanced` in 4 of 4 seeds at 18 and 21, so its results equal the balanced variant there. At 14 it picked `balanced` in 2 of 4 seeds (seeds 1 and 2); in seeds 0 and 3 both settings give the same 2-rule tree.

### Findings

1. **Cutoff 14: the tree barely beats the all-slow predictor.** Mean F1 is 0.687 to 0.688 against a baseline of 0.680, with an sd of 0.03. Precision is about 7 points above the base rate. The result is bimodal: seeds 0 and 3 give a 2-rule tree with recall 0.97, seeds 1 and 2 give 11 to 14 rules with recall about 0.73. Class weighting makes no difference here.
2. **Cutoff 18, unweighted: high variance, low recall.** Recall is 0.14 to 0.24 and F1 (0.247) is half the all-slow F1. The single-seed precision of 0.639 (seed 0) was the best of the four; the others are 0.43 to 0.44, so the mean is 0.483 ± 0.104. Pruning did not hold the tree down: `ccp_alpha = 0` was selected in 3 of 4 seeds, giving up to 22 rules.
3. **Cutoff 21, unweighted: stable but narrow.** Precision is 0.58 to 0.63 (about 2.4x the base rate) and recall about 0.13, so the tree finds a small, precise slow group and misses most slow cases. F1 is far below the all-slow F1.
4. **Cutoffs 18 and 21, balanced / searched:** F1 is above the baseline (0.540 vs 0.501, and 0.460 vs 0.397) but the gain is modest (+0.04 and +0.06). It comes from recall of about 0.8; precision is only 7 to 8 points above the base rate. Variance across seeds is small (sd of F1 0.009 and 0.018).
5. **Rule counts depend on the seed.** Even with balancing at 18 days, seed 0 gives 2 rules and the other seeds give 9 to 12. The 2-rule trees are therefore a property of the split, not a stable finding.

### Rules (seed 0 only)

- `log_move_W-Call-after-offers-suspend` is the root split in every variant at seed 0. Traces without this log move (389, 12.6%) are mostly fast: 16% slow at cutoff 14, 9% at 18, 6% at 21. The tree acts mainly as a detector of fast traces. The other seeds' rules are not in the saved files, so we cannot yet say how often this root is chosen.
- Cutoffs 18 and 21 share `log_move_O-Refused` and `model_move_W-Complete-application-suspend`.
- The clearest slow rules (unweighted, seed 0) are small leaves: three or more `O-Refused` log moves (for example 113 traces at 60% slow and 55 traces at 71% slow), repeated validate suspend/resume, and log moves around fraud assessment. Their slow shares are 59 to 72%, but each leaf has under about 120 traces, which explains the low recall.
- Balanced trees contain "slow" leaves that are barely above the base rate, for example 1,201 traces at 26.7% slow against 24.8% at cutoff 21. They are labelled slow because of the class weights, so they are weak rules to interpret.

### Limitations

- Four seeds on a single dataset: the sd values are rough, and differences of a few points are within noise.
- The grid with `class_weight` was not fixed before the first results were seen, so the balanced and searched variants are a sensitivity analysis, not a pre-registered method.
- Many split features are lifecycle-level log moves (suspend, resume, start, schedule), which come from the encoding and make some rules hard to read.
- Rules are listed for seed 0 only, and their case counts are computed on all 3,093 traces, while the scores come from the hold-out.
- No published BPIC 2017 paper uses the Denied subset with a throughput KPI and alignment-based trees, so there is no direct comparison.

## 4. Lifecycle merge experiment

The report appendix compares the unmerged encoding (108 features) with two merged encodings, where the lifecycle variants of a work item are summed. The alignments are not recomputed, only the counting changes. The numbers are in the appendix of the report.

| Variant | Command | Output files |
|---|---|---|
| Pause and execution merged (suspend plus resume, schedule plus start plus complete) | `uv run python scripts/compare_cutoffs.py --merge` | `data/output/cutoff_comparison_merged*.csv` |
| Every lifecycle variant of a task merged into one column per move kind | `uv run python scripts/compare_cutoffs_merge_all.py` | `data/output/cutoff_comparison_merged_all*.csv` |

Each variant writes to its own files (summary, per-seed and rules), so the unmerged results are never overwritten. `compare_cutoffs_merge_all.py` is an experiment: nothing else imports it.
