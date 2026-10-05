# The parallel + decision toy (Step 0 — design only)

This is the second gold-standard toy. The first toy (`docs/toy.md`) is a straight line. This one adds what the teacher asked for: **parallelism** and a **decision (XOR)**.

**Status:** Step 0 design approved. Step 1 scripts are in the repo. Run the three commands below from the project root after `make_toy_parallel.py`.

```bash
uv run python scripts/make_toy_parallel.py
uv run python scripts/align_toy_parallel.py
uv run python scripts/evaluate_toy_alignments.py ^
  --gold data/gold/toy_parallel_alignment_gold.csv ^
  --log data/raw/toy_parallel.xes ^
  --pnml data/raw/toy_parallel.pnml ^
  --plot data/output/toy_parallel_alignment_gold_vs_pred.png ^
  --title "Parallel toy: gold vs predicted"
```

On PowerShell use backticks instead of `^` for line continuation, or paste as one line.

`make_toy_parallel.py` writes PNML + XES with pm4py (same style as the linear toy). SimPN can replace how the *fitting* log is generated later; the hand gold CSV stays the source of truth.

## What you draw

Silent transitions (`tau_*`) fire in the model, never appear in the log, and are **not** features.

```text
                         +--> (pB) --> B --> (pB2) --+
                         |                           |
(source) --> A --> (p1) --+ tau_and_split            +-- tau_and_join --> (p2)
                         |                           |
                         +--> (pC) --> C --> (pC2) --+

(p2) --+--> D --> (p3) --+
       |                 |
       +--> E --> (p3) --+   (XOR: exactly one of D or E)

(p3) --> F --> (sink)
```

**In words:**

1. Always start with **A**.
2. Then **B and C in parallel** (either order in the log is fine: `B` then `C`, or `C` then `B`).
3. Then a **choice**: either **D** or **E**, not both.
4. Always end with **F**.

**Fitting traces (examples):**

- `A, B, C, D, F`
- `A, C, B, D, F` (same as above; B and C swapped)
- `A, B, C, E, F`
- `A, C, B, E, F`

## Cases we plant (for the gold CSV later)


| Case | Trace you write down     | What is wrong with it                                      |
| ---- | ------------------------ | ---------------------------------------------------------- |
| p1   | `A, B, C, D, F`          | Nothing. Parallel order B then C, take XOR branch D.       |
| p2   | `A, C, B, E, F`          | Nothing. Parallel order C then B, take XOR branch E.       |
| p3   | `A, B, D, F`             | **C** is missing (skipped one parallel branch).            |
| p4   | `A, B, B, C, D, F`       | One **extra B** (did B twice).                             |
| p5   | `A, B, C, D`             | **F** is missing (stopped before the end).                 |
| p6   | `A, A, B, C, E, F`       | One **extra A** at the start.                              |


We deliberately avoid “did both D and E” for now. That case has two equally cheap alignments (sync D + log E, or sync E + log D), so a single gold cell for `log_move_D` vs `log_move_E` would be ambiguous. We can add it later with a note that either of two golds is allowed.

## Hand move counts (source of truth for alignment)

Same rules as `docs/toy.md`:

- Sync = both agree → do **not** count.
- Log move = case did it, model did not → count under `log_move_*`.
- Model move = model needed it, case skipped it → count under `model_move_*`.
- `tau_*` never counted.


| case | moves you mark (sketch)              | model A | model B | model C | model D | model E | model F | log A | log B | log C | log D | log E | log F |
| ---- | ------------------------------------ | ------- | ------- | ------- | ------- | ------- | ------- | ----- | ----- | ----- | ----- | ----- | ----- |
| p1   | sync A,B,C,D,F                       | 0       | 0       | 0       | 0       | 0       | 0       | 0     | 0     | 0     | 0     | 0     | 0     |
| p2   | sync A,C,B,E,F                       | 0       | 0       | 0       | 0       | 0       | 0       | 0     | 0     | 0     | 0     | 0     | 0     |
| p3   | sync A,B; model C; sync D,F          | 0       | 0       | 1       | 0       | 0       | 0       | 0     | 0     | 0     | 0     | 0     | 0     |
| p4   | sync A,B; log B; sync C,D,F          | 0       | 0       | 0       | 0       | 0       | 0       | 0     | 1     | 0     | 0     | 0     | 0     |
| p5   | sync A,B,C,D; model F                | 0       | 0       | 0       | 0       | 0       | 1       | 0     | 0     | 0     | 0     | 0     | 0     |
| p6   | sync A; log A; sync B,C,E,F          | 0       | 0       | 0       | 0       | 0       | 0       | 1     | 0     | 0     | 0     | 0     | 0     |


## Why this design

| Piece | Why it is here |
| ----- | ---------------- |
| **AND (B \|\| C)** | Checks that the aligner treats either order as fitting, and that skipping one branch is a **model move**. |
| **XOR (D vs E)** | Checks that either branch alone is fine; both fitting cases use different branches. |
| **Extra / missing labeled activities** | Same gold idea as toy 1, with unambiguous counts. |
| **SimPN later** | Step 1 can *simulate* fitting behaviour from this net; deviant cases can still be written by hand into the XES (like toy 1), so the gold stays under your control. |

## What we do **not** do yet

- Nothing blocking for Rick’s gold lane. Optional extras only if you want more practise.

## Optional: planted rule (practise)

```bash
uv run python scripts/check_toy_parallel_rules.py
```

Cutoff **10**. Only **p4** is slow (25 days). Hand rule: **extra B** (`log_move_B ≥ 1`) → bad.
p3 still *deviates* (missing C) but stays **good** — deviation ≠ slow. Expect P/R **1.0** and a
depth-1 split on `log_move_B` (same *kind* of story as the linear toy).

## SimPN export spike (Step 1b)

Run:

```bash
uv run python scripts/spike_simpn_export.py
```

**Result of the spike:**

| Question | Answer |
| -------- | ------ |
| Can SimPN write an event log? | **Yes.** `EventLogReporter` → CSV (`case_id`, `task`, `resource`, `start_time`, `completion_time`). |
| Parallelism visible in the log? | **Yes.** B and C share the same start time on a case (AND split). |
| XOR visible? | **Yes.** Each case takes D or E, not both. |
| Direct PNML export? | **No usable API.** Keep `make_toy_parallel.py` (pm4py) as the model file for alignments. |
| Path into our pipeline? | CSV → filter A–F → XES (`data/output/simpn_spike_events.xes`). Fitting traces only; deviant cases stay hand-written in the gold XES. |

So: SimPN is useful as a **fitting-log generator**. The **gold net (PNML)** and the **deviant cases** stay under our control, as in Step 1.
