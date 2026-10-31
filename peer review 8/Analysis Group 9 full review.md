# Peer review draft: Group 9 short paper (S1 to S6)

Draft for Rick to review and adjust. Grades are proposals, feedback text is in the workbook
`Rubric_Group9_peer_review_DRAFT_v1.xlsx` (columns I and K of sheet Rubric_ShortPaper).
Our feedback to Group 9 is due 3 November, 23:59. The rubric asks for an on-time, elaborate,
constructive, complete review with improvement directions. S3 can only be partly checked because we
have no access to their code. We do not have the page limit of the short paper template (S6).

Paper: "Assignment Predictive Process Monitoring", Group 9. Combines Francescomarino et al. (2019)
(cluster prefixes, one classifier per cluster) with Padella et al. (2025) (LLM prompt, originally
remaining time), adapted to outcome prediction on BPIC 2011 with four LTL rules. Models: model-based
clustering and DBSCAN with DT/RF, unclustered RF, Qwen2.5 3B in three prompt versions, and JEV.
Own additions: no case attributes, plus a boolean history encoding.

| ID | Max | Proposed grade | Points | Band |
|---|---|---|---|---|
| S1 Motivation | 4 | 7 | 2.8 | Good |
| S2 Conceptual approach | 10 | 7 | 7.0 | Good, low end |
| S3 Implementation | 3 | 9 | 2.7 | Very good, partial check |
| S4 Evaluation | 10 | 8 | 8.0 | Good |
| S5 Limitations, future work | 4 | 8 | 3.2 | Good |
| S6 Report quality | 4 | 6 | 2.4 | Sufficient |
| **Total** | **35** | | **26.1** | about 7.5 out of 10 |

## S1 Motivation and scientific background (7)

**Works:** the gap is stated precisely (Padella only tested remaining time, so the prompt is adapted
to outcome prediction across four labeling strategies). Course embedding and the relation to other
groups (same pipeline, different learner; others changed feature space or did post-hoc explainability).

**Holds it back from 9 to 10:**
- Generic hospital example, not BPIC 2011. The rubric asks for a concrete use case or comprehensive example.
- Prefix, outcome, labeling strategy and LTL rule are used before they are explained.
- The claim that LLMs are accurate and robust in PPM leans on one general citation (Requeima et al., 2024).
- No explicit research question or hypothesis, so the evaluation cannot be tied back to it.
- The two-sentence summary of both papers is repeated at the start of Section 2.

## S2 Conceptual approach (7)

**Works:** two workflows clearly separated, parameters and values listed, output stated, Figure 1 exists.

**Holds it back:**
- Section 2.2 gives parameter values but not their purpose (g, k via BIC, epsilon, minPoints, 0.5 threshold). The rubric asks for purpose.
- Section 2.3 is longer than 2.2 but has a lot to cover (five models, two encodings, three prompt versions, JEV) and names terms without defining them: last-state, sequential and frequency encoding (frequency only appears in 3.2.1). The reader learns the meaning in Section 3.
- Their own additions and the leakage argument (pm4py copies trace-level attributes onto every event, so a length-1 prefix already carries the final diagnosis and treatment) are the most original conceptual part, yet sit under Implementation (3.2.2) and are missing from Figure 1.
- Figure 1 omits JEV and its layout is hard to read.
- LTL rules 1 to 4 (phi 1 to phi 4) are never stated in the text.
- Input details are split across 2.1 and 3.1.

## S3 Implementation (9, partial check)

**Works:** Python version, uv and pyproject, package table with versions, module and notebook structure, seeds, temperature 0, 32,768 context with a server check, token limit, timeout, retries, fallback label (115 of 12,084 answers), split and prefix counts, diagonal covariance choice with reason, prompt in Appendix A. Numbers are internally consistent (914 + 229 = 1,143 cases; 1,007 prefixes x 3 versions x 4 rules = 12,084).

