# The pipeline

The pipeline answers one question about these denied applications: which departures from the normative Petri net go together with a long time from the first event to the last. Denial itself is already true for every case, so the model never predicts it.

This is the deviation-analysis step from Dees, de Leoni and Mannhardt (2017). The program takes the BPI 2017 Denied event log and its Petri net, and returns rules that link deviations to throughput time, plus the traces that match each rule. The data those rules describe is in [dataset.md](dataset.md).

## 1. Measure how long each denial took

For each application, `throughput_time` is the last timestamp minus the first, in days. Lower is better. A case that opens on Monday and reaches `A-Denied` ten days later has throughput 10, whatever activities sit in between.

## 2. Compare each case with the Petri net

The Petri net is the normative model: the path the bank's process is supposed to follow. An alignment walks one application and the net together and marks every step as one of three moves.

- **Synchronous move.** The log and the net both take that activity. The case did what the model allows. These are ignored later.
- **Model move.** The net needs the activity and the log skips it. The application missed a required step.
- **Log move.** The log takes the activity and the net does not allow it there. The application did something extra, or did it out of place.

Silent `Inv` transitions in the net are not activities, so they never become features.

## 3. Turn that comparison into one row per application

Each case becomes a row: its id, its `throughput_time`, and two counts per activity, `model_move_*` and `log_move_*`. With about 2,038 different sequences, the activity string itself is a poor feature. The counts say how the case departed from the net, which is what the tree is allowed to use.

`src/main.py` does steps 1 to 5 in one run. It needs `--cutoff`, because good and bad are chosen from the throughput distribution. It writes `data/output/alignment_encodings.csv`, `data/output/tree_rules.csv`, and `data/output/tree_rule_cases.csv`.

## 4. Split fast and slow, then let a tree explain the split

You pick a cutoff in days. An application at or below the cutoff is **good** (a fast denial). One above it is **bad** (a slow denial).

A classification tree predicts that label from the move counts only. It never sees the timestamps again. A quarter of the cases is held out. On the rest, a grid search tries tree depths 2 to 5 and minimum leaf sizes 5, 10, and 20, and keeps the tree with the best F1 on the **bad** class.

## 5. Read each leaf as a rule

A leaf is a conjunction of thresholds, for example "the after-offers call was suspended in the log more than once, and the application was not missing the abort the net expected." Every application whose counts satisfy that conjunction is listed under the rule, with how many of them are actually good or bad.

The rules and the case lists are the result on the loan log. `scripts/fit_tree.py` repeats steps 4 and 5 from a saved encoding table, so a new cutoff does not require aligning the log again.

## What gets scored

The loan traces are too long to check by hand, so the same scripts are first run on a tiny log and a tiny net where the correct move counts and the correct rule are already written down. The toy and the loan log are the same kind of input. They are not the same process, and the script will not find the same deviations in both.

- **Alignments.** Precision and recall against those hand-written counts.
- **Rules.** Precision and recall against the case list written for the planted rule.
- **Loan log.** Precision and recall of the tree's predicted class against the class from the cutoff, on the held-out applications only.

The toy checks that a log move is still a log move. The loan rules are new: they describe which deviations in these denied applications travel with a long throughput time.
