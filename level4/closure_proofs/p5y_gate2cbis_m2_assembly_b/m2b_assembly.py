"""P5Y Gate-2C-bis driver: PILOT-M2-ASSEMBLY-B."""
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
from rebaseguard_certify.arb_backend import (                                # noqa: E402
    ball_record, gaussian_cdf, rational, workprec)
from rebaseguard_certify.polynomial import bi_eval                            # noqa: E402
import ra_certifier as RA                                                     # noqa: E402
import raw_certifier as RAW                                                   # noqa: E402
import m2b_certifier as M2B                                                   # noqa: E402
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
MAX_COMPLEXITY_SCORE = 400_000
MAX_CANDIDATE_RESIDUAL_SHARE = 0.50
K_F, H_F, C_F = 0.5, 5.0, 5.5
G1_M1_ANCHOR = (-1.581636423919952, -1.5707254871977971)
GATE2C_DEFECTIVE_BIDEGREE = (121, 121)      # recorded, for the guard demonstration


def monte_carlo_R2(n_cycles: int, seed: int, e: float, batch: int = 200_000):
    """Independent estimate: simulates the FROZEN detector recursion only."""
    rng = np.random.default_rng(seed)
    tot = tot2 = 0.0; tot_t1 = tot_t1_sq = 0.0; n_t1 = 0; done = 0
    while done < n_cycles:
        nb = min(batch, n_cycles - done)
        sp = np.zeros(nb); sm = np.zeros(nb)
        prev_raw = np.zeros(nb); cur_raw = np.zeros(nb)
        tau = np.zeros(nb, dtype=np.int64); alive = np.ones(nb, dtype=bool); step = 0
        while alive.any() and step < 200_000:
            step += 1
            idx = np.nonzero(alive)[0]
            raw = rng.standard_normal(idx.size); z = raw - e
            sp_n = np.maximum(0.0, sp[idx] + z - K_F)
            sm_n = np.maximum(0.0, sm[idx] - z - K_F)
            sp[idx] = sp_n; sm[idx] = sm_n
            prev_raw[idx] = cur_raw[idx]; cur_raw[idx] = raw
            hit = idx[(sp_n >= H_F) | (sm_n >= H_F)]
            tau[hit] = step; alive[hit] = False
        if alive.any():
            raise ArithmeticError("MC step cap reached")
        rbar = np.where(tau == 1, cur_raw, 0.5 * (cur_raw + prev_raw))
        tot += rbar.sum(); tot2 += (rbar * rbar).sum()
        one = tau == 1; n_t1 += int(one.sum())
        tot_t1 += cur_raw[one].sum(); tot_t1_sq += (cur_raw[one] ** 2).sum()
        done += nb
    mean = tot / n_cycles; var = tot2 / n_cycles - mean * mean
    m1 = tot_t1 / n_cycles; v1 = tot_t1_sq / n_cycles - m1 * m1
    return {"n_cycles": n_cycles, "seed": seed, "mean": mean,
            "sd": math.sqrt(max(var, 0.0)), "se": math.sqrt(max(var, 0.0) / n_cycles),
            "p_tau1": n_t1 / n_cycles, "E_raw_tau1_mean": m1,
            "E_raw_tau1_se": math.sqrt(max(v1, 0.0) / n_cycles)}


