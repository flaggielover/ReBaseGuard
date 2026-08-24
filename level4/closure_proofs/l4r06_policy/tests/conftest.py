from __future__ import annotations

import sys
from pathlib import Path

CAMPAIGN = Path(__file__).resolve().parents[1]
ROOT = CAMPAIGN.parents[2]
sys.path.insert(0, str(ROOT / "level4" / "stage_c" / "src"))
sys.path.insert(0, str(ROOT / "level4" / "src"))
sys.path.insert(0, str(CAMPAIGN / "src"))
