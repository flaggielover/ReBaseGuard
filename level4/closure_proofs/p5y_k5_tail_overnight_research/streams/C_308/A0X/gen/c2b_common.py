"""C2b common: quarantine wiring, model constants, rigorous Gaussian lattice enclosures (stdlib only).

Model (verified against the docstring of c11_certifier.py, read before import):
  state (p, m) >= 0 on the reachable set R = {0<=p,m<=5 and (p+m<=4 or p==0 or m==0)};
  increment z with z + e ~ N(0,1); alarm-free window z in [m - C, C - p], C = K + H = 11/2;
  next state (max(0, p+z-K), max(0, m-z-K)), K = 1/2, H = 5; atom a = (0,0).

Imports allowed by the campaign preamble (Q3): c7_gaussian (pure, `fractions` only) and c11_certifier/c11_common
(pure libraries; c11_common defines constants and functions only, no side effects at import).  Nothing else from
earlier campaigns is imported.  Every entry point that takes a drift calls ov_quarantine.guard_drift.
"""
from __future__ import annotations

import pathlib
import sys
from fractions import Fraction as F

HERE = pathlib.Path(__file__).resolve().parent
NS = HERE.parents[3]                      # .../p5y_k5_tail_overnight_research
sys.path.insert(0, str(NS / "code"))
import ov_quarantine as Q  # noqa: E402

Q.install_import_guard()

CLOSURE = NS.parent
C7_CODE = CLOSURE / "p5y_k5_tail_c7_e2_lambda309" / "code"
C11_CODE = CLOSURE / "p5y_k5_tail_c11_n9_independent_certifier" / "code"
sys.path.insert(0, str(C7_CODE))
import c7_gaussian as G  # noqa: E402

K = F(1, 2)
H = F(5)
CC = K + H
VALIDATION_DIR = NS / "validation"
STREAM = "C2b"

# fixed-point scale for rigorous integer interval arithmetic
P_BITS = 128
ONE_P = 1 << P_BITS


def guard(e_lo, e_hi=None):
    """Quarantine: refuse any drift point/interval meeting the tail band (and mirror)."""
    Q.guard_drift(F(e_lo), None if e_hi is None else F(e_hi))


def floor_scaled(x: F, bits: int = P_BITS) -> int:
    return (x.numerator << bits) // x.denominator


def ceil_scaled(x: F, bits: int = P_BITS) -> int:
    return -((-x.numerator << bits) // x.denominator)


_S2PI = None


def _s2pi():
    global _S2PI
    if _S2PI is None:
        _S2PI = G.sqrt_two_pi()
    return _S2PI


def Phi_iv(t: F) -> G.Iv:
    """Rigorous Phi(t): the formula of c7_gaussian.Phi with sqrt(2 pi) computed once (same primitives)."""
    t = F(t)
    if t < 0:
        return G.Iv(1, 1) - Phi_iv(-t)
    return G.Iv(F(1, 2), F(1, 2)) + G._erf_integral(t) / _s2pi()


def phi_iv(t: F) -> G.Iv:
    t = F(t)
    return G.exp_neg(t * t / 2) / _s2pi()


class Lattice:
    """Rigorous Phi/phi enclosures at t_d = c + d*h, d in [dmin, dmax], stored as scaled integers (2^-P_BITS)."""

    def __init__(self, c: F, h: F, dmin: int, dmax: int):
        self.c, self.h, self.dmin, self.dmax = F(c), F(h), dmin, dmax
        self.Phi_lo, self.Phi_hi, self.phi_lo, self.phi_hi = {}, {}, {}, {}
        for d in range(dmin, dmax + 1):
            t = self.c + d * self.h
            a = Phi_iv(t)
            b = phi_iv(t)
            self.Phi_lo[d], self.Phi_hi[d] = floor_scaled(a.lo), ceil_scaled(a.hi)
            self.phi_lo[d], self.phi_hi[d] = floor_scaled(max(b.lo, F(0))), ceil_scaled(b.hi)

    def t(self, d: int) -> F:
        return self.c + d * self.h


def phi_float(t: float) -> float:
    import math
    return math.exp(-0.5 * t * t) / math.sqrt(2.0 * math.pi)


def Phi_float(t: float) -> float:
    import math
    if t < 0:
        return 0.5 * math.erfc(-t / math.sqrt(2.0))
    return 1.0 - 0.5 * math.erfc(t / math.sqrt(2.0))
