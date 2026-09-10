"""P5Y K1 SR O9 -- B_int P1-bound successor (minimal certifier change).

Authorized by config/P1_BOUND_REUSE_AUTHORIZATION.json
(P1_DERIVATIVE_BOUND_REUSE_FOR_SOFTPLUS_LAGRANGE_FACTOR).  The ONLY change against the
endpoint-strip successor b48973d6 is the SOURCE of the L-R3.1 Lagrange-factor ball A_9 that
sr_local.softplus_local_enclosure hands to harness.softplus_tm2:

    before  A_9 = coefficient 9 of arb_series(log(1+exp(x))) at x = centre + [-rho, rho]
    after   A_9 = [-M/9!, M/9!],  M = sr_local.softplus_derivative_bound_tight(9)
            (the frozen P1 rule's own M; |sp^(9)(u)| <= M for EVERY real u)

a_0..a_8 are the frozen function's own output (the same objects), centre and rho are passed
through untouched, and E_d := |A_9| rho^9 exactly as in L-R3.1.  Every other module
(harness, opt_backend, the T2 certifier, the endpoint strips) is imported unchanged.  The
override is scoped to the certification call only; candidate construction runs outside it.
"""
from __future__ import annotations

import argparse
import contextlib
import copy
import hashlib
import json
import resource
import time
from fractions import Fraction as Fr
from math import factorial
from pathlib import Path

import sr_o9_candidates as T
import sr_o9_patch_certifier as PC
import sr_o9_endpoint_strips as ES          # b48973d6 architecture; raw-shift fix installed by import
from flint import arb

L, H = PC.L, PC.H
AUTHORIZATION = "P1_DERIVATIVE_BOUND_REUSE_FOR_SOFTPLUS_LAGRANGE_FACTOR"
NS = Path(__file__).resolve().parents[1]
PRED = NS.parent / "p5y_k1_sr_o9_endpoint_strip_successor"
_FROZEN_ENCLOSURE = L.softplus_local_enclosure
STATS: dict = {}


def a9_p1(degree: int) -> arb:
    """[-M/(d+1)!, M/(d+1)!] with the frozen tight derivative bound M (the P1 rule's M)."""
    M = L.softplus_derivative_bound_tight(degree + 1)
    return arb(0, (M / arb(factorial(degree + 1))).upper())


def softplus_local_enclosure_p1(centre: arb, half_width: arb, degree: int):
    if degree != H.SOFTPLUS_DEGREE:
        raise T.T1Refusal(f"softplus degree {degree} != frozen {H.SOFTPLUS_DEGREE}")
    a, _E_old, a_next_old = _FROZEN_ENCLOSURE(centre, half_width, degree)
    A = a9_p1(degree)
    E = arb(0, (A.abs_upper() * half_width ** (degree + 1)).upper())
    STATS["calls"] += 1
    STATS["old_ball_contains_new"] += int(a_next_old.contains(A))
    r = float(a_next_old.rad())
    STATS["old_rad_min"] = r if STATS["old_rad_min"] is None else min(STATS["old_rad_min"], r)
    STATS["old_rad_max"] = r if STATS["old_rad_max"] is None else max(STATS["old_rad_max"], r)
    return a, E, A


@contextlib.contextmanager
def p1_lagrange_factor():
    if H.L is not L or L.softplus_local_enclosure is not _FROZEN_ENCLOSURE:
        raise T.T1Refusal("sr_local binding is not the frozen one (double install or foreign module)")
    STATS.clear()
    STATS.update(calls=0, old_ball_contains_new=0, old_rad_min=None, old_rad_max=None)
    L.softplus_local_enclosure = softplus_local_enclosure_p1
    try:
        yield STATS
    finally:
        L.softplus_local_enclosure = _FROZEN_ENCLOSURE


def predecessor_record(cell_index, i, j):
    p = PRED / f"evidence/pilot36/c{cell_index}_p{i}_{j}.json"
    return (p, json.loads(p.read_text())) if p.exists() else (None, None)


def _diag_comparable_hash(nodes):
    n = copy.deepcopy(nodes)
    for rec in n.values():
        rec["candidate_identity_hash"] = None
    return hashlib.sha256(T.canonical(n)).hexdigest()


