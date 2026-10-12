# Cutoff comparison: 14, 18, 21 days (seeds 0-3)

Classification tree on alignment move counts (BPIC 2017 Denied, 3,093 traces). A trace is slow (`bad`, the positive class) if its throughput time is above the cutoff, otherwise fast (`good`).

Produced by `scripts/compare_cutoffs.py`. Output files in `data/output/`:

- `cutoff_comparison.csv`: mean and sd per variant and cutoff
- `cutoff_comparison_seeds.csv`: one row per seed
- `cutoff_comparison_rules.csv`: leaf rules, seed 0 only

## Setup

- **Model:** `DeviationTree` with GridSearchCV (5-fold, scoring = F1 on slow). Grid: `max_depth` [2, 3, 4, 5], `min_samples_leaf` [5, 10, 20], `ccp_alpha` [0, 0.001, 0.01, 0.1] (cost-complexity pruning).
- **Evaluation:** stratified 25% hold-out, seeds 0, 1, 2, 3 (the same seeds as the stability check at cutoff 14). Scores are the mean ± sd over seeds. The sd measures sensitivity to the random split, not independent samples, because all seeds use the same 3,093 traces.
- **Baseline:** each cutoff is compared with its own all-slow predictor: precision = slow share, recall = 1, F1 = 2p / (1 + p).
- **Class-weight variants:**
  - *unweighted*: `class_weight` fixed to None.
  - *balanced*: `class_weight` fixed to `"balanced"`.
  - *searched*: the grid search chooses between the two.

## Why we test this

- **Several cutoffs:** the slow/fast label is our choice, so we check that the findings do not depend on it. 14 days is the median of the data (14.43); 18 and 21 test rarer, longer delays. The class balance changes with the cutoff (51%, 33%, 25% slow), so each cutoff gets its own baseline.
- **Several seeds:** one random split can mislead. At cutoff 14 the selected tree has between 2 and 14 rules depending on the seed.
- **Class-weight variants:** at 18 and 21 days the slow class is a minority and trees tend to ignore minority classes. We show the unweighted tree, the forced balanced tree and the cross-validated choice, so the precision/recall trade-off is visible.
- **Pruning and cross-validated search:** `ccp_alpha`, depth and leaf size keep rule sets readable (an unpruned tree gave 22 rules at 18 days). They are tuned on training data only, so the hold-out stays untouched.
- **All-slow baseline:** a trivial predictor with recall 1 is hard to beat on F1, and a high recall alone says little.

## Results (hold-out, mean ± sd over 4 seeds)

| Cutoff | Slow share | Variant | Precision | Recall | F1 | Rules, mean (min-max) |
|---|---|---|---|---|---|---|
| 14 | 51.5% | baseline | 0.515 | 1.000 | 0.680 | - |
| 14 | | unweighted | 0.582 ± 0.019 | 0.855 ± 0.133 | 0.688 ± 0.030 | 7.3 (2-14) |
| 14 | | balanced | 0.584 ± 0.023 | 0.848 ± 0.141 | 0.687 ± 0.032 | 7.0 (2-13) |
| 14 | | searched | 0.584 ± 0.023 | 0.848 ± 0.141 | 0.687 ± 0.032 | 7.0 (2-13) |
| 18 | 33.4% | baseline | 0.334 | 1.000 | 0.501 | - |
| 18 | | unweighted | 0.483 ± 0.104 | 0.171 ± 0.046 | 0.247 ± 0.042 | 12.3 (4-22) |
| 18 | | balanced | 0.403 ± 0.016 | 0.826 ± 0.106 | 0.540 ± 0.009 | 8.0 (2-12) |
| 18 | | searched | 0.403 ± 0.016 | 0.826 ± 0.106 | 0.540 ± 0.009 | 8.0 (2-12) |
| 21 | 24.8% | baseline | 0.248 | 1.000 | 0.397 | - |
| 21 | | unweighted | 0.608 ± 0.021 | 0.133 ± 0.020 | 0.217 ± 0.027 | 11.0 (8-18) |
| 21 | | balanced | 0.320 ± 0.014 | 0.814 ± 0.030 | 0.460 ± 0.018 | 12.3 (11-14) |
| 21 | | searched | 0.320 ± 0.014 | 0.814 ± 0.030 | 0.460 ± 0.018 | 12.3 (11-14) |

