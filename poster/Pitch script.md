# Pitch script and Q&A sheet, Group 8

Limit: 3 minutes. About 375 words (about 2:45 at a calm pace, leaving room to breathe). Every member must be able to deliver it. Point at the poster block named in brackets. If a listener asks a question, answer it, then return to the next block (the script can be cut at the marked points).

## Pitch (about 375 words)

**0:00 to 0:35, Motivation [top block]**

"Good afternoon, we are group 8. A Dutch bank denied 3,093 loan applications: some within a day, others after about 260 days. The process owner asks which deviations from the normative process go together with slow denials, and whether to allow or forbid them. Deviations are not automatically bad; Dees and colleagues showed that some are workarounds linked to better performance. We implement their deviation analysis step. Other course topics check resources or time against text constraints; we check control flow against a Petri net."

**0:35 to 1:25, Approach [second block]**

"The input is an XES log with case, activity and timestamp per event, plus a Petri net. Four steps. One: throughput time per trace. Two: an optimal alignment per trace. In this example, trace A, A, C against model A, B, C, the extra A is a log move and the missing B a model move. We count both move types for each of the 54 activities, so every trace becomes 108 numbers. Three: a trace is slow above 14 days, close to the median. A decision tree is trained on 75 percent of the traces, tuned by grid search with five fold cross validation. Four: every leaf is a rule, and we list the traces satisfying it."

*Cut point if short on time: skip the parameter sentence.*

**1:25 to 2:25, Evaluation [third block]**

"Two evaluations. First, correctness: two hand built toy logs with derived move counts and a planted rule. All counts matched and the rules were recovered, precision and recall 1.0. Second, usefulness on the real log: a 25 percent hold-out, F1 of the slow class against an all-slow baseline. Seed 0 gives two rules and F1 0.712, but over four seeds the mean is 0.688 against 0.680 for the baseline, and the tree size jumps between 2 and 14 rules. The two rule tree splits on an extra suspension of W-Call-after-offers: 57 percent of those traces are slow, against 16 percent without it. At 18 and 21 days only balanced class weights beat the baseline."

*Cut point: drop the 18 and 21 day sentence.*

**2:25 to 2:55, Limitations and future work [bottom block]**

"Take-away: the pipeline is correct, but the link between deviations and slow denials is weak and unstable. That suspension occurs in 87 percent of traces, so the net may be too strict. Future work: a regression tree on the continuous throughput time, several optimal alignments per trace, and data-aware checking."

**2:55 to 3:00, Close**

"We are happy to take your questions."

The spoken text is 374 words; time it aloud and adjust.

## Rehearsal rules

* Each member delivers it once with a timer. Target between 2:40 and 3:00. Never exceed 3:00.
* Do not read from the poster; use the poster as the cue.
* Speak numbers slowly: 0.712, 0.688, 0.680.
* If the audience asks something early, answer it fully and skip to the next block, using the cut points.

## Q&A sheet

Short answers drawn from the paper and the result files. If a question goes beyond the paper, say "we did not test that" and name what we would do.

1. **Why a cutoff of 14 days?** It is close to the median of 14.43 days, gives 1,501 fast and 1,592 slow traces, and was fixed before any tree was fitted. We tested 18 and 21 days as a sensitivity analysis.

2. **Is F1 0.712 good?** Not by itself. The all-slow baseline has F1 0.680, and the mean over four seeds is 0.688. The tree adds recall but little precision (0.563 against 0.515 base rate).

3. **Why do the seeds give different trees?** The same grid picks different depth, leaf size and pruning per split: two rules for seeds 0 and 3, 11 and 14 rules for seeds 1 and 2. That is why we call the two rule tree unstable. The seeds reuse the same traces, so the standard deviation measures split sensitivity, not independent replication.

4. **What does the main rule mean?** A log move of W-Call-after-offers-suspend means an additional suspension, because the net allows one. Traces without it are slow in 16 percent of cases (389 traces), with it 57 percent (2,704 traces), against a base rate of 51.5 percent. The association is modest.

5. **Is that deviation really a deviation?** It occurs in 87 percent of the traces, so the net may be too strict about suspensions. We say so in the paper; we did not test a repaired net.

6. **Is an optimal alignment unique?** No. The solver returns one of them. Dees et al. argue the choice does not matter with many traces, but we did not test it. Future work: sample several optimal alignments.

7. **How do you know the alignments are correct?** We compared them with hand derived move counts on two toy logs (5 of 5 and 6 of 6 traces exact, precision and recall 1.0). The real log is too long to align by hand.

8. **How did you build the gold standard for the rules?** We planted throughput times so that one deviation separates slow from fast traces, then compared the recovered trace sets with the planted ones. Precision and recall were 1.0 on both toys.

9. **Which cost function and tool?** PM4Py 2.7.23.8: synchronous moves cost 0, log and model moves on visible activities cost 10,000 each, silent moves cost 1 as a tie-breaker.

10. **Why do you count moves instead of using the activity sequence?** The 3,093 traces contain 2,038 distinct sequences, so the sequence is unsuitable as a feature. Move counts describe how a trace departs from the net: 54 activities times two move types is 108 features.

11. **Why a classification tree and not a regression tree?** The brief asks for a classification tree. A regression tree would keep the magnitude of the throughput time, which the cutoff discards. It is our first future work item.

12. **Why precision, recall and F1 of the slow class?** The brief requires precision and recall. We use the slow class as the class of interest and compare with the all-slow baseline, which has precision 0.515, recall 1.0 and F1 0.680.

13. **Why do the trace lists include misclassified traces?** Each rule lists all traces that satisfy its conditions, because the brief asks for the traces compliant with the rule. Dees et al. keep only correctly classified ones. This is a design choice we state as a limitation.

14. **Did merging lifecycle events help?** We merged suspend and resume into a pause feature and schedule, start and complete into an execution feature (108 to 74 features). No F1 changed by more than one standard deviation, and the root split is the same.

15. **What would you tell the process owner?** Honestly: no robust recommendation yet. The one candidate is the additional suspension of the after-offers call, but the association is modest and the net may be too strict. The method is correct; the signal in this log is weak.

16. **How is the code organised and how do I run it?** Python 3.12, three packages that mirror the pipeline (loading and KPI, alignment and encoding, classification and rules). Entry point `src/main.py` with the required `--cutoff` parameter, optional hold-out fraction, seed (default 0), sample size and output paths. Output: encoding table, rule table and rule-to-trace assignments as CSV. (The README is still to be written, see open items.)

## Open items for the group

1. Stefan: confirm the pruning claim in the paper (unpruned trees gave at least twenty rules) and that it can appear in the pitch.
2. Confirm with Karolin that the CSV of rule and case identifiers satisfies "split the log accordingly" (office hour 26 October; was an answer received?).
3. Decide whether to add a Petri net excerpt or the throughput histogram to the poster (there is room only if another block shrinks).
4. Decide whether to print "mean and SD over four seeds" next to the class weight chart.
5. Decide the print size (A2 is the minimum; the PDF scales without distortion to A1).
6. Print a draft at A2 (or A4 at 25 percent) and check readability from 1.5 m.
7. Fix the duplicated "Lifecycle merge experiment" heading in the appendix of the paper.
8. Decide who gives the pitch first and the rotation, and rehearse with a timer.
