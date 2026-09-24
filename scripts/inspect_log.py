import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import matplotlib.pyplot as plt
import pm4py
from pathlib import Path

from data_kpi import DataLoader

LOG = ROOT / "data" / "source" / "BPI2017Denied(3).xes"

log = DataLoader().load_log(LOG)
df = pm4py.convert_to_dataframe(log)

case_col = "case:concept:name"
act_col = "concept:name"

print("applications", df[case_col].nunique())
print("events", len(df))
print("from", df["time:timestamp"].min())
print("to", df["time:timestamp"].max())

families = df[act_col].where(df[act_col].str.match(r"^[AOW]-"), other="other").str[0]
print(families.value_counts())
print(df.loc[families == "o", act_col].value_counts())

n_cases = df[case_col].nunique()
summary = df.groupby(act_col)[case_col].nunique().rename("cases").to_frame()
summary["case_pct"] = (summary["cases"] / n_cases * 100).round(1)
summary["family"] = (
    summary.index.to_series()
    .where(
        summary.index.to_series().str.match(r"^[AOW]-"),
        other="other",
    )
    .str[0]
)
summary = summary.reset_index().sort_values(
    ["family", "case_pct", act_col],
    ascending=[True, False, True],
)
print(summary.to_string(index=False))

denied = df.groupby(case_col)[act_col].apply(
    lambda names: int((names == "A-Denied").sum())
)
print("A-Denied once in every case", bool((denied == 1).all()))

print("distinct sequences", df.groupby(case_col)[act_col].agg(tuple).nunique())

lengths = df.groupby(case_col).size()
mean_length = lengths.mean()
median_length = lengths.median()

fig, ax = plt.subplots()
ax.hist(lengths, bins=30)
ax.axvline(mean_length, color="C1", linestyle="--", label=f"mean {mean_length:.1f}")
ax.axvline(
    median_length, color="C2", linestyle="-", label=f"median {median_length:.0f}"
)
ax.set_xlabel("events per application")
ax.set_ylabel("applications")
ax.legend()
fig.savefig(ROOT / "data" / "output" / "trace_length_hist.png")