**Missing:** notebook run order, data location, runtime, hardware behind Ollama, note that temperature 0 on a remote server is not guaranteed identical, JEV as hosted API (key, cost, availability of the pinned version), typesafe-sdk 0.7.4 versus model jev-1.13.0, typo "removed form". Package versions could not be checked against their pyproject, so "matches the actual implementation" is unverified.

## S4 Evaluation design and results (8)

**Works:**
- Data and ground truth: BPIC 2011, 1,143 cases, chronological 80/20 split, label set on the completed case and shared by all prefixes, class distribution (47, 38, 61, 56 percent deviant) checked against the original paper.
- Metrics: F1 of the deviant class plus accuracy, overall and per prefix length. Tables 2 and 3 and Figures 2 and 3 are clear.
- Discussion: the LLM's higher F1 on rule 1 comes from over-predicting deviant (accuracy below the majority share). The attribute ablation shows how much of the score may rest on information not available at prediction time.
- I checked the numbers quoted in the text against Tables 2 and 3 and the majority shares (0.53, 0.62, 0.61, 0.56). They match.

**Holds it back:**
- No majority-class baseline row in the tables.
- The reproduction is claimed but never compared to the numbers or curves of Francescomarino et al.
- Selected k per model, DBSCAN cluster count, noise share and cluster sizes are not reported. Defaults, no tuning, no justification.
- 1,007 test prefixes come from 229 cases, so they are not independent. No confidence intervals, one run.
- Failure analysis is thin: 115 unparsable answers not split by rule or version, JEV on rule 2 (almost all normal) noted but not explained, no confusion matrices or prediction rates.
- "Deciding activities occur after the prefix" is a plausible but untested explanation for the LLM result.
- Two small text inaccuracies: the LLM F1 range 0.500 to 0.579 on rule 1 is called higher than the classifiers, but 0.500 is below DBSCAN + DT (0.531). The unclustered RF is called best or near-best on F1, which does not hold on rule 1 (0.473 vs 0.531).
- One small LLM, one prompt, no comparison with the results of Padella et al. (2025).

## S5 Limitations and future work (8)

**Works:** limitations come from the design and results, not generic: no minimum class probability (so failure rate and earliness are not measured), one log, one split, one run, no significance tests, missing timestamps on case attributes, one small LLM, fixed examples, no LLM probabilities. Future work (token probabilities, cluster-based example selection) is linked to those limitations.

**Missing:** order loss of the history encoding (matters for rules 2 and 3), non-independent prefixes, no tuning, JEV as a black box, reproducibility on remote servers. Future work stays close to the prompt: other logs, larger LLMs, order-aware encodings, intake-only case attributes and case-level evaluation are absent. The claim that the original paper also suffers the leakage is a hypothesis that should be verified.

## S6 Report quality, structure and appearance (6)

**Works:** clear academic language, logical structure, clean tables, technology statement included.

**Holds it back:**
- Only three references. LLM robustness, LTL labelling, BPIC 2011, DBSCAN, Gaussian mixtures with BIC, Qwen2.5, JEV and related PPM work are unreferenced. The rubric asks for statements supported by literature. Requeima et al. has no venue.
- The only figure in the main text is Figure 1. The results figures sit in appendices B and C, are very small, use inconsistent axes (Figure 2 ticks at 2.5, 5.0 although prefixes are 1, 6, 11, 16, 21; Figure 3 ticks at 5 to 20), and use code names (mbased_dt) where the tables say M-based + DT. No visual for the LLM and JEV results.
- Weighting: Section 2 is short, Sections 3 and the discussion are long, page 6 is half empty.
- Main text is 6 pages, then references and appendices A to D (10 pages plus title page). Check against the page limit, which we do not have.
- Small points: "removed form all cases", a capital W mid-sentence in the technology statement, key terms undefined in the introduction, dense paragraphs in 3.2.2 and 3.3.

## For Rick to decide

1. Grades. S6 at 6 is the most debatable (page limit unknown). S4 at 8 could also be 7 if you weigh the missing reproduction comparison heavily.
2. Tone and length of the workbook text before it goes to the team, who then review and extend it via GitHub.
3. Whether to hand over the whole folder or only the filled workbook.
