"""Verifier V_A for Theorem CV certificates -- EXACT RATIONAL path (fractions + C7 rigorous Gaussian enclosures).

Independence: this module shares no code with cv_verify_b.py (the decimal path).  Its only import beyond the
standard library is C7's `c7_gaussian` (a pure library: imports only `fractions`, no side effects; read before
use), which supplies Phi/phi enclosures with proved series remainders and 2^-320 outward rounding.

Certificate (schema A306_CV_CERT/1, see THEOREM_CV.md section 5; sufficient condition section 4):
    kind          ARL_SUPER | TABOO_SUPER | D_SUPER | ARL_SUB | TABOO_SUB | D_SUB
    drift_block   [e_lo, e_hi]  exact rationals (a point block is allowed)
    weight        {"i,j": "rational"}  meaning f(p, m) = sum c p^i m^j
    claims        {"value_at_atom": "r"} and, for TABOO_SUPER, "C_T_upper"; for TABOO_SUB, "C_T_lower"
    hints         {"depth": int, "panels": int}   (a verifier may use any sound discretisation; these are defaults)

Sufficient condition checked (box/panel, Theorem CV section 3):
    for every box B of the depth-d dyadic cover of R and every e in the block:
      SUPER:  f_lo(B) - src_hi(B) - U(B) >= 0   with U an upper bound of (K f) or (Khat f) over B x block
      SUB:    src_lo(B) + L(B) - f_hi(B) >= 0   with L a lower bound of (K f) or (Khat f) over B x block
    and f_lo(B) >= 0 on every box (f >= 0 on R); for SUB kinds also h_min = min_B h1_lo(B) > 0.
Values are recomputed exactly from the weight; claims must match (value_at_atom exactly; C_T_upper >= the verifier's
own sup bound; C_T_lower <= the verifier's own exact point maximum on R).
"""
from __future__ import annotations

import functools
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parents[2]
sys.path.insert(0, str(NS / "code"))
import ov_quarantine as Q  # noqa: E402

Q.install_import_guard()
sys.path.insert(0, str(NS.parent / "p5y_k5_tail_c7_e2_lambda309/code"))
import c7_gaussian as G  # noqa: E402

# sqrt(2 pi) is a pure constant that c7_gaussian.Phi recomputes on every call (a 400-term exact Machin series).
# Memoising the zero-argument pure function cannot change any bit (checked: identical Iv endpoints on a sample of
# arguments, see cv_validate.py) and cuts the cost of Phi about 3x.  The library file is not modified.
G.sqrt_two_pi = functools.lru_cache(maxsize=None)(G.sqrt_two_pi)

K, H = F(1, 2), F(5)
C = K + H
KINDS = {  # kind: (atom_removed, source, direction)
    "ARL_SUPER": (False, "one", "super"), "TABOO_SUPER": (True, "one", "super"), "D_SUPER": (True, "h1", "super"),
    "ARL_SUB": (False, "one", "sub"), "TABOO_SUB": (True, "one", "sub"), "D_SUB": (True, "h1", "sub"),
}


@functools.lru_cache(maxsize=None)
def Phi(t: F) -> G.Iv:
    return G.Phi(t)          # pure function of an exact rational: memoising cannot change any bit


def mass(u0: F, u1: F) -> tuple:
    """Rigorous [lo, hi] of int_u0^u1 phi (u0 <= u1)."""
    a, b = Phi(u0), Phi(u1)
    lo = b.lo - a.hi
    return (lo if lo > 0 else F(0)), b.hi - a.lo


def weight(cert: dict) -> dict:
    return {tuple(int(x) for x in k.split(",")): F(v) for k, v in cert["weight"].items()}


def feval_iv(w: dict, P: tuple, M: tuple) -> tuple:
    """Interval of sum c p^i m^j over the box P x M (P, M exact rational pairs, nonnegative), monomial-wise."""
    lo = hi = F(0)
    for (i, j), c in w.items():
        pl, ph = P[0] ** i, P[1] ** i
        ml, mh = M[0] ** j, M[1] ** j           # p, m >= 0: monomials are monotone
        tl, th = pl * ml, ph * mh
        if c >= 0:
            lo += c * tl
            hi += c * th
        else:
            lo += c * th
            hi += c * tl
    return lo, hi


def f_exact(w: dict, p: F, m: F) -> F:
    return sum((c * p ** i * m ** j for (i, j), c in w.items()), F(0))


def cover(depth: int) -> list:
    boxes = [(F(0), H, F(0), H)]
    for _ in range(depth):
        nxt = []
        for (a, b, c, d) in boxes:
            am, cm = (a + b) / 2, (c + d) / 2
            for (x0, x1, y0, y1) in ((a, am, c, cm), (am, b, c, cm), (a, am, cm, d), (am, b, cm, d)):
                if (x0 + y0 <= 4) or y0 == 0 or x0 == 0:
                    nxt.append((x0, x1, y0, y1))
        boxes = nxt
    return boxes


def h1_bounds(a, b, c, d, elo, ehi) -> tuple:
    """h1(p,m,e) = 1 - Phi(C - p + e) + Phi(m - C + e): increasing in p and m; each term bounded separately in e."""
    lo = 1 - Phi(C - a + ehi).hi + Phi(c - C + elo).lo
    hi = 1 - Phi(C - b + elo).lo + Phi(d - C + ehi).hi
    return lo, hi


