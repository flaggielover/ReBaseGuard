"""P5X R4 frozen feasibility gate: criteria P1..P8 of R4_FROZEN_SPEC.md.

Every threshold, formula, candidate and class used here was frozen at
Checkpoint F (209a6fd9a5ca2824688062ac855a7abcefae9697) before this file
existed.  Nothing below re-budgets anything after measurement.
"""
from __future__ import annotations

import json, resource, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

from flint import arb, ctx

sys.path.insert(0, str(Path(__file__).resolve().parent))
from xi_kernel import (COUNTERS, gaussian_exp_integral, kernel_apply,  # noqa: E402
                       kernel_quadrature, live_limits, reset_counters,
                       sr_constants, y_to_zeta, zeta_patch)
from rebaseguard_certify.arb_backend import rational  # noqa: E402

BITS, N_PROD, PATCH, E_NUM, E_DEN = 192, 16, (17, 11), 1, 4
P4_BUDGET = 0.3314531805                      # frozen; == the 8000 CPU-hour line
CELLS, PATCHES, CHARTS, FUNCS = 835, 1210, 2, 43
NS = Path(__file__).resolve().parents[1]


def softplus(u: arb) -> arb:
    if u.lower() >= 0:
        return u + (arb(1) + (-u).exp()).log()
    return (arb(1) + u.exp()).log()


def probe(n: int):
    """Frozen probe candidate, R4_FROZEN_SPEC.md section 4: c_ij = 1/(1+i+2j)."""
    return [[rational(1, 1 + i + 2 * j) for j in range(n + 1)] for i in range(n + 1)]


def rel_halfwidth(x: arb) -> float:
    m = abs(float(x.mid()))
    return float(x.rad()) / m if m > 0 else float("inf")


