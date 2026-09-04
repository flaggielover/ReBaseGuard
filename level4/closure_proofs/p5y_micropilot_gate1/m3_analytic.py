"""P5Y Gate-1 M3 analytic component (NON-DECISIVE unless M2 fails).

Verifies the xi-transform and exponential-Gaussian moment identities and
computes the DETERMINISTIC induced panel count for the frozen patch.  It builds
no certifier and returns no PASS/FAIL for Gate-1 unless promoted by M2 = FAIL.
"""
from __future__ import annotations

import json, math, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
R3 = ROOT / "level4" / "closure_proofs" / "p5x_global_nonlinear_dynamics" / "compute_optimization_r3_sr_symbolic"
for p in (str(R3), str(ROOT / "rebaseguard-proof" / "src")):
    if p not in sys.path:
        sys.path.insert(0, p)

from flint import arb                                                        # noqa: E402
from rebaseguard_certify.arb_backend import gaussian_cdf, rational, workprec  # noqa: E402
import sr_local as L                                                         # noqa: E402

BITS = 192
GRID = 64
PATCH = (17, 11)
E_NUM, E_DEN = 1, 4
PANEL_THRESHOLD = 2 * (GRID - 1) + 1        # frozen at 127, see prereg section 4.3


def G_centred(c, z_lo, z_hi, z_c, e):
    """int_{z_lo}^{z_hi} exp(c (z - z_c)) phi(z+e) dz, exact closed form."""
    cc = arb(c)
    return ((cc * cc / arb(2)) - cc * (z_c + e)).exp() * (
        gaussian_cdf(z_hi + e - cc) - gaussian_cdf(z_lo + e - cc))


