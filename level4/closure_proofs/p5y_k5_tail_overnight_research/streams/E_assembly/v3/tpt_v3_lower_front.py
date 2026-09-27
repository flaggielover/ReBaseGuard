"""TPT V3: theorem TPT on the REAL, NON-TARGET lower-front TC cells (CUSUM cells 11..44, m in {1, 2, 3, 5}).

Quarantine (config/TARGET_QUARANTINE.json + the task's binding rules):
* data: ONLY p5y_k5_lower_front_order3/evidence/tc_r1/cells/TC_CELL_<k>.json (k = 11..44) and
  TC_CONSUMPTION.json, restricted to cells 11..44 immediately after loading (the rest is dropped before any
  computation);
* no historical campaign module is imported (import guard installed first); the TC enclosure is re-derived
  independently in tc_reder.py from THEOREM_TC.md; tpt.py (the code under test) is imported, never edited;
* ov_quarantine.guard_cell("CUSUM", m, cell) before every (cell, m) evaluation; one ledger line per run;
* writes only NS/validation/TPT_V3_LOWER_FRONT.json.

Steps per (cell, m):
 1. whole-cell TC enclosure H_m from the frozen record fields (tc_reder.whole_cell);
 2. REPRODUCTION GATE: H_m == tc_audit[cell][m]["H_TC"] exactly (as rationals). Pairs failing are gated out;
 3. tpt.CellProfile from the same per-source quantities (profile form); variant A with H_K1 = None, variant B with
    H_K1 := the consumed certified enclosure H_final; g_hi = hi(R - e0 D) = R.hi - e0 D.lo (K5_GLOBAL_BRIDGE.md,
    frozen k5b_literal); P_tpt (closed), P_riemann (N = 64 and 256), P_c5t, P_frozen, Gamma under each; an
    independent exact P* (no cap) and an independent Riemann LOWER sum bracket; dominance and ordering checks;
    direct-clause (Gamma < 0) status under each consumer (information only: every pair is closed already).
Also: non-target probes of three tpt.py properties (guard coverage, m-vs-terms binding, split-point side).
"""
from __future__ import annotations

import datetime
import hashlib
import json
import statistics
import sys
import time
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent               # .../streams/E_assembly/v3
NS = HERE.parents[2]                                  # namespace root
sys.path.insert(0, str(NS / "code"))
import ov_quarantine as Q  # noqa: E402

Q.install_import_guard()
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import tc_reder as T  # noqa: E402
import tpt  # noqa: E402  (code under test; imported, never modified)

LF_EVID = NS.parent / "p5y_k5_lower_front_order3" / "evidence" / "tc_r1"
CELLS = tuple(range(11, 45))                          # lower-front TC cells: the only allowed addresses
MS = (1, 2, 3, 5)
DETECTOR = "CUSUM"
OUT = NS / "validation" / "TPT_V3_LOWER_FRONT.json"

_guard_calls = [0]


def guard(m: int, cell: int) -> None:
    if cell not in CELLS:
        raise Q.QuarantineRefusal(f"cell {cell} outside the allowed lower-front set")
    Q.guard_cell(DETECTOR, m, cell)
    _guard_calls[0] += 1


def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha_q(x: Fr) -> str:
    return hashlib.sha256(str(x).encode()).hexdigest()


def dec(x: Fr, sig: int = 25) -> str:
    """Round-to-nearest decimal display of an exact rational with `sig` significant digits (display only)."""
    if x == 0:
        return "0"
    neg = x < 0
    a = -x if neg else x
    e = len(str(a.numerator)) - len(str(a.denominator))
    if Fr(10) ** e > a:
        e -= 1
    scaled = a / Fr(10) ** (e - sig + 1)
    q = (scaled.numerator * 2 + scaled.denominator) // (2 * scaled.denominator)
    digits = str(q)
    if len(digits) > sig:
        digits, e = digits[:sig], e + 1
    return f"{'-' if neg else ''}{digits[0]}.{digits[1:]}e{e:+d}"


