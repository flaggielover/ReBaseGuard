"""Rigorous rational enclosures of the standard normal phi and Phi, and of E[(|z| - K)^+].

Exact `fractions.Fraction` arithmetic throughout with explicit outward rounding. No float is used in any value that
reaches a certificate, no library special function is called, and nothing here touches an operator, a kernel, a K1
record or a scientific address: the inputs are two rational numbers (a drift e and the frozen CUSUM reference K).

Every series carries a proved remainder bound, and each is checked at run time rather than assumed:

  exp(y), y >= 0   S_N = sum_{n<=N} y^n/n!;  0 < exp(y) - S_N <= y^(N+1)/(N+1)! * 1/(1 - y/(N+2))   for y < N+2.
                   Verified by the ratio test on the tail; the guard raises if y >= N + 2.

  I(t) = int_0^t exp(-u^2/2) du = sum_{n>=0} (-1)^n t^(2n+1) / (2^n n! (2n+1)).
                   Alternating. |a_{n+1}/a_n| = t^2 (2n+1) / (2(n+1)(2n+3)) < 1 once n >= t^2/2, so from that index
                   the partial sums bracket the limit and the truncation error is at most the first omitted term.
                   The guard checks the terms really are decreasing over the whole truncated tail it relies on.

  Phi(t) = 1/2 + I(t)/sqrt(2 pi),   phi(t) = exp(-t^2/2)/sqrt(2 pi),   Phi(-t) = 1 - Phi(t).

  pi: Machin, pi/4 = 4 arctan(1/5) - arctan(1/239), each arctan by its alternating series with the first-omitted-term
      bound. sqrt(2 pi) by integer square root at 2^-SCALE, rounded outward.
"""
from fractions import Fraction as F

SCALE = 320                      # outward-rounding grid, 2^-SCALE
EXP_TERMS = 220
ERF_TERMS = 240
ATAN_TERMS = 400


class Refusal(Exception):
    pass


def _out(x: F, up: bool) -> F:
    """Round a Fraction outward onto the 2^-SCALE grid."""
    n, d = x.numerator * (1 << SCALE), x.denominator
    q, r = divmod(n, d)
    if r and up:
        q += 1
    return F(q, 1 << SCALE)


class Iv:
    """A closed rational interval. Every operation rounds outward onto the grid."""
    __slots__ = ("lo", "hi")

    def __init__(self, lo, hi=None):
        lo = F(lo)
        hi = lo if hi is None else F(hi)
        if lo > hi:
            raise Refusal("inverted interval")
        self.lo, self.hi = _out(lo, False), _out(hi, True)

    def __add__(self, o):
        o = o if isinstance(o, Iv) else Iv(o)
        return Iv(self.lo + o.lo, self.hi + o.hi)

    def __sub__(self, o):
        o = o if isinstance(o, Iv) else Iv(o)
        return Iv(self.lo - o.hi, self.hi - o.lo)

    def __rsub__(self, o):
        return Iv(o) - self

    def __mul__(self, o):
        o = o if isinstance(o, Iv) else Iv(o)
        c = (self.lo * o.lo, self.lo * o.hi, self.hi * o.lo, self.hi * o.hi)
        return Iv(min(c), max(c))

    __rmul__ = __mul__

    def __truediv__(self, o):
        o = o if isinstance(o, Iv) else Iv(o)
        if o.lo <= 0 <= o.hi:
            raise Refusal("division by an interval containing zero")
        c = (self.lo / o.lo, self.lo / o.hi, self.hi / o.lo, self.hi / o.hi)
        return Iv(min(c), max(c))

    def __repr__(self):
        return f"[{float(self.lo):.15g}, {float(self.hi):.15g}]"


def _atan_small(x: F, terms: int = ATAN_TERMS) -> Iv:
    """arctan(x) for 0 < x < 1 by its alternating series; error at most the first omitted term."""
    if not (0 < x < 1):
        raise Refusal("arctan series needs 0 < x < 1")
    s, p = F(0), x
    x2 = x * x
    for n in range(terms):
        s += (-1) ** n * p / (2 * n + 1)
        p *= x2
    err = p / (2 * terms + 1)                      # p is now x^(2*terms+1)
    return Iv(s - err, s + err)


