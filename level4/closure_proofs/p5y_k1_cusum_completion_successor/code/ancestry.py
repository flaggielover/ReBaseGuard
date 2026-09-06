"""Import bootstrap and inherited adjudicated facts for the CUSUM successor.

Every predecessor is IMPORTED, never copied or edited.

  frozen successor    p5y_k1_cover_ledger_successor
  reviewed c0a1f40    p5y_k1_cover_ledger_implementation
  repair1  4164121    p5y_k1_cover_ledger_repair1
  repair2  7a7df9b    p5y_k1_cover_ledger_repair2
  final    f8e6f75    p5y_k1_final_completion

INHERITED INDEPENDENTLY ADJUDICATED FACTS (not re-derived here)

    DRIFT_AWARE_NORM  = SOUND
    CELL_325          = CERTIFIED_PASS
    CUSUM_FAR_FIELD   = PASS      binding K1/P5X certificate
    SR_FAR_FIELD      = PASS      binding K1/P5X certificate

The previous namespace's far-field "uncovered interval between c_D and e_far"
reading was rejected by independent adjudication: there is NO uncovered
interval, and the authoritative binding certificate already gives PASS for both
detectors. This successor inherits that PASS and does not re-derive or contradict
it. `far_field_inherited.py` records it; no far-field logic is changed here.
"""
from __future__ import annotations

import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
ROOT = NS.parents[2]
FINAL_NS = ROOT / "level4/closure_proofs/p5y_k1_final_completion"
REPAIR2_NS = ROOT / "level4/closure_proofs/p5y_k1_cover_ledger_repair2"
REPAIR1_NS = ROOT / "level4/closure_proofs/p5y_k1_cover_ledger_repair1"
IMPL_NS = ROOT / "level4/closure_proofs/p5y_k1_cover_ledger_implementation"
SPEC_NS = ROOT / "level4/closure_proofs/p5y_k1_cover_ledger_successor"
PROOF_SRC = ROOT / "rebaseguard-proof/src"
P5X = ROOT / "level4/closure_proofs/p5x_global_nonlinear_dynamics"
GATE1 = ROOT / "level4/closure_proofs/p5y_micropilot_gate1"

REVIEWED_COMMIT = "c0a1f40cff6974899cd44ab424591bb6a819c949"
REPAIR1_COMMIT = "41641218363f2c8b2bf14a571eecc193ae271fc2"
REPAIR2_COMMIT = "7a7df9b173e5de535c15037089fabebc687c5e6f"
FINAL_COMMIT = "f8e6f7583e798813c7f7e0dc8b952488c2a06a7e"

INHERITED_FACTS = {
    "DRIFT_AWARE_NORM": "SOUND",
    "CELL_325": "CERTIFIED_PASS",
    "CUSUM_FAR_FIELD": "PASS",
    "SR_FAR_FIELD": "PASS",
    "source": "independent adjudication of f8e6f758",
    "no_uncovered_interval_between_c_D_and_e_far": True,
}

for _p in (str(FINAL_NS / "code"), str(REPAIR2_NS / "code"),
           str(REPAIR1_NS / "code"), str(IMPL_NS / "code"),
           str(SPEC_NS / "code")):
    if _p not in sys.path:
        sys.path.append(_p)

__all__ = ["NS", "ROOT", "FINAL_NS", "REPAIR2_NS", "REPAIR1_NS", "IMPL_NS",
           "SPEC_NS", "PROOF_SRC", "P5X", "GATE1", "INHERITED_FACTS",
           "REVIEWED_COMMIT", "REPAIR1_COMMIT", "REPAIR2_COMMIT", "FINAL_COMMIT"]
