"""Manufactured qualification of theorem TC (tc_rule.py) on exact finite atom chains. Non-scientific: no CUSUM value.

Model (a finite analogue of the CUSUM structure): states 0..N-1, atom a = 0, analytic Gaussian-weighted kernel
    K_e[x, y] = c[x, y] phi(z[x, y] + e),   K_i(e)[x, y] = c[x, y] (-1)^i He_i(z + e) phi(z + e),
source S(e)[x] = s1[x] phi(u[x] + e) - s2[x] phi(l[x] + e), S^(n) with the same Hermite rule. The truth
F^(n)(e) = R_e [S^(n) + sum_{i>=1} C(n,i) K_i F^(n-i)] is computed by Arb matrix solves (python-flint, 256 bits).
Constants handed to the rule are VALID upper bounds computed over the whole cell by interval (ball) evaluation on
sub-balls: k_i >= sup ||K_i(e)||_inf, sigma4 >= sup ||S''''(e)||, and the exact atom functionals
A0 >= sup ||e_a^T R||_1, A1 >= sup ||e_a^T R K_1 R||_1, A2 >= sup ||e_a^T (2 R K_1 R K_1 R + R K_2 R)||_1.

Fixture families (each makes one term of the bound NECESSARY, so the matching mutant must be caught):
  VAR   exact candidates at e0: only the centre motion rho|G(a)| (and the rho^2 Env4 remainder) is non-zero.
  A0    H-candidate off by R(eps sgn(e_a^T R)): |E''(e0)(a)| = eps ||e_a^T R||_1 exactly.
  A1    D-candidate error w with phi''(e0) = 0 by construction: |E''(e0)(a)| = 2 eps ||e_a^T R K1 R||_1.
  A2    F-candidate error u with phi'(e0) = phi''(e0) = 0 by construction: |E''(e0)(a)| = eps ||e_a^T d2R||_1.
  G     G-candidate off by R(eps sgn(e_a^T R)) with eps opposite to F'''(e0)(a): the rho f_G term is necessary.
  SRC   H-candidate solves the equation with a WRONG order-2 source: the residual is 0, the source error is not.
  RAND  random candidates, sources and cells.
Checks per fixture and per e on a 25-point grid of the cell (endpoints included):
  ||phi^(j)(e)|| <= p_j (j = 0, 1, 2)  and  |F''(e)(a) - Hhat(a)| <= rho |Ghat(a)| + rad.

    python -B tc_manufactured.py [--mutants] --out OUT.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
import types
from fractions import Fraction as F
from math import comb
from pathlib import Path

from flint import arb, arb_mat, ctx

HERE = Path(__file__).resolve()
RULE = HERE.parent / "tc_rule.py"
ctx.prec = 256
N = 6
GRID = 25
SUB = 8


def eye(n: int) -> arb_mat:
    return arb_mat([[arb(1) if i == j else arb(0) for j in range(n)] for i in range(n)])


def he(n: int, x):
    a, b = arb(1), x
    if n == 0:
        return a
    for k in range(1, n):
        a, b = b, x * b - k * a
    return b


def phi(x):
    return (-(x * x) / 2).exp() / (2 * arb.pi()).sqrt()


def up(x) -> F:
    """Exact rational upper bound of |x| (outward)."""
    m = x.abs_upper()
    return F(int(m.man_exp()[0])) * F(2) ** int(m.man_exp()[1]) if m != 0 else F(0)


def lo_hi(x) -> tuple[F, F]:
    def ex(v):
        man, e = v.man_exp()
        return F(int(man)) * F(2) ** int(e)
    return ex(x.lower()), ex(x.upper())


class Chain:
    def __init__(self, rnd: random.Random, row_mass: float):
        self.c = [[rnd.random() for _ in range(N)] for _ in range(N)]
        self.z = [[rnd.uniform(-2, 2) for _ in range(N)] for _ in range(N)]
        for x in range(N):                      # scale rows so that the row sum at e = 0 is about row_mass
            s = sum(self.c[x][y] * float(phi(arb(self.z[x][y])).mid()) for y in range(N))
            for y in range(N):
                self.c[x][y] = self.c[x][y] * row_mass / s
        self.c = [[arb(str(round(v, 12))) for v in row] for row in self.c]
        self.z = [[arb(str(round(v, 6))) for v in row] for row in self.z]
        self.s1 = [arb(str(round(rnd.uniform(0, 1), 6))) for _ in range(N)]
        self.s2 = [arb(str(round(rnd.uniform(0, 1), 6))) for _ in range(N)]
        self.u = [arb(str(round(rnd.uniform(0.5, 3), 6))) for _ in range(N)]
        self.l = [arb(str(round(-rnd.uniform(0.5, 3), 6))) for _ in range(N)]

    def K(self, i: int, e) -> arb_mat:
        sgn = -1 if i % 2 else 1
        return arb_mat([[self.c[x][y] * sgn * he(i, self.z[x][y] + e) * phi(self.z[x][y] + e) for y in range(N)]
                        for x in range(N)])

    def S(self, n: int, e) -> arb_mat:
        sgn = -1 if n % 2 else 1
        return arb_mat([[sgn * (self.s1[x] * he(n, self.u[x] + e) * phi(self.u[x] + e)
                                - self.s2[x] * he(n, self.l[x] + e) * phi(self.l[x] + e))] for x in range(N)])

    def resolvent(self, e) -> arb_mat:
        return (eye(N) - self.K(0, e)).inv()

    def truth(self, e, order: int) -> list:
        R = self.resolvent(e)
        Fs = []
        for n in range(order + 1):
            rhs = self.S(n, e)
            for i in range(1, n + 1):
                rhs = rhs + self.K(i, e) * Fs[n - i] * comb(n, i)
            Fs.append(R * rhs)
        return Fs


def vnorm(v: arb_mat) -> F:
    return max(up(v[x, 0]) for x in range(v.nrows()))


def rownorm(M: arb_mat) -> F:
    return max(sum((up(M[x, y]) for y in range(M.ncols())), F(0)) for x in range(M.nrows()))


def row_sign(M: arb_mat, x: int = 0) -> arb_mat:
    return arb_mat([[arb(1) if float(M[x, y].mid()) >= 0 else arb(-1)] for y in range(M.ncols())])


def cell_constants(ch: Chain, e0: F, rho: F) -> dict:
    """Valid upper bounds over the whole cell, by ball evaluation on SUB sub-balls."""
    k = {i: F(0) for i in range(5)}
    A = {"A0": F(0), "A1": F(0), "A2": F(0)}
    s4 = F(0)
    w = rho / SUB
    for s in range(SUB):
        mid = e0 - rho + w * (2 * s + 1)
        e = arb(str(mid.numerator)) / arb(str(mid.denominator)) + arb(0, str(float(w) * 1.0000001))
        Ks = {i: ch.K(i, e) for i in range(5)}
        for i in range(5):
            k[i] = max(k[i], rownorm(Ks[i]))
        s4 = max(s4, vnorm(ch.S(4, e)))
        R = (eye(N) - Ks[0]).inv()
        ea = arb_mat([[arb(1) if y == 0 else arb(0) for y in range(N)]])
        r0 = ea * R
        r1 = r0 * Ks[1] * R
        r2 = (r1 * Ks[1] * R) * 2 + r0 * Ks[2] * R
        A["A0"] = max(A["A0"], rownorm(r0))
        A["A1"] = max(A["A1"], rownorm(r1))
        A["A2"] = max(A["A2"], rownorm(r2))
    return {"k": k, "A": A, "sigma4": s4}


def fx(v: F):
    return arb(str(v.numerator)) / arb(str(v.denominator))


def build(ch: Chain, e0: F, rho: F, family: str, eps: float, rnd: random.Random) -> dict:
    E0 = fx(e0)
    T = ch.truth(E0, 3)
    R = ch.resolvent(E0)
    K1, K2, K3 = ch.K(1, E0), ch.K(2, E0), ch.K(3, E0)
    I = eye(N)
    ea = arb_mat([[arb(1) if y == 0 else arb(0) for y in range(N)]])
    Fh, Dh, Hh, Gh = T[0], T[1], T[2], T[3]
    src_err = [arb_mat(N, 1) for _ in range(4)]            # candidate source minus true source, per order
    e = arb(str(eps))
    if family == "A0":
        Hh = Hh + R * row_sign(ea * R) * e
    elif family == "A1":
        w = R * row_sign(ea * R * K1 * R) * e
        Dh = Dh + w
        Hh = Hh + R * (K1 * w * 2)
    elif family == "A2":
        u = R * row_sign(ea * (R * K1 * R * K1 * R * 2 + R * K2 * R)) * e
        dD = R * K1 * u
        Fh, Dh = Fh + u, Dh + dD
        Hh = Hh + R * (K1 * dD * 2 + K2 * u)
    elif family == "G":
        g = R * row_sign(ea * R)
        sgn = -1 if float(T[3][0, 0].mid()) > 0 else 1
        Gh = Gh + g * (e * sgn)
    elif family == "SRC":
        err = row_sign(ea * R) * e
        src_err[2] = err
        Hh = Hh + R * err                                    # exact solution of the WRONG source equation
    elif family == "RAND":
        def rv(scale):
            return arb_mat([[arb(str(round(rnd.uniform(-1, 1) * scale, 12)))] for _ in range(N)])
        Fh, Dh, Hh, Gh = Fh + rv(eps), Dh + rv(eps * 10), Hh + rv(eps * 30), Gh + rv(eps * 300)
        src_err = [rv(eps * 0.3) for _ in range(4)]
    # residuals at e0, exactly as the frozen DAG defines them (candidate sources S + err)
    S = [ch.S(n, E0) + src_err[n] for n in range(4)]
    res = [(I - ch.K(0, E0)) * Fh - S[0],
           (I - ch.K(0, E0)) * Dh - K1 * Fh - S[1],
           (I - ch.K(0, E0)) * Hh - K2 * Fh - K1 * Dh * 2 - S[2],
           (I - ch.K(0, E0)) * Gh - K3 * Fh - K2 * Dh * 3 - K1 * Hh * 3 - S[3]]
    cc = cell_constants(ch, e0, rho)
    rec = {"rho": f"{rho.numerator}/{rho.denominator}",
           "norms": {"k": [str(cc["k"][i]) for i in range(5)], "j": ["0"] * 5},
           "sup_S0": ["0", "0", "0", "0", str(cc["sigma4"])],
           "r": {"0": {"delta_F": str(vnorm(res[0])), "delta_D": str(vnorm(res[1])), "delta_H": str(vnorm(res[2])),
                       "delta_G": str(vnorm(res[3])), "eps_src": [str(vnorm(src_err[n])) for n in range(4)],
                       "sup": {"F": str(vnorm(Fh)), "D": str(vnorm(Dh)), "H": str(vnorm(Hh)), "G": str(vnorm(Gh))},
                       "H_at_a": [str(x) for x in lo_hi(Hh[0, 0])], "abs_G_at_a": str(up(Gh[0, 0]))}}}
    return {"rec": rec, "A": cc["A"], "cand": (Fh, Dh, Hh, Gh), "ch": ch, "e0": e0, "rho": rho}


def check(fix: dict, R) -> dict:
    """Validity of p_j and of the object enclosure on the e-grid; returns violations."""
    rec, A, ch = fix["rec"], fix["A"], fix["ch"]
    q = R.per_r(rec, 0, A)
    Fh, Dh, Hh, Gh = fix["cand"]
    h_lo, h_hi = (F(x) for x in rec["r"]["0"]["H_at_a"])
    enc = R.cell_enclosure(rec, A, 1)                  # m = 1: the object itself, through the assembly code path
    viol, worst = [], F(0)
    for g in range(GRID):
        t = -fix["rho"] + 2 * fix["rho"] * F(g, GRID - 1)
        e = fx(fix["e0"] + t)
        tt = fx(t)
        T = ch.truth(e, 2)
        Ft = Fh + Dh * tt + Hh * (tt * tt / 2) + Gh * (tt * tt * tt / 6)
        Dt = Dh + Hh * tt + Gh * (tt * tt / 2)
        Ht = Hh + Gh * tt
        K0, K1, K2 = ch.K(0, e), ch.K(1, e), ch.K(2, e)
        I = eye(N)
        ph = [ch.S(0, e) - (I - K0) * Ft,
              ch.S(1, e) - (I - K0) * Dt + K1 * Ft,
              ch.S(2, e) - (I - K0) * Ht + K1 * Dt * 2 + K2 * Ft]
        for j in range(3):
            lo_norm = max(lo_hi(ph[j][x, 0].abs_lower())[0] for x in range(N))   # exact certified lower bound
            if lo_norm > q["p"][j]:
                viol.append({"kind": f"p{j}", "t": str(t)})
        tv = T[2][0, 0]
        tl, th = lo_hi(tv)
        if th < enc[0] or tl > enc[1]:
            viol.append({"kind": "enclosure", "t": str(t)})
        dev = max(abs(th - (h_lo + h_hi) / 2), abs(tl - (h_lo + h_hi) / 2))
        worst = max(worst, dev / q["half"] if q["half"] > 0 else F(0))
    return {"violations": viol, "tightness": float(worst)}


FAMILIES = [("VAR", 0.0, F(1, 50)), ("A0", 1e-4, F(1, 10 ** 6)), ("A1", 1e-4, F(1, 10 ** 6)),
            ("A2", 1e-4, F(1, 10 ** 6)), ("G", 1e-3, F(1, 10 ** 4)), ("SRC", 1e-4, F(1, 10 ** 6)),
            ("RAND", 1e-5, F(1, 1000)), ("RAND", 1e-3, F(1, 100)), ("RAND", 1e-6, F(1, 30))]


def fixtures(seed: int = 20260920, per_family: int = 4) -> list:
    out = []
    for fi, (fam, eps, rho) in enumerate(FAMILIES):
        for s in range(per_family):
            rnd = random.Random(seed + 1000 * fi + s)
            ch = Chain(rnd, row_mass=rnd.choice([0.7, 0.85, 0.95]))
            e0 = F(rnd.randint(-200, 200), 1000)
            out.append((f"{fam}_{fi}_{s}", build(ch, e0, rho, fam, eps, rnd)))
    return out


def load_rule(src: str | None = None):
    text = RULE.read_text() if src is None else src
    mod = types.ModuleType("tc_rule_under_test")
    exec(compile(text, str(RULE), "exec"), mod.__dict__)
    return mod


MUTANTS = {
    "M01_drop_env4_in_p2": ("    p2 = fH + rho * fG + rho ** 2 * e4 / 2\n", "    p2 = fH + rho * fG\n"),
    "M02_drop_A2_term": ('return A["A0"] * p2 + 2 * A["A1"] * p1 + A["A2"] * p0', 'return A["A0"] * p2 + 2 * A["A1"] * p1'),
    "M03_single_A1": ('return A["A0"] * p2 + 2 * A["A1"] * p1 + A["A2"] * p0', 'return A["A0"] * p2 + A["A1"] * p1 + A["A2"] * p0'),
    "M04_drop_A0_term": ('return A["A0"] * p2 + 2 * A["A1"] * p1 + A["A2"] * p0', 'return 2 * A["A1"] * p1 + A["A2"] * p0'),
    "M05_drop_rho_fG": ("    p2 = fH + rho * fG + rho ** 2 * e4 / 2\n", "    p2 = fH + rho ** 2 * e4 / 2\n"),
    "M06_drop_centre_motion": ('return _nonneg("rho", rho) * _nonneg("|G(a)|", abs_G_at_a) + _nonneg("rad", rad)',
                               'return _nonneg("rad", rad)'),
    "M07_half_cell_domain": ('return _nonneg("rho", rho) * _nonneg("|G(a)|", abs_G_at_a) + _nonneg("rad", rad)',
                             'return _nonneg("rho", rho) / 2 * _nonneg("|G(a)|", abs_G_at_a) + _nonneg("rad", rad)'),
    "M08_point_not_cell": ('    rho = F(cellrec["rho"])\n', '    rho = F(cellrec["rho"]) * 0\n'),
    "M09_wrong_source_node": ('fH = F(o["delta_H"]) + F(o["eps_src"][2])', 'fH = F(o["delta_H"]) + F(o["eps_src"][1])'),
    "M10_sign_flip_lower": ("lo += c * (h_lo - q[\"half\"])", "lo += c * (h_lo + q[\"half\"])"),
    "M11_wrong_m_table": ('rows = [("F", r, 0, F(1, m)) for r in range(m)]', 'rows = [("F", r, 0, F(1, m + 1)) for r in range(m)]'),
    "M12_drop_fD_in_p1": ("    p1 = fD + rho * fH + rho ** 2 * fG / 2 + rho ** 3 * e4 / 6\n",
                          "    p1 = rho * fH + rho ** 2 * fG / 2 + rho ** 3 * e4 / 6\n"),
    "M13_underestimate_env4": ("    return (sigma4 + 4 * k[1] * sG", "    return (sigma4 + 0 * k[1] * sG"),
    "M14_drop_fF_in_p0": ("    p0 = fF + rho * fD", "    p0 = rho * fD"),
}


def frozen_table_ok(R) -> bool:
    def ref(m):
        rows = [("F", r, 0, F(1, m)) for r in range(m)]
        return rows + [("W", r, t - r - 1, F(1, t) - F(1, m)) for t in range(1, m) for r in range(t)]
    return all(sorted(R.coefficients(m)) == sorted(ref(m)) for m in (1, 2, 3, 5))


def run(mutants: bool) -> dict:
    fx_list = fixtures()
    R = load_rule()
    base = {name: check(f, R) for name, f in fx_list}
    out = {"schema": "rebaseguard.p5y.k5.lower-front-order3.tc-manufactured.v1", "fixtures": len(fx_list),
           "grid": GRID, "rule_sha256": hashlib.sha256(RULE.read_bytes()).hexdigest(),
           "correct": {n: {"violations": len(v["violations"]), "tightness": v["tightness"]} for n, v in base.items()},
           "correct_violations": sum(len(v["violations"]) for v in base.values()),
           "frozen_table_ok": frozen_table_ok(R)}
    tight = {fam: max(v["tightness"] for n, v in base.items() if n.startswith(fam + "_")) for fam, _, _ in FAMILIES}
    out["max_tightness_per_family"] = tight
    if mutants:
        src = RULE.read_text()
        res = {}
        for name, (old, new) in MUTANTS.items():
            if src.count(old) != 1:
                res[name] = {"applied": False}
                continue
            Rm = load_rule(src.replace(old, new))
            caught_by = []
            if not frozen_table_ok(Rm):
                caught_by.append("frozen_table")
            nv = 0
            for n, f in fx_list:
                try:
                    nv += len(check(f, Rm)["violations"])
                except Exception as exc:                            # refusal is also detection
                    caught_by.append(f"refusal:{type(exc).__name__}")
                    break
            if nv:
                caught_by.append(f"containment:{nv}")
            res[name] = {"applied": True, "detected": bool(caught_by), "caught_by": caught_by}
        out["mutants"] = res
        out["mutants_detected"] = sum(1 for v in res.values() if v.get("detected"))
        out["mutants_applied"] = sum(1 for v in res.values() if v.get("applied"))
    out["pass"] = (out["correct_violations"] == 0 and out["frozen_table_ok"]
                   and (not mutants or out["mutants_detected"] == out["mutants_applied"] == len(MUTANTS)))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mutants", action="store_true")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    res = run(a.mutants)
    Path(a.out).write_text(json.dumps(res, sort_keys=True, indent=1) + "\n")
    print(json.dumps({k: v for k, v in res.items() if k not in ("correct", "mutants")}))
    if a.mutants:
        print(json.dumps(res["mutants"]))
    return 0 if res["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
