"""Static quarantine scan of THIS namespace with the research campaign's pinned scanner (q309_guard.scan), rooted here.
A planted negative control (tests/planted_control_p309.py) must fire every finding kind.  Exit 0 iff PASS."""
import json
import sys
from pathlib import Path

FNS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FNS.parent / "p5y_k5_cell309_research_r1" / "code"))
import q309_guard as Q  # noqa: E402

if __name__ == "__main__":
    Q.NS = FNS
    r = Q.scan(FNS)
    print(json.dumps(r, indent=1))
    sys.exit(0 if r["verdict"] == "PASS" else 1)