def pi_iv() -> Iv:
    return 4 * (4 * _atan_small(F(1, 5)) - _atan_small(F(1, 239)))


def sqrt_iv(v: Iv) -> Iv:
    if v.lo <= 0:
        raise Refusal("sqrt of a non-positive interval")
    out = []
    for x, up in ((v.lo, False), (v.hi, True)):
        n = (x.numerator * (1 << (2 * SCALE))) // x.denominator
        r = _isqrt(n)
        out.append(F(r, 1 << SCALE) if not up else F(r + 1, 1 << SCALE))
    return Iv(out[0], out[1])


def _isqrt(n: int) -> int:
    if n < 0:
        raise Refusal("isqrt of a negative integer")
    x = 1 << ((n.bit_length() + 1) // 2)
    while True:
        y = (x + n // x) // 2
        if y >= x:
            return x
        x = y


def sqrt_two_pi() -> Iv:
    return sqrt_iv(2 * pi_iv())


def exp_neg(y: F, terms: int = EXP_TERMS) -> Iv:
    """exp(-y) for y >= 0, as 1 / exp(y) with a proved tail bound on exp(y)."""
    if y < 0:
        raise Refusal("exp_neg expects y >= 0")
    if y >= terms + 2:
        raise Refusal("exp series tail bound needs y < N + 2")
    s, p = F(0), F(1)
    for n in range(terms + 1):
        s += p
        p = p * y / (n + 1)                        # p is now y^(n+1)/(n+1)!
    tail_hi = p / (1 - F(y) / (terms + 2))         # p == y^(N+1)/(N+1)!
    return Iv(1, 1) / Iv(s, s + tail_hi)


def _erf_integral(t: F, terms: int = ERF_TERMS) -> Iv:
    """I(t) = int_0^t exp(-u^2/2) du for t >= 0, by the alternating series."""
    if t < 0:
        raise Refusal("I(t) is computed for t >= 0 and reflected by the caller")
    if t == 0:
        return Iv(0, 0)
    t2 = t * t
    a, s = t, F(0)                                  # a = t^(2n+1)/(2^n n!)
    mags = []
    for n in range(terms):
        term = a / (2 * n + 1)
        mags.append(abs(term))
        s += (-1) ** n * term
        a = a * t2 / (2 * (n + 1))
    nxt = abs(a / (2 * terms + 1))
    # the alternating-series bound is only valid where the magnitudes really are decreasing
    start = 0
    while start < len(mags) - 1 and mags[start + 1] > mags[start]:
        start += 1
    if start >= terms - 2:
        raise Refusal("the alternating series has not entered its decreasing regime")
    for n in range(start, len(mags) - 1):
        if mags[n + 1] > mags[n]:
            raise Refusal("magnitudes are not monotone over the tail the bound relies on")
    if nxt > mags[-1]:
        raise Refusal("the first omitted term exceeds the last kept term")
    return Iv(s - nxt, s + nxt)


def Phi(t: F) -> Iv:
    """Standard normal CDF at a rational point, as a rigorous interval."""
    t = F(t)
    if t < 0:
        return 1 - Phi(-t)
    return Iv(F(1, 2), F(1, 2)) + _erf_integral(t) / sqrt_two_pi()


def phi(t: F) -> Iv:
    """Standard normal density at a rational point, as a rigorous interval."""
    t = F(t)
    return exp_neg(t * t / 2) / sqrt_two_pi()


def E_excess(e: F, K: F) -> Iv:
    """E[(|z| - K)^+] for z ~ N(e, 1), K > 0, as a rigorous interval.

    E[(z - K)^+]  = (e - K) Phi(e - K) + phi(e - K)
    E[(-z - K)^+] = -(e + K) Phi(-(e + K)) + phi(e + K)
    and the two events {z > K}, {z < -K} are disjoint because K > 0, so (|z| - K)^+ is their sum.
    The law of |z| is the same for N(e, 1) and N(-e, 1), so the sign convention on the drift does not enter.
    """
    e, K = F(e), F(K)
    if K <= 0:
        raise Refusal("the CUSUM reference value K must be positive")
    a, b = e - K, e + K
    return (Iv(a, a) * Phi(a) + phi(a)) + (Iv(-b, -b) * Phi(-b) + phi(b))
