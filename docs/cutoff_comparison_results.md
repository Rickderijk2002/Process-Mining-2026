# Cutoff comparison: 14, 18, 21 days

Classification tree on alignment move counts (BPIC 2017 Denied, 3,093 traces). Label: slow (bad) if throughput time > cutoff, otherwise fast (good). Positive class = slow.

Setup: `DeviationTree`, GridSearchCV (5-fold, F1 on slow), grid over `max_depth` [2-5], `min_samples_leaf` [5, 10, 20], `ccp_alpha` [0, 0.001, 0.01, 0.1] (pruning), stratified 25% hold-out, seed 0. The balanced variant additionally fixes `class_weight="balanced"`. Each cutoff is compared with its own all-bad baseline (predict every case slow: precision = slow share, recall = 1).

Source: `scripts/compare_cutoffs.py` -> `data/output/cutoff_comparison.csv`, `cutoff_comparison_rules.csv`.

## Results (hold-out, seed 0)

| Cutoff | Slow cases (share) | Variant | ccp_alpha / depth / min leaf | Rules (slow) | Precision (baseline) | Recall | F1 (baseline F1) |
|---|---|---|---|---|---|---|---|
| 14 | 1,592 (51.5%) | unweighted = balanced | 0.01 / 2 / 5 | 2 (1) | 0.563 (0.515) | 0.970 | 0.712 (0.680) |
| 18 | 1,034 (33.4%) | unweighted | 0.0 / 5 / 20 | 22 (7) | 0.639 (0.334) | 0.151 | 0.244 (0.501) |
| 18 | | balanced | 0.01 / 2 / 5 | 2 (1) | 0.381 (0.334) | 0.985 | 0.549 (0.501) |
| 21 | 767 (24.8%) | unweighted | 0.001 / 4 / 5 | 8 (4) | 0.580 (0.248) | 0.151 | 0.240 (0.397) |
| 21 | | balanced | 0.001 / 4 / 10 | 11 (6) | 0.337 (0.248) | 0.854 | 0.484 (0.397) |

Baseline F1 = 2p / (1 + p), with p the slow share.

## Observations

1. **Cutoff 14 is insensitive to balancing.** The classes are already about 50/50, so both variants give the same single split.
2. **Unweighted trees at 18 and 21 trade recall for precision.** Precision is 1.7x to 2.3x the baseline, but recall is 0.151 and F1 is below the all-bad predictor. They isolate a small, precise slow group and miss most slow cases.
3. **Balanced trees at 18 and 21 beat the all-bad F1, but only modestly** (+0.05 and +0.09), mostly by flagging most cases as slow. Precision is only 3 to 9 points above baseline.
4. **At 18, balancing collapses the tree to the cutoff-14 split.** The result is 2 rules, with a slow-rule share of 0.37.
5. **Pruning matters most at 18 unweighted.** The search chose `ccp_alpha = 0` there, which gives 22 rules. The other configurations use pruning and have 2 to 11 rules.

## Rules

- `log_move_W-Call-after-offers-suspend` is the root split in every variant. Cases without this log move (389, 12.6%) are mostly fast: 16% slow at cutoff 14, 9% at 18, 6% at 21. The tree is mainly a detector of fast cases.
- Cutoffs 18 and 21 share `log_move_O-Refused` and `model_move_W-Complete-application-suspend`.
- The strongest slow rules (unweighted) are small leaves: three or more `O-Refused` log moves, repeated validate suspend/resume, and log moves around fraud assessment. Slow shares are 59% to 72%, leaves have under about 120 cases (for example 113 cases at 60% and 29 cases at 72% at cutoff 21), which explains the low recall.
- Balanced trees contain "slow" leaves that are barely above the baseline (for example 1,201 cases at 26.7% slow vs a 24.8% baseline at cutoff 21). They are flagged slow only because of the class weights and are weak rules to interpret.

## Caveats

- One seed, one 25% hold-out split: differences of a few points are within noise. Rerun with `--seeds 0 1 2 3 4`.
- Hold-out scores come from the split; the rule listings are computed on all 3,093 traces.
- Many split features are lifecycle-level log moves (suspend, resume, start, schedule), which may be an artefact of the encoding.
- No published BPIC 2017 paper uses the Denied subset with a throughput KPI and alignment-based trees, so there is no direct comparison. Related work (Park et al., grid search with 5-fold CV and pruning) supports the setup.
- The earlier locked result (20 rules, precision 0.62, recall 0.74) predates pruning and is outdated.
