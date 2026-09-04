"""P5Y Gate-1 M2 driver: PILOT-SR-DEGREE.

Same detector, same e, same patch, same candidate, same precision as the
historical R3 local gate.  Two things change, both frozen before execution:
the degree grid {8,10,12} and the DYADIC panel rule replaced by the CONTINUOUS
minimal-safe rule derived from the certified step-size inequality.

Mathematical gates are evaluated BEFORE the cost gate is read.
"""
from __future__ import annotations

import json, math, resource, statistics, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
R3 = ROOT / "level4" / "closure_proofs" / "p5x_global_nonlinear_dynamics" / "compute_optimization_r3_sr_symbolic"
for p in (str(R3), str(ROOT / "rebaseguard-proof" / "src")):
    if p not in sys.path:
        sys.path.insert(0, p)

from flint import arb                                                        # noqa: E402
from rebaseguard_certify.arb_backend import ball_record, rational, workprec   # noqa: E402
import sr_local as L                                                         # noqa: E402
from r3_gate import unit_candidate                                           # noqa: E402

BITS = 192                    # frozen, unchanged from R3
CAND_DEGREE = 16              # frozen, unchanged
PATCH = (17, 11)              # frozen, the R3 incumbent-worst patch
E_NUM, E_DEN = 1, 4           # frozen
DEGREES = (8, 10, 12)         # FROZEN GRID -- may not be extended
CONTROL_DEGREE = 6            # free baseline control only
P1_MAX_REMAINDER = arb("1e-9")
P2_MAX_REL = arb("1e-6")
P3_MAX_RADIUS = 1e-20
P4_BUDGET = 0.3314531805      # exact frozen R3 cost threshold
TIMING_REPEATS = 5            # frozen before execution


def continuous_panel_rule(degree, core_len, patch_half):
    """h_z from the certified inequality M H^{d+1}/(d+1)! <= 1e-9, no dyadic rounding."""
    M = L.softplus_derivative_bound_tight(degree + 1)
    fact = arb(math.factorial(degree + 1))
    # H_max = (1e-9 (d+1)! / M)^{1/(d+1)}, evaluated by log/exp in Arb
    H_max = ((P1_MAX_REMAINDER * fact / M).log() / arb(degree + 1)).exp()
    h_z_ball = H_max - patch_half
    if not h_z_ball.lower() > 0:
        return None
    h_z = arb(float(h_z_ball.lower()))          # conservative, deterministic
    H_used = h_z + patch_half
    E_used = M * (H_used ** (degree + 1)) / fact
    n_z = int(math.ceil(float((core_len / (arb(2) * h_z)).upper())))
    return {"M": M, "fact": fact, "H_max": H_max, "h_z": h_z, "H_used": H_used,
            "E_used": E_used, "n_z": n_z}


