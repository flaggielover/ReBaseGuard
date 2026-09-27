"""UNTRUSTED certificate search for the Theorem CV validation (non-target drift only).

Theorem CV separates SEARCH from VERIFICATION: nothing here is trusted.  Candidates are LP-optimal members of a
declared polynomial family on the float Nystrom operator (mechanism/mech_core.py, mech_lp.py), made robust by a
one-parameter inflation (super kinds) or deflation (sub kinds), rounded to a dyadic grid, and pre-screened with a
FLOAT emulation of the box/panel condition.  Only the rigorous verifiers (cv_verify_a.py, cv_verify_b.py) decide.

Declared validation set (fixed before any verification; non-target, by rule):
  drift block  E = [3, 3 + 1/16] for the supply kinds (ARL_SUPER, TABOO_SUPER, D_SUB);
               E' = {3} (the block's left end) for the other-side kinds (ARL_SUB, TABOO_SUB, D_SUPER)
  family       monotone polynomials in m of degree 3 (ARL/TABOO: A - sum b_j m^j; D: a + sum b_j m^j; b_j >= 0),
               optimised directly over the float box/panel condition (an LP), then rounded safely
  discretisation hints  depth 5 (363 boxes), 32 u-panels (C11R's frozen configuration; a trial at depth 4 / 16
                        panels was run first and gave vacuous D_SUPER bounds -- recorded in PROGRESS.md)
"""
from __future__ import annotations

import json
import math
import sys
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parents[2]
sys.path.insert(0, str(NS / "code"))
sys.path.insert(0, str(HERE.parent / "mechanism"))
import ov_quarantine as Q  # noqa: E402
import mech_core as MC  # noqa: E402
import mech_lp as LP  # noqa: E402

Q.install_import_guard()

E_LO, E_HI = Fr(3), Fr(49, 16)
DEPTH, PANELS = 5, 32
GRID = 2 ** 24
KIND = {  # kind: (atom_removed, source, direction, family degree in m, block)
    "ARL_SUPER": (False, "one", "super", 3, (E_LO, E_HI)),
    "TABOO_SUPER": (True, "one", "super", 3, (E_LO, E_HI)),
    "D_SUB": (True, "h1", "sub", 3, (E_LO, E_HI)),
    "ARL_SUB": (False, "one", "sub", 3, (E_LO, E_LO)),
    "TABOO_SUB": (True, "one", "sub", 3, (E_LO, E_LO)),
    "D_SUPER": (True, "h1", "super", 3, (E_LO, E_LO)),
}


# ------------------------------------------------------------------------------------------------ float box screen
def _cover(depth):
    n = 2 ** depth
    s = 5.0 / n
    return [(s * i, s * i + s, s * j, s * j + s) for i in range(n) for j in range(n)
            if s * i + s * j <= 4 or i == 0 or j == 0]


def _frange(cs, lo, hi):
    """Range of the polynomial in m over [lo, hi]: exact for the monotone families used here (ends), plus a
    sampled check (screen only)."""
    xs = [lo + (hi - lo) * t / 8 for t in range(9)]
    v = [sum(c * x ** j for j, c in enumerate(cs)) for x in xs]
    return min(v), max(v)


def screen(kind: str, cs: list) -> float:
    ar, src, direc, _, (elo, ehi) = KIND[kind]
    elo, ehi = float(elo), float(ehi)
    K_, C_ = 0.5, 5.5
    worst = math.inf
    for (a, b, c, d) in _cover(DEPTH):
        fl, fh = _frange(cs, c, d)
        if fl < 0:
            return -1.0
        h_lo = 1 - MC.pmass(-60, C_ - a + ehi) + MC.pmass(-60, c - C_ + elo)
        h_hi = 1 - MC.pmass(-60, C_ - b + elo) + MC.pmass(-60, d - C_ + ehi)
        acc = 0.0
        if direc == "super":
            u0a, u1a = c - C_ + elo, C_ - a + ehi
            st = (u1a - u0a) / PANELS
            for k in range(PANELS):
                u0, u1 = u0a + st * k, u0a + st * (k + 1)
                zl, zh = u0 - ehi, u1 - elo
                if ar and (d - K_) < (K_ - b) and zl >= d - K_ and zh <= K_ - b:
                    continue
                _, ih = _frange(cs, max(0, c - zh - K_), max(0, d - zl - K_))
                acc += max(0.0, ih) * MC.pmass(u0, u1)
            mg = fl - (h_hi if src == "h1" else 1.0) - acc
        else:
            u0a, u1a = d - C_ + ehi, C_ - b + elo
            if u1a > u0a:
                st = (u1a - u0a) / PANELS
                for k in range(PANELS):
                    u0, u1 = u0a + st * k, u0a + st * (k + 1)
                    zl, zh = u0 - ehi, u1 - elo
                    if ar and (c - K_) < (K_ - a) and zl < K_ - a and zh > c - K_:
                        continue
                    il, _ = _frange(cs, max(0, c - zh - K_), max(0, d - zl - K_))
                    acc += il * MC.pmass(u0, u1)
            mg = (h_lo if src == "h1" else 1.0) + acc - fh
        worst = min(worst, mg)
    return worst


