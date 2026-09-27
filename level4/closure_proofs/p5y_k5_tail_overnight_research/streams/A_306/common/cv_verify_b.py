"""Verifier V_B for Theorem CV certificates -- DECIMAL DIRECTED-ROUNDING path (stdlib `decimal` only).

Independence from V_A (cv_verify_a.py): no shared code and no shared numerical primitive.
  * arithmetic   base-10 floating point at 90 digits with explicit ROUND_FLOOR / ROUND_CEILING per operation
                 (V_A: exact binary rationals with 2^-320 outward rounding);
  * Gaussian     Phi(y) = 1/2 + phi(y) * sum_n y^(2n+1)/(2n+1)!!  (all-positive series, geometric tail bound),
                 phi via decimal exp (correctly rounded, half-even, widened by 2 ulps), pi by Machin in decimal with
                 alternating-series error terms  (V_A: C7's alternating erf series and binary Machin);
  * polynomials  interval Horner in m then in p  (V_A: monotone monomial bounds);
  * the box/panel sufficient condition is the SAME mathematical statement (THEOREM_CV.md section 3), coded again
    from the specification.  A mathematical error in that shared specification would be common-mode (disclosed).
Its only non-stdlib import is ov_quarantine (the campaign's guard).
"""
from __future__ import annotations

import decimal
import sys
from decimal import Decimal as D, ROUND_CEILING, ROUND_FLOOR
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parents[2]
sys.path.insert(0, str(NS / "code"))
import ov_quarantine as Q  # noqa: E402

Q.install_import_guard()

PREC = 90
CTX_DN = decimal.Context(prec=PREC, rounding=ROUND_FLOOR)
CTX_UP = decimal.Context(prec=PREC, rounding=ROUND_CEILING)


def q2d(x: Fr) -> tuple:
    x = Fr(x)
    return CTX_DN.divide(D(x.numerator), D(x.denominator)), CTX_UP.divide(D(x.numerator), D(x.denominator))


def i_add(x, y):
    return CTX_DN.add(x[0], y[0]), CTX_UP.add(x[1], y[1])


def i_sub(x, y):
    return CTX_DN.subtract(x[0], y[1]), CTX_UP.subtract(x[1], y[0])


def i_mul(x, y):
    c = [(x[i], y[j]) for i in (0, 1) for j in (0, 1)]
    return min(CTX_DN.multiply(a, b) for a, b in c), max(CTX_UP.multiply(a, b) for a, b in c)


def _widen(v: D, k: int = 2) -> tuple:
    lo = hi = v
    for _ in range(k):
        lo, hi = CTX_DN.next_minus(lo), CTX_UP.next_plus(hi)
    return lo, hi


def _atan_inv(n: int) -> tuple:
    """arctan(1/n), n >= 2, alternating series with the first omitted term as error."""
    x = (CTX_DN.divide(D(1), D(n)), CTX_UP.divide(D(1), D(n)))
    lo = hi = D(0)
    k, sign = 0, 1
    p = x
    while True:
        t = (CTX_DN.divide(p[0], D(2 * k + 1)), CTX_UP.divide(p[1], D(2 * k + 1)))
        if t[1] < D(10) ** (-(PREC + 5)):
            return CTX_DN.subtract(lo, t[1]), CTX_UP.add(hi, t[1])
        if sign > 0:
            lo, hi = CTX_DN.add(lo, t[0]), CTX_UP.add(hi, t[1])
        else:
            lo, hi = CTX_DN.subtract(lo, t[1]), CTX_UP.subtract(hi, t[0])
        p = i_mul(p, i_mul(x, x))
        sign, k = -sign, k + 1


def _sqrt_2pi() -> tuple:
    a5, a239 = _atan_inv(5), _atan_inv(239)
    pi = i_sub(i_mul((D(16), D(16)), a5), i_mul((D(4), D(4)), a239))
    two_pi = i_mul((D(2), D(2)), pi)
    return _widen(CTX_DN.sqrt(two_pi[0]))[0], _widen(CTX_UP.sqrt(two_pi[1]))[1]


S2PI = _sqrt_2pi()


def phi_pt(y: D) -> tuple:
    """phi at a decimal point y."""
    y2 = (CTX_DN.multiply(y, y), CTX_UP.multiply(y, y))
    half = (CTX_DN.divide(y2[0], D(2)), CTX_UP.divide(y2[1], D(2)))
    # exp(-half) is decreasing in half: lower from half.hi, upper from half.lo
    e_lo = _widen(decimal.Context(prec=PREC).exp(-half[1]))[0]
    e_hi = _widen(decimal.Context(prec=PREC).exp(-half[0]))[1]
    return CTX_DN.divide(e_lo, S2PI[1]), CTX_UP.divide(e_hi, S2PI[0])


