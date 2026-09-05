"""Import bootstrap for the final-completion namespace.

Everything validated so far is IMPORTED, never copied or edited:

  frozen successor  level4/closure_proofs/p5y_k1_cover_ledger_successor
  reviewed (c0a1f40) level4/closure_proofs/p5y_k1_cover_ledger_implementation
  repair1  (4164121) level4/closure_proofs/p5y_k1_cover_ledger_repair1
  repair2  (7a7df9b) level4/closure_proofs/p5y_k1_cover_ledger_repair2
"""
from __future__ import annotations

import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
ROOT = NS.parents[2]
REPAIR2_NS = ROOT / "level4/closure_proofs/p5y_k1_cover_ledger_repair2"
REPAIR1_NS = ROOT / "level4/closure_proofs/p5y_k1_cover_ledger_repair1"
IMPL_NS = ROOT / "level4/closure_proofs/p5y_k1_cover_ledger_implementation"
SPEC_NS = ROOT / "level4/closure_proofs/p5y_k1_cover_ledger_successor"
PROOF_SRC = ROOT / "rebaseguard-proof/src"
P5X = ROOT / "level4/closure_proofs/p5x_global_nonlinear_dynamics"
GATE1 = ROOT / "level4/closure_proofs/p5y_micropilot_gate1"
TASK1R = ROOT / "level4/closure_proofs/p5y_k1_task1r_budget_harness"

REVIEWED_COMMIT = "c0a1f40cff6974899cd44ab424591bb6a819c949"
REPAIR1_COMMIT = "41641218363f2c8b2bf14a571eecc193ae271fc2"
REPAIR2_COMMIT = "7a7df9b173e5de535c15037089fabebc687c5e6f"

for _p in (str(REPAIR2_NS / "code"), str(REPAIR1_NS / "code"),
           str(IMPL_NS / "code"), str(SPEC_NS / "code")):
    if _p not in sys.path:
        sys.path.append(_p)

__all__ = ["NS", "ROOT", "REPAIR2_NS", "REPAIR1_NS", "IMPL_NS", "SPEC_NS",
           "PROOF_SRC", "P5X", "GATE1", "TASK1R",
           "REVIEWED_COMMIT", "REPAIR1_COMMIT", "REPAIR2_COMMIT"]
