"""Import bootstrap and inherited adjudicated facts for the Aux4 full-cover run.

Every predecessor is IMPORTED, never copied or edited.

  frozen successor    p5y_k1_cover_ledger_successor
  reviewed c0a1f40    p5y_k1_cover_ledger_implementation
  repair1  4164121    p5y_k1_cover_ledger_repair1
  repair2  7a7df9b    p5y_k1_cover_ledger_repair2
  final    f8e6f75    p5y_k1_final_completion
  cusum    70a2943    p5y_k1_cusum_completion_successor
  aux3     4191beb    p5y_k1_cusum_aux3_successor

WHY THIS MODULE IS CALLED `ancestry4` AND NOT `ancestry`
--------------------------------------------------------
Aux3 named its bootstrap `ancestry`, and so did the CUSUM completion successor.
Both directories end up on `sys.path`, so `import ancestry` resolves to whichever
came first -- and Aux3's own certifying run tripped over exactly that: its lazy
`import successor_producer` picked up Aux3's `ancestry`, could not find the files
it expected, raised, and was swallowed by a bare `except Exception`. The result
was a record whose `rejected_identities` silently depended on module-cache state,
inside the scientific hash. A unique module name removes the collision at the
root; Aux4 additionally performs NO lazy imports on the certifying path.

INHERITED, ADJUDICATED, NOT RE-OPENED

    AUXILIARY_DERIVATIVE_SOUND = YES      the h''' / S''' mathematics
    AUX3_BLOCK_REPLAY          = 32/32    cells 318-325 under Aux3 mathematics
    REPOSITORY_PROVENANCE      = PASS     (Aux3)
    EXPLICIT_REFINEMENT_WIRING = PASS     (Aux3)
    FAR_FIELD                  = PASS     binding K1/P5X certificate
    COST_CAP                   = NOT_ESTABLISHED

REPAIRED HERE (all adjudicated FAIL against Aux3)

    PRODUCER_MANIFEST           exact path-based TCB, no basename exemptions
    STRICT_PRODUCER_ENFORCEMENT the final gate runs after the scientific hash
    RUNTIME_BINDING             BLAS kernel, backend library bytes, build identity
    CERTIFICATE_DETERMINISM     no swallowed lazy import can move the hash
    AUXILIARY_GOVERNANCE        candidate_suprema / order / hermite_weight bound

RERUN, NOT INHERITED

    CUSUM_COVER_INHERITANCE = REQUIRES_FULL_326_RERUN. No predecessor cell record
    is composed into this namespace's ledger; all 326 cells are recertified under
    the Aux4 producer identity.
"""
from __future__ import annotations

import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
ROOT = NS.parents[2]
AUX3_NS = ROOT / "level4/closure_proofs/p5y_k1_cusum_aux3_successor"
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
AUX3_COMMIT = "4191beb8fd6ed5bffac87fe47a7284e8fa0b0de0"

PREDECESSOR_NAMESPACES = {
    "frozen_successor": (SPEC_NS, REVIEWED_COMMIT),
    "reviewed_implementation": (IMPL_NS, REVIEWED_COMMIT),
    "repair1": (REPAIR1_NS, REPAIR1_COMMIT),
    "repair2": (REPAIR2_NS, REPAIR2_COMMIT),
    "final_completion": (FINAL_NS, FINAL_COMMIT),
    "cusum_completion_successor": (CUSUM_NS, CUSUM_COMMIT),
    "aux3_successor": (AUX3_NS, AUX3_COMMIT),
}

INHERITED_FACTS = {
    "AUXILIARY_DERIVATIVE_SOUND": "YES",
    "AUX3_BLOCK_REPLAY": "32_32_PASS",
    "REPOSITORY_PROVENANCE": "PASS",
    "EXPLICIT_REFINEMENT_WIRING": "PASS",
    "CUSUM_FAR_FIELD": "PASS",
    "SR_FAR_FIELD": "PASS",
    "COST_CAP": "NOT_ESTABLISHED",
    "source": "independent adjudication of 4191beb8",
    "no_uncovered_interval_between_c_D_and_e_far": True,
}

REPAIRED_HERE = {
    "PRODUCER_MANIFEST": "FAIL -> exact path TCB; no basename exemption; "
                         "successor_producer.py removed from the execution path",
    "STRICT_PRODUCER_ENFORCEMENT": "FAIL -> final gate after certificate assembly "
                                   "AND after the scientific hash",
    "RUNTIME_BINDING": "FAIL -> OpenBLAS runtime kernel, backend library bytes, "
                       "CPython build, precision and thread contract all bound",
    "CERTIFICATE_DETERMINISM": "FAIL -> no lazy imports, no swallowed exceptions "
                               "on the certifying path",
    "AUXILIARY_GOVERNANCE": "FAIL -> schema-driven hash binds candidate_suprema, "
                            "auxiliary order and hermite_weight",
}

# Aux3 name-collides with the CUSUM successor on `ancestry`; put Aux3 first so a
# transitive `import ancestry` from Aux3's science modules resolves to Aux3's.
for _p in (str(AUX3_NS / "code"), str(CUSUM_NS / "code"), str(FINAL_NS / "code"),
           str(REPAIR2_NS / "code"), str(REPAIR1_NS / "code"),
           str(IMPL_NS / "code"), str(SPEC_NS / "code")):
    if _p not in sys.path:
        sys.path.append(_p)

__all__ = ["NS", "ROOT", "AUX3_NS", "CUSUM_NS", "FINAL_NS", "REPAIR2_NS",
           "REPAIR1_NS", "IMPL_NS", "SPEC_NS", "PROOF_SRC", "P5X", "GATE1",
           "INHERITED_FACTS", "REPAIRED_HERE", "PREDECESSOR_NAMESPACES",
           "REVIEWED_COMMIT", "REPAIR1_COMMIT", "REPAIR2_COMMIT", "FINAL_COMMIT",
           "CUSUM_COMMIT", "AUX3_COMMIT"]