def _series(y: D) -> tuple:
    """S(y) = sum_n y^(2n+1)/(2n+1)!! for y >= 0, with a geometric tail bound."""
    if y == 0:
        return D(0), D(0)
    y2 = (CTX_DN.multiply(y, y), CTX_UP.multiply(y, y))
    t = (y, y)
    s = (D(0), D(0))
    n = 0
    while True:
        s = (CTX_DN.add(s[0], t[0]), CTX_UP.add(s[1], t[1]))
        nxt = (CTX_DN.divide(CTX_DN.multiply(t[0], y2[0]), D(2 * n + 3)),
               CTX_UP.divide(CTX_UP.multiply(t[1], y2[1]), D(2 * n + 3)))
        n += 1
        r = CTX_UP.divide(y2[1], D(2 * n + 3))            # bound on every later term ratio
        if r < D("0.5") and nxt[1] < D(10) ** (-(PREC - 8)) * s[0]:
            tail = CTX_UP.divide(nxt[1], CTX_DN.subtract(D(1), r))
            return s[0], CTX_UP.add(s[1], tail)
        t = nxt
        if n > 20000:
            raise RuntimeError("series did not converge")


def Phi_pt(y: D) -> tuple:
    if y < 0:
        lo, hi = Phi_pt(-y)
        return CTX_DN.subtract(D(1), hi), CTX_UP.subtract(D(1), lo)
    if y > 38:
        raise RuntimeError("argument outside the verified range")
    ph = phi_pt(y)
    S = _series(y)
    return CTX_DN.add(D("0.5"), CTX_DN.multiply(ph[0], S[0])), CTX_UP.add(D("0.5"), CTX_UP.multiply(ph[1], S[1]))


_PHI_CACHE: dict = {}


def Phi_q(x: Fr) -> tuple:
    """Phi at an exact rational x: monotone, so [Phi_lo(x_dn), Phi_hi(x_up)]."""
    r = _PHI_CACHE.get(x)
    if r is None:
        xl, xh = q2d(x)
        r = (Phi_pt(xl)[0], Phi_pt(xh)[1])
        _PHI_CACHE[x] = r
    return r


def gmass(u0: Fr, u1: Fr) -> tuple:
    a, b = Phi_q(u0), Phi_q(u1)
    lo = CTX_DN.subtract(b[0], a[1])
    return (lo if lo > 0 else D(0)), CTX_UP.subtract(b[1], a[0])


# --------------------------------------------------------------------------------------- polynomial, Horner
def poly_rows(cert: dict) -> dict:
    """{i: {j: Fraction}} from the certificate's weight."""
    rows: dict = {}
    for k, v in cert["weight"].items():
        i, j = (int(t) for t in k.split(","))
        rows.setdefault(i, {})[j] = Fr(v)
    return rows


def horner_iv(rows: dict, P: tuple, M: tuple) -> tuple:
    """Interval Horner: sum_i p^i (sum_j c_ij m^j) over decimal intervals P, M."""
    def horner(coeffs: dict, X: tuple) -> tuple:
        deg = max(coeffs)
        acc = q2d(coeffs.get(deg, Fr(0)))
        for k in range(deg - 1, -1, -1):
            acc = i_add(i_mul(acc, X), q2d(coeffs.get(k, Fr(0))))
        return acc
    inner = {i: horner(r, M) for i, r in rows.items()}
    deg = max(inner)
    acc = inner.get(deg, (D(0), D(0)))
    for i in range(deg - 1, -1, -1):
        acc = i_add(i_mul(acc, P), inner.get(i, (D(0), D(0))))
    return acc


# --------------------------------------------------------------------------------------- box/panel condition
KQ, HQ = Fr(1, 2), Fr(5)
CQ = KQ + HQ
KINDS = {"ARL_SUPER": ("K", "1", +1), "TABOO_SUPER": ("Khat", "1", +1), "D_SUPER": ("Khat", "h1", +1),
         "ARL_SUB": ("K", "1", -1), "TABOO_SUB": ("Khat", "1", -1), "D_SUB": ("Khat", "h1", -1)}


def boxes(depth: int) -> list:
    n = 2 ** depth
    s = HQ / n
    out = []
    for i in range(n):
        for j in range(n):
            a, c = s * i, s * j
            if a + c <= 4 or a == 0 or c == 0:
                out.append((a, a + s, c, c + s))
    return out


def _img(a, b, c, d, zl, zh):
    z = Fr(0)
    return ((max(z, a + zl - KQ), max(z, b + zh - KQ)), (max(z, c - zh - KQ), max(z, d - zl - KQ)))


