import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CAMPAIGN = Path(__file__).resolve().parents[1]
for p in (CAMPAIGN / "src", ROOT / "level4" / "stage_d" / "src",
          ROOT / "level4" / "src"):
    sys.path.insert(0, str(p))