The *searched* variant picked `balanced` in 4 of 4 seeds at 18 and 21, so its results equal the balanced variant there. At 14 it picked `balanced` in 2 of 4 seeds (seeds 1 and 2); in seeds 0 and 3 both settings give the same 2-rule tree.

## Findings

1. **Cutoff 14: the tree barely beats the all-slow predictor.** Mean F1 is 0.687-0.688 against a baseline of 0.680, with an sd of 0.03. Precision is about 7 points above the base rate. The result is bimodal: seeds 0 and 3 give a 2-rule tree with recall 0.97, seeds 1 and 2 give 11-14 rules with recall about 0.73. Class weighting makes no difference here.
2. **Cutoff 18, unweighted: high variance, low recall.** Recall is 0.14-0.24 and F1 (0.247) is half the all-slow F1. The single-seed precision of 0.639 (seed 0) was the best of the four; the others are 0.43-0.44, so the mean is 0.483 ± 0.104. Pruning did not hold the tree down: `ccp_alpha = 0` was selected in 3 of 4 seeds, giving up to 22 rules.
3. **Cutoff 21, unweighted: stable but narrow.** Precision is 0.58-0.63 (about 2.4x the base rate) and recall about 0.13, so the tree finds a small, precise slow group and misses most slow cases. F1 is far below the all-slow F1.
4. **Cutoffs 18 and 21, balanced / searched:** F1 is above the baseline (0.540 vs 0.501, and 0.460 vs 0.397) but the gain is modest (+0.04 and +0.06). It comes from recall of about 0.8; precision is only 7 to 8 points above the base rate. Variance across seeds is small (sd of F1 0.009 and 0.018).
5. **Rule counts depend on the seed.** Even with balancing at 18 days, seed 0 gives 2 rules and the other seeds give 9-12. The 2-rule trees are therefore a property of the split, not a stable finding.

## Rules (seed 0 only)

- `log_move_W-Call-after-offers-suspend` is the root split in every variant at seed 0. Traces without this log move (389, 12.6%) are mostly fast: 16% slow at cutoff 14, 9% at 18, 6% at 21. The tree acts mainly as a detector of fast traces. The other seeds' rules are not in the saved files, so we cannot yet say how often this root is chosen.
- Cutoffs 18 and 21 share `log_move_O-Refused` and `model_move_W-Complete-application-suspend`.
- The clearest slow rules (unweighted, seed 0) are small leaves: three or more `O-Refused` log moves (for example 113 traces at 60% slow and 55 traces at 71% slow), repeated validate suspend/resume, and log moves around fraud assessment. Their slow shares are 59-72%, but each leaf has under about 120 traces, which explains the low recall.
- Balanced trees contain "slow" leaves that are barely above the base rate, for example 1,201 traces at 26.7% slow against 24.8% at cutoff 21. They are labelled slow because of the class weights, so they are weak rules to interpret.

## Limitations

- Four seeds on a single dataset: the sd values are rough, and differences of a few points are within noise.
- The grid with `class_weight` was not fixed before the first results were seen, so the balanced and searched variants are a sensitivity analysis, not a pre-registered method.
- Many split features are lifecycle-level log moves (suspend, resume, start, schedule), which come from the encoding and make some rules hard to read.
- Rules are listed for seed 0 only, and their case counts are computed on all 3,093 traces, while the scores come from the hold-out.
- No published BPIC 2017 paper uses the Denied subset with a throughput KPI and alignment-based trees, so there is no direct comparison.

## Open decisions (team meeting)

- Does class weight go into the official grid, or stay a sensitivity analysis?
- Do we drop `ccp_alpha = 0` from the grid, to limit the number of rules at 18 days?
- Which seed or aggregate is the headline, and how do we present the seed-dependent rule counts?
- Do we merge lifecycle variants in the encoding?
