# Derived rule set (cutoff 14 days)

This file documents the 20 classification rules from the locked run, what they mean for the denied-loan process, and the evidence behind each statement. `LM` means a log move and `MM` a model move, per activity.

## 1. Provenance

| Item | Value |
|---|---|
| Source | `data/output/tree_rules.csv` (cutoff 14) |
| Cutoff | 14 days: at or below is `good`, above is `bad` |
| Class balance | good = 1,501, bad = 1,592 |
| Tree | `max_depth` 5, `min_samples_leaf` 10, held-out 25%, `random_state` 0 |
| Held-out scores (class `bad`) | precision 0.621, recall 0.744 |
| Rules | 20 (one per leaf) |

The rules and their counts are computed on the **full log** (3,093 applications). The scores are on the **held-out 25%**. They answer different questions and are not expected to match.

## 2. Integrity checks on the rule file

These were run on `tree_rules.csv`:

| Check | Result |
|---|---|
| `n_cases` summed over the 20 rules | 3,093 (every application is in exactly one rule) |
| `n_good` summed | 1,501 (matches the class balance) |
| `n_bad` summed | 1,592 (matches the class balance) |
| `n_good + n_bad = n_cases` for every rule | True |
| `share_bad = n_bad / n_cases` for every rule | True |
| `predicted_class = bad` exactly when `share_bad > 0.5` | True for all 20 rules |

Reading counts: `<= 0.5` is zero times, `> 0.5` at least once, `> 1.5` at least twice, `> 2.5` at least three times. Two conditions on the same feature combine, so `<= 1.5` with `> 0.5` means exactly once.

## 3. The 20 rules

