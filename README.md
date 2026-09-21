# Process Mining — Conformance Checking for Process Improvement

JADS course JM0211, Process Mining. Group 8's implementation assignment. Repository for the
team's work and for instructor access.

## The assignment

Implement the "Deviation analysis" step from Dees, de Leoni and Mannhardt (2017), *Enhancing
process models to improve business performance*. Given a Petri net (PNML) and an event log
(XES), the artefact must:

1. Compute the throughput time of each trace and add it as a log attribute (the KPI).
2. Generate an alignment for each trace, then encode each trace as model-move and log-move
   counts per activity.
3. Fit a classification tree on the encoded traces, using throughput time as the dependent
   variable, with hyperparameter optimization.
4. Derive classification rules from the tree and split the log accordingly, so each rule maps
   to a subset of compliant traces.

Command-line parameter selection is enough; no UI is required. Evaluate the alignments and the
classification rules against a manually built gold standard, reporting at least precision and
recall.

Full brief: [assignment/description_group8_conformance_checking.pdf](assignment/description_group8_conformance_checking.pdf)

## Team & task division

Four people, one pipeline stage each, so the technical load splits evenly along the steps the
assignment already defines.

| Member | Owns | Short paper section |
|---|---|---|
| **Rick** — Data & KPI | Load the XES log and PNML model; compute per-trace throughput time and add it as a log attribute | KPI definition |
| **Stefan** — Alignment & encoding | Generate optimal alignments per trace; encode each trace as model-move / log-move counts per activity | Alignment methodology |
| **Tycho or Thom** — Classification | Fit a classification tree on the encoded traces against the throughput-time KPI, with hyperparameter optimization | Modeling |
| **Tycho or Thom** — Rules & evaluation | Derive classification rules from the tree, split the log per rule; build the manual gold standard and score precision/recall | Evaluation |

Classification vs rules/evaluation is still open between Tycho and Thom. Shared rather than owned by
one person: the poster (assembled from all four sections), the technology statement, and
integration testing before each deadline. The pipeline is sequential (Stefan needs Rick's output,
classification needs Stefan's, rules need classification), so whoever finishes their stage early
picks up the next bottleneck rather than sitting idle.

## Deliverables and dates

| Item | Due |
|---|---|
| Short paper draft (peer review) | 28 October, 23:59 |
| Peer feedback on partner group's draft | 3 November, 23:59 |
| Final assignment (implementation, poster, short paper, technology statement) | 9 November, 23:59 |
| Poster session | 12 November, 13:45-15:30 |

Implementation, poster and short paper follow the templates on Canvas.

## Dataset

`datasets/` holds the BPI Challenge 2017 (Denied) subset provided with the assignment:

- `BPI2017Denied(3).xes` — the event log
- `BPI2017Denied_petriNet.pnml` — the normative process model
- `Log Description.pdf` — dataset overview
- `M_dL_M@COOPIS17.pdf` — the Dees/de Leoni/Mannhardt paper the assignment implements

Background: https://www.win.tue.nl/bpi/2017/challenge.html. While developing, work against a
sample of the log for speed, then validate on the full dataset.

## Setup

```bash
uv sync
```