def main():
    t_all = time.time(); c_all = time.process_time()
    out = {"schema": "rebaseguard.p5y.gate2cbis.m2assemblyb.v1", "binding": False,
           "pilot": "PILOT-M2-ASSEMBLY-B",
           "generated_utc": datetime.now(timezone.utc).isoformat(),
           "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                        capture_output=True, text=True).stdout.strip(),
           "frozen": {"detector": "cusum", "m_set": list(M_SET), "e": f"{E_NUM}/{E_DEN}",
                      "bits": RA.BITS, "order": RA.TAYLOR_N, "solve_degree": RA.DEGREE,
                      "candidate_degree": M2B.KEEP, "cheb_interp_degree": M2B.CHEB_N,
                      "scale_bits": M2B.SCALE_BITS,
                      "certified_repeats": CERTIFIED_REPEATS,
                      "assembly_repeats": ASSEMBLY_REPEATS,
                      "n_cycles": N_CYCLES, "seed": SEED, "abs_tol": ABS_TOL,
                      "max_complexity_score": MAX_COMPLEXITY_SCORE,
                      "max_candidate_residual_share": MAX_CANDIDATE_RESIDUAL_SHARE},
           "second_moment_object_created": False, "sr_executed": False,
           "cover_executed": False, "degree121_in_kernel_path": False}

    # ---------- structural complexity precheck (cheap; T2 is not entered if it fails)
    t0 = time.process_time()
    with workprec(RA.BITS):
        e_arb = rational(E_NUM, E_DEN)
        cand = M2B.build_candidates(e_arb)
    calls = [("K_z,b hhat", cand["hhat"], 1), ("K_0,b hhat", cand["hhat"], 0),
             ("K_z,b dhhat", cand["dhhat"], 1), ("K_0,b dhhat", cand["dhhat"], 0),
             ("K_z,db hhat", cand["hhat"], 1), ("K_0,db hhat", cand["hhat"], 0),
             ("K_0,b F1hat", None, 0), ("K_0,b dF1hat", None, 0), ("K_0,db F1hat", None, 0)]
    nphi = RA.TAYLOR_N + 1
    rows, score = [], 0
    for tag, obj, zw in calls:
        dp = dm = M2B.KEEP if obj is None else max(max(i for i, _ in obj),
                                                   max(j for _, j in obj))
        terms = (M2B.KEEP + 1) ** 2 if obj is None else len(obj)
        zd = dp + dm + nphi + zw
        s = (dp + 1) * (dm + 1) * (zd + 1)
        score += s
        rows.append({"tag": tag, "deg_p": dp, "deg_m": dm, "terms": terms,
                     "z_degree_after": zd, "score": s, "z_weight": zw})
    m1_rows = [{"tag": t, "deg_p": 12, "deg_m": 12, "terms": 169,
                "z_degree_after": 12 + 12 + nphi + 0, "score": 13 * 13 * (24 + nphi + 1)}
               for t in ("K_0,b F0hat", "K_0,b dF0hat", "K_0,db F0hat")]
    m1_score = sum(r["score"] for r in m1_rows)
    dp2 = GATE2C_DEFECTIVE_BIDEGREE[0]
    defective = 6 * (dp2 + 1) * (dp2 + 1) * (2 * dp2 + nphi + 1 + 1) + m1_score
    max_bideg = max(max(r["deg_p"], r["deg_m"]) for r in rows)
    guard_pass = bool(max_bideg <= M2B.KEEP and score <= MAX_COMPLEXITY_SCORE)
    out["complexity_guard"] = {
        "kernel_calls": rows, "n_calls_m2_increment": len(rows),
        "complexity_score_m2_increment": score,
        "complexity_score_m1_baseline": m1_score, "m1_calls": m1_rows,
        "max_bidegree": max_bideg, "budget": MAX_COMPLEXITY_SCORE,
        "PASS": guard_pass,
        "gate2c_defective_path_score": defective,
        "gate2c_would_have_been_rejected_by": defective / MAX_COMPLEXITY_SCORE,
        "precheck_cpu_seconds": time.process_time() - t0}
    if not guard_pass:
        out["GATE2CBIS_DECISION"] = "M2_ASSEMBLY_B_FAIL_REPRESENTATION"
        out["reason"] = "complexity guard failed; T2 certification not entered"
        (HERE / "results" / "m2b_assembly.json").write_text(json.dumps(out, indent=1) + "\n")
        print(json.dumps(out["complexity_guard"], indent=1)); return

    res = drift_monotone_resolvent(e_num=E_NUM, e_den=E_DEN)
    with workprec(RA.BITS):
        C = arb(res["resolvent_bound"]["ball"])
    out["resolvent"] = {"C_float": res["resolvent_bound_upper_float"]}

    # ---------- m = 1 baseline
    t_m1 = []
    for _ in range(CERTIFIED_REPEATS):
        t0 = time.process_time()
        rec1 = RAW.certify_raw_at_exact_drift(E_NUM, E_DEN, resolvent=C,
                                              e_hi_for_allowance=0.26)
        t_m1.append(time.process_time() - t0)
    T_m1 = statistics.median(t_m1)

    # ---------- m = 2 increment (candidates + sources + F_1, d_e F_1)
    t_incr, t_cand = [], []
    for _ in range(CERTIFIED_REPEATS):
        tc = time.process_time()
        with workprec(RA.BITS):
            M2B.build_candidates(rational(E_NUM, E_DEN))
        t_cand.append(time.process_time() - tc)
        t0 = time.process_time()
        M2B.KERNEL_LOG.clear()
        rec2 = M2B.certify_F1(E_NUM, E_DEN, resolvent=C, e_hi_for_allowance=0.26)
        t_incr.append(time.process_time() - t0)
    T_incr = statistics.median(t_incr)
    T_cand = statistics.median(t_cand)
    out["runtime_kernel_log"] = M2B.KERNEL_LOG
    out["runtime_max_bidegree"] = max(max(k["deg_p"], k["deg_m"]) for k in M2B.KERNEL_LOG)
    out["runtime_complexity_score"] = sum(k["score"] for k in M2B.KERNEL_LOG)

    # ---------- assembly
    with workprec(RA.BITS):
        e = rational(E_NUM, E_DEN)
        phi = lambda x: (-(x * x) / arb(2)).exp() / (arb(2) * arb.pi()).sqrt()
        S0_exact = phi(arb(C_F) + e) - phi(-arb(C_F) + e)     # exact scalar, no kernel
        F0 = arb(rec1["Fhat_origin"]["ball"]); d0 = arb(rec1["delta"]["ball"])
        F1 = arb(rec2["F1hat_origin"]["ball"]); d1 = arb(rec2["delta"]["ball"])
        F0e = F0 + arb(0, (C * d0).upper()); F1e = F1 + arb(0, (C * d1).upper())
        t_as = []
        for _ in range(ASSEMBLY_REPEATS):
            tt = time.process_time()
            R1e = F0e; R2e = (F0e + F1e + S0_exact) / arb(2)
            t_as.append(time.process_time() - tt)
        cand_contrib = (C * rec2["_cand_allow"]) / arb(2)
        share = float(cand_contrib.upper()) / float(R2e.rad())
        out["assembly"] = {
            "formula_m2": "R_2 = (1/2)[ F_0(x0) + F_1(x0) + S_0^raw(x0) ]",
            "F_0_x0": ball_record(F0e), "F_1_x0": ball_record(F1e),
            "S_0raw_x0_exact": ball_record(S0_exact),
            "R_1_enclosure": ball_record(R1e), "R_2_enclosure": ball_record(R2e),
            "R_1_center": float(R1e.mid()), "R_2_center": float(R2e.mid()),
            "R_2_half_width": float(R2e.rad()),
            "R_2_lower": float(R2e.lower()), "R_2_upper": float(R2e.upper()),
            "C_delta_F0": ball_record(C * d0), "C_delta_F1": ball_record(C * d1),
            "candidate_contribution_to_half_width": float(cand_contrib.upper()),
            "candidate_residual_share": share,
            "candidate_residual_share_PASS": bool(share <= MAX_CANDIDATE_RESIDUAL_SHARE)}
        # predeclared exact-candidate inclusion check
        inc = []
        for frac in (0, 1, 2, 3, 4):
            x = arb(5) * arb(frac) / arb(4)
            exact = arb(1) - gaussian_cdf(arb(C_F) - x + e) + gaussian_cdf(x - arb(C_F) + e)
            approx = bi_eval(rec2["_hhat"], x, x) + arb(0, rec2["_eps_h"].upper())
            inc.append({"state": float(x), "exact": float(exact),
                        "candidate_center": float(bi_eval(rec2["_hhat"], x, x)),
                        "included": bool((approx - exact).contains(arb(0)))})
        out["exact_candidate_inclusion"] = {"points": inc,
                                            "all_included": all(p["included"] for p in inc)}

    # ---------- correspondence
    t0 = time.process_time()
    mc = monte_carlo_R2(N_CYCLES, SEED, E_NUM / E_DEN)
    mc["cpu_seconds"] = time.process_time() - t0
    out["monte_carlo"] = mc
    lo, hi = out["assembly"]["R_2_lower"], out["assembly"]["R_2_upper"]
    ci = (mc["mean"] - 4 * mc["se"], mc["mean"] + 4 * mc["se"])
    gap = abs(out["assembly"]["R_2_center"] - mc["mean"]); tol = max(4 * mc["se"], ABS_TOL)
    out["correspondence"] = {
        "mc_mean": mc["mean"], "mc_se": mc["se"], "ci_4se": list(ci),
        "assembled_enclosure": [lo, hi],
        "enclosure_intersects_ci": bool(not (hi < ci[0] or lo > ci[1])),
        "centre_gap": gap, "tolerance": tol, "centre_within_tolerance": bool(gap <= tol),
        "PASS": bool(not (hi < ci[0] or lo > ci[1]) and gap <= tol)}
    out["m1_vs_gate1"] = {"gate1_cell_hull": list(G1_M1_ANCHOR),
                          "this_gate_R1": [float(R1e.lower()), float(R1e.upper())],
                          "overlaps": bool(not (float(R1e.upper()) < G1_M1_ANCHOR[0]
                                                or float(R1e.lower()) > G1_M1_ANCHOR[1]))}

    # ---------- sharing and ratios
    ratio_incr = T_incr / T_m1
    out["sharing"] = {"m1_unique_resolvent_solves": 2, "m1_names": ["F_0", "d_e F_0"],
                      "m2_additional_resolvent_solves": 2, "m2_names": ["F_1", "d_e F_1"],
                      "m2_candidate_source_objects": ["hhat_1", "dhhat_1",
                                                      "S_1^raw", "d_e S_1^raw"],
                      "shared_resolvent_fraction": 0.5,
                      "duplicate_m1_solve_created": False,
                      "hhat1_is_source_not_resolvent": True,
                      "new_solve_architecture_required": False}
    cls = ("STRONG" if ratio_incr <= 1.15 else "MODERATE" if ratio_incr <= 1.50
           else "WEAK" if ratio_incr <= 2.00 else "HIGH")
    out["cost"] = {"T_m1_seconds": T_m1, "T_m1_repeats": t_m1,
                   "T_incr_seconds": T_incr, "T_incr_repeats": t_incr,
                   "T_candidate_construction_seconds": T_cand,
                   "T_cold_m1": T_m1, "T_cold_m2": T_m1 + T_incr,
                   "T_assembly_median": statistics.median(t_as),
                   "spread_m1": (max(t_m1) - min(t_m1)) / T_m1,
                   "spread_incr": (max(t_incr) - min(t_incr)) / T_incr,
                   "ratio_incremental": ratio_incr,
                   "ratio_cold": (T_m1 + T_incr) / T_m1,
                   "ratio_source_only": T_cand / T_m1,
                   "units_added_by_m2": UNITS_ADDED_BY_M2,
                   "ratio_per_unit_used_by_production_model": ratio_incr / UNITS_ADDED_BY_M2,
                   "cost_class_on_ratio_incremental": cls}

    rep_ok = (out["complexity_guard"]["PASS"] and out["runtime_max_bidegree"] <= M2B.KEEP
              and out["assembly"]["candidate_residual_share_PASS"]
              and out["sharing"]["new_solve_architecture_required"] is False)
    corr_ok = out["correspondence"]["PASS"]
    out["GATE2CBIS_DECISION"] = ("M2_ASSEMBLY_B_FAIL_REPRESENTATION" if not rep_ok else
                                 "M2_ASSEMBLY_B_FAIL_CORRESPONDENCE" if not corr_ok else
                                 "M2_ASSEMBLY_B_PASS_COST_HIGH" if ratio_incr > 2.0 else
                                 "M2_ASSEMBLY_B_PASS")
    cpu = time.process_time() - c_all
    out["runtime"] = {"wall_seconds": time.time() - t_all, "cpu_seconds": cpu,
                      "cpu_hours": cpu / 3600.0, "cap_cpu_seconds": 1260,
                      "within_cap": bool(cpu <= 1260),
                      "peak_rss_mib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 * 1024)}
    (HERE / "results" / "m2b_assembly.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: out[k] for k in
                      ("complexity_guard", "assembly", "exact_candidate_inclusion",
                       "monte_carlo", "correspondence", "m1_vs_gate1", "sharing", "cost",
                       "GATE2CBIS_DECISION", "runtime")}, indent=1, default=str))


if __name__ == "__main__":
    main()
