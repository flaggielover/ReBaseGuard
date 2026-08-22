import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
for extra in (ROOT / "level4" / "stage_c" / "src",
              ROOT / "level4" / "src",
              ROOT / "rebaseguard-proof" / "src"):
    if str(extra) not in sys.path:
        sys.path.insert(0, str(extra))