def load_inputs() -> tuple:
    files = {}
    recs = {}
    for k in CELLS:
        p = LF_EVID / "cells" / f"TC_CELL_{k}.json"
        Q.guard_path(p)
        raw = p.read_bytes()
        files[str(p.relative_to(NS.parent))] = sha_bytes(raw)
        rec = json.loads(raw)
        if rec.get("cell") != k or rec.get("mode") != "real" or not rec.get("identity_gate", {}).get("identical"):
            raise RuntimeError(f"cell record {k} is not the gated real record of that cell")
        recs[k] = rec
    p = LF_EVID / "TC_CONSUMPTION.json"
    Q.guard_path(p)
    raw = p.read_bytes()
    files[str(p.relative_to(NS.parent))] = sha_bytes(raw)
    full = json.loads(raw)
    del raw
    # ---- restrict to cells 11..44 IMMEDIATELY; nothing else is kept or computed on
    cons = {m: {k: {f: full["consumptions"][str(m)]["cells"][str(k)][f] for f in ("R", "D", "H", "M")}
                | {"via": full["consumptions"][str(m)]["via"][str(k)]} for k in CELLS} for m in MS}
    audit = {k: {m: full["tc_audit"][str(k)][str(m)] for m in MS} for k in CELLS}
    meta = {"tc_cells": full["tc_cells"], "schema": full["schema"], "replay_gate": full["replay_gate"],
            "protocol_sha256": full["protocol_sha256"], "freeze_commit": full["freeze_commit"]}
    del full
    if sorted(meta["tc_cells"]) != list(CELLS):
        raise RuntimeError("TC consumption does not list exactly the lower-front cells")
    return recs, cons, audit, meta, files


def build_profile(rec: dict, wc: dict, k: int, m: int, A: dict, g_hi: Fr, H_K1) -> "tpt.CellProfile":
    terms = [tpt.SourceTerm(H_at_a=t["H_at_a"], abs_G_at_a=t["abs_G_at_a"], fF=t["f"][0], fD=t["f"][1],
                            fH=t["f"][2], fG=t["f"][3], Env4=t["Env4"]) for t in wc["terms"]]
    return tpt.CellProfile(detector=DETECTOR, m=m, cell=k, e0=Fr(rec["e0"]), rho=Fr(rec["rho"]), g_hi=g_hi,
                           A0=A["A0"], A1=A["A1"], A2=A["A2"], terms=terms, W=wc["W"], H_K1=H_K1,
                           label=f"CUSUM m={m} cell={k}")


