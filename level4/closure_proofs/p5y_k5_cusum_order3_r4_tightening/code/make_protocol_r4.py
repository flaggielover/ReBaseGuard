"""Emit config/QUALIFICATION_PROTOCOL_R4.json (frozen) or a seed-disjoint DEV protocol.

    python3 -B code/make_protocol_r4.py              -> config/QUALIFICATION_PROTOCOL_R4.json
    python3 -B code/make_protocol_r4.py --dev OUT    -> DEV (fixture seeds + 900000, lemma seed + 900000)
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
REPO = NS.parents[2]
CP = NS.parents[0]
REL = "level4/closure_proofs/p5y_k5_cusum_order3_r4_tightening/"

BOUND = ["odd_block_certificate.py", "odd_block_crosscheck.py", "operator_audit.py", "local_r5.py", "first_cell_r4.py",
         "m5_crosscheck.py", "constants_r4.py", "forecast_r4.py", "qualify_r4.py", "make_protocol_r4.py"]
CONFIG = ["config/OPERATOR_CERTIFICATES_R4.json", "config/REAL_CELL_AUTHORIZATION_REGISTRY_R4.json",
          "config/FEASIBILITY_CRITERION_R4.json", "config/PRE_RESULT_GATES_R4.json",
          "config/operator_certificates/C_o0_odd_block_certificate.json"]


def pins(ns: str) -> dict:
    root = CP / ns
    return {str(p.relative_to(REPO)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*")) if p.is_file() and "__pycache__" not in p.parts}


def odd_certificate_mutations():
    M = [
        ("O01_REFLECTED_HALF_SIGN", 'high = bi_add(high, bi_scale(kp(ws, "both", alpha, mid), -arb(1)))',
         'high = bi_add(high, bi_scale(kp(ws, "both", alpha, mid), arb(1)))'),
        ("O02_SPLIT_AT_ZERO_NOT_MINUS_HALF_D", 'mid = _lin(0, 1, "-1/2"), _lin(-1, 0, "1/2"), _lin("-1/2", "1/2", 0)',
         'mid = _lin(0, 1, "-1/2"), _lin(-1, 0, "1/2"), _lin(0, 0, 0)'),
        ("O03_H_COVER_DROPS_NEAR_DIAGONAL", "t0 = exact(HALF)", "t0 = exact(F(3, 4))"),
        ("O04_TRUNCATION_ALLOWANCE_DROPPED", "allow = arb(2) * Z_RANGE * sup_w * eps_z",
         "allow = arb(0) * Z_RANGE * sup_w * eps_z"),
    ]
    return [{"id": i, "old": o, "new": n, "required": True} for i, o, n in M]


def r5_mutations_r3():
    """The R3 R^(5) mutation set, verbatim (anchors in the R3 r5_majorant.py, which is not modified)."""
    r3 = json.loads((CP / "p5y_k5_cusum_order3_r3_infrastructure/config/QUALIFICATION_PROTOCOL_R3.json").read_text())
    return [dict(m, required=True) for m in r3["r5_mutations"]]


def local_r5_mutations():
    M = [
        ("L01_WRONG_PARITY_DRIFT_DROPPED_EVEN", "        o = x1 * nxt.o\n", "        o = 0 * nxt.o\n"),
        ("L02_POINT_ERROR_DROPPED", "e = cand[0] + err.e + x1 * nxt.e", "e = cand[0] + x1 * nxt.e"),
        ("L03_H_BASE_PARITY_FLIPPED", 'BASE_PARITY = {"h": 1, "S": -1, "F": -1, "W": -1}',
         'BASE_PARITY = {"h": -1, "S": -1, "F": -1, "W": -1}'),
        ("L04_RIGHT_PARITY_DRIFT_DROPPED", "o = cand[1] + err.o + x1 * nxt.o", "o = cand[1] + err.o"),
        ("L05_ANCHOR_REPLACES_TOWER_WITHOUT_MIN", "new[node] = R5._minv(a, anchors[node]) if node in anchors else a",
         "new[node] = G.V(a.e * 0, a.o * 0, a.t * 0)"),
    ]
    return [{"id": i, "old": o, "new": n, "required": True} for i, o, n in M]


def fixtures(dev: bool):
    s = 900000 if dev else 0
    F = [
        {"id": "FR4_01_tight_M5_a", "family": "tight_M5", "seed": 41001 + s, "C_target": 3, "x1": "1/4000", "noise": "0"},
        {"id": "FR4_02_tight_M5_b", "family": "tight_M5", "seed": 41002 + s, "C_target": 8, "x1": "1/2000", "noise": "0"},
        {"id": "FR4_03_tight_M5_c", "family": "tight_M5", "seed": 41003 + s, "C_target": 5, "c": "1/5", "x1": "1/3000",
         "noise": "0"},
        {"id": "FR4_04_parity_pure_cusum_like", "family": "parity_pure", "seed": 41004 + s, "C_target": 1233,
         "x1": "3133/6165000", "noise": "1/1000000"},
        {"id": "FR4_05_parity_leak", "family": "parity_leak", "seed": 41005 + s, "C_target": 20, "k_scale": "2",
         "x1": "1/100", "noise": "1/100000"},
        {"id": "FR4_06_slow_even_mode", "family": "slow_even", "seed": 41006 + s, "C_target": 400, "c": "1/5",
         "x1": "1/2000", "noise": "0"},
        {"id": "FR4_07_well_conditioned_odd", "family": "well_conditioned_odd", "seed": 41007 + s, "C_target": 6,
         "b": "1/3", "d": "1/5", "c": "1/5", "x1": "1/50", "noise": "1/1000000"},
        {"id": "FR4_08_near_boundary", "family": "near_boundary", "seed": 41008 + s, "C_target": 20, "x1": "1/20",
         "noise": "1/10000000"},
    ]
    return F


def build(dev: bool) -> dict:
    r3proto = CP / "p5y_k5_cusum_order3_r3_infrastructure/config/QUALIFICATION_PROTOCOL_R3.json"
    r3ev = CP / "p5y_k5_cusum_order3_r3_infrastructure/evidence/qualification_r3/part_synthetic_real.json"
    fx = fixtures(dev)
    return {
        "schema": "rebaseguard.p5y.k5.order3-r4.qualification-protocol.v1",
        "status": "DEV_CALIBRATION_ONLY" if dev else "FROZEN_PRE_RESULT", "frozen_utc": "2026-09-17",
        "scope": ("NON-SCIENTIFIC R4 qualification: exact odd-block C_o0 certificate replay and cross-check, R3 constants "
                  "and suites re-executed unchanged, local first-cell R^(5) majorant on manufactured sigma-systems against "
                  "exact truth and an independent Cauchy derivative, B01 test-power fixtures, cell-0 forecast from committed "
                  "magnitudes. No real cell, no R''' or R^(5) value of any (D,m), no probe, no authorization."),
        "runtime_contract": {"python": "3.12.3", "python_flint": "0.9.0", "numpy": "2.5.2",
                             "host": "rebaseguard-vultr-02", "prefix": "/root/work/rbg-cusum-aux5-venv", "machine": "x86_64"},
        "certificate_artifact": "config/operator_certificates/C_o0_odd_block_certificate.json",
        "odd_bad_payload_proposal": {"alpha": "21/20", "beta": "0", "depth": 3},
        "odd_certificate_mutations": odd_certificate_mutations(),
        "r5_mutations": r5_mutations_r3(), "local_r5_mutations": local_r5_mutations(),
        "fixtures": fx,
        "b01_fixtures": [f["id"] for f in fx if f["family"] == "tight_M5"],
        "b01_controls": [
            {"id": "SHAM_TOTAL_COMPONENT", "old": "acc = acc + R1E.exact(abs(c)) * (v.e if parity else v.t)",
             "new": "acc = acc + R1E.exact(abs(c)) * (v.t if parity else v.t)", "expect": "no violations (sound superset)"},
            {"id": "SHAM_ADD_ZERO_ODD", "old": "acc = acc + R1E.exact(abs(c)) * (v.e if parity else v.t)",
             "new": "acc = acc + R1E.exact(abs(c)) * ((v.e + 0 * v.o) if parity else v.t)", "expect": "no violations"}],
        "b01_precisions": [256, 384],
        "mutation_trials": [f["id"] for f in fx],
        "m5_crosscheck_fixtures": ["FR4_01_tight_M5_a", "FR4_06_slow_even_mode", "FR4_05_parity_leak"],
        "m5_crosscheck_grid_points": 5,
        "lemma_seed": 4401 + (900000 if dev else 0),
        "r3_protocol": str(r3proto.relative_to(REPO)), "r3_protocol_sha256": hashlib.sha256(r3proto.read_bytes()).hexdigest(),
        "r3_synthetic_payload_sha256": json.loads(r3ev.read_text())["body"]["payload_sha256"],
        "pure_modules": ["local_r5.py", "first_cell_r4.py", "m5_crosscheck.py"],
        "forbidden_imports_pure": ["cusum_layer1", "cusum_layer2", "aux_certifier", "aux_collocation", "aux_propagate",
                                   "refine2", "cusum_order3", "graded_real", "synthetic_real", "resolvent_certificate",
                                   "odd_block_certificate", "subprocess", "socket", "urllib", "requests"],
        "r1_bound_sha256": pins("p5y_k5_cusum_order3_real_producer"),
        "r2_bound_sha256": pins("p5y_k5_cusum_order3_r2_repair"),
        "r3_bound_sha256": pins("p5y_k5_cusum_order3_r3_infrastructure"),
        "bound_code_sha256": {REL + "code/" + f: hashlib.sha256((NS / "code" / f).read_bytes()).hexdigest() for f in BOUND},
        "bound_config_sha256": {REL + c: hashlib.sha256((NS / c).read_bytes()).hexdigest() for c in CONFIG},
        "gates": "config/PRE_RESULT_GATES_R4.json", "criterion": "config/FEASIBILITY_CRITERION_R4.json",
        "serialization": "json.dumps(sort_keys=True, separators=(',', ':'), ensure_ascii=True, default=str) for hashes; "
                         "exact rationals as strings",
    }


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--dev":
        Path(sys.argv[2]).write_text(json.dumps(build(True), indent=1) + "\n")
    else:
        (NS / "config/QUALIFICATION_PROTOCOL_R4.json").write_text(json.dumps(build(False), indent=1) + "\n")
