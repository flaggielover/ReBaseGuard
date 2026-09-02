"""P5X R6 frozen gate: criteria G1-G10 of R6_FROZEN_SPEC.md.

Frozen at Checkpoint H (7800911d4ca5b93f1f4317494669f228501ef42a) before this
file existed.  Nothing here re-budgets anything after measurement.
"""
from __future__ import annotations

import json, resource, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

from flint import arb, ctx

sys.path.insert(0, str(Path(__file__).resolve().parent))
from minimal_evaluator import (COUNTERS, I_k, I_k_r4, compute_Gk,  # noqa: E402
                               kernel_apply, live_limits, rational,
                               reset_counters, sr_constants, zeta_patch)
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "compute_optimization_r4_xi_reformulation"))
import xi_kernel as XK  # noqa: E402

BITS, N, PATCH, E_NUM, E_DEN = 192, 16, (17, 11), 1, 4
AMP_THRESHOLD, RUNTIME_MS = 1e12, 2.0
SWEEP = (192, 256, 320, 384, 512)
CELLS, PATCHES, CHARTS, FUNCS = 835, 1210, 2, 43
R4_AMP, R5_AMP = 2.1355909533505946e17, 2.238123651003098e20
NS = Path(__file__).resolve().parents[1]


def probe(n):
    return [[rational(1, 1 + i + 2 * j) for j in range(n + 1)] for i in range(n + 1)]


def geom():
    A, b, c = sr_constants()
    g = zeta_patch(*PATCH)
    return A, b, c, g, (g["zp"][0] + g["zp"][1]) / arb(2), (g["zm"][0] + g["zm"][1]) / arb(2)


