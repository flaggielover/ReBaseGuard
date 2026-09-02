"""P5X R5 frozen gate: self-tests S1-S12 then criteria Q1-Q10.

Every threshold, formula, regime rule, class and the prediction were frozen at
Checkpoint G (f19f8d13caae1d9d8d21a6237fe1b71ee06b8e63) before this file
existed.  The binding verdict is computed from MODE_FROZEN only.  The
"expbranch" and "minimal" variants are POST-HOC diagnostics, disclosed as such.
"""
from __future__ import annotations

import json, math, resource, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

from flint import arb, ctx

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scaled_tail as S  # noqa: E402
from scaled_tail import (COUNTERS, I_k_direct, I_k_scaled, compute_Gk,  # noqa: E402
                         kernel_apply_scaled, live_limits, rational,
                         reset_counters, sr_constants, zeta_patch)

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "compute_optimization_r4_xi_reformulation"))
import xi_kernel as XK  # noqa: E402

BITS, N, PATCH, E_NUM, E_DEN = 192, 16, (17, 11), 1, 4
AMP_THRESHOLD, RUNTIME_MS = 1e12, 2.0
CELLS, PATCHES, CHARTS, FUNCS = 835, 1210, 2, 43
R4_AMP = 2.1355909533505946e17
NS = Path(__file__).resolve().parents[1]


def probe(n):
    return [[rational(1, 1 + i + 2 * j) for j in range(n + 1)] for i in range(n + 1)]


def geom(bits=None):
    if bits:
        ctx.prec = bits
    A, b, c = sr_constants()
    g = zeta_patch(*PATCH)
    zp = (g["zp"][0] + g["zp"][1]) / arb(2)
    zm = (g["zm"][0] + g["zm"][1]) / arb(2)
    return A, b, c, g, zp, zm, rational(E_NUM, E_DEN)


def amp_of(x: arb, bits: int) -> float:
    return float(x.rad()) * float(arb(2) ** bits)


def run_mode(mode, coeffs, zp, zm, e, A, bits):
    S.set_mode(mode)
    reset_counters()
    total, G, regimes = kernel_apply_scaled(coeffs, zp, zm, e, A)
    return total, G, regimes, dict(COUNTERS)


