"""R2 selected method: sigma-GRADED (parity-block) certified error propagation, orders 0..3, midpoint and whole cell.

Detector-agnostic, in Arb. It REPLACES the scalar error cascade of R1 (`rung3_engine` plus the frozen order 0..2 DAG)
by a cascade on 3-vectors  v = (e, o, t):

    e >= ||P_e err||,   o >= ||P_o err||,   t >= ||err||,     P_e = (I + sigma)/2,  P_o = (I - sigma)/2

where sigma is an isometric involution of the state space that fixes the evaluation state x0 and satisfies, AT e = 0,

    sigma K_i(0) = (-1)^i K_i(0) sigma,       sigma J_i(0) = (-1)^(i+1) J_i(0) sigma.

(CUSUM: sigma(p, m) = (m, p), x0 = (0, 0); proof in ../R2_DESIGN.md section 3.)

Inputs (radius-zero certified upper bounds unless stated)
    C                 >= sup_(e in cell) ||(I - K_e)^-1||               (the existing scalar certificate)
    C_e0, C_o0        >= ||(I - K_0)^-1 restricted to even / odd||      (C_o0 is the NEW operator certificate)
    k[i], j[i]        >= sup_(e in cell) ||K_i||, ||J_i||, i = 0..5
    k_hull, j_hull    >= sup over hull({0} U cell) of ||K_i||, ||J_i||, i = 0..5  (leakage and perturbation integrate
                         from 0, so they need norms on the hull; for a cell whose left endpoint is 0 they equal k, j)
    eta_mid           >= |e0|;  eta_cell >= max |e| over the cell
    res[name]         {"mid": (e, o, t), "cell": (e, o, t)}  graded certified residual / leaf bounds; a backend forms
                      "cell" = "mid" + rho * graded_env(...) (equations) or rho * graded_true_sup(...) (closed leaves)
                      names: h_1:k S_0:k Sclosed_k (leaves), h_j:k S_r:k W_r_j:k F_r:n (equations), k, n <= 3
    origin            candidate values at x0 (only for an export; omitted in radius-only forecast mode)

Rules (each a bound on a distinct term of an exact identity)
    operator  ||P_x K_i(e) P_y|| <= k_i            if the parity of K_i(0) maps y to x
                                <= eta k_(i+1)      otherwise   (K_i(e) - K_i(0), mean value; K_i(0) vanishes there)
              J_i likewise with parity (-1)^(i+1).
    resolvent A(e) = A0 - Delta, A0 = I - K_0 parity-diagonal, ||P_x Delta P_x|| <= eta^2 k_2 / 2  (K_1(0) swaps
              parity), ||P_x Delta P_y|| <= eta k_1 (x != y).  With M = diag(C_e0, C_o0) [[a, b], [b, a]],
              a = eta^2 k_2/2, b = eta k_1: if rho(M) < 1 (certified: 1 - M_xx > 0, det > 0) then the block norm
              matrix of A(e)^-1 is <= (I - M)^-1 diag(C_e0, C_o0), entrywise; always capped by C. Else scalar C.
    node      h_j:k = res + sum_i C(k,i) K_i h_(j-1):(k-i);  S_r:k = res + sum_i C(k,i) J_i h_r:(k-i)
              F_r:n = A^-1 [ res + sum_(i>=1) C(n,i) K_i F_r:(n-i) + src ],  src = Sclosed_n (r = 0) | S_r:n
              W_r_j:k = res + sum_(i=0..k) C(k,i) K_i W_r_(j-1):(k-i),  W_r_0 = S_r
    vector    after every step  t <- min(t, e + o),  e <- min(e, t),  o <- min(o, t)
    export    the error at the sigma-fixed x0 equals the EVEN part of the error at x0, so the radius uses e
              (t when parity is disabled): rad = sum |c| e(node)

`parity=False` reproduces the scalar R1 cascade exactly (every component = the scalar value): that is the
"current generic resolvent enclosure" baseline, run by the same code.
"""
from __future__ import annotations

import sys
from math import comb
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
R1_CODE = NS.parents[0] / "p5y_k5_cusum_order3_real_producer/code"
if str(R1_CODE) not in sys.path:
    sys.path.append(str(R1_CODE))

from flint import arb  # noqa: E402

import rung3_engine as R1E  # noqa: E402  (R1, frozen; helpers only)

ProducerRefusal = R1E.ProducerRefusal
M_VALUES = R1E.M_VALUES
W_INDICES = R1E.W_INDICES
GRADED_SCHEMA = "rebaseguard.p5y.k5.order3-r2.graded-dag.v1"


def _up(x, what):
    return R1E._up(x, what)


