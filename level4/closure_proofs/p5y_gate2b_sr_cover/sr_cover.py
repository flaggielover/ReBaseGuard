"""P5Y Gate-2B: PILOT-SR-COVER.

Geometry and counting only.  No certified function solve is invoked anywhere in
this module: the heaviest operation is a 200x200 Bellman envelope iteration,
which is the same object R1 already uses for the CUSUM resolvent.

Three measurements:
  1. C_SR(e), drift-explicit, on the AUTHORITATIVE SR chart (not a CUSUM
     surrogate), cross-checked at e = 0 against the certified SR component;
  2. the production sub-cell cover over [0, e_star_SR] by a full deterministic
     greedy walk under a certified monotone envelope;
  3. the live patch count from the EXACT multiplicative invariant of the SR
     two-chart recursion, plus the per-patch panel count n_z(i,j).
"""
from __future__ import annotations

import json, math, resource, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in (str(ROOT / "rebaseguard-proof" / "src"),):
    if p not in sys.path:
        sys.path.insert(0, p)

from flint import arb, arb_mat                                               # noqa: E402
from rebaseguard_certify.arb_backend import (                                # noqa: E402
    ball_record, gaussian_cdf, rational, workprec,
)

# ------------------------------------------------- FROZEN (GATE2B_PREREG §2-§7)
A_NUM, A_DEN = 4581762885148045, 8796093022208
CELLS, N_MAX, BITS = 200, 250, 192
GRID = 64                                   # nominal state patches per axis
DEGREE = 8                                  # Gate-1/2A selected; degree 10 forbidden here
H_Z = 0.19386660811172551                   # Gate-1 degree-8 continuous panel rule
E_GRID_POINTS = 199                         # e_i = e_star*(i/199)^3, i = 0..199
T_PANEL = 0.006091                          # Gate-2A, degree 8 @ 256 bits, incl. moments
N_FUNCTIONS = 49                            # 24.5 units x 2 (value + derivative)
CUSUM_UNIT_CPU_H = 2.862480884236111        # Gate-1 measured
C3, OVERHEAD = 0.17, 0.15
CERT_Q_SAFE = (19, 100)                     # sr_monotone_contraction.json
CERT_RESOLVENT = (25000, 19)
SENSITIVITY = 0.05                          # predeclared +/-5% envelope diagnostic


def sr_constants():
    A = arb(A_NUM) / arb(A_DEN)
    return A, (arb(1) + A).log(), A.log() + rational(1, 2)   # A, b_SR, c_SR


def sr_drift_monotone_resolvent(e: arb, *, cells: int = CELLS, n_max: int = N_MAX):
    """C_SR(e) >= sup_x E_{x,e}[tau] on the aligned one-sided SR chart.

    `e` must be the SMALLEST |e| of the region it is used for (M2).
    Returns (bound, t_star, H_t_star_lower, H_at_n_max, mass_ok).
    """
    A, b_sr, _ = sr_constants()
    logA = A.log()
    x = [b_sr * arb(i) / arb(cells) for i in range(cells)]        # LEFT endpoints (M1)
    # cell j receives y' in [x_j, x_{j+1}) <=> y+inc in [u_j, u_{j+1}); u_0 = -inf
    u = [None] + [(xx.exp() - arb(1)).log() for xx in x[1:]] + [logA]
    trans = arb_mat(cells, cells)
    reward = arb_mat(cells, 1)
    one = arb(1)
    mass_ok = True
    for i in range(cells):
        m = x[i] + e - rational(1, 2)
        reward[i, 0] = one - gaussian_cdf(logA - m)              # alarm this step
        prev = arb(0)
        for j in range(cells):
            hi = gaussian_cdf(u[j + 1] - m)
            trans[i, j] = hi - prev
            prev = hi
        tot = reward[i, 0]
        for j in range(cells):
            tot += trans[i, j]
        if not tot.contains(one):
            mass_ok = False
    H = arb_mat(cells, 1)
    best = None
    H_at_n = None
    for t in range(1, n_max + 1):
        H = reward + trans * H
        lo = H[0, 0].lower()
        if t == n_max:
            H_at_n = arb(lo)
        if not lo > 0:
            continue
        b = arb(t) / lo
        if best is None or b.upper() < best[0].upper():
            best = (b, t, arb(lo))
    if best is None:
        raise ArithmeticError("no positive hitting lower bound")
    return best[0], best[1], best[2], H_at_n, mass_ok


def cover_walk(env_e, env_C, e_star, a, scale=1.0):
    """Greedy production walk.  Returns the sub-cell list."""
    cells = []
    e = 0.0
    k = 0
    guard = 0
    while e < e_star and guard < 2_000_000:
        guard += 1
        while k + 1 < len(env_e) and env_e[k + 1] <= e:
            k += 1
        C = env_C[k] * scale
        h = 1.0 / (4.0 * a * C)
        nxt = min(e + 2.0 * h, e_star)
        if nxt <= e:
            raise ArithmeticError("walk stalled")
        cells.append((e, nxt))
        e = nxt
    if e < e_star:
        raise ArithmeticError("walk did not reach e_star")
    return cells


