#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
srk_verify_indep.py -- an INDEPENDENT verifier for SRK_CERT/1 certificates.

Written from the mathematical specification only (impl/SRK_CERT_SPEC.md, theory/THEOREM_SRK.md sections 1, 2, 9 and
OPERATOR_AUDIT section 1).  No producer code was read or imported.  Standard-library Python only; every inequality is
decided with exact integers / Fractions or with outward-rounded fixed-point enclosures.

Usage
-----
    python3 srk_verify_indep.py CERT.json [--index I] [--max-depth 24] [--order 8] [--procs 1] [--json OUT]

CERT.json is either a bare SRK_CERT/1 object or a decoy-suite file {"certificates": {i: cert}, ...}.  Without
--index every certificate of a suite file is verified.  Exit status 0 iff every verified certificate is ACCEPTED.

What is decided
---------------
For the model of SRK_CERT_SPEC.md section 1 (geometry (h, k), c = h + k, X the reachable closure) and the certificate
polynomials V_e = V0 + (e - e_c) V1, W_e = W0 + (e - e_c) W1:

    (C1)  W_e(x) >= 0                              for all x in X, e in E = block
    (C2)  W_e(x) - (K_e W_e)(x) - 1 >= 0           for all x in X, e in E
    (C3)  V_e(x) - (K_e V_e)(x) - kbar(x) >= 0     for all x in X, e in E,
          kbar(x) = sup_{e' in Ew} k_i(x; e'),  Ew = weight_block (default: block)
    (C4)  Gamma >= max(V_{e_lo}(a), V_{e_hi}(a))   exact rational comparison
    and sha256(canonical JSON of all other keys) == sha256.

With "kernel": "taboo" (certificate or file level) K_e is replaced in (C2)/(C3) by the taboo kernel (atom sub-window
z in [m - k, k - p] removed).  For the frozen real geometry (h, k) = (5, 1/2) any certificate whose block or weight
block meets [6/5, 13/5] or [-13/5, -6/5] is REFUSED before any evaluation.

Method (and why it is sound)
----------------------------
1.  Closed form of the kernel.  With sigma = p - e, tau = m + e, t = e - e_c and u = z + e, the images of the three
    clipping pieces are (0, tau-u-k), (sigma+u-k, tau-u-k), (sigma+u-k, 0) (and the atom (0,0) when p+m <= 2k); the
    four window limits are  L1 = tau - c,  L2 = k - sigma,  L3 = tau - k,  L4 = c - sigma.  For a polynomial
    Q(u) = sum_n a_n u^n,  int_A^B Q phi = (sum_n a_n c_n)(Phi(B) - Phi(A)) + (sum_n a_n H_n(A)) phi(A)
    - (sum_n a_n H_n(B)) phi(B), with c_n = (n-1)!! (n even, c_0 = 1), c_n = 0 (n odd), H_0 = 0, H_1 = 1,
    H_n = u^{n-1} + (n-1) H_{n-2}; this is the spec's recursion M_n = (n-1) M_{n-2} + A^{n-1}phi(A) - B^{n-1}phi(B)
    solved in closed form (checked by induction and by the quadrature self-test).  Hence, on each of the two regions
    p + m >= 2k ("case A") and p + m <= 2k ("case B"),
        (K_e P)(x) = sum_{L in L1..L4} alpha_L(sigma, tau, t) Phi(L) + beta_L(sigma, tau, t) phi(L)
    with EXACT rational polynomials alpha_L, beta_L computed once per certificate (derived here by expanding
    P(image) in u; the piece ordering m-c <= k-p <= m-k <= c-p (case A) / m-c <= m-k <= k-p <= c-p (case B) holds on
    X because p + m <= h + 2k there).  Each case formula is an entire function of (sigma, tau, t); it equals K_eP
    exactly on its closed region.
2.  Cover.  X = triangle {p, m >= 0, p + m <= h - 2k}  union  {m = 0, p in [h-2k, h]}  union  {p = 0, m in [h-2k, h]}.
    It is covered by prisms  Pi x [e0, e1]  where Pi = (axis-parallel box) intersected with the half-planes
    p + m <= h - 2k and (case A/B) p + m >= 2k / <= 2k, or a segment for the two axis pieces; [e0, e1] runs over
    a subdivision of E.  Polygons are clipped with exact Fractions.  A cell is split (bisection of its widest
    dimension) until a certified lower bound is >= 0 or the depth limit is reached (then REJECT, reporting the cell).
3.  Taylor models.  On a cell, (sigma, tau, t) = centre + (r0 x0, r1 x1, r2 x2) with x in [-1, 1]^3 containing the
    prism (r0 = (w_p + w_e)/2, r1 = (w_m + w_e)/2, r2 = w_e/2).  Every polynomial is Taylor-shifted EXACTLY (integer
    arithmetic after clearing denominators), its coefficients are rounded to the fixed-point grid 2^-128 and every
    rounding error (<= 1 ulp per coefficient, since |x^a| <= 1) and every truncated term of total degree > N
    (bounded by |coefficient|) is added to an interval remainder.  Phi(L) and phi(L) are expanded in one variable
    around the rational centre L_c with derivatives Phi^(j) = (-1)^(j-1) He_{j-1} phi, phi^(j) = (-1)^j He_j phi and
    Lagrange remainder sup|He_N phi| s^(N+1)/(N+1)! (resp. He_{N+1}); products of Taylor models carry the standard
    remainder |A| rem_B + rem_A |B| + rem_A rem_B + (truncated products).  The exact cancellation between P and K_eP
    therefore happens inside the polynomial part.
4.  Lower bound of a Taylor model over a prism: constant + exact minimum of the linear part over the prism vertices
    (a linear function attains its minimum over a polytope at a vertex; vertices are exact rationals) + sum over
    monomials of degree >= 2 of min(0, c) (all exponents even, x^a in [0, 1]) or -|c| (otherwise) - remainder.
    On the two axis segments the prism is 2-dimensional and x1 = x2 (m = 0) resp. x0 = -x2 (p = 0) hold
    identically on it; these identities are substituted before bounding (exact on the feasible set).
5.  Gaussian enclosures.  pi from Machin's formula (alternating series, partial sums bracket the limit), 1/sqrt(2 pi)
    by integer square roots with directed rounding; exp(z), z >= 0, by argument halving + Taylor series with directed
    rounding + tail bound + repeated squaring; phi = exp(-x^2/2)/sqrt(2pi); Phi(x) = 1/2 + phi(x) sum x^(2n+1)/(2n+1)!!
    (positive series, geometric tail bound) for 0 <= x <= 8, Phi(x) in [1 - phi(x)/x, 1] (Mills) for x > 8, and
    Phi(-x) = 1 - Phi(x).  Ranges of |He_n| phi over intervals: centred form for He_n on pieces of width <= 1/4 and
    monotonicity of phi on each side of 0.