| Rule | Predicted | Cases | Good | Bad | Share bad | Conditions |
|---|---|---|---|---|---|---|
| 0 | good | 19 (small) | 17 | 2 | 0.11 | LM W-Call-after-offers-suspend <= 0.5<br>LM O-Returned <= 0.5<br>MM W-Call-after-offers-ate-abort <= 0.5 |
| 1 | good | 81 | 81 | 0 | 0.00 | LM W-Call-after-offers-suspend <= 0.5<br>LM O-Returned <= 0.5<br>MM W-Call-after-offers-ate-abort > 0.5 |
| 2 | good | 17 (small) | 11 | 6 | 0.35 | LM W-Call-after-offers-suspend <= 0.5<br>LM O-Returned > 0.5<br>MM W-Handle-leads-suspend <= 0.5<br>LM O-Cancelled <= 0.5<br>LM A-Denied <= 0.5 |
| 3 | good | 233 | 190 | 43 | 0.18 | LM W-Call-after-offers-suspend <= 0.5<br>LM O-Returned > 0.5<br>MM W-Handle-leads-suspend <= 0.5<br>LM O-Cancelled <= 0.5<br>LM A-Denied > 0.5 |
| 4 | good | 12 (small) | 12 | 0 | 0.00 | LM W-Call-after-offers-suspend <= 0.5<br>LM O-Returned > 0.5<br>MM W-Handle-leads-suspend <= 0.5<br>LM O-Cancelled > 0.5 |
| 5 | good | 27 | 16 | 11 | 0.41 | LM W-Call-after-offers-suspend <= 0.5<br>LM O-Returned > 0.5<br>MM W-Handle-leads-suspend > 0.5 |
| 6 | bad | 1046 | 448 | 598 | 0.57 | LM W-Call-after-offers-suspend > 0.5<br>MM W-Complete-application-suspend <= 0.5<br>LM O-Create-Offer <= 0.5<br>LM W-Validate-application-suspend <= 2.5<br>LM W-Call-after-offers-suspend <= 2.5 |
| 7 | good | 20 (small) | 14 | 6 | 0.30 | LM W-Call-after-offers-suspend > 0.5<br>MM W-Complete-application-suspend <= 0.5<br>LM O-Create-Offer <= 0.5<br>LM W-Validate-application-suspend <= 2.5<br>LM W-Call-after-offers-suspend > 2.5 |
| 8 | bad | 152 | 47 | 105 | 0.69 | LM W-Call-after-offers-suspend > 0.5<br>MM W-Complete-application-suspend <= 0.5<br>LM O-Create-Offer <= 0.5<br>LM W-Validate-application-suspend > 2.5<br>LM W-Call-after-offers-resume <= 0.5 |
| 9 | bad | 15 (small) | 3 | 12 | 0.80 | LM W-Call-after-offers-suspend > 0.5<br>MM W-Complete-application-suspend <= 0.5<br>LM O-Create-Offer <= 0.5<br>LM W-Validate-application-suspend > 2.5<br>LM W-Call-after-offers-resume > 0.5 |
| 10 | good | 15 (small) | 11 | 4 | 0.27 | LM W-Call-after-offers-suspend > 0.5<br>MM W-Complete-application-suspend <= 0.5<br>LM O-Create-Offer > 0.5<br>LM O-Returned <= 0.5 |
| 11 | bad | 374 | 106 | 268 | 0.72 | LM W-Call-after-offers-suspend > 0.5<br>MM W-Complete-application-suspend <= 0.5<br>LM O-Create-Offer > 0.5<br>LM O-Returned > 0.5<br>LM W-Complete-application-suspend <= 0.5 |
| 12 | bad | 15 (small) | 1 | 14 | 0.93 | LM W-Call-after-offers-suspend > 0.5<br>MM W-Complete-application-suspend <= 0.5<br>LM O-Create-Offer > 0.5<br>LM O-Returned > 0.5<br>LM W-Complete-application-suspend > 0.5 |
| 13 | good | 692 | 398 | 294 | 0.42 | LM W-Call-after-offers-suspend > 0.5<br>MM W-Complete-application-suspend > 0.5<br>LM O-Create-Offer <= 0.5<br>LM W-Assess-potential-fraud-resume <= 0.5<br>MM W-Call-incomplete-files-ate-abort <= 0.5 |
| 14 | bad | 67 | 31 | 36 | 0.54 | LM W-Call-after-offers-suspend > 0.5<br>MM W-Complete-application-suspend > 0.5<br>LM O-Create-Offer <= 0.5<br>LM W-Assess-potential-fraud-resume <= 0.5<br>MM W-Call-incomplete-files-ate-abort > 0.5 |
| 15 | bad | 19 (small) | 4 | 15 | 0.79 | LM W-Call-after-offers-suspend > 0.5<br>MM W-Complete-application-suspend > 0.5<br>LM O-Create-Offer <= 0.5<br>LM W-Assess-potential-fraud-resume > 0.5<br>LM W-Validate-application-start <= 0.5 |
| 16 | bad | 15 (small) | 5 | 10 | 0.67 | LM W-Call-after-offers-suspend > 0.5<br>MM W-Complete-application-suspend > 0.5<br>LM O-Create-Offer <= 0.5<br>LM W-Assess-potential-fraud-resume > 0.5<br>LM W-Validate-application-start > 0.5 |
| 17 | good | 14 (small) | 9 | 5 | 0.36 | LM W-Call-after-offers-suspend > 0.5<br>MM W-Complete-application-suspend > 0.5<br>LM O-Create-Offer > 0.5<br>LM O-Returned <= 1.5<br>LM O-Returned <= 0.5 |
| 18 | bad | 244 | 94 | 150 | 0.61 | LM W-Call-after-offers-suspend > 0.5<br>MM W-Complete-application-suspend > 0.5<br>LM O-Create-Offer > 0.5<br>LM O-Returned <= 1.5<br>LM O-Returned > 0.5 |
| 19 | bad | 16 (small) | 3 | 13 | 0.81 | LM W-Call-after-offers-suspend > 0.5<br>MM W-Complete-application-suspend > 0.5<br>LM O-Create-Offer > 0.5<br>LM O-Returned > 1.5 |

"small" marks leaves with 20 cases or fewer (rules 0, 2, 4, 7, 9, 10, 12, 15, 16, 17, 19). No claim in this document rests on them. Rules 11 and 17 contain a redundant condition because the tree split twice on the same feature.

## 4. Main finding: the first split

Every rule starts with `LM W-Call-after-offers-suspend`.

