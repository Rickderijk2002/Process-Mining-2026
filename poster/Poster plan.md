# Poster plan, Group 8: Conformance Checking for Process Improvement

Course JM0211 Process Mining. Poster session 12 November, 13:45 to 15:30. Pitch limit: 3 minutes. Deliverable weight: Poster and Pitch is 25 percent of the assignment grade.

Source of truth for all content: `docs/Report/Report-process-Mining.qmd`. Verified numbers: `docs/locked_results.md`. Sources checked for this plan: the qmd and the PDF of the paper (same timestamp, 31 October 14:50; every number I compared is identical), the template `Poster_GroupX.pdf`, the rubric sheet `Rubric_PosterandPitch` and `Rubric_Explanation`, the assignment description, `docs/pipeline.md`, `docs/locked_results.md`, `data/output/tree_rules_cutoff14_pruned_2026-10-06.csv` and `tree_stability_cutoff14_pruned_2026-10-06.csv` (the 389 and 2,704 trace counts and the per-seed scores match the paper).

## 1. Format taken from the template

The template page is the left panel of the PDF; the right panel is instructions "to be removed for printing". Required: upright, at least A2. We use **A2 portrait (420 by 594 mm)**.

Template sections in order, with their share of the page height in the template:

| Order | Section | Template share | Our share |
|---|---|---|---|
| 0 | Header: course, title, group, member names, JADS logo | about 10 percent | about 9 percent |
| 1 | Motivation and Scientific Background | about 19 percent | about 17 percent |
| 2 | Explanation of Conceptual Approach | about 34 percent | about 27 percent |
| 3 | Evaluation Design and Results | about 25 percent | about 36 percent |
| 4 | Limitations and Future Work | about 12 percent | about 9 percent |

Deviation from the template, on purpose: Evaluation gets more space than the template suggests, because it carries all the visual evidence and the honest message of the paper. The template is "reasonably extended" (rubric P2) by two small additions only: a take-away bar at the end of Evaluation, and a one line reference footer. Section titles are kept word for word.

## 2. Rubric rows, criteria and how the poster meets them

### P1 Content (2 points)

"The content of the poster is correct and complete. It matches the content of the short paper."

What satisfies it on our poster:
* Every number on the poster is copied from the qmd or `locked_results.md` (3,093 traces, 54 activities, 108 features, median 14.43 days, 1,501 fast and 1,592 slow, 0.563, 0.970, 0.712, 0.688, 0.680, 389 and 2,704 traces, 16 and 57 percent, seeds 0 to 3, 18 and 21 day tables).
* All four steps of the brief appear: KPI, alignment and encoding, classification tree with grid search, rules with trace subsets.
* The honest result is stated: the tree is barely better than the baseline and is unstable. The poster must not claim more than the paper.

Checklist:
* [ ] Each number is traceable to a table or sentence in the qmd (done in section 6 below).
* [ ] No claim on the poster that is absent from the paper.
* [ ] Both evaluation tracks shown: gold standard and real log.
* [ ] Limitations on the poster equal the limitations in the paper.

### P2 Structure (4 points)

"The poster is structured based on the provided template. The template is reasonably extended in case necessary. The structure is followed during the pitch. The connection between the different parts is clear and logically presented."

What satisfies it:
* The same five blocks in the same order as the template, with the template titles.
* A visible thread: question (Motivation) to pipeline (Approach, numbered 1 to 4) to test (Evaluation: 1 Correctness, 2 Usefulness) to caveats (Limitations). The numbered steps and numbered evaluation tracks make the order easy to follow while pitching.
* The pitch (see `Pitch script.md`) walks the poster top to bottom and names each section while pointing at it.

Checklist:
* [ ] Section titles identical to the template.
* [ ] Reading order is top to bottom, left to right, no ambiguity.
* [ ] Template guiding questions answered: relevant use case, course embedding, input characteristics, parameters, crucial steps, output, data, gold standard, metrics, parameter testing, results, limitations, future work.
* [ ] Pitch follows the same order.

### P3 Timing (4 points)

"The overall time frame of 3 minutes is used adequately (not too short and not exceeded). The different parts of the pitch are allocated a reasonable amount of time considering their importance."

What satisfies it: a script of about 375 words (about 2:45 at a calm speaking pace) with time marks, weighted like the template: Motivation about 35 seconds, Approach about 50, Evaluation about 60, Limitations and close about 35. See the split in section 5.

