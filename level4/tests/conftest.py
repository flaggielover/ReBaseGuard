"""Make the Level 4 package and the frozen Level 1-3 package importable.

The frozen ``rebaseguard-proof`` tree is added to ``sys.path`` rather than
installed, so running the Level 4 suite cannot mutate any frozen artifact.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for extra in (ROOT / "level4" / "src", ROOT / "rebaseguard-proof" / "src"):
    if str(extra) not in sys.path:
        sys.path.insert(0, str(extra))