class V:
    """(e, o, t) certified bounds; every constructor normalizes."""

    __slots__ = ("e", "o", "t")

    def __init__(self, e, o, t):
        t = _up(t, "t")
        e, o = _up(e, "e"), _up(o, "o")
        s = _up(e + o, "e+o")
        t = t if t.upper() <= s.upper() else s
        self.e = e if e.upper() <= t.upper() else t
        self.o = o if o.upper() <= t.upper() else t
        self.t = t

    @staticmethod
    def scalar(x):
        return V(x, x, x)

    def __add__(self, w):
        return V(self.e + w.e, self.o + w.o, self.t + w.t)

    def scale(self, c):
        c = arb(c)
        return V(c * self.e, c * self.o, c * self.t)


def resolvent_block(C, Ce0, Co0, k1, k2, eta, parity: bool):
    C = _up(C, "C")
    if not parity:
        return {"ee": C, "eo": C, "oe": C, "oo": C, "mode": "scalar"}
    a = _up(eta * eta * k2 / arb(2), "a")
    b = _up(eta * k1, "b")
    M = {"ee": Ce0 * a, "eo": Ce0 * b, "oe": Co0 * b, "oo": Co0 * a}
    d1, d2 = arb(1) - M["ee"], arb(1) - M["oo"]
    det = d1 * d2 - M["eo"] * M["oe"]
    if not (d1.lower() > 0 and d2.lower() > 0 and det.lower() > 0):
        return {"ee": C, "eo": C, "oe": C, "oo": C, "mode": "scalar_fallback"}
    inv = {"ee": d2 / det, "eo": M["eo"] / det, "oe": M["oe"] / det, "oo": d1 / det}
    out = {"ee": inv["ee"] * Ce0, "eo": inv["eo"] * Co0, "oe": inv["oe"] * Ce0, "oo": inv["oo"] * Co0}
    out = {key: _min(_up(val, "R"), C) for key, val in out.items()}
    out["mode"] = "graded"
    return out


def _min(a, b):
    return a if a.upper() <= b.upper() else b


def apply_op(norms, hull, i, v: V, eta, flip_base: int, parity: bool) -> V:
    """Bound of K_i(e) err (flip_base 0) or J_i(e) err (flip_base 1)."""
    kn = _up(norms[i], "norm")
    if not parity:
        return V(kn * v.t, kn * v.t, kn * v.t)
    leak = _up(eta * hull[i + 1], "leak")
    if (i + flip_base) % 2 == 0:       # parity preserving at e = 0
        return V(kn * v.e + leak * v.o, leak * v.e + kn * v.o, kn * v.t)
    return V(leak * v.e + kn * v.o, kn * v.e + leak * v.o, kn * v.t)


def graded_env(terms, k, j, k_hull, j_hull, eta) -> V:
    """Certified (e, o, t) bound of sup_cell ||d_e res|| for a residual whose e-derivative is
    - sum coef * Op_(order)(e) Xhat, candidates constant in e.  terms: (coef, "K"|"J", order, sup-vector of Xhat),
    the sup-vector being (||P_e Xhat||, ||P_o Xhat||, ||Xhat||). Parity leakage uses eta * norm_(order+1) on the hull."""
    acc = V(arb(0), arb(0), arb(0))
    for coef, fam, order, sv in terms:
        norms, hull, base = (k, k_hull, 0) if fam == "K" else (j, j_hull, 1)
        acc = acc + apply_op(norms, hull, order, sv, eta, base, True).scale(coef)
    return acc


def graded_true_sup(parity_at_0: int, T_n, T_n1, eta) -> V:
    """(e, o, t) bound of sup_cell ||X^(n)|| for a TRUE object whose n-th derivative has parity (+1 even, -1 odd) at
    e = 0: the wrong-parity part vanishes at 0 and moves at most eta * sup ||X^(n+1)|| (hull)."""
    right, wrong = _up(T_n, "T"), _up(eta * T_n1, "T")
    return V(right, wrong, right) if parity_at_0 == 1 else V(wrong, right, right)


def apply_res(R, v: V, C) -> V:
    return V(R["ee"] * v.e + R["eo"] * v.o, R["oe"] * v.e + R["oo"] * v.o, _up(C, "C") * v.t)


def _vec(triple, what):
    e, o, t = triple
    return V(e, o, t)


