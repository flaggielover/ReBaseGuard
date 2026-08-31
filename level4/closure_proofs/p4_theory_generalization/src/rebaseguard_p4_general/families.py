"""Location families under test.

Every family is a *location* family: the observation is ``X_t = mu + eps_t``
with ``eps_t`` iid from the fixed base density ``f``.  In the frozen residual
convention of the closed core,

```text
e   = R_j - mu            (reference error)
Z_t = X_t - R_j = eps_t - e
```

so the residual coordinate has density ``f_e(z) = f(z + e)``.  The conventional
location score is ``psi = -f'/f`` and the *parameter* score for this convention
is ``s = d/de log f(z+e)|_0 = f'(z)/f(z) = -psi(z)``.  This is the sign
convention already fixed by the frozen location-family track and it is not
re-derived here.

Nothing in this module is family-adaptive: the detector recursions are frozen
and only the innovation law changes.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable

import numpy as np
from scipy import special


@dataclass(frozen=True, slots=True)
class Family:
    """A base innovation density with its analytic score."""

    name: str
    sample: Callable[[np.random.Generator, tuple[int, ...]], np.ndarray]
    logpdf: Callable[[np.ndarray], np.ndarray]
    psi: Callable[[np.ndarray], np.ndarray]
    #: uniform bound on ``|psi|`` when the score is bounded, else ``None``
    score_bound: float | None
    #: supremum of the orders ``r`` with ``E|eps|^r < infinity``; the value
    #: itself is not attained (Cauchy records ``1.0`` and has no mean)
    finite_abs_moment_order: float
    symmetric: bool
    #: ``True`` when ``f > 0`` on all of ``R`` and the support does not move
    common_support: bool
    #: ``True`` when ``e -> log f(z+e)`` is differentiable at every ``e`` for
    #: every ``z``; Laplace fails this at the single kink point ``e = -z``
    everywhere_differentiable_logdensity: bool
    classification: str
    note: str


_SQRT2 = math.sqrt(2.0)
_LOG2PI = math.log(2.0 * math.pi)


def _gaussian() -> Family:
    return Family(
        name="gaussian",
        sample=lambda rng, size: rng.standard_normal(size),
        logpdf=lambda z: -0.5 * z * z - 0.5 * _LOG2PI,
        psi=lambda z: np.asarray(z, dtype=float),
        score_bound=None,
        finite_abs_moment_order=math.inf,
        symmetric=True,
        common_support=True,
        everywhere_differentiable_logdensity=True,
        classification="THEOREM-SUPPORTED",
        note="frozen control; unbounded but linear score, all exponential moments",
    )


def _laplace() -> Family:
    # unit variance: f(z) = (1/(2b)) exp(-|z|/b) with b = 1/sqrt(2)
    b = 1.0 / _SQRT2
    return Family(
        name="laplace",
        sample=lambda rng, size: rng.laplace(0.0, b, size),
        logpdf=lambda z: -np.abs(z) / b - math.log(2.0 * b),
        psi=lambda z: np.sign(np.asarray(z, dtype=float)) / b,
        score_bound=1.0 / b,
        finite_abs_moment_order=math.inf,
        symmetric=True,
        common_support=True,
        everywhere_differentiable_logdensity=False,
        classification="THEOREM-SUPPORTED",
        note="bounded score; log-density has a kink, so only the "
             "difference-quotient hypothesis applies",
    )


def _logistic() -> Family:
    # unit variance: scale s with s*pi/sqrt(3) = 1
    s = math.sqrt(3.0) / math.pi
    return Family(
        name="logistic",
        sample=lambda rng, size: rng.logistic(0.0, s, size),
        logpdf=lambda z: -np.asarray(z, float) / s
        - 2.0 * np.logaddexp(0.0, -np.asarray(z, float) / s)
        - math.log(s),
        psi=lambda z: np.tanh(np.asarray(z, dtype=float) / (2.0 * s)) / s,
        score_bound=1.0 / s,
        finite_abs_moment_order=math.inf,
        symmetric=True,
        common_support=True,
        everywhere_differentiable_logdensity=True,
        classification="THEOREM-SUPPORTED",
        note="bounded smooth score, all polynomial moments finite",
    )


def _student(nu: float, *, standardise: bool, classification: str,
             note: str, label: str) -> Family:
    """Student-t innovations.

    ``standardise`` rescales to unit variance, which is only possible for
    ``nu > 2``; the infinite-variance cells keep the raw scale.
    """
    scale = math.sqrt(nu / (nu - 2.0)) if standardise else 1.0
    logconst = (
        special.gammaln((nu + 1.0) / 2.0)
        - special.gammaln(nu / 2.0)
        - 0.5 * math.log(nu * math.pi)
        + math.log(scale)
    )

    def sample(rng: np.random.Generator, size: tuple[int, ...]) -> np.ndarray:
        return rng.standard_t(nu, size=size) / scale

    def logpdf(z: np.ndarray) -> np.ndarray:
        y = scale * np.asarray(z, dtype=float)
        return logconst - 0.5 * (nu + 1.0) * np.log1p(y * y / nu)

    def psi(z: np.ndarray) -> np.ndarray:
        y = scale * np.asarray(z, dtype=float)
        return scale * (nu + 1.0) * y / (nu + y * y)

    # sup_y (nu+1)|y|/(nu+y^2) is attained at |y| = sqrt(nu)
    bound = scale * (nu + 1.0) / (2.0 * math.sqrt(nu))
    return Family(
        name=label,
        sample=sample,
        logpdf=logpdf,
        psi=psi,
        score_bound=bound,
        finite_abs_moment_order=nu,
        symmetric=True,
        common_support=True,
        everywhere_differentiable_logdensity=True,
        classification=classification,
        note=note,
    )


def _skewnormal(alpha: float) -> Family:
    """Standardised skew-normal: smooth, positive on R, asymmetric."""
    delta = alpha / math.sqrt(1.0 + alpha * alpha)
    mean = delta * math.sqrt(2.0 / math.pi)
    sd = math.sqrt(1.0 - mean * mean)

    def raw_logpdf(y: np.ndarray) -> np.ndarray:
        return (
            math.log(2.0) - 0.5 * y * y - 0.5 * _LOG2PI
            + special.log_ndtr(alpha * y)
        )

    def sample(rng: np.random.Generator, size: tuple[int, ...]) -> np.ndarray:
        u = rng.standard_normal(size)
        v = rng.standard_normal(size)
        y = delta * np.abs(u) + math.sqrt(1.0 - delta * delta) * v
        return (y - mean) / sd

    def logpdf(z: np.ndarray) -> np.ndarray:
        y = mean + sd * np.asarray(z, dtype=float)
        return raw_logpdf(y) + math.log(sd)

    def psi(z: np.ndarray) -> np.ndarray:
        # psi(z) = -d/dz log f(z); with y = mean + sd*z,
        # d/dy log g(y) = -y + alpha * phi(alpha y)/Phi(alpha y)
        y = mean + sd * np.asarray(z, dtype=float)
        ratio = np.exp(
            -0.5 * (alpha * y) ** 2 - 0.5 * _LOG2PI - special.log_ndtr(alpha * y)
        )
        return sd * (y - alpha * ratio)

    return Family(
        name=f"skewnormal{alpha:g}",
        sample=sample,
        logpdf=logpdf,
        psi=psi,
        score_bound=None,
        finite_abs_moment_order=math.inf,
        symmetric=False,
        common_support=True,
        everywhere_differentiable_logdensity=True,
        classification="THEOREM-SUPPORTED",
        note="asymmetric: the derivative identity applies, the zero fixed "
             "point does not",
    )


def _uniform() -> Family:
    a = math.sqrt(3.0)  # unit variance on [-a, a]

    def psi(z: np.ndarray) -> np.ndarray:
        # the a.e. interior score of a flat density is identically zero
        return np.zeros_like(np.asarray(z, dtype=float))

    def logpdf(z: np.ndarray) -> np.ndarray:
        z = np.asarray(z, dtype=float)
        return np.where(np.abs(z) <= a, -math.log(2.0 * a), -math.inf)

    return Family(
        name="uniform",
        sample=lambda rng, size: rng.uniform(-a, a, size),
        logpdf=logpdf,
        psi=psi,
        score_bound=0.0,
        finite_abs_moment_order=math.inf,
        symmetric=True,
        common_support=False,
        everywhere_differentiable_logdensity=False,
        classification="OUTSIDE-ASSUMPTIONS",
        note="compact moving support: no local absolute continuity, the "
             "a.e. score is identically zero and the identity must fail",
    )


def _cauchy() -> Family:
    return Family(
        name="cauchy",
        sample=lambda rng, size: rng.standard_cauchy(size),
        logpdf=lambda z: -math.log(math.pi) - np.log1p(np.asarray(z, float) ** 2),
        psi=lambda z: 2.0 * np.asarray(z, float) / (1.0 + np.asarray(z, float) ** 2),
        score_bound=1.0,
        finite_abs_moment_order=1.0,
        symmetric=True,
        common_support=True,
        everywhere_differentiable_logdensity=True,
        classification="OUTSIDE-ASSUMPTIONS",
        note="no first moment: neither the mean map nor the gain is defined",
    )


def build_registry() -> dict[str, Family]:
    families = [
        _gaussian(),
        _laplace(),
        _logistic(),
        _student(3.0, standardise=True, label="t3",
                 classification="THEOREM-SUPPORTED",
                 note="bounded score, finite variance"),
        _student(1.5, standardise=False, label="t1p5",
                 classification="THEOREM-SUPPORTED",
                 note="bounded score, finite mean, INFINITE variance"),
        _skewnormal(4.0),
        _uniform(),
        _cauchy(),
    ]
    return {family.name: family for family in families}


REGISTRY = build_registry()
