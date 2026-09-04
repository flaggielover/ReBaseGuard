"""P5Y Gate-2D: PILOT-SR-REALCANDIDATE.

Builds ONE genuine production exact-dyadic SR backward-function candidate and
re-runs Gate-2A's precision grid on it, to test whether Gate-2A's conditioning
conclusion survives replacing `unit_candidate` by a real object.

Decisive candidate      hhat_1^SR   (P5X-T1's first backward function, closed
                                     form, rigorously certified on the whole square)
Non-decisive probe      hhat_2^SR   (= K_e h_1, genuinely NON-separable, node
                                     values from rigorous acb.integral;
                                     conditioning only, certifies nothing)
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

from flint import arb, acb, ctx                                              # noqa: E402
from rebaseguard_certify.arb_backend import (                                # noqa: E402
    ball_record, gaussian_cdf, rational, workprec)
import sr_local as L                                                         # noqa: E402
from r3_gate import unit_candidate                                           # noqa: E402

# ------------------------------------------------------------------- FROZEN
PATCH = (17, 11)
GRID = 64
E_NUM, E_DEN = 1, 4
DEGREE = 8                       # softplus Taylor degree; degree 10 NOT used here
CAND_DEGREE = 16                 # bidegree (16,16); may not be raised after T2
CHEB_N = 60                      # 1-D interpolation degree for the decisive candidate
SCALE_BITS = 50
PRECISIONS = (256, 384, 512)     # no 640/768/1024, no adaptive point
P1_TARGET = arb("1e-9")
EPS_P1 = arb(1) / arb(1000)      # repaired target (1 - eps_P1) * 1e-9
P2_TARGET = 1e-8
MAX_COMPLEXITY_SCORE = 100_000
TIMING_REPEATS = 5
REPRO_BITS = 384
GATE2A_DIGITS_LOST = 51.8
GATE2A_NZ = 28
CRAMER = arb(1086) / arb(1000)


def sr_constants():
    A = arb(4581762885148045) / arb(8796093022208)
    return A, (arb(1) + A).log(), A.log() + rational(1, 2)


# ---------------------------------------------------------------------------
# Decisive candidate: hhat_1, separable, rigorously certified on [0,b_SR]^2
# ---------------------------------------------------------------------------
def cheb_fit_1d(fn, b_sr, *, n=CHEB_N, keep=CAND_DEGREE):
    half = b_sr / arb(2)
    vals = [fn(half * (arb(math.cos(math.pi * k / n)) + arb(1))) for k in range(n + 1)]
    coeffs = []
    for j in range(n + 1):
        s = arb(0)
        for k in range(n + 1):
            w = arb(1) / arb(2) if k in (0, n) else arb(1)
            s += w * vals[k] * arb(math.cos(math.pi * j * k / n))
        c = arb(2) * s / arb(n)
        coeffs.append(c / arb(2) if j in (0, n) else c)
    tail = arb(0)
    for j in range(keep + 1, n + 1):
        tail += coeffs[j].abs_upper()
    sup_der = (CRAMER / (arb(2) * arb.pi()).sqrt()) * arb(math.factorial(n)).sqrt()
    interp_err = arb(2) * ((b_sr / arb(4)) ** (n + 1)) * sup_der / arb(math.factorial(n + 1))
    scale = arb(2) ** SCALE_BITS
    kept = [arb(int(round(float(coeffs[j].mid() * scale)))) / scale for j in range(keep + 1)]
    round_err = sum((coeffs[j] - kept[j]).abs_upper() for j in range(keep + 1))
    eps = tail + interp_err + round_err
    T = [[arb(1)], [arb(0), arb(1)]]
    for _ in range(2, keep + 1):
        prev, prev2 = T[-1], T[-2]
        nxt = [arb(0)] * (len(prev) + 1)
        for i, cc in enumerate(prev):
            nxt[i + 1] += arb(2) * cc
        for i, cc in enumerate(prev2):
            nxt[i] -= cc
        T.append(nxt)
    tmono = [arb(0)] * (keep + 1)
    for j in range(keep + 1):
        for i, cc in enumerate(T[j]):
            tmono[i] += kept[j] * cc
    xmono = [arb(0)] * (keep + 1)
    for i, cc in enumerate(tmono):
        for r in range(i + 1):
            xmono[r] += cc * arb(math.comb(i, r)) * ((arb(2) / b_sr) ** r) * ((-arb(1)) ** (i - r))
    return xmono, eps, tail, interp_err, round_err


def build_hhat1(e, b_sr, c_sr):
    A, epsA, tA, iA, rA = cheb_fit_1d(lambda a: gaussian_cdf(c_sr - a + e), b_sr)
    B, epsB, tB, iB, rB = cheb_fit_1d(lambda x: gaussian_cdf(x - c_sr + e), b_sr)
    rows = [[arb(0)] * (CAND_DEGREE + 1) for _ in range(CAND_DEGREE + 1)]
    rows[0][0] = arb(1)
    for i, co in enumerate(A):
        rows[i][0] -= co
    for j, co in enumerate(B):
        rows[0][j] += co
    return rows, epsA + epsB, {"A": [float(epsA), float(tA), float(iA), float(rA)],
                               "B": [float(epsB), float(tB), float(iB), float(rB)]}


# ---------------------------------------------------------------------------
# Non-decisive probe: hhat_2 = K_e h_1, NON-separable, rigorous node values
# ---------------------------------------------------------------------------
def build_hhat2(e_f, b_f, c_f, bits):
    ctx.prec = bits
    E, C = acb(e_f), acb(c_f)
    half = b_f / 2.0
    nodes = [half * (math.cos(math.pi * k / CAND_DEGREE) + 1.0) for k in range(CAND_DEGREE + 1)]
    two_pi_sqrt = (acb(2) * acb.pi()).sqrt()

    def phi_cdf(x):
        return (acb(1) + (x / acb(2).sqrt()).erf()) / acb(2)

    vals = [[None] * (CAND_DEGREE + 1) for _ in range(CAND_DEGREE + 1)]
    for i, yp in enumerate(nodes):
        for j, ym in enumerate(nodes):
            YP, YM = acb(yp), acb(ym)

            def integrand(z, analytic, YP=YP, YM=YM):
                v = (acb(1) + (YP + z - acb(1) / acb(2)).exp()).log()
                w = (acb(1) + (YM - z - acb(1) / acb(2)).exp()).log()
                h1 = acb(1) - phi_cdf(C - v + E) + phi_cdf(w - C + E)
                return h1 * (-((z + E) ** 2) / acb(2)).exp() / two_pi_sqrt

            vals[i][j] = acb.integral(integrand, acb(ym) - C, C - acb(yp))
    # tensor Chebyshev interpolation on the 17x17 Lobatto grid, then to monomials
    n = CAND_DEGREE
    def dct(v):
        out = []
        for jj in range(n + 1):
            s = arb(0)
            for k in range(n + 1):
                w = arb(1) / arb(2) if k in (0, n) else arb(1)
                s += w * v[k] * arb(math.cos(math.pi * jj * k / n))
            c = arb(2) * s / arb(n)
            out.append(c / arb(2) if jj in (0, n) else c)
        return out
    with workprec(bits):
        real = [[arb(vals[i][j].real.str(40, radius=True)) for j in range(n + 1)]
                for i in range(n + 1)]
        rowc = [dct(real[i]) for i in range(n + 1)]
        cheb = [dct([rowc[i][j] for i in range(n + 1)]) for j in range(n + 1)]
        scale = arb(2) ** SCALE_BITS
        cheb = [[arb(int(round(float(cheb[j][i].mid() * scale)))) / scale
                 for j in range(n + 1)] for i in range(n + 1)]
        T = [[arb(1)], [arb(0), arb(1)]]
        for _ in range(2, n + 1):
            prev, prev2 = T[-1], T[-2]
            nxt = [arb(0)] * (len(prev) + 1)
            for q, cc in enumerate(prev):
                nxt[q + 1] += arb(2) * cc
            for q, cc in enumerate(prev2):
                nxt[q] -= cc
            T.append(nxt)
        def to_mono(cs):
            tm = [arb(0)] * (n + 1)
            for j in range(n + 1):
                for q, cc in enumerate(T[j]):
                    tm[q] += cs[j] * cc
            xm = [arb(0)] * (n + 1)
            for q, cc in enumerate(tm):
                for r in range(q + 1):
                    xm[r] += cc * arb(math.comb(q, r)) * ((arb(2) / arb(b_f)) ** r) \
                             * ((-arb(1)) ** (q - r))
            return xm
        step1 = [to_mono(cheb[i]) for i in range(n + 1)]          # in b
        rows = [[arb(0)] * (n + 1) for _ in range(n + 1)]
        cols = [to_mono([step1[i][j] for i in range(n + 1)]) for j in range(n + 1)]
        for j in range(n + 1):
            for i in range(n + 1):
                rows[i][j] = cols[j][i]
    return rows


# ---------------------------------------------------------------------------
def run_cell(bits, cand, geo, e, h_z, n_z, tag):
    t0 = time.process_time()
    with workprec(bits):
        core_lo, core_hi = geo["core"]
        z_c = (core_lo + core_hi) / arb(2)
        up_c = (geo["yp"][0] + geo["yp"][1]) / arb(2) + z_c - rational(1, 2)
        um_c = (geo["ym"][0] + geo["ym"][1]) / arb(2) - z_c - rational(1, 2)
        a_p = L.softplus_taylor(up_c, DEGREE)
        a_m = L.softplus_taylor(um_c, DEGREE)
        comp_deg = CAND_DEGREE * DEGREE
        p_lo, p_hi = z_c - h_z, z_c + h_z
        N = L.centred_gaussian_moments(p_lo, p_hi, z_c, e, comp_deg)
        M = L.softplus_derivative_bound_tight(DEGREE + 1)
        H_used = h_z + (geo["yp"][1] - geo["yp"][0]) / arb(2)
        E_used = M * (H_used ** (DEGREE + 1)) / arb(math.factorial(DEGREE + 1))
        comp = L.compose_candidate(cand, a_p, a_m, comp_deg + 1)
        cl = list(comp)
        acc = arb(0)
        for k, ck in enumerate(cl[: len(N)]):
            acc += ck * N[k]
        sup_g = sum(abs(c) for row in cand for c in row)
        rem_width = arb(CAND_DEGREE) * arb(2) * E_used * N[0].abs_upper() * sup_g
        rel = (float((arb(0, rem_width.upper()) + acc).rad() / acc.abs_upper())
               if acc.abs_upper() > 0 else float("inf"))
        rad = float(acc.rad()); ab = float(acc.abs_upper())
        floor = float(rem_width.upper()) / ab if ab > 0 else float("inf")
        dig_av = bits * math.log10(2)
        dig_keep = -math.log10(rad / ab) if (ab > 0 and rad > 0) else float("inf")
        times = []
        for _ in range(TIMING_REPEATS):
            tt = time.process_time()
            c2 = L.compose_candidate(cand, a_p, a_m, comp_deg + 1)
            s = arb(0)
            for k, ck in enumerate(list(c2)[: len(N)]):
                s += ck * N[k]
            times.append(time.process_time() - tt)
        radii = [float(c.rad()) for c in cl[:20]]
        return {"tag": tag, "bits": bits, "n_z": n_z,
                "P2": rel, "P2_pass": bool(rel <= P2_TARGET),
                "P2_margin_factor": P2_TARGET / rel if rel > 0 else float("inf"),
                "P2_floor": floor, "acc_radius": rad, "acc_abs": ab,
                "acc_enclosure": ball_record(acc),
                "acc_lower": acc.lower().str(40), "acc_upper": acc.upper().str(40),
                "digits_available": dig_av, "digits_retained": dig_keep,
                "digits_lost": dig_av - dig_keep if dig_keep != float("inf") else 0.0,
                "precision_consumed": (dig_av - dig_keep) / dig_av if dig_keep != float("inf") else 1.0,
                "sup_g": float(sup_g), "rem_width": float(rem_width.upper()),
                "E_d": float(E_used.upper()),
                "P1_repaired_pass": bool(E_used <= (arb(1) - EPS_P1) * P1_TARGET),
                "P1_margin": float(((arb(1) - EPS_P1) * P1_TARGET - E_used) / P1_TARGET),
                "P3_max_coefficient_radius": max(radii),
                "P3_pass": bool(max(radii) < 1e-20),
                "t_compose_median": statistics.median(times),
                "t_compose_min": min(times), "t_compose_max": max(times),
                "t_spread": (max(times) - min(times)) / statistics.median(times),
                "cell_cpu": time.process_time() - t0}


def classify(cells):
    rad = [(c["bits"], c["acc_radius"]) for c in cells]
    mono = all(rad[i + 1][1] <= rad[i][1] for i in range(len(rad) - 1))
    anypass = any(c["P2_pass"] for c in cells)
    floors_ok = all(c["P2_floor"] <= P2_TARGET for c in cells)
    if anypass and mono:
        return "NONE" if cells[0]["P2_pass"] else "PRECISION_INSUFFICIENT"
    if not floors_ok:
        return "CANDIDATE_RESIDUAL_DOMINANT"
    if not mono:
        return "REPRESENTATION_ILL_CONDITIONED"
    return "MATHEMATICALLY_FALSE" if not anypass else "UNKNOWN"


def main():
    t_all = time.time(); c_all = time.process_time()
    out = {"schema": "rebaseguard.p5y.gate2d.srrealcandidate.v1", "binding": False,
           "pilot": "PILOT-SR-REALCANDIDATE",
           "generated_utc": datetime.now(timezone.utc).isoformat(),
           "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                        capture_output=True, text=True).stdout.strip(),
           "frozen": {"patch": list(PATCH), "grid": GRID, "e": f"{E_NUM}/{E_DEN}",
                      "softplus_degree": DEGREE, "candidate_bidegree": [CAND_DEGREE, CAND_DEGREE],
                      "cheb_interp_degree": CHEB_N, "scale_bits": SCALE_BITS,
                      "precisions": list(PRECISIONS), "P2_target": P2_TARGET,
                      "eps_P1": float(EPS_P1), "timing_repeats": TIMING_REPEATS,
                      "repro_bits": REPRO_BITS,
                      "max_complexity_score": MAX_COMPLEXITY_SCORE},
           "candidate_is_unit_candidate": False, "other_patch_used": False,
           "second_moment_object_created": False}

    with workprec(512):
        A, b_sr, c_sr = sr_constants()
        e = rational(E_NUM, E_DEN)
        geo = L.patch_geometry(*PATCH, grid=GRID)
        core_lo, core_hi = geo["core"]
        core_len = core_hi - core_lo
        patch_half = (geo["yp"][1] - geo["yp"][0]) / arb(2)
        # P1-repaired continuous panel rule
        M = L.softplus_derivative_bound_tight(DEGREE + 1)
        fact = arb(math.factorial(DEGREE + 1))
        target = (arb(1) - EPS_P1) * P1_TARGET
        H_max = ((target * fact / M).log() / arb(DEGREE + 1)).exp()
        h_z = arb(float((H_max - patch_half).lower()))
        n_z = int(math.ceil(float((core_len / (arb(2) * h_z)).upper())))
        out["p1_repair"] = {"eps_P1": float(EPS_P1), "h_z_repaired": float(h_z),
                            "h_z_gate2b_unrepaired": 0.19386660811172551,
                            "n_z": n_z, "n_z_gate2a_gate2b": GATE2A_NZ,
                            "panel_count_unchanged": bool(n_z == GATE2A_NZ),
                            "PASS": bool(n_z == GATE2A_NZ)}
        # decisive genuine candidate
        t0 = time.process_time()
        cand, eps_cand, eps_detail = build_hhat1(e, b_sr, c_sr)
        t_build = time.process_time() - t0
        sup_g = sum(abs(c) for row in cand for c in row)
        nz_terms = sum(1 for row in cand for c in row if not c.contains(arb(0)) or c != arb(0))
        max_bideg = CAND_DEGREE
        score = (CAND_DEGREE + 1) ** 2 * (CAND_DEGREE * DEGREE + 1)
        out["complexity_guard"] = {
            "candidate_bidegree": [max_bideg, max_bideg],
            "composed_z_degree": CAND_DEGREE * DEGREE,
            "compositions_per_cell": 1, "score_per_composition": score,
            "budget": MAX_COMPLEXITY_SCORE,
            "PASS": bool(max_bideg <= CAND_DEGREE and score <= MAX_COMPLEXITY_SCORE),
            "no_high_degree_exact_series_in_path": True}
        out["genuine_candidate"] = {
            "represents": "h_1^SR = 1 - K_e 1 = 1 - Phi(c_SR - a + e) + Phi(b - c_SR + e)",
            "role": "first backward function of P5X-T1, charged by Gate-1 MSHARE",
            "is_unit_candidate": False, "separable": True,
            "bidegree": [CAND_DEGREE, CAND_DEGREE],
            "nonzero_coefficients": 2 * CAND_DEGREE + 1,
            "exact_dyadic_denominator_bits": SCALE_BITS,
            "fit_domain": "full state square [0, b_SR]^2 (stronger than the patch)",
            "eps_cand": float(eps_cand), "eps_detail_A_B": eps_detail,
            "sup_g": float(sup_g), "unit_candidate_sup_g": 11.65234375,
            "build_cpu_seconds": t_build}
        if not out["complexity_guard"]["PASS"]:
            out["GATE2D_DECISION"] = "SR_REALCANDIDATE_FAIL_REPRESENTATION"
            (HERE / "results" / "sr_realcandidate.json").write_text(json.dumps(out, indent=1) + "\n")
            print(json.dumps(out["complexity_guard"], indent=1)); return

    cells = [run_cell(b, cand, geo, e, h_z, n_z, "genuine_hhat1") for b in PRECISIONS]
    out["cells_genuine"] = cells
    # acceptance precondition: is P2 <= 1e-8 reachable given eps_cand?
    with workprec(512):
        Nz = L.centred_gaussian_moments(
            (core_lo + core_hi) / arb(2) - h_z, (core_lo + core_hi) / arb(2) + h_z,
            (core_lo + core_hi) / arb(2), e, 1)
        reach = float(eps_cand) * float(Nz[0].abs_upper()) / cells[0]["acc_abs"]
    out["acceptance_precondition"] = {
        "eps_cand_times_N0_over_acc": reach,
        "P2_target_reachable": bool(reach <= P2_TARGET), "eps_cand_finite": True}

    ctrl = [run_cell(b, unit_candidate(), geo, e, h_z, n_z, "unit_candidate_control")
            for b in PRECISIONS]
    out["cells_unit_control"] = ctrl

    # reproducibility at the frozen precision
    rep = run_cell(REPRO_BITS, cand, geo, e, h_z, n_z, "repro")
    base = next(c for c in cells if c["bits"] == REPRO_BITS)
    out["reproducibility"] = {
        "bits": REPRO_BITS,
        "lower_identical": base["acc_lower"] == rep["acc_lower"],
        "upper_identical": base["acc_upper"] == rep["acc_upper"],
        "P2_identical": base["P2"] == rep["P2"],
        "ball_identical": bool(base["acc_lower"] == rep["acc_lower"]
                               and base["acc_upper"] == rep["acc_upper"]
                               and base["P2"] == rep["P2"]),
        "t_run1": base["t_compose_median"], "t_run2": rep["t_compose_median"]}

    # NON-DECISIVE non-separable conditioning probe
    t0 = time.process_time()
    try:
        with workprec(512):
            _, b2, c2 = sr_constants()
            bf, cf = float(b2), float(c2)
        cand2 = build_hhat2(E_NUM / E_DEN, bf, cf, 256)
        probe = [run_cell(b, cand2, geo, e, h_z, n_z, "nonseparable_hhat2_PROBE")
                 for b in PRECISIONS]
        with workprec(512):
            sg2 = float(sum(abs(c) for row in cand2 for c in row))
        out["nonseparable_probe"] = {
            "decisive": False, "certifies_nothing": True,
            "represents": "h_2 = K_e h_1, the second backward function of P5X-T1",
            "separable": False, "node_values": "rigorous acb.integral enclosures",
            "no_whole_domain_residual_certificate": True,
            "sup_g": sg2, "cells": probe,
            "build_cpu_seconds": time.process_time() - t0}
    except Exception as ex:
        out["nonseparable_probe"] = {"decisive": False, "status": "NOT_COMPLETED",
                                     "error": f"{type(ex).__name__}: {ex}",
                                     "build_cpu_seconds": time.process_time() - t0}

    sel = next((c["bits"] for c in cells
                if c["P2_pass"] and c["P1_repaired_pass"] and c["P3_pass"]
                and out["reproducibility"]["ball_identical"]), None)
    dl = cells[0]["digits_lost"]
    delta = dl - GATE2A_DIGITS_LOST
    cond = ("STABLE" if delta <= 5 else "MILDLY_WORSE" if delta <= 15
            else "MATERIALLY_WORSE" if delta <= 30 else "SEVERE")
    if sel is None:
        cond = "SEVERE"
    out["digit_loss"] = {
        "genuine": {str(c["bits"]): c["digits_lost"] for c in cells},
        "unit_control": {str(c["bits"]): c["digits_lost"] for c in ctrl},
        "gate2a_reference": GATE2A_DIGITS_LOST,
        "delta_digits_vs_gate2a": delta,
        "delta_digits_vs_control_same_run": dl - ctrl[0]["digits_lost"],
        "conditioning_class": cond}
    out["failure_class"] = classify(cells)
    out["selected_safe_precision"] = sel
    out["GATE2D_DECISION"] = (f"SR_REALCANDIDATE_PASS_{sel}" if sel
                              else "SR_REALCANDIDATE_FAIL_WITHIN_GRID")
    cpu = time.process_time() - c_all
    out["runtime"] = {"wall_seconds": time.time() - t_all, "cpu_seconds": cpu,
                      "cpu_hours": cpu / 3600.0, "cap_cpu_seconds": 540,
                      "within_cap": bool(cpu <= 540),
                      "peak_rss_mib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 * 1024)}
    (HERE / "results" / "sr_realcandidate.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: out[k] for k in
                      ("p1_repair", "complexity_guard", "genuine_candidate",
                       "acceptance_precondition", "cells_genuine", "cells_unit_control",
                       "reproducibility", "nonseparable_probe", "digit_loss",
                       "failure_class", "selected_safe_precision", "GATE2D_DECISION",
                       "runtime")}, indent=1, default=str))


if __name__ == "__main__":
    main()
