"""Exact replay of the K2 constants, plus a NON-CERTIFYING float cross-check that the bound is below the true
Gaussian conditional variance over a grid (guards against an algebra slip; it certifies nothing)."""
import math
import sys
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NS / "code"))
import verify_k2_constants as V  # noqa: E402


def test_exact_replay_all_checks_pass():
    r = V.report()
    assert r["all_pass"], {k: v for k, v in r["checks"].items() if not v}
    assert r["kappa"] == {"CUSUM": "121/46875", "SR": "49/30000"}


def test_bounds_scale_with_m_squared():
    r = V.report()
    assert F(r["s_min_lower_bounds"]["SR|m=5"]) == F(49, 30000) / 25


def _var_T(a, g):
    phi = lambda x: math.exp(-x * x / 2) / math.sqrt(2 * math.pi)
    Q = lambda x: 0.5 * math.erfc(x / math.sqrt(2))
    b = a + g
    pL, pR = Q(-a), Q(b)                      # P(N <= a) = Q(-a): no cancellation for very negative a
    mL, mR = -phi(a) / pL, phi(b) / pR
    eL2, eR2 = 1 - a * phi(a) / pL, 1 + b * phi(b) / pR
    p = pL + pR
    m1, m2 = (pL * mL + pR * mR) / p, (pL * eL2 + pR * eR2) / p
    return m2 - m1 * m1


def test_float_crosscheck_bound_below_true_variance():
    for G, kappa in ((11.0, 121 / 46875), (2 * math.log(520.886133602749) + 1, 49 / 30000)):
        worst = min(_var_T(a / 10, g / 20) for a in range(-120, 121) for g in range(1, int(20 * G) + 1))
        assert worst > kappa
