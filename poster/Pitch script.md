# Pitch script and Q&A sheet, Group 8

Limit: 3 minutes. About 375 words (about 2:45 at a calm pace, leaving room to breathe). Every member must be able to deliver it. Point at the poster block named in brackets. If a listener asks a question, answer it, then return to the next block (the script can be cut at the marked points).

## Pitch (about 365 words)

**0:00 to 0:30, Motivation [top block]**

"Hi, we are group 8. Imagine you apply for a loan and get denied. One applicant hears back within a day. Another waits more than eight months. Same bank, same process. We analysed 3,093 such denied applications from a Dutch bank. Our question: which deviations from the official process go with the slow cases? Then the bank knows what to allow and what to forbid. Deviations are not automatically bad, some are useful workarounds."

**0:30 to 1:15, Approach [second block]**

"We implement the method of Dees and colleagues in four steps. Take this example: the model says A, B, C, but the case did A, A, C. The extra A is a log move, the skipped B is a model move. We count both for each of the 54 activities, so every case becomes 108 numbers. A case over 14 days is slow. A decision tree learns which counts separate slow from fast, and every leaf becomes a rule with a list of traces."

**1:15 to 1:45, Evaluation: is it correct? [third block, left]**

"First, correctness. On two hand-built toy logs, every alignment and both planted rules matched the hand-derived answer exactly. Then the real log, tested on a 25 percent hold-out against a baseline that calls every case slow."

**1:45 to 2:30, What we found [third block, tree]**

"The tree has one rule. The process allows the call after the offers to be paused once. Cases where it was paused an extra time are slow in 57 percent of cases. Cases without it are slow in only 16 percent. Before you trust that: 2,704 of the 3,093 cases have the extra pause, and across four data splits the tree barely beats the baseline, F1 0.688 against 0.680. So this is a lead, not proof."

**2:30 to 3:00, Limitations and future work [bottom block]**

"Why so weak? Not one case is deviation-free, half of all deviations are pauses and resumes that the process model does not describe, and alignments cannot see waiting time. In one sentence: when the follow-up call after an offer is interrupted more than the process allows, denials take longer. Next, we would use a Petri net that allows repeated pauses, so a second pause is no longer counted as a deviation, and time-aware features, such as the days waited after a pause. Thank you, we are happy to take your questions."

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