def run_case(cell_index, i, j):
    nodes = [f"F:{r}:k0" for r in range(5)]
    built = T.build_cell_candidates(cell_index)["scientific"]
    hashes = {x["node"]: x["identity_hash"] for x in built["candidates"]}
    cell = T.frozen_cell(cell_index)
    C = Fr(cell["C_upper"])
    with T.scientific_precision():
        cands = {x["node"]: T.to_arb_matrix(x["mantissas"]) for x in built["candidates"]}
        e = T.cell_geometry(cell)["e0"]
        with p1_lagrange_factor() as st:
            new = ES.certify_patch_strips(i, j, e, cands, cand_hashes=hashes, C_gate=C, nodes=nodes)
        stats = dict(st)
    cpu, wall = new.pop("cpu_s"), new.pop("wall_s")
    int_allow = Fr(T.spec.NESTED_CANDIDATE["B_int"]) / C
    per_node, fails = {}, set()
    for n, rec in sorted(new["nodes"].items()):
        lg = rec["local_gates"]
        end_exact = C * Fr(*_enc_frac(rec["channels"]["end"])) <= Fr(1, 250)
        per_node[n] = {"int_over_allowance": float(Fr(*_enc_frac(rec["channels"]["int"])) / int_allow),
                       "end_gate_exact_PASS": end_exact, "end_over_gate": rec["end_over_gate"],
                       "local_gates_PASS": {k: v["PASS"] for k, v in lg.items()},
                       "channels_float": rec["channels_float"]}
        fails |= {k for k, v in lg.items() if not v["PASS"]}
        if not end_exact:
            fails.add("endpoint_gate")
    ppath, prec = predecessor_record(cell_index, i, j)
    comparison = None
    if prec is not None:
        old = prec["scientific"]["new"]
        comparison = {"predecessor_file": str(ppath.relative_to(NS.parent)),
                      "predecessor_file_sha256": hashlib.sha256(ppath.read_bytes()).hexdigest(),
                      "n_z_equal": old["n_z"] == new["n_z"], "strip_ids_equal": old["strip_ids"] == new["strip_ids"],
                      "strip_P1_equal": old["strip_P1"] == new["strip_P1"],
                      "C_upper_equal": prec["scientific"]["C_upper"] == f"{C.numerator}/{C.denominator}",
                      "candidate_hashes_equal": all(old["nodes"][n]["candidate_identity_hash"] == new["nodes"][n]["candidate_identity_hash"] for n in nodes),
                      "contracts_equal": all(old["nodes"][n]["contracts"] == new["nodes"][n]["contracts"] for n in nodes),
                      "channels_old": {n: old["nodes"][n]["channels_float"] for n in nodes},
                      "failing_old": sorted({k for n in nodes for k, v in old["nodes"][n]["local_gates"].items() if not v["PASS"]})}
    sci = {"case": {"cell": cell_index, "patch": [i, j]}, "C_upper": f"{C.numerator}/{C.denominator}",
           "authorization": AUTHORIZATION, "new": new}
    summary = {"B_int_PASS": all(p["local_gates_PASS"]["int"] for p in per_node.values()),
               "endpoint_PASS": all(p["end_gate_exact_PASS"] and p["local_gates_PASS"]["end"] for p in per_node.values()),
               "all_local_gates_PASS": not fails, "failing": sorted(fails),
               "worst_int_over_allowance": max(p["int_over_allowance"] for p in per_node.values()),
               "worst_end_over_gate": max(p["end_over_gate"] for p in per_node.values()),
               "F0_int_over_allowance": per_node["F:0:k0"]["int_over_allowance"]}
    return {"scientific": sci, "scientific_hash": hashlib.sha256(T.canonical(sci)).hexdigest(),
            "diag_comparable_nodes_hash": _diag_comparable_hash(new["nodes"]),
            "summary": summary, "per_node": per_node, "lagrange_factor_stats": stats,
            "comparison_b48973d6": comparison,
            "timing": {"certify_cpu_s": cpu, "certify_wall_s": wall, "process_cpu_s": time.process_time()},
            "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}


def _enc_frac(enc):
    m, ex = enc
    return (m * 2 ** ex, 1) if ex >= 0 else (m, 2 ** (-ex))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", type=int, required=True)
    ap.add_argument("--patch", type=int, nargs=2, required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    T.check_threads()
    r = run_case(a.cell, *a.patch)
    open(a.out, "wb").write(T.canonical(r))
    print(json.dumps({"case": [a.cell, *a.patch], "hash": r["scientific_hash"], **r["summary"],
                      "cpu": r["timing"]["certify_cpu_s"], "rss_kib": r["peak_rss_kib"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
