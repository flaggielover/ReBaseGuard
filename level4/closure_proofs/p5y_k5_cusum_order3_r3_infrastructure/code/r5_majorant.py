"""R3 Parts F/G: first-cell Strategy B (point R'''(0) + evenness transport) and its certified R^(5) majorant.

LEMMA (evenness transport). Let R be odd and C^5 on [0, x1] (CUSUM: P5-T3 oddness, P5X L5 real-analyticity; the
manufactured sigma-systems satisfy R(-e) = -R(e) exactly). Then R''' is even, R'''' is odd, R''''(0) = 0, and for
every e in [0, x1]
    R'''(e) = R'''(0) + e R''''(0) + int_0^e (e - t) R^(5)(t) dt  >=  R'''(0) - (e^2 / 2) sup_[0,e] |R^(5)|
            >=  lo(R'''(0)) - (x1^2 / 2) M5,        M5 >= sup_[0,x1] |R^(5)|.
So  L_1^B := lo(I_0) - (x1^2/2) M5  is a valid K5-B first-cell object whenever I_0 is a certified enclosure of R'''(0).
(Upper side symmetric: U_1^B := hi(I_0) + (x1^2/2) M5.)

M5 (this module): a certified ABSOLUTE majorant, no sign. R^(5)_m(e)(x0) = sum c X^(5)(e)(x0), and at the sigma-fixed
x0 only the even part survives, so |R^(5)_m(e)| <= sum |c| sup_e ||P_e X^(5)(e)||. A graded tower of TRUE objects on
the hull [0, x1], using the same graded operator / resolvent rules as graded_dag (R2) with the certified C_e0, C_o0:
    h_1^(n)   graded_true_sup(parity (-1)^n, sup||h_1^(n)||, sup||h_1^(n+1)||)  with h_1^(0) in [0,1], h_1^(n) = -S_0^(n-1)
    S_0^(n)   graded_true_sup(parity (-1)^(n+1), sup||S_0^(n)||, sup||S_0^(n+1)||)
    h_j^(n) = sum_i C(n,i) K_i h_(j-1)^(n-i)        S_r^(n) = sum_i C(n,i) J_i h_r^(n-i)
    F_r^(n) = A(e)^-1 [ sum_(i>=1) C(n,i) K_i F_r^(n-i) + S_r^(n) ]          W_(r,j)^(n) = sum_i C(n,i) K_i W_(r,j-1)^(n-i)
    anchor    optional (n <= 3): componentwise min with graded sup(candidate) + graded whole-cell error (valid bound)
"""
from __future__ import annotations

import sys
from fractions import Fraction as F
from math import comb
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CP = NS.parents[0]
for _p in (str(CP / "p5y_k5_cusum_order3_r2_repair/code"), str(CP / "p5y_k5_cusum_order3_real_producer/code")):
    if _p not in sys.path:
        sys.path.append(_p)

from flint import arb  # noqa: E402

import graded_dag as G  # noqa: E402
import rung3_engine as R1E  # noqa: E402

MAX_N = 5


def _minv(a: "G.V", b: "G.V") -> "G.V":
    m = lambda x, y: x if x.upper() <= y.upper() else y
    return G.V(m(a.e, b.e), m(a.o, b.o), m(a.t, b.t))


def true_tower(inp: dict, *, parity: bool = True) -> dict:
    """inp: C, C_e0, C_o0, k, j (hull norms 0..6), eta (= x1), S0 {n: sup||S_0^(n)||, n = 0..6}, anchors {node: V}."""
    k, j, eta, C = inp["k"], inp["j"], inp["eta"], inp["C"]
    R = G.resolvent_block(C, inp["C_e0"], inp["C_o0"], k[1], k[2], eta, parity)
    s0 = inp["S0"]
    anchors = inp.get("anchors", {})
    T: dict = {}

    def put(node, v):
        if node in anchors:
            v = _minv(v, anchors[node])
        T[node] = v
        return v

    def gts(par, right, nxt):
        if not parity:
            return G.V(right, right, right)
        return G.graded_true_sup(par, right, nxt, eta)

    h1 = inp.get("h1")
    for n in range(MAX_N + 1):
        if h1 is None:                                        # CUSUM identity h_1^(n) = -S_0^(n-1), h_1 in [0,1]
            right, nxt = (arb(1) if n == 0 else s0[n - 1]), s0[n]
        else:                                                 # system without that identity: explicit leaf sups
            right, nxt = h1[n], h1[n + 1]
        put(f"h:1:{n}", gts((-1) ** n, right, nxt))
        put(f"S:0:{n}", gts((-1) ** (n + 1), s0[n], s0[n + 1]))
    for jj in range(2, 5):
        for n in range(MAX_N + 1):
            acc = G.V(arb(0), arb(0), arb(0))
            for i in range(n + 1):
                acc = acc + G.apply_op(k, k, i, T[f"h:{jj - 1}:{n - i}"], eta, 0, parity).scale(comb(n, i))
            put(f"h:{jj}:{n}", acc)
    for r in range(1, 5):
        for n in range(MAX_N + 1):
            acc = G.V(arb(0), arb(0), arb(0))
            for i in range(n + 1):
                acc = acc + G.apply_op(j, j, i, T[f"h:{r}:{n - i}"], eta, 1, parity).scale(comb(n, i))
            put(f"S:{r}:{n}", acc)
    for r in range(5):
        for n in range(MAX_N + 1):
            acc = T[f"S:{r}:{n}"]
            for i in range(1, n + 1):
                acc = acc + G.apply_op(k, k, i, T[f"F:{r}:{n - i}"], eta, 0, parity).scale(comb(n, i))
            put(f"F:{r}:{n}", G.apply_res(R, acc, C))
    for r in range(4):
        for n in range(MAX_N + 1):
            T[f"W:{r}:0:{n}"] = T[f"S:{r}:{n}"]
    for (r, jj) in G.W_INDICES:
        for n in range(MAX_N + 1):
            acc = G.V(arb(0), arb(0), arb(0))
            for i in range(n + 1):
                acc = acc + G.apply_op(k, k, i, T[f"W:{r}:{jj - 1}:{n - i}"], eta, 0, parity).scale(comb(n, i))
            put(f"W:{r}:{jj}:{n}", acc)
    return {"towers": T, "resolvent_mode": R["mode"]}


def m5(towers: dict, *, parity: bool = True, order: int = MAX_N) -> dict:
    out = {}
    for m in G.M_VALUES:
        acc = arb(0)
        for kind, r, jj, c in R1E.coefficients(m):
            v = towers[f"F:{r}:{order}"] if kind == "F" else towers[f"W:{r}:{jj}:{order}"]
            acc = acc + R1E.exact(abs(c)) * (v.e if parity else v.t)
        out[m] = acc.abs_upper()
    return out


def strategy_b_bounds(point_interval: tuple[F, F], x1: F, M5: arb) -> tuple[F, F]:
    """(L_1^B, U_1^B) from a certified point enclosure of R'''(0) and M5 >= sup_[0,x1] |R^(5)|."""
    pen = (x1 * x1 / 2) * R1E.fraction_of(M5.abs_upper())
    return point_interval[0] - pen, point_interval[1] + pen
