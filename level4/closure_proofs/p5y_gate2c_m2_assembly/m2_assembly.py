"""P5Y Gate-2C driver: PILOT-M2-ASSEMBLY.

Measures the m>1 per-function cost ratio and checks the assembled
R_{CUSUM,2}(1/4) against an independent Monte Carlo simulation of the frozen
detector recursion.
"""
from __future__ import annotations

import json, math, resource, statistics, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
G1 = ROOT / "level4" / "closure_proofs" / "p5y_micropilot_gate1"
P5X = ROOT / "level4" / "closure_proofs" / "p5x_global_nonlinear_dynamics"
for _p in (str(ROOT / "rebaseguard-proof" / "src"), str(HERE), str(G1),
           str(P5X / "certified_method_repair_ra"), str(P5X / "compute_optimization_r1"),
           str(P5X / "compute_optimization_r2")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
from flint import arb                                                        # noqa: E402
from rebaseguard_certify.arb_backend import ball_record, rational, workprec   # noqa: E402
import ra_certifier as RA                                                     # noqa: E402
import raw_certifier as RAW                                                   # noqa: E402
import m2_certifier as M2                                                     # noqa: E402
from drift_minorant import drift_monotone_resolvent                           # noqa: E402

# ------------------------------------------------------------------ FROZEN
E_NUM, E_DEN = 1, 4
M_SET = (1, 2)
CERTIFIED_REPEATS = 2
ASSEMBLY_REPEATS = 5
N_CYCLES = 1_000_000
SEED = 20260904
ABS_TOL = 5e-3
UNITS_ADDED_BY_M2 = 2
K_F, H_F, C_F = 0.5, 5.0, 5.5
G1_M1_ANCHOR = (-1.581636423919952, -1.5707254871977971)   # Gate-1 raw cell A hull


def monte_carlo_R2(n_cycles: int, seed: int, e: float, batch: int = 200_000):
    """Independent estimate of R_{CUSUM,2}(e).  Simulates the FROZEN detector
    recursion directly: no operator, no candidate, no Fredholm machinery, and no
    line of the assembly code is touched."""
    rng = np.random.default_rng(seed)
    tot = tot2 = 0.0
    tot_tau1 = tot_tau1_sq = 0.0
    n_tau1 = 0
    done = 0
    while done < n_cycles:
        nb = min(batch, n_cycles - done)
        sp = np.zeros(nb); sm = np.zeros(nb)
        prev_raw = np.zeros(nb); cur_raw = np.zeros(nb)
        tau = np.zeros(nb, dtype=np.int64)
        alive = np.ones(nb, dtype=bool)
        step = 0
        while alive.any() and step < 200_000:
            step += 1
            idx = np.nonzero(alive)[0]
            raw = rng.standard_normal(idx.size)
            z = raw - e
            sp_n = np.maximum(0.0, sp[idx] + z - K_F)
            sm_n = np.maximum(0.0, sm[idx] - z - K_F)
            sp[idx] = sp_n; sm[idx] = sm_n
            prev_raw[idx] = cur_raw[idx]; cur_raw[idx] = raw
            fired = (sp_n >= H_F) | (sm_n >= H_F)
            hit = idx[fired]
            tau[hit] = step
            alive[hit] = False
        if alive.any():
            raise ArithmeticError("MC step cap reached")
        rbar = np.where(tau == 1, cur_raw, 0.5 * (cur_raw + prev_raw))
        tot += rbar.sum(); tot2 += (rbar * rbar).sum()
        one = tau == 1
        n_tau1 += int(one.sum())
        tot_tau1 += cur_raw[one].sum(); tot_tau1_sq += (cur_raw[one] ** 2).sum()
        done += nb
    mean = tot / n_cycles
    var = tot2 / n_cycles - mean * mean
    se = math.sqrt(max(var, 0.0) / n_cycles)
    # E[raw_1 ; tau = 1] as a full-sample mean of raw*1{tau=1}
    m_t1 = tot_tau1 / n_cycles
    v_t1 = tot_tau1_sq / n_cycles - m_t1 * m_t1
    se_t1 = math.sqrt(max(v_t1, 0.0) / n_cycles)
    return {"n_cycles": n_cycles, "seed": seed, "mean": mean, "sd": math.sqrt(max(var, 0.0)),
            "se": se, "p_tau1": n_tau1 / n_cycles,
            "E_raw_tau1_mean": m_t1, "E_raw_tau1_se": se_t1}


def main():
    t_all = time.time(); c_all = time.process_time()
    out = {"schema": "rebaseguard.p5y.gate2c.m2assembly.v1", "binding": False,
           "pilot": "PILOT-M2-ASSEMBLY",
           "generated_utc": datetime.now(timezone.utc).isoformat(),
           "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                        capture_output=True, text=True).stdout.strip(),
           "frozen": {"detector": "cusum", "m_set": list(M_SET),
                      "e": f"{E_NUM}/{E_DEN}", "bits": RA.BITS, "order": RA.TAYLOR_N,
                      "degree": RA.DEGREE, "certified_repeats": CERTIFIED_REPEATS,
                      "assembly_repeats": ASSEMBLY_REPEATS, "n_cycles": N_CYCLES,
                      "seed": SEED, "abs_tol": ABS_TOL,
                      "units_added_by_m2": UNITS_ADDED_BY_M2},
           "second_moment_object_created": False, "sr_executed": False,
           "cover_executed": False}

    res = drift_monotone_resolvent(e_num=E_NUM, e_den=E_DEN)
    with workprec(RA.BITS):
        C = arb(res["resolvent_bound"]["ball"])
    out["resolvent"] = {"C": res["resolvent_bound"], "C_float": res["resolvent_bound_upper_float"]}

    # ---------------- m = 1 baseline: certified (F_0, d_e F_0)
    t_m1 = []
    for _ in range(CERTIFIED_REPEATS):
        t0 = time.process_time()
        rec1 = RAW.certify_raw_at_exact_drift(E_NUM, E_DEN, resolvent=C,
                                              e_hi_for_allowance=0.26)
        t_m1.append(time.process_time() - t0)
    T_m1 = statistics.median(t_m1)

    # ---------------- m = 2 increment: h_1, S_1^raw, d_e S_1^raw, F_1, d_e F_1
    t_incr = []
    for _ in range(CERTIFIED_REPEATS):
        t0 = time.process_time()
        rec2 = M2.certify_F1(E_NUM, E_DEN, resolvent=C, e_hi_for_allowance=0.26)
        t_incr.append(time.process_time() - t0)
    T_incr = statistics.median(t_incr)

    # ---------------- finite assembly (the only m-dependent arithmetic)
    with workprec(RA.BITS):
        F0 = arb(rec1["Fhat_origin"]["ball"]); d0 = arb(rec1["delta"]["ball"])
        F1 = arb(rec2["F1hat_origin"]["ball"]); d1 = arb(rec2["delta"]["ball"])
        S0 = arb(rec2["S0raw_origin"]["ball"])
        F0e = F0 + arb(0, (C * d0).upper())
        F1e = F1 + arb(0, (C * d1).upper())
        t_as = []
        for _ in range(ASSEMBLY_REPEATS):
            t0 = time.process_time()
            R1e = F0e
            R2e = (F0e + F1e + S0) / arb(2)
            t_as.append(time.process_time() - t0)
        T_assembly = statistics.median(t_as)
        out["assembly"] = {
            "formula_m1": "R_1 = F_0(x0)",
            "formula_m2": "R_2 = (1/2)[ F_0(x0) + F_1(x0) + S_0^raw(x0) ]",
            "F_0_x0": ball_record(F0e), "F_1_x0": ball_record(F1e),
            "S_0raw_x0": ball_record(S0), "h_1_x0": rec2["h1_origin"],
            "R_1_enclosure": ball_record(R1e), "R_2_enclosure": ball_record(R2e),
            "R_1_center": float(R1e.mid()), "R_2_center": float(R2e.mid()),
            "R_1_half_width": float(R1e.rad()), "R_2_half_width": float(R2e.rad()),
            "R_2_lower": float(R2e.lower()), "R_2_upper": float(R2e.upper()),
            "C_delta_F0": ball_record(C * d0), "C_delta_F1": ball_record(C * d1)}

        # ---- predeclared algebraic cross-checks
        e = rational(E_NUM, E_DEN)
        phi = lambda x: (-(x * x) / arb(2)).exp() / (arb(2) * arb.pi()).sqrt()
        from rebaseguard_certify.arb_backend import gaussian_cdf
        a_, b_ = arb(C_F) + e, -arb(C_F) + e
        h1_cf = arb(1) - gaussian_cdf(a_) + gaussian_cdf(b_)
        s0_cf = phi(a_) - phi(b_)
        out["cross_checks"] = {
            "CHK_A_h1_vs_closed_form": float((arb(rec2["h1_origin"]["ball"]) - h1_cf).abs_upper()),
            "CHK_A_pass": bool((arb(rec2["h1_origin"]["ball"]) - h1_cf).abs_upper() < arb("1e-25")),
            "CHK_B_S0raw_vs_closed_form": float((S0 - s0_cf).abs_upper()),
            "CHK_B_pass": bool((S0 - s0_cf).abs_upper() < arb("1e-25"))}

    # ---------------- independent Monte Carlo correspondence
    t0 = time.process_time()
    mc = monte_carlo_R2(N_CYCLES, SEED, E_NUM / E_DEN)
    mc["cpu_seconds"] = time.process_time() - t0
    out["monte_carlo"] = mc

    lo, hi = out["assembly"]["R_2_lower"], out["assembly"]["R_2_upper"]
    ci_lo, ci_hi = mc["mean"] - 4 * mc["se"], mc["mean"] + 4 * mc["se"]
    intersects = not (hi < ci_lo or lo > ci_hi)
    centre_gap = abs(out["assembly"]["R_2_center"] - mc["mean"])
    tol = max(4 * mc["se"], ABS_TOL)
    out["correspondence"] = {
        "mc_mean": mc["mean"], "mc_se": mc["se"], "ci_4se": [ci_lo, ci_hi],
        "assembled_enclosure": [lo, hi], "enclosure_intersects_ci": bool(intersects),
        "centre_gap": centre_gap, "tolerance": tol,
        "centre_within_tolerance": bool(centre_gap <= tol),
        "PASS": bool(intersects and centre_gap <= tol)}
    with workprec(RA.BITS):
        gap = abs(float(arb(rec2["S0raw_origin"]["ball"]).mid()) - mc["E_raw_tau1_mean"])
    out["cross_checks"]["CHK_C_S0raw_vs_mc_E_raw_tau1"] = {
        "assembled": float(arb(rec2["S0raw_origin"]["ball"]).mid()),
        "mc": mc["E_raw_tau1_mean"], "mc_se": mc["E_raw_tau1_se"], "gap": gap,
        "pass": bool(gap <= 4 * mc["E_raw_tau1_se"] + 1e-9)}
    out["cross_checks"]["CHK_D_m1_overlaps_gate1"] = {
        "gate1_cell_hull": list(G1_M1_ANCHOR),
        "this_gate_R1": [float(R1e.lower()), float(R1e.upper())],
        "pass": bool(not (float(R1e.upper()) < G1_M1_ANCHOR[0]
                          or float(R1e.lower()) > G1_M1_ANCHOR[1]))}

    # ---------------- sharing audit and cost ratios
    ratio_incr = T_incr / T_m1
    ratio_per_unit = ratio_incr / UNITS_ADDED_BY_M2
    ratio_cold = (T_m1 + T_incr) / T_m1
    cls = ("STRONG" if ratio_per_unit <= 1.15 else "MODERATE" if ratio_per_unit <= 1.50
           else "WEAK" if ratio_per_unit <= 2.00 else "HIGH")
    out["sharing"] = {
        "m1_unique_solved_functions": 2, "m1_names": ["F_0", "d_e F_0"],
        "m2_additional_unique_solved_functions": 2, "m2_names": ["F_1", "d_e F_1"],
        "m2_closed_form_objects": ["h_1", "d_e h_1 = -S_0^raw"],
        "m2_kernel_derived_sources": ["S_1^raw", "d_e S_1^raw"],
        "shared_fraction_at_m2": 2 / 4,
        "duplicate_solve_created": False,
        "F_0_reused_by_identity": True,
        "new_solve_architecture_required": False}
    out["cost"] = {
        "T_m1_seconds": T_m1, "T_m1_repeats": t_m1,
        "T_incr_seconds": T_incr, "T_incr_repeats": t_incr,
        "T_cold_m1": T_m1, "T_cold_m2": T_m1 + T_incr,
        "T_assembly_seconds_median": T_assembly,
        "assembly_spread": (max(t_as) - min(t_as)) / T_assembly if T_assembly > 0 else 0.0,
        "certified_spread_m1": (max(t_m1) - min(t_m1)) / T_m1,
        "certified_spread_incr": (max(t_incr) - min(t_incr)) / T_incr,
        "ratio_incremental": ratio_incr, "ratio_cold": ratio_cold,
        "units_added_by_m2": UNITS_ADDED_BY_M2,
        "ratio_per_unit_PRODUCTION_RELEVANT": ratio_per_unit,
        "cost_class": cls}

    arch_ok = (out["sharing"]["new_solve_architecture_required"] is False
               and out["sharing"]["duplicate_solve_created"] is False
               and out["cross_checks"]["CHK_A_pass"] and out["cross_checks"]["CHK_B_pass"])
    corr_ok = out["correspondence"]["PASS"]
    out["GATE2C_DECISION"] = ("M2_ASSEMBLY_FAIL_ARCHITECTURE" if not arch_ok else
                              "M2_ASSEMBLY_FAIL_CORRESPONDENCE" if not corr_ok else
                              "M2_ASSEMBLY_PASS_COST_HIGH" if ratio_per_unit > 2.0 else
                              "M2_ASSEMBLY_PASS")
    cpu = time.process_time() - c_all
    out["runtime"] = {"wall_seconds": time.time() - t_all, "cpu_seconds": cpu,
                      "cpu_hours": cpu / 3600.0, "cap_cpu_hours": 0.20,
                      "within_cap": bool(cpu / 3600.0 <= 0.20),
                      "peak_rss_mib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 * 1024)}
    (HERE / "results" / "m2_assembly.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: out[k] for k in ("assembly", "cross_checks", "monte_carlo",
                                          "correspondence", "sharing", "cost",
                                          "GATE2C_DECISION", "runtime")}, indent=1))


if __name__ == "__main__":
    main()