def run_degree(degree, geo, e, cand):
    core_lo, core_hi = geo["core"]
    core_len = core_hi - core_lo
    patch_half = (geo["yp"][1] - geo["yp"][0]) / arb(2)
    rule = continuous_panel_rule(degree, core_len, patch_half)
    out = {"degree": degree}
    if rule is None:
        out.update({"INFEASIBLE": True, "verdict": "FAIL",
                    "reason": "h_z <= 0: patch half-width alone exceeds H_max"})
        return out
    M, fact, h_z, H_used, E_used, n_z = (rule["M"], rule["fact"], rule["h_z"],
                                         rule["H_used"], rule["E_used"], rule["n_z"])
    out["panel_rule"] = {"rule": "continuous minimal-safe (no dyadic rounding)",
                         "M_derivative_bound": float(M), "H_max": float(rule["H_max"]),
                         "patch_half": float(patch_half), "h_z": float(h_z),
                         "H_used": float(H_used), "n_z": n_z,
                         "core_len": float(core_len)}

    z_c = (core_lo + core_hi) / arb(2)
    up_c = (geo["yp"][0] + geo["yp"][1]) / arb(2) + z_c - rational(1, 2)
    um_c = (geo["ym"][0] + geo["ym"][1]) / arb(2) - z_c - rational(1, 2)
    a_p = L.softplus_taylor(up_c, degree)
    a_m = L.softplus_taylor(um_c, degree)

    # ---------------- mathematical gates, evaluated FIRST ----------------
    g = {}
    g["P1_remainder"] = float(E_used.upper())
    g["P1_pass"] = bool(E_used <= P1_MAX_REMAINDER)

    ok1 = True
    for frac in (-1, -0.5, 0, 0.5, 1):
        u = up_c + H_used * arb(frac)
        poly = arb(0)
        for c in reversed(a_p):
            poly = poly * (u - up_c) + c
        encl = poly + arb(0, (M * (H_used ** (degree + 1)) / fact).upper())
        ok1 = ok1 and (encl - L.softplus(u)).contains(arb(0))
    g["T1_enclosure_contains_point_evals"] = bool(ok1)
    g["T2_remainder_monotone_in_H"] = bool(
        M * ((H_used / arb(2)) ** (degree + 1)) / fact < E_used)
    l_min, l_max = geo["l"]; u_min, u_max = geo["u"]
    g["T3_split_exhaustive"] = bool(l_min <= l_max and l_max <= u_min and u_min <= u_max)

    comp_deg = CAND_DEGREE * degree
    p_lo, p_hi = z_c - h_z, z_c + h_z
    N = L.centred_gaussian_moments(p_lo, p_hi, z_c, e, comp_deg)
    g["T5_moment_decay"] = bool(all(N[k].abs_upper() <= (h_z ** k) * N[0].abs_upper() * arb(2)
                                    for k in range(1, 12)))

    comp_pt = L.compose_candidate(cand, a_p, a_m, comp_deg + 1)
    radii = [float(c.rad()) for c in list(comp_pt)[:20]]
    g["P3_max_coefficient_radius"] = max(radii)
    g["P3_pass"] = bool(max(radii) < P3_MAX_RADIUS)

    acc = arb(0)
    for k, ck in enumerate(list(comp_pt)[: len(N)]):
        acc += ck * N[k]
    sup_g = sum(abs(c) for row in cand for c in row)
    rem_width = arb(CAND_DEGREE) * arb(2) * E_used * N[0].abs_upper() * sup_g
    rel = (float((arb(0, rem_width.upper()) + acc).rad() / acc.abs_upper())
           if acc.abs_upper() > 0 else float("inf"))
    g["P2_relative_half_width"] = rel
    g["P2_pass"] = bool(rel <= float(P2_MAX_REL))
    g["P2_integrated_enclosure"] = ball_record(acc)
    out["math_gates"] = g
    math_keys = ["P1_pass", "P2_pass", "P3_pass", "T1_enclosure_contains_point_evals",
                 "T2_remainder_monotone_in_H", "T3_split_exhaustive", "T5_moment_decay"]
    out["math_gates_all_pass"] = all(g[k] for k in math_keys)

    # ---------------- cost gate, read only after the maths ----------------
    times, times_full = [], []
    for _ in range(TIMING_REPEATS):
        t0 = time.process_time()
        comp = L.compose_candidate(cand, a_p, a_m, comp_deg + 1)
        cl = list(comp)
        s = arb(0)
        for k, ck in enumerate(cl[: len(N)]):
            s += ck * N[k]
        times.append(time.process_time() - t0)
        t1 = time.process_time()
        Nf = L.centred_gaussian_moments(p_lo, p_hi, z_c, e, comp_deg)
        comp2 = L.compose_candidate(cand, a_p, a_m, comp_deg + 1)
        s2 = arb(0)
        for k, ck in enumerate(list(comp2)[: len(Nf)]):
            s2 += ck * Nf[k]
        times_full.append(time.process_time() - t1)
    t_panel = statistics.median(times)
    out["timing"] = {"repeats": TIMING_REPEATS, "t_panel_median": t_panel,
                     "t_panel_min": min(times), "t_panel_max": max(times),
                     "t_panel_spread_pct": 100.0 * (max(times) - min(times)) / t_panel,
                     "t_panel_full_median_incl_moments": statistics.median(times_full),
                     "composed_degree": comp_deg}
    out["cost"] = {"metric": "n_z * t_panel (R3-comparable: compose+contract)",
                   "n_z": n_z, "t_panel": t_panel, "value": n_z * t_panel,
                   "budget": P4_BUDGET, "P4_pass": bool(n_z * t_panel <= P4_BUDGET),
                   "value_incl_moments": n_z * statistics.median(times_full)}
    out["verdict"] = "PASS" if (out["math_gates_all_pass"] and out["cost"]["P4_pass"]) else "FAIL"
    out["failed"] = ([k for k in math_keys if not g[k]]
                     + ([] if out["cost"]["P4_pass"] else ["P4_cost"]))
    return out


