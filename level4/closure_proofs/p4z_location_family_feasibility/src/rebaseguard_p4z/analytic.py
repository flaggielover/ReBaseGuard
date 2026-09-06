"""Analytic contract for the Rao-Blackwellised routes.

The two frozen detectors share a structural property that the whole P4Z
redesign rests on.

**Bounded-survival lemma.**  Write the pre-step state of the detector as
``(u, d)`` and let ``c_D`` be the detector's *forcing increment* -- the residual
value that alarms in one step from every live state, already defined by the
frozen implementation (``h + k`` for the two-sided CUSUM, ``1/2 + log A`` for
the two-chart SR, and used by discharge lemma L1 of ``THEOREM.md`` Sec. 8).
Then the set of residuals that do **not** alarm is an interval

    I(u, d) = (L(u, d), U(u, d)),      L < 0 < U,     |L|, |U| <= c_D,

so every residual on a live path is uniformly bounded by ``c_D``.  Explicitly

    CUSUM  U = h + k - u,                     L = d - h - k
    SR     U = log A + 1/2 - log(1 + e^u),    L = -(log A + 1/2 - log(1 + e^d))

using ``u, d`` in the log domain for SR, exactly as ``detectors.py`` carries
them.  Both are immediate from the frozen recursions and the inclusive
boundary: the alarm test is ``>= threshold`` after the update, so the survival
set is open.

The consequence is the entire scientific content of P4Z: on ``{tau = n}`` the
*only* unbounded coordinate of

    A_m = (1/w) sum_{r=0}^{w-1} Z_{tau-r},     w = min(m, tau)

is the single alarm-causing increment ``Z_tau``.  All other window terms, and
every term of ``S_tau^psi = sum_{t<=tau} psi(Z_t)``, are bounded functions of
residuals confined to ``I``.

Integrating ``Z_tau`` out against the base law over the alarm set therefore
removes the family's tail from the estimator exactly.  That integration needs
only four scalar functionals of the alarm set ``E = (-inf, L] u [U, inf)``:

    J0 = int_E f              J1 = int_E z f
    J2 = int_E z psi(z) f     J3 = int_E psi(z) f

and, because ``psi f = -f'`` by definition of the score, three of the four are
**family free**:

    J3 = f(U) - f(L)
    J2 = F(L) - L f(L) + U f(U) + 1 - F(U)
    J0 = F(L) + 1 - F(U)

leaving only ``J1``, the partial first moment, family specific.  A family's
contract is therefore exactly ``(f, F, Mlow)`` with
``Mlow(x) = int_{-inf}^{x} z f(z) dz``.  ``J1 = Mlow(L) - Mlow(U)`` uses
``int_U^inf z f = -Mlow(U)``, which is the centring ``E[eps] = 0`` that
hypothesis (A7) already requires of every family in scope.

``J1`` is also where the theorem's proved failure mode reappears structurally:
for an innovation law without a first moment ``Mlow`` does not exist, so the
estimator cannot even be written down.  That is the F2 non-existence of
``THEOREM.md`` Sec. 9, not a numerical difficulty.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable

import numpy as np
from scipy import special, stats

Array = np.ndarray


@dataclass(frozen=True, slots=True)
class FamilyKit:
    """``(f, F, Mlow)`` for one base density, plus its declared moment order."""

    name: str
    pdf: Callable[[Array], Array]
    cdf: Callable[[Array], Array]
    #: ``Mlow(x) = int_{-inf}^{x} z f(z) dz``; ``None`` when no first moment
    #: exists, which makes the family inadmissible for these routes.
    partial_mean: Callable[[Array], Array] | None
    finite_abs_moment_order: float


def _gaussian() -> FamilyKit:
    inv = 1.0 / math.sqrt(2.0 * math.pi)
    return FamilyKit(
        "gaussian",
        lambda z: inv * np.exp(-0.5 * np.asarray(z, float) ** 2),
        lambda z: special.ndtr(np.asarray(z, float)),
        lambda x: -inv * np.exp(-0.5 * np.asarray(x, float) ** 2),
        math.inf,
    )


def _laplace() -> FamilyKit:
    b = 1.0 / math.sqrt(2.0)  # unit variance, matching families.py

    def pdf(z: Array) -> Array:
        return np.exp(-np.abs(np.asarray(z, float)) / b) / (2.0 * b)

    def cdf(z: Array) -> Array:
        z = np.asarray(z, float)
        # as in partial_mean: factor out exp(-|z|/b) so the discarded branch
        # cannot overflow for large |z|.
        decay = 0.5 * np.exp(-np.abs(z) / b)
        return np.where(z < 0.0, decay, 1.0 - decay)

    def partial_mean(x: Array) -> Array:
        # both branches carry the same decaying factor exp(-|x|/b), so it is
        # factored out: evaluating exp(+x/b) on the discarded branch would
        # overflow for large positive x.
        x = np.asarray(x, float)
        decay = 0.5 * np.exp(-np.abs(x) / b)
        return np.where(x < 0.0, x - b, -(x + b)) * decay

    return FamilyKit("laplace", pdf, cdf, partial_mean, math.inf)


def _logistic() -> FamilyKit:
    s = math.sqrt(3.0) / math.pi  # unit variance, matching families.py

    def pdf(z: Array) -> Array:
        e = special.expit(np.asarray(z, float) / s)
        return e * (1.0 - e) / s

    def cdf(z: Array) -> Array:
        return special.expit(np.asarray(z, float) / s)

    def partial_mean(x: Array) -> Array:
        # int_{-inf}^{x} z f dz = x q(x) + s log(1 - q(x)),  q = expit(x/s).
        # Differentiating gives x q (1-q) / s = x f(x), and both terms vanish
        # as x -> -inf.  Written through logaddexp so that the large-x limit
        # x - x = 0 is reached exactly instead of through log1p(-1) = -inf.
        x = np.asarray(x, float)
        return x * special.expit(x / s) - s * np.logaddexp(0.0, x / s)

    return FamilyKit("logistic", pdf, cdf, partial_mean, math.inf)


def _student(nu: float, scale: float, name: str) -> FamilyKit:
    """``Z = T_nu / scale`` exactly as ``families.py`` parametrises it."""
    logc = (
        special.gammaln((nu + 1.0) / 2.0)
        - special.gammaln(nu / 2.0)
        - 0.5 * math.log(nu * math.pi)
    )
    c = math.exp(logc)

    def pdf(z: Array) -> Array:
        y = scale * np.asarray(z, float)
        return scale * c * np.power(1.0 + y * y / nu, -(nu + 1.0) / 2.0)

    def cdf(z: Array) -> Array:
        return stats.t.cdf(scale * np.asarray(z, float), nu)

    if nu <= 1.0:
        return FamilyKit(name, pdf, cdf, None, nu)

    tail_const = nu * c / (nu - 1.0)

    def partial_mean(x: Array) -> Array:
        # By symmetry int_{-inf}^{inf} y f_T = 0, and for every real a
        #   int_{a}^{inf} y f_T(y) dy = (nu c / (nu-1)) (1 + a^2/nu)^{-(nu-1)/2}
        #                               * sign correction
        # so int_{-inf}^{a} y f_T = -(that tail).  Substituting u = 1 + y^2/nu
        # gives the closed form directly; it is finite exactly for nu > 1.
        a = scale * np.asarray(x, float)
        tail = tail_const * np.power(1.0 + a * a / nu, -(nu - 1.0) / 2.0)
        return -tail / scale

    return FamilyKit(name, pdf, cdf, partial_mean, nu)


def _skewnormal(alpha: float) -> FamilyKit:
    """Standardised skew-normal, matching ``families.py``."""
    delta = alpha / math.sqrt(1.0 + alpha * alpha)
    mean = delta * math.sqrt(2.0 / math.pi)
    sd = math.sqrt(1.0 - mean * mean)
    inv = 1.0 / math.sqrt(2.0 * math.pi)

    def _y(z: Array) -> Array:
        return mean + sd * np.asarray(z, float)

    def pdf(z: Array) -> Array:
        y = _y(z)
        return sd * 2.0 * inv * np.exp(-0.5 * y * y) * special.ndtr(alpha * y)

    def cdf(z: Array) -> Array:
        y = _y(z)
        return special.ndtr(y) - 2.0 * special.owens_t(y, alpha)

    def partial_mean(x: Array) -> Array:
        # int_{-inf}^{x} z f_Z(z) dz with z = (y - mean)/sd
        #   = (1/sd) [ int_{-inf}^{y} t g(t) dt - mean * G(y) ]
        # and for the raw skew-normal g,
        #   int_{-inf}^{y} t g(t) dt = -2 phi(y) Phi(alpha y)
        #                              + (delta/sqrt(2 pi)) * (1 - 2 Phi_2)
        # The closed form below is verified against quadrature by
        # tests/test_analytic_contract.py.
        y = _y(x)
        phi = inv * np.exp(-0.5 * y * y)
        low_moment = (
            -2.0 * phi * special.ndtr(alpha * y)
            + delta * math.sqrt(2.0 / math.pi)
            * special.ndtr(y * math.sqrt(1.0 + alpha * alpha))
        )
        return (low_moment - mean * cdf(x)) / sd

    return FamilyKit(f"skewnormal{alpha:g}", pdf, cdf, partial_mean, math.inf)


def _cauchy() -> FamilyKit:
    return FamilyKit(
        "cauchy",
        lambda z: 1.0 / (math.pi * (1.0 + np.asarray(z, float) ** 2)),
        lambda z: 0.5 + np.arctan(np.asarray(z, float)) / math.pi,
        None,  # no first moment: the estimator cannot be written down
        1.0,
    )


def build_kits() -> dict[str, FamilyKit]:
    kits = [
        _gaussian(),
        _laplace(),
        _logistic(),
        _student(3.0, math.sqrt(3.0), "t3"),
        _student(1.5, 1.0, "t1p5"),
        _skewnormal(4.0),
        _cauchy(),
    ]
    return {kit.name: kit for kit in kits}


FAMILY_KITS = build_kits()

#: ``uniform`` is deliberately absent.  Its support moves with ``e``, so (A3)
#: fails and the identity itself is false (``THEOREM.md`` Sec. 9, F1).  No
#: estimator of the score side is admissible there and P4Z does not provide
#: one; that cell's evidence is the existing analytic and Arb witness.


def alarm_bounds(kind: str, threshold: float, up: Array, down: Array,
                 k: float) -> tuple[Array, Array]:
    """``(L, U)``: the frozen detector alarms iff ``z <= L`` or ``z >= U``.

    ``up`` and ``down`` are the *pre-step* charts in the representation
    ``detectors.py`` carries them (linear for CUSUM, logarithmic for SR).
    """
    if kind == "cusum":
        upper = threshold + k - np.asarray(up, float)
        lower = np.asarray(down, float) - threshold - k
        return lower, upper
    if kind == "sr":
        log_a = math.log(threshold)
        upper = log_a + 0.5 - np.logaddexp(0.0, np.asarray(up, float))
        lower = -(log_a + 0.5 - np.logaddexp(0.0, np.asarray(down, float)))
        return lower, upper
    raise ValueError(f"P4Z supports the two frozen detectors only, not {kind!r}")


def whole_line_integrals(kit: FamilyKit) -> tuple[float, float, float, float]:
    """``(J0, J1, J2, J3)`` when the alarm set is all of ``R``.

    This is the deterministic-stopping control ``tau = n0`` of Corollary G2.
    The four values are the exact integration-by-parts constants

        J0 = 1,   J1 = E[eps] = 0,   J2 = E[eps psi(eps)] = 1,   J3 = E[psi] = 0

    of ``THEOREM.md`` Sec. 5(b).  They are constants of the theorem, not
    measurements, and they are what makes ``Gamma = 1`` exactly for every
    family and every ``m`` under a non-selective rule.
    """
    if kit.partial_mean is None:
        raise ValueError(f"family {kit.name!r} has no first moment")
    return 1.0, 0.0, 1.0, 0.0


def alarm_integrals(kit: FamilyKit, lower: Array, upper: Array,
                    shift: float = 0.0) -> tuple[Array, Array, Array, Array]:
    """``(J0, J1, J2, J3)`` over the alarm set, for residuals ``Z = eps - e``.

    ``shift`` is the location parameter ``e``.  The residual alarm set
    ``{z <= L} u {z >= U}`` is the innovation set ``{eps <= L + e} u
    {eps >= U + e}``, so every functional is evaluated at the shifted
    endpoints and ``J1`` is corrected by ``-e * J0``.
    """
    if kit.partial_mean is None:
        raise ValueError(
            f"family {kit.name!r} has no first moment: the conditional-mean map "
            "is undefined and no P4Z route applies (THEOREM.md Sec. 9, F2)"
        )
    if shift != 0.0:
        # J2 and J3 are score-side functionals and are only ever evaluated at
        # e = 0 (Theorem G1a).  The map route uses J0 and J1 alone.  Returning
        # shifted J2/J3 would silently mean a different object, so they are
        # returned as NaN and any use is a test failure, not a wrong number.
        pass
    le = np.asarray(lower, float) + shift
    ue = np.asarray(upper, float) + shift
    if np.any(le >= ue):
        # The two tails would overlap and every functional would be
        # double counted.  A live state always has L < 0 < U (bounded-survival
        # lemma), so this can only mean the caller wants the degenerate
        # "alarm everywhere" case -- which is the deterministic-stopping
        # neutrality control and has its own exact constants.
        raise ValueError(
            "empty survival interval: use whole_line_integrals() for the "
            "deterministic-stopping neutrality control"
        )
    f_l, f_u = kit.pdf(le), kit.pdf(ue)
    cdf_l, cdf_u = kit.cdf(le), kit.cdf(ue)
    j0 = cdf_l + 1.0 - cdf_u
    j1 = kit.partial_mean(le) - kit.partial_mean(ue) - shift * j0
    if shift == 0.0:
        j2 = cdf_l - le * f_l + ue * f_u + 1.0 - cdf_u
        j3 = f_u - f_l
    else:
        j2 = np.full(np.shape(j0), np.nan)
        j3 = np.full(np.shape(j0), np.nan)
    return j0, j1, j2, j3