def propagate(inp: dict, which: str, *, parity: bool) -> dict:
    """The full graded DAG at the midpoint (which='mid') or over the whole cell (which='cell')."""
    k, jn, kh, jh = inp["k"], inp["j"], inp["k_hull"], inp["j_hull"]
    eta = _up(inp["eta_mid"] if which == "mid" else inp["eta_cell"], "eta")
    C = inp["C"]
    R = resolvent_block(C, _up(inp["C_e0"], "C_e0"), _up(inp["C_o0"], "C_o0"), _up(kh[1], "k1"), _up(kh[2], "k2"),
                        eta, parity)
    res = inp["res"]
    caps = inp.get("scalar_caps", {}).get(which, {})
    N: dict = {}

    def r(name):
        return _vec(res[name][which], name)

    def put(node, v):
        if node in caps:
            c = _up(caps[node], "cap")
            v = V(_min(v.e, c), _min(v.o, c), _min(v.t, c))
        N[node] = v
        return v

    for kk in range(4):
        put(f"h:1:{kk}", r(f"h_1:{kk}"))
    for j in range(2, 5):
        for kk in range(4):
            acc = r(f"h_{j}:{kk}")
            for i in range(kk + 1):
                acc = acc + apply_op(k, kh, i, N[f"h:{j - 1}:{kk - i}"], eta, 0, parity).scale(comb(kk, i))
            put(f"h:{j}:{kk}", acc)
    for kk in range(4):
        put(f"Sclosed:{kk}", r(f"Sclosed_{kk}"))
        put(f"S:0:{kk}", r(f"S_0:{kk}"))
    for rr in range(1, 5):
        for kk in range(4):
            acc = r(f"S_{rr}:{kk}")
            for i in range(kk + 1):
                acc = acc + apply_op(jn, jh, i, N[f"h:{rr}:{kk - i}"], eta, 1, parity).scale(comb(kk, i))
            put(f"S:{rr}:{kk}", acc)
    for rr in range(5):
        for n in range(4):
            acc = r(f"F_{rr}:{n}")
            for i in range(1, n + 1):
                acc = acc + apply_op(k, kh, i, N[f"F:{rr}:{n - i}"], eta, 0, parity).scale(comb(n, i))
            acc = acc + (N[f"Sclosed:{n}"] if rr == 0 else N[f"S:{rr}:{n}"])
            put(f"F:{rr}:{n}", apply_res(R, acc, C))
    for rr in range(4):
        for kk in range(4):
            N[f"W:{rr}:0:{kk}"] = N[f"S:{rr}:{kk}"]
    for (rr, j) in W_INDICES:
        for kk in range(4):
            acc = r(f"W_{rr}_{j}:{kk}")
            for i in range(kk + 1):
                acc = acc + apply_op(k, kh, i, N[f"W:{rr}:{j - 1}:{kk - i}"], eta, 0, parity).scale(comb(kk, i))
            put(f"W:{rr}:{j}:{kk}", acc)
    return {"nodes": N, "resolvent": R}


def radii(nodes: dict, *, parity: bool, order: int = 3) -> dict:
    out = {}
    for m in M_VALUES:
        rad = arb(0)
        for kind, rr, j, c in R1E.coefficients(m):
            v = nodes[f"F:{rr}:{order}"] if kind == "F" else nodes[f"W:{rr}:{j}:{order}"]
            rad = rad + R1E.exact(abs(c)) * (v.e if parity else v.t)
        out[m] = _up(rad, "radius")
    return out


def certify_graded(inp: dict, *, bits: int = R1E.PRODUCTION_BITS, parity: bool = True) -> dict:
    with R1E.precision(bits):
        for key in ("C", "C_e0", "C_o0", "k", "j", "k_hull", "j_hull", "eta_mid", "eta_cell", "res"):
            if key not in inp:
                raise ProducerRefusal(f"missing input {key}")
        if not inp.get("x0_sigma_fixed", False):
            raise ProducerRefusal("the evaluation state must be sigma-fixed")
        mid = propagate(inp, "mid", parity=parity)
        cell = propagate(inp, "cell", parity=parity)
        rad_mid, rad_cell = radii(mid["nodes"], parity=parity), radii(cell["nodes"], parity=parity)
        out = {"schema": GRADED_SCHEMA, "parity": parity, "bits": bits, "mid": mid, "cell": cell,
               "rad_mid": rad_mid, "rad_cell": rad_cell, "m": {}}
        if "origin" in inp:
            for m in M_VALUES:
                centre = arb(0)
                for kind, rr, j, c in R1E.coefficients(m):
                    o = inp["origin"][("G", rr)] if kind == "F" else inp["origin"][("W", (rr, j))]
                    centre = centre + R1E._finite(o, "origin") * R1E.exact(c)
                lo, hi = R1E.ball_fractions(R1E._finite(centre, "centre"))
                rm, rc = R1E.fraction_of(rad_mid[m]), R1E.fraction_of(rad_cell[m])
                out["m"][m] = {"R3_mid": (lo - rm, hi + rm), "R3_cell": (lo - rc, hi + rc)}
        return out
