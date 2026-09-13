"""Freeze the K4 assembly checkpoint (pre-result). Writes config/K4_ASSEMBLY_CHECKPOINT.json and its external hash.

Binds the exact assembly code, its tests and the (byte-unchanged) proposal. Refuses to overwrite an existing, different
frozen checkpoint. Reads no scientific value of any cell record.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CP = NS.parent
OUT = NS / "config/K4_ASSEMBLY_CHECKPOINT.json"
HASH = NS / "config/K4_ASSEMBLY_CHECKPOINT_HASH"
BOUND = ("code/k4_assembly.py", "tests/test_k4_assembly.py", "config/K4_ASSEMBLY_PREDECLARATION.json")


def sha(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def build() -> dict:
    return {
        "schema": "rebaseguard.p5y.k4.assembly-checkpoint.v1",
        "status": "FROZEN_PRE_RESULT",
        "frozen_utc": "2026-09-13",
        "result_bearing": False,
        "supersedes_proposal": {"path": "config/K4_ASSEMBLY_PREDECLARATION.json", "sha256": sha(NS / BOUND[2]),
                                "amendments": ["domain predicate made strict (left < 2): a cell meeting (0,2] only at {2} is excluded",
                                               "genuine inputs fixed to sealed SR records + Lane C integrity audit + CUSUM attestation",
                                               "outcome -> disposition mapping fixed"]},
        "blinding": {"genuine_production_values_observed_before_freeze": False,
                     "disclosure": "committed NON-production PS1 control/qualification T4 records and Aux4 CUSUM cells 318,323 "
                                   "pre-date the freeze and were not evaluated for K4; one control T4 record was used only to "
                                   "confirm the t4_record_sha256 integrity function (hash equality, no interval read)"},
        "target": {
            "statement": "for each D in {CUSUM, SR} and m in {1,2,3,5}: R_{D,m}(e) < 0 for every e in (0, 2]",
            "not_asserted": "H2 for e > 2; the consumer licence (T8/T9 need only (0,2] given K1 sup|R| < 2) is P5X FEASIBILITY_AUDIT s8 / FROZEN_THEOREM s8 P5X-T7(1)",
            "premises": ["R(0) = 0 exactly (P5-T3)", "R differentiable, |R''| <= M_R2 on every cell (K1 frozen curvature_bound semantics)",
                         "R_interval, D_interval are the K1-certified enclosures of R(e0), R'(e0)"]},
        "domain": {
            "SR": {"table": "p5y_k1_sr_o9_partition_successor/config/successor_cells.json",
                   "table_sha256": sha(CP / "p5y_k1_sr_o9_partition_successor/config/successor_cells.json"),
                   "cells": "indices 0..294 (295 cells, contiguous from 0, last right 40372863/20000000)"},
            "CUSUM": {"table": "p5y_k1_cover_ledger_successor/config/cells.json",
                      "table_sha256": sha(CP / "p5y_k1_cover_ledger_successor/config/cells.json"),
                      "cells": "CUSUM indices 0..309 (310 cells, contiguous from 0, last right 2092283/1000000)"},
            "predicate": "non-symbolic cell with left < 2 and right > 0"},
        "input_schema": {
            "per_cell": {"cell|cell_index": "int", "e0": "[p, s] exact rationals, s == 0", "rho": "[p, s] exact rationals, s == 0",
                         "m": {"1|2|3|5": {"detector": "CUSUM|SR", "R_interval": {"lo": "rational str", "hi": "rational str"},
                                           "D_interval": {"lo": "rational str", "hi": "rational str"}, "M_R2": "rational str"}}},
            "encoding": "outward exact rational endpoints (intervals.record)", "floats": "refused"},
        "integrity": {
            "SR": "only via sealed PS1 production cell records: evidence t4 file sha256 == sealed sha256, T4 cell == sealed cell_id, "
                  "t4_record_sha256 == sha256(t4_cell.canonical(record minus key)); plus the Lane C audit "
                  "(rebaseguard.p5y.k1.ps1.postk1-adjudication-audit.v1) with INTEGRITY_READY_FOR_ADJUDICATION and A_completeness.complete true",
            "CUSUM": "attestation rebaseguard.p5y.k1.cusum-production.integrity-attestation.v1 with cells_verified == 326, "
                     "all_scientific_hashes_verified true, producer_identity_hash equal to the FROZEN CUSUM successor checkpoint "
                     "(recorded as producer_checkpoint_sha256), and every record carrying that producer_identity_hash"},
        "arithmetic": "exact rational; strict inequalities",
        "per_cell_enclosures": {"R_cell": "[R.lo - rho*mag(D) - rho^2*M/2 , R.hi + rho*mag(D) + rho^2*M/2]",
                                "Rprime_cell": "[D.lo - rho*M , D.hi + rho*M]"},
        "decision_procedure": [
            "cover: first left == 0, contiguous, last right >= 2, else K4_COVER_GAP",
            "chain: maximal prefix from e = 0 with Rprime_cell.hi < 0",
            "direct: every other cell R_cell.hi < 0",
            "counterexample: R.lo > 0 on any non-chain cell",
            "otherwise CERTIFICATE_TOO_LOOSE; no refinement, splitting, retry, tolerance or delta in this checkpoint"],
        "disposition_mapping": {
            "all 8 (D,m) K4_CELLWISE_ALL_CERTIFIED": "K4_DISCHARGE_CANDIDATE (K4 CLOSED only by independent adjudication)",
            "any K4_MATHEMATICAL_COUNTEREXAMPLE": "K4_FAIL_MATHEMATICAL",
            "any K4_CERTIFICATE_TOO_LOOSE, no counterexample": "K4_INCONCLUSIVE_K1_RECORDS (any tightening is a NEW predeclared successor)",
            "any K4_COVER_GAP / K4_SCOPE_INCOMPLETE / integrity refusal": "K4_FAIL_GOVERNANCE_INPUTS"},
        "execution_precondition": "K1 production inputs complete (PS1 369 sealed + CUSUM 326 successor records) and attested; not before",
        "bound_sources": {r: sha(NS / r) for r in BOUND},
    }


def main() -> int:
    cp = build()
    payload = (json.dumps(cp, indent=1, sort_keys=True) + "\n").encode()
    if OUT.exists() and OUT.read_bytes() != payload:
        raise SystemExit("a DIFFERENT frozen K4 checkpoint exists; refusing to overwrite")
    OUT.write_bytes(payload)
    HASH.write_text(sha(OUT) + "\n")
    print(json.dumps({"checkpoint_sha256": sha(OUT), "bound_sources": cp["bound_sources"]}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