def box_lp(kind: str) -> list:
    """Float LP over the BOX/PANEL condition for a monotone polynomial family in m (untrusted search).

    ARL/TABOO (value functions decreasing in m):  f = A - sum_{j<=DEG} b_j m^j, b_j >= 0;
    D (increasing in m):                          f = a + sum_{j<=DEG} b_j m^j, b_j >= 0.
    For such f the interval bounds the verifiers use are attained at interval ends, so every box inequality is
    LINEAR in (A, b): the optimal certifiable member at the declared depth/panels is an LP.  Margin >= 1e-6."""
    ar, src, direc, deg, (elo, ehi) = KIND[kind]
    Q.guard_drift(elo, ehi)
    elo, ehi = float(elo), float(ehi)
    inc = src == "h1"
    sg = 1.0 if inc else -1.0                      # f = x0 + sg * sum b_j m^j

    def row_at(m, scale=1.0):                      # coefficients of f(m) in (x0, b_1..b_deg)
        return [scale] + [scale * sg * m ** j for j in range(1, deg + 1)]
    K_, C_ = 0.5, 5.5
    G, g = [], []
    for (a, b, c, d) in _cover(DEPTH):
        h_lo = 1 - MC.pmass(-60, C_ - a + ehi) + MC.pmass(-60, c - C_ + elo)
        h_hi = 1 - MC.pmass(-60, C_ - b + elo) + MC.pmass(-60, d - C_ + ehi)
        if direc == "super":
            u0a, u1a = c - C_ + elo, C_ - a + ehi
            st = (u1a - u0a) / PANELS
            row = row_at(c if inc else d)          # f_lo on the box
            for k in range(PANELS):
                u0, u1 = u0a + st * k, u0a + st * (k + 1)
                zl, zh = u0 - ehi, u1 - elo
                if ar and (d - K_) < (K_ - b) and zl >= d - K_ and zh <= K_ - b:
                    continue
                mimg = max(0.0, d - zl - K_) if inc else max(0.0, c - zh - K_)   # where f is largest
                r2 = row_at(mimg, MC.pmass(u0, u1) * (1 + 1e-12))
                row = [x - y for x, y in zip(row, r2)]
            G.append(row)
            g.append((h_hi if src == "h1" else 1.0) + 1e-6)
        else:
            u0a, u1a = d - C_ + ehi, C_ - b + elo
            row = [-x for x in row_at(d if inc else c)]   # - f_hi on the box
            if u1a > u0a:
                st = (u1a - u0a) / PANELS
                for k in range(PANELS):
                    u0, u1 = u0a + st * k, u0a + st * (k + 1)
                    zl, zh = u0 - ehi, u1 - elo
                    if ar and (c - K_) < (K_ - a) and zl < K_ - a and zh > c - K_:
                        continue
                    mimg = max(0.0, c - zh - K_) if inc else max(0.0, d - zl - K_)  # where f is smallest
                    r2 = row_at(mimg, MC.pmass(u0, u1) * (1 - 1e-12))
                    row = [x + y for x, y in zip(row, r2)]
            G.append(row)
            g.append(-(h_lo if src == "h1" else 1.0) + 1e-6)
    G.append(row_at(0.0 if inc else 5.0))          # f >= 0 on [0, 5]
    g.append(0.0)
    for j in range(1, deg + 1):                    # b_j >= 0
        G.append([0.0] * j + [1.0] + [0.0] * (deg - j))
        g.append(0.0)
    c = [1.0] + [0.0] * deg if direc == "super" else [-1.0] + [0.0] * deg
    sol = LP.solve(G, g, c)
    x = sol["x"]
    return [x[0]] + [sg * bj for bj in x[1:]]      # raw monomial coefficients


