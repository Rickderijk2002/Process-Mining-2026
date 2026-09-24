import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import statistics

import matplotlib.pyplot as plt

from data_kpi import DataLoader, ThroughputTimeEnricher, THROUGHPUT_ATTR

LOG = ROOT / "data" / "source" / "BPI2017Denied(3).xes"

log = DataLoader().load_log(LOG)
ThroughputTimeEnricher().enrich(log)
days = [float(trace.attributes[THROUGHPUT_ATTR]) for trace in log]

mean_days = statistics.fmean(days)
median_days = statistics.median(days)

print("applications", len(days))
print("min days", min(days))
print("median days", median_days)
print("max days", max(days))

fig, axes = plt.subplots(1, 2, figsize=(10, 4))

axes[0].hist(days, bins=30)
axes[0].axvline(mean_days, color="C1", linestyle="--", label=f"mean {mean_days:.1f}")
axes[0].axvline(
    median_days, color="C2", linestyle="-", label=f"median {median_days:.1f}"
)
axes[0].set_xlabel("throughput time (days)")
axes[0].set_ylabel("applications")
axes[0].legend()

axes[1].boxplot(days, vert=True)
axes[1].set_ylabel("throughput time (days)")
axes[1].set_xticks([])

fig.tight_layout()
fig.savefig(ROOT / "data" / "output" / "throughput_hist.png")
