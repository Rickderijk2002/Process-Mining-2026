# Locked results: classification step

## Cutoff and fixed search protocol

**Cutoff: 14 days.** A denied application with throughput time at or below 14 days is `good` (fast denial); one above 14 days is `bad` (slow denial). The cutoff is close to the all-log median of 14.43 days and was selected before fitting the tree.

Before looking at scores for this run, the search grid was fixed at 48 combinations:

| Parameter | Candidates |
|---|---|
| `max_depth` | 2, 3, 4, 5 |
| `min_samples_leaf` | 5, 10, 20 |
| `ccp_alpha` | 0, 0.001, 0.01, 0.1 |

`class_weight` is not searched: the classes are nearly balanced at this cutoff, so class weighting was excluded to keep the search focused. Grid search maximizes five-fold cross-validated F1 for `bad`, using only the 75% training partition. The locked evaluation uses the remaining 25%, `random_state=0`, and test size 0.25. Random seed is set to 0 for any and all runs, unless specified otherwise.

## Data distribution

| Item | Value |
|---|---:|
| Applications | 3,093 |
| Good (at or below 14 days) | 1,501 (48.5%) |
| Bad (above 14 days) | 1,592 (51.5%) |
| Throughput minimum | 0.0058 days |
| Throughput median | 14.43 days |
| Throughput mean | 17.0 days |
| Throughput maximum | 259.89 days |

## Locked result

| Item | Value |
|---|---:|
| Best parameters | `max_depth=2`, `min_samples_leaf=5`, `ccp_alpha=0.01` |
| Held-out precision (`bad`) | 0.563 |
| Held-out recall (`bad`) | 0.970 |
| Held-out F1 (`bad`) | 0.712 |
| Rules (leaves) | 2 |

Precision and recall are calculated on the held-out 25%. The rule conditions are from the fitted estimator, and their case counts are calculated over all 3,093 applications, including the training and held-out partitions.

The all-`bad` baseline has precision 0.515, recall 1.000, and F1 about 0.680. The locked tree has substantially higher F1 and recall, though its precision is only slightly above the class base rate.

## Stability check (random seeds 0–3)

The grid, cutoff, and test size were kept fixed. The locked result remains seed 0; the other seeds measure split sensitivity, not alternatives from which to select a better headline.

| Seed | Best parameters (`depth`, `leaf`, `ccp_alpha`) | Precision | Recall | F1 | Rules |
|---:|---|---:|---:|---:|---:|
| 0 (locked) | 2, 5, 0.01 | 0.563 | 0.970 | 0.712 | 2 |
| 1 | 5, 5, 0.001 | 0.600 | 0.736 | 0.661 | 11 |
| 2 | 4, 20, 0 | 0.597 | 0.744 | 0.662 | 14 |
| 3 | 2, 5, 0.01 | 0.568 | 0.970 | 0.716 | 2 |
| **Mean** | | **0.582** | **0.855** | **0.688** | **7.25** |
| **Range** | | **0.563–0.600** | **0.736–0.970** | **0.661–0.716** | **2–14** |

Testing across seeds shows differing optimal parameters, and differing numbers of leaves. While seeds 0 and 3 show a highly pruned two-rule tree, seeds 1 and 2 select much larger trees.
The pruned tree (as used in seed 0) has substantially higher recall, but suffers from lower precision. We can thus conclude there is significant instability in the classification process.

## Result files

These versioned outputs were written for this run (prior result files were left unchanged):

- `data/output/tree_rules_cutoff14_pruned_2026-10-06.csv` - two full-log leaf summaries and conditions.
- `data/output/tree_rule_cases_cutoff14_pruned_2026-10-06.csv` - full-log case-to-rule assignment.
- `data/output/tree_stability_cutoff14_pruned_2026-10-06.csv` - per-seed scores and selected parameters.
- `data/output/alignment_encodings.csv` - reused unchanged; independent of the cutoff.

Reproduce the locked fit into fresh files:

```powershell
.\.venv\Scripts\python.exe scripts\fit_tree.py --cutoff 14 --random-state 0 --output data\output\tree_rules_cutoff14_pruned_rerun_2026-10-06.csv --export-cases data\output\tree_rule_cases_cutoff14_pruned_rerun_2026-10-06.csv
```

Rerun the stability check to a fresh output path:

```powershell
.\.venv\Scripts\python.exe scripts\check_tree_stability.py --cutoff 14 --seeds 0 1 2 3 --output data\output\tree_stability_cutoff14_pruned_rerun_2026-10-06.csv
```
