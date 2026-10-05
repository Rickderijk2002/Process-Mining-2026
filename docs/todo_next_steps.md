# Process Mining to-do (cutoff 14, classification)

## What the teacher said

* Gold standard: a toy is fine, but make a second toy with parallelism and decision points, ideally simulated with SimPN.
* Add pruning, because 20 rules is a lot.
* Compare multiple cutoffs.
* Core part and evaluation are the minimum needed for peer review (28 Oct).

## Before 28 Oct (draft for peer review)

Pruning will probably change the locked result (20 rules, precision 0.62, recall 0.74), so settle it before investing more in interpreting the current rules.

* \[Stefan] Add pruning (`ccp\_alpha`) to the grid in `model.py`, on a git branch.
* \[Stefan] Decide the grid once (depth, leaf size, `ccp\_alpha`, maybe class weights) before looking at scores.
* \[Stefan] Refit at cutoff 14 and re-lock the result (number of rules, scores, files).
* \[Stefan] Update `locked\_results` and `derived\_rulesets`, since the old rule stories belong to the old 20 rules. 
* \[Stefan] Rerun the stability check on the new grid.
* \[Tycho] Compare multiple cutoffs (14, 21, maybe 10 and 28), each against its own all-bad baseline.
* \[Rick] Gold standard script for the alignments: toy counts in a CSV, precision and recall computed from it. **Done** for the linear toy (`data/gold/toy_alignment_gold.csv`, `scripts/evaluate_toy_alignments.py`). Second toy design in progress: `docs/toy_parallel.md` (Step 0).
* \[Tycho] Agree who owns evaluation (me or Thom).
* \[ ] Find the technology statement requirements on Canvas (skipping it fails the assignment).
* \[Tycho] Draft my paper sections (classification, evaluation).
* \[Rick] Second toy with parallelism and decision points, simulated (SimPN). First check that it can export PNML and XES.
* \[Tycho] Read BPI 2017 papers: cutoffs, results, temporal deviations. Compare with our result.
* \[All] Read the paper on interpreting rules (the teacher will send it) and use it.



## Deadlines

|Date|What|
|-|-|
|25 Oct, 15:00|Questions for the 26 Oct office hour|
|28 Oct, 23:59|Short paper draft|
|3 Nov, 23:59|Peer feedback|
|9 Nov, 23:59|Final delivery|
|12 Nov|Poster session|



