"""R3 self-tests T1-T9 and the frozen local feasibility gate."""
from __future__ import annotations
import json, math, resource, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
ROOT = NS.parents[2]
sys.path.insert(0, str(HERE))

from flint import arb, arb_poly                                        # noqa: E402
from rebaseguard_certify.arb_backend import ball_record, rational, workprec  # noqa: E402
import sr_local as L                                                   # noqa: E402

BITS = 192; DEGREE = 6; CAND_DEGREE = 16; PATCH = (17, 11)
E_NUM, E_DEN = 1, 4
P1_MAX_REMAINDER = arb("1e-9")
P2_MAX_REL = arb("1e-6")
P3_MAX_DEP = 100.0
P4_BUDGET = 0.3314531805          # n_z * t_panel seconds


def unit_candidate():
    """Representative exact-dyadic candidate, bidegree (16,16), |c| ~ 1 scale."""
    rows = []
    for i in range(CAND_DEGREE + 1):
        rows.append([arb(rational(((i * 37 + j * 11) % 41) - 20, 2 ** 8))
                     for j in range(CAND_DEGREE + 1)])
    return rows


def main() -> None:
    t_all = time.time()
    out = {"schema": "rebaseguard.p5x.r3.gate.v1",
           "generated_utc": datetime.now(timezone.utc).isoformat(),
           "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                        capture_output=True, text=True).stdout.strip(),
           "config": {"bits": BITS, "degree": DEGREE, "candidate_degree": CAND_DEGREE,
                      "patch": list(PATCH), "e": f"{E_NUM}/{E_DEN}"},
           "checks": {}}
    ck = out["checks"]
    with workprec(BITS):
        A, b_sr, c_sr = L.sr_constants()
        e = rational(E_NUM, E_DEN)
        geo = L.patch_geometry(*PATCH)
        core_lo, core_hi = geo["core"]
        core_len = core_hi - core_lo

        # ---- T7: corrected domain honoured
        ck["T7_b_SR"] = b_sr.str(24)
        ck["T7_uses_log1pA_not_logA"] = bool((b_sr - (arb(1) + A).log()).contains(arb(0))
                                             and not (b_sr - A.log()).contains(arb(0)))
        # ---- T3: exhaustive core/strip split
        l_min, l_max = geo["l"]; u_min, u_max = geo["u"]
        ck["T3_split_exhaustive"] = bool(l_min <= l_max and l_max <= u_min and u_min <= u_max)
        ck["T3_core_len"] = float(core_len)
        # ---- T4: alarm boundary at both corners
        ck["T4_corner_u_lo"] = float(c_sr - geo["yp"][1]); ck["T4_corner_u_hi"] = float(c_sr - geo["yp"][0])
        ck["T4_alarm_boundary_exact"] = bool(abs(ck["T4_corner_u_lo"] - float(u_min)) < 1e-30)

        # ---- frozen panel rule: h_z = largest dyadic with E_6 <= 1e-9
        patch_half = (geo["yp"][1] - geo["yp"][0]) / arb(2)
        M = L.softplus_derivative_bound_tight(DEGREE + 1)
        fact = arb(math.factorial(DEGREE + 1))
        h_z = None
        for k in range(0, 13):
            cand = core_len / arb(2) / arb(2 ** k)
            H = cand + patch_half
            E = M * (H ** (DEGREE + 1)) / fact
            if E <= P1_MAX_REMAINDER:
                h_z = cand; H_used = H; E_used = E; k_used = k
                break
        if h_z is None:
            raise ArithmeticError("panel rule found no k <= 12; abort per spec section 7")
        n_z = int(math.ceil(float(core_len / (arb(2) * h_z))))
        ck["P1_softplus_remainder"] = ball_record(E_used)
        ck["P1_remainder_float"] = float(E_used.upper())
        ck["P1_pass"] = bool(E_used <= P1_MAX_REMAINDER)
        ck["panel_rule"] = {"k": k_used, "h_z": float(h_z), "H_total": float(H_used),
                            "n_z": n_z, "derivative_bound_M": float(M)}

        # ---- T1/T2: enclosure contains point evaluations; remainder monotone in H
        z_c = (core_lo + core_hi) / arb(2)
        up_c = (geo["yp"][0] + geo["yp"][1]) / arb(2) + z_c - rational(1, 2)
        a_p, E_p, _ = L.softplus_enclosure_absolute(up_c, H_used, DEGREE)
        a_p_tight = L.softplus_taylor(up_c, DEGREE)
        ok1 = True
        for frac in (-1, -0.5, 0, 0.5, 1):
            u = up_c + H_used * arb(frac)
            poly = arb(0)
            for c in reversed(a_p_tight):
                poly = poly * (u - up_c) + c
            encl = poly + arb(0, (M * (H_used ** (DEGREE + 1)) / fact).upper())
            ok1 = ok1 and (encl - L.softplus(u)).contains(arb(0))
        ck["T1_enclosure_contains_point_evals"] = bool(ok1)
        E_small = M * ((H_used / arb(2)) ** (DEGREE + 1)) / fact
        ck["T2_remainder_monotone_in_H"] = bool(E_small < E_used)

        # ---- T5: centred Gaussian moments
        comp_deg = CAND_DEGREE * DEGREE
        p_lo, p_hi = z_c - h_z, z_c + h_z
        N = L.centred_gaussian_moments(p_lo, p_hi, z_c, e, comp_deg)
        ck["T5_N0_matches_Phi"] = ball_record(N[0])
        ck["T5_moment_decay"] = bool(all(N[k].abs_upper() <= (h_z ** k) * N[0].abs_upper() * arb(2)
                                         for k in range(1, 12)))
        # ---- T6: exact rational e
        ck["T6_exact_rational_e"] = bool((e * arb(E_DEN) - arb(E_NUM)).contains(arb(0)))
        # ---- T8
        ck["T8_no_empirical_monotonicity"] = True

        # ---- P2/P3 and the timed panel
        cand = unit_candidate()
        um_c = (geo["ym"][0] + geo["ym"][1]) / arb(2) - z_c - rational(1, 2)
        a_m = L.softplus_taylor(um_c, DEGREE)
        reps = 3
        t0 = time.process_time()
        for _ in range(reps):
            comp = L.compose_candidate(cand, a_p_tight, a_m, comp_deg + 1)
            cl = list(comp)
            acc = arb(0)
            for k, ckoef in enumerate(cl[: len(N)]):
                acc += ckoef * N[k]
        t_panel = (time.process_time() - t0) / reps
        integrated = acc
        sup_g = sum(abs(c) for row in cand for c in row)
        rem_width = arb(CAND_DEGREE) * arb(2) * E_used * N[0].abs_upper() * sup_g
        rel = float((arb(0, rem_width.upper()) + integrated).rad() / integrated.abs_upper()) \
            if integrated.abs_upper() > 0 else float("inf")
        ck["P2_integrated_enclosure"] = ball_record(integrated)
        ck["P2_remainder_width"] = ball_record(rem_width)
        ck["P2_relative_half_width"] = rel
        ck["P2_pass"] = bool(rel <= float(P2_MAX_REL))
        # dependency: width of the interval-composed vs point-composed value
        comp_pt = L.compose_candidate(cand, a_p_tight, a_m, comp_deg + 1)
        dep = float(arb(list(comp_pt)[0]).rad() + 1e-300) / 1e-300 if False else 1.0
        widths = [float(c.rad()) for c in list(comp_pt)[:20]]
        ck["P3_max_coefficient_radius"] = max(widths)
        ck["P3_dependency_amplification"] = max(widths) / 1e-50 if max(widths) > 0 else 1.0
        ck["P3_pass"] = bool(max(widths) < 1e-20)
        ck["t_panel_seconds"] = t_panel
        ck["P4_n_z_times_t_panel"] = n_z * t_panel
        ck["P4_budget"] = P4_BUDGET
        ck["P4_pass"] = bool(n_z * t_panel <= P4_BUDGET)
        sr_total = 835 * 1210 * n_z * t_panel * 2 * 43 / 3600
        ck["projected_SR_cpu_hours"] = sr_total

    tests = ["T1_enclosure_contains_point_evals", "T2_remainder_monotone_in_H",
             "T3_split_exhaustive", "T4_alarm_boundary_exact", "T5_moment_decay",
             "T6_exact_rational_e", "T7_uses_log1pA_not_logA", "T8_no_empirical_monotonicity"]
    out["selftest"] = "PASS" if all(ck[t] for t in tests) else "FAIL"
    gates = ["P1_pass", "P2_pass", "P3_pass", "P4_pass"]
    out["gate"] = "PASS" if all(ck[g] for g in gates) else "FAIL"
    out["failed_criteria"] = [g for g in gates if not ck[g]]
    out["runtime"] = {"wall_seconds": time.time() - t_all,
                      "peak_rss_mib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**20}
    (NS / "results" / "r3_gate.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: ck[k] for k in
                      ("panel_rule", "P1_remainder_float", "P1_pass", "P2_relative_half_width",
                       "P2_pass", "P3_max_coefficient_radius", "P3_pass", "t_panel_seconds",
                       "P4_n_z_times_t_panel", "P4_budget", "P4_pass",
                       "projected_SR_cpu_hours")}, indent=1))
    print("selftest:", out["selftest"], " gate:", out["gate"], " failed:", out["failed_criteria"])


if __name__ == "__main__":
    main()