STATS = {"upper_skips": 0, "lower_drops": 0}   # instrumentation (R1 repair): how often each Khat branch fires


def upper_Kf(w, a, b, c, d, elo, ehi, panels, atom_removed) -> F:
    lo_z, hi_z = c - C, C - a                     # union of the alarm-free windows over the box
    u0a, u1a = lo_z + elo, hi_z + ehi
    step = (u1a - u0a) / panels
    acc = F(0)
    for k in range(panels):
        u0, u1 = u0a + step * k, u0a + step * (k + 1)
        zl, zh = u0 - ehi, u1 - elo
        if atom_removed and (d - K) < (K - b) and zl >= d - K and zh <= K - b:
            STATS["upper_skips"] += 1
            continue                              # inside every state's atom window: no Khat mass
        pl, ph = max(F(0), a + zl - K), max(F(0), b + zh - K)
        ml, mh = max(F(0), c - zh - K), max(F(0), d - zl - K)
        _, fh = feval_iv(w, (pl, ph), (ml, mh))
        if fh > 0:
            acc += fh * mass(u0, u1)[1]
    return acc


def lower_Kf(w, a, b, c, d, elo, ehi, panels, atom_removed) -> F:
    u0a, u1a = d - C + ehi, C - b + elo           # intersection of the windows over box and block
    if u1a <= u0a:
        return F(0)
    step = (u1a - u0a) / panels
    acc = F(0)
    ulo, uhi = c - K, K - a                       # union of the atom windows over the box
    for k in range(panels):
        u0, u1 = u0a + step * k, u0a + step * (k + 1)
        zl, zh = u0 - ehi, u1 - elo
        if atom_removed and ulo < uhi and zl < uhi and zh > ulo:
            STATS["lower_drops"] += 1
            continue                              # may meet an atom window: drop (f >= 0 on R)
        pl, ph = max(F(0), a + zl - K), max(F(0), b + zh - K)
        ml, mh = max(F(0), c - zh - K), max(F(0), d - zl - K)
        fl, _ = feval_iv(w, (pl, ph), (ml, mh))
        mlo, mhi = mass(u0, u1)
        acc += fl * (mlo if fl >= 0 else mhi)
    return acc


def verify(cert: dict) -> dict:
    kind = cert["kind"]
    if kind not in KINDS:
        return {"accepted": False, "reasons": [f"unknown kind {kind}"]}
    elo, ehi = (F(x) for x in cert["drift_block"])
    Q.guard_drift(elo, ehi)
    atom_removed, src, direction = KINDS[kind]
    depth, panels = int(cert["hints"]["depth"]), int(cert["hints"]["panels"])
    w = weight(cert)
    STATS["upper_skips"] = STATS["lower_drops"] = 0
    reasons, mn, fmin, hmin, fsup = [], None, None, None, None
    for (a, b, c, d) in cover(depth):
        fl, fh = feval_iv(w, (a, b), (c, d))
        fmin = fl if fmin is None or fl < fmin else fmin
        fsup = fh if fsup is None or fh > fsup else fsup
        hl, hh = h1_bounds(a, b, c, d, elo, ehi) if (src == "h1" or direction == "sub") else (F(0), F(0))
        if direction == "sub":
            hmin = hl if hmin is None or hl < hmin else hmin
        if direction == "super":
            s_hi = hh if src == "h1" else F(1)
            mg = fl - s_hi - upper_Kf(w, a, b, c, d, elo, ehi, panels, atom_removed)
        else:
            s_lo = hl if src == "h1" else F(1)
            mg = s_lo + lower_Kf(w, a, b, c, d, elo, ehi, panels, atom_removed) - fh
        mn = mg if mn is None or mg < mn else mn
    if mn < 0:
        reasons.append("box inequality fails (margin lower bound < 0)")
    if fmin < 0:
        reasons.append("f >= 0 on R not established")
    if direction == "sub" and not (hmin is not None and hmin > 0):
        reasons.append("h_min > 0 not established")
    val = f_exact(w, F(0), F(0))
    cl = cert.get("claims", {})
    claimed = cl.get("value_at_atom")
    if claimed is None or F(claimed) != val:
        reasons.append("claimed value_at_atom differs from f(a)")
    out = {"verifier": "V_A (fractions + c7_gaussian)", "kind": kind, "accepted": not reasons, "reasons": reasons,
           "margin_lower_bound": float(mn), "f_min_lower_bound": float(fmin), "value_at_atom": str(val),
           "boxes": len(cover(depth)), "khat_branch_counts": dict(STATS)}
    if direction == "sub":
        out["h_min_lower_bound"] = float(hmin)
    if kind == "TABOO_SUPER":
        out["C_T_upper_bound"] = str(fsup)
        if F(cl.get("C_T_upper", "-1")) < fsup:
            out["accepted"] = False
            out["reasons"].append("claimed C_T_upper below the verifier's sup bound")
    if kind == "TABOO_SUB":
        pts = [(x, y) for (x, _, y, _) in cover(depth)] + [(H, F(0)), (F(0), H)]
        pmax = max(f_exact(w, x, y) for x, y in pts)   # box lower-left corners lie in R by construction
        out["C_T_lower_bound"] = str(pmax)
        if F(cl.get("C_T_lower", "0")) > pmax:
            out["accepted"] = False
            out["reasons"].append("claimed C_T_lower above the verifier's point maximum on R")
    return out
