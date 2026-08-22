"""D3 innovation families and their CORRECT location scores.

For a location family p_e(z) = p(z + e) -- matching the Stage D convention
z = raw - e -- the score is

    d/de log p_e(z)|_{e=0} = p'(z)/p(z) = -psi(z),      psi = -p'/p

so the stopped score sum is sum_{t<=tau} psi(z_t) and

    d/de E_e[g] |_0 = -E_0[ g * sum_t psi(z_t) ].

For the Gaussian, psi(x) = x and this reduces to the frozen Gamma = E[zbar T].

Every score here is verified numerically against three independent identities
(E[psi] = 0, E[psi^2] = E[psi'] = Fisher information, and a finite-difference
check of -p'/p) by tests/test_nongaussian.py.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
from scipy import integrate, stats


@dataclass(frozen=True, slots=True)
class Family:
    name: str
    draw: Callable[[np.random.Generator, int], np.ndarray]
    psi: Callable[[np.ndarray], np.ndarray]
    logpdf: Callable[[np.ndarray], np.ndarray]
    variance: float
    unit_variance_rescaled: bool


# ------------------------------------------------------------------ Gaussian
def _gaussian() -> Family:
    return Family(
        name="gaussian",
        draw=lambda rng, n: rng.standard_normal(n),
        psi=lambda x: x,
        logpdf=lambda x: stats.norm.logpdf(x),
        variance=1.0,
        unit_variance_rescaled=False,
    )


# ----------------------------------------------------------------- Student-t
def _student_t(nu: int) -> Family:
    """t_nu rescaled to UNIT VARIANCE, as the protocol specifies.

    X = Y / s with Y ~ t_nu and s = sqrt(nu / (nu - 2)), so Var(X) = 1. Then
    p_X(x) = s * p_Y(s x) and

        psi_X(x) = -d/dx log p_X(x) = s * psi_Y(s x)
                 = (nu + 1) s^2 x / (nu + s^2 x^2).

    The bare form (nu+1)x/(nu+x^2) is the score of the UNSCALED t and is NOT
    the score of the unit-variance variable; using it would silently mis-weight
    every D3 estimate.
    """
    if nu <= 2:
        raise ValueError("unit-variance rescaling needs nu > 2")
    s2 = nu / (nu - 2.0)
    s = float(np.sqrt(s2))
    return Family(
        name=f"t{nu}",
        draw=lambda rng, n: rng.standard_t(nu, size=n) / s,
        psi=lambda x: (nu + 1.0) * s2 * x / (nu + s2 * x * x),
        logpdf=lambda x: stats.t.logpdf(x * s, nu) + np.log(s),
        variance=1.0,
        unit_variance_rescaled=True,
    )


# ------------------------------------------------------- contaminated normal
def _contaminated(eps: float, scale: float = 3.0) -> Family:
    """(1-eps) N(0,1) + eps N(0, scale^2), NOT rescaled.

    The protocol specifies the unit-variance rescaling for the t families only,
    so this family is used as written and its variance is 1 + (scale^2 - 1)*eps
    > 1. That is recorded rather than silently corrected, because the CUSUM
    threshold is recalibrated per family anyway.
    """
    v = (1.0 - eps) + eps * scale ** 2

    def pdf_parts(x):
        a = (1.0 - eps) * np.exp(-0.5 * x * x) / np.sqrt(2 * np.pi)
        b = eps * np.exp(-0.5 * (x / scale) ** 2) / (scale * np.sqrt(2 * np.pi))
        return a, b

    def psi(x):
        a, b = pdf_parts(x)
        return (a * x + b * x / scale ** 2) / (a + b)

    def logpdf(x):
        a, b = pdf_parts(x)
        return np.log(a + b)

    def draw(rng, n):
        pick = rng.random(n) < eps
        z = rng.standard_normal(n)
        return np.where(pick, z * scale, z)

    return Family(name=f"contam{eps:g}", draw=draw, psi=psi, logpdf=logpdf,
                  variance=float(v), unit_variance_rescaled=False)


FAMILIES: dict[str, Family] = {
    "gaussian": _gaussian(),
    "t10": _student_t(10),
    "t5": _student_t(5),
    "t3": _student_t(3),
    "contam0.05": _contaminated(0.05),
    "contam0.1": _contaminated(0.10),
}


def fisher_information(fam: Family, lim: float = 40.0) -> float:
    """I = E[psi^2] by quadrature against the family's own density."""
    f = lambda x: fam.psi(np.array([x]))[0] ** 2 * np.exp(fam.logpdf(np.array([x]))[0])
    val, _ = integrate.quad(f, -lim, lim, limit=400)
    return float(val)


def expected_psi_prime(fam: Family, h: float = 1e-5, lim: float = 40.0) -> float:
    """E[psi'] by quadrature; equals I when the family is regular."""
    def f(x):
        xa = np.array([x + h, x - h])
        d = (fam.psi(xa)[0] - fam.psi(xa)[1]) / (2 * h)
        return d * np.exp(fam.logpdf(np.array([x]))[0])
    val, _ = integrate.quad(f, -lim, lim, limit=400)
    return float(val)
