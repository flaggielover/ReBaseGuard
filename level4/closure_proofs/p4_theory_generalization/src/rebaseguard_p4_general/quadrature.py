"""Route Q -- a deterministic reference evaluation of both sides of the theorem.

Monte Carlo can only ever *fail to contradict* an identity.  Route Q removes
the sampling error entirely for one detector for which every stopped quantity
collapses to one-dimensional integrals: the memoryless rule

```text
tau = inf{t >= 1 : |Z_t| >= c}.
```

Conditionally on ``tau = n`` the residuals ``Z_1,...,Z_{n-1}`` are iid from the
law of ``Z`` restricted to ``|z| < c`` ("inner"), ``Z_n`` is drawn from the law
restricted to ``|z| >= c`` ("outer"), the two are independent, and
``tau - 1`` is geometric.  Both the conditional-mean map ``g_m`` and the
theorem's gain ``Gamma_m`` are then explicit series in seven scalar integrals.

This detector is *not* the frozen ReBaseGuard detector.  Route Q tests the
mathematics -- the score identity, the truncated window ``w = min(m,tau)``, the
random denominator, and the ``tau < m`` branch -- not the frozen operating
point.  It is reported as an independent analytic route, never as evidence
about the frozen CUSUM or SR gains.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy import integrate

from .families import Family

_QUAD_KW = {"limit": 500, "epsabs": 1e-13, "epsrel": 1e-13}


def _integrate(fn, lo: float, hi: float) -> tuple[float, float]:
    value, error = integrate.quad(fn, lo, hi, **_QUAD_KW)
    return value, error


@dataclass(frozen=True, slots=True)
class Moments:
    """The seven conditional integrals at one parameter value."""

    p: float            # P(|Z| >= c)
    mu_out: float       # E[Z | outer]
    mu_in: float        # E[Z | inner]
    zpsi_out: float     # E[Z psi(Z) | outer]
    psi_out: float      # E[psi(Z) | outer]
    zpsi_in: float      # E[Z psi(Z) | inner]
    psi_in: float       # E[psi(Z) | inner]
    quad_error: float


def moments(family: Family, c: float, e: float, *, tail: float = 60.0) -> Moments:
    """Conditional moments of ``Z ~ f(. + e)`` split at ``|z| = c``."""

    def dens(z: float) -> float:
        return float(np.exp(family.logpdf(np.array([z + e]))[0]))

    def psi(z: float) -> float:
        return float(family.psi(np.array([z]))[0])

    pieces = {
        "p": ((lambda z: dens(z)), True),
        "mu_out": ((lambda z: z * dens(z)), True),
        "zpsi_out": ((lambda z: z * psi(z) * dens(z)), True),
        "psi_out": ((lambda z: psi(z) * dens(z)), True),
        "mass_in": ((lambda z: dens(z)), False),
        "mu_in": ((lambda z: z * dens(z)), False),
        "zpsi_in": ((lambda z: z * psi(z) * dens(z)), False),
        "psi_in": ((lambda z: psi(z) * dens(z)), False),
    }
    raw: dict[str, float] = {}
    err = 0.0
    for name, (fn, outer) in pieces.items():
        if outer:
            lo, elo = _integrate(fn, -tail - abs(e), -c)
            hi, ehi = _integrate(fn, c, tail + abs(e))
            raw[name], piece_err = lo + hi, elo + ehi
        else:
            # split at the kink/mode location -e so quad never straddles it
            mid = min(max(-e, -c), c)
            lo, elo = _integrate(fn, -c, mid)
            hi, ehi = _integrate(fn, mid, c)
            raw[name], piece_err = lo + hi, elo + ehi
        err = max(err, piece_err)

    p = raw["p"]
    q = raw["mass_in"]
    return Moments(
        p=p,
        mu_out=raw["mu_out"] / p,
        mu_in=raw["mu_in"] / q,
        zpsi_out=raw["zpsi_out"] / p,
        psi_out=raw["psi_out"] / p,
        zpsi_in=raw["zpsi_in"] / q,
        psi_in=raw["psi_in"] / q,
        quad_error=err,
    )


def _series(p: float, m: int, term) -> float:
    """``sum_{n>=1} (1-p)^{n-1} p * term(n, min(m,n))`` summed to machine
    precision.  The summand grows at most linearly in ``n`` against a
    geometric weight, so truncating where the remaining geometric mass is
    below ``1e-18`` is exact in double precision."""
    if not 0.0 < p <= 1.0:
        raise ValueError(f"degenerate alarm probability {p}")
    n_max = max(int(math.ceil(-40.0 * math.log(10.0) / math.log1p(-p))), 4 * m + 8) \
        if p < 1.0 else 1
    total = 0.0
    for n in range(1, n_max + 1):
        total += (1.0 - p) ** (n - 1) * p * term(n, min(m, n))
    return total


def mean_map(family: Family, c: float, m: int, e: float,
             *, tail: float = 60.0) -> float:
    """``g_m(e) = E_e[A_m]`` for the memoryless detector."""
    mo = moments(family, c, e, tail=tail)
    return _series(mo.p, m, lambda n, w: (mo.mu_out + (w - 1) * mo.mu_in) / w)


def gain(family: Family, c: float, m: int) -> tuple[float, Moments]:
    """``Gamma_m = E_0[A_m sum_{t<=tau} psi(Z_t)]`` for the memoryless detector."""
    mo = moments(family, c, 0.0)

    def term(n: int, w: int) -> float:
        return (
            mo.zpsi_out
            + mo.mu_out * (n - 1) * mo.psi_in
            + (w - 1) * mo.mu_in * mo.psi_out
            + (w - 1) * mo.zpsi_in
            + (w - 1) * (n - 2) * mo.mu_in * mo.psi_in
        ) / w

    return _series(mo.p, m, term), mo


def map_derivative(family: Family, c: float, m: int, step: float = 1e-4,
                   *, tail: float = 60.0) -> float:
    """``g_m'(0)`` by a fifth-order-accurate difference of the exact series."""
    values = [mean_map(family, c, m, k * step, tail=tail)
              for k in (-2, -1, 1, 2)]
    return (values[0] - 8.0 * values[1] + 8.0 * values[2] - values[3]) / (12.0 * step)


def laplace_closed_form(b: float, c: float) -> dict[str, object]:
    """Exact closed form for Laplace innovations, memoryless detector, ``m=1``.

    With ``f(z) = exp(-|z|/b)/(2b)`` and ``0 < e < c`` one gets, in elementary
    functions,

    ```text
    P_e(|Z| >= c)   = exp(-c/b) cosh(e/b),
    g_1(e)          = -(c + b) tanh(e/b),
    g_1'(0)         = -(c + b)/b,
    Gamma_1         = E_0[Z_tau psi(Z_tau)] = (c + b)/b.
    ```

    Every step is elementary integration of an exponential, so this is a
    non-Gaussian instance of the theorem with no numerical content at all.
    """
    return {
        "b": b,
        "c": c,
        "alarm_probability_at_zero": math.exp(-c / b),
        "gain": (c + b) / b,
        "map_derivative": -(c + b) / b,
        "map": "g_1(e) = -(c+b) tanh(e/b)",
    }
