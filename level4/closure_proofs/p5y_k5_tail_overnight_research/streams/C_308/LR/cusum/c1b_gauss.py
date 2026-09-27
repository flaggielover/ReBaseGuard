"""C1b rigorous Gaussian primitives (stdlib only, exact integers / fractions).

phi(t), Phi(t) at RATIONAL t as rigorous intervals (lo, hi) of Fractions on the 2^-PREC grid.

  exp(y), y >= 0:  S_N = sum_{n<=N} y^n/n!,  tail <= t_N * q/(1-q), q = y/(N+1) < 1   (t_N = y^N/N!)
  exp(-y)         = 1/exp(y) (interval division, outward)
  phi(t)          = exp(-t^2/2) * [1/sqrt(2 pi)]
  Phi(t), t >= 0  = 1/2 + phi(t) * sum_{n>=0} t^(2n+1)/(2n+1)!!   (all terms > 0; tail <= a_N q/(1-q),
                    q = t^2/(2N+3) < 1)                              Phi(-t) = 1 - Phi(t)
  pi              Machin, alternating series, first-omitted-term bound, computed once in fractions.

Every partial sum is accumulated twice with directed (floor / ceil) integer rounding, so the returned interval
contains the exact value.  Derivative bound used by the Taylor models (proved by Fourier inversion,
phi^(n)(t) = (1/2pi) int (i w)^n e^{-w^2/2} e^{iwt} dw):   sup_t |phi^(n)(t)| <= E|Y|^n / sqrt(2 pi).
No side effects at import.
"""
from __future__ import annotations

from fractions import Fraction as F
from functools import lru_cache

PREC = 160
ONE = 1 << PREC


