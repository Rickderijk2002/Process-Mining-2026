## Work order

The code already covers the first two pipeline steps. Finish the checks around those steps before the tree, because the cutoff and the rules depend on a throughput distribution and an encoding table you actually trust.

### Already in the repo

`data_kpi/` loads the log and the net and writes `throughput_time` on each case. `alignment/alignment_encoding.py` builds the move-count table. `main.py` runs both and can export the enriched XES. There is no inspection, no saved encoding table, no toy, no tree, and no scores.

### Order of the remaining work

- [x] **Inspect the log, briefly.** You need this for the paper and for the cutoff, not as a separate study of the bank. Record the size (3,093 applications, about 125,000 events, 2016 through early 2017), the three activity families (`A-`, `O-`, `W-`), that every case contains `A-Denied` once, and that there are roughly 2,000 distinct sequences. One histogram of trace length is enough. Skip resources, offer amounts, and a full redraw of the net.

- [x] **Report the KPI.** Run the enricher and describe `throughput_time`: minimum, median, maximum, and a histogram, in days. The group picks the "good" cutoff from that distribution. Lock the number in the notes before anyone fits a tree. The enriched log is an intermediate file. The paper only needs the definition and that distribution.

- [x] **Toy for the alignment script.** A net with a few activities, one silent transition, and a handful of short traces. Write the model-move and log-move counts by hand. Run `alignment_encoding.py` on that toy. Precision and recall against your counts are the alignment gold standard. Do this before the long run, so a counting bug is fixed while the example still fits on a page.

- [ ] **Encoding table for the real log.** Run the same script on a sample, then on all 3,093 cases. Save the dataframe (`case_id`, `throughput_time`, and the move counts). That file is the input to the tree. While doing this, align the log in one call rather than one trace at a time, or the full run will be unnecessarily slow.

- [ ] **Toy for the rules.** You can reuse the alignment toy. Give the short traces a throughput you chose, and write down the rule and the case list yourself. After the tree code exists, run it on this toy and score precision and recall against that list. This checks rule extraction, which the alignment toy does not check.

- [ ] **Tree on the loan log.** Split off a held-out set. Fit a classification tree on the rest, with a hyperparameter search. Read each leaf as a rule and list the matching applications. On the held-out cases, precision and recall compare the predicted class with the class from the cutoff.

- [ ] **Write up the same numbers.** The short paper gets the KPI definition, the encoding, the tree settings, the rules, and both sets of scores. The poster is that story in brief. The README lists the commands that reproduce the scores, in order, and `requirements.txt` lists the libraries.

The paper's data section is step 1 and the KPI paragraph from step 2. The results section is the rules from step 6 and the scores from steps 3, 5, and 6.