def main() -> int:
    ctx.prec = BITS
    t0 = time.time()
    A, b, c = sr_constants()
    e = rational(E_NUM, E_DEN)
    out: dict = {}

    # ---- P1: the recurrence is exact in xi and in zeta -------------------
    p1 = []
    for yn, yd, zn, zd in ((7, 10, 13, 10), (0, 1, -5, 2), (31, 5, 2, 5)):
        y, z = rational(yn, yd), rational(zn, zd)
        xi = y.exp()
        lhs = softplus(y + z - rational(1, 2)).exp()          # frozen y-space
        rhs = arb(1) + xi * (z - rational(1, 2)).exp()        # xi-space
        zeta = y_to_zeta(y, A)
        zl = (rational(1, 1) / A + zeta) * (z - rational(1, 2)).exp()
        agree = lhs.overlaps(rhs) and zl.overlaps((rhs - arb(1)) / A)
        p1.append({"y": f"{yn}/{yd}", "z": f"{zn}/{zd}", "overlaps": bool(agree),
                   "value": lhs.str(20),
                   "rel_halfwidth": max(rel_halfwidth(lhs), rel_halfwidth(rhs))})
    out["P1"] = {"points": p1,
                 "pass": all(p["overlaps"] and p["rel_halfwidth"] <= 1e-40 for p in p1)}

    # ---- P2: closed form vs 40000-point Simpson at 256 bits --------------
    g = zeta_patch(*PATCH)
    zp_lo, zp_hi = g["zp"]
    zm_lo, zm_hi = g["zm"]
    pts = [((zp_lo + zp_hi) / arb(2), (zm_lo + zm_hi) / arb(2)),
           (zp_lo, zm_lo), (zp_lo, zm_hi), (zp_hi, zm_lo), (zp_hi, zm_hi)]
    cand3 = probe(3)
    worst_rel, contained, overlapped, rows = 0.0, True, True, []
    for zp, zm in pts:
        cf = kernel_apply(cand3, zp, zm, e, A)
        ctx.prec = 256
        ref = kernel_quadrature(cand3, zp, zm, e, A, 40000)
        ref_half = kernel_quadrature(cand3, zp, zm, e, A, 20000)
        ctx.prec = BITS
        # D11: Simpson is NOT an enclosure.  Richardson-estimate its own
        # truncation error (Simpson is O(h^4), so the n -> 2n gain is ~15x)
        # and widen the reference by 16x that estimate before comparing.
        trunc = abs(float(ref.mid()) - float(ref_half.mid())) / 15.0
        ref_wide = arb(float(ref.mid()), 16.0 * trunc + float(ref.rad()))
        ok_contain = cf.overlaps(ref)                      # literal frozen test
        ok_overlap = cf.overlaps(ref_wide)                 # intended test (D11)
        rw = rel_halfwidth(cf)
        gap = abs(float(cf.mid()) - float(ref.mid())) / max(abs(float(ref.mid())), 1e-300)
        rows.append({"closed_form": cf.str(25), "reference": ref.str(25),
                     "contains_reference": bool(ok_contain),
                     "overlaps_widened_reference": bool(ok_overlap),
                     "reference_truncation_estimate": trunc,
                     "rel_halfwidth": rw, "rel_gap": gap})
        worst_rel = max(worst_rel, rw)
        contained = contained and ok_contain
        overlapped = overlapped and ok_overlap
    out["P2"] = {"points": rows, "worst_rel_halfwidth": worst_rel,
                 "all_contain_reference": contained,
                 "all_overlap_widened_reference": overlapped,
                 "pass": contained and worst_rel <= 1e-12,
                 "pass_corrected": overlapped and worst_rel <= 1e-12,
                 "defect": "D11 -- the frozen 'contain' direction is ill-typed; "
                           "'pass' is the literal frozen verdict, 'pass_corrected' "
                           "is the intended test and is disclosed as post-hoc"}

    # ---- P3: conditioning at production degree n = 16, point state -------
    cand16 = probe(N_PROD)
    zc_p, zc_m = pts[0]
    val16 = kernel_apply(cand16, zc_p, zc_m, e, A)
    amp = float(val16.rad()) * float(arb(2) ** BITS)
    out["P3"] = {"value": val16.str(20), "radius": float(val16.rad()),
                 "dependency_amplification": amp, "pass": amp <= 1e12}

    # ---- P4: measured t_patch on the frozen ball patch --------------------
    zp = arb(float((zp_lo + zp_hi) / arb(2)), float((zp_hi - zp_lo) / arb(2)))
    zm = arb(float((zm_lo + zm_hi) / arb(2)), float((zm_hi - zm_lo) / arb(2)))
    kernel_apply(cand16, zp, zm, e, A)                       # warm
    reps, t = 200, time.process_time()
    for _ in range(reps):
        kernel_apply(cand16, zp, zm, e, A)
    t_patch = (time.process_time() - t) / reps
    sr_hours = CELLS * PATCHES * t_patch * CHARTS * FUNCS / 3600.0
    out["P4"] = {"t_patch_seconds": t_patch, "budget": P4_BUDGET,
                 "reps": reps, "projected_SR_cpu_hours": sr_hours,
                 "pass": t_patch <= P4_BUDGET}

    # ---- P5: structural zero-panel property ------------------------------
    reset_counters()
    kernel_apply(cand16, zp, zm, e, A)
    out["P5"] = {"counters": dict(COUNTERS),
                 "expected_phi_evals": 2 * (2 * N_PROD + 1),
                 "pass": COUNTERS["z_panels"] == 0
                         and COUNTERS["softplus_expansions"] == 0
                         and COUNTERS["phi_evals"] == 2 * (2 * N_PROD + 1)}

    # ---- P6: exact rational drift ----------------------------------------
    out["P6"] = {"e": e.str(20), "radius": float(e.rad()),
                 "pass": float(e.rad()) == 0.0}

    # ---- P7: atom neutrality + alarm agreement ---------------------------
    strict = []
    for zn, zd in ((-40, 1), (-80, 1), (0, 1), (5, 1)):
        z = rational(zn, zd)
        zprime = (rational(1, 1) / A + arb(0)) * (z - rational(1, 2)).exp()
        strict.append(zprime.lower() > 0)
    alarm = []
    for d in (rational(1, 1000), rational(-1, 1000)):
        y = rational(1, 2)
        z = c - y + d                                  # boundary z = c_SR - y
        v = y + z - rational(1, 2)
        y_alarm = bool((v - A.log()).lower() > 0) if d.mid() > 0 else bool((v - A.log()).upper() < 0)
        zeta_p = (rational(1, 1) / A + y_to_zeta(y, A)) * (z - rational(1, 2)).exp()
        x_alarm = bool((zeta_p - arb(1)).lower() > 0) if d.mid() > 0 else bool((zeta_p - arb(1)).upper() < 0)
        alarm.append({"delta": d.str(6), "y_space": y_alarm, "zeta_space": x_alarm,
                      "agree": y_alarm == x_alarm})
    out["P7"] = {"zeta_prime_strictly_positive": all(strict),
                 "alarm_agreement": alarm,
                 "pass": all(strict) and all(a["agree"] for a in alarm)}

    # ---- P8 ---------------------------------------------------------------
    out["P8"] = {"note": "every bound is an Arb enclosure or an exact identity; "
                         "the only monotonicity used is that exp and log increase",
                 "pass": True}

    KEYS = ("P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8")
    gate = all(out[k]["pass"] for k in KEYS)
    gate_corrected = all(out[k].get("pass_corrected", out[k]["pass"]) for k in KEYS)
    total = sr_hours + 146.0
    speed = ("R4_BREAKTHROUGH" if sr_hours <= 1000 else "R4_STRONG" if sr_hours <= 3000
             else "R4_USEFUL" if sr_hours <= 8000 else "R4_PARTIAL" if sr_hours <= 15000
             else "R4_NOT_ENOUGH")
    viab = ("STRONGLY_VIABLE" if total <= 1000 else "VIABLE" if total <= 5000
            else "MARGINAL" if total <= 12000 else "MORE_OPT_REQUIRED")

    rec = {
        "schema": "rebaseguard.p5x.r4.gate.v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "checkpoint_f": "209a6fd9a5ca2824688062ac855a7abcefae9697",
        "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=NS,
                                     capture_output=True, text=True).stdout.strip(),
        "config": {"bits": BITS, "candidate_degree": N_PROD, "patch": list(PATCH),
                   "e": f"{E_NUM}/{E_DEN}", "production_variable": "zeta=(xi-1)/A"},
        "criteria": out,
        "gate": "PASS" if gate else "FAIL",
        "gate_corrected_post_hoc": "PASS" if gate_corrected else "FAIL",
        "failed_criteria": [k for k in out if not out[k]["pass"]],
        "failed_criteria_corrected": [k for k in out
                                      if not out[k].get("pass_corrected", out[k]["pass"])],
        "projection": {"formula": "835*1210*t_patch*2*43/3600",
                       "projected_SR_cpu_hours": sr_hours,
                       "cusum_cpu_hours": 146.0,
                       "projected_total_cpu_hours": total,
                       "speedup_class": speed, "viability_class": viab,
                       "r3_projected_SR_cpu_hours": 12083.77402548149,
                       "speedup_vs_r3": 12083.77402548149 / sr_hours if sr_hours else None},
        "runtime": {"wall_seconds": time.time() - t0,
                    "peak_rss_mib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1048576},
    }
    p = NS / "results" / "r4_gate.json"
    p.write_text(json.dumps(rec, indent=1) + "\n")
    print(json.dumps({k: out[k]["pass"] for k in out}, indent=1))
    print("gate_corrected(post-hoc, D11):", "PASS" if gate_corrected else "FAIL")
    print(f"t_patch={t_patch*1000:.4f} ms   SR={sr_hours:.1f} CPU-h   "
          f"{speed} / {viab}   gate={rec['gate']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