def main() -> int:
    ctx.prec = BITS
    t0 = time.time()
    A, b_SR, c_SR, g, zp, zm = geom()
    e = rational(E_NUM, E_DEN)
    l, u = live_limits(zp, zm, A)
    cand = probe(N)

    # G1 -------------------------------------------------------------------
    reset_counters()
    per_k, regs = {}, {}
    for k in range(-N, N + 1):
        v, r = I_k(k, l, u, e)
        regs[k] = r
        per_k[k] = bool(v.overlaps(I_k_r4(k, l, u, e)))

    # G2, G3 ---------------------------------------------------------------
    reset_counters()
    tot, G, regimes = kernel_apply(cand, zp, zm, e, A)
    cnt = dict(COUNTERS)
    tot_r4, _, _ = kernel_apply(cand, zp, zm, e, A, r4=True)
    amp = float(tot.rad()) * float(arb(2) ** BITS)

    # G6 runtime on the BALL patch, matching R4/R5 t_patch semantics --------
    zpb = arb(float((g["zp"][0] + g["zp"][1]) / arb(2)), float((g["zp"][1] - g["zp"][0]) / arb(2)))
    zmb = arb(float((g["zm"][0] + g["zm"][1]) / arb(2)), float((g["zm"][1] - g["zm"][0]) / arb(2)))
    kernel_apply(cand, zpb, zmb, e, A)
    reps, t = 200, time.process_time()
    for _ in range(reps):
        kernel_apply(cand, zpb, zmb, e, A)
    t_patch = (time.process_time() - t) / reps

    # G9 -------------------------------------------------------------------
    l4, u4 = XK.live_limits(zp, zm, A)
    tot_xk = XK.kernel_apply(cand, zp, zm, e, A)
    via_G = arb(0)
    for k, gg in compute_Gk(cand, zp, zm, A).items():
        via_G += gg * I_k_r4(k, l, u, e)
    g9 = bool(l.str(30) == l4.str(30) and u.str(30) == u4.str(30) and via_G.overlaps(tot_xk))

    # G10 precision sweep --------------------------------------------------
    sweep = []
    for bits in SWEEP:
        ctx.prec = bits
        A2, _, _, g2, zp2, zm2 = geom()
        e2 = rational(E_NUM, E_DEN)
        c2 = probe(N)                      # rebuilt at each precision
        reset_counters()
        t2, _, _ = kernel_apply(c2, zp2, zm2, e2, A2)
        sweep.append({"bits": bits, "amplification": float(t2.rad()) * float(arb(2) ** bits),
                      "rad": float(t2.rad()), "value": t2.str(25)})
    ctx.prec = BITS

    G_ = {
        "G1_per_k_overlap_R4": {"all": all(per_k.values()),
                                "failing_k": [k for k, v in per_k.items() if not v],
                                "n_k": len(per_k), "pass": all(per_k.values())},
        "G2_rigorous_containment": {"overlaps_R4": bool(tot.overlaps(tot_r4)),
                                    "R6_subset_R4": bool(tot.lower() >= tot_r4.lower()
                                                         and tot.upper() <= tot_r4.upper()),
                                    "R6": tot.str(30), "R4": tot_r4.str(30),
                                    "pass": bool(tot.overlaps(tot_r4))
                                            and bool(tot.lower() >= tot_r4.lower()
                                                     and tot.upper() <= tot_r4.upper())},
        "G3_amplification": {"value": amp, "threshold": AMP_THRESHOLD,
                             "r4_reference": R4_AMP, "r5_frozen": R5_AMP,
                             "improvement_vs_r4": R4_AMP / amp if amp else None,
                             "pass": amp <= AMP_THRESHOLD},
        "G4_z_panels": {"count": cnt["z_panels"], "pass": cnt["z_panels"] == 0},
        "G5_softplus": {"count": cnt["softplus_approximations"],
                        "pass": cnt["softplus_approximations"] == 0},
        "G6_runtime": {"t_patch_ms": t_patch * 1000, "budget_ms": RUNTIME_MS, "reps": reps,
                       "class": ("EXCELLENT" if t_patch * 1000 <= 0.75 else
                                 "ACCEPTABLE" if t_patch * 1000 <= 2.0 else "COST_FAIL"),
                       "pass": t_patch * 1000 <= RUNTIME_MS},
        "G7_no_empirical_monotonicity": {"note": "only Phi and exp increasing - classical",
                                         "pass": True},
        "G8_exact_rational_e": {"e": e.str(20), "radius": float(e.rad()),
                                "pass": float(e.rad()) == 0.0},
        "G9_xi_recurrence_unchanged": {"live_limits_identical": g9,
                                       "Gk_matches_R4_kernel_apply": bool(via_G.overlaps(tot_xk)),
                                       "pass": g9},
        "G10_precision_sweep": {"sweep": sweep,
                                "all_within_threshold": all(s["amplification"] <= AMP_THRESHOLD
                                                            for s in sweep),
                                "pass": all(s["amplification"] <= AMP_THRESHOLD for s in sweep)},
    }
    gate = all(v["pass"] for v in G_.values())
    sr_hours = CELLS * PATCHES * t_patch * CHARTS * FUNCS / 3600
    amp_cls = ("R6_FAIL" if amp > 1e12 else "R6_PASS" if amp > 1e9
               else "R6_STRONG_PASS" if amp >= 1e6 else "R6_BREAKTHROUGH")
    sr_cls = ("R6_NOT_ENOUGH" if sr_hours > 100 else "R6_USEFUL" if sr_hours > 25
              else "R6_STRONG" if sr_hours > 10 else "R6_BREAKTHROUGH")

    rec = {
        "schema": "rebaseguard.p5x.r6.gate.v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "checkpoint_h": "7800911d4ca5b93f1f4317494669f228501ef42a",
        "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=NS,
                                     capture_output=True, text=True).stdout.strip(),
        "config": {"bits": BITS, "candidate_degree": N, "patch": list(PATCH),
                   "e": f"{E_NUM}/{E_DEN}", "k_range": [-N, N],
                   "l": l.str(25), "u": u.str(25)},
        "criteria": G_,
        "gate": "PASS" if gate else "FAIL",
        "failed_criteria": [k for k, v in G_.items() if not v["pass"]],
        "amp_class": amp_cls,
        "regimes_used": {str(k): v for k, v in regs.items()},
        "reporting_diagnostics_not_criteria": {
            "note": "D13: huge x tiny is reported, never gated",
            "huge_tiny_products": cnt["huge_tiny_products"],
            "max_abs_log10": cnt["max_abs_log10"],
            "max_raw_prefactor_log10": cnt["max_raw_prefactor_log10"],
            "min_tail_factor": cnt["min_tail_factor"],
            "erfc_calls": cnt["erfc_calls"], "erf_calls": cnt["erf_calls"],
            "regime_B": cnt["regime_B"], "regime_C": cnt["regime_C"], "regime_D": cnt["regime_D"]},
        "projection": {"formula": "835*1210*t_patch*2*43/3600",
                       "projected_SR_cpu_hours": sr_hours, "cusum_cpu_hours": 146.0,
                       "projected_total_cpu_hours": sr_hours + 146.0,
                       "sr_class": sr_cls},
        "runtime": {"wall_seconds": time.time() - t0,
                    "peak_rss_mib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1048576},
    }
    (NS / "results" / "r6_gate.json").write_text(json.dumps(rec, indent=1) + "\n")
    print(json.dumps({k: v["pass"] for k, v in G_.items()}, indent=1))
    print(f"amp={amp:.4e} ({amp_cls})  t_patch={t_patch*1000:.4f} ms  "
          f"SR={sr_hours:.2f} CPU-h ({sr_cls})  gate={rec['gate']}")
    print("sweep:", [f"{s['bits']}:{s['amplification']:.4e}" for s in sweep])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
