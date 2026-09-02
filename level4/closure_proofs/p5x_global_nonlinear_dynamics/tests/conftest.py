import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
for extra in (NS / "scripts", NS / "feasibility"):
    sys.path.insert(0, str(extra))