def evaluate_pair(rec: dict, cons_km: dict, aud_km: dict, k: int, m: int) -> dict:
    guard(m, k)
    A = {x: Fr(aud_km["A"][x]) for x in ("A0", "A1", "A2")}
    e0, rho = Fr(rec["e0"]), Fr(rec["rho"])
    xl, xh = Fr(rec["left"]), Fr(rec["right"])
    geom_ok = (e0 == (xl + xh) / 2 and rho == (xh - xl) / 2 and xl > 0)
    wc = T.whole_cell(rec, A, m)
    H_TC = tuple(Fr(x) for x in aud_km["H_TC"])
    H_fin = tuple(Fr(x) for x in aud_km["H_final"])
    gate = wc["H"] == H_TC
    out = {"cell": k, "m": m, "e0": str(e0), "rho": str(rho), "x_lo": str(xl), "x_hi": str(xh),
           "geometry_consistent": geom_ok,
           "gate": {"pass": gate, "H_TC_committed_sha256": [sha_q(H_TC[0]), sha_q(H_TC[1])],
                    "H_rederived_sha256": [sha_q(wc["H"][0]), sha_q(wc["H"][1])],
                    "H_TC_dec": [dec(H_TC[0]), dec(H_TC[1])]}}
    if not gate:
        d = [wc["H"][0] - H_TC[0], wc["H"][1] - H_TC[1]]
        out["gate"]["difference_dec"] = [dec(d[0]), dec(d[1])]
        return out
    # ---- consumption-side inputs for this (cell, m)
    R = [Fr(x) for x in cons_km["R"]]
    D = [Fr(x) for x in cons_km["D"]]
    H_cons = tuple(Fr(x) for x in cons_km["H"])
    M_cons = Fr(cons_km["M"])
    g_hi = R[1] - e0 * D[0]                          # hi(R - e0 D), e0 > 0 (k5b_literal: R.hi - e0 * D.lo)
    g_lo = R[0] - e0 * D[1]
    # ---- variant A (H_K1 = None) and B (H_K1 = consumed certified enclosure H_final)
    cpA = build_profile(rec, wc, k, m, A, g_hi, None)
    cpB = build_profile(rec, wc, k, m, A, g_hi, H_fin)
    wcA = tpt.whole_cell_enclosure(cpA)
    gateB = (wcA == H_TC)
    loT, hiT = tpt.lo_hi_polys(cpA)
    lo, hi = T.profile_polys(wc, m)
    polys_equal = ([list(loT), list(hiT)] == [lo, hi])
    pc = tpt.penalty_closed(cpA)
    pr64 = tpt.penalty_riemann(cpA, N=64)
    pr256 = tpt.penalty_riemann(cpA, N=256)
    c5 = tpt.penalty_c5t(cpA)
    fr = tpt.penalty_frozen(cpA)
    fr_cons = rho * xh * M_cons                       # the frozen direct clause exactly as consumed (M_k)
    ex = T.exact_Pstar_nocap(lo, hi, e0, rho)
    lw64 = T.lower_sum(lo, hi, e0, rho, 64)
    pcB = tpt.penalty_closed(cpB)
    c5B, frB = tpt.penalty_c5t(cpB), tpt.penalty_frozen(cpB)
    try:
        tpt.evaluate(cpA)
        eval_raised = None
    except AssertionError as exc:                     # evaluate() asserts V4 and TPT-D
        eval_raised = str(exc)
    P = pc["P_star"]
    # profile at the midpoint must meet the consumed enclosure (both contain R''(e0)): a real-data soundness probe
    lo0, hi0 = T.poly_eval(lo, Fr(0)), T.poly_eval(hi, Fr(0))
    loR, hiR = T.poly_eval(lo, rho), T.poly_eval(hi, rho)
    rad_tot = [sum((T.poly_eval(t["radpoly_s"], s) for t in wc["terms"]), Fr(0)) / m for s in (Fr(0), rho)]
    # breakdown of the upper profile hi(s) = W_hi + (1/m) sum_r [H_hi_r + rad_r(s) + s |G_r(a)|]
    tc_rad0 = sum((T.poly_eval(t["radpoly_s"], Fr(0)) for t in wc["terms"]), Fr(0)) / m   # rad_r(0): motion term is 0
    tc_radR = sum((t["rad"] for t in wc["terms"]), Fr(0)) / m
    motion = sum((rho * t["abs_G_at_a"] for t in wc["terms"]), Fr(0)) / m
    breakdown = {
        "tc_rad_mid_over_tc_rad_whole": float(tc_rad0 / tc_radR),
        "Gmotion_over_half_width_at_rho": float(motion / (tc_radR + motion)),
        "hi_variation_over_hi_rho": float((hiR - hi0) / hiR) if hiR else None,
        "hi_variation_over_width_at_rho": float((hiR - hi0) / (hiR - loR)),
        "W_width_over_width_at_rho": float((wc["W"][1] - wc["W"][0]) / (hiR - loR)),
    }
    checks = {
        "gate_B_tpt_whole_cell_equals_H_TC": gateB,
        "tpt_profile_polys_equal_independent": polys_equal,
        "P_tpt_equals_independent_exact_Pstar": P == ex["P_star"],
        "I_right_equal": pc["I_right"] == ex["I_right"], "I_left_equal": pc["I_left"] == ex["I_left"],
        "no_split_used": pc["split_right"] is None and pc["split_left"] is None,
        "lower64_le_P_tpt": lw64 <= P,
        "P_tpt_le_riemann64": P <= pr64, "P_tpt_le_riemann256": P <= pr256, "riemann256_le_riemann64": pr256 <= pr64,
        "P_tpt_le_P_c5t": P <= c5, "P_c5t_le_P_frozen": c5 <= fr, "P_c5t_lt_P_frozen": c5 < fr,
        "P_frozen_tpt_equals_consumed_clause": fr == fr_cons,
        "variantB_identical_to_A": (pcB["P_star"] == P and c5B == c5 and frB == fr),
        "H_final_equals_H_TC": H_fin == H_TC, "H_consumed_equals_H_final": H_cons == H_fin,
        "profile_at_e0_meets_H_final": max(lo0, H_fin[0]) <= min(hi0, H_fin[1]),
        "profile_at_rho_equals_H_TC": (loR, hiR) == H_TC,
        "profile_monotone_coeffs_nonneg": all(c >= 0 for t in wc["terms"] for c in t["radpoly_s"]),
        "g_lo_le_g_hi": g_lo <= g_hi,
        "evaluate_raised": eval_raised,
    }
    G = {"tpt": g_hi + P, "riemann64": g_hi + pr64, "c5t": g_hi + c5, "frozen": g_hi + fr}
    out.update({
        "via_consumed": cons_km["via"],
        "g_hi": {"dec": dec(g_hi), "sha256": sha_q(g_hi)},
        "P": {"tpt_closed": dec(P), "riemann64": dec(pr64), "riemann256": dec(pr256), "lower64_indep": dec(lw64),
              "exact_indep": dec(ex["P_star"]), "c5t": dec(c5), "frozen": dec(fr), "frozen_consumed": dec(fr_cons),
              "I_right": dec(pc["I_right"]), "I_left": dec(pc["I_left"]),
              "sha256": {"tpt": sha_q(P), "c5t": sha_q(c5), "frozen": sha_q(fr)}},
        "attaining_side": "none" if P == 0 else ("right" if pc["I_right"] >= pc["I_left"] else "left"),
        "ratios": {"tpt_over_c5t": float(P / c5) if c5 else None, "tpt_over_frozen": float(P / fr) if fr else None,
                   "c5t_over_frozen": float(c5 / fr) if fr else None,
                   "riemann64_gap_over_P": float((pr64 - P) / P) if P else None,
                   "riemann256_gap_over_P": float((pr256 - P) / P) if P else None,
                   "rad_mid_over_rad_whole": float(rad_tot[0] / rad_tot[1]) if rad_tot[1] else None},
        "Gamma": {x: dec(v) for x, v in G.items()},
        "Gamma_delta": {"c5t_minus_tpt": dec(c5 - P), "frozen_minus_tpt": dec(fr - P), "frozen_minus_c5t": dec(fr - c5),
                        "c5t_minus_tpt_over_abs_g_hi": float((c5 - P) / abs(g_hi)) if g_hi else None},
        "direct_pass": {x: bool(v < 0) for x, v in G.items()},
        "H_TC_lo_positive": H_TC[0] > 0,
        "radius_breakdown": breakdown,
        "checks": checks,
        "_exact": {"P": P, "c5": c5, "fr": fr, "g_hi": g_hi, "pr64": pr64},
    })
    return out


