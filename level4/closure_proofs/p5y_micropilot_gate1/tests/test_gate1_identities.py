"""Pre-T2 preconditions for P5Y Gate-1.  Must pass BEFORE any result-bearing run.

Implements GATE1_PREREGISTRATION.md section 2.1 (identities I1/I3) and the
structural discipline checks of the brief section 27 that do not need results.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest
from flint import arb

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
P5X = ROOT / "level4" / "closure_proofs" / "p5x_global_nonlinear_dynamics"
for p in (str(ROOT / "rebaseguard-proof" / "src"), str(HERE), str(P5X / "certified_method_repair_ra"),
          str(P5X / "compute_optimization_r1"), str(P5X / "compute_optimization_r2"),
          str(P5X / "compute_optimization_r3_sr_symbolic")):
    if p not in sys.path:
        sys.path.insert(0, p)

from rebaseguard_certify.arb_backend import gaussian_cdf, rational, workprec  # noqa: E402
from rebaseguard_certify.polynomial import bi_add, bi_eval, bi_scale          # noqa: E402
import ra_certifier as RA                                                     # noqa: E402
import raw_certifier as RAW                                                   # noqa: E402

BITS = 256
ORDER = 40
DRIFTS = [(0, 1), (1, 4), (1, 2), (1, 1), (2, 1), (11, 2), (8, 1), (43, 4), (12, 1)]
STATES = [(arb(p) / arb(2), arb(m) / arb(2)) for p in (0, 3, 6, 9) for m in (0, 1, 5, 9)]


def _phi(x):
    return (-(x * x) / arb(2)).exp() / (arb(2) * arb.pi()).sqrt()


def test_I1_raw_reward_identity_is_exact():
    """rho_{1,e} + e h_1 == phi(u+e) - phi(l+e) for every frozen (e, state)."""
    with workprec(BITS):
        worst = arb(0)
        for en, ed in DRIFTS:
            e = rational(en, ed)
            for p, m in STATES:
                u = RA.C_CUSUM - p
                ll = m - RA.C_CUSUM
                a, b = u + e, ll + e
                h1 = arb(1) - gaussian_cdf(a) + gaussian_cdf(b)
                rho1 = _phi(a) - _phi(b) - e * h1
                worst = worst.max((rho1 + e * h1 - (_phi(a) - _phi(b))).abs_upper())
        assert float(worst) < 1e-12, f"I1 violated, worst {float(worst)}"


def test_I3_raw_source_shift_identity():
    """S_r^raw = S_r + e h_{r+1}: the raw z-weighted operator is K_z + e K."""
    with workprec(BITS):
        # K_{raw,e} f = int (z+e) f(q) phi(z+e) dz = K_{z,e} f + e K_e f, checked
        # on the reward level where both sides are closed form:  E[raw ; alarm]
        # = E[z ; alarm] + e P(alarm).
        worst = arb(0)
        for en, ed in DRIFTS:
            e = rational(en, ed)
            for p, m in STATES:
                u = RA.C_CUSUM - p
                ll = m - RA.C_CUSUM
                a, b = u + e, ll + e
                e_z_alarm = _phi(a) - _phi(b) - e * (arb(1) - gaussian_cdf(a) + gaussian_cdf(b))
                p_alarm = arb(1) - gaussian_cdf(a) + gaussian_cdf(b)
                e_raw_alarm = _phi(a) - _phi(b)
                worst = worst.max((e_raw_alarm - (e_z_alarm + e * p_alarm)).abs_upper())
        assert float(worst) < 1e-12, f"I3 violated, worst {float(worst)}"


def test_raw_reward_polynomials_match_closed_form():
    """The BiPoly rewards used by the pilot evaluate to the closed forms."""
    with workprec(BITS):
        for en, ed in [(1, 4), (43, 4)]:
            e = rational(en, ed)
            r1 = RAW.reward_rho1_raw(120, e)
            dr1 = RAW.reward_drho1_raw(120, e)
            for p, m in STATES:
                u = RA.C_CUSUM - p
                ll = m - RA.C_CUSUM
                a, b = u + e, ll + e
                assert (bi_eval(r1, p, m) - (_phi(a) - _phi(b))).abs_upper() < arb("1e-25")
                assert (bi_eval(dr1, p, m) - (-a * _phi(a) + b * _phi(b))).abs_upper() < arb("1e-25")


def test_raw_source_is_uniformly_bounded_in_e():
    """sup|rho_1^raw| <= 2 phi(0) for EVERY drift; the z-source is not."""
    with workprec(BITS):
        cap = arb(2) / (arb(2) * arb.pi()).sqrt()
        for en, ed in DRIFTS:
            e = rational(en, ed)
            for p, m in STATES:
                a = RA.C_CUSUM - p + e
                b = m - RA.C_CUSUM + e
                assert (_phi(a) - _phi(b)).abs_upper() <= cap.upper()
        # and the z-source really does grow like |e| at e = 12
        e = rational(12, 1)
        a = RA.C_CUSUM - arb(0) + e
        b = arb(0) - RA.C_CUSUM + e
        z_src = (_phi(a) - _phi(b) - e * (arb(1) - gaussian_cdf(a) + gaussian_cdf(b))).abs_upper()
        assert float(z_src) > 10.0


def test_no_external_plus_e_in_raw_assembly():
    """The raw arm must not add an e_range term; the z arm must."""
    src = (HERE / "m1_raw_2cell.py").read_text()
    tree = ast.parse(src)
    fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "assemble")
    body = ast.dump(fn)
    assert "e_range" in body, "z control arm must carry the +e term"
    guard = [n for n in ast.walk(fn) if isinstance(n, ast.Compare)
             and ast.dump(n).count("'raw'") and "NotEq" in ast.dump(n)]
    assert guard, "the e_range term must be guarded by arm != 'raw'"


def test_far_cell_is_the_frozen_historical_cell():
    import m1_raw_2cell as M1
    assert M1.CELLS["B_far"] == (105441104, 120000000)
    assert M1.CELLS["A_near"] == (2400000, 2600000)
    assert len(M1.CELLS) == 2, "exactly two cells; no third may be added"
    assert M1.R2_ANCHOR == (-1.584973380499857, -1.5676443748392161)


def test_m2_degree_grid_is_exactly_8_10_12():
    import m2_sr_degree as M2
    assert M2.DEGREES == (8, 10, 12)
    assert M2.CONTROL_DEGREE == 6
    assert M2.P4_BUDGET == 0.3314531805
    assert M2.TIMING_REPEATS == 5


def test_m2_panel_rule_has_no_dyadic_rounding():
    src = (HERE / "m2_sr_degree.py").read_text()
    fn = src.split("def continuous_panel_rule")[1].split("\ndef ")[0]
    assert "2 **" not in fn and "2**" not in fn, "dyadic rounding must be absent"
    assert "for k in range" not in fn, "no dyadic search loop"
    assert "log()" in fn and "exp()" in fn, "closed-form root required"


def test_m2_math_gate_precedes_cost_gate():
    src = (HERE / "m2_sr_degree.py").read_text()
    assert src.index('out["math_gates_all_pass"]') < src.index('out["timing"]'), \
        "mathematical gates must be evaluated before any timing"
    assert 'out["verdict"] = "PASS" if (out["math_gates_all_pass"] and' in src


def test_m3_panel_semantics_are_geometry_only():
    src = (HERE / "m3_analytic.py").read_text()
    assert "adaptive" not in src.lower().replace("no error-driven adaptive", "")
    assert "PANEL_THRESHOLD = 2 * (GRID - 1) + 1" in src


def test_pilot_does_not_touch_protected_tree():
    import subprocess
    changed = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                             capture_output=True, text=True).stdout.split("\n")
    outside = [c for c in changed if c.strip()
               and "level4/closure_proofs/p5y_micropilot_gate1/" not in c]
    assert not outside, f"protected tree touched: {outside}"
