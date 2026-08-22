from __future__ import annotations

import math
from pathlib import Path

import numpy as np

from stopped import _sr_update

CAMPAIGN = Path(__file__).resolve().parents[1]
A = 520.886133602749


def raw_step(r_plus: np.ndarray, r_minus: np.ndarray, z: np.ndarray):
    new_plus = (1.0 + r_plus) * np.exp(z - 0.5)
    new_minus = (1.0 + r_minus) * np.exp(-z - 0.5)
    return new_plus, new_minus


def test_authoritative_threshold_binary64_identity():
    assert A.hex() == "0x1.04716cd36dd8dp+9"
    assert A.as_integer_ratio() == (4581762885148045, 8796093022208)
    assert A != 520.3125


def test_frozen_log_update_is_raw_sr_update():
    r_plus = np.array([0.0, 1.25, 510.0, 17.0])
    r_minus = np.array([0.0, 4.0, 2.0, 500.0])
    z = np.array([-0.7, 0.2, 1.0, -1.1])
    y_plus = np.log1p(r_plus)
    y_minus = np.log1p(r_minus)
    got_y_plus, got_y_minus, got_cross_plus, got_cross_minus = _sr_update(
        y_plus, y_minus, z, math.log(A)
    )
    raw_plus, raw_minus = raw_step(r_plus, r_minus, z)

    np.testing.assert_allclose(np.expm1(got_y_plus), raw_plus, rtol=2e-15)
    np.testing.assert_allclose(np.expm1(got_y_minus), raw_minus, rtol=2e-15)
    np.testing.assert_array_equal(got_cross_plus, raw_plus >= A)
    np.testing.assert_array_equal(got_cross_minus, raw_minus >= A)


def test_sign_reflection_swaps_sr_charts():
    r_plus = np.array([0.0, 3.0, 100.0])
    r_minus = np.array([7.0, 0.5, 2.0])
    z = np.array([0.4, -1.7, 2.0])
    forward = _sr_update(np.log1p(r_plus), np.log1p(r_minus), z, math.log(A))
    reflected = _sr_update(
        np.log1p(r_minus), np.log1p(r_plus), -z, math.log(A)
    )

    np.testing.assert_array_equal(forward[0], reflected[1])
    np.testing.assert_array_equal(forward[1], reflected[0])
    np.testing.assert_array_equal(forward[2], reflected[3])
    np.testing.assert_array_equal(forward[3], reflected[2])


def test_derived_forcing_bound_crosses_from_every_tested_live_state():
    live = np.array([0.0, 1e-200, 0.1, A / 2.0, np.nextafter(A, 0.0)])
    bound = math.log(A) + 0.5
    plus, minus = raw_step(live, live[::-1], np.full(live.size, bound))
    assert np.all(plus >= A)
    assert np.all(minus >= 0.0)

    plus, minus = raw_step(live, live[::-1], np.full(live.size, -bound))
    assert np.all(minus >= A)
    assert np.all(plus >= 0.0)


def test_audit_states_fixed_path_functional_and_conditional_lean_boundary():
    audit = (CAMPAIGN / "DEFINITION_AUDIT.md").read_text()
    assert "path functional fixed, law varies" in audit
    assert "Z_t ~ N(-e,1)" in audit
    assert "F'_rho(0) = rho(1 - E_0[Z_tau T_tau])" in audit
    assert "log(A) + 1/2" in audit

