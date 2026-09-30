"""Environment for every formal-campaign run (p5y_k5_cell309_p309_r1).

* puts the research campaign's pinned modules (impl/, verify/, code/) on sys.path, READ-ONLY;
* redirects every q309_guard ledger to THIS namespace's ledgers, so no formal run ever writes a research file
  (the research branch/namespace stays unchanged; owner instruction 2026-09-30 "GITHUB / HISTORY");
* keeps the research quarantine guards active (band, quarantined cells, forbidden paths) until a grant exists
  (protocol rev. 2b section 6).  No grant exists in this stage.
"""
from __future__ import annotations

import sys
from pathlib import Path

FNS = Path(__file__).resolve().parents[1]                                     # formal namespace
REPO = FNS.parents[2]
RNS = REPO / "level4" / "closure_proofs" / "p5y_k5_cell309_research_r1"      # research namespace (read-only)
for p in (RNS / "impl", RNS / "verify", RNS / "code", FNS / "code"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import q309_guard as Q  # noqa: E402

Q.EXEC_LEDGER = FNS / "ledger" / "ZERO_TARGET_LEDGER.jsonl"
Q.EXPOSURE_LEDGER = FNS / "ledger" / "EXPOSURE_LEDGER.jsonl"


def log(script: str, purpose: str, *, klass: str, drifts=None, notes: str = "") -> dict:
    return Q.log_execution(script, purpose, klass=klass, drifts=drifts, notes=notes)


def exposure(ref: str, path: str, *, content: str, necessity: str, carried_309_numbers: bool) -> dict:
    return Q.log_exposure("formal-campaign coordinator", ref, path, content=content, necessity=necessity,
                          carried_309_numbers=carried_309_numbers)