def patch_geometry_counts(b_sr_f, c_sr_f, A_f, grid=GRID, h_z=H_Z):
    """Live-patch classification from the EXACT multiplicative invariant."""
    d = b_sr_f / grid
    inv_e = math.exp(-1.0)
    hi_lim = (1.0 + A_f) ** 2 * inv_e
    live, dead_low, dead_high, x0_patch = [], 0, 0, None
    for i in range(grid):
        a1, a2 = i * d, (i + 1) * d
        for j in range(grid):
            b1, b2 = j * d, (j + 1) * d
            pmax = (math.exp(a2) - 1.0) * (math.exp(b2) - 1.0)
            pmin = (math.exp(a1) - 1.0) * (math.exp(b1) - 1.0)
            is_x0 = (i == 0 and j == 0)
            if is_x0:
                x0_patch = (i, j)
            if pmax < inv_e and not is_x0:
                dead_low += 1
                continue
            if pmin > hi_lim:
                dead_high += 1
                continue
            core_len = 2.0 * c_sr_f - a2 - b2
            n_z = math.ceil(core_len / (2.0 * h_z))
            live.append({"i": i, "j": j, "core_len": core_len, "n_z": n_z,
                         "panels": n_z + 2, "contains_x0": is_x0})
    return live, dead_low, dead_high, x0_patch


def forward_invariance_check(b_sr_f, A_f, samples=64):
    """{x_0} u R is forward invariant under q_SR: P' = xi+ xi- /e >= 1/e."""
    inv_e = math.exp(-1.0)
    hi_lim = (1.0 + A_f) ** 2 * inv_e
    worst_lo, worst_hi, ok = math.inf, 0.0, True
    for si in range(samples + 1):
        for sj in range(samples + 1):
            yp = b_sr_f * si / samples
            ym = b_sr_f * sj / samples
            xp, xm = math.exp(yp), math.exp(ym)
            if not (1.0 <= xp <= 1.0 + A_f and 1.0 <= xm <= 1.0 + A_f):
                continue
            Pn = xp * xm * inv_e          # (xi+' -1)(xi-' -1), independent of z
            worst_lo = min(worst_lo, Pn)
            worst_hi = max(worst_hi, Pn)
            if Pn < inv_e * (1 - 1e-12) or Pn > hi_lim * (1 + 1e-12):
                ok = False
    return {"forward_invariant": bool(ok), "min_image_product": worst_lo,
            "max_image_product": worst_hi, "lower_constraint": inv_e,
            "upper_constraint": hi_lim,
            "note": "z cancels exactly in (xi+'-1)(xi-'-1) = xi+ xi- / e"}


