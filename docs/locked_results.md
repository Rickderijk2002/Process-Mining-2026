# Locked results: classification step

## Decision

**Cutoff: 14 days.** A denied application with throughput time at or below 14 days is `good` (fast denial). One above 14 days is `bad` (slow denial).

Why 14: it sits almost exactly at the median (14.43 days), so the classes are nearly balanced, and "faster than two weeks" is easy to explain. It was chosen before any tree scores were seen.

Other settings were left at their defaults: test size 0.25, random state 0. The result was reproduced with identical output on a second run.

## Throughput distribution (all 3,093 applications)

| Statistic | Days |
|---|---|
| Minimum | 0.0058 |
| Median | 14.43 |
| Mean | 17.0 |
| Maximum | 259.89 |

Right-skewed, with a thin long tail. The tallest histogram bar contains the median, so many cases sit close to the 14-day boundary.

## Locked result

| Item | Value |
|---|---|
| Rows | 3,093 |
| Class balance | good = 1,501, bad = 1,592 (48.5% / 51.5%) |
| Best parameters | `max_depth` = 5, `min_samples_leaf` = 10 |
| Held-out precision (class `bad`) | 0.621 |
| Held-out recall (class `bad`) | 0.744 |
| Held-out F1 (class `bad`) | about 0.68 |
| Rules (leaves) | 20 |

Scores are on the 25% holdout only. The rules and their `n_cases`, `n_good`, `n_bad`, `share_bad` are computed on the full log, so they will not match the printed scores. This is intentional.

## How to read the scores

- A tree that predicts `bad` for every case would get precision of about 0.515, recall of 1.0 and F1 of about 0.68.
- The tree reaches precision 0.62 (above the 0.515 base rate) but has about the same F1 as that trivial predictor. It carries some signal, but it is weak.
- Likely reasons: many cases lie near the 14-day boundary, and the move counts explain only part of the duration.
- The holdout is one split (about 770 cases), so scores could shift by a few points with another random state.

## Stability check (four random splits, cutoff 14)

The headline result above stays fixed at seed 0. To see how much it depends on the 75/25 split, the tree was refitted with other seeds. The class balance was good = 1,501 and bad = 1,592 in every run.

| Seed | Best parameters | Precision | Recall | F1 | Rules |
|---|---|---|---|---|---|
| 0 (locked) | depth 5, leaf 10 | 0.621 | 0.744 | 0.677 | 20 |
| 1 | depth 5, leaf 5 | 0.603 | 0.724 | 0.657 | 24 |
| 2 | depth 4, leaf 20 | 0.597 | 0.744 | 0.662 | 14 |
| 3 | depth 5, leaf 10 | 0.629 | 0.774 | 0.694 | 23 |
| **Mean** | | **0.612** | **0.746** | **0.673** | |
| **Range** | | 0.597 to 0.629 | 0.724 to 0.774 | 0.657 to 0.694 | 14 to 24 |

F1, the mean and the ranges were computed from the printed precision and recall.

What it shows:

- The locked scores are close to the mean, so they are representative and not a lucky split.
- Precision is always above the 0.515 base rate, but F1 stays around the 0.68 of a tree that predicts `bad` for every case. The signal is real but modest.
- The tree's shape is unstable: depth 4 or 5, leaf size 5, 10 or 20, and 14 to 24 rules. No single lower-level leaf should be treated as a stable finding.
- Whether the first split (`LM W-Call-after-offers-suspend`) is the same on every seed was not checked.

Seed 0 was fixed before this check. Choosing the best of four seeds (seed 3) would be tuning on the result, so the headline was not changed. Only the split and the tree's tie-breaking vary here, so this measures how much the holdout estimate moves, not performance on new data.

Suggested sentence for the paper: "Over four random splits, precision ranged from 0.60 to 0.63 and recall from 0.72 to 0.77."

## Files that belong to this result

- `data/output/tree_rules.csv` (20 rules)
- `data/output/tree_rule_cases.csv` (case ids per rule)
- `data/output/alignment_encodings.csv` (independent of the cutoff)

## Still to do

- Read the 20 rules: check `predicted_class` against `share_bad`, ignore leaves with fewer than about 15 cases, and interpret the largest leaves using `dataset.md`.
- Optionally check that the first split is the same on every seed.
- Settle with the group whether the toy plus the held-out score is enough as the "manually built gold standard".