Checklist:
* [ ] Script rehearsed aloud with a timer by every member, between 2:40 and 3:00.
* [ ] Time marks on the script match the poster blocks.
* [ ] A cut version exists (drop the lifecycle merge sentence and the 18 and 21 day detail) for when a listener interrupts.
* [ ] Every member can deliver it (template instruction).

### P4 Terminology and presentation style (3 points)

"Academic language and terminology are used properly. Presentation style during the pitch is adequate."

What satisfies it: consistent terms taken from the paper: log move, model move, synchronous move, optimal alignment, Petri net, throughput time, KPI, cutoff, hold-out, precision, recall, F1 of the slow class, baseline, pruning (cost-complexity), stratified sample, seed. "Slow" and "fast" are used for the two classes, never "bad" and "good" (the repo notes use good and bad, the paper uses slow and fast; the poster follows the paper). No dashes as punctuation.

Checklist:
* [ ] One term per concept across poster, paper and pitch.
* [ ] "Log move" and "model move" defined once on the poster (the Step 2 example).
* [ ] Pitch delivered facing the audience, pointing at figures, not reading the poster.
* [ ] Plain claims with numbers, no overselling ("proves", "significant" without a test).

### P5 Visualizations (4 points)

"There is effective use of visualizations, i.e., content is not only presented through textual information but supported by appropriate visualizations."

Visuals on the poster, each tied to a message:

| Poster element | Message | Origin |
|---|---|---|
| Fast versus slow bar and four stat tiles (Motivation) | The scale of the problem and a balanced KPI split | New, numbers from qmd and `locked_results.md` |
| Four step pipeline with numbered cards (Approach) | The four steps of the brief | New, redrawn from the paper's mermaid figure `fig-pipeline` |
| Alignment table with colour coded sync, log move, model move (Approach) | What a deviation is, and what the 108 features count | Reused content of paper table `tbl-align`, redrawn |
| Parameter table (Approach) | Which knobs exist | New layout, content from qmd Step 3 |
| Seed stability bar chart, F1 per seed with baseline and rule counts (Evaluation) | Same grid, 2 to 14 rules, F1 around the baseline | New, data from `locked_results.md` seed table |
| Class weight chart at 18 and 21 days with standard deviations (Evaluation) | Balanced weights beat the baseline, uniform fall below | Redrawn from paper `fig-f1` / `tbl-robust`, with poster sized labels |
| Two rule tree diagram (Evaluation) | The only split, 389 versus 2,704 traces | New, data from `tree_rules_cutoff14_pruned_2026-10-06.csv` |

Reuse note: the paper figure `docs/Report/figures/f1_by_cutoff.png` (1300 by 620 px) is copied to `poster/figures/` but is not used as is, because its axis and legend labels would shrink below 14 px at poster width. The same data is redrawn as vector SVG with large labels. The 14 day group of that figure is covered by the seed chart (which also shows the per seed values), so the chart on the poster shows 18 and 21 days only.

Not on the poster, deliberately: the Petri net of the loan process (`data/output/petri_net.svg` is 12,434 pt wide and unreadable at poster size), the throughput histogram (`data/output/throughput_hist.png`, small labels, adds nothing the tiles do not say).

Checklist:
* [ ] Every section has at least one visual; Evaluation has three.
* [ ] Each visual has one clear message and no chart junk.
* [ ] Colours consistent (blue, orange, grey as in the paper figure), colour is never the only carrier of meaning (move types carry text labels).
* [ ] Axes honest, starting at zero.
* [ ] Error bars labelled as standard deviation over four seeds in the pitch (not on the chart, see open items).

### P6 Readability and formatting (3 points)

"All elements on the poster are clearly readable, in particular visualizations. Poster is well-formatted."

