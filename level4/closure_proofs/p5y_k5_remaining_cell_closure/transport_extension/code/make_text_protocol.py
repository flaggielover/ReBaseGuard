"""Build config/TEXT_PROTOCOL.json (the T-EXT freeze object): pins of every bound source/data file, the frozen hull
family, gates, fixture and mutant lists. Deterministic; refuses to overwrite an existing protocol.

    python3 -B code/make_text_protocol.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
REPO = HERE.parents[5]
CP = "level4/closure_proofs/"
OWN = ["TEXT_SPEC.md", "code/text_transport.py", "code/text_consume.py", "code/text_crosscheck.py",
       "code/text_fixtures.py", "code/text_mutants.py", "code/qualify_text.py", "code/make_text_protocol.py"]
FROZEN_CODE = [
    "p5x_global_nonlinear_dynamics/certified_method_repair_ra/ra_certifier.py",
    "p5x_global_nonlinear_dynamics/compute_optimization_r2/fast_range.py",
    "p5y_k1_cover_ledger_implementation/code/cusum_layer1.py", "p5y_k1_cover_ledger_implementation/code/cusum_layer2.py",
    "p5y_k1_cover_ledger_implementation/code/intervals.py", "p5y_k1_cover_ledger_implementation/code/opnorms.py",
    "p5y_k1_cover_ledger_implementation/code/spec.py", "p5y_k1_cover_ledger_repair1/code/prior.py",
    "p5y_k1_cover_ledger_repair1/code/repair_layer2.py", "p5y_k1_cusum_aux3_successor/code/ancestry.py",
    "p5y_k1_cusum_aux4_fullcover/code/ancestry4.py", "p5y_k1_cusum_aux5_successor/code/ancestry5.py",
    "p5y_k1_cusum_completion_successor/code/order2.py", "p5y_k1_final_completion/code/base.py",
    "p5y_k1_final_completion/code/sharp_certifier.py", "p5y_k1_final_completion/code/sharp_norms.py",
    "p5y_k5_cusum_first_real_probe_protocol/code/probe_rules.py", "p5y_k5_cusum_order3_r2_repair/code/graded_dag.py",
    "p5y_k5_cusum_order3_r2_repair/code/sigma_systems.py", "p5y_k5_cusum_order3_r3_infrastructure/code/first_cell.py",
    "p5y_k5_cusum_order3_r3_infrastructure/code/hermite6_ext.py",
    "p5y_k5_cusum_order3_r3_infrastructure/code/r5_majorant.py",
    "p5y_k5_cusum_order3_r3_infrastructure/code/resolvent_certificate.py",
    "p5y_k5_cusum_order3_r4_tightening/code/constants_r4.py", "p5y_k5_cusum_order3_r4_tightening/code/first_cell_r4.py",
    "p5y_k5_cusum_order3_r4_tightening/code/local_r5.py",
    "p5y_k5_cusum_order3_r4_tightening/code/odd_block_certificate.py",
    "p5y_k5_cusum_order3_real_producer/code/manufactured_chain.py",
    "p5y_k5_cusum_order3_real_producer/code/rung3_engine.py", "p5y_k5_cusum_real_point_executor/code/backends.py",
    "p5y_k5_cusum_real_point_executor/code/executor_core.py", "p5y_k5_cusum_real_point_executor/code/paths.py",
    "p5y_k5b_consumption_adapter/code/consumption_adapter.py", "p5y_k5_order3_readiness_audit/code/k5_minimality.py",
    "p5y_k5b_independent_countersignature/code/k5b_check.py",
]
FROZEN_DATA = [
    "p5y_k5_cusum_first_real_probe_protocol/evidence/slot-1/SCIENTIFIC_RECORD_SEALED.json",
    "p5y_k1_cover_ledger_successor/config/cells.json",
    "p5y_k1_cusum_aux5_composite_closure/evidence/closure_r1/COMPOSITE_EXPORT_MANIFEST.json",
    "p5y_k5_cusum_order3_r4_tightening/config/OPERATOR_CERTIFICATES_R4.json",
    "p5y_k5_cusum_order3_r4_tightening/config/QUALIFICATION_PROTOCOL_R4.json",
    "p5y_k5_feasibility/K5_GLOBAL_BRIDGE.md",
    "p5y_k5_remaining_cell_closure/phase_a/OPEN_CELL_MAP.json",
]
ROOT_FILES = ["rebaseguard-proof/src/rebaseguard_certify/__init__.py", "rebaseguard-proof/src/rebaseguard_certify/arb_backend.py",
              "rebaseguard-proof/src/rebaseguard_certify/polynomial.py", "rebaseguard-proof/src/rebaseguard_certify/residual.py",
              "rebaseguard-proof/src/rebaseguard_certify/spectral_candidate.py"]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    out = NS / "config/TEXT_PROTOCOL.json"
    if out.exists():
        print("refusing to overwrite", out)
        return 2
    ns_rel = str(NS.relative_to(REPO)) + "/"
    rels = [ns_rel + f for f in OWN] + [CP + f for f in FROZEN_CODE + FROZEN_DATA] + ROOT_FILES
    pins = {r: sha(REPO / r) for r in rels}
    sys.path.insert(0, str(NS / "code"))
    import text_mutants as TM
    proto = {
        "schema": "rebaseguard.p5y.k5.remaining-cell-closure.text-protocol.v1",
        "status": "FROZEN_PRE_RESULT",
        "statement": "TEXT_SPEC.md (pinned)",
        "scientific_question": "Deterministic wider-hull evenness transport of the adopted slot-1 point evidence; "
                               "per-cell L_k for K1 cells 1..40; consumption by the frozen K5-B",
        "new_real_scientific_addresses": 0,
        "hull_cells": list(range(1, 41)),
        "hull_rule": "eta = x_hi(k); C = max C_upper over cells 0..k; He6 hull norms and Hermite source sups on [0, eta]",
        "channel": {"cell_0": "adopted sealed L1",
                    "cells_1_40": "Lambda(k) = max(L0_m - sum_j M5_m(x_hi(j)) [(X - x_lo(j))^2 - (X - x_hi(j))^2]/2, "
                                  "-M3_m(X)), X = x_hi(k), j = 0..k, M5(x_hi(0)) = sealed",
                    "cells_ge_41": None},
        "consumptions": {"C1": "channel only (E6 semantics otherwise)",
                         "C2": "channel + curvature tightening on cells 0..40: H' = H cap [-M2, M2], M' = min(M_R2, M2) "
                               "with M2 = M2_m(x_hi(k)); the T-EXT result (dominates C1)"},
        "verdict_rule": "sign-blind; pre-evaluation gate failure -> NOT_QUALIFIED; post-evaluation gate failure -> VOID; "
                        "no rerun under this protocol; consumption only after the TEXT_RESULT sha256 is committed",
        "relation_to_slot1": "successor consumption of the sealed slot-1 record; the slot-1 result, its E6 output and its "
                             "POSITIVE map are not amended",
        "precision_bits": 256,
        "retry": "none; deterministic; any failed gate => T_EXT = NOT_QUALIFIED, nothing consumed",
        "adaptation": "none",
        "stopping_rule": "none (the whole frozen family is evaluated)",
        "gates": {
            "Q00_CLEAN_CHECKOUT": {"requirement": "git status --porcelain empty at the freeze commit"},
            "Q01_PINS": {"requirement": "every pin matches"},
            "Q02_REPLAY": {"requirement": "hull norms equal sealed; M5, trace, L1 within relative 2^-160; mode graded; CRAMER"},
            "Q03_FIXTURES": {"violations": 0, "min_ran": 100, "min_max_eta_C_e0": 10.7, "min_ran_eta_C_e0_ge_4": 3,
                             "min_ran_graded_det_in_0_0p1": 2, "max_min_graded_positive_det": 0.06,
                             "min_ran_scalar_fallback": 1,
                             "not_covered_by_fixtures": "the ee cap regime (hulls 33-40): the rule is min(graded, C) of two "
                                                        "valid bounds; manufactured Neumann rigs have C above the graded value"},
            "Q04_EVALUATE": {"requirement": "hulls 0..40 (hull 0 reproduces the sealed M5 exactly), all modes graded"},
            "Q05_XA": {"requirement": "independent re-derivation of M2..M5 and Lambda equal; M_n nondecreasing in k"},
            "Q06_MUTATIONS": {"transport": [m[0] for m in TM.TRANSPORT_MUTANTS], "consumption": [m[0] for m in TM.CONSUME_MUTANTS],
                              "requirement": "shams reproduce; all mutants detected"},
            "Q07_COST": {"cpu_seconds_max": 3600},
            "Q08_DETERMINISM": {"requirement": "second evaluate byte-identical"},
        },
        "post_seal": ["text_consume.py consume (manifest-bound K1 records 0-309 on vultr-02)",
                      "text_crosscheck.py consumption (X-B)", "independent adjudication (fresh context)"],
        "host": "rebaseguard-vultr-02, venv /root/work/rbg-cusum-aux5-venv, clean checkout of the freeze commit",
        "pins": pins,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proto, sort_keys=True, indent=1) + "\n")
    print("wrote", out, "pins", len(pins), "sha256", sha(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
