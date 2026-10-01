# The toy example

The loan log is too long to replay by hand. This toy is five short traces on a net you can draw on a page. You write the move counts and the slow cases yourself, then run the same scripts. If the scripts return that page, the encoding and the rule extraction match the definitions. The toy is not the bank, and its rule is not a finding about the bank.

Two commands produce the two outputs below.

```bash
uv run python scripts/align_toy.py
uv run python scripts/check_toy_rules.py
```

`scripts/make_toy.py` writes the net and the log to `data/raw/toy.pnml` and `data/raw/toy.xes`. The traces have activity names and no timestamps, so the alignment table has no throughput yet. The rule script fills the throughput in afterwards.

## What you draw

The net is one path. `tau` is silent: it fires in the model and never appears as an activity in the log, and it is not a feature.

```text
(source) -> A -> (p1) -> B -> (p2) -> tau -> (p3) -> C -> (sink)
```

A fitting trace is `A`, `B`, `C`. Anything else is a deviation.


| Case | Trace you write down | What is wrong with it              |
| ---- | -------------------- | ---------------------------------- |
| t1   | `A, B, C`            | Nothing. This is the model.        |
| t2   | `A, C`               | `B` is missing.                    |
| t3   | `A, B, B, C`         | One extra `B`.                     |
| t4   | `A, B, B, B, C`      | Two extra `B`s.                    |
| t5   | `A, A, C`            | One extra `A`, and `B` is missing. |


Replay each trace against the path and mark every step.

- Both sides take the same activity: a synchronous move. Leave it out of the counts.
- The log takes an activity and the net does not: a log move for that activity.
- The net takes an activity and the log skips it: a model move for that activity.
- `tau` is a model move with no label. Do not count it.

The page you fill in before running the script:


| case | moves you mark                       | model A | model B | model C | log A | log B | log C |
| ---- | ------------------------------------ | ------- | ------- | ------- | ----- | ----- | ----- |
| t1   | sync A, sync B, sync C               | 0       | 0       | 0       | 0     | 0     | 0     |
| t2   | sync A, model B, sync C              | 0       | 1       | 0       | 0     | 0     | 0     |
| t3   | sync A, sync B, log B, sync C        | 0       | 0       | 0       | 0     | 1     | 0     |
| t4   | sync A, sync B, log B, log B, sync C | 0       | 0       | 0       | 0     | 2     | 0     |
| t5   | sync A, log A, model B, sync C       | 0       | 1       | 0       | 1     | 0     | 0     |


`t5` can also be drawn as log A first and then a synchronous A. The counts are the same: one extra `A`, and `B` still missing.

## What `align_toy.py` prints

```text
case_id throughput_time  model_move_A  model_move_B  model_move_C  log_move_A  log_move_B  log_move_C
     t1            None             0             0             0           0           0           0
     t2            None             0             1             0           0           0           0
     t3            None             0             0             0           0           1           0
     t4            None             0             0             0           0           2           0
     t5            None             0             1             0           1           0           0
```

`throughput_time` is `None` because these events have no timestamps. The six count columns are the hand table. That match is the alignment check. There is one column pair per activity on the net (`A`, `B`, `C`), and `tau` has no column.

## What you plant for the rule

You then choose a throughput and a cutoff, on purpose, so you already know which cases are slow and which deviation separates them.

Cutoff: 10 days. At or below is good. Above is bad.


| Case | Days you assign | Class | Why that number                           |
| ---- | --------------- | ----- | ----------------------------------------- |
| t1   | 5               | good  | The fitting trace is fast.                |
| t2   | 8               | good  | Missing `B` is still fast.                |
| t3   | 20              | bad   | One extra `B` is slow.                    |
| t4   | 30              | bad   | Two extra `B`s are slow.                  |
| t5   | 6               | good  | Extra `A` and missing `B` are still fast. |


The bad cases are `t3` and `t4`. On the count page, those are exactly the rows with `log_move_B` at least once. The rule you write down before fitting is:

```text
log_move_B at least once  ->  bad
log_move_B zero times     ->  good
```

`t2` and `t5` are deviations too, and they are good. The rule is not "any deviation". It is the deviation you tied to a long throughput.

## What `check_toy_rules.py` prints

The script copies those days onto the encoding table, fits a tree of depth 1 on all five rows, and compares the cases in the bad leaf with `t3` and `t4`.

```text
cutoff days:           10.0
planted throughput:    {'t1': 5.0, 't2': 8.0, 't3': 20.0, 't4': 30.0, 't5': 6.0}
expected bad cases:    ['t3', 't4']
predicted bad cases:   ['t3', 't4']
rule precision:        1.0
rule recall:           1.0
best params:           {'max_depth': 1}
 rule_id predicted_class        conditions  n_cases  n_good  n_bad  share_bad
       0            good log_move_B <= 0.5        3       3      0        0.0
       1             bad  log_move_B > 0.5        2       0      2        1.0
```

`expected bad cases` is the list you wrote. `predicted bad cases` is who landed in the leaf the tree called bad. Both sets are `{t3, t4}`, so precision and recall are `2/2 = 1.0`.

The two rows are that rule, in the same shape as the loan-log rule table. Counts are whole numbers, so `<= 0.5` means zero times and `> 0.5` means at least once.

- Rule 0 is t1, t2, and t5. Three cases, all good, `share_bad` 0.
- Rule 1 is t3 and t4. Two cases, both bad, `share_bad` 1.

`max_depth` is 1 because the script asks for one split and turns the search off. The tree still chooses the feature. It picks `log_move_B`, which is the column you planted. There is no holdout on five rows, so `n_cases` adds up to all five traces.

This only shows that a planted rule can be read back out of the tree. The loan log uses a real throughput, a holdout, and a search over depth and leaf size. Its rules are a separate result.