# ------------------------------------------------------------------ non-target probes of tpt.py properties

def probe_guard_coverage(rec: dict, aud_km: dict, cons_km: dict, k: int, m: int) -> dict:
    """Does every public tpt entry point call ov_quarantine.guard_cell? Counted on a NON-target profile."""
    guard(m, k)
    A = {x: Fr(aud_km["A"][x]) for x in ("A0", "A1", "A2")}
    wc = T.whole_cell(rec, A, m)
    cp = build_profile(rec, wc, k, m, A, Fr(0), None)
    calls = [0]
    orig = tpt.Q.guard_cell

    def counting(*a, **kw):
        calls[0] += 1
        return orig(*a, **kw)

    res = {}
    tpt.Q.guard_cell = counting
    try:
        for name, fn in (("lo_hi_polys", lambda: tpt.lo_hi_polys(cp)),
                         ("rad_poly", lambda: tpt.rad_poly(cp, cp.terms[0])),
                         ("whole_cell_enclosure", lambda: tpt.whole_cell_enclosure(cp)),
                         ("penalty_closed", lambda: tpt.penalty_closed(cp)),
                         ("penalty_c5t", lambda: tpt.penalty_c5t(cp))):
            calls[0] = 0
            fn()
            res[name] = calls[0]
    finally:
        tpt.Q.guard_cell = orig
    return {"cell": k, "m": m, "guard_calls_per_entry_point": res,
            "unguarded_entry_points": sorted(n for n, c in res.items() if c == 0)}