def _cdiv(a: int, b: int) -> int:
    return -((-a) // b)


def _pi_bounds():
    def atan_inv(x: int, terms: int):
        s = F(0)
        p = F(1, x)
        x2 = x * x
        for k in range(terms):
            s += (-1) ** k * p / (2 * k + 1)
            p /= x2
        err = p / (2 * terms + 1)
        return s - err, s + err
    a_lo, a_hi = atan_inv(5, 80)
    b_lo, b_hi = atan_inv(239, 30)
    return 16 * a_lo - 4 * b_hi, 16 * a_hi - 4 * b_lo


def _isqrt(n: int) -> int:
    if n < 0:
        raise ValueError("isqrt of negative")
    if n == 0:
        return 0
    x = 1 << ((n.bit_length() + 1) // 2)
    while True:
        y = (x + n // x) // 2
        if y >= x:
            return x
        x = y


def _inv_sqrt_2pi_int():
    """(lo, hi) integers with lo/2^P <= 1/sqrt(2 pi) <= hi/2^P."""
    plo, phi_ = _pi_bounds()
    # sqrt(2 pi) bounds on the 2^-P grid
    s_lo_n = 2 * plo.numerator * (1 << (2 * PREC)) // plo.denominator
    s_hi_n = _cdiv(2 * phi_.numerator * (1 << (2 * PREC)), phi_.denominator)
    sq_lo = _isqrt(s_lo_n)            # floor sqrt  <= sqrt(2pi) * 2^P
    sq_hi = _isqrt(s_hi_n) + 1        # >= sqrt(2pi) * 2^P
    inv_lo = (ONE * ONE) // sq_hi
    inv_hi = _cdiv(ONE * ONE, sq_lo)
    return inv_lo, inv_hi


INV_S2PI = _inv_sqrt_2pi_int()
PI_LO, PI_HI = _pi_bounds()


def _exp_pos_int(y: F):
    """(lo, hi) integers: lo/2^P <= exp(y) <= hi/2^P, y >= 0 rational."""
    if y < 0:
        raise ValueError("exp_pos needs y >= 0")
    a, b = y.numerator, y.denominator
    tlo, thi = ONE, ONE
    slo, shi = ONE, ONE
    n = 0
    while True:
        n += 1
        tlo = (tlo * a) // (b * n)
        thi = _cdiv(thi * a, b * n)
        slo += tlo
        shi += thi
        q = F(a, b * (n + 1))
        if n > 2 * y + 10 and q < F(1, 2) and thi <= 1:
            # tail <= t_n * q/(1-q)
            tail = _cdiv(thi * q.numerator, q.denominator - q.numerator)
            return slo, shi + tail + 1


@lru_cache(maxsize=200000)
def exp_neg(y: F):
    """rigorous exp(-y), y >= 0, as Fractions (lo, hi)."""
    elo, ehi = _exp_pos_int(F(y))
    lo = (ONE * ONE) // ehi
    hi = _cdiv(ONE * ONE, elo)
    return F(lo, ONE), F(hi, ONE)


def _phi_int(t: F):
    elo, ehi = exp_neg(t * t / 2)
    lo_n = (elo.numerator * INV_S2PI[0] * ONE) // (elo.denominator * ONE)
    hi_n = _cdiv(ehi.numerator * INV_S2PI[1] * ONE, ehi.denominator * ONE)
    return lo_n, hi_n       # integers on the 2^-P grid


@lru_cache(maxsize=200000)
def phi(t) -> tuple:
    t = F(t)
    lo, hi = _phi_int(t)
    return F(lo, ONE), F(hi, ONE)


def _series_int(t: F):
    """(lo, hi) integers bounding sum_{n>=0} t^(2n+1)/(2n+1)!! * 2^P, t >= 0."""
    a2, b2 = (t * t).numerator, (t * t).denominator
    alo = (t.numerator * ONE) // t.denominator
    ahi = _cdiv(t.numerator * ONE, t.denominator)
    slo, shi = alo, ahi
    n = 0
    while True:
        n += 1
        alo = (alo * a2) // (b2 * (2 * n + 1))
        ahi = _cdiv(ahi * a2, b2 * (2 * n + 1))
        slo += alo
        shi += ahi
        q = F(a2, b2 * (2 * n + 3))
        if q < F(1, 2) and ahi <= 1:
            tail = _cdiv(ahi * q.numerator, q.denominator - q.numerator)
            return slo, shi + tail + 1


@lru_cache(maxsize=200000)
def Phi(t) -> tuple:
    t = F(t)
    if t < 0:
        lo, hi = Phi(-t)
        return 1 - hi, 1 - lo
    if t == 0:
        return F(1, 2), F(1, 2)
    plo, phi_ = _phi_int(t)
    slo, shi = _series_int(t)
    lo = F(ONE // 2 * ONE + plo * slo, ONE * ONE)
    hi = F(ONE // 2 * ONE + phi_ * shi, ONE * ONE)
    return lo, min(hi, F(1))


def hermite_he(n: int, t: F) -> F:
    """probabilists' Hermite He_n(t), exact."""
    if n == 0:
        return F(1)
    h0, h1 = F(1), F(t)
    for k in range(1, n):
        h0, h1 = h1, t * h1 - k * h0
    return h1


def abs_moment_upper(n: int) -> F:
    """rational upper bound of E|Y|^n, Y ~ N(0,1)."""
    df = 1
    for k in range(n - 1, 0, -2):
        df *= k
    if n % 2 == 0:
        return F(df)
    # odd: (n-1)!! sqrt(2/pi);  sqrt(2/pi) <= 0.7978845609 (checked below against pi bounds)
    s = F(7978845609, 10 ** 10)
    assert s * s * PI_LO >= 2, "sqrt(2/pi) bound failed"
    return df * s


def dphi_sup(n: int) -> F:
    """upper bound of sup_t |phi^(n)(t)| = E|Y|^n / sqrt(2 pi)."""
    return abs_moment_upper(n) * F(INV_S2PI[1], ONE)


KAPPA1 = F(7978845609, 10 ** 10)          # >= sqrt(2/pi) = E|Y|   (asserted in abs_moment_upper)


def kappa2_upper() -> F:
    """4 phi(1) = E|Y^2 - 1| upper bound."""
    return 4 * phi(F(1))[1]


def selftest(verbose=True) -> dict:
    import math
    out = {}
    # pi bounds bracket math.pi
    out["pi_ok"] = float(PI_LO) <= math.pi <= float(PI_HI) and PI_HI - PI_LO < F(1, 10 ** 40)
    worst = 0.0
    for t in [F(0), F(1, 3), F(-7, 4), F(5, 2), F(-11, 2), F(17, 2), F(-9)]:
        lo, hi = Phi(t)
        ref = 0.5 * math.erfc(-float(t) / math.sqrt(2))
        worst = max(worst, abs(float((lo + hi) / 2) - ref) / max(ref, 1e-300))
        assert lo <= hi and hi - lo < F(1, 10 ** 30), (t, float(hi - lo))
        plo, phh = phi(t)
        refp = math.exp(-float(t) ** 2 / 2) / math.sqrt(2 * math.pi)
        worst = max(worst, abs(float(plo) - refp) / refp)
    out["float_agreement_rel"] = worst
    out["float_agreement_ok"] = worst < 1e-12
    # standard normal moments by M_j recurrence would be tested in the kernel module
    out["kappa1"] = float(KAPPA1)
    out["kappa2_up"] = float(kappa2_upper())
    if verbose:
        print(out)
    return out


if __name__ == "__main__":
    selftest()
