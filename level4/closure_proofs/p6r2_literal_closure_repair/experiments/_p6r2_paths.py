"""Import paths.  P6R2 consumes frozen P6R/P6 evidence READ-ONLY."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P6R = ROOT.parent / "p6r_safe_rebaselining_confirmation"
P6 = ROOT.parent / "p6_safe_rebaselining"
P7 = ROOT.parent / "p7_statistical_consequences"
RESULTS = ROOT / "results"
PRECOMMIT = ROOT / "precommit"

for _p in (ROOT / "src", P6R / "src", P6 / "src", P7 / "src"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
