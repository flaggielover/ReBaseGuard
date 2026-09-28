"""Stream D format adapter: stored certificate -> the verifier's own StripPW representation.

C1b data layout (learned from the ORIGINAL code for layout only; no algorithm is used):
  * a candidate is a list ws = [P_1, ..., P_S] of polynomials, P_s = {(i, j, k): Fraction} = sum c p^i m^j e^k;
    point certificates have k = 0 only (c1b_kernel.py lines 31-34 and 38-80: keys (p, m, e) exponents, peval);
  * strip s is [BW[s-1], BW[s]] of t = p + m (right-closed; strip 1 closed); the value at x in x-region
    J = ceil(t) (J = 1 for t = 0) uses the strip containing [J-1, J] (c1b_pw.py lines 1-13, 45-49, 97-112);
    for integer BW this is exactly "the right-closed strip of t", which is the StripPW semantics (asserted below);
  * the certified whole-kernel supersolution is W = (1 + eta_W) * rec['_c']['W'] (c1b_certpw.py lines 193, 206-207:
    W = wscale(c["W"], 1 + etaW); record keys at lines 279, 298) and A_bar = W on strip 1 at (0, 0, 0)
    (lines 119-120, 211).
This module imports nothing from any certifier.
"""
from __future__ import annotations

from fractions import Fraction as F


def c1b_raw_from_record_polys(ws: list) -> list:
    """C1b in-memory strip list [{(i,j,k): F}] -> JSON-able [[i, j, k, 'n/d'], ...] per strip (exact)."""
    out = []
    for P in ws:
        mons = []
        for (i, j, k), v in sorted(P.items()):
            v = F(v)
            if v:
                mons.append([int(i), int(j), int(k), f"{v.numerator}/{v.denominator}"])
        out.append(mons)
    return out


def from_c1b_raw(raw: dict):
    """raw = {'BW': [...], 'W_unscaled': [[[i,j,k,'n/d'], ...] per strip], 'eta_W': 'n/d'}  ->  StripPW."""
    from vd_verify import StripPW
    BW = [F(b) for b in raw["BW"]]
    if any(b.denominator != 1 for b in BW):
        raise ValueError("C1b region semantics equal right-closed strips only for integer BW")
    eta = F(raw["eta_W"])
    polys = []
    for mons in raw["W_unscaled"]:
        P = {}
        for i, j, k, c in mons:
            if int(k) != 0:
                raise ValueError("e-dependent monomial in a point certificate")
            v = F(c) * (1 + eta)
            if v:
                P[(int(i), int(j))] = P.get((int(i), int(j)), F(0)) + v
        polys.append(P)
    return StripPW(BW, polys, {"source": "C1b certify_degree record, W = (1 + eta_W) * _c['W']"})
