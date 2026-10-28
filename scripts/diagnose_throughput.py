"""Diagnose why alignment deviations explain throughput time so little.

Reads the saved alignment encoding and the Denied log, and reports:
  * how many traces fit the net and how the deviations are distributed,
  * where the elapsed time goes (time after each event until the next one),
  * the ROC AUC of several models for the slow class (5-fold CV), so that the
    ceiling of the 108 deviation features can be compared with simple baselines.
Writes data/output/diagnostics_*.csv and docs/Report/figures/why_weak.png.

Usage (from the repo root):
    uv run python scripts/diagnose_throughput.py
"""

from __future__ import annotations

import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import pm4py  # noqa: E402
from scipy.stats import spearmanr  # noqa: E402
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.model_selection import StratifiedKFold, cross_val_score  # noqa: E402
from sklearn.tree import DecisionTreeClassifier  # noqa: E402

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "output"
FIG = ROOT / "docs" / "Report" / "figures" / "why_weak.png"

enc = pd.read_csv(OUT / "alignment_encodings.csv").set_index("case_id")
feats = [c for c in enc.columns if c.startswith(("model_move_", "log_move_"))]
tp = enc["throughput_time"]

log = pm4py.read_xes(
    str(ROOT / "data" / "source" / "BPI2017Denied(3).xes"), show_progress_bar=False
).sort_values(["case:concept:name", "time:timestamp"])
grp = log.groupby("case:concept:name")
n_events = grp.size().reindex(enc.index)
log["gap"] = (grp["time:timestamp"].shift(-1) - log["time:timestamp"]).dt.total_seconds() / 86400
log["next"] = grp["concept:name"].shift(-1)

# 1. fit and distribution of deviations
total = enc[feats].sum(axis=1)
print(f"fitting traces: {(total == 0).sum()} of {len(enc)}")
print(f"deviations per trace: mean {total.mean():.1f}, median {total.median():.0f}, min {total.min()}")
lifecycle = [c for c in feats if c.endswith(("suspend", "resume", "ate-abort"))]
print(f"share of deviations on suspend/resume/abort: {enc[lifecycle].sum().sum() / enc[feats].sum().sum():.3f}")
print(f"features never non-zero: {sum(enc[c].max() == 0 for c in feats)} of {len(feats)}")

# 2. where the time goes
suspend_gap = log[log["concept:name"].str.endswith("suspend")].groupby("case:concept:name")["gap"].sum().reindex(enc.index).fillna(0)
call_gap = log[log["concept:name"] == "W-Call-after-offers-suspend"].groupby("case:concept:name")["gap"].sum().reindex(enc.index).fillna(0)
print(f"time after a suspend event / throughput: median {(suspend_gap / tp).median():.2f}")
print(f"time after Call-after-offers-suspend / throughput: median {(call_gap / tp).median():.2f}, rho {spearmanr(call_gap, tp)[0]:.2f}")
log["kind"] = np.where(log["concept:name"] == "W-Call-after-offers-suspend", "Call after offers: suspended",
              np.where(log["concept:name"].str.endswith("suspend"), "Other work item suspended", "Other"))
share = log.groupby("kind")["gap"].sum() / log["gap"].sum()
print(share.round(3))
mx = log.groupby("case:concept:name")["gap"].max().reindex(enc.index)
print(f"largest single gap / throughput: median {(mx / tp).median():.2f}")

# 3. predictability ceiling
rows = []
for cutoff in (14, 18, 21):
    y = (tp > cutoff).astype(int)
    cv = StratifiedKFold(5, shuffle=True, random_state=0)
    models = {
        "Tree, depth 3 (deviations)": (DecisionTreeClassifier(max_depth=3, min_samples_leaf=10, random_state=0), enc[feats].values),
        "Random forest (deviations)": (RandomForestClassifier(300, min_samples_leaf=5, random_state=0, n_jobs=-1), enc[feats].values),
        "Gradient boosting (deviations)": (GradientBoostingClassifier(random_state=0), enc[feats].values),
        "Total deviations only": (LogisticRegression(), total.values.reshape(-1, 1)),
        "Number of events only": (LogisticRegression(), n_events.values.reshape(-1, 1)),
    }
    for name, (model, X) in models.items():
        auc = cross_val_score(model, X, y, cv=cv, scoring="roc_auc").mean()
        rows.append({"cutoff": cutoff, "model": name, "roc_auc": round(auc, 3)})
auc = pd.DataFrame(rows)
auc.to_csv(OUT / "diagnostics_auc.csv", index=False)
print(auc.pivot(index="model", columns="cutoff", values="roc_auc"))
print("spearman with throughput: events", round(spearmanr(n_events, tp)[0], 2), "total deviations", round(spearmanr(total, tp)[0], 2))

# 4. figure
fig, (a, b) = plt.subplots(1, 2, figsize=(7.2, 2.5), gridspec_kw={"width_ratios": [1, 1.3]})
labels = ["Call after offers\nsuspended", "Other work item\nsuspended", "Other"]
vals = [share["Call after offers: suspended"], share["Other work item suspended"], share["Other"]]
a.barh(labels[::-1], np.array(vals[::-1]) * 100, color=["#a9a8a3", "#2a78d6", "#eb6834"])
for i, v in enumerate(vals[::-1]):
    a.text(v * 100 + 1, i, f"{v*100:.0f}%", va="center", fontsize=8)
a.set_xlim(0, 100); a.set_xlabel("Share of elapsed time in the log (%)", fontsize=8)
a.set_title("(a) Time after each event", fontsize=9)
d14 = auc[auc.cutoff == 14].set_index("model")["roc_auc"]
order = ["Number of events only", "Random forest (deviations)", "Tree, depth 3 (deviations)", "Total deviations only"]
b.barh([o.replace(" (deviations)", "\n(deviations)") for o in order[::-1]], [d14[o] for o in order[::-1]], color="#2a78d6")
for i, o in enumerate(order[::-1]):
    b.text(d14[o] + 0.01, i, f"{d14[o]:.2f}", va="center", fontsize=8)
b.axvline(0.5, color="#52514e", lw=0.8, ls="--"); b.set_xlim(0.4, 0.85)
b.set_xlabel("ROC AUC, slow class, cutoff 14 days (5-fold CV)", fontsize=8)
b.set_title("(b) Predictive information", fontsize=9)
for ax in (a, b):
    ax.tick_params(labelsize=7.5)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
fig.tight_layout()
fig.savefig(FIG, dpi=200)
print("saved", FIG)
