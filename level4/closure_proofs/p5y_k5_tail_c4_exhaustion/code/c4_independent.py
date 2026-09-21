"""A second implementation of the Gaussian constants that shares NO SERIES with the production module.

Written after the pre-result review found that the first attempt at an "independent" path still called the
production power series for exp, arctan and sqrt (review, OTHER FINDINGS 4). Here:

  exp(-y)   Bernoulli / AM-GM brackets, no series at all:
                (1 + y/n)^n <= e^y <= (1 - y/n)^-n      for 0 <= y < n
            so  e^-y in [ (1 - y/n)^n , (1 + y/n)^-n ].  n = 2^BERN_DOUBLINGS, reached by repeated squaring with
            outward rounding after each squaring, so the exact rationals never blow up.

  pi        Archimedes' inscribed/circumscribed polygon perimeters, doubled ARCH_DOUBLINGS times from the hexagon.
            Uses only square roots.

  I(t)      the composite MIDPOINT rule, whose error is bounded by t h^2 / 24 * sup|f''| with
            f(u) = exp(-u^2/2), f''(u) = (u^2 - 1) f(u), and |(u^2 - 1) exp(-u^2/2)| <= 1 for all real u
            (it is 1 at u = 0 and at most 2 exp(-3/2) = 0.4463 for u >= 1). No Taylor remainder, no alternating
            series, no Simpson.

The only thing shared with production is the integer-square-root helper and the interval container, both of which
are a dozen lines and are checked directly by the arithmetic mutants.

RESOLUTION. This path is deliberately cheap and its intervals are about 1e-7 wide, against production's 1e-95. It
is a CROSS-CHECK that would catch any gross error, not a reproduction at certificate precision, and the evidence
file says so rather than claiming otherwise.
"""
from fractions import Fraction as F

import c4_rigorous_gaussian as G

BERN_DOUBLINGS = 30
ARCH_DOUBLINGS = 28
MIDPOINT_PANELS = 2048


def exp_neg_indep(y: F) -> G.Iv:
    """exp(-y) for y >= 0 with no series: Bernoulli brackets plus repeated squaring."""
    y = F(y)
    if y < 0:
        raise G.Refusal("exp_neg_indep expects y >= 0")
    n = 1 << BERN_DOUBLINGS
    if y >= n:
        raise G.Refusal("Bernoulli bracket needs y < n")
    lo_base, hi_base = G.Iv(1 - y / n), G.Iv(1 + y / n)
    lo, hi = lo_base, hi_base
    for _ in range(BERN_DOUBLINGS):                      # lo -> (1 - y/n)^n,  hi -> (1 + y/n)^n
        lo, hi = lo * lo, hi * hi
    return G.Iv(lo.lo, (G.Iv(1) / hi).hi)                # [ (1-y/n)^n , (1+y/n)^-n ]


def pi_indep() -> G.Iv:
    """Archimedes: inscribed and circumscribed regular polygons, doubled from the hexagon."""
    # a = circumscribed semiperimeter / n, b = inscribed; start at the hexagon
    a = G.Iv(2) * (G.sqrt_iv(G.Iv(3)) / G.Iv(3)) * G.Iv(3)     # 2*sqrt(3) ~ circumscribed hexagon semiperimeter
    b = G.Iv(3)                                                # inscribed hexagon semiperimeter
    for _ in range(ARCH_DOUBLINGS):
        a = (G.Iv(2) * a * b) / (a + b)                        # harmonic mean
        b = G.sqrt_iv(a * b)                                   # geometric mean
    return G.Iv(b.lo, a.hi)


def _f(u: F) -> G.Iv:
    return exp_neg_indep(u * u / 2)


def I_indep(t: F, panels: int = MIDPOINT_PANELS) -> G.Iv:
    """int_0^t exp(-u^2/2) du by the composite midpoint rule with its exact second-derivative remainder."""
    t = F(t)
    if t < 0:
        raise G.Refusal("I_indep is computed for t >= 0")
    if t == 0:
        return G.Iv(0)
    h = t / panels
    acc = G.Iv(0)
    for i in range(panels):
        acc = acc + _f((F(2 * i + 1) / 2) * h)
    s = acc * G.Iv(h)
    err = t * h * h / 24                                        # sup|f''| <= 1, proved in the module docstring
    return G.Iv(s.lo - err, s.hi + err)


def Phi_indep(t: F) -> G.Iv:
    t = F(t)
    if t < 0:
        return 1 - Phi_indep(-t)
    return G.Iv(F(1, 2)) + I_indep(t) / G.sqrt_iv(2 * pi_indep())


def phi_indep(t: F) -> G.Iv:
    t = F(t)
    return exp_neg_indep(t * t / 2) / G.sqrt_iv(2 * pi_indep())


def E_excess_indep(e: F, K: F) -> G.Iv:
    e, K = F(e), F(K)
    if K <= 0:
        raise G.Refusal("K must be positive")
    a, b = e - K, e + K
    return (G.Iv(a) * Phi_indep(a) + phi_indep(a)) + (G.Iv(-b) * Phi_indep(-b) + phi_indep(b))
