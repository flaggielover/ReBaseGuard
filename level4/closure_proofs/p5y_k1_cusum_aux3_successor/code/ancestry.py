"""Import bootstrap and inherited adjudicated facts for the aux3 successor.

Every predecessor is IMPORTED, never copied or edited.

  frozen successor    p5y_k1_cover_ledger_successor
  reviewed c0a1f40    p5y_k1_cover_ledger_implementation
  repair1  4164121    p5y_k1_cover_ledger_repair1
  repair2  7a7df9b    p5y_k1_cover_ledger_repair2
  final    f8e6f75    p5y_k1_final_completion
  cusum    70a2943    p5y_k1_cusum_completion_successor

INHERITED INDEPENDENTLY ADJUDICATED FACTS (not re-derived, not re-opened)

    DRIFT_AWARE_NORM        = SOUND
    REFINE2_SOUND           = YES
    CERTIFICATE_DETERMINISM = PASS
    CELL_325                = CERTIFIED_PASS
    CUSUM_FAR_FIELD         = PASS      binding K1/P5X certificate
    SR_FAR_FIELD            = PASS      binding K1/P5X certificate
    REMAINING_WIDTH_DIAGNOSIS = CONFIRMED
    COST_CAP                = NOT_ESTABLISHED

WHAT THIS SUCCESSOR EXISTS TO FIX

The predecessor's verdict was CUSUM_SUCCESSOR_UNSOUND, applied to its
VALIDATION AND PROVENANCE ARCHITECTURE -- not to Refine2's mathematics and not
to the scientific target:

    REPOSITORY_PROVENANCE = FAIL      no committed immutable manifest to resolve
    PRODUCER_BINDING      = FAIL      records could not be independently rechecked

and, structurally, the predecessor redirected scientific behaviour by assigning
into an imported module (`propagate.refine = <module>`). That is repaired here by
explicit wiring, not by patching. The predecessor namespace is left byte-identical
and its records stand as its own evidence.

WHAT THIS SUCCESSOR ADDS SCIENTIFICALLY

Auxiliary third-derivative evidence (h''', S''', W''') used ONLY as nested
internal support for the EXISTING frozen curvature obligations. No new top-level
work id, no change to the 17,978-obligation universe, no geometry change.
"""
from __future__ import annotations

import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
ROOT = NS.parents[2]
CUSUM_NS = ROOT / "level4/closure_proofs/p5y_k1_cusum_completion_successor"
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
CUSUM_COMMIT = "70a29436d5ab78ed3150303f1e32a210a9845a6c"

PREDECESSOR_NAMESPACES = {
    "frozen_successor": (SPEC_NS, REVIEWED_COMMIT),
    "reviewed_implementation": (IMPL_NS, REVIEWED_COMMIT),
    "repair1": (REPAIR1_NS, REPAIR1_COMMIT),
    "repair2": (REPAIR2_NS, REPAIR2_COMMIT),
    "final_completion": (FINAL_NS, FINAL_COMMIT),
    "cusum_completion_successor": (CUSUM_NS, CUSUM_COMMIT),
}

INHERITED_FACTS = {
    "DRIFT_AWARE_NORM": "SOUND",
    "REFINE2_SOUND": "YES",
    "CERTIFICATE_DETERMINISM": "PASS",
    "CELL_325": "CERTIFIED_PASS",
    "CUSUM_FAR_FIELD": "PASS",
    "SR_FAR_FIELD": "PASS",
    "REMAINING_WIDTH_DIAGNOSIS": "CONFIRMED",
    "COST_CAP": "NOT_ESTABLISHED",
    "source": "independent adjudication of 70a29436",
    "no_uncovered_interval_between_c_D_and_e_far": True,
}

REPAIRED_HERE = {
    "REPOSITORY_PROVENANCE": "FAIL -> committed immutable manifest artifact",
    "PRODUCER_BINDING": "FAIL -> manifest hash + schema id carried by every record",
    "MONKEY_PATCHING": "propagate.refine assignment -> explicit dependency injection",
    "LOADED_MODULE_COVERAGE": "strict=False audit -> fail-closed inside the run",
}

for _p in (str(CUSUM_NS / "code"), str(FINAL_NS / "code"), str(REPAIR2_NS / "code"),
           str(REPAIR1_NS / "code"), str(IMPL_NS / "code"), str(SPEC_NS / "code")):
    if _p not in sys.path:
        sys.path.append(_p)

__all__ = ["NS", "ROOT", "CUSUM_NS", "FINAL_NS", "REPAIR2_NS", "REPAIR1_NS",
           "IMPL_NS", "SPEC_NS", "PROOF_SRC", "P5X", "GATE1", "INHERITED_FACTS",
           "REPAIRED_HERE", "PREDECESSOR_NAMESPACES", "REVIEWED_COMMIT",
           "REPAIR1_COMMIT", "REPAIR2_COMMIT", "FINAL_COMMIT", "CUSUM_COMMIT"]
