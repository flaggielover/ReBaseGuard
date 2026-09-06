"""Certified SR operator norms and the exact e-derivative operator identities.

The three frozen operators all integrate over the continuation interval
(l(y), u(y)) = (y^- - c_SR, c_SR - y^+), which does NOT depend on e. Every
e-derivative therefore differentiates phi(z+e) only, with no boundary term:

    d^k/de^k phi(z+e) = (-1)^k He_k(z+e) phi(z+e)

so, writing w = z + e,

    (K'   f)(y) = - int_l^u (w)         f(q) phi(w) dz
    (K''  f)(y) =   int_l^u (w^2 - 1)   f(q) phi(w) dz
    (K_z' f)(y) = - int_l^u z (w)       f(q) phi(w) dz

Sup-norm operator bounds follow by pulling |f| <= sup|f| out, leaving explicit
Gaussian integrals of |w|, |w^2-1|, |z|, |z w|, ... over [l+e, u+e]. Each has a
closed antiderivative, so every norm below is EXACT up to Arb outward rounding --
no quadrature, no sampling.

Because the integrands are non-negative, enlarging the integration interval is
always a valid upper bound. The state domain is y^+ , y^- in [0, b_SR]
independently, so l in [-c_SR, b_SR - c_SR] and u in [c_SR - b_SR, c_SR], and the
widest continuation interval -- attained at the reset state y_0 = (0,0) -- is
[-c_SR, c_SR]. That is what the sup-norm bounds use.

CRITICAL, and the reason no whole-cell SR certificate can be closed from this
module alone: the one-step norm is

    k0 = Phi(c_SR) - Phi(-c_SR) = 1 - 1.4e-11

so the naive Neumann bound 1/(1-k0) ~ 7e10 is useless. K_e is substochastic with
mass essentially 1 at the reset state; the contraction is an n-STEP effect
(||K^n|| = sup_y P_y(tau > n) decays geometrically at the alarm rate), not a
one-step one. `resolvent_bound` therefore takes CERTIFIED power norms as input
and is documented as requiring the n-step operator iteration -- the heavy
numerical work this lane defers. Supplying k0^n in its place is rejected.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
_PROOF = ROOT / "rebaseguard-proof/src"
if str(_PROOF) not in sys.path:
    sys.path.insert(0, str(_PROOF))

from flint import arb                                              # noqa: E402

from sr_sources import Phi, phi                                    # noqa: E402


class ResolventNotContractive(RuntimeError):
    """The supplied power norms do not establish ||K^n|| < 1."""


class NaivePowerNormRejected(RuntimeError):
    """k0^n was supplied as a stand-in for a certified ||K^n||."""


def sr_constants() -> tuple[arb, arb, arb]:
    """(A, b_SR = log(1+A), c_SR = log A + 1/2), exact-rational-derived balls."""
    A = arb(4581762885148045) / arb(8796093022208)
    return A, (arb(1) + A).log(), A.log() + arb(1) / arb(2)


def domain_w_interval(e: arb) -> tuple[arb, arb]:
    """[L, U] = [l_min + e, u_max + e], the widest continuation interval in w."""
    _A, _b, c = sr_constants()
    return -c + e, c + e


# ------------------------------------------------------- exact Gaussian pieces
def _int_phi(a: arb, b: arb) -> arb:
    """int_a^b phi(w) dw."""
    return Phi(b) - Phi(a)


def _int_abs_w_phi(a: arb, b: arb) -> arb:
    """int_a^b |w| phi(w) dw.  int w phi = -phi."""
    if a.lower() >= 0:
        return phi(a) - phi(b)
    if b.upper() <= 0:
        return phi(b) - phi(a)
    return arb(2) * phi(arb(0)) - phi(a) - phi(b)


def _G(a: arb, b: arb) -> arb:
    """int_a^b (w^2 - 1) phi(w) dw = a phi(a) - b phi(b)."""
    return a * phi(a) - b * phi(b)


def _int_abs_w2m1_phi(a: arb, b: arb) -> arb:
    """int_a^b |w^2 - 1| phi(w) dw, splitting the sign at w = -1 and w = +1."""
    one, none = arb(1), arb(-1)
    pts = [a]
    for p in (none, one):
        if a.upper() < p.lower() < b.lower():
            pts.append(p)
    pts.append(b)
    total = arb(0)
    for lo, hi in zip(pts[:-1], pts[1:]):
        seg = _G(lo, hi)
        mid = (lo + hi) / arb(2)
        inside = (mid * mid - arb(1)).upper() <= 0
        total = total + (-seg if inside else seg)
    return total


def _int_w2_phi(a: arb, b: arb) -> arb:
    """int_a^b w^2 phi(w) dw = [Phi(w) - w phi(w)]_a^b."""
    return (Phi(b) - b * phi(b)) - (Phi(a) - a * phi(a))


# --------------------------------------------------------------- norm bundle
def one_step_norms(e: arb) -> dict:
    """Exact sup-norm bounds for the frozen operators and their e-derivatives.

    Returned keys are the error-algebra symbols:
        k0 = ||K_e||, k1 = ||K_e'||, k2 = ||K_e''||,
        kz = ||K_z,e||, kz1 = ||K_z,e'||, kz2 = ||K_z,e''||
    """
    L, U = domain_w_interval(e)
    ae = e if e.lower() >= 0 else -e            # |e|, as an enclosure

    k0 = _int_phi(L, U)
    k1 = _int_abs_w_phi(L, U)                          # int |w| phi
    k2 = _int_abs_w2m1_phi(L, U)                       # int |w^2 - 1| phi
    # z = w - e, so |z| <= |w| + |e| and |z| |w| <= w^2 + |e| |w|
    kz = _int_abs_w_phi(L, U) + ae * k0
    kz1 = _int_w2_phi(L, U) + ae * _int_abs_w_phi(L, U)
    # |z (w^2 - 1)| <= (|w| + |e|) |w^2 - 1|
    kz2 = _int_abs_w_phi(L, U) * arb(1) + ae * k2 + _int_w2_phi(L, U)
    return {"k0": k0, "k1": k1, "k2": k2, "kz": kz, "kz1": kz1, "kz2": kz2,
            "w_interval": (L, U)}


def resolvent_bound(power_norms: dict[int, arb], *, allow_naive: bool = False,
                    k0: arb | None = None) -> arb:
    """C >= ||(I - K_e)^{-1}|| from CERTIFIED power norms {j: ||K^j||}.

        C <= ( sum_{j<n} ||K^j|| ) / ( 1 - ||K^n|| )

    Requires ||K^n|| < 1 for the largest supplied n. The one-step norm alone is
    NOT sufficient for SR (k0 = 1 - 1.4e-11); supplying k0^n is rejected, because
    ||K^n|| = sup_y P_y(tau > n) is genuinely smaller and must be certified by
    iterating the operator.
    """
    if not power_norms:
        raise ResolventNotContractive("no power norms supplied")
    n = max(power_norms)
    if 0 not in power_norms:
        power_norms = {0: arb(1), **power_norms}
    tail = power_norms[n]
    if not (tail < arb(1)):
        raise ResolventNotContractive(
            f"||K^{n}|| = {tail} is not < 1; the resolvent is not certified")
    if k0 is not None and not allow_naive:
        naive = k0 ** n
        if (naive - tail).abs_upper() <= (tail * arb(1) / arb(1000)).abs_upper():
            raise NaivePowerNormRejected(
                "||K^n|| equals k0^n to within 0.1%: this is the useless "
                "one-step bound, not a certified n-step contraction")
    num = arb(0)
    for j in range(n):
        num = num + power_norms.get(j, power_norms[0] if j == 0 else arb(1))
    return num / (arb(1) - tail)
