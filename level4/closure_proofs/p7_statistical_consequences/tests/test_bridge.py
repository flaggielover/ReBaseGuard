"""The theory-bridge identities must hold on the produced results."""
import json

import numpy as np
import pytest

from rebaseguard_p7.analysis import (
    ResponseCurves, beta_r, gamma_eff, gamma_eff_from_h, h_grid, load_curves,
)
from rebaseguard_p7.config import DETECTORS, M_GRID, RESULTS

pytestmark = pytest.mark.skipif(
    not (RESULTS / "consequences.json").exists(),
    reason="run experiments/analyze.py first")


@pytest.fixture(scope="module")
def data():
    raw = load_curves()["curves"]
    return ({d: ResponseCurves(raw[d], M_GRID) for d in DETECTORS},
            json.loads((RESULTS / "consequences.json").read_text()),
            np.load(RESULTS / "chain_sweep_arrays.npz"))


def test_selection_bias_is_bounded_and_opposes_the_reference_error(data):
    """e*h(e) <= 0 and sup|h| < infinity -- the hypotheses of P7-C and P7-D.

    At very large x every path alarms at tau = 1 and h -> 0, so the sign test is
    made against three standard errors rather than against exact zero.
    """
    curves, _, _ = data
    for d in DETECTORS:
        c = curves[d]
        for m in M_GRID:
            h = h_grid(c, m)
            se = c.g_se[m]
            pos = c.x > 0
            assert np.all(h[pos] < 3.0 * se[pos]), "h must oppose the sign of e"
            # strictly negative wherever it is resolvable at all
            resolvable = pos & (np.abs(h) > 3.0 * se)
            assert np.all(h[resolvable] < 0)
            assert np.max(np.abs(h)) < 2.0, "h must stay bounded"


def test_beta_r_tends_to_one_over_rho_c(data):
    """beta_r -> GammaTilde - 1 = 1/rho_c as r -> 0 (Proposition P7-C anchor)."""
    curves, res, _ = data
    for d in DETECTORS:
        c = curves[d]
        for m in M_GRID:
            target = c.gamma_tilde[m] - 1.0
            got = beta_r(c, m, 0.005)
            assert abs(got - target) / target < 0.12
    del res


def test_effective_multiplier_identity(data):
    """ACF1 measured must equal rho(1 - Gamma_eff) computed from pi and h."""
    curves, res, arrays = data
    worst = 0.0
    for cell in res["cells"]:
        if cell["rho"] == 0.0:
            continue
        pred = cell["acf1_predicted_from_gamma_eff"]
        got = cell["acf1_measured"]
        worst = max(worst, abs(pred - got))
    assert worst < 0.05, f"identity broken, worst absolute gap {worst}"
    del curves, arrays


def test_two_routes_to_gamma_eff_agree(data):
    curves, res, arrays = data
    for cell in res["cells"][:20]:
        if cell["rho"] == 0.0:
            continue
        assert abs(cell["gamma_eff"] - cell["gamma_eff_via_h"]) < 1e-9
    del curves, arrays


def test_variance_floor_from_the_independent_fresh_term(data):
    """E[e^2] >= (1-rho)^2/m, exact and free."""
    _, res, _ = data
    for cell in res["cells"]:
        assert cell["ref_mse"] >= cell["variance_floor_fresh"] * 0.98


def test_delay_identity_validated(data):
    path = RESULTS / "delay_validation.json"
    if not path.exists():
        pytest.skip("run experiments/run_delay_validation.py first")
    rows = json.loads(path.read_text())["cells"]
    assert len(rows) >= 8
    assert max(abs(r["z"]) for r in rows) < 3.0
    assert max(abs(r["relative_gap"]) for r in rows) < 0.05


def test_conditional_plugin_diagnostic_is_not_numerically_violated(data):
    """The conditional P7-D plug-in diagnostic should exceed measured ARL."""
    _, res, _ = data
    checked = 0
    for cell in res["cells"]:
        rb = cell["repulsion_bound"]
        if rb is None:
            continue
        assert cell["arl"] <= rb["plug_in_arl_upper_bound"] + 1e-9, cell["array_key"]
        checked += 1
    assert checked > 20
