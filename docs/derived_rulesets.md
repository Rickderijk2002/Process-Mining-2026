# Derived rule set (cutoff 14 days, pruned grid)

This file documents the rules from the locked, cost-complexity-pruned run. `LM` means a log move and `MM` a model move, per activity.

## 1. Provenance

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

## 2. Integrity checks

The two rules cover 3,093 cases exactly once. Their counts sum to 1,501 good and 1,592 bad cases, matching the full-data class balance. For each rule, `n_good + n_bad = n_cases`, `share_bad = n_bad / n_cases`, and the predicted class agrees with the majority class.

## 3. The two rules

| Rule | Predicted | Cases | Good | Bad | Share bad | Conditions |
|---:|---|---:|---:|---:|---:|---|
| 0 | good | 389 | 327 | 62 | 0.1594 | `LM W-Call-after-offers-suspend <= 0.5` |
| 1 | bad | 2,704 | 1,174 | 1,530 | 0.5658 | `LM W-Call-after-offers-suspend > 0.5` |

Move counts are integers: `<= 0.5` means no log move on this activity; `> 0.5` means at least one. Based on the Petri-net structure, which allows one `W-Call-after-offers` suspend, a log move on that suspend indicates an additional suspend. The tree associates that pattern with a 56.6% slow-case share, versus 15.9% when the additional-suspend log move is absent.

The split is easy to explain, but the larger leaf contains 87.4% of all cases and its bad share is only 5.1 percentage points above the overall 51.5% base rate. Treat it as a modest association, not a precise characterization of every case in the group.

## 4. Interpretation and limits

- **Association is not causation.** Throughput is elapsed time, so repeated suspensions can both signal and contribute to longer cases.
- **The pattern is common.** 2,704 of 3,093 cases have the additional-suspend log move. This may indicate a Petri net that is too strict about the number of suspensions, rather than an exceptional deviation.
- **Held-out recall is high, precision is modest.** The tree identifies almost all slow cases in the locked holdout but produces false positives. Its F1 (0.712) is above the all-`bad` baseline (about 0.680), though the improvement should be read alongside split instability.
- **The tree shape is not stable across splits.** The fixed-grid stability run selected 2, 11, 14 and 2 leaves for seeds 0–3. The two-rule structure is therefore not established as a stable process explanation.
- **Model interpretation has limits.** The additional-suspend reading follows from the Petri-net structure; this result does not establish why those cases take longer.

See [locked_results.md](locked_results.md) for the pre-fixed grid, full stability table and reproducible commands. The older unversioned files `data/output/tree_rules.csv` and `data/output/tree_rule_cases.csv` were not replaced; use the versioned files above for this pruned result.