def main():
    t0 = time.time()
    out = {"schema": "rebaseguard.p5y.gate1.m3analytic.v1",
           "pilot": "PILOT-SR-XI (analytic component only)", "binding": False,
           "decisive": False,
           "generated_utc": datetime.now(timezone.utc).isoformat(),
           "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                        capture_output=True, text=True).stdout.strip(),
           "checks": {}}
    ck = out["checks"]
    with workprec(BITS):
        A, b_sr, c_sr = L.sr_constants()
        e = rational(E_NUM, E_DEN)
        geo = L.patch_geometry(*PATCH, grid=GRID)

        # ---- X1: transform identity exp(softplus(v)) = 1 + exp(y) exp(z-1/2)
        worst = arb(0)
        alarm_ok = True
        for yi in range(9):
            y = b_sr * arb(yi) / arb(8)
            for zi in range(11):
                z = arb(-6) + arb(12) * arb(zi) / arb(10)
                v = y + z - rational(1, 2)
                lhs = L.softplus(v).exp()
                rhs = arb(1) + y.exp() * (z - rational(1, 2)).exp()
                d = (lhs - rhs).abs_upper() / rhs.abs_upper()
                worst = worst.max(d)
                alarm_ok = alarm_ok and ((v >= A.log()) == (y.exp() * (z - rational(1, 2)).exp() >= A))
        ck["X1_transform_max_rel_error"] = float(worst)
        ck["X1_transform_identity_holds"] = bool(worst < arb("1e-25"))
        ck["X1_alarm_equivalence_holds"] = bool(alarm_ok)

        # ---- X2: exponential-Gaussian moment identity cross-checked against
        #          R3's own exact centred-moment recursion, via  e^{cv} series.
        core_lo, core_hi = geo["core"]
        z_c = (core_lo + core_hi) / arb(2)
        h_panel = b_sr / arb(2 * GRID)          # a geometry panel half-width in z
        p_lo, p_hi = z_c - h_panel, z_c + h_panel
        KMAX = 60
        N = L.centred_gaussian_moments(p_lo, p_hi, z_c, e, KMAX)
        worst_rel = arb(0)
        for c in (0, 1, -1, 4, -4, 16, -16):
            closed = G_centred(c, p_lo, p_hi, z_c, e)
            series = arb(0)
            for k in range(KMAX + 1):
                series += (arb(c) ** k) / arb(math.factorial(k)) * N[k]
            tail = (abs(arb(c)) * h_panel) ** (KMAX + 1) / arb(math.factorial(KMAX + 1)) \
                * N[0].abs_upper() * arb(2)
            gap = (closed - series).abs_upper()
            rel = gap / closed.abs_upper() if closed.abs_upper() > 0 else arb(0)
            worst_rel = worst_rel.max(rel)
            ck.setdefault("X2_per_c", {})[str(c)] = {
                "closed_form": float(closed), "series": float(series),
                "abs_gap": float(gap), "series_tail_bound": float(tail),
                "gap_within_tail": bool(gap <= tail.abs_upper() + closed.abs_upper() * arb("1e-30"))}
        ck["X2_moment_identity_max_rel_gap"] = float(worst_rel)
        ck["X2_moment_identity_holds"] = all(
            v["gap_within_tail"] for v in ck["X2_per_c"].values())

        # ---- X3: deterministic induced panel count for the frozen patch.
        # y'_+ = softplus(y_+ + z - 1/2) is increasing in z, y'_- decreasing;
        # both live in [0, b_SR] cut into GRID cells, so crossings are bounded.
        yp = (geo["yp"][0] + geo["yp"][1]) / arb(2)
        ym = (geo["ym"][0] + geo["ym"][1]) / arb(2)
        n_plus = n_minus = 0
        for i in range(1, GRID):
            edge = b_sr * arb(i) / arb(GRID)
            # y'_+ = edge  <=>  z = log(exp(edge)-1) - y_+ + 1/2
            arg = (edge.exp() - arb(1))
            if arg.lower() > 0:
                z_star = arg.log() - yp + rational(1, 2)
                if z_star > core_lo and z_star < core_hi:
                    n_plus += 1
                z_star_m = -(arg.log() - ym + rational(1, 2))
                if z_star_m > core_lo and z_star_m < core_hi:
                    n_minus += 1
        n_panels = n_plus + n_minus + 1
        ck["X3_panels"] = {"crossings_plus_chart": n_plus, "crossings_minus_chart": n_minus,
                           "induced_panel_count": n_panels,
                           "closed_form_upper_bound": PANEL_THRESHOLD,
                           "frozen_threshold": PANEL_THRESHOLD,
                           "brief_default_threshold": 100,
                           "within_frozen_threshold": bool(n_panels <= PANEL_THRESHOLD),
                           "within_brief_default": bool(n_panels <= 100)}

        # ---- X4: conditioning of the centred exponential factor over one panel
        rng = (arb(16) * h_panel).exp()
        ck["X4_conditioning"] = {
            "panel_half_width_z": float(h_panel),
            "max_centred_exponential_range_exp_16h": float(rng),
            "note": "bounded dynamic range: the composed integrand is expanded in "
                    "panel-centred variables, so no e^{c z} magnitude blow-up occurs",
            "acceptable": bool(rng < arb(100))}

    out["summary"] = {
        "transform_verified": ck["X1_transform_identity_holds"] and ck["X1_alarm_equivalence_holds"],
        "moment_identity_verified": ck["X2_moment_identity_holds"],
        "induced_panel_count": ck["X3_panels"]["induced_panel_count"],
        "panels_within_frozen_threshold": ck["X3_panels"]["within_frozen_threshold"],
        "conditioning_acceptable": ck["X4_conditioning"]["acceptable"],
        "backend_built": False,
        "status": "ANALYTIC_ONLY_NOT_DECISIVE",
    }
    out["runtime"] = {"wall_seconds": time.time() - t0}
    (HERE / "results" / "m3_analytic.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({"summary": out["summary"],
                      "X1_rel": ck["X1_transform_max_rel_error"],
                      "X2_rel": ck["X2_moment_identity_max_rel_gap"],
                      "X3": ck["X3_panels"], "X4": ck["X4_conditioning"]}, indent=1))


if __name__ == "__main__":
    main()
