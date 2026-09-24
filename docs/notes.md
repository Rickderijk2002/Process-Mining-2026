## 24-09 | Understanding what the assignment asks and means with 'toy model'

We implement the deviation-analysis step from Dees, de Leoni and Mannhardt (2017). The program takes the BPI 2017 Denied event log and its Petri net, and returns rules that link deviations to throughput time, plus the traces that match each rule. A short paper and a poster explain that pipeline and its scores.

### Do this, in order

1. **Throughput time.** For each application, store the number of days between its first and last timestamp as `throughput_time`. This is the KPI. Lower is better.
2. **Align and encode.** For each application, compute an optimal alignment with the Petri net. Turn it into counts: per activity, how many model moves (the net expected the step and the log skipped it) and how many log moves (the log did the step and the net does not allow it). Synchronous moves are not counted. Silent `Inv` transitions are not activities.
3. **Tree.** Choose a cutoff so each case is "good" or "bad" from its throughput time. Fit a classification tree that predicts that class from the move counts, and tune it with a hyperparameter search. Keep some cases out of the fitting.
4. **Rules.** Each leaf is a rule. For each rule, list the applications whose move counts match it. That list, together with the rules, is the result on the real log.

### Why a toy log exists

The loan traces are too long to replay by hand, so you cannot check 3,093 alignments yourself. You build a tiny log and a tiny net, write the correct move counts and the correct rule yourself, and run the same scripts on it. If the scripts return that answer key, the scripts implement the definitions correctly. You then run those same scripts on the loan log.

The toy and the loan log are the same kind of input: an event log plus a Petri net, passed through the same scripts. They are not the same process, and the script will not find the same deviations in both.

You write the scripts so they work on any log and any net. You first run them on a tiny log you invented, where you already know the alignment counts and the rule. If the script returns those, the script is doing the job you defined. You then run that same script on the loan log. The alignments there are right because a log move is still a log move, not because the loan process looks like the toy.

The rules that come out of the loan log are new. They describe the loan applications. The toy only showed that, when you plant a rule, the tree and the trace lists can recover it.

### What to report

- Precision and recall of the alignments against the hand-written toy alignments.
- Precision and recall of the recovered rule against the traces you listed for that toy rule.
- On the real log, precision and recall of the tree's predicted class against the class given by the throughput cutoff, on the cases the tree was not fitted on.

### Misc
The loan file is about 3,100 denied applications, on the order of 40 events each, with a throughput time of about two weeks from the first timestamp to the last. Every case reaches A-Denied. The Petri net in data/source/ is the normative model those traces are compared with.