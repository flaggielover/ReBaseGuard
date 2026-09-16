"""R3 Part E: the REAL frozen CUSUM Arb residual stack on SYNTHETIC candidates. NON-SCIENTIFIC.

`SyntheticGradedCert` is the R3 GradedRealCertifier with `prepare` replaced by the frozen prepare MINUS the collocation,
Layer-1 objects and candidate solves: exact closed forms, frozen phi series, truncation allowances, drift-aware norm
merge (sharp_certifier) and the order-3 closed forms (Aux3) are the real ones at a SYNTHETIC drift that is not a cover
cell. Every candidate is a synthetic degree-12 dyadic Chebyshev polynomial of prescribed sigma-parity (not a DAG
object, not an approximation of any R derivative). The real residual passes then run unchanged: all_residuals
(reviewed + Repair1 + order-2 tightening), aux_residuals (Aux3), R1 g_residual; no R''' is formed and no export centre
is computed (radius-only).

Checks (all independent of any scientific value):
    C1 scalar fallback equivalence   graded_dag(parity=False) midpoint nodes == FROZEN aux_propagate.cell_dag +
                                     aux_certifier.midpoint_order3_eps, and the R1 rung formula for F:r:3
    C2 graded residuals at e0         |(r(x) +- r(sigma x))/2| from independent float quadrature <= graded mid bound
    C3 graded whole-cell residuals    the same at the cell endpoints against mid + rho * graded envelope
    C4 parity identities             K_i(0) and J_i(0) on real kernels: T(f o sigma)(x) = s (T f)(sigma x)
    C5 graded never looser            e, o <= t for every node; graded radius <= scalar radius
"""
from __future__ import annotations