def verify(cert: dict) -> dict:
    kind = cert["kind"]
    if kind not in KINDS:
        return {"accepted": False, "reasons": ["unknown kind"]}
    kern, src, sgn = KINDS[kind]
    elo, ehi = Fr(cert["drift_block"][0]), Fr(cert["drift_block"][1])
    Q.guard_drift(elo, ehi)
    depth, npan = int(cert["hints"]["depth"]), int(cert["hints"]["panels"])
    rows = poly_rows(cert)
    worst, fmin, hmin, fsup = None, None, None, None
    for (a, b, c, d) in boxes(depth):
        fbox = horner_iv(rows, q2d(a)[:1] + q2d(b)[1:], q2d(c)[:1] + q2d(d)[1:])
        fmin = fbox[0] if fmin is None else min(fmin, fbox[0])
        fsup = fbox[1] if fsup is None else max(fsup, fbox[1])
        # h1 bounds: 1 - Phi(C - p + e) + Phi(m - C + e)
        h_lo = CTX_DN.add(CTX_DN.subtract(D(1), Phi_q(CQ - a + ehi)[1]), Phi_q(c - CQ + elo)[0])
        h_hi = CTX_UP.add(CTX_UP.subtract(D(1), Phi_q(CQ - b + elo)[0]), Phi_q(d - CQ + ehi)[1])
        if sgn > 0:
            u_start, u_end = c - CQ + elo, CQ - a + ehi
            acc = D(0)
            step = (u_end - u_start) / npan
            for k in range(npan):
                u0, u1 = u_start + k * step, u_start + (k + 1) * step
                zl, zh = u0 - ehi, u1 - elo
                if kern == "Khat" and (d - KQ) < (KQ - b) and zl >= d - KQ and zh <= KQ - b:
                    continue
                (P, M) = _img(a, b, c, d, zl, zh)
                fi = horner_iv(rows, q2d(P[0])[:1] + q2d(P[1])[1:], q2d(M[0])[:1] + q2d(M[1])[1:])
                if fi[1] > 0:
                    acc = CTX_UP.add(acc, CTX_UP.multiply(fi[1], gmass(u0, u1)[1]))
            s_hi = h_hi if src == "h1" else D(1)
            margin = CTX_DN.subtract(CTX_DN.subtract(fbox[0], s_hi), acc)
        else:
            hmin = h_lo if hmin is None else min(hmin, h_lo)
            u_start, u_end = d - CQ + ehi, CQ - b + elo
            acc = D(0)
            if u_end > u_start:
                step = (u_end - u_start) / npan
                for k in range(npan):
                    u0, u1 = u_start + k * step, u_start + (k + 1) * step
                    zl, zh = u0 - ehi, u1 - elo
                    if kern == "Khat" and (c - KQ) < (KQ - a) and zl < KQ - a and zh > c - KQ:
                        continue
                    (P, M) = _img(a, b, c, d, zl, zh)
                    fi = horner_iv(rows, q2d(P[0])[:1] + q2d(P[1])[1:], q2d(M[0])[:1] + q2d(M[1])[1:])
                    ms = gmass(u0, u1)
                    acc = CTX_DN.add(acc, CTX_DN.multiply(fi[0], ms[0] if fi[0] >= 0 else ms[1]))
            s_lo = h_lo if src == "h1" else D(1)
            margin = CTX_DN.subtract(CTX_DN.add(s_lo, acc), fbox[1])
        worst = margin if worst is None else min(worst, margin)
    reasons = []
    if worst < 0:
        reasons.append("box inequality fails")
    if fmin < 0:
        reasons.append("nonnegativity on R not established")
    if sgn < 0 and not (hmin > 0):
        reasons.append("h_min > 0 not established")
    val = rows.get(0, {}).get(0, Fr(0))                 # f(0, 0) is the constant coefficient
    cl = cert.get("claims", {})
    if "value_at_atom" not in cl or Fr(cl["value_at_atom"]) != val:
        reasons.append("claimed value_at_atom is not f(0,0)")
    out = {"verifier": "V_B (decimal, directed rounding)", "kind": kind, "margin_lower_bound": float(worst),
           "f_min_lower_bound": float(fmin), "value_at_atom": str(val), "boxes": len(boxes(depth))}
    if sgn < 0:
        out["h_min_lower_bound"] = float(hmin)
    if kind == "TABOO_SUPER":
        out["C_T_upper_bound"] = str(fsup)
        if "C_T_upper" not in cl or q2d(Fr(cl["C_T_upper"]))[0] < fsup:
            reasons.append("claimed C_T_upper is below the verifier's sup bound")
    if kind == "TABOO_SUB":
        n = 2 ** depth
        s = HQ / n
        pts = [(s * i, s * j) for i in range(n + 1) for j in range(n + 1)
               if (s * i + s * j <= 4) or i == 0 or j == 0]
        pm = max(sum((cf * p ** i * m ** j for i, r in rows.items() for j, cf in r.items()), Fr(0)) for p, m in pts)
        out["C_T_lower_bound"] = str(pm)
        if "C_T_lower" not in cl or Fr(cl["C_T_lower"]) > pm:
            reasons.append("claimed C_T_lower exceeds the verifier's point maximum on R")
    out["reasons"] = reasons
    out["accepted"] = not reasons
    return out