6.  The weight kbar(x) = sup_{e' in Ew} k_i(x; e'),  k_i(x; e') = G(c - p + e') - G(m - c + e'),  G(u) = int_{-inf}^u
    |He_i| phi.  For i >= 1, with the roots r_0 < ... < r_{i-1} of He_i (isolated by exact sign changes and bisected
    to width 2^-200) and s_J = sign of He_i on piece J, G(u) = C_J - s_J He_{i-1}(u) phi(u) on piece J with
    C_0 = 0, C_{J+1} = C_J + 2 s_{J+1} He_{i-1}(r_J) phi(r_J).  Near a root, G_{J+1} - G_J = 2 s_{J+1}(H(r_J) - H(u))
    >= 0 (H = He_{i-1} phi), which gives the one-sided rules used when a cell is split at a root line.
    Sup over e': on a subinterval I = [a, b] of Ew, if d/de' k = g(c-p+e') - g(m-c+e') (g = |He_i| phi) has a
    certified sign over cell x I the sup is at an endpoint; otherwise sup_I k <= max(k(a), k(b)) + (b - a)^2/8 * M2
    with M2 >= sup |d^2/de'^2 k| (a.e.) <= sup|He_{i+1} phi|(c-p+e') + sup|He_{i+1} phi|(m-c+e') (the linear
    interpolation error bound for a C^{1,1} function).  Hence kbar(x) <= max_j k(x; e'_j) + delta on the cell, and
    (C3) follows from  min_j LB(D - k_j) - delta >= 0  where each k_j is a Taylor model in (x0, x2) / (x1, x2).
    Points e'_j whose k-range over the cell lies entirely below another point's k-range are dropped (valid: they
    never realise the max).
7.  Disproof.  When a cell fails, the verifier also evaluates a rigorous UPPER bound of the claimed quantity at the
    cell centre, and at the depth limit also at the cell vertices x e-endpoints (point Taylor model with zero radii;
    for (C3) kbar(x) >= k(x; e') for 17 sample e' in Ew).  If it is < 0 the claim is
    FALSE (reported as such); otherwise the failure is a method limitation (reported as UNPROVEN).

Assumptions (the soundness argument relies on): exactness of Python integer / Fraction arithmetic; the classical
facts used above (Machin's formula, alternating-series bracketing, Taylor's theorem with Lagrange remainder,
Mills' ratio 1 - Phi(x) <= phi(x)/x for x > 0, simplicity/interlacing-free isolation of the real roots of He_n
verified by counting n sign changes, the interpolation error bound for C^{1,1} functions); and the model of
SRK_CERT_SPEC.md section 1, whose closed form is re-derived here and cross-checked against quadrature in the tests.
Limitations: acceptance power is limited by the depth limit and Taylor order; a REJECT that is not a disproof may be
a method limitation.  Runtime grows quickly with the polynomial degree and the depth needed.
"""

import argparse
import hashlib
import json
import math
import multiprocessing as mp
import os
import re
import sys
import time
from fractions import Fraction as Fr
from functools import lru_cache
from math import comb, factorial, isqrt

# ----------------------------------------------------------------------------------------------------------------------
# precision
WX = 256            # bits of the internal special-function enclosures
WXL = 64            # bits of the cheap range enclosures
WB = 128            # bits of the Taylor-model coefficient grid
SH = WX - WB
ONEB = 1 << WB
HALFB = 1 << (WB - 1)

QUARANTINE_BANDS = ((Fr(6, 5), Fr(13, 5)), (Fr(-13, 5), Fr(-6, 5)))  # q309: literal-ok (the quarantine band definition (refusal), not an evaluation)


class CertError(Exception):
    """Malformed certificate: refuse."""


class Refusal(Exception):
    """Certificate outside the verifier's remit (quarantine band): refuse, do not evaluate."""


def cdiv(a, b):
    """ceil(a / b) for integer b > 0."""
    return -((-a) // b)


def fl(q, bits):
    """floor(q * 2^bits) for a Fraction q."""
    return (q.numerator << bits) // q.denominator


def ce(q, bits):
    """ceil(q * 2^bits) for a Fraction q."""
    return -((-q.numerator << bits) // q.denominator)


def iv_mul_q(lo, hi, q):
    """Outward enclosure of [lo, hi] * q (same fixed-point scale), q a Fraction."""
    n, d = q.numerator, q.denominator
    if n >= 0:
        return (lo * n) // d, cdiv(hi * n, d)
    return (hi * n) // d, cdiv(lo * n, d)


# ----------------------------------------------------------------------------------------------------------------------
# parsing / validation
_RAT_RE = re.compile(r'^[+-]?\d+(/\d+)?$')
_MON_RE = re.compile(r'^(\d+),(\d+)$')
REQUIRED = ('geometry', 'block', 'e_c', 'hermite_index', 'V0', 'V1', 'W0', 'W1', 'Gamma', 'sha256')


def parse_rat(s, what):
    if isinstance(s, bool) or not isinstance(s, str) or not _RAT_RE.match(s):
        raise CertError('%s: not a rational string "p/q": %r' % (what, s))
    if '/' in s:
        a, b = s.split('/')
        if int(b) == 0:
            raise CertError('%s: zero denominator' % what)
        return Fr(int(a), int(b))
    return Fr(int(s))


def parse_poly(obj, what):
    if not isinstance(obj, dict) or not obj:
        raise CertError('%s: expected a non-empty object {"a,b": "p/q"}' % what)
    out = {}
    for key, val in obj.items():
        mt = _MON_RE.match(key) if isinstance(key, str) else None
        if not mt:
            raise CertError('%s: bad monomial key %r' % (what, key))
        a, b = int(mt.group(1)), int(mt.group(2))
        if a + b > 24:
            raise CertError('%s: degree %d too large for this verifier' % (what, a + b))
        v = parse_rat(val, '%s[%s]' % (what, key))
        if v:
            out[(a, b)] = out.get((a, b), 0) + v
    return out


def canonical_sha(cert):
    body = {k: v for k, v in cert.items() if k != 'sha256'}
    return hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()


class Cert:
    """Validated, parsed certificate."""

    def __init__(self, raw, file_kernel=None):
        if not isinstance(raw, dict):
            raise CertError('certificate is not a JSON object')
        for key in REQUIRED:
            if key not in raw:
                raise CertError('missing key %r' % key)
        g = raw['geometry']
        if not isinstance(g, dict) or 'h' not in g or 'k' not in g:
            raise CertError('geometry must be {"h": .., "k": ..}')
        self.h = parse_rat(g['h'], 'geometry.h')
        self.k = parse_rat(g['k'], 'geometry.k')
        if not (self.h > 0 and self.k >= 0 and self.h - 2 * self.k >= 0):
            raise CertError('unsupported geometry (need h > 0, k >= 0, h >= 2k)')
        self.c = self.h + self.k
        self.S = self.h - 2 * self.k
        blk = raw['block']
        if not isinstance(blk, list) or len(blk) != 2:
            raise CertError('block must be ["e_lo", "e_hi"]')
        self.e_lo = parse_rat(blk[0], 'block[0]')
        self.e_hi = parse_rat(blk[1], 'block[1]')
        if self.e_lo > self.e_hi:
            raise CertError('block: e_lo > e_hi')
        self.e_c = parse_rat(raw['e_c'], 'e_c')
        if self.e_c != (self.e_lo + self.e_hi) / 2:
            raise CertError('e_c != (e_lo + e_hi)/2')
        wb = raw.get('weight_block', None)
        if wb is None:
            self.w_lo, self.w_hi = self.e_lo, self.e_hi
        else:
            if not isinstance(wb, list) or len(wb) != 2:
                raise CertError('weight_block must be ["w_lo", "w_hi"]')
            self.w_lo = parse_rat(wb[0], 'weight_block[0]')
            self.w_hi = parse_rat(wb[1], 'weight_block[1]')
            if not (self.w_lo <= self.e_lo and self.e_hi <= self.w_hi):
                raise CertError('weight_block does not contain block')
        hi = raw['hermite_index']
        if isinstance(hi, bool) or not isinstance(hi, int) or not (0 <= hi <= 8):
            raise CertError('hermite_index must be an integer in [0, 8]')
        self.i = hi
        kern = raw.get('kernel', None)
        if kern is not None and file_kernel is not None and kern != file_kernel:
            raise CertError('kernel key conflicts with the file-level kernel key')
        kern = kern if kern is not None else file_kernel
        if kern not in (None, 'whole', 'taboo'):
            raise CertError('unknown kernel %r' % (kern,))
        self.taboo = (kern == 'taboo')
        self.V0 = parse_poly(raw['V0'], 'V0')
        self.V1 = parse_poly(raw['V1'], 'V1')
        self.W0 = parse_poly(raw['W0'], 'W0')
        self.W1 = parse_poly(raw['W1'], 'W1')
        self.Gamma = parse_rat(raw['Gamma'], 'Gamma')
        sha = raw['sha256']
        if not isinstance(sha, str) or not re.match(r'^[0-9a-f]{64}$', sha):
            raise CertError('sha256 must be 64 lowercase hex digits')
        self.sha_ok = (canonical_sha(raw) == sha)
        # quarantine (frozen real geometry only)
        self.quarantined = False
        if self.h == 5 and self.k == Fr(1, 2):
            for (a, b) in QUARANTINE_BANDS:
                for (lo, hi_) in ((self.e_lo, self.e_hi), (self.w_lo, self.w_hi)):
                    if lo <= b and a <= hi_:
                        self.quarantined = True

    def describe(self):
        return ('h=%s k=%s block=[%s,%s] weight_block=[%s,%s] i=%d kernel=%s deg=%d'
                % (self.h, self.k, self.e_lo, self.e_hi, self.w_lo, self.w_hi, self.i,
                   'taboo' if self.taboo else 'whole', max(a + b for (a, b) in self.V0)))


def load_certs(path):
    """Returns list of (label, raw_cert, file_kernel)."""
    with open(path) as f:
        data = json.load(f)
    if isinstance(data, dict) and 'certificates' in data:
        certs = data['certificates']
        fk = data.get('kernel', None)
        if not isinstance(certs, dict):
            raise CertError('"certificates" must be an object')
        return [(str(k), certs[k], fk) for k in sorted(certs, key=lambda s: (len(str(s)), str(s)))]
    return [('-', data, None)]


# ----------------------------------------------------------------------------------------------------------------------
# rigorous constants
def _atan_inv(n, bits):
    """Bracket of arctan(1/n) (alternating series; partial sums bracket the limit)."""
    s = Fr(0)
    k = 0
    while True:
        t = Fr(1, (2 * k + 1) * n ** (2 * k + 1))
        if t < Fr(1, 1 << bits):
            nxt = t if k % 2 == 0 else -t
            return (s, s + nxt) if nxt > 0 else (s + nxt, s)
        s += t if k % 2 == 0 else -t
        k += 1


def _pi_bracket(bits=600):
    a_lo, a_hi = _atan_inv(5, bits)
    b_lo, b_hi = _atan_inv(239, bits)
    return 16 * a_lo - 4 * b_hi, 16 * a_hi - 4 * b_lo


PI_LO, PI_HI = _pi_bracket()


def _isq(bits):
    A = fl(2 * PI_LO, 2 * bits)
    B = ce(2 * PI_HI, 2 * bits)
    s_lo = isqrt(A)
    s_hi = isqrt(B) + 1
    return (1 << (2 * bits)) // s_hi, cdiv(1 << (2 * bits), s_lo)


ISQ = {WX: _isq(WX), WXL: _isq(WXL)}   # 1/sqrt(2 pi) at the two precisions


def _exp_pos(z, bits):
    """(lo, hi) with lo <= exp(z) 2^bits <= hi, z >= 0 a Fraction."""
    one = 1 << bits
    s = 0
    quarter = Fr(1, 4)
    while z > quarter * (1 << s):
        s += 1
    y = z / (1 << s)
    ylo, yhi = fl(y, bits), ce(y, bits)
    lo = one
    t = one
    n = 1
    while True:
        t = ((t * ylo) >> bits) // n
        if t == 0:
            break
        lo += t
        n += 1
    hi = one
    t = one
    n = 1
    while True:
        t = cdiv(cdiv(t * yhi, one), n)
        hi += t
        if t <= 1:
            break
        n += 1
    hi += 1          # tail: y <= 1/4, remaining terms < t/3 <= 1 ulp
    for _ in range(s):
        lo = (lo * lo) >> bits
        hi = cdiv(hi * hi, one)
    return lo, hi


@lru_cache(maxsize=400000)
def phi_iv(x, bits=WX):
    """Enclosure of phi(x) at scale 2^-bits (x a Fraction)."""
    elo, ehi = _exp_pos(x * x / 2, bits)
    one2 = 1 << (2 * bits)
    mlo, mhi = one2 // ehi, cdiv(one2, elo)
    ilo, ihi = ISQ[bits]
    return (mlo * ilo) >> bits, cdiv(mhi * ihi, 1 << bits)


@lru_cache(maxsize=400000)
def Phi_iv(x):
    """Enclosure of Phi(x) at scale 2^-WX."""
    one = 1 << WX
    if x < 0:
        lo, hi = Phi_iv(-x)
        return one - hi, one - lo
    if x == 0:
        return one >> 1, one >> 1
    if x > 8:
        plo, phh = phi_iv(x)
        return one - cdiv(phh * x.denominator, x.numerator), one
    plo, phh = phi_iv(x)
    xlo, xhi = fl(x, WX), ce(x, WX)
    x2lo, x2hi = (xlo * xlo) >> WX, cdiv(xhi * xhi, one)
    t = xlo
    S = t
    n = 0
    while True:
        t = ((t * x2lo) >> WX) // (2 * n + 3)
        n += 1
        if t == 0:
            break
        S += t
    Slo = S
    t = xhi
    S = t
    n = 0
    while True:
        t = cdiv(cdiv(t * x2hi, one), 2 * n + 3)
        n += 1
        S += t
        if 2 * x2hi <= (2 * n + 3) * one and t <= 1:
            break
    Shi = S + t
    lo = (one >> 1) + ((plo * Slo) >> WX)
    hi = (one >> 1) + cdiv(phh * Shi, one)
    return max(lo, 0), min(hi, one)


def phi_fr_range(a, b):
    """(lo, hi) Fractions bounding phi on [a, b] (monotone on each side of 0)."""
    near = Fr(0) if a <= 0 <= b else (a if a > 0 else b)
    far = a if abs(a) >= abs(b) else b
    return Fr(phi_iv(far, WXL)[0], 1 << WXL), Fr(phi_iv(near, WXL)[1], 1 << WXL)


# ----------------------------------------------------------------------------------------------------------------------
# Hermite polynomials
@lru_cache(None)
def he_coeffs(n):
    if n == 0:
        return (1,)
    if n == 1:
        return (0, 1)
    a, b = he_coeffs(n - 1), he_coeffs(n - 2)
    c = [0] * (n + 1)
    for j, v in enumerate(a):
        c[j + 1] += v
    for j, v in enumerate(b):
        c[j] -= (n - 1) * v
    return tuple(c)


def he_eval(n, x):
    r = Fr(0)
    for cf in reversed(he_coeffs(n)):
        r = r * x + cf
    return r


def he_values(x, nmax):
    vals = [Fr(1), Fr(x)]
    for n in range(1, nmax):
        vals.append(x * vals[n] - n * vals[n - 1])
    return vals[:nmax + 1]


def he_abscoef_bound(n, R):
    """sum_j |c_j| R^j >= sup_{|v| <= R} |He_n(v)|."""
    s = Fr(0)
    for cf in reversed(he_coeffs(n)):
        s = s * R + abs(cf)
    return s


def he_abs_bounds(n, a, b):
    """(lo, hi) Fractions with lo <= |He_n(v)| <= hi on [a, b] (centred form on pieces of width <= 1/4)."""
    if n == 0:
        return Fr(1), Fr(1)
    lo = None
    hi = Fr(0)
    x = a
    piece = Fr(1, 4)
    while True:
        y = b if b - x <= piece else x + piece
        mid = (x + y) / 2
        v = abs(he_eval(n, mid))
        R = max(abs(x), abs(y))
        rad = n * he_abscoef_bound(n - 1, R) * (y - x) / 2
        plo = v - rad if v > rad else Fr(0)
        lo = plo if lo is None or plo < lo else lo
        if v + rad > hi:
            hi = v + rad
        if y >= b:
            break
        x = y
    return lo, hi


def absHephi_bounds(n, a, b):
    """(lo, hi) Fractions with lo <= |He_n(v)| phi(v) <= hi on [a, b]."""
    lo = None
    hi = Fr(0)
    x = a
    piece = Fr(1, 4)
    while True:
        y = b if b - x <= piece else x + piece
        hlo, hhi = he_abs_bounds(n, x, y)
        flo, fhi = phi_fr_range(x, y)
        plo, phh = hlo * flo, hhi * fhi
        lo = plo if lo is None or plo < lo else lo
        if phh > hi:
            hi = phh
        if y >= b:
            break
        x = y
    return lo, hi


@lru_cache(None)
def he_roots(n):
    """Brackets (rl, rh), rh - rl <= 2^-200, of the n simple real roots of He_n, increasing."""
    if n == 0:
        return ()
    B = 2 * isqrt(n) + 3
    grid = [Fr(j, 64) for j in range(-64 * B, 64 * B + 1)]
    vals = [he_eval(n, x) for x in grid]
    br = []
    for j in range(len(grid) - 1):
        if vals[j] == 0:
            br.append((grid[j], grid[j]))
        elif vals[j] * vals[j + 1] < 0:
            br.append((grid[j], grid[j + 1]))
    if vals[-1] == 0:
        br.append((grid[-1], grid[-1]))
    if len(br) != n:
        raise RuntimeError('root isolation of He_%d failed' % n)
    out = []
    eps = Fr(1, 1 << 200)
    for (a, b) in br:
        if a == b:
            out.append((a, b))
            continue
        fa = he_eval(n, a)
        while b - a > eps:
            m = (a + b) / 2
            fm = he_eval(n, m)
            if fm == 0:
                a = b = m
                break
            if (fm < 0) == (fa < 0):
                a, fa = m, fm
            else:
                b = m
        out.append((a, b))
    return tuple(out)


def _fr_iv_from_fixed(lo, hi, bits):
    return Fr(lo, 1 << bits), Fr(hi, 1 << bits)


@lru_cache(None)
def g_structure(n):
    """For n >= 1: roots, signs s_J (J = 0..n), constants C_J (WX enclosures), err_q (WB ints).
    G(u) = C_J - s_J He_{n-1}(u) phi(u) on piece J (between root J-1 and root J)."""
    roots = he_roots(n)
    signs = tuple((-1) ** (n - J) for J in range(n + 1))
    C = [(Fr(0), Fr(0))]
    errs = []
    for q, (rl, rh) in enumerate(roots):
        # H(r) = He_{n-1}(r) phi(r), r in [rl, rh]
        w = rh - rl
        R = max(abs(rl), abs(rh))
        hv = he_eval(n - 1, rl)
        hrad = (n - 1) * he_abscoef_bound(n - 2, R) * w if n >= 2 else Fr(0)
        h_lo, h_hi = hv - hrad, hv + hrad
        p1 = _fr_iv_from_fixed(*phi_iv(rl), WX)
        p2 = _fr_iv_from_fixed(*phi_iv(rh), WX)
        f_lo, f_hi = min(p1[0], p2[0]), max(p1[1], p2[1])
        prods = [h_lo * f_lo, h_lo * f_hi, h_hi * f_lo, h_hi * f_hi]
        H_lo, H_hi = min(prods), max(prods)
        s = signs[q + 1]
        a, b = (2 * H_lo, 2 * H_hi) if s > 0 else (-2 * H_hi, -2 * H_lo)
        C.append((C[-1][0] + a, C[-1][1] + b))
        # err: sup over the bracket of |G_{q+1} - G_q| <= 2 w sup|He_n phi|
        err = 2 * w * he_abscoef_bound(n, R) * Fr(2, 5)
        errs.append(ce(err, WB) + 1)
    Cfx = tuple((fl(a, WX), ce(b, WX)) for (a, b) in C)
    return roots, signs, Cfx, tuple(errs)


def piece_of(n, u):
    """Index J of the piece containing u, and whether u lies inside a root bracket."""
    roots = he_roots(n)
    J = 0
    inside = False
    for (rl, rh) in roots:
        if rh <= u:
            J += 1
        elif rl < u:
            inside = True
    return J, inside


def G_value(n, u):
    """Enclosure (WX ints) of G_n(u) = int_{-inf}^u |He_n| phi at a rational u."""
    if n == 0:
        return Phi_iv(u)
    roots, signs, C, errs = g_structure(n)
    J, inside = piece_of(n, u)
    hv = he_eval(n - 1, u)
    plo, phh = phi_iv(u)
    a, b = iv_mul_q(plo, phh, hv)            # He_{n-1}(u) phi(u)
    if signs[J] > 0:
        lo, hi = C[J][0] - b, C[J][1] - a
    else:
        lo, hi = C[J][0] + a, C[J][1] + b
    if inside:
        e = errs[J] << SH if J < len(errs) else 0
        lo, hi = lo - e, hi + e
    return lo, hi


@lru_cache(maxsize=200000)
def G_taylor(n, J, uc, N):
    """WX enclosures of the Taylor coefficients g_r (r = 0..N) of G_J(uc + s) in powers of s, where G_J is the
    analytic formula of piece J (n >= 1) or Phi (n == 0)."""
    plo, phh = phi_iv(uc)
    if n == 0:
        he = he_values(uc, N)
        out = [Phi_iv(uc)]
        for r in range(1, N + 1):
            q = Fr((-1) ** (r - 1)) * he[r - 1] / factorial(r)
            out.append(iv_mul_q(plo, phh, q))
        return tuple(out)
    roots, signs, C, errs = g_structure(n)
    sJ = signs[J]
    he = he_values(uc, n - 1 + N)
    out = []
    for r in range(0, N + 1):
        q = -sJ * Fr((-1) ** r) * he[n - 1 + r] / factorial(r)
        a, b = iv_mul_q(plo, phh, q)
        if r == 0:
            a, b = a + C[J][0], b + C[J][1]
        out.append((a, b))
    return tuple(out)


# ----------------------------------------------------------------------------------------------------------------------
# exact polynomial algebra (dict: exponent tuple -> Fraction)
def p_add(A, B, s=1):
    C = dict(A)
    for e, v in B.items():
        w = C.get(e, 0) + s * v
        if w:
            C[e] = w
        else:
            C.pop(e, None)
    return C


def p_mul(A, B):
    C = {}
    for ea, ca in A.items():
        for eb, cb in B.items():
            e = tuple(x + y for x, y in zip(ea, eb))
            C[e] = C.get(e, 0) + ca * cb
    return {e: v for e, v in C.items() if v}


def p_scale(A, s):
    return {e: v * s for e, v in A.items() if v * s}


def p_powers(L, n, nvars):
    out = [{(0,) * nvars: Fr(1)}]
    for _ in range(n):
        out.append(p_mul(out[-1], L))
    return out


def dfact(n):
    """c_n: (n-1)!! for even n (c_0 = 1), 0 for odd n."""
    if n % 2:
        return 0
    r = 1
    for j in range(n - 1, 0, -2):
        r *= j
    return r


class IntPoly:
    """Polynomial in (sigma, tau, t) with integer coefficients over a common denominator."""
    __slots__ = ('c', 'den', 'deg')

    def __init__(self, P):
        den = 1
        for v in P.values():
            den = den * v.denominator // math.gcd(den, v.denominator)
        self.den = den
        self.c = {e: int(v * den) for e, v in P.items() if v}
        self.deg = max((sum(e) for e in self.c), default=0)


class PolySet:
    """Everything needed for D = P - K_e P of one certificate polynomial pair (P0, P1): P = P0 + t P1."""

    def __init__(self, P0, P1, h, k, e_c, taboo):
        c = h + k
        self.raw0, self.raw1 = P0, P1
        d = max(max(a + b for (a, b) in P0), max((a + b for (a, b) in P1), default=0))
        self.d = d
        # variables (sigma, tau, t, u)
        X = {(1, 0, 0, 0): Fr(1), (0, 0, 0, 1): Fr(1), (0, 0, 0, 0): -k}          # sigma + u - k
        Y = {(0, 1, 0, 0): Fr(1), (0, 0, 0, 1): Fr(-1), (0, 0, 0, 0): -k}         # tau - u - k
        Xp = p_powers(X, d, 4)
        Yp = p_powers(Y, d, 4)

        def pab(a, b):
            out = {}
            if P0.get((a, b)):
                out[(0, 0, 0, 0)] = P0[(a, b)]
            if P1.get((a, b)):
                out[(0, 0, 1, 0)] = P1[(a, b)]
            return out

        mons = set(P0) | set(P1)
        Q2, Q1, Q3 = {}, {}, {}
        for (a, b) in mons:
            co = pab(a, b)
            if not co:
                continue
            Q2 = p_add(Q2, p_mul(co, p_mul(Xp[a], Yp[b])))
            if a == 0:
                Q1 = p_add(Q1, p_mul(co, Yp[b]))
            if b == 0:
                Q3 = p_add(Q3, p_mul(co, Xp[a]))
        Q0 = pab(0, 0)

        def ucoef(Q):
            out = {}
            for e, v in Q.items():
                out.setdefault(e[3], {})[e[:3]] = v
            return out

        L = {1: {(0, 1, 0): Fr(1), (0, 0, 0): -c}, 2: {(1, 0, 0): Fr(-1), (0, 0, 0): k},
             3: {(0, 1, 0): Fr(1), (0, 0, 0): -k}, 4: {(1, 0, 0): Fr(-1), (0, 0, 0): c}}
        self.L = L
        nmax = d + 1
        Hn = {}
        for li, Lp in L.items():
            pw = p_powers({e: v for e, v in Lp.items() if v}, nmax, 3)
            H = [{}, {(0, 0, 0): Fr(1)}]
            for n in range(2, nmax + 1):
                H.append(p_add(pw[n - 1], p_scale(H[n - 2], n - 1)))
            Hn[li] = H

        def S_of(Qc):
            out = {}
            for n, a in Qc.items():
                if dfact(n):
                    out = p_add(out, p_scale(a, dfact(n)))
            return out

        def Hs_of(Qc, li):
            out = {}
            for n, a in Qc.items():
                if n >= 1:
                    out = p_add(out, p_mul(a, Hn[li][n]))
            return out

        pieces = {'A': [(Q1, 1, 2), (Q2, 2, 3), (Q3, 3, 4)],
                  'B': [(Q1, 1, 3), (Q3, 2, 4)] + ([] if taboo else [(Q0, 3, 2)])}
        self.alpha, self.beta = {}, {}
        self.alpha_frac, self.beta_frac = {}, {}      # exact rational forms (used by the self-tests)
        for case, plist in pieces.items():
            al = {li: {} for li in L}
            be = {li: {} for li in L}
            for (Q, A, B) in plist:
                Qc = ucoef(Q)
                S = S_of(Qc)
                al[B] = p_add(al[B], S)
                al[A] = p_add(al[A], S, -1)
                be[A] = p_add(be[A], Hs_of(Qc, A))
                be[B] = p_add(be[B], Hs_of(Qc, B), -1)
            self.alpha[case] = {li: IntPoly(al[li]) for li in L}
            self.beta[case] = {li: IntPoly(be[li]) for li in L}
            self.alpha_frac[case] = al
            self.beta_frac[case] = be
        # P(sigma + e_c + t, tau - e_c - t, t)
        Xs = {(1, 0, 0): Fr(1), (0, 0, 1): Fr(1), (0, 0, 0): e_c}
        Ys = {(0, 1, 0): Fr(1), (0, 0, 1): Fr(-1), (0, 0, 0): -e_c}
        Xsp = p_powers({e: v for e, v in Xs.items() if v}, d, 3)
        Ysp = p_powers({e: v for e, v in Ys.items() if v}, d, 3)
        Pst = {}
        for (a, b) in mons:
            co = {}
            if P0.get((a, b)):
                co[(0, 0, 0)] = P0[(a, b)]
            if P1.get((a, b)):
                co[(0, 0, 1)] = P1[(a, b)]
            if co:
                Pst = p_add(Pst, p_mul(co, p_mul(Xsp[a], Ysp[b])))
        self.st_frac = Pst
        self.st = IntPoly(Pst)

    def eval_raw(self, p, m, t):
        s = Fr(0)
        for (a, b), v in self.raw0.items():
            s += v * p ** a * m ** b
        for (a, b), v in self.raw1.items():
            s += t * v * p ** a * m ** b
        return s


# ----------------------------------------------------------------------------------------------------------------------
# Taylor models: dict {(i, j, l): int at scale 2^-WB} + remainder (int, scale 2^-WB), variables x in [-1, 1]^3
def int_taylor_shift(c, a):
    """c: dict exponent -> int.  Returns coefficients of R(a + w) (exact integer Taylor shift)."""
    for v in range(3):
        av = a[v]
        if av == 0:
            continue
        groups = {}
        for e, val in c.items():
            groups.setdefault(e[:v] + e[v + 1:], {})[e[v]] = val
        newc = {}
        for key, g in groups.items():
            n = max(g)
            arr = [g.get(i, 0) for i in range(n + 1)]
            for i in range(n):
                for j in range(n - 1, i - 1, -1):
                    arr[j] += av * arr[j + 1]
            for i, val in enumerate(arr):
                if val:
                    newc[key[:v] + (i,) + key[v:]] = val
        c = newc
    return c


class Frame:
    """Centre/radii of a cell's Taylor-model frame, with integer representations for exact shifting."""
    __slots__ = ('cen', 'rad', 'Q', 'a', 'Rd', 'rn')

    def __init__(self, cen, rad):
        self.cen = cen
        self.rad = rad
        Q = 1
        for x in cen:
            Q = Q * x.denominator // math.gcd(Q, x.denominator)
        self.Q = Q
        self.a = tuple(int(x * Q) for x in cen)
        Rd = 1
        for x in rad:
            Rd = Rd * x.denominator // math.gcd(Rd, x.denominator)
        self.Rd = Rd
        self.rn = tuple(int(x * Rd) for x in rad)


def shift_to_tm(ip, fr, N):
    """Exact Taylor shift of an IntPoly into the frame, rounded to the WB grid, truncated at total degree N."""
    if not ip.c:
        return {}, 0
    d = ip.deg
    Q = fr.Q
    Qp = [1]
    for _ in range(d):
        Qp.append(Qp[-1] * Q)
    c = {e: v * Qp[d - (e[0] + e[1] + e[2])] for e, v in ip.c.items()}
    c = int_taylor_shift(c, fr.a)
    r0, r1, r2 = fr.rn
    P0 = [r0 ** j for j in range(d + 1)]
    P1 = [r1 ** j for j in range(d + 1)]
    P2 = [r2 ** j for j in range(d + 1)]
    base = Qp[d] * ip.den
    Rdp = [1]
    for _ in range(d):
        Rdp.append(Rdp[-1] * fr.Rd)
    tm = {}
    rem = 0
    trunc_num = {}
    for e, v in c.items():
        s = e[0] + e[1] + e[2]
        num = v * Qp[s] * P0[e[0]] * P1[e[1]] * P2[e[2]]
        if num == 0:
            continue
        if s <= N:
            D = base * Rdp[s]
            tm[e] = ((num << (WB + 1)) + D) // (2 * D)
            rem += 1
        else:
            trunc_num[s] = trunc_num.get(s, 0) + abs(num)
    for s, num in trunc_num.items():
        rem += cdiv(num << WB, base * Rdp[s])
    return tm, rem


def fx_to_tmcoef(lo, hi):
    """WX interval -> (WB midpoint, WB radius bound)."""
    lo_b = lo >> SH
    hi_b = cdiv(hi, 1 << SH)
    mid = (lo_b + hi_b) >> 1
    return mid, hi_b - mid


@lru_cache(maxsize=100000)
def univ_Phi_phi(Lc, s, N):
    """Univariate Taylor models (in x in [-1, 1], L = Lc + s x) of Phi(L) and phi(L), order N.
    Returns (Phi_coefs, Phi_rem, phi_coefs, phi_rem) on the WB grid."""
    plo, phh = phi_iv(Lc)
    he = he_values(Lc, N + 1)
    Phi_c, phi_c = [], []
    Phi_r = phi_r = 0
    m, r = fx_to_tmcoef(*Phi_iv(Lc))
    Phi_c.append(m)
    Phi_r += r
    sp = Fr(1)
    for j in range(0, N + 1):
        if j >= 1:
            sp *= s
            q = Fr((-1) ** (j - 1)) * he[j - 1] * sp / factorial(j)
            m, r = fx_to_tmcoef(*iv_mul_q(plo, phh, q))
            Phi_c.append(m)
            Phi_r += r
        q = Fr((-1) ** j) * he[j] * sp / factorial(j)
        m, r = fx_to_tmcoef(*iv_mul_q(plo, phh, q))
        phi_c.append(m)
        phi_r += r
    sa = abs(s)
    if sa:
        f = sa ** (N + 1) / factorial(N + 1)
        Phi_r += ce(absHephi_bounds(N, Lc - sa, Lc + sa)[1] * f, WB) + 1
        phi_r += ce(absHephi_bounds(N + 1, Lc - sa, Lc + sa)[1] * f, WB) + 1
    return tuple(Phi_c), Phi_r + N + 2, tuple(phi_c), phi_r + N + 2


def mul_sub_acc(acc, A, Arem, B, Brem, var, N):
    """acc (scale 2^-2WB) -= A * B, B univariate in variable `var`.  Returns the WB remainder contribution."""
    trunc = 0
    normA = 0
    for e, a in A.items():
        normA += abs(a)
        lim = N - (e[0] + e[1] + e[2])
        for r, b in enumerate(B):
            if not b:
                continue
            if r <= lim:
                e2 = (e[0] + r, e[1], e[2]) if var == 0 else (e[0], e[1] + r, e[2])
                acc[e2] = acc.get(e2, 0) - a * b
            else:
                trunc += abs(a * b)
    normB = sum(abs(b) for b in B)
    return cdiv(trunc + normA * Brem + Arem * normB + Arem * Brem, ONEB)


# limit L -> (variable index, centre offset function, sign of the step)
def limit_frame(li, cert, fr):
    sc, tc, _ = fr.cen
    r0, r1, _ = fr.rad
    if li == 1:
        return 1, tc - cert.c, r1
    if li == 2:
        return 0, cert.k - sc, -r0
    if li == 3:
        return 1, tc - cert.k, r1
    return 0, cert.c - sc, -r0


def build_D(ps, case, cert, fr, N, P_tm=None):
    """Taylor model of D = P - K_e P (case A or B formula) on the frame."""
    if P_tm is None:
        P_tm = shift_to_tm(ps.st, fr, N)
    T, rem = P_tm
    acc = {e: v << WB for e, v in T.items()}
    for li in (1, 2, 3, 4):
        A = ps.alpha[case][li]
        B = ps.beta[case][li]
        if not A.c and not B.c:
            continue
        var, Lc, s = limit_frame(li, cert, fr)
        Phc, Phr, phc, phr = univ_Phi_phi(Lc, s, N)
        if A.c:
            a_tm, a_rem = shift_to_tm(A, fr, N)
            rem += mul_sub_acc(acc, a_tm, a_rem, Phc, Phr, var, N)
        if B.c:
            b_tm, b_rem = shift_to_tm(B, fr, N)
            rem += mul_sub_acc(acc, b_tm, b_rem, phc, phr, var, N)
    D = {}
    for e, v in acc.items():
        D[e] = (v + HALFB) >> WB
        rem += 1
    return D, rem


def tm_hi_bound(T, skip=None):
    """Lower bound of sum_{|a|>=2} c_a x^a over [-1, 1]^3 (non-positive int)."""
    s = 0
    for e, v in T.items():
        if e[0] + e[1] + e[2] >= 2 and (skip is None or e not in skip):
            if v < 0 or (e[0] & 1) or (e[1] & 1) or (e[2] & 1):
                s -= abs(v)
    return s


def lin_min(T, verts):
    c1 = T.get((1, 0, 0), 0)
    c2 = T.get((0, 1, 0), 0)
    c3 = T.get((0, 0, 1), 0)
    best = None
    for (x0, x1, x2) in verts:
        v = c1 * x0 + c2 * x1 + c3 * x2
        if best is None or v < best:
            best = v
    return math.floor(best)


def reduce_axis(T, kind):
    """On an axis cell the prism is 2-dimensional: for 'axp' (m = 0) x1 = x2 identically (tau - tau_c = t - t_c
    = e - e_box, r1 = r2 = w_e/2); for 'axm' (p = 0) x0 = -x2.  Substituting these identities is exact on the
    feasible set and removes large cancelling coefficients in the infeasible direction."""
    if kind == 'axp':
        out = {}
        for (i, j, l), v in T.items():
            e = (i, 0, j + l)
            out[e] = out.get(e, 0) + v
        return out
    if kind == 'axm':
        out = {}
        for (i, j, l), v in T.items():
            e = (0, j, i + l)
            out[e] = out.get(e, 0) + (-v if i & 1 else v)
        return out
    return T


def tm_lb(T, rem, verts, kind='tri'):
    T = reduce_axis(T, kind)
    return T.get((0, 0, 0), 0) + lin_min(T, verts) + tm_hi_bound(T) - rem


# ----------------------------------------------------------------------------------------------------------------------
# geometry of cells
def clip(poly, a, b, cst):
    """Keep {a p + b m <= cst} of a convex polygon (list of vertices; 1 or 2 vertices allowed)."""
    n = len(poly)
    if n == 0:
        return []
    if n == 1:
        P = poly[0]
        return poly if a * P[0] + b * P[1] <= cst else []
    out = []
    for idx in range(n):
        P = poly[idx]
        Q = poly[(idx + 1) % n]
        fP = a * P[0] + b * P[1] - cst
        fQ = a * Q[0] + b * Q[1] - cst
        if fP <= 0:
            out.append(P)
        if (fP < 0 < fQ) or (fQ < 0 < fP):
            t = fP / (fP - fQ)
            out.append((P[0] + t * (Q[0] - P[0]), P[1] + t * (Q[1] - P[1])))
    ded = []
    for v in out:
        if not ded or ded[-1] != v:
            ded.append(v)
    if len(ded) > 1 and ded[0] == ded[-1]:
        ded.pop()
    # remove duplicates globally (degenerate segments)
    seen = []
    for v in ded:
        if v not in seen:
            seen.append(v)
    return seen


def cell_polygon(cert, cell):
    kind, p0, p1, m0, m1 = cell[:5]
    if kind == 'tri':
        poly = [(p0, m0), (p1, m0), (p1, m1), (p0, m1)]
        return clip(poly, 1, 1, cert.S)
    if kind == 'axp':
        return [(p0, Fr(0)), (p1, Fr(0))] if p1 > p0 else [(p0, Fr(0))]
    return [(Fr(0), m0), (Fr(0), m1)] if m1 > m0 else [(Fr(0), m0)]


def make_frame(cert, cell):
    kind, p0, p1, m0, m1, e0, e1 = cell[:7]
    pc, mc, ec = (p0 + p1) / 2, (m0 + m1) / 2, (e0 + e1) / 2
    wp, wm, we = p1 - p0, m1 - m0, e1 - e0
    cen = (pc - ec, mc + ec, ec - cert.e_c)
    rad = ((wp + we) / 2, (wm + we) / 2, we / 2)
    return Frame(cen, rad)


def prism_verts(poly, e0, e1, fr, cert):
    sc, tc, ttc = fr.cen
    r0, r1, r2 = fr.rad
    out = []
    es = (e0,) if e0 == e1 else (e0, e1)
    for (p, m) in poly:
        for e in es:
            x0 = (p - e - sc) / r0 if r0 else Fr(0)
            x1 = (m + e - tc) / r1 if r1 else Fr(0)
            x2 = (e - cert.e_c - ttc) / r2 if r2 else Fr(0)
            out.append((x0, x1, x2))
    return out


# ----------------------------------------------------------------------------------------------------------------------
# weight kbar: e'-points
def kbar_points(cert, pmin, pmax, mmin, mmax, tol, maxpts=4096):
    """Points e'_j in Ew and delta with kbar(x) <= max_j k(x; e'_j) + delta for p in [pmin,pmax], m in [mmin,mmax].
    Returns (sorted points, delta) or None if the resolution limit is hit."""
    n, c = cert.i, cert.c
    if cert.w_lo == cert.w_hi:
        return [cert.w_lo], Fr(0)
    pts = set()
    delta = Fr(0)
    stack = [(cert.w_lo, cert.w_hi)]
    min_len = (cert.w_hi - cert.w_lo) / (1 << 16)
    while stack:
        a, b = stack.pop()
        uB = (c - pmax + a, c - pmin + b)
        uA = (mmin - c + a, mmax - c + b)
        gB = absHephi_bounds(n, *uB)
        gA = absHephi_bounds(n, *uA)
        if gB[0] > gA[1]:        # k increasing in e' on I for every x of the cell
            pts.add(b)
            continue
        if gB[1] < gA[0]:        # decreasing
            pts.add(a)
            continue
        M2 = absHephi_bounds(n + 1, *uB)[1] + absHephi_bounds(n + 1, *uA)[1]
        dI = (b - a) ** 2 / 8 * M2
        if dI <= tol:
            pts.add(a)
            pts.add(b)
            if dI > delta:
                delta = dI
            continue
        if b - a <= min_len or len(pts) + len(stack) > maxpts:
            return None
        mid = (a + b) / 2
        stack.append((a, mid))
        stack.append((mid, b))
    return sorted(pts), delta


def prune_points(cert, pts, pmin, pmax, mmin, mmax):
    n, c = cert.i, cert.c
    rng = []
    for e in pts:
        up = G_value(n, c - pmin + e)[1] - G_value(n, mmin - c + e)[0]
        lo = G_value(n, c - pmax + e)[0] - G_value(n, mmax - c + e)[1]
        rng.append((e, lo, up))
    best_lo = max(r[1] for r in rng)
    return [e for (e, lo, up) in rng if up >= best_lo]


def root_hits(n, ulo, uhi):
    return [q for q, (rl, rh) in enumerate(he_roots(n)) if rh > ulo and rl < uhi]


def G_tm(n, J, uc, var_a, a, var_b, b, N):
    """Taylor model (dict, rem) of G_J(uc + a x_{var_a} + b x_{var_b})."""
    g = G_taylor(n, J, uc, N)
    acc = {}
    for r in range(N + 1):
        glo, ghi = g[r]
        for l in range(r + 1):
            q = comb(r, l) * a ** l * b ** (r - l)
            if not q:
                continue
            lo, hi = iv_mul_q(glo, ghi, q)
            e = [0, 0, 0]
            e[var_a] += l
            e[var_b] += r - l
            e = tuple(e)
            o = acc.get(e)
            acc[e] = (lo, hi) if o is None else (o[0] + lo, o[1] + hi)
    T = {}
    rem = 0
    for e, (lo, hi) in acc.items():
        m, r = fx_to_tmcoef(lo, hi)
        T[e] = m
        rem += r + 1
    smax = abs(a) + abs(b)
    if smax:
        nn = n + N if n >= 1 else N
        bound = absHephi_bounds(nn, uc - smax, uc + smax)[1] * smax ** (N + 1) / factorial(N + 1)
        rem += ce(bound, WB) + 1
    return T, rem


# ----------------------------------------------------------------------------------------------------------------------
# cell checks
class Ctx:
    pass


CTX = None          # set in the parent before forking workers


def split_cases(cert, poly):
    out = []
    A = clip(poly, -1, -1, -2 * cert.k)
    if A:
        out.append(('A', A))
    B = clip(poly, 1, 1, 2 * cert.k)
    if B:
        out.append(('B', B))
    return out


def bbox(poly):
    ps = [v[0] for v in poly]
    ms = [v[1] for v in poly]
    return min(ps), max(ps), min(ms), max(ms)


TOL0 = Fr(1, 1 << 12)      # first weight-grid tolerance; refined (below) only when delta decides the cell


def check_cell(kind, cell, N):
    """Certified lower bound (Fraction) of the claimed quantity over the cell, or (lb, reason).
    Returns (ok: bool, lb: Fraction, info: str)."""
    ctx = CTX
    cert = ctx.cert
    poly = cell_polygon(cert, cell)
    if not poly:
        return True, None, 'empty'
    e0, e1 = cell[5], cell[6]
    fr = make_frame(cert, cell)
    ps = ctx.W if kind in ('C1', 'C2') else ctx.V
    P_tm = shift_to_tm(ps.st, fr, N)
    if kind == 'C1':
        verts = prism_verts(poly, e0, e1, fr, cert)
        lb = tm_lb(P_tm[0], P_tm[1], verts, cell[0])
        return lb >= 0, Fr(lb, ONEB), ''
    cases = split_cases(cert, poly)
    Ds = []
    for case, cpoly in cases:
        D, rem = build_D(ps, case, cert, fr, N, P_tm)
        Ds.append((case, cpoly, D, rem))
    if kind == 'C2':
        worst = None
        for case, cpoly, D, rem in Ds:
            D = dict(D)
            D[(0, 0, 0)] = D.get((0, 0, 0), 0) - ONEB
            lb = tm_lb(D, rem, prism_verts(cpoly, e0, e1, fr, cert), cell[0])
            worst = lb if worst is None or lb < worst else worst
        return worst >= 0, Fr(worst, ONEB), ''
    # (C3)
    pmin, pmax, mmin, mmax = bbox(poly)
    tol = TOL0
    info = ''
    lb = None
    for attempt in range(6):
        res = kbar_points(cert, pmin, pmax, mmin, mmax, tol)
        if res is None:
            return False, None if lb is None else Fr(lb, ONEB), 'kbar-resolution'
        pts, delta = res
        pts = prune_points(cert, pts, pmin, pmax, mmin, mmax)
        worst = c3_lower_bound(cert, fr, Ds, pts, e0, e1, N, cell[0])
        if worst is None:
            return False, None, 'multi-root'
        dfx = ce(delta, WB)
        lb = worst - dfx
        info = 'pts=%d delta=%.2e' % (len(pts), float(delta))
        if lb >= 0:
            return True, Fr(lb, ONEB), info
        if worst > 0 and delta > 0:
            tol = min(tol / 16, Fr(worst, ONEB) / 4)
            continue
        return False, Fr(lb, ONEB), info
    return False, Fr(lb, ONEB), info


def c3_lower_bound(cert, fr, Ds, pts, e0, e1, N, kind='tri'):
    n, c = cert.i, cert.c
    r0, r1, r2 = fr.rad
    pc = fr.cen[0] + fr.cen[2] + cert.e_c           # p_c = sigma_c + e_box_c
    mc = fr.cen[1] - fr.cen[2] - cert.e_c           # m_c = tau_c - e_box_c
    worst = None
    roots = he_roots(n)
    errs = g_structure(n)[3] if n >= 1 else ()
    for case, cpoly, D, rem in Ds:
        pmin, pmax, mmin, mmax = bbox(cpoly)
        for ej in pts:
            uB = (c - pmax + ej, c - pmin + ej)
            uA = (mmin - c + ej, mmax - c + ej)
            hB = root_hits(n, *uB) if n >= 1 else []
            hA = root_hits(n, *uA) if n >= 1 else []
            if len(hB) > 1 or len(hA) > 1:
                return None
            # options: (clip constraint (a, b, cst) or None, piece J, err)
            if not hB:
                JB = sum(1 for (rl, rh) in roots if rh <= uB[0])
                optB = [(None, JB, 0)]
            else:
                q = hB[0]
                rl, rh = roots[q]
                # u_B <= rh  <=>  p >= c + ej - rh   : G <= G_q + err_q
                # u_B >= rl  <=>  p <= c + ej - rl   : G <= G_{q+1}
                optB = [((-1, 0, -(c + ej - rh)), q, errs[q]), ((1, 0, c + ej - rl), q + 1, 0)]
            if not hA:
                JA = sum(1 for (rl, rh) in roots if rh <= uA[0])
                optA = [(None, JA, 0)]
            else:
                q = hA[0]
                rl, rh = roots[q]
                # u_A <= rh <=> m <= rh + c - ej : G >= G_q
                # u_A >= rl <=> m >= rl + c - ej : G >= G_{q+1} - err_q
                optA = [((0, 1, rh + c - ej), q, 0), ((0, -1, -(rl + c - ej)), q + 1, errs[q])]
            for (cB, JB, errB) in optB:
                polyB = cpoly if cB is None else clip(cpoly, *cB)
                if not polyB:
                    continue
                GB, GBr = G_tm(n, JB, c - pc + ej, 0, -r0, 2, -r2, N)
                for (cA, JA, errA) in optA:
                    pol = polyB if cA is None else clip(polyB, *cA)
                    if not pol:
                        continue
                    GA, GAr = G_tm(n, JA, mc - c + ej, 1, r1, 2, -r2, N)
                    T = dict(D)
                    for e, v in GB.items():
                        T[e] = T.get(e, 0) - v
                    for e, v in GA.items():
                        T[e] = T.get(e, 0) + v
                    lb = tm_lb(T, rem + GBr + GAr + errB + errA, prism_verts(pol, e0, e1, fr, cert), kind)
                    if worst is None or lb < worst:
                        worst = lb
    return worst


# ----------------------------------------------------------------------------------------------------------------------
# point evaluation (for disproof)
def point_upper(kind, p, m, e):
    """Rigorous UPPER bound (Fraction) of the claimed quantity at the point (p, m, e)."""
    ctx = CTX
    cert = ctx.cert
    cell = ('pt', p, p, m, m, e, e)
    fr = make_frame(cert, cell)
    ps = ctx.W if kind in ('C1', 'C2') else ctx.V
    if kind == 'C1':
        return ps.eval_raw(p, m, e - cert.e_c)
    case = 'A' if p + m >= 2 * cert.k else 'B'
    D, rem = build_D(ps, case, cert, fr, 0)
    up = Fr(D.get((0, 0, 0), 0) + rem, ONEB)
    if kind == 'C2':
        return up - 1
    n, c = cert.i, cert.c
    best = None
    k = 16
    for j in range(k + 1):
        ep = cert.w_lo + (cert.w_hi - cert.w_lo) * j / k
        lo = G_value(n, c - p + ep)[0] - G_value(n, m - c + ep)[1]
        if best is None or lo > best:
            best = lo
    return up - Fr(best, 1 << WX)


# ----------------------------------------------------------------------------------------------------------------------
# driver
def split_cell(cert, cell):
    kind, p0, p1, m0, m1, e0, e1, depth = cell
    wp, wm, we = p1 - p0, m1 - m0, e1 - e0
    # e is weighted x2 against space (a cell's frame radius r0 = (wp + we)/2 already contains we)
    if we >= max(wp, wm) and we > 0:
        em = (e0 + e1) / 2
        return [(kind, p0, p1, m0, m1, e0, em, depth + 1), (kind, p0, p1, m0, m1, em, e1, depth + 1)]
    if wp >= wm:
        pm = (p0 + p1) / 2
        return [(kind, p0, pm, m0, m1, e0, e1, depth + 1), (kind, pm, p1, m0, m1, e0, e1, depth + 1)]
    mm = (m0 + m1) / 2
    return [(kind, p0, p1, m0, mm, e0, e1, depth + 1), (kind, p0, p1, mm, m1, e0, e1, depth + 1)]


def initial_cells(cert, width=Fr(1, 4)):
    S, h = cert.S, cert.h
    cells = []
    n = max(1, math.ceil(S / width)) if S > 0 else 0
    for i in range(n):
        for j in range(n):
            p0, p1 = S * i / n, S * (i + 1) / n
            m0, m1 = S * j / n, S * (j + 1) / n
            if p0 + m0 < S:
                cells.append(('tri', p0, p1, m0, m1, cert.e_lo, cert.e_hi, 0))
    if S == 0:
        cells.append(('tri', Fr(0), Fr(0), Fr(0), Fr(0), cert.e_lo, cert.e_hi, 0))
    na = max(1, math.ceil((h - S) / width))
    for i in range(na):
        a0, a1 = S + (h - S) * i / na, S + (h - S) * (i + 1) / na
        cells.append(('axp', a0, a1, Fr(0), Fr(0), cert.e_lo, cert.e_hi, 0))
        cells.append(('axm', Fr(0), Fr(0), a0, a1, cert.e_lo, cert.e_hi, 0))
    return cells


def fmt_cell(cell):
    kind, p0, p1, m0, m1, e0, e1, depth = cell
    return ('%s p=[%s,%s] m=[%s,%s] e=[%s,%s] depth=%d'
            % (kind, p0, p1, m0, m1, e0, e1, depth))


def run_subtree(args):
    """Worker: verify one initial cell for one claim kind by adaptive bisection."""
    kind, cell, N, max_depth = args
    t0 = time.time()
    stack = [cell]
    nboxes = 0
    maxd = 0
    minlb = None
    while stack:
        cl = stack.pop()
        try:
            ok, lb, info = check_cell(kind, cl, N)
        except Exception as exc:                       # never accept on an internal error
            return {'kind': kind, 'ok': False, 'reason': 'internal error: %r' % (exc,), 'cell': fmt_cell(cl),
                    'boxes': nboxes, 'maxdepth': maxd, 'sec': time.time() - t0}
        if ok:
            nboxes += 1
            maxd = max(maxd, cl[7])
            if lb is not None and (minlb is None or lb < minlb):
                minlb = lb
            continue
        # failure: try a disproof at the cell centre
        poly = cell_polygon(CTX.cert, cl)
        if cl[7] >= 2 or cl[7] >= max_depth:
            pc = sum(v[0] for v in poly) / len(poly)
            mc = sum(v[1] for v in poly) / len(poly)
            ec = (cl[5] + cl[6]) / 2
            cands = [(pc, mc, ec)]
            if cl[7] >= max_depth:                   # last chance: also the vertices x e-endpoints
                cands += [(v[0], v[1], e) for v in poly for e in (cl[5], cl[6])]
            for (px, mx, ex) in cands:
                up = point_upper(kind, px, mx, ex)
                if up < 0:
                    return {'kind': kind, 'ok': False, 'false': True,
                            'reason': '%s is FALSE at (p, m, e) = (%s, %s, %s): certified upper bound %.6e < 0'
                                      % (kind, px, mx, ex, float(up)),
                            'cell': fmt_cell(cl), 'boxes': nboxes, 'maxdepth': max(maxd, cl[7]),
                            'sec': time.time() - t0}
        if cl[7] >= max_depth:
            return {'kind': kind, 'ok': False, 'false': False,
                    'reason': '%s UNPROVEN at depth limit: certified lower bound %s (%s)'
                              % (kind, 'n/a' if lb is None else '%.6e' % float(lb), info),
                    'cell': fmt_cell(cl), 'boxes': nboxes, 'maxdepth': cl[7], 'sec': time.time() - t0}
        stack.extend(split_cell(CTX.cert, cl))
    return {'kind': kind, 'ok': True, 'boxes': nboxes, 'maxdepth': maxd,
            'minlb': None if minlb is None else float(minlb), 'sec': time.time() - t0}


def prepare(cert):
    ctx = Ctx()
    ctx.cert = cert
    ctx.V = PolySet(cert.V0, cert.V1, cert.h, cert.k, cert.e_c, cert.taboo)
    ctx.W = PolySet(cert.W0, cert.W1, cert.h, cert.k, cert.e_c, cert.taboo)
    return ctx


def verify_cert(raw, file_kernel=None, N=8, max_depth=24, procs=1, kinds=('C4', 'C1', 'C2', 'C3'),
                log=None, stop_on_fail=True):
    """Verify one raw certificate object.  Returns a result dict with 'verdict' in ACCEPT/REJECT/REFUSE."""
    global CTX
    t0 = time.time()
    res = {'verdict': None}

    def say(s):
        if log:
            log(s)
    try:
        cert = Cert(raw, file_kernel)
    except CertError as exc:
        res.update(verdict='REFUSE', reason='malformed: %s' % exc, sec=time.time() - t0)
        return res
    res['describe'] = cert.describe()
    if cert.quarantined:
        res.update(verdict='REFUSE', reason='quarantine: block/weight block meets the excluded band for h=5, k=1/2; '
                   'nothing evaluated', sec=time.time() - t0)
        return res
    if not cert.sha_ok:
        res.update(verdict='REJECT', reason='sha256 mismatch', sec=time.time() - t0)
        return res
    # (C4)
    v_lo = cert.V0.get((0, 0), 0) + (cert.e_lo - cert.e_c) * cert.V1.get((0, 0), 0)
    v_hi = cert.V0.get((0, 0), 0) + (cert.e_hi - cert.e_c) * cert.V1.get((0, 0), 0)
    res['C4'] = {'ok': cert.Gamma >= max(v_lo, v_hi), 'Gamma': str(cert.Gamma), 'max_V_at_atom': str(max(v_lo, v_hi))}
    if 'C4' in kinds and not res['C4']['ok']:
        res.update(verdict='REJECT', reason='(C4) fails: Gamma < max(V_elo(a), V_ehi(a))', false=True,
                   sec=time.time() - t0)
        return res
    CTX = prepare(cert)
    cells = initial_cells(cert)
    tasks = [(k, cl, N, max_depth) for k in ('C1', 'C2', 'C3') if k in kinds for cl in cells]
    say('  %s: %d initial cells x %d claims, N=%d, max_depth=%d'
        % (cert.describe(), len(cells), len([k for k in ('C1', 'C2', 'C3') if k in kinds]), N, max_depth))
    stats = {k: {'boxes': 0, 'maxdepth': 0, 'sec': 0.0, 'minlb': None} for k in ('C1', 'C2', 'C3') if k in kinds}
    failure = None
    completed = 0
    if procs > 1:
        ctxm = mp.get_context('fork')
        with ctxm.Pool(procs) as pool:
            for out in pool.imap_unordered(run_subtree, tasks):
                completed += 1
                st = stats[out['kind']]
                st['boxes'] += out['boxes']
                st['maxdepth'] = max(st['maxdepth'], out['maxdepth'])
                st['sec'] += out['sec']
                if out.get('minlb') is not None:
                    st['minlb'] = out['minlb'] if st['minlb'] is None else min(st['minlb'], out['minlb'])
                if not out['ok']:
                    if failure is None or (out.get('false') and not failure.get('false')):
                        failure = out
                    if stop_on_fail:
                        pool.terminate()
                        break
    else:
        for tk in tasks:
            out = run_subtree(tk)
            completed += 1
            st = stats[out['kind']]
            st['boxes'] += out['boxes']
            st['maxdepth'] = max(st['maxdepth'], out['maxdepth'])
            st['sec'] += out['sec']
            if out.get('minlb') is not None:
                st['minlb'] = out['minlb'] if st['minlb'] is None else min(st['minlb'], out['minlb'])
            if not out['ok']:
                failure = out
                if stop_on_fail:
                    break
    res['claims'] = stats
    res['boxes'] = sum(s['boxes'] for s in stats.values())
    res['maxdepth'] = max([s['maxdepth'] for s in stats.values()] or [0])
    if failure is not None:
        res.update(verdict='REJECT', reason=failure['reason'], cell=failure.get('cell'),
                   false=bool(failure.get('false')))
    elif completed != len(tasks):
        res.update(verdict='REJECT', reason='internal: only %d of %d cover tasks completed' % (completed, len(tasks)))
    else:
        res.update(verdict='ACCEPT', reason='(C1)-(C4) and sha256 proved')
    res['sec'] = time.time() - t0
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description='Independent SRK_CERT/1 verifier')
    ap.add_argument('cert')
    ap.add_argument('--index', default=None)
    ap.add_argument('--max-depth', type=int, default=24)
    ap.add_argument('--order', type=int, default=8, help='Taylor model order N')
    ap.add_argument('--procs', type=int, default=1, help='worker processes (default 1)')
    ap.add_argument('--json', default=None, help='write the result list to this file')
    a = ap.parse_args(argv)
    try:
        items = load_certs(a.cert)
    except (CertError, ValueError, OSError) as exc:
        print('REFUSE %s: %s' % (a.cert, exc))
        return 2
    if a.index is not None:
        items = [it for it in items if it[0] == str(a.index)]
        if not items:
            print('REFUSE: no certificate with index %s' % a.index)
            return 2
    results = []
    allok = True
    for label, raw, fk in items:
        print('[%s] index %s' % (os.path.basename(a.cert), label), flush=True)
        r = verify_cert(raw, fk, N=a.order, max_depth=a.max_depth, procs=a.procs,
                        log=lambda s: print(s, flush=True))
        r['index'] = label
        results.append(r)
        line = '  %s  (%s)  boxes=%s maxdepth=%s  %.1fs' % (r['verdict'], r.get('reason'), r.get('boxes'),
                                                          r.get('maxdepth'), r['sec'])
        if r['verdict'] != 'ACCEPT':
            allok = False
            if r.get('cell'):
                line += '\n  failing cell: %s' % r['cell']
        print(line, flush=True)
    if a.json:
        with open(a.json, 'w') as f:
            json.dump(results, f, indent=1, default=str)
    return 0 if allok else 1


if __name__ == '__main__':
    sys.exit(main())