def dyadic(x: float, up: bool) -> Fr:
    return Fr(math.ceil(x * GRID) if up else math.floor(x * GRID), GRID)


def robustify(kind: str, cs: list) -> tuple:
    """Round to the dyadic grid in the safe direction (super: up; sub: down; m^j >= 0 so each coefficient moves f
    monotonically) and confirm with the float screen; shrink/inflate on a fixed ladder only if needed."""
    direc = KIND[kind][2]
    for eta in [0.0, 1e-4, 1e-3, 1e-2]:
        c2 = [(1 + eta) * c for c in cs] if direc == "super" else [(1 - eta) * c for c in cs]
        q = [dyadic(c, up=(direc == "super")) for c in c2]
        if screen(kind, [float(x) for x in q]) >= 0:
            return q, eta
    raise RuntimeError(f"no robust candidate for {kind}")


def make_cert(kind: str, q: list) -> dict:
    _, _, _, _, (lo, hi) = KIND[kind]
    w = {f"0,{j}": str(c) for j, c in enumerate(q) if c != 0}
    cert = {"schema": "A306_CV_CERT/1", "kind": kind, "drift_block": [str(lo), str(hi)], "weight": w,
            "claims": {"value_at_atom": str(q[0])}, "hints": {"depth": DEPTH, "panels": PANELS},
            "model": {"K": "1/2", "H": "5", "R": "0<=p,m<=5 and (p+m<=4 or p==0 or m==0)", "atom": [0, 0]}}
    if kind == "TABOO_SUPER":
        # sup_R f for a polynomial in m: bound over [0,5] by dense sampling + Lipschitz pad, rounded up (claim only)
        xs = [5 * t / 4000 for t in range(4001)]
        mx = max(sum(float(c) * x ** j for j, c in enumerate(q)) for x in xs)
        L = sum(abs(float(c)) * j * 5 ** (j - 1) for j, c in enumerate(q) if j) * 5 / 8000
        cert["claims"]["C_T_upper"] = str(dyadic(mx + L + 1e-9, up=True))
    if kind == "TABOO_SUB":
        n = 2 ** DEPTH
        s = Fr(5, n)
        pts = [(s * i, s * j) for i in range(n) for j in range(n) if s * i + s * j <= 4 or i == 0 or j == 0]
        pts += [(Fr(5), Fr(0)), (Fr(0), Fr(5))]
        cert["claims"]["C_T_lower"] = str(max(sum((c * m ** j for j, c in enumerate(q)), Fr(0)) for _, m in pts))
    return cert


def main() -> dict:
    out = {}
    for kind in KIND:
        cs = box_lp(kind)
        q, eta = robustify(kind, cs)
        out[kind] = {"certificate": make_cert(kind, q), "search": {"lp_coeffs_float": cs, "eta": eta,
                                                                     "float_screen_margin": screen(kind, [float(x) for x in q])}}
        print(kind, "eta", eta, "f(a)", float(q[0]), flush=True)
    return out


if __name__ == "__main__":
    o = main()
    (HERE / "certs").mkdir(exist_ok=True)
    for k, v in o.items():
        (HERE / "certs" / f"{k}.json").write_text(json.dumps(v["certificate"], indent=1, sort_keys=True) + "\n")
    (HERE / "certs" / "SEARCH_LOG.json").write_text(json.dumps({k: v["search"] for k, v in o.items()},
                                                               indent=1, sort_keys=True, default=str) + "\n")
    Q.log_execution("streams/A_306/common/cv_search.py", "untrusted LP certificate search at e in [3, 49/16]",
                    cells_touched=[], klass="NONTARGET_DRIFT_VALIDATION", notes="float search; verification separate")