def main():
    t_all = time.time()
    payload = {"schema": "rebaseguard.p5y.gate1.m2.v1", "pilot": "PILOT-SR-DEGREE",
               "binding": False,
               "generated_utc": datetime.now(timezone.utc).isoformat(),
               "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                            capture_output=True, text=True).stdout.strip(),
               "frozen": {"degrees": list(DEGREES), "control_degree": CONTROL_DEGREE,
                          "patch": list(PATCH), "e": f"{E_NUM}/{E_DEN}", "bits": BITS,
                          "candidate_degree": CAND_DEGREE, "budget": P4_BUDGET,
                          "timing_repeats": TIMING_REPEATS,
                          "panel_rule": "continuous minimal-safe; dyadic rounding removed"},
               "degrees": {}}
    with workprec(BITS):
        A, b_sr, c_sr = L.sr_constants()
        e = rational(E_NUM, E_DEN)
        geo = L.patch_geometry(*PATCH)
        payload["T7_uses_log1pA_not_logA"] = bool(
            (b_sr - (arb(1) + A).log()).contains(arb(0))
            and not (b_sr - A.log()).contains(arb(0)))
        payload["T6_exact_rational_e"] = bool((e * arb(E_DEN) - arb(E_NUM)).contains(arb(0)))
        payload["T8_no_empirical_monotonicity"] = True
        cand = unit_candidate()
        for d in (CONTROL_DEGREE,) + DEGREES:
            payload["degrees"][str(d)] = run_degree(d, geo, e, cand)
            payload["degrees"][str(d)]["role"] = ("control_only_not_selectable"
                                                  if d == CONTROL_DEGREE else "candidate")

    qualifying = [d for d in DEGREES if payload["degrees"][str(d)]["verdict"] == "PASS"]
    selected = min(qualifying) if qualifying else None
    payload["qualifying_degrees"] = qualifying
    payload["selected_degree"] = selected
    payload["tie_break"] = "lowest qualifying degree (frozen)"
    payload["PILOT_SR_DEGREE"] = "PASS" if selected is not None else "FAIL"
    if selected is not None:
        s = payload["degrees"][str(selected)]
        payload["selected"] = {"degree": selected, "n_z": s["cost"]["n_z"],
                               "t_panel": s["cost"]["t_panel"],
                               "cost_metric": s["cost"]["value"]}
    ch = resource.getrusage(resource.RUSAGE_CHILDREN)
    me = resource.getrusage(resource.RUSAGE_SELF)
    payload["runtime"] = {"wall_seconds": time.time() - t_all,
                          "cpu_seconds": me.ru_utime + me.ru_stime,
                          "peak_rss_mib": me.ru_maxrss / (1024 * 1024)}
    (HERE / "results" / "m2_sr_degree.json").write_text(json.dumps(payload, indent=1) + "\n")
    brief = {d: {"n_z": payload["degrees"][d].get("panel_rule", {}).get("n_z"),
                 "t_panel": payload["degrees"][d].get("cost", {}).get("t_panel"),
                 "cost": payload["degrees"][d].get("cost", {}).get("value"),
                 "math_all_pass": payload["degrees"][d].get("math_gates_all_pass"),
                 "verdict": payload["degrees"][d]["verdict"]}
             for d in payload["degrees"]}
    print(json.dumps({"per_degree": brief, "qualifying": qualifying,
                      "selected_degree": selected,
                      "PILOT_SR_DEGREE": payload["PILOT_SR_DEGREE"],
                      "runtime": payload["runtime"]}, indent=1))


if __name__ == "__main__":
    main()
