import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT / "src", ROOT / "experiments",
          ROOT.parent / "p6r_safe_rebaselining_confirmation" / "src",
          ROOT.parent / "p6_safe_rebaselining" / "src",
          ROOT.parent / "p7_statistical_consequences" / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
