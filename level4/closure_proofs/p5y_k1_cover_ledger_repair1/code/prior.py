"""Import bootstrap for the reviewed implementation and the frozen successor.

This repair namespace does NOT copy or edit the reviewed implementation at
c0a1f40. It puts that namespace's `code/` directory on the import path and
imports from it, overriding only the two independently identified defects.

Reviewed implementation : level4/closure_proofs/p5y_k1_cover_ledger_implementation
Frozen successor        : level4/closure_proofs/p5y_k1_cover_ledger_successor
"""
from __future__ import annotations

import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
ROOT = NS.parents[2]
IMPL_NS = ROOT / "level4/closure_proofs/p5y_k1_cover_ledger_implementation"
SPEC_NS = ROOT / "level4/closure_proofs/p5y_k1_cover_ledger_successor"

REVIEWED_COMMIT = "c0a1f40cff6974899cd44ab424591bb6a819c949"

for _p in (str(IMPL_NS / "code"), str(SPEC_NS / "code")):
    if _p not in sys.path:
        sys.path.append(_p)

__all__ = ["NS", "ROOT", "IMPL_NS", "SPEC_NS", "REVIEWED_COMMIT"]
