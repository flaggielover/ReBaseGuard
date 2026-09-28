"""Stream D, D5: NON-RIGOROUS float cross-check of Lambda(e) = E_a[tau] by value iteration of U = 1 + K_e U.

Completely different method from vd_verify.py: floats (math.erf / math.exp), no certificate involved in the solve.
Discretisation: nodes (i h, j h) of the lattice with i + j <= 4N plus the axis nodes up to 5 (h = 1/N); U is the P1
(linear) interpolant along the lines the images move on (the two axes and the anti-diagonal t' = t - 1, which is a
lattice line because t = (i + j) h).  The transition weights of each hat function are integrated exactly against the
Gaussian (closed forms in Phi and phi); the atom window puts its mass on the node (0, 0).  Gauss-Seidel value
iteration until the max update is < tol; Richardson extrapolation over N assumes O(h^2).
"""
from __future__ import annotations

import importlib.util
import json
import math
import sys
import time
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parents[1]


def _load_quarantine():
    spec = importlib.util.spec_from_file_location("c308_quarantine", NS / "code" / "c308_quarantine.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


Q = _load_quarantine()
Q.install_import_guard()

K = 0.5
C = 5.5
S2PI = math.sqrt(2 * math.pi)


def Phi(x: float) -> float:
    return 0.5 * math.erfc(-x / math.sqrt(2.0))


def phi(x: float) -> float:
    return math.exp(-0.5 * x * x) / S2PI


def build(N: int, e: float):
    h = 1.0 / N
    nodes = {}
    for i in range(4 * N + 1):
        for j in range(4 * N - i + 1):
            nodes[(i, j)] = len(nodes)
    for i in range(4 * N + 1, 5 * N + 1):
        nodes[(i, 0)] = len(nodes)
    for j in range(4 * N + 1, 5 * N + 1):
        nodes[(0, j)] = len(nodes)
    rows = [None] * len(nodes)

    def hat_segments(acc, node_of, lo_k, hi_k, dens_shift, sign):
        """int over coordinate c in [lo_k h, hi_k h] of (P1 interpolant) * phi(sign*(c - dens_shift)) dc."""
        for k in range(lo_k, hi_k):
            c0, c1 = k * h, (k + 1) * h
            v0, v1 = sign * (c0 - dens_shift), sign * (c1 - dens_shift)
            a, b = (v0, v1) if v0 < v1 else (v1, v0)
            I0 = Phi(b) - Phi(a)
            # int c phi(sign (c - s)) dc: c = s + sign v, dc = |dv|  ->  s I0 + sign * int v phi dv
            I1 = dens_shift * I0 + sign * (phi(a) - phi(b))
            w0 = (c1 * I0 - I1) / h
            w1 = (I1 - c0 * I0) / h
            n0, n1 = node_of(k), node_of(k + 1)
            acc[n0] = acc.get(n0, 0.0) + w0
            acc[n1] = acc.get(n1, 0.0) + w1

    for (i, j), idx in nodes.items():
        p, m = i * h, j * h
        kk = i + j
        acc: dict = {}
        a_m = m - K + e            # m' = a_m - u   ->  u = a_m - m'  : density phi(a_m - m') = phi(-(m' - a_m))
        a_p = p - K - e            # p' = a_p + u   ->  density phi(p' - a_p)
        low = 0 if kk <= N else kk - N
        hat_segments(acc, lambda k: nodes[(0, k)], low, 5 * N, a_m, -1.0)          # A on the m-axis
        hat_segments(acc, lambda k: nodes[(k, 0)], low, 5 * N, a_p, 1.0)           # C on the p-axis
        if kk <= N:
            mass = Phi(K - p + e) - Phi(m - K + e)
            acc[nodes[(0, 0)]] = acc.get(nodes[(0, 0)], 0.0) + mass                # atom window
        else:
            d = kk - N
            hat_segments(acc, lambda k: nodes[(k, d - k)], 0, d, a_p, 1.0)          # B on the anti-diagonal
        rows[idx] = list(acc.items())
    return nodes, rows


def solve(N: int, e: float, tol: float = 1e-11, max_sweeps: int = 200000):
    nodes, rows = build(N, e)
    U = [1.0] * len(nodes)
    sweeps = 0
    t0 = time.time()
    while sweeps < max_sweeps:
        sweeps += 1
        dmax = 0.0
        for idx, row in enumerate(rows):
            s = 1.0
            for jdx, w in row:
                s += w * U[jdx]
            d = abs(s - U[idx])
            if d > dmax:
                dmax = d
            U[idx] = s
        if dmax < tol:
            break
    return {"N": N, "U_atom": U[nodes[(0, 0)]], "sweeps": sweeps, "last_update": dmax,
            "seconds": round(time.time() - t0, 1), "nodes": len(nodes), "_U": U, "_nodes": nodes}


def run(e: F, Ns=(10, 20)) -> dict:
    Q.guard_drift(e)
    out = {"drift": f"{e.numerator}/{e.denominator}", "method": "float P1 Galerkin-collocation + Gauss-Seidel",
           "levels": []}
    res = []
    for N in Ns:
        r = solve(N, float(e))
        res.append(r)
        out["levels"].append({k: v for k, v in r.items() if not k.startswith("_")})
    if len(res) >= 2:
        a, b = res[-2]["U_atom"], res[-1]["U_atom"]
        ratio = Ns[-1] / Ns[-2]
        out["richardson_h2"] = b + (b - a) / (ratio ** 2 - 1)
    return out, res


def run_only(e_str: str) -> dict:
    out, _ = run(F(e_str))
    return out


if __name__ == "__main__":
    import multiprocessing as mp
    drifts = [F(x) for x in sys.argv[1:]] or [F(3), F(1), F(7, 2), F(1, 2)]
    for e in drifts:
        Q.guard_drift(e)
    with mp.get_context("spawn").Pool(min(3, len(drifts))) as pool:
        outs = pool.map(run_only, [str(e) for e in drifts])
    print(json.dumps(outs, indent=1))