def main():
    t_all = time.time(); c0 = time.process_time()
    out = {"schema": "rebaseguard.p5y.gate2b.srcover.v1", "binding": False,
           "pilot": "PILOT-SR-COVER", "production_solve_invoked": False,
           "generated_utc": datetime.now(timezone.utc).isoformat(),
           "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                        capture_output=True, text=True).stdout.strip(),
           "frozen": {"cells": CELLS, "n_max": N_MAX, "bits": BITS, "grid": GRID,
                      "degree": DEGREE, "h_z": H_Z, "t_panel": T_PANEL,
                      "n_functions": N_FUNCTIONS, "e_grid_points": E_GRID_POINTS + 1}}

    with workprec(BITS):
        A, b_sr, c_sr = sr_constants()
        e_star = c_sr
        a_const = arb(2) / (arb(2) * arb.pi()).sqrt()
        out["e_star_SR"] = c_sr.str(30)
        out["b_SR"] = b_sr.str(30)
        out["a_constant_2phi0"] = a_const.str(30)

        # ---- (1) C_SR on the frozen grid + mandatory e=0 cross-check
        e_star_f = float(e_star)
        grid_e = [e_star_f * (i / E_GRID_POINTS) ** 3 for i in range(E_GRID_POINTS + 1)]
        Cvals, trail = [], []
        for idx, ef in enumerate(grid_e):
            eb = arb(ef)
            bound, t_star, h_star, H_n, mass_ok = sr_drift_monotone_resolvent(eb)
            Cvals.append(float(bound.upper()))
            if idx == 0:
                out["cross_check_e0"] = {
                    "H_250_lower": float(H_n.lower()),
                    "certified_q_safe": CERT_Q_SAFE[0] / CERT_Q_SAFE[1],
                    "H_250_ge_q_safe": bool(H_n.lower() >= arb(CERT_Q_SAFE[0]) / arb(CERT_Q_SAFE[1])),
                    "C_SR_0": float(bound.upper()),
                    "certified_resolvent": CERT_RESOLVENT[0] / CERT_RESOLVENT[1],
                    "C_SR_0_le_certified": bool(bound <= arb(CERT_RESOLVENT[0]) / arb(CERT_RESOLVENT[1])),
                    "t_star": t_star, "mass_balance_ok": bool(mass_ok)}
            if mass_ok is False:
                raise ArithmeticError("row mass balance failed")
        out["C_SR_grid"] = {"e": grid_e, "C": Cvals}

        # representative points (explanatory only)
        rep = {}
        for name, ef in (("0", 0.0), ("1/4", 0.25), ("1/2", 0.5), ("1", 1.0),
                         ("2", 2.0), ("e_star", e_star_f)):
            bound, t_star, _, _, _ = sr_drift_monotone_resolvent(arb(ef))
            Cf = float(bound.upper())
            rep[name] = {"e": ef, "C_SR": Cf, "t_star": t_star,
                         "h": 1.0 / (4.0 * float(a_const) * Cf)}
        out["representative"] = rep

    a_f = float(a_const)
    # ---- (2) cover walk: upper (left-endpoint envelope) and lower (right-endpoint)
    up = cover_walk(grid_e, Cvals, e_star_f, a_f)
    env_lo = Cvals[1:] + [Cvals[-1]]
    lo = cover_walk(grid_e, env_lo, e_star_f, a_f)
    widths = sorted(b - aa for aa, b in up)
    n = len(up)
    def frac(lo_e, hi_e):
        return sum(1 for aa, b in up if lo_e <= aa < hi_e) / n
    # outer cells: maximal runs whose widths agree within a factor of 2
    outer, cur = [], [up[0]]
    for k in range(1, n):
        w0, w1 = cur[0][1] - cur[0][0], up[k][1] - up[k][0]
        if max(w0, w1) / min(w0, w1) <= 2.0:
            cur.append(up[k])
        else:
            outer.append(cur); cur = [up[k]]
    outer.append(cur)
    dense = max(range(n), key=lambda k: 1.0 / (up[k][1] - up[k][0]))
    out["cover"] = {
        "subcell_count_upper_bound": n, "subcell_count_lower_bound": len(lo),
        "outer_cell_count": len(outer),
        "subcells_per_outer_cell_min": min(len(o) for o in outer),
        "subcells_per_outer_cell_max": max(len(o) for o in outer),
        "width_min": widths[0], "width_median": widths[n // 2], "width_max": widths[-1],
        "densest_subcell_index": dense,
        "densest_region_e": [up[dense][0], up[dense][1]],
        "fraction_in_0_0p5": frac(0.0, 0.5),
        "fraction_in_0p5_2": frac(0.5, 2.0),
        "fraction_in_2_estar": frac(2.0, e_star_f + 1),
        "covers_exactly": bool(abs(up[0][0]) < 1e-15 and abs(up[-1][1] - e_star_f) < 1e-12
                               and all(abs(up[k][1] - up[k + 1][0]) < 1e-15 for k in range(n - 1))),
        "historical_estimate": 835, "ratio_vs_historical": n / 835.0,
        "classification": ("LOWER" if n < 835 * 0.9 else
                           "HIGHER" if n > 835 * 1.1 else "CONSISTENT")}

    # ---- predeclared +/-5% sensitivity (diagnostic only)
    out["sensitivity_5pct"] = {
        "plus_5pct_C": len(cover_walk(grid_e, Cvals, e_star_f, a_f, 1.0 + SENSITIVITY)),
        "minus_5pct_C": len(cover_walk(grid_e, Cvals, e_star_f, a_f, 1.0 - SENSITIVITY)),
        "baseline": n}

    # ---- (3) patch geometry
    b_f, c_f, A_f = float(b_sr), float(c_sr), float(A)
    live, dead_low, dead_high, x0p = patch_geometry_counts(b_f, c_f, A_f)
    nz = [p["n_z"] for p in live]
    panels = sum(p["panels"] for p in live)
    out["patches"] = {
        "nominal": GRID * GRID, "live": len(live),
        "excluded_unreachable_low_product": dead_low,
        "excluded_unreachable_high_product": dead_high,
        "live_fraction": len(live) / (GRID * GRID),
        "x0_patch": list(x0p), "x0_patch_kept_as_reset_state": True,
        "geometry_depends_on_e": False,
        "geometry_depends_on_e_reason": "l, u, q_SR and the invariant contain no e; "
                                        "e enters only the weight phi(z+e)",
        "n_z_min": min(nz), "n_z_max": max(nz), "n_z_mean": sum(nz) / len(nz),
        "n_z_at_gate1_patch_17_11": next(p["n_z"] for p in live if p["i"] == 17 and p["j"] == 11),
        "total_panels_over_live_patches": panels,
        "naive_live_times_28": len(live) * 28,
        "per_patch_saving_factor": len(live) * 28 / panels}
    out["forward_invariance"] = forward_invariance_check(b_f, A_f)

    # ---- P1 headroom repair, estimated analytically, NOT applied
    eps = 1e-3
    Hmax = H_Z + b_f / (2 * GRID)
    Hnew = Hmax * (1 - eps) ** (1.0 / (DEGREE + 1))
    hz_new = Hnew - b_f / (2 * GRID)
    nz_new = sum(math.ceil((2 * c_f - (p["i"] + 1) * b_f / GRID - (p["j"] + 1) * b_f / GRID)
                           / (2 * hz_new)) + 2 for p in live)
    out["p1_headroom_repair_estimate"] = {
        "applied": False, "recommended_epsilon": eps,
        "h_z_current": H_Z, "h_z_repaired": hz_new,
        "relative_h_z_change": (H_Z - hz_new) / H_Z,
        "panels_current": panels, "panels_repaired": nz_new,
        "panel_cost_increase_factor": nz_new / panels}

    # ---- (4) cost model with the corrected sharing
    cpu_sr = n * N_FUNCTIONS * panels * T_PANEL / 3600.0
    cusum_total = CUSUM_UNIT_CPU_H * 24.5
    def band(sr_mult=1.0, m_mult=1.0):
        return (cpu_sr * sr_mult * m_mult + cusum_total * m_mult) * (1 + C3) * (1 + OVERHEAD)
    bands = {
        "optimistic": {"cpu_hours": band(), "assumption": "measured geometry; m>1 per-function cost = m=1"},
        "central": {"cpu_hours": band(1.0, 1.0) * 1.0, "assumption": "measured geometry, degree 8 @ 256 bits"},
        "conservative": {"cpu_hours": band(1.0, 1.5), "assumption": "m>1 functions 1.5x"},
        "worst": {"cpu_hours": band(out["p1_headroom_repair_estimate"]["panel_cost_increase_factor"], 2.0),
                  "assumption": "P1 repair applied AND m>1 functions 2x"}}
    for v in bands.values():
        for cores, eff in ((16, 0.95), (64, 0.90), (128, 0.80)):
            v[f"wall_hours_{cores}_cores"] = v["cpu_hours"] / (cores * eff)
    central = bands["central"]["cpu_hours"]
    feas = ("STRONG" if central <= 5000 else "MODERATE" if central <= 10000
            else "WEAK" if central <= 30000 else "NOT_FEASIBLE")
    out["cost"] = {"cpu_sr_hours": cpu_sr, "cusum_total_hours": cusum_total,
                   "formula": "n_subcells x 49 functions x sum_livepatches(panels) x t_panel",
                   "geometric_cover_multiplied_by_m": False,
                   "bands": bands, "central_cpu_hours": central,
                   "cover_feasibility": feas}

    geometry_sound = bool(out["cross_check_e0"]["H_250_ge_q_safe"]
                          and out["cross_check_e0"]["C_SR_0_le_certified"]
                          and out["cover"]["covers_exactly"]
                          and out["forward_invariance"]["forward_invariant"]
                          and not out["production_solve_invoked"])
    out["geometry_sound"] = geometry_sound
    out["GATE2B_DECISION"] = ("SR_COVER_PASS_MEASURED" if geometry_sound and feas in ("STRONG", "MODERATE")
                              else "SR_COVER_PASS_BUT_COST_HIGH" if geometry_sound
                              else "SR_COVER_FAIL_GEOMETRY")
    cpu = time.process_time() - c0
    out["runtime"] = {"wall_seconds": time.time() - t_all, "cpu_seconds": cpu,
                      "cpu_hours": cpu / 3600.0, "cap_cpu_hours": 0.10,
                      "within_cap": bool(cpu / 3600.0 <= 0.10),
                      "peak_rss_mib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 * 1024)}
    (HERE / "results" / "sr_cover.json").write_text(json.dumps(out, indent=1) + "\n")

    print(json.dumps({k: out[k] for k in ("cross_check_e0", "representative", "cover",
                                          "sensitivity_5pct", "patches", "forward_invariance",
                                          "p1_headroom_repair_estimate")}, indent=1))
    print(json.dumps({"cost": {kk: out["cost"][kk] for kk in
                               ("cpu_sr_hours", "cusum_total_hours", "central_cpu_hours",
                                "cover_feasibility")},
                      "bands": {k: round(v["cpu_hours"]) for k, v in bands.items()},
                      "geometry_sound": geometry_sound,
                      "GATE2B_DECISION": out["GATE2B_DECISION"],
                      "runtime": out["runtime"]}, indent=1))


if __name__ == "__main__":
    main()
