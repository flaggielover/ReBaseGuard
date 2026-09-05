"""Import bootstrap for Repair2.

Repair2 imports and reuses the reviewed implementation and Repair1; it copies
and edits neither. Only provenance/evidence binding is overridden.

  frozen successor        level4/closure_proofs/p5y_k1_cover_ledger_successor
  reviewed implementation level4/closure_proofs/p5y_k1_cover_ledger_implementation   (c0a1f40)
  repair1                 level4/closure_proofs/p5y_k1_cover_ledger_repair1          (4164121)
"""
from __future__ import annotations

import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
ROOT = NS.parents[2]
REPAIR1_NS = ROOT / "level4/closure_proofs/p5y_k1_cover_ledger_repair1"
IMPL_NS = ROOT / "level4/closure_proofs/p5y_k1_cover_ledger_implementation"
SPEC_NS = ROOT / "level4/closure_proofs/p5y_k1_cover_ledger_successor"
PROOF_SRC = ROOT / "rebaseguard-proof/src"
P5X = ROOT / "level4/closure_proofs/p5x_global_nonlinear_dynamics"
GATE1 = ROOT / "level4/closure_proofs/p5y_micropilot_gate1"

REVIEWED_COMMIT = "c0a1f40cff6974899cd44ab424591bb6a819c949"
REPAIR1_COMMIT = "41641218363f2c8b2bf14a571eecc193ae271fc2"

for _p in (str(REPAIR1_NS / "code"), str(IMPL_NS / "code"), str(SPEC_NS / "code")):
    if _p not in sys.path:
        sys.path.append(_p)

__all__ = ["NS", "ROOT", "REPAIR1_NS", "IMPL_NS", "SPEC_NS", "PROOF_SRC",
           "P5X", "GATE1", "REVIEWED_COMMIT", "REPAIR1_COMMIT"]