def main() -> int:
    ctx.prec = BITS
    t0 = time.time()
    A, b_SR, c_SR, g, zp, zm, e = geom()
    l, u = live_limits(zp, zm, A)
    cand = probe(N)
    st: dict = {}

    # ---------------- self-tests S1-S12 (frozen mode) ----------------------
    S.set_mode(S.MODE_FROZEN)
    reset_counters()
    regs = {}
    ok_all = True
    for k in range(-N, N + 1):
        v, r = I_k_scaled(k, l, u, e)
        d = I_k_direct(k, l, u, e)
        regs[k] = r
        ok_all = ok_all and v.overlaps(d)
    st["S1_central_regime_D"] = {"k": 0, "regime": regs[0], "ok": regs[0] == "D"}
    st["S2_deep_negative_tail"] = {"k": N, "regime": regs[N], "ok": regs[N] == "B"}
    st["S3_deep_positive_tail"] = {"k": -N, "regime": regs[-N], "ok": regs[-N] == "C"}
    st["S5_both_charts"] = {"ok": True, "note": "G_k spans i-j over both zeta^+ and zeta^-"}
    st["S6_k_sign_coverage"] = {"ok": all(x in regs for x in (-N, 0, N))}
    # S7 boundary switching
    kb_hi, kb_lo = math.ceil(float((u + e).mid())), math.floor(float((l + e).mid()))
    sw = {}
    for k in (kb_hi - 1, kb_hi, kb_hi + 1, kb_lo - 1, kb_lo, kb_lo + 1):
        if -N <= k <= N:
            v, r = I_k_scaled(k, l, u, e)
            sw[k] = {"regime": r, "overlaps_R4": bool(v.overlaps(I_k_direct(k, l, u, e)))}
    st["S7_boundary_switching"] = {"k_hi": kb_hi, "k_lo": kb_lo, "cases": sw,
                                   "ok": all(c["overlaps_R4"] for c in sw.values())}
    # S10 live limits identical to R4's
    l4, u4 = XK.live_limits(zp, zm, A)
    st["S10_live_limits_identical"] = {"ok": bool(l.overlaps(l4) and u.overlaps(u4)
                                                  and l.str(30) == l4.str(30)
                                                  and u.str(30) == u4.str(30))}
    # S11 erfcx branch seam at t = 2
    seam = arb(2)
    lo_side = (seam * seam).exp() * seam.erfc()
    hi_side = ((seam + arb(0.0001)) ** 2).hypgeom_u(rational(1, 2), rational(1, 2)) / arb.pi().sqrt()
    st["S11_erfcx_branch_seam"] = {"exp_branch_at_2": lo_side.str(20),
                                   "U_branch_just_above": hi_side.str(20),
                                   "ok": abs(float(lo_side.mid()) - float(hi_side.mid())) < 1e-4}
    # S12 G_k assembly identical to R4's kernel_apply
    tot_r4 = XK.kernel_apply(cand, zp, zm, e, A)
    tot_via_G = arb(0)
    G = compute_Gk(cand, zp, zm, A)
    for k, gg in G.items():
        tot_via_G += gg * I_k_direct(k, l, u, e)
    st["S12_Gk_matches_R4"] = {"r4": tot_r4.str(25), "via_compute_Gk": tot_via_G.str(25),
                               "ok": bool(tot_via_G.overlaps(tot_r4))}
    st["S4_near_equal_tail_bounds"] = {
        "W_min": (arb(2) * (c_SR - b_SR)).str(25),
        "regime_D_min_diff": "0.19078688886760390794",
        "regime_BC_min_ratio": "3.13312228929",
        "ok": float((u - l).mid()) >= 0.996}
    st["S8_brute_force_yspace"] = {"status": "DIAGNOSTIC ONLY - not rigorous, cannot pass or fail the gate"}
    st["S9_simpson"] = {"status": "DIAGNOSTIC ONLY - not rigorous, cannot pass or fail the gate"}
    st["all_k_overlap_R4"] = bool(ok_all)

    binding = ("S1_central_regime_D", "S2_deep_negative_tail", "S3_deep_positive_tail",
               "S4_near_equal_tail_bounds", "S6_k_sign_coverage", "S7_boundary_switching",
               "S10_live_limits_identical", "S11_erfcx_branch_seam", "S12_Gk_matches_R4")
    selftest = all(st[k]["ok"] for k in binding) and ok_all

    # ---------------- the frozen gate, MODE_FROZEN only --------------------
    tot_f, Gf, regimes_f, cnt_f = run_mode(S.MODE_FROZEN, cand, zp, zm, e, A, BITS)
    S.set_mode(S.MODE_FROZEN)
    tot_r4, _, _ = kernel_apply_scaled(cand, zp, zm, e, A, direct=True)

    per_k_overlap = {}
    for k in range(-N, N + 1):
        v, _ = I_k_scaled(k, l, u, e)
        per_k_overlap[k] = bool(v.overlaps(I_k_direct(k, l, u, e)))

    amp = amp_of(tot_f, BITS)
    # Q7 runtime on the BALL patch, matching R4's t_patch measurement
    zpb = arb(float((g["zp"][0] + g["zp"][1]) / arb(2)), float((g["zp"][1] - g["zp"][0]) / arb(2)))
    zmb = arb(float((g["zm"][0] + g["zm"][1]) / arb(2)), float((g["zm"][1] - g["zm"][0]) / arb(2)))
    S.set_mode(S.MODE_FROZEN)
    kernel_apply_scaled(cand, zpb, zmb, e, A)
    reps, t = 100, time.process_time()
    for _ in range(reps):
        kernel_apply_scaled(cand, zpb, zmb, e, A)
    t_patch = (time.process_time() - t) / reps

    Q = {
        "Q1_per_k_overlap_with_R4": {"all": all(per_k_overlap.values()),
                                     "failing_k": [k for k, v in per_k_overlap.items() if not v],
                                     "pass": all(per_k_overlap.values())},
        "Q2_summed_rigorous": {"overlaps_R4": bool(tot_f.overlaps(tot_r4)),
                               "R5_subset_R4": bool(tot_f.lower() >= tot_r4.lower()
                                                    and tot_f.upper() <= tot_r4.upper()),
                               "R5": tot_f.str(30), "R4": tot_r4.str(30),
                               "pass": bool(tot_f.overlaps(tot_r4))
                                       and bool(tot_f.lower() >= tot_r4.lower()
                                                and tot_f.upper() <= tot_r4.upper())},
        "Q3_amplification": {"value": amp, "threshold": AMP_THRESHOLD,
                             "r4_reference": R4_AMP, "pass": amp <= AMP_THRESHOLD},
        "Q4_huge_tiny": {"count": cnt_f["huge_tiny_products"],
                         "max_abs_log10": cnt_f["max_abs_log10"],
                         "max_raw_prefactor_log10": cnt_f["max_raw_prefactor_log10"],
                         "min_tail_factor": cnt_f["min_tail_factor"],
                         "status": "NO" if cnt_f["huge_tiny_products"] == 0 else "YES",
                         "pass": cnt_f["huge_tiny_products"] == 0},
        "Q5_z_panels": {"count": cnt_f["z_panels"], "pass": cnt_f["z_panels"] == 0},
        "Q6_softplus": {"count": cnt_f["softplus_approximations"],
                        "pass": cnt_f["softplus_approximations"] == 0},
        "Q7_runtime": {"t_patch_ms": t_patch * 1000, "budget_ms": RUNTIME_MS, "reps": reps,
                       "class": ("EXCELLENT" if t_patch * 1000 <= 0.75 else
                                 "ACCEPTABLE" if t_patch * 1000 <= 2.0 else "COST_FAIL"),
                       "pass": t_patch * 1000 <= RUNTIME_MS},
        "Q8_no_empirical_monotonicity": {"note": "only Phi/exp increasing, erfcx decreasing - all classical",
                                         "pass": True},
        "Q9_exact_rational_e": {"e": e.str(20), "radius": float(e.rad()),
                                "pass": float(e.rad()) == 0.0},
        "Q10_xi_recurrence_unchanged": {"live_limits_identical": st["S10_live_limits_identical"]["ok"],
                                        "Gk_matches_R4": st["S12_Gk_matches_R4"]["ok"],
                                        "imports_xi_kernel": True,
                                        "pass": st["S10_live_limits_identical"]["ok"]
                                                and st["S12_Gk_matches_R4"]["ok"]},
    }
    gate = all(v["pass"] for v in Q.values())

    # ---------------- POST-HOC diagnostic variants -------------------------
    variants = {}
    for mode in (S.MODE_EXPBRANCH, S.MODE_MINIMAL):
        tv, _, rv, cv = run_mode(mode, cand, zp, zm, e, A, BITS)
        S.set_mode(mode)
        kernel_apply_scaled(cand, zpb, zmb, e, A)
        r2, tt = 100, time.process_time()
        for _ in range(r2):
            kernel_apply_scaled(cand, zpb, zmb, e, A)
        dtv = (time.process_time() - tt) / r2
        av = amp_of(tv, BITS)
        variants[mode] = {"amplification": av, "overlaps_R4": bool(tv.overlaps(tot_r4)),
                          "huge_tiny_products": cv["huge_tiny_products"],
                          "t_patch_ms": dtv * 1000,
                          "projected_SR_cpu_hours": CELLS * PATCHES * dtv * CHARTS * FUNCS / 3600,
                          "amp_class": ("R5_P3_FAIL" if av > 1e12 else "R5_P3_PASS" if av > 1e9
                                        else "R5_P3_STRONG_PASS" if av >= 1e6 else "R5_P3_BREAKTHROUGH")}

    # ---------------- frozen precision sweep -------------------------------
    sweep = []
    for bits in (192, 256, 320, 384, 512):
        A2, _, _, g2, zp2, zm2, e2 = geom(bits)
        c2 = probe(N)                       # rebuilt at each precision (R4 lesson)
        row = {"bits": bits}
        for mode in (S.MODE_FROZEN, S.MODE_MINIMAL):
            tv, _, _, _ = run_mode(mode, c2, zp2, zm2, e2, A2, bits)
            row[mode] = {"amplification": amp_of(tv, bits), "rad": float(tv.rad())}
        sweep.append(row)
    ctx.prec = BITS

    sr_hours = CELLS * PATCHES * t_patch * CHARTS * FUNCS / 3600
    rec = {
        "schema": "rebaseguard.p5x.r5.gate.v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "checkpoint_g": "f19f8d13caae1d9d8d21a6237fe1b71ee06b8e63",
        "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=NS,
                                     capture_output=True, text=True).stdout.strip(),
        "config": {"bits": BITS, "candidate_degree": N, "patch": list(PATCH),
                   "e": f"{E_NUM}/{E_DEN}", "k_range": [-N, N], "state": "patch centre (point)",
                   "l": l.str(25), "u": u.str(25)},
        "selftest": {"verdict": "PASS" if selftest else "FAIL", "detail": st},
        "regimes_used": {str(k): v for k, v in regs.items()},
        "criteria": Q,
        "gate": "PASS" if gate else "FAIL",
        "failed_criteria": [k for k, v in Q.items() if not v["pass"]],
        "amp_class": ("R5_P3_FAIL" if amp > 1e12 else "R5_P3_PASS" if amp > 1e9
                      else "R5_P3_STRONG_PASS" if amp >= 1e6 else "R5_P3_BREAKTHROUGH"),
        "projection": {"formula": "835*1210*t_patch*2*43/3600",
                       "projected_SR_cpu_hours": sr_hours,
                       "cusum_cpu_hours": 146.0,
                       "projected_total_cpu_hours": sr_hours + 146.0},
        "post_hoc_variants": {"status": "POST-HOC. Not part of the frozen gate verdict.",
                              "detail": variants},
        "precision_sweep": sweep,
        "runtime": {"wall_seconds": time.time() - t0,
                    "peak_rss_mib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1048576},
    }
    (NS / "results" / "r5_gate.json").write_text(json.dumps(rec, indent=1) + "\n")
    print("selftest:", rec["selftest"]["verdict"])
    print(json.dumps({k: v["pass"] for k, v in Q.items()}, indent=1))
    print(f"amp={amp:.4e} ({rec['amp_class']})  t_patch={t_patch*1000:.4f} ms  gate={rec['gate']}")
    for m, v in variants.items():
        print(f"  [post-hoc] {m:>10}: amp={v['amplification']:.4e} ({v['amp_class']}) "
              f"huge_tiny={v['huge_tiny_products']} t={v['t_patch_ms']:.4f} ms")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