def probe_m_binding(rec: dict, aud: dict, k: int) -> dict:
    """tpt weights sources by 1/len(terms) and guards on the label cp.m: are they bound together?
    Non-target probe: an m=5 term list labelled m=3 on cell k (both labels are allowed for this cell)."""
    guard(5, k)
    guard(3, k)
    A = {x: Fr(aud[5]["A"][x]) for x in ("A0", "A1", "A2")}
    wc5 = T.whole_cell(rec, A, 5)
    cp = build_profile(rec, wc5, k, 3, A, Fr(0), None)      # label m=3, five m=5 source terms
    try:
        H = tpt.whole_cell_enclosure(cp)
        tpt.penalty_closed(cp)                                # guard sees label m=3 only
        accepted = True
        note = (f"accepted: label m={cp.m}, len(terms)={len(cp.terms)}; the computed enclosure is the m=5 "
                f"enclosure (weights 1/len(terms)): {H == wc5['H']}")
    except Exception as exc:  # noqa: BLE001
        accepted, note = False, f"refused: {exc!r}"
    return {"cell": k, "label_m": 3, "terms": 5, "accepted_without_error": accepted, "note": note}


def probe_split_side() -> dict:
    """_crossing returns the bisection MIDPOINT, which can lie past the true crossing. Synthetic profile (detector
    'SYNTH', no CUSUM cell) with the cap crossing at s* = rho 2^-70, below the 60-step bisection resolution."""
    rho, e0 = Fr(1, 100), Fr(1, 2)
    s_star = rho / Fr(2) ** 70
    st = tpt.SourceTerm(H_at_a=(Fr(-1), Fr(-1)), abs_G_at_a=Fr(0), fF=Fr(0), fD=Fr(0), fH=Fr(0), fG=Fr(1),
                        Env4=Fr(0))
    # A0 = 1, A1 = A2 = 0  ->  lo(s) = -1 - s, hi(s) = -1 + s;  cap.lo = lo(s*) so the cap binds on (s*, rho]
    cp = tpt.CellProfile(detector="SYNTH", m=1, cell=0, e0=e0, rho=rho, g_hi=Fr(0), A0=Fr(1), A1=Fr(0), A2=Fr(0),
                         terms=[st], H_K1=(Fr(-1) - s_star, Fr(10)), label="split-side probe")
    pc = tpt.penalty_closed(cp)
    c5 = tpt.penalty_c5t(cp)
    # exact P* for this profile: int_0^s* (e0+s)(1+s) ds + int_s*^rho (e0+s)(1+s*) ds
    def F1(a, b):
        return (e0 * (b - a) + (e0 + 1) * (b ** 2 - a ** 2) / 2 + (b ** 3 - a ** 3) / 3)

    exact = F1(Fr(0), s_star) + (1 + s_star) * (e0 * (rho - s_star) + (rho ** 2 - s_star ** 2) / 2)
    try:
        tpt.evaluate(cp)
        raised = None
    except AssertionError as exc:
        raised = str(exc)
    return {"split_right": dec(pc["split_right"]) if pc["split_right"] is not None else None,
            "true_crossing": dec(s_star), "split_past_crossing": pc["split_right"] > s_star,
            "P_closed_minus_exact": dec(pc["P_star"] - exact), "P_closed_minus_P_c5t": dec(pc["P_star"] - c5),
            "exact_le_c5t": exact <= c5, "closed_sound_upper_bound": pc["P_star"] >= exact,
            "dominance_P_closed_le_P_c5t": pc["P_star"] <= c5, "evaluate_raised": raised}


def self_scan() -> dict:
    files = sorted(q for q in HERE.glob("*.py"))
    findings = []
    for q in files:
        findings.extend(Q._scan_file(q))
    return {"files_scanned": [q.name for q in files], "findings": findings, "verdict": "PASS" if not findings else "FINDINGS"}


