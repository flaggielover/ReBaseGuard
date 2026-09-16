"""Emit config/QUALIFICATION_PROTOCOL_R3.json (frozen) or a seed-disjoint DEV protocol.

    python3 -B code/make_protocol_r3.py              -> config/QUALIFICATION_PROTOCOL_R3.json
    python3 -B code/make_protocol_r3.py --dev OUT    -> DEV (seeds + 900000), calibration of required mutation flags only
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
REPO = NS.parents[2]
CP = NS.parents[0]
REL = "level4/closure_proofs/p5y_k5_cusum_order3_r3_infrastructure/"

BOUND = ["resolvent_certificate.py", "hermite6_ext.py", "graded_real.py", "synthetic_real.py", "r5_majorant.py",
         "first_cell.py", "cell0_forecast_r3.py", "qualify_r3.py", "make_protocol_r3.py"]

# Required flags fixed from the seed-disjoint DEV calibration before the freeze (ids -> False with a reason).
NOT_REQUIRED = {}


def pins(ns: str) -> dict:
    root = CP / ns
    return {str(p.relative_to(REPO)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*")) if p.is_file() and "__pycache__" not in p.parts}


def wiring_mutations():
    M = [
        ("RW01_PARITY_BASE_S_EVEN", 'PARITY_BASE = {"h": 1, "S": -1, "F": -1, "W": -1}',
         'PARITY_BASE = {"h": 1, "S": 1, "F": -1, "W": -1}'),
        ("RW02_F_ENVELOPE_ORDER_SHIFT",
         '[(comb(n, i), "K", i + 1, keys[n - i]) for i in range(1, n + 1)]',
         '[(comb(n, i), "K", i, keys[n - i]) for i in range(1, n + 1)]'),
        ("RW03_F_ENVELOPE_DROPS_K1_TERM", 'terms = [(1, "K", 1, keys[n])] + ', 'terms = [] + '),
        ("RW04_S_ENVELOPE_J_AS_K", '[(comb(k, i), "J", i + 1, ("h", r, k - i)) for i in range(k + 1)]',
         '[(comb(k, i), "K", i + 1, ("h", r, k - i)) for i in range(k + 1)]'),
        ("RW05_ALLOWANCE_DROPPED", 'return G.V(e + allow, o + allow, entry["delta_mid"])',
         'return G.V(e, o, entry["delta_mid"])'),
        ("RW06_LEAF_S0_PARITY", 'return "leaf_S0", (derivative_parity("S", k + 1), k + 1)',
         'return "leaf_S0", (derivative_parity("S", k), k + 1)'),
        ("RW07_CELL_DROPS_RHO", '"cell": (mid.e + rho * env.e, mid.o + rho * env.o, mid.t + rho * env.t)}',
         '"cell": (mid.e + 0 * env.e, mid.o + 0 * env.o, mid.t + rho * env.t)}'),
        ("RW08_NO_LEAKAGE_ETA", 'eta_cell = exact(max(abs(left), abs(right)))', 'eta_cell = exact(0)'),
        ("RW09_SCLOSED3_ALLOWANCE_DROPPED", 'res["Sclosed_3"] = {"mid": (a3, a3, a3),',
         'res["Sclosed_3"] = {"mid": (a3 * 0, a3 * 0, a3 * 0),'),
        ("RW10_ENGINE_NAME_DF_H_SWAP", 'ENGINE_NAME = {"F": 0, "dF": 1, "H": 2, "G": 3}',
         'ENGINE_NAME = {"F": 0, "dF": 2, "H": 1, "G": 3}'),
        ("RW11_CANDIDATE_SUP_PARITY_SWAP", 'return G.V(e, o, cert.sup[key])', 'return G.V(o, e, cert.sup[key])'),
        ("RW12_RESIDUAL_RANGE_PARITY_SWAP", 'e, o = parity_ranges(cert, ("res", name), pair)',
         'o, e = parity_ranges(cert, ("res", name), pair)'),
    ]
    return [{"id": i, "old": o, "new": n, "required": i not in NOT_REQUIRED} for i, o, n in M]


def r5_mutations():
    M = [
        ("B01_M5_USES_ODD_COMPONENT", "acc = acc + R1E.exact(abs(c)) * (v.e if parity else v.t)",
         "acc = acc + R1E.exact(abs(c)) * (v.o if parity else v.t)"),
        ("B02_TRANSPORT_SIGN", "return point_interval[0] - pen, point_interval[1] + pen",
         "return point_interval[0] + pen, point_interval[1] - pen"),
        ("B03_TOWER_DROPS_RESOLVENT", 'put(f"F:{r}:{n}", G.apply_res(R, acc, C))', 'put(f"F:{r}:{n}", acc)'),
        ("B04_PENALTY_SCALE", "pen = (x1 * x1 / 2) * R1E.fraction_of(M5.abs_upper())",
         "pen = (x1 * x1 / 200) * R1E.fraction_of(M5.abs_upper())"),
        ("B05_S0_TOWER_PARITY", 'put(f"S:0:{n}", gts((-1) ** (n + 1), s0[n], s0[n + 1]))',
         'put(f"S:0:{n}", gts((-1) ** n, s0[n], s0[n + 1]))'),
        ("B06_TOWER_J_AS_K", 'G.apply_op(j, j, i, T[f"h:{r}:{n - i}"], eta, 1, parity)',
         'G.apply_op(j, j, i, T[f"h:{r}:{n - i}"], eta, 0, parity)'),
    ]
    return [{"id": i, "old": o, "new": n, "required": i not in NOT_REQUIRED} for i, o, n in M]


def certificate_mutations():
    M = [
        ("CM01_BERNSTEIN_MIN_FROM_UPPER", "lo_c, hi_c = c.lower(), c.upper()", "lo_c, hi_c = c.upper(), c.upper()"),
        ("CM02_MARGIN_THRESHOLD_RELAXED", "ok = bool(Lmin > 0) and bool(wmin >= 0)", "ok = bool(Lmin > -1) and bool(wmin >= 0)"),
        ("CM03_ATOM_REMOVED_THRICE", "lo = bi_add(lo, bi_scale(origin, -arb(1)))", "lo = bi_add(lo, bi_scale(origin, -arb(3)))"),
    ]
    return [{"id": i, "old": o, "new": n, "required": i not in NOT_REQUIRED} for i, o, n in M]


def first_cell_fixtures(dev: bool):
    s = 900000 if dev else 0
    return [
        {"id": "FC1_cusum_cell0_analogue_C1233", "seed": 3001 + s, "C_target": 1233, "x1": "3133/6165000", "noise": "1/1000000"},
        {"id": "FC2_C50_exact", "seed": 3002 + s, "C_target": 50, "x1": "1/50", "noise": "0"},
        {"id": "FC3_C4_wide", "seed": 3003 + s, "C_target": 4, "x1": "1/10", "noise": "1/100000"},
        {"id": "FC4_C100_small_odd_eigen", "seed": 3004 + s, "C_target": 100, "c": "1/5", "x1": "3133/500000",
         "noise": "1/10000000"},
        {"id": "FC5_C10_exact_x1_large", "seed": 3005 + s, "C_target": 10, "x1": "1/20", "noise": "0"},
    ]


def build(dev: bool) -> dict:
    return {
        "schema": "rebaseguard.p5y.k5.order3-r3.qualification-protocol.v1",
        "status": "DEV_CALIBRATION_ONLY" if dev else "FROZEN_PRE_RESULT", "frozen_utc": "2026-09-16",
        "scope": ("NON-SCIENTIFIC R3 infrastructure qualification: certified C_o0 / C_e0 replay, He_6 extension, real "
                  "CUSUM graded wiring on synthetic candidates through the real Arb operator path, first-cell strategy A "
                  "vs B on manufactured odd systems, cell-0 forecast from committed magnitudes and certified constants. "
                  "No real cell, no R''' of any (D,m), no probe, no authorization."),
        "runtime_contract": {"python": "3.12.3", "python_flint": "0.9.0", "numpy": "2.5.2",
                             "host": "rebaseguard-vultr-02", "prefix": "/root/work/rbg-cusum-aux5-venv", "machine": "x86_64"},
        "synthetic_seed": 9001 if dev else 1,
        "certificate_artifacts": {"C_o0": "config/operator_certificates/C_o0_certificate.json",
                                  "C_e0": "config/operator_certificates/C_e0_certificate.json"},
        "wiring_mutations": wiring_mutations(), "r5_mutations": r5_mutations(),
        "certificate_mutations": certificate_mutations(),
        "first_cell_fixtures": first_cell_fixtures(dev),
        "r5_mutation_trials": ["FC5_C10_exact_x1_large", "FC2_C50_exact", "FC3_C4_wide", "FC1_cusum_cell0_analogue_C1233",
                               "FC4_C100_small_odd_eigen"],
        "lemma_seed": 99001 if dev else 4001,
        "he6_cells": [["0", "5083/10000000"], ["1/3", "103/300"], ["-1/20", "1/20"]],
        "pure_modules": ["r5_majorant.py", "first_cell.py"],
        "forbidden_imports_pure": ["cusum_layer1", "cusum_layer2", "aux_certifier", "aux_collocation", "aux_propagate",
                                   "refine2", "cusum_order3", "graded_real", "synthetic_real", "resolvent_certificate",
                                   "subprocess", "socket", "urllib", "requests"],
        "r1_bound_sha256": pins("p5y_k5_cusum_order3_real_producer"),
        "r2_bound_sha256": pins("p5y_k5_cusum_order3_r2_repair"),
        "bound_code_sha256": {REL + "code/" + f: hashlib.sha256((NS / "code" / f).read_bytes()).hexdigest() for f in BOUND},
        "gates": "config/PRE_RESULT_GATES_R3.json", "criterion": "config/FEASIBILITY_CRITERION_R3.json",
    }


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--dev":
        Path(sys.argv[2]).write_text(json.dumps(build(True), indent=1) + "\n")
    else:
        (NS / "config/QUALIFICATION_PROTOCOL_R3.json").write_text(json.dumps(build(False), indent=1) + "\n")