| Group | Rules | Cases | Bad | Share bad |
|---|---|---|---|---|
| No log move on the call suspend | 0 to 5 | 389 | 62 | 15.9% |
| At least one log move | 6 to 19 | 2,704 | 1,530 | 56.6% |

Both groups sum from the table above. The base rate over the whole log is 51.5%.

## 5. What the net allows (evidence for the meaning of the features)

The meaning of a log move or model move depends on what the Petri net allows. This was read from the drawing of the net (`petri_net.svg`) by listing each transition's input and output places. It is a structural reading. No alignments were replayed for this document.

| Task or feature | What the net allows | Consequence for the rules |
|---|---|---|
| `W-Call-after-offers` | One pass: schedule, start, then one suspend, one resume and one abort, then complete, withdraw or skip. No loop and no way to skip the suspend. | `LM ...-suspend > 0.5` means at least two suspends. `> 2.5` means roughly four or more. |
| `W-Complete-application` | A suspend and resume loop that can repeat. The resume can be skipped. A resume can only follow a suspend. | `MM ...-suspend > 0.5` most likely means a resume with no suspend before it. |
| `W-Validate-application` | Within one pass, at most one suspend and one resume, or none. Whether the whole validation can repeat was not traced. | `LM ...-suspend > 2.5` means roughly four or more suspends. |
| `O-Create-Offer` | Once. `O-Cancelled` is optional before it. No loop. | `LM O-Create-Offer > 0.5` means a second offer was created. |
| `O-Returned` | One slot after the call, as an alternative to scheduling validation. Reused only through the incomplete-files loop. | A log move means the return happened outside that slot. This is common. This is the least certain reading. |
| `A-Denied` | One slot right after the call, followed by `O-Refused`. | Every case has exactly one `A-Denied`, so `LM A-Denied` is a modelling artefact and carries no business meaning. |

The labels of the net were listed with `pm4py.read_pnml`. All `W-` tasks have suspend and resume labels.

## 6. The story across the rules

| Step | Rule | Cases | Share bad |
|---|---|---|---|
| Call suspended at most once | 0 to 5 | 389 | 16% |
| Call suspended two or more times, nothing else flagged | 6 | 1,046 | 57% |
| Plus roughly four or more validation suspends | 8 | 152 | 69% |
| Plus a second offer and an off-slot return | 11 | 374 | 72% |

The more the work is interrupted and the more offer rounds there are, the larger the share of slow denials.

Other leaves that support or qualify this:

| Rule | Cases | Share bad | Reading |
|---|---|---|---|
| 1 | 81 | 0.00 | No extra call suspension and the abort missing (`MM W-Call-after-offers-ate-abort`). All 81 are fast. They skip the long call. |
| 3 | 233 | 0.18 | No extra call suspension. Depends on `LM A-Denied`, so it is not interpreted as a business pattern. |
| 13 | 692 | 0.42 | Suspended call with a missing complete-application suspend. Mixed, predicted `good`, with 294 slow cases. |
| 18 | 244 | 0.61 | The rule 11 pattern plus the missing complete-application suspend, and exactly one `LM O-Returned`. |

## 7. Limitations

- **Association, not cause.** Throughput is elapsed time and every suspend adds waiting time, so "more suspends, slower" is partly built in.
- **Most cases deviate.** 2,704 of 3,093 applications (87%) have a log move on the call suspend. The net describes one suspend, but repeated suspension is the normal case. This may point to a model that is too strict, which is a discussion point and not a result.
- **Rule 6 is close to the base rate.** 1,046 cases at 57% bad is the common path, only slightly slower.
- **Predictive power is modest.** Held-out precision 0.62 and recall 0.74, and a tree that predicts `bad` for every case has an F1 of about 0.68, the same as this tree. The rules are tendencies.
- **Small leaves.** Leaves with 20 cases or fewer are not interpreted, even when their share bad looks extreme (rule 12 at 0.93, rule 19 at 0.81).
- **One split.** The scores come from one held-out split with `random_state` 0.
- **Unchecked parts of the net.** The wiring was read from the drawing only, and the validation repeat and the `O-Returned` slot were not confirmed with replayed alignments.
