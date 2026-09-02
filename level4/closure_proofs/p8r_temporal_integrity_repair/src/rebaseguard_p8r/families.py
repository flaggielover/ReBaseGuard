"""The six frozen innovation families, re-implemented independently.

The definitions are the ones frozen by Stage-D D3 and copied by P4
(``location_family/src/rebaseguard_location_family/route_a.py``).  P8
re-implements them from the mathematics rather than importing P4's module, so
that the cross-check in ``tests/test_families.py`` is a real check and not a
tautology.

Conventions
-----------
Physical observation ``eps ~ f`` with ``E[eps] = 0`` and ``Var[eps] = 1``
(``t`` families are rescaled to unit variance; the contaminated families
already have variance ``1 + 8 eps_c``, and are **not** rescaled -- that is the
frozen Stage-D convention and it is preserved here verbatim, see
``variance()``).

Residual convention (frozen, from ``location_family/PROTOCOL.md`` section 2)::

    e      = R_j - mu          reference error
    Z_t    = eps_t - e         residual fed to the detector
    f_e(z) = f(z + e)          residual density under reference error e
    s(z)   = f'(z)/f(z)        parameter score  (d/de log f_e(z) at e=0)
    psi(z) = -f'(z)/f(z)       conventional location score,  s = -psi

For the Gaussian, ``psi(z) = z``.

P8R provenance: byte-for-byte the P8 module `p8_model_class_robustness/src/rebaseguard_p8/families.py` apart from this note.  The P8 adjudication found no defect in it (G1d/G1e PASS); the P8 failure was procedural, so re-deriving the six frozen families would add risk without adding evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

SQRT_2PI = float(np.sqrt(2.0 * np.pi))


@dataclass(frozen=True, slots=True)
class Family:
    name: str
    draw: Callable[[np.random.Generator, tuple], np.ndarray]
    psi: Callable[[np.ndarray], np.ndarray]
    logpdf: Callable[[np.ndarray], np.ndarray]
    variance: float
    #: largest p with E|eps|^p < inf (inf for the Gaussian/contaminated cases)
    tail_moment_order: float


def _gaussian() -> Family:
    return Family(
        name="gaussian",
        draw=lambda rng, size: rng.standard_normal(size),
        psi=lambda z: np.asarray(z, dtype=float),
        logpdf=lambda z: -0.5 * np.asarray(z, float) ** 2 - np.log(SQRT_2PI),
        variance=1.0,
        tail_moment_order=float("inf"),
    )


def _student_t(nu: int) -> Family:
    """Unit-variance Student ``t_nu``:  eps = t_nu / sqrt(nu/(nu-2))."""
    a = float(np.sqrt(nu / (nu - 2.0)))          # rescaling divisor
    a2 = a * a                                   # = nu/(nu-2)

    def draw(rng, size):
        return rng.standard_t(nu, size=size) / a

    def psi(z):
        z = np.asarray(z, dtype=float)
        return (nu + 1.0) * a2 * z / (nu + a2 * z * z)

    def logpdf(z):
        from scipy.special import gammaln
        z = np.asarray(z, dtype=float)
        y = a * z
        c = (gammaln((nu + 1.0) / 2.0) - gammaln(nu / 2.0)
             - 0.5 * np.log(nu * np.pi) + np.log(a))
        return c - 0.5 * (nu + 1.0) * np.log1p(y * y / nu)

    return Family(name=f"t{nu}", draw=draw, psi=psi, logpdf=logpdf,
                  variance=1.0, tail_moment_order=float(nu))


def _contaminated(eps_c: float) -> Family:
    """``(1-eps_c) N(0,1) + eps_c N(0,3^2)``, NOT rescaled (Stage-D frozen)."""

    def draw(rng, size):
        broad = rng.random(size) < eps_c
        z = rng.standard_normal(size)
        return np.where(broad, 3.0 * z, z)

    def _components(z):
        z = np.asarray(z, dtype=float)
        narrow = (1.0 - eps_c) * np.exp(-0.5 * z * z) / SQRT_2PI
        broad = eps_c * np.exp(-0.5 * (z / 3.0) ** 2) / (3.0 * SQRT_2PI)
        return narrow, broad

    def psi(z):
        narrow, broad = _components(z)
        z = np.asarray(z, dtype=float)
        return (narrow * z + broad * z / 9.0) / (narrow + broad)

    def logpdf(z):
        narrow, broad = _components(z)
        return np.log(narrow + broad)

    return Family(name=f"contam{eps_c:g}", draw=draw, psi=psi, logpdf=logpdf,
                  variance=1.0 + 8.0 * eps_c, tail_moment_order=float("inf"))


_BUILDERS = {
    "gaussian": _gaussian,
    "t10": lambda: _student_t(10),
    "t5": lambda: _student_t(5),
    "t3": lambda: _student_t(3),
    "contam0.05": lambda: _contaminated(0.05),
    "contam0.1": lambda: _contaminated(0.1),
}


def get(name: str) -> Family:
    try:
        return _BUILDERS[name]()
    except KeyError:
        raise ValueError(f"unknown family {name!r}") from None


def all_families() -> tuple[Family, ...]:
    return tuple(get(n) for n in _BUILDERS)


# ---------------------------------------------------------------------------
# regularity diagnostics (quadrature, used by tests and the results record)
# ---------------------------------------------------------------------------

def fisher_information(fam: Family, lim: float = 60.0) -> float:
    """``I = E[psi(eps)^2]`` by quadrature against the family's own density."""
    from scipy.integrate import quad
    g = lambda x: fam.psi(np.array([x]))[0] ** 2 * np.exp(fam.logpdf(np.array([x]))[0])
    v, _ = quad(g, -lim, lim, limit=400)
    return float(v)


def expected_z_psi(fam: Family, lim: float = 60.0) -> float:
    """``E[eps psi(eps)]``.  Exactly 1 for every regular location family."""
    from scipy.integrate import quad
    g = lambda x: x * fam.psi(np.array([x]))[0] * np.exp(fam.logpdf(np.array([x]))[0])
    v, _ = quad(g, -lim, lim, limit=400)
    return float(v)


def expected_psi(fam: Family, lim: float = 60.0) -> float:
    """``E[psi(eps)]``.  Exactly 0 for every regular location family."""
    from scipy.integrate import quad
    g = lambda x: fam.psi(np.array([x]))[0] * np.exp(fam.logpdf(np.array([x]))[0])
    v, _ = quad(g, -lim, lim, limit=400)
    return float(v)


def score_by_finite_difference(fam: Family, z, h: float = 1e-5) -> np.ndarray:
    """``-d/dz log f(z)`` numerically; must agree with ``fam.psi``."""
    z = np.asarray(z, dtype=float)
    return -(fam.logpdf(z + h) - fam.logpdf(z - h)) / (2.0 * h)
