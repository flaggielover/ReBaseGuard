"""Per-unit scientific kernel for the K1 successor production DAG.

SCOPE OF WHAT EXISTS TODAY -- stated plainly, because the driver's readiness
depends on it.

The frozen DAG has 19 raw-variable objects per detector:
    h_1..h_4, S_0..S_4, F_0..F_4, dF_0..dF_4
Task1R qualified exactly ONE of these: the F_0-class equation-defect
certification for SR, on one patch, at one drift. The pre-existing
`ra_certifier.certify_at_exact_drift` certifies the OLD g-variable system for
CUSUM, which is a different formulation from the frozen raw-variable DAG and
does not decompose into these 19 objects.

Therefore the per-unit kernel is IMPLEMENTED for one object class and
NOT_IMPLEMENTED for the rest. This module reports that honestly per unit; it
never silently substitutes an object, and the driver never counts a
NOT_IMPLEMENTED unit as coverage.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
ROOT = NS.parents[2]
T1R = ROOT / "level4/closure_proofs/p5y_k1_task1r_budget_harness"
AUD = ROOT / "level4/closure_proofs/p5y_k1_sr_backend_cost_audit"
K1 = ROOT / "level4/closure_proofs/p5y_k1_binding_campaign"

# object classes and their implementation status
_CUSUM_OBJECTS = (["h_%d" % j for j in range(1, 5)]
                  + ["S_%d" % r for r in range(5)]
                  + ["F_%d" % r for r in range(5)]
                  + ["dF_%d" % r for r in range(5)])

IMPLEMENTED: dict[tuple[str, str], str] = {
    ("SR", "F_0"): "qualified by Task1R (PASS) and re-timed by the backend audit",
}
IMPLEMENTED.update({
    ("CUSUM", o): "raw-variable CUSUM kernel (p5y_k1_cusum_kernel), certified "
                  "against the frozen ledger at the representative cell"
    for o in _CUSUM_OBJECTS})

GAP_REASON = {
    "h": "kernel application h_j = K_e h_{j-1}: the source recursion has no "
         "production implementation",
    "S": "S_r = K_{raw,e} h_r: the raw-variable source has no production "
         "implementation for r >= 1",
    "F": "F_r = (I - K_e)^{-1} S_r for r >= 1: needs the S_r source, which does "
         "not exist",
    "dF": "derivative resolvent solve: the derivative source system has no "
          "production implementation",
}


def object_class(fn: str) -> str:
    if fn.startswith("dF_"):
        return "dF"
    if fn.startswith("F_"):
        return "F"
    if fn.startswith("S_"):
        return "S"
    if fn.startswith("h_"):
        return "h"
    raise ValueError(f"unknown function id: {fn}")


def kernel_status(det: str, fn: str) -> tuple[bool, str]:
    if (det, fn) in IMPLEMENTED:
        return True, IMPLEMENTED[(det, fn)]
    cls = object_class(fn)
    if det == "CUSUM":
        return False, (
            "no CUSUM raw-variable production kernel exists. "
            "ra_certifier.certify_at_exact_drift certifies the OLD g-variable "
            "system, which is a different formulation from the frozen "
            f"raw-variable DAG. {GAP_REASON[cls]}")
    return False, GAP_REASON[cls]


def implemented_fraction(units) -> dict:
    ok = sum(1 for d, _, f in units if kernel_status(d, f)[0])
    return {"implemented_units": ok, "total_units": len(units),
            "fraction": ok / len(units) if units else 0.0,
            "implemented_classes": sorted({f"{d}/{f}" for (d, f) in IMPLEMENTED})}


def run_unit(det: str, cell: int, fn: str, rec: dict, *, dry_run: bool = True) -> dict:
    """Execute one production unit into `rec`.

    dry_run=True (the default) performs NO certified numerics and marks the unit
    NOT_RUN. Production sets dry_run=False. A unit whose kernel does not exist is
    always marked NOT_IMPLEMENTED -- never FAILED, and never silently skipped.
    """
    ok, why = kernel_status(det, fn)
    rec["contributing_object_ids"] = [fn]
    if det == "CUSUM" and ok:
        rec["m_relevance"] = _m_relevance(fn)
        if dry_run:
            rec["status"] = "NOT_RUN"
            rec["certificate_status"] = "dry run: no certified numerics executed"
            return rec
        if CELL_DRIFT_IS_PLACEHOLDER:
            rec["status"] = "NOT_IMPLEMENTED"
            rec["failure_class"] = "CELL_DRIFT_MAPPING_NOT_IMPLEMENTED"
            rec["certificate_status"] = (
                "the CUSUM object kernel is implemented and certified, but the "
                "frozen cover walk mapping cell index -> exact rational drift is "
                "not. Refusing to certify at a placeholder drift.")
            return rec
        return _run_cusum(cell, fn, rec)
    if not ok:
        rec["status"] = "NOT_IMPLEMENTED"
        rec["failure_class"] = "KERNEL_NOT_IMPLEMENTED"
        rec["certificate_status"] = why
        return rec
    if dry_run:
        rec["status"] = "NOT_RUN"
        rec["certificate_status"] = "dry run: no certified numerics executed"
        return rec

    t0 = time.process_time()
    for p in (str(AUD / "code"), str(T1R / "code"), str(K1 / "task1")):
        if p not in sys.path:
            sys.path.insert(0, p)
    import harness as H
    import opt_backend as O
    from task1_f0 import build_candidate, resolvent_upper_bound
    from rebaseguard_certify.arb_backend import workprec

    ckj = _ck()
    D, Z = ckj["backend"]["D"], ckj["backend"]["Z"]
    amp = resolvent_upper_bound(H.E_NUM, H.E_DEN)
    with workprec(H.PROD_BITS):
        g = H.geometry()
        p1 = H.p1_rule(g["H"], g["span"])
        cand, cinfo = build_candidate(float(g["b"]), float(g["c"]), float(g["e"]))
        orig = H.run_panels
        H.run_panels = lambda cd, Dd, Zz, gg, pp, *, majorant=False, only_panel=None: \
            O.run_panels_opt(cd, Dd, Zz, gg, pp, only_panel=only_panel,
                             shared_cache={}, drift_cache={})
        try:
            cert = H.certify(cand, D, Z, g, p1, amp["C_at_e"], cinfo)
        finally:
            H.run_panels = orig
    rec.update({
        "patch": list(H.PATCH), "working_precision_bits": H.PROD_BITS,
        "candidate_id": "F_0/cheb(16,16)/dyadic2^-50",
        "candidate_degree": [H.CAND_DEGREE, H.CAND_DEGREE],
        "candidate_residual": cert["components"]["equation_defect_polynomial"],
        "kernel_residual": cert["components"]["tail_zeta_and_moments"],
        "resolvent_amplification_bound": amp["C_at_e"],
        "rounding_error": cert["components"]["rounding_exact_dyadic"],
        "interval_radius": cert["components"]["interval_arithmetic"],
        "propagated_absolute_half_width": amp["C_at_e"] * cert["delta_F0"],
        "allowed_absolute_half_width": H.B_CANDIDATE,
        "budget_usage_by_component": {k: v["fraction_of_line"]
                                      for k, v in cert["per_line"].items()},
        "endpoint_sliver_contribution": cert["components"]["endpoint_slivers"],
        "P1_E_d": p1["E_d"], "P1_headroom_rel": p1["HEADROOM_REL"],
        "cpu_seconds": time.process_time() - t0,
        "status": "COMPLETE" if cert["all_lines_pass"] else "FAILED",
        "failure_class": None if cert["all_lines_pass"] else "CANDIDATE_RESIDUAL_TOO_LARGE",
        "certificate_status": "equation-defect certificate, all frozen lines checked",
    })
    # R / R' are assembled in PHASE D from the certified objects; this unit
    # contributes F_0 and records that it did.
    return rec


def _m_relevance(fn: str) -> list[int]:
    """Which frozen m values consume this object (from the frozen DAG)."""
    idx = int(fn.split("_")[1])
    if fn.startswith(("F_", "dF_")):
        return [m for m in (1, 2, 3, 5) if idx <= m - 1]
    if fn.startswith("S_"):
        return [3, 5] if idx == 1 else ([2, 3, 5] if idx == 0 else [5])
    return [3, 5] if idx == 1 else [5]


def _run_cusum(cell: int, fn: str, rec: dict) -> dict:
    """One certified CUSUM raw-variable unit."""
    import time
    t0 = time.process_time()
    CK = ROOT / "level4/closure_proofs/p5y_k1_cusum_kernel/code"
    R1 = ROOT / "level4/closure_proofs/p5x_global_nonlinear_dynamics/compute_optimization_r1"
    for p in (str(CK), str(R1), str(ROOT / "rebaseguard-proof" / "src")):
        if p not in sys.path:
            sys.path.insert(0, p)
    import cusum_raw as CR
    from drift_minorant import drift_monotone_resolvent
    ck = _ck()
    e_num, e_den = _cell_drift(cell)
    C = drift_monotone_resolvent(e_num=e_num, e_den=e_den)["resolvent_bound_upper_float"]
    co = CR.collocation(e_num / e_den); co["e_rational"] = (e_num, e_den)
    obj = CR.build_objects(co)
    res = CR.certify_object(fn, obj, co)
    line = {"h": "B_kernel", "S": "B_kernel",
            "F": "B_candidate", "dF": "B_candidate"}[fn.split("_")[0]]
    allow = ck["budget_ledger"]["ledger_absolute"][line] / C
    ok = res["total_certified_error"] <= allow
    Rm = {m: CR.assemble(obj, co, m) for m in ck["scope"]["m_values"]}
    rec.update({
        "e_interval": [e_num / e_den, e_num / e_den],
        "candidate_id": f"CUSUM/{fn}/cheb(12,12)/dyadic2^-50",
        "candidate_degree": [CR.DEGREE, CR.DEGREE],
        "candidate_residual": res["equation_defect"],
        "kernel_residual": res["truncation_and_tail"],
        "resolvent_amplification_bound": C,
        "interval_radius": res["truncation_and_tail"],
        "propagated_absolute_half_width": C * res["total_certified_error"],
        "allowed_absolute_half_width": ck["budget_ledger"]["ledger_absolute"][line],
        "budget_usage_by_component": {line: res["total_certified_error"] / allow},
        "working_precision_bits": CR.BITS,
        "R_enclosure": {str(m): Rm[m][0] for m in Rm},
        "R_prime_enclosure": {str(m): Rm[m][1] for m in Rm},
        "cpu_seconds": time.process_time() - t0,
        "status": "COMPLETE" if ok else "FAILED",
        "failure_class": None if ok else "NUMERICAL_BUDGET_FAILURE",
        "certificate_status": f"raw-variable certified defect vs {line}",
    })
    return rec


CELL_DRIFT_IS_PLACEHOLDER = True


def _cell_drift(cell: int) -> tuple[int, int]:
    """PLACEHOLDER. NOT the frozen cover mapping.

    The frozen CUSUM cover is defined by a step-rule walk -- h(e) = 1/(4 a C(e)),
    greedy from e = 0, exact tiling over [0, 5.5] giving 323 sub-cells -- and the
    manifest records the RULE, not an explicit endpoint list. Resolving cell
    index -> exact rational drift therefore requires executing that walk, which
    this task did not implement.

    Production must not run against this placeholder: `run_unit` refuses when
    CELL_DRIFT_IS_PLACEHOLDER is set, so a cell cannot be silently certified at
    the wrong drift.
    """
    return (cell if cell > 0 else 1), 4


def _ck() -> dict:
    import json
    return json.loads((ROOT / "level4/closure_proofs/p5y_k1_successor_optimized"
                       / "config/checkpoint_s.json").read_text())
