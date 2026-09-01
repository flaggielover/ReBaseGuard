import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P7_SRC = ROOT.parents[0] / "p7_statistical_consequences" / "src"
for p in (ROOT / "src", P7_SRC):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