import math
import sys
from fractions import Fraction as F
from math import comb
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CP = NS.parents[0]
for _p in (str(NS / "code"), str(CP / "p5y_k5_cusum_order3_r2_repair/code"),
           str(CP / "p5y_k5_cusum_order3_real_producer/code")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import graded_real as GR  # noqa: E402

import numpy as np  # noqa: E402
from flint import arb  # noqa: E402

import aux_certifier  # noqa: E402
import aux_propagate  # noqa: E402
import cusum_layer1 as L1  # noqa: E402
import graded_dag as G  # noqa: E402
import opnorms  # noqa: E402
import ra_certifier as RA  # noqa: E402
import sharp_norms  # noqa: E402
from cusum_layer2 import REWARD_RADIUS  # noqa: E402
from intervals import exact  # noqa: E402
from rebaseguard_certify.polynomial import bi_eval, chebyshev_payload_to_power  # noqa: E402
from rebaseguard_certify.residual import _chebyshev_sup  # noqa: E402

K_, C_ = 0.5, 5.5
FLOAT_TOL = 1e-7
CELL = {"detector": "CUSUM", "index": -7, "left": ["0"], "right": ["1/20"], "e0": ["1/40"], "rho": ["1/40"],
        "C_upper": "1233"}


# ------------------------------------------------------------------ synthetic payloads with prescribed parity
def _payload(seed: int, parity: int, scale: float):
    n = L1.DEGREE + 1
    x = np.cos(np.pi * np.arange(n) / L1.DEGREE)
    nodes = 0.5 * L1.H_FROZEN * (1.0 - x)
    P, M = np.meshgrid(nodes, nodes, indexing="ij")
    a = 0.25 + 0.05 * (seed % 7)
    g = lambda u: np.cos(a * u + 0.1 * seed) * np.exp(-0.04 * u)
    v = scale * (g(P) + parity * g(M) + 0.3 * math.sin(seed) * (P * M / 25.0) * (1 if parity == 1 else 0))
    return L1.dyadic_candidate(v.ravel(), n)


class SyntheticGradedCert(GR.GradedRealCertifier):
    def prepare_synthetic(self, seed: int = 1):
        self.n = L1.DEGREE + 1
        e = exact(self.e0)
        self.e = e
        self.norms = opnorms.table(exact(self.e_max))
        self.b = [RA.phi_taylor_coefficients(self.order, e)]
        for _ in range(3):
            self.b.append(RA.derivative_coefficients(self.b[-1]))
        self.eps_z = RA.taylor_remainder(self.order, exact(F(11, 2)))
        self.eps_r = RA.taylor_remainder(self.order, exact(REWARD_RADIUS))
        (self.phi_u, self.cdf_u), (self.phi_l, self.cdf_l), self.arg_u, self.arg_l = RA._recentred_sites(self.order, e)
        self._closed_forms()
        sharp = sharp_norms.table(self.left, self.right)                      # sharp_certifier merge
        merged = dict(self.norms)
        merged.update({"k": sharp["k"], "j": sharp["j"], "window": sharp["window"]})
        self.norms = merged
        self._closed_forms_order3()
        self.P, self.sup, self.payloads = {}, {}, {}
        s = seed * 1000

        def put(key, parity, scale=1.0):
            pay = _payload(s + len(self.payloads), parity, scale)
            self.payloads[key] = pay
            self.P[key], self.sup[key] = chebyshev_payload_to_power(pay), _chebyshev_sup(pay)

        par = GR.derivative_parity
        for j in range(1, 5):
            for k in range(4):
                put(("h", j, k), par("h", k), 0.8)
        for k in range(4):
            self.P["hclosed", 1, k] = self.h1_closed[k]
            self.sup["hclosed", 1, k] = self.sup_h1[k]
            self.P["Sclosed", 0, k] = self.S0_closed[k]
            self.sup["Sclosed", 0, k] = self.sup_S0[k]
        for r in range(5):
            for k in range(4):
                put(("S", r, k), par("S", k), 0.5)
        for r in range(5):
            for q, fam in enumerate(("F", "D", "H", "G")):
                put((fam, r, 0), par("F", q), 1.0 + q)
        for (r, j) in L1.W_INDICES:
            for k in range(4):
                put(("W", (r, j), k), par("W", k), 0.6)
        for r in range(4):
            for k in range(4):
                self.P["W", (r, 0), k] = self.P["S", r, k]
                self.sup["W", (r, 0), k] = self.sup["S", r, k]
                self.payloads[("W", (r, 0), k)] = self.payloads[("S", r, k)]
        return self


def build(seed: int = 1, bits: int = 256):
    from intervals import workprec
    with workprec(bits):
        cert = SyntheticGradedCert(dict(CELL), bits=bits).prepare_synthetic(seed)
        residuals = GR.all_residuals_for_graded(cert)
    return cert, residuals


# ------------------------------------------------------------------ independent float reference
def _he(i, y):
    return [1.0, y, y * y - 1.0, y ** 3 - 3 * y, y ** 4 - 6 * y * y + 3.0][i]


def phi_d(i, y):
    return (-1) ** i * _he(i, y) * math.exp(-0.5 * y * y) / math.sqrt(2 * math.pi)


def cheb(pay, p, m):
    c = np.asarray(pay["numerators"], dtype=float) / float(1 << int(pay["scale_bits"]))
    return float(np.polynomial.chebyshev.chebval2d(2 * p / 5.0 - 1, 2 * m / 5.0 - 1, c))


GN, GW = np.polynomial.legendre.leggauss(80)


def op_float(pay, i, p, m, e, zweight):
    lo, hi = m - C_, C_ - p
    cuts = sorted({lo, hi, *(z for z in (K_ - p, m - K_) if lo < z < hi)})
    tot = 0.0
    for a, b in zip(cuts[:-1], cuts[1:]):
        mid, rad = 0.5 * (a + b), 0.5 * (b - a)
        for t, w in zip(GN, GW):
            z = mid + rad * t
            tot += rad * w * phi_d(i, z + e) * (z if zweight else 1.0) * cheb(pay, max(0.0, p + z - K_), max(0.0, m - z - K_))
    return tot


def J_float(pay, i, p, m, e):
    out = op_float(pay, i, p, m, e, True) + e * op_float(pay, i, p, m, e, False)
    if i >= 1:
        out += i * op_float(pay, i - 1, p, m, e, False)
    return out


def S0_float(k, p, m, e):
    return phi_d(k, C_ - p + e) - phi_d(k, m - C_ + e)


def h1_float(k, p, m, e):
    if k == 0:
        Phi = lambda y: 0.5 * (1 + math.erf(y / math.sqrt(2)))
        return 1 - Phi(C_ - p + e) + Phi(m - C_ + e)
    return -S0_float(k - 1, p, m, e)


def residual_float(cert, name, p, m, e):
    pl = cert.payloads
    if name.startswith("h_1:"):
        k = int(name.split(":")[1])
        return cheb(pl["h", 1, k], p, m) - h1_float(k, p, m, e)
    if name.startswith("S_0:"):
        k = int(name.split(":")[1])
        return cheb(pl["S", 0, k], p, m) - S0_float(k, p, m, e)
    if name.startswith("h_"):
        j, k = map(int, name[2:].split(":"))
        return cheb(pl["h", j, k], p, m) - sum(comb(k, i) * op_float(pl["h", j - 1, k - i], i, p, m, e, False)
                                               for i in range(k + 1))
    if name.startswith("S_"):
        r, k = map(int, name[2:].split(":"))
        return cheb(pl["S", r, k], p, m) - sum(comb(k, i) * J_float(pl["h", r, k - i], i, p, m, e) for i in range(k + 1))
    if name.startswith("W_"):
        rj, k = name[2:].split(":")
        r, j = map(int, rj.split("_"))
        k = int(k)
        return cheb(pl["W", (r, j), k], p, m) - sum(comb(k, i) * op_float(pl["W", (r, j - 1), k - i], i, p, m, e, False)
                                                    for i in range(k + 1))
    head, r = name.split("_")
    n = {"F": 0, "dF": 1, "H": 2, "G": 3}[head]
    r = int(r)
    fams = ("F", "D", "H", "G")
    X = pl[fams[n], r, 0]
    val = cheb(X, p, m) - op_float(X, 0, p, m, e, False)
    for i in range(1, n + 1):
        val -= comb(n, i) * op_float(pl[fams[n - i], r, 0], i, p, m, e, False)
    # the r = 0 residual is certified against the FIXED closed form at e0; its drift is charged to the Sclosed leaf
    src = S0_float(n, p, m, float(F(CELL["e0"][0]))) if r == 0 else cheb(pl["S", r, n], p, m)
    return val - src


CHECK_NAMES = ["h_1:2", "S_0:1", "h_2:1", "h_3:2", "S_1:1", "S_2:2", "F_0", "dF_1", "H_1", "G_1", "G_0",
               "W_0_1:1", "W_1_1:2", "h_2:3", "S_1:3", "W_0_1:3"]


def reachable_states():
    out = []
    for r in (F(0), F(1, 2), F(1), F(2), F(3), F(4)):
        for t in (F(0), F(1, 4), F(1, 2), F(3, 4), F(1)):
            out.append((float(r * t), float(r * (1 - t))))
    for x in (4.5, 5.0):
        out += [(x, 0.0), (0.0, x)]
    return out


def float_references(cert) -> dict:
    """Float residual values for CHECK_NAMES at every reachable state, at e0 and at both cell endpoints."""
    drifts = {"e0": float(F(CELL["e0"][0])), "left": float(F(CELL["left"][0])), "right": float(F(CELL["right"][0]))}
    return {name: {tag: {f"{p},{m}": residual_float(cert, name, p, m, e) for p, m in reachable_states()}
                   for tag, e in drifts.items()} for name in CHECK_NAMES}


def graded_residual_checks(inputs: dict, refs: dict) -> list[str]:
    """C2 (tag e0 vs mid) and C3 (cell endpoints vs cell) on the float references."""
    import rung3_engine as R1E
    viol = []
    for name, by_tag in refs.items():
        ent = inputs["res"][GR.engine_name(name)]
        for tag, vals in by_tag.items():
            b = ent["mid"] if tag == "e0" else ent["cell"]
            be, bo = float(R1E.fraction_of(b[0].abs_upper())), float(R1E.fraction_of(b[1].abs_upper()))
            for key, v in vals.items():
                p, m = key.split(",")
                vs = vals[f"{m},{p}"]
                ev, ov = abs(v + vs) / 2, abs(v - vs) / 2
                if ev > be + FLOAT_TOL:
                    viol.append(f"{name}@{tag} even {ev:.3e} > {be:.3e} at {key}")
                if ov > bo + FLOAT_TOL:
                    viol.append(f"{name}@{tag} odd {ov:.3e} > {bo:.3e} at {key}")
    return viol


def scalar_equivalence(cert, residuals, inputs) -> list[str]:
    """C1: graded engine in scalar mode == frozen midpoint DAG (orders 0..2), Aux3 order-3 midpoint and the R1 rung."""
    import rung3_engine as R1E
    problems = []
    cert.residuals = {k: v for k, v in residuals.items() if not k.startswith("G_") and ":3" not in k} | \
        {k: v for k, v in residuals.items() if k.startswith("Sclosed")}
    mid = aux_propagate.cell_dag(cert, "delta_mid")
    cert.aux = {k: v for k, v in residuals.items() if k.endswith(":3")}
    frozen = aux_certifier.midpoint_order3_eps(cert, mid.nodes)
    out = G.certify_graded(inputs, parity=False)
    nodes = out["mid"]["nodes"]
    tol = F(1, 2 ** 200)

    def cmp(eng_node, value):
        a, b = R1E.fraction_of(nodes[eng_node].t), R1E.fraction_of(value.abs_upper())
        if abs(a - b) > tol * max(abs(b), F(1)):
            problems.append(f"{eng_node}: engine {float(a):.12e} frozen {float(b):.12e}")

    for fn, v in frozen.items():
        parts = fn.split(":")
        if parts[0] == "F":
            cmp(f"F:{parts[1]}:0", v)
        elif parts[0] == "D":
            cmp(f"F:{parts[1]}:1", v)
        elif parts[0] == "H":
            cmp(f"F:{parts[1]}:2", v)
        elif parts[0] in ("h", "S", "W", "Sclosed") and fn in nodes:
            cmp(fn, v)
    k = cert.norms["k"]
    C = exact(cert.C)
    for r in range(5):
        src = frozen["Sclosed:3"] if r == 0 else frozen[f"S:{r}:3"]
        gm = C * (residuals[f"G_{r}"]["delta_mid"] + k[3] * frozen[f"F:{r}"] + arb(3) * k[2] * frozen[f"D:{r}"]
                  + arb(3) * k[1] * frozen[f"H:{r}"] + src)
        cmp(f"F:{r}:3", gm)
    for w in ("mid", "cell"):
        for n, v in out[w]["nodes"].items():
            if not (v.e.upper() <= v.t.upper() and v.o.upper() <= v.t.upper()):
                problems.append(f"{w} {n}: component exceeds total")
    return problems


def parity_identity_checks(cert, samples=None) -> list[str]:
    """C4 at e = 0 on the real kernels (a separate zero-drift synthetic certifier)."""
    from intervals import workprec
    viol = []
    cell = dict(CELL, left=["-1/1000"], right=["1/1000"], e0=["0"], rho=["1/1000"])
    with workprec(256):
        c0 = SyntheticGradedCert(cell, bits=256).prepare_synthetic(3)
        f = c0.P["F", 1, 0]
        fs = {(j, i): v for (i, j), v in f.items()}
        states = [(F(1, 4), F(1, 2)), (F(0), F(3)), (F(2), F(1)), (F(9, 2), F(0))]
        for kind in ("K", "J"):
            for i in range(4):
                a = c0.K(fs, i) if kind == "K" else c0.J(fs, i)
                b = c0.K(f, i) if kind == "K" else c0.J(f, i)
                sign = (-1) ** i if kind == "K" else (-1) ** (i + 1)
                allow = float((arb(40) * c0.sup["F", 1, 0] * c0.eps_zi(max(i, 1))).upper())
                for p, m in states:
                    br = "lo" if p + m <= 1 else "hi"
                    lhs = bi_eval(getattr(a, br), exact(p), exact(m))
                    rhs = bi_eval(getattr(b, br), exact(m), exact(p)) * arb(sign)
                    gap = abs(float(lhs.mid()) - float(rhs.mid())) - float(lhs.rad()) - float(rhs.rad())
                    if gap > 2 * allow + 1e-12:
                        viol.append(f"{kind}_{i} parity gap {gap:.3e} at ({p},{m})")
    return viol


def candidate_parity_checks(gr, cert) -> list[str]:
    """C6: graded candidate suprema (gr.graded_sup) dominate the float even / odd parts of the candidate payload at every
    reachable state (only candidates whose parity ranges the wiring actually computed)."""
    import rung3_engine as R1E
    cache = cert.__dict__.get("_parity_range_cache", {})
    viol = []
    for key in sorted(cert.payloads, key=repr):
        if ("cand",) + tuple(key) not in cache:
            continue
        v = gr.graded_sup(cert, key)
        be, bo = float(R1E.fraction_of(v.e.abs_upper())), float(R1E.fraction_of(v.o.abs_upper()))
        pay = cert.payloads[key]
        for p, m in reachable_states():
            a, b = cheb(pay, p, m), cheb(pay, m, p)
            if abs(a + b) / 2 > be + FLOAT_TOL:
                viol.append(f"cand {key} even {abs(a + b) / 2:.3e} > {be:.3e} at {p},{m}")
            if abs(a - b) / 2 > bo + FLOAT_TOL:
                viol.append(f"cand {key} odd {abs(a - b) / 2:.3e} > {bo:.3e} at {p},{m}")
    return viol


def leibniz_checks(gr, cert, residuals) -> list[str]:
    """C7 (structural): every operator-residual envelope term list equals the generic rule. For an order-n equation
    X^(n) = sum_(i=0..n) C(n,i) T_i Y^(n-i) + source with e-independent candidates, d/de of the residual is
    -sum_(i=0..n) C(n,i) T_(i+1) Y^(n-i)  (T = K for h, W, F; T = J for S)."""
    viol = []
    fams = ("F", "D", "H", "G")
    for name in residuals:
        if name.startswith(("h_1:", "S_0:", "Sclosed")):
            continue
        if name.startswith(("h_", "S_", "W_")):
            head, k = name.split(":")
            n = int(k)
            if head.startswith("h_"):
                T, Y = "K", (lambda q, j=int(head[2:]): ("h", j - 1, q))
            elif head.startswith("S_"):
                T, Y = "J", (lambda q, r=int(head[2:]): ("h", r, q))
            else:
                r, j = map(int, head[2:].split("_"))
                T, Y = "K", (lambda q, r=r, j=j: ("W", (r, j - 1), q))
        else:
            head, r = name.split("_")
            n = {"F": 0, "dF": 1, "H": 2, "G": 3}[head]
            T, Y = "K", (lambda q, r=int(r): (fams[q], r, 0))
        expected = sorted((comb(n, i), T, i + 1, Y(n - i)) for i in range(n + 1))
        kind, got = gr.envelope_terms(cert, name)
        if kind != "ops" or sorted(got) != expected:
            viol.append(f"{name}: envelope terms {got} != Leibniz {expected}")
    return viol