def dist(xs: list) -> dict:
    xs = [x for x in xs if x is not None]
    if not xs:
        return {"n": 0}
    return {"n": len(xs), "min": min(xs), "median": statistics.median(xs), "max": max(xs),
            "mean": statistics.fmean(xs)}


def main() -> None:
    status = {"ok": False, "note": "started"}
    try:
        _main(status)
    finally:
        Q.log_execution("streams/E_assembly/v3/tpt_v3_lower_front.py",
                        "TPT V3: TC reproduction gate + TPT/C5-T/frozen penalties on real non-target lower-front cells",
                        cells_touched=[{"detector": DETECTOR, "m": m, "cell": k} for k in CELLS for m in MS],
                        klass="NONTARGET_REAL_VALIDATION",
                        notes=("completed; " if status["ok"] else "FAILED before completion; ") + status["note"]
                        + "; also one SYNTH (non-cell) split-side probe")


def _main(status: dict) -> None:
    t0 = time.time()
    recs, cons, audit, meta, files = load_inputs()
    results = []
    for k in CELLS:
        for m in MS:
            results.append(evaluate_pair(recs[k], cons[m][k], audit[k][m], k, m))
    passed = [r for r in results if r["gate"]["pass"]]
    failed = [r for r in results if not r["gate"]["pass"]]
    probes = {"guard_coverage": probe_guard_coverage(recs[11], audit[11][5], cons[5][11], 11, 5),
              "m_label_vs_terms": probe_m_binding(recs[11], audit[11], 11),
              "split_point_side": probe_split_side()}
    ck_names = [n for n in passed[0]["checks"] if n != "evaluate_raised"] if passed else []
    check_counts = {n: sum(1 for r in passed if r["checks"][n] is True) for n in ck_names}
    by_m = {}
    for m in MS:
        rm = [r for r in passed if r["m"] == m]
        by_m[str(m)] = {
            "pairs": len(rm),
            "tpt_over_c5t": dist([r["ratios"]["tpt_over_c5t"] for r in rm]),
            "tpt_over_frozen": dist([r["ratios"]["tpt_over_frozen"] for r in rm]),
            "c5t_minus_tpt_over_abs_g_hi": dist([r["Gamma_delta"]["c5t_minus_tpt_over_abs_g_hi"] for r in rm]),
            "direct_pass_counts": {x: sum(1 for r in rm if r["direct_pass"][x]) for x in ("frozen", "c5t", "tpt")},
        }
    flips = [{"cell": r["cell"], "m": r["m"], "frozen": r["direct_pass"]["frozen"], "c5t": r["direct_pass"]["c5t"],
              "tpt": r["direct_pass"]["tpt"]} for r in passed
             if len({r["direct_pass"]["frozen"], r["direct_pass"]["c5t"], r["direct_pass"]["tpt"]}) > 1]
    dC = [r["_exact"]["c5"] - r["_exact"]["P"] for r in passed]
    dF = [r["_exact"]["fr"] - r["_exact"]["P"] for r in passed]
    summary = {
        "pairs_total": len(results), "cells": [CELLS[0], CELLS[-1]], "m_values": list(MS),
        "reproduction_gate": {"evaluated": len(results), "passed": len(passed), "failed": len(failed),
                              "failures": [{"cell": r["cell"], "m": r["m"], **r["gate"]} for r in failed]},
        "gated_out_pairs": len(failed), "tpt_evaluated_pairs": len(passed),
        "check_counts_true": check_counts,
        "evaluate_raised_count": sum(1 for r in passed if r["checks"]["evaluate_raised"]),
        "tpt_over_c5t_all": dist([r["ratios"]["tpt_over_c5t"] for r in passed]),
        "tpt_over_frozen_all": dist([r["ratios"]["tpt_over_frozen"] for r in passed]),
        "c5t_over_frozen_all": dist([r["ratios"]["c5t_over_frozen"] for r in passed]),
        "riemann64_rel_gap": dist([r["ratios"]["riemann64_gap_over_P"] for r in passed]),
        "riemann256_rel_gap": dist([r["ratios"]["riemann256_gap_over_P"] for r in passed]),
        "rad_mid_over_rad_whole": dist([r["ratios"]["rad_mid_over_rad_whole"] for r in passed]),
        "radius_breakdown": {x: dist([r["radius_breakdown"][x] for r in passed])
                             for x in (passed[0]["radius_breakdown"] if passed else {})},
        "Gamma_change_c5t_minus_tpt": {"min": dec(min(dC)), "max": dec(max(dC))} if dC else None,
        "Gamma_change_frozen_minus_tpt": {"min": dec(min(dF)), "max": dec(max(dF))} if dF else None,
        "c5t_minus_tpt_over_abs_g_hi": dist([r["Gamma_delta"]["c5t_minus_tpt_over_abs_g_hi"] for r in passed]),
        "attaining_side_counts": {s: sum(1 for r in passed if r["attaining_side"] == s) for s in ("left", "right", "none")},
        "H_TC_lo_positive_count": sum(1 for r in passed if r["H_TC_lo_positive"]),
        "g_hi_negative_count": sum(1 for r in passed if r["_exact"]["g_hi"] < 0),
        "via_consumed_counts": {v: sum(1 for r in passed if r["via_consumed"] == v) for v in
                                sorted({r["via_consumed"] for r in passed})},
        "direct_pass_counts": {x: sum(1 for r in passed if r["direct_pass"][x]) for x in ("frozen", "c5t", "tpt", "riemann64")},
        "direct_status_flips": flips,
        "by_m": by_m,
    }
    for r in results:
        r.pop("_exact", None)
    doc = {
        "schema": "OV_TPT_V3_LOWER_FRONT/1",
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "class": "NONTARGET_REAL_VALIDATION",
        "quarantine": {"detector": DETECTOR, "allowed_cells": [CELLS[0], CELLS[-1]], "m_values": list(MS),
                       "guard_cell_calls": _guard_calls[0], "target_cells_evaluated": 0,
                       "import_guard_installed": True, "consumption_restricted_to_allowed_cells_on_load": True,
                       "self_scan_v3": self_scan()},
        "inputs": {"files_sha256": files, "consumption_meta": meta,
                   "code_under_test": {"tpt.py": sha_bytes((HERE.parent / "tpt.py").read_bytes())},
                   "own_code": {q.name: sha_bytes(q.read_bytes()) for q in sorted(HERE.glob("*.py"))}},
        "method": {
            "gate": "tc_reder.whole_cell (independent, from THEOREM_TC.md 2-3) == tc_audit[cell][m]['H_TC'] exactly",
            "g_hi": "hi(R - e0 D) = R.hi - e0 * D.lo from the consumed R, D (K5_GLOBAL_BRIDGE.md, frozen k5b_literal)",
            "H_K1": ("K1-only R2_interval is NOT in the allowed data (tc_r1 records carry no R2_interval; the consumption "
                     "stores only H_final = H_prior cap H_TC). Variant A: H_K1 = None. Variant B: H_K1 := H_final (a "
                     "certified whole-cell enclosure). Since H_final == H_TC on both sides for every pair, H_prior never "
                     "binds, and max(H_prior.lo, lo(s)) = lo(s) because lo(s) >= lo(rho) = H_TC.lo >= H_prior.lo: "
                     "variant A equals the TPT bound with the true prior cap exactly."),
            "P_frozen": "rho * x_hi * mag(whole-cell H) (tpt) and rho * x_hi * M_consumed (as consumed); compared",
            "independent_P": "exact closed-form integrals of the independently built profile polynomials (no cap) and "
                             "a Riemann LOWER sum (N=64) bracketing P* from below",
        },
        "summary": summary,
        "probes_tpt_py": probes,
        "results": results,
        "wall_s": round(time.time() - t0, 2),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n")
    status["ok"] = True
    status["note"] = f"gate {len(passed)}/{len(results)}"
    print(json.dumps({x: summary[x] for x in ("reproduction_gate", "check_counts_true", "evaluate_raised_count",
                                               "tpt_over_c5t_all", "direct_pass_counts", "direct_status_flips")},
                     indent=1, default=str))
    print(json.dumps(probes, indent=1, default=str))
    print("wrote", OUT, "wall", doc["wall_s"], "s")


if __name__ == "__main__":
    main()
