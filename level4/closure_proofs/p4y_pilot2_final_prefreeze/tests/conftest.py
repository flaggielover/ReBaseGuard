import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P1 = ROOT.parent / "p4y_precision_governance_pilot"
for p in (ROOT / "src", P1 / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
