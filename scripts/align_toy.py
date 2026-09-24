import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from alignment import Aligner, Encoder
from data_kpi import DataLoader

loader = DataLoader()
log = loader.load_log(ROOT / "data" / "raw" / "toy.xes")
net, initial_marking, final_marking = loader.load_petri_net(
    ROOT / "data" / "raw" / "toy.pnml"
)

activities = Encoder.activities_from_model(net)
batch = Aligner.align_log(log, net, initial_marking, final_marking, activities)
print(batch.encodings.to_string(index=False))