Readability rules, checked in section 6:
* Page A2 portrait, 420 by 594 mm; browser pixels at 96 per inch, so 1 px is 0.265 mm.
* Title 44 px (about 33 pt). Section headings 42 px (about 32 pt). Body text 28 px (about 21 pt). Smallest text anywhere (chart labels, footer) 24 px at least (about 18 pt) after scaling; this is the minimum so a reader at 1 to 1.5 m can read it. Footer references are the only 24 px text.
* Dark text (#1b1b1b) on white or very light fills; white on dark maroon or blue only for large bold text.
* About 380 words in total on the poster, maximum two lines per bullet, no paragraph longer than two sentences.
* Equal gutters (10 to 14 px), aligned card edges, one accent colour (the JADS maroon) plus the chart colours.
* PDF exported at the true page size so printing at A2 needs no scaling.

Checklist:
* [ ] Minimum font size 24 px confirmed from the CSS.
* [ ] No text clipped (visual check of the PDF render).
* [ ] No wall of text: longest block is two sentences.
* [ ] Contrast acceptable for all fills (no light grey text).
* [ ] Logo sharp (cropped from the template PDF at 4 times resolution).

### P7 Q&A and discussion (5 points)

"Questions by peers and lecturers can be answered correctly and comprehensively. If necessary, questions are answered during the pitch, i.e., there is flexibility in how it is presented without losing focus."

What satisfies it: the Q&A sheet in `Pitch script.md` (16 questions with short answers taken from the paper), a clear "if interrupted, go to this poster block" rule, and every member knowing the weak points listed in section 7 so nobody is surprised by a critical question. Lecturers will also ask about the implementation after the session (Rubric_Explanation, Technology Statement row), so implementation questions are included.

Checklist:
* [ ] Each member has read the Q&A sheet and the weak points list.
* [ ] Each member can find the answer on the poster (which block) in under 5 seconds.
* [ ] Agreed policy: say "we did not test that" rather than guess (the paper itself says so for alignment uniqueness).
* [ ] One member always at the poster during the session; the others visit other groups (template rule).

## 3. Section by section content outline and word budgets

Total budget about 380 words plus visuals.

| Section | Words | Content | Visuals |
|---|---|---|---|
| Header | 12 | Title, JM0211 Process Mining, group 8 and four names, JADS logo | Logo |
| 1 Motivation and Scientific Background | 75 | Use case: Dutch bank, BPI Challenge 2017, 3,093 denied applications, under a day to about 260 days. Question: which deviations go with slow denials, allow or forbid. Why not flag all: workarounds can link to better performance (Dees et al., 2017). Course fit: other topics check resources or time against text constraints, we check control flow against a Petri net | Four stat tiles, fast versus slow split bar |
| 2 Explanation of Conceptual Approach | 95 | Input (XES log with case id, activity, timestamp per event; PNML net). Output (rules plus trace lists as CSV). Four steps. Parameters: cutoff 14 days, 25 percent hold-out, seed 0, 48 grid combinations (depth 2 to 5, min leaf 5, 10, 20, pruning 0, 0.001, 0.01, 0.1), five fold CV on F1 of the slow class | Pipeline cards, alignment table, parameter table |
| 3 Evaluation Design and Results | 130 | Track 1: two toy logs (5 and 6 traces), hand derived move counts and planted rule, 5 of 5 and 6 of 6 exact, precision and recall 1.0. Track 2: real log, 25 percent hold-out, slow class P, R, F1 against all-slow baseline (0.515, 1.000, 0.680), seeds 0 to 3. Results at 14, 18, 21 days. Take-away | Seed chart, class weight chart, tree diagram, score chips |
| 4 Limitations and Future Work | 60 | Unstable two rule tree; root split in 87 percent of traces, net may be too strict; one cutoff, one dataset, control flow only. Future: regression tree, several optimal alignments, data-aware checking | None (text only, two columns) |
| Footer | 25 | Four references | None |

Template question "How is your topic embedded in the course and related to the topics of the other groups?" is answered by the "Course fit" bullet. It uses only what the paper states (resource and temporal conformance). We do not name other groups, because the paper does not.

## 4. New visuals to make versus reuse

Reuse from the paper (redrawn, same content): pipeline (`fig-pipeline`), alignment table (`tbl-align`), cutoff results (`fig-f1`, `tbl-robust`, `tbl-cut14`).
New: stat tiles and split bar, seed stability chart, tree diagram, parameter table, score chips.
Possible additions if the group wants them (not done, see open items): a small excerpt of the Petri net around `W-Call-after-offers`; a distribution plot of throughput time with the 14 day line.

## 5. Pitch timing split (3 minutes, about 375 words)

| Time | Block | Seconds | Why this long |
|---|---|---|---|
| 0:00 to 0:35 | Motivation | 35 | Hook and question; audience needs context |
| 0:35 to 1:25 | Approach | 50 | Most crucial for understanding, includes the alignment example |
| 1:25 to 2:25 | Evaluation | 60 | The evidence and the honest finding |
| 2:25 to 2:55 | Limitations and future work | 30 | Shows critical reflection |
| 2:55 to 3:00 | Invitation to questions | 5 | Opens the discussion |

The full script with time marks is in `Pitch script.md`.

## 6. Self check of the finished poster (ticked honestly)

Checks were done on the rendered PDF `Poster_Group8_A2_final.pdf` (A2, one page; the file `Poster_Group8.pdf` is an older render that Windows kept locked and must be deleted) and on the HTML source.

P1 Content
* [x] Each number traced to the qmd or `locked_results.md`.
* [x] No claim absent from the paper. One wording check: "Why not flag all deviations? Some are workarounds linked to better performance" paraphrases the assignment description and Dees et al. as cited in the paper.
* [x] Both evaluation tracks shown.
* [x] Limitations equal those in the paper (shortened).

P2 Structure
* [x] Template titles in template order.
* [x] Template guiding questions answered (course embedding, input characteristics, parameters, crucial steps, output, data, gold standard, metrics, results, limitations, future work).
* [ ] Pitch follows the structure: script written, not yet rehearsed by the group.

P3 Timing
* [x] Script length 374 words with time marks.
* [ ] Timed aloud: not done, needs the group.

P4 Terminology and style
* [x] Consistent terms (slow and fast, log move, model move).
* [x] No dashes as punctuation on poster, plan and script.
* [ ] Delivery style: needs rehearsal.

P5 Visualizations
* [x] Visuals in every section except Limitations (text only, by design).
* [x] Axes start at zero; move types carry text labels, not only colour.
* [x] Evaluation has three data visuals.
* [ ] Standard deviation error bars are drawn on the class weight chart but the poster does not say "SD over four seeds" next to it (only in the pitch). Open item.

P6 Readability
* [x] Page size A2 portrait, one page, PDF exported at true size.
* [x] Minimum font 24 px (footer, chart labels at least 26 px in the SVG viewBox which is displayed near 1:1).
* [x] No clipped text in the final render.
* [x] No paragraph longer than two sentences.
* [ ] Print test at A2 (or a 25 percent print on A4) not possible here, the group should do it before 12 November.

P7 Q&A
* [x] Q&A sheet written (16 questions).
* [ ] Group has read it: needs the group.

## 7. Honest assessment: weak or unverified points in the paper

These are the points a critical reader can attack. The poster does not hide them.

1. **The headline result is weak.** The tree has F1 0.712 on seed 0 but the mean over four seeds is 0.688 versus 0.680 for the all-slow baseline. The difference of 0.008 is far inside one standard deviation (0.030). We cannot claim the tree beats the baseline at 14 days.
2. **The seed 0 result is the locked one**, selected before the seeds 1 to 3 were looked at. The other seeds measure split sensitivity, not alternatives. The poster shows all four seeds so the headline is not cherry picked.
3. **The only rule is a modest association.** 57 percent slow in the larger leaf against a base rate of 51.5 percent, and that leaf holds 87 percent of traces. The paper itself suggests the net may be too strict about suspensions. This is an interpretation, not a tested finding.
4. **Alignment uniqueness is untested.** The paper cites Dees et al. that the choice does not matter with many traces, but says "this was not tested here".
5. **Gold standards are small.** Two toy logs (5 and 6 traces); precision and recall 1.0 show the implementation matches the hand derived counts, not that it handles real log complexity. Both planted rules recovered with precision and recall 1.0 is also from the paper only (I did not rerun the scripts).
6. **Class weight handling is slightly inconsistent in documentation.** `locked_results.md` says class weight is not searched at 14 days; the paper adds uniform versus balanced as a sensitivity analysis outside the fixed grid. The poster states the 14 day setting as the fixed grid only. The paper is consistent with this, but a lecturer might ask.
7. **Open author notes remain in the qmd** (HTML comments marked RICK): (a) Stefan owns the pruning decision and the sentences "Unpruned trees produced at least twenty rules, which is too many to interpret" need confirmation, (b) the format of the trace lists must be confirmed with Karolin Winter at the 26 October office hour, (c) run commands wait for the README. These do not appear in the PDF but the claims behind them should be confirmed before the poster is printed.
8. **Appendix heading "Lifecycle merge experiment" appears twice** in the qmd and in the PDF (a copy and paste duplicate). Not a poster problem, but fix it in the paper.
9. **Trace lists include misclassified traces** whereas Dees et al. keep only correctly classified ones. Stated in the paper; a lecturer may ask why.
10. **Single dataset, one denied subset, no comparison method.** There is no published BPIC 2017 study with the same setup to compare with.
11. **Mismatch check qmd versus PDF:** none found in the numbers compared. The PDF was not re-rendered by me; both files carry the same timestamp.

## 8. Open items needing the group's decision

See the final message and the bottom of `Pitch script.md`. In short: confirm the pruning claim (Stefan), whether to add a Petri net excerpt or throughput histogram, whether to add "SD over four seeds" text next to the chart, print size (A2 or larger), and who delivers the pitch first.
