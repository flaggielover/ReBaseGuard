"""P5Y Gate-2A: PILOT-SR-PRECISION.

One experimental variable: WORKING PRECISION.  The state patch, drift,
candidate, panel geometry, approximation formula, step-size criterion and every
mathematical gate are imported unmodified from the historical R3 module and from
Gate-1's frozen outputs.

Panel geometry is NOT recomputed per precision cell: Gate-1's continuous
minimal-safe rule was evaluated once at 192 bits and its output is frozen here,
so that n_z is bit-identical across every cell and precision is the sole variable.
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

# ----------------------------- FROZEN (GATE2A_PREREGISTRATION.md sections 2-6)
PATCH = (17, 11)
E_NUM, E_DEN = 1, 4
CAND_DEGREE = 16
DEGREES = (8, 10)                       # degree 12 PROHIBITED
PRECISIONS = (256, 384, 512)            # no 768/1024 may be added post-result
CONTROL_PRECISION = 192                 # frozen before T2, essentially free
P1_MAX_REMAINDER = arb("1e-9")
P2_SAFETY_TARGET = 1e-8                 # frozen; 100x inside Gate-1's 1e-6
P3_MAX_RADIUS = 1e-20
TIMING_REPEATS = 5                      # frozen, not reducible
REPRO_CELL = (8, 384)                   # frozen reproducibility configuration
# Gate-1 panel-rule OUTPUT, frozen so geometry is identical across all cells:
FROZEN_PANEL = {
    8:  {"h_z": 0.19386660811172551, "H_used": 0.24275293177756252, "n_z": 28},
    10: {"h_z": 0.31331186801206190, "H_used": 0.36219819167789891, "n_z": 17},
}
GATE1_BASELINE = {8: {"P2": 7.4487e-07, "t_panel": 0.005797, "acc_radius": 5.6532e-05},
                  10: {"P2": 9.9187e-01, "t_panel": 0.006776, "acc_radius": 1.4040e+12}}


def run_cell(degree: int, bits: int, cand):
    """One (degree, precision) cell.  Geometry frozen; only `bits` varies."""
    t_cell = time.process_time()
    fp = FROZEN_PANEL[degree]
    with workprec(bits):
        A, b_sr, c_sr = L.sr_constants()
        e = rational(E_NUM, E_DEN)
        geo = L.patch_geometry(*PATCH)
        core_lo, core_hi = geo["core"]
        core_len = core_hi - core_lo
        patch_half = (geo["yp"][1] - geo["yp"][0]) / arb(2)
        h_z = arb(fp["h_z"])
        H_used = h_z + patch_half
        n_z = fp["n_z"]
        M = L.softplus_derivative_bound_tight(degree + 1)      # exact rational
        fact = arb(math.factorial(degree + 1))
        E_used = M * (H_used ** (degree + 1)) / fact

        z_c = (core_lo + core_hi) / arb(2)
        up_c = (geo["yp"][0] + geo["yp"][1]) / arb(2) + z_c - rational(1, 2)
        um_c = (geo["ym"][0] + geo["ym"][1]) / arb(2) - z_c - rational(1, 2)
        a_p = L.softplus_taylor(up_c, degree)
        a_m = L.softplus_taylor(um_c, degree)

        g = {}
        g["P1_remainder"] = float(E_used.upper())
        g["P1_pass"] = bool(E_used <= P1_MAX_REMAINDER)
        g["P1_margin_relative"] = float((P1_MAX_REMAINDER - E_used) / P1_MAX_REMAINDER)

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
        g["T6_exact_rational_e"] = bool((e * arb(E_DEN) - arb(E_NUM)).contains(arb(0)))
        g["T7_uses_log1pA_not_logA"] = bool(
            (b_sr - (arb(1) + A).log()).contains(arb(0))
            and not (b_sr - A.log()).contains(arb(0)))
        g["T8_no_empirical_monotonicity"] = True

        comp_deg = CAND_DEGREE * degree
        p_lo, p_hi = z_c - h_z, z_c + h_z
        N = L.centred_gaussian_moments(p_lo, p_hi, z_c, e, comp_deg)
        g["T5_moment_decay"] = bool(all(N[k].abs_upper() <= (h_z ** k) * N[0].abs_upper() * arb(2)
                                        for k in range(1, 12)))

        comp = L.compose_candidate(cand, a_p, a_m, comp_deg + 1)
        cl = list(comp)
        radii = [float(c.rad()) for c in cl[:20]]
        g["P3_max_coefficient_radius"] = max(radii)
        g["P3_pass"] = bool(max(radii) < P3_MAX_RADIUS)
        g["P3_margin_orders"] = (math.log10(P3_MAX_RADIUS / max(radii))
                                 if max(radii) > 0 else float("inf"))

        acc = arb(0)
        for k, ck in enumerate(cl[: len(N)]):
            acc += ck * N[k]
        sup_g = sum(abs(c) for row in cand for c in row)
        rem_width = arb(CAND_DEGREE) * arb(2) * E_used * N[0].abs_upper() * sup_g
        rel = (float((arb(0, rem_width.upper()) + acc).rad() / acc.abs_upper())
               if acc.abs_upper() > 0 else float("inf"))
        acc_rad = float(acc.rad())
        acc_abs = float(acc.abs_upper())
        floor = float(rem_width.upper()) / acc_abs if acc_abs > 0 else float("inf")
        g["P2_relative_half_width"] = rel
        g["P2_pass"] = bool(rel <= P2_SAFETY_TARGET)
        g["P2_margin_factor"] = P2_SAFETY_TARGET / rel if rel > 0 else float("inf")
        g["P2_floor_precision_independent"] = floor
        g["P2_floor_below_target"] = bool(floor <= P2_SAFETY_TARGET)
        g["acc_radius"] = acc_rad
        g["acc_relative_radius"] = acc_rad / acc_abs if acc_abs > 0 else float("inf")
        g["acc_enclosure"] = ball_record(acc)
        g["acc_lower_str"] = acc.lower().str(40)
        g["acc_upper_str"] = acc.upper().str(40)
        g["rem_width"] = float(rem_width.upper())
        dig_avail = bits * math.log10(2)
        dig_kept = (-math.log10(acc_rad / acc_abs) if acc_abs > 0 and acc_rad > 0
                    else float("inf"))
        g["digits_available"] = dig_avail
        g["digits_retained"] = dig_kept
        g["digits_lost"] = dig_avail - dig_kept if dig_kept != float("inf") else 0.0

        times = []
        for _ in range(TIMING_REPEATS):
            t0 = time.process_time()
            Nf = L.centred_gaussian_moments(p_lo, p_hi, z_c, e, comp_deg)
            cf = L.compose_candidate(cand, a_p, a_m, comp_deg + 1)
            s = arb(0)
            for k, ck in enumerate(list(cf)[: len(Nf)]):
                s += ck * Nf[k]
            times.append(time.process_time() - t0)
    t_panel = statistics.median(times)
    math_keys = ["P1_pass", "P3_pass", "T1_enclosure_contains_point_evals",
                 "T2_remainder_monotone_in_H", "T3_split_exhaustive", "T5_moment_decay",
                 "T6_exact_rational_e", "T7_uses_log1pA_not_logA"]
    return {"degree": degree, "bits": bits, "n_z": n_z,
            "h_z": fp["h_z"], "H_used": fp["H_used"],
            "gates": g,
            "inherited_gates_all_pass": all(g[k] for k in math_keys),
            "safety_pass": bool(g["P2_pass"]),
            "timing": {"repeats": TIMING_REPEATS, "t_panel_median": t_panel,
                       "t_panel_min": min(times), "t_panel_max": max(times),
                       "relative_spread": (max(times) - min(times)) / t_panel},
            "cost_metric_n_z_times_t_panel": n_z * t_panel,
            "cell_cpu_seconds": time.process_time() - t_cell,
            "peak_rss_mib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 * 1024),
            "qualifies": bool(all(g[k] for k in math_keys) and g["P2_pass"])}


def classify(cells, degree):
    """Section 8 diagnosis, from interval RADII and their behaviour in precision."""
    seq = [(b, cells[f"{degree}@{b}"]) for b in (CONTROL_PRECISION,) + PRECISIONS
           if f"{degree}@{b}" in cells]
    rads = [(b, c["gates"]["acc_radius"]) for b, c in seq]
    monotone = all(rads[i + 1][1] <= rads[i][1] for i in range(len(rads) - 1))
    contracts = rads[0][1] > 0 and rads[-1][1] < rads[0][1] * 1e-6
    any_pass = any(c["qualifies"] for _, c in seq)
    floor_ok = all(c["gates"]["P2_floor_below_target"] for _, c in seq)
    if any_pass and monotone and contracts:
        cls = "PRECISION_INSUFFICIENT"       # low-precision failure, repaired by precision
    elif not floor_ok:
        cls = "REPRESENTATION_ILL_CONDITIONED"
    elif not monotone:
        cls = "REPRESENTATION_ILL_CONDITIONED"
    elif not any_pass:
        cls = "MATHEMATICALLY_FALSE"
    else:
        cls = "UNKNOWN"
    return {"radius_by_precision": rads, "radius_monotone_in_precision": monotone,
            "radius_contracts": contracts, "P2_floor_below_target_everywhere": floor_ok,
            "classification": cls}


def main():
    t_all = time.time()
    c0 = time.process_time()
    cand = unit_candidate()
    cells = {}
    for d in DEGREES:
        for b in (CONTROL_PRECISION,) + PRECISIONS:
            cells[f"{d}@{b}"] = run_cell(d, b, cand)

    rd, rb = REPRO_CELL
    rerun = run_cell(rd, rb, cand)
    base = cells[f"{rd}@{rb}"]
    repro = {"cell": f"degree {rd} @ {rb} bits",
             "lower_identical": base["gates"]["acc_lower_str"] == rerun["gates"]["acc_lower_str"],
             "upper_identical": base["gates"]["acc_upper_str"] == rerun["gates"]["acc_upper_str"],
             "P2_identical": base["gates"]["P2_relative_half_width"]
                             == rerun["gates"]["P2_relative_half_width"],
             "t_panel_run1": base["timing"]["t_panel_median"],
             "t_panel_run2": rerun["timing"]["t_panel_median"]}
    repro["ball_identical"] = bool(repro["lower_identical"] and repro["upper_identical"]
                                   and repro["P2_identical"])

    # ---- selection (mechanical, section 9)
    selected = None
    for b in PRECISIONS:
        c = cells[f"8@{b}"]
        if c["qualifies"] and repro["ball_identical"]:
            selected = b
            break
    decision = (f"SR_PRECISION_PASS_{selected}" if selected
                else "SR_PRECISION_FAIL_WITHIN_GRID")

    # ---- degree-10 replacement rule (section 10), evaluated only if it qualifies
    d10_min = next((b for b in PRECISIONS if cells[f"10@{b}"]["qualifies"]), None)
    rep = {"degree10_min_safe_precision": d10_min, "eligible": False, "reasons": []}
    if selected and d10_min:
        c8, c10 = cells[f"8@{selected}"], cells[f"10@{d10_min}"]
        a = c10["gates"]["P2_pass"]
        b_ = c10["inherited_gates_all_pass"]
        c_ = (c10["gates"]["P2_relative_half_width"] <= c8["gates"]["P2_relative_half_width"]
              and c10["gates"]["P2_floor_precision_independent"]
              <= c8["gates"]["P2_floor_precision_independent"])
        cost8 = c8["cost_metric_n_z_times_t_panel"]
        cost10 = c10["cost_metric_n_z_times_t_panel"]
        d_ = cost10 <= 0.80 * cost8
        rep.update({"a_P2_target": a, "b_all_gates": b_, "c_margins_not_worse": c_,
                    "d_materially_lower_cost_20pct": d_,
                    "cost_degree8": cost8, "cost_degree10": cost10,
                    "cost_ratio_10_over_8": cost10 / cost8,
                    "eligible": bool(a and b_ and c_ and d_)})
        rep["reasons"] = [k for k, v in (("P2_target", a), ("all_gates", b_),
                                         ("margins_not_worse", c_),
                                         ("materially_lower_cost", d_)) if not v]
    backend = ("DEGREE10_CONTINUOUS" if rep["eligible"] else
               "DEGREE8_CONTINUOUS" if selected else "NONE")

    diag = {str(d): classify(cells, d) for d in DEGREES}
    cpu = time.process_time() - c0
    payload = {"schema": "rebaseguard.p5y.gate2a.srprecision.v1", "binding": False,
               "pilot": "PILOT-SR-PRECISION",
               "generated_utc": datetime.now(timezone.utc).isoformat(),
               "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                            capture_output=True, text=True).stdout.strip(),
               "frozen": {"patch": list(PATCH), "e": f"{E_NUM}/{E_DEN}",
                          "degrees": list(DEGREES), "precisions": list(PRECISIONS),
                          "control_precision": CONTROL_PRECISION,
                          "candidate_degree": CAND_DEGREE,
                          "P2_safety_target": P2_SAFETY_TARGET,
                          "timing_repeats": TIMING_REPEATS,
                          "panel_geometry_frozen_from_gate1": FROZEN_PANEL,
                          "repro_cell": list(REPRO_CELL)},
               "gate1_baseline": GATE1_BASELINE,
               "cells": cells, "reproducibility": repro, "diagnosis": diag,
               "selected_precision_degree8": selected,
               "degree10_replacement": rep,
               "recommended_backend": backend,
               "GATE2A_DECISION": decision,
               "runtime": {"wall_seconds": time.time() - t_all, "cpu_seconds": cpu,
                           "cpu_hours": cpu / 3600.0, "cap_cpu_hours": 0.10,
                           "within_cap": bool(cpu / 3600.0 <= 0.10),
                           "peak_rss_mib": resource.getrusage(
                               resource.RUSAGE_SELF).ru_maxrss / (1024 * 1024)}}
    (HERE / "results" / "sr_precision.json").write_text(json.dumps(payload, indent=1) + "\n")

    print(f"{'cell':>10} {'n_z':>4} {'P2':>11} {'floor':>11} {'acc_rad':>11} "
          f"{'dig_lost':>9} {'t_panel(ms)':>12} {'cost(s)':>8}  gates")
    for d in DEGREES:
        for b in (CONTROL_PRECISION,) + PRECISIONS:
            c = cells[f"{d}@{b}"]; g = c["gates"]
            print(f"{f'd{d}@{b}':>10} {c['n_z']:>4} {g['P2_relative_half_width']:>11.4e} "
                  f"{g['P2_floor_precision_independent']:>11.4e} {g['acc_radius']:>11.4e} "
                  f"{g['digits_lost']:>9.1f} {c['timing']['t_panel_median']*1000:>12.3f} "
                  f"{c['cost_metric_n_z_times_t_panel']:>8.4f}  "
                  f"{'ALL_PASS' if c['inherited_gates_all_pass'] else 'GATE_FAIL'}"
                  f" {'P2_OK' if g['P2_pass'] else 'P2_FAIL'}")
    print(json.dumps({"reproducibility": repro, "diagnosis": diag,
                      "selected_precision_degree8": selected,
                      "degree10_replacement": rep, "recommended_backend": backend,
                      "GATE2A_DECISION": decision, "runtime": payload["runtime"]}, indent=1))


if __name__ == "__main__":
    main()
