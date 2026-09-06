"""PHASE 8: the frozen collocation grid carried one derivative order further.

WHY
---
The reviewed Layer 1 builds the discrete operators through order two, because
the frozen obligation set stops at the curvature equation:

    K   : phi(y)            Kz   : z phi(y)
    dK  : -y phi(y)         dKz  : -y z phi(y)
    ddK : (y^2-1) phi(y)    ddKz : (y^2-1) z phi(y)

Those weights are exactly `phi^(i)(y)/phi(y) = (-1)^i He_i(y)` for i = 0,1,2,
since `He_0 = 1`, `He_1 = y`, `He_2 = y^2 - 1`. This module continues the same
sequence at i = 3, with `He_3(y) = y^3 - 3y`:

    dddK : -(y^3-3y) phi(y)   dddKz : -(y^3-3y) z phi(y)

and the third derivative of the closed-form source, `phi'''(t) = -He_3(t) phi(t)`:

    S_0^(3) = phi'''(u+e) - phi'''(l+e)

NOTHING ELSE CHANGES: same frozen degree, same frozen quadrature, same frozen
nodes, same barycentric basis, same reachable window, same drift. The grid, the
weights and the basis functions are taken from the reviewed module and are not
re-derived here -- only the one additional Hermite weight is new.

WHAT IT IS FOR
--------------
These values are CANDIDATES ONLY. Nothing here is certified: every number this
module produces is later either (a) certified in Arb against its defining frozen
equation, or (b) used only as the argument of an operator whose certified
enclosure is computed in Arb. Layer 1 is float by design; it proposes, Layer 2
disposes.
"""
from __future__ import annotations

import math
from math import comb

import numpy as np

import ancestry                                                 # noqa: F401

import cusum_layer1 as L1                                       # noqa: E402

# The frozen Hermite weight sequence, continued one order.
HERMITE_WEIGHT_ORDER_3 = "phi'''(y)/phi(y) = -He_3(y) = -(y^3 - 3y)"


def _he3(y: float) -> float:
    return y * y * y - 3.0 * y


def collocation_order3(drift: float, *, degree: int = L1.DEGREE,
                       quad: int = L1.QUADRATURE) -> dict:
    """`dddK`, `dddKz` and `d3S0` on the frozen grid, at this cell's drift."""
    n = degree + 1
    x = np.cos(np.pi * np.arange(n) / degree)
    nodes = 0.5 * L1.H_FROZEN * (1.0 - x)
    bary = L1._barycentric_weights(degree)
    gn, gw = np.polynomial.legendre.leggauss(quad)
    dim = n * n
    dddK = np.zeros((dim, dim))
    dddKz = np.zeros((dim, dim))
    d3S0 = np.zeros(dim)
    norm = math.sqrt(2.0 * math.pi)

    for i, p in enumerate(nodes):
        for j, m in enumerate(nodes):
            row = i * n + j
            ell, upper = m - L1.C_CUSUM, L1.C_CUSUM - p
            mid, rad = 0.5 * (ell + upper), 0.5 * (upper - ell)
            for node, weight in zip(gn, gw, strict=True):
                z = mid + rad * node
                y = z + drift
                dens = rad * weight * math.exp(-0.5 * y * y) / norm
                wp = L1._basis(max(0.0, p + z - L1.K_FROZEN), nodes, bary)
                wm = L1._basis(max(0.0, m - z - L1.K_FROZEN), nodes, bary)
                interp = np.outer(wp, wm).ravel()
                w3 = -_he3(y)
                dddK[row] += w3 * dens * interp
                dddKz[row] += w3 * z * dens * interp
            au, al = upper + drift, ell + drift
            pu = math.exp(-0.5 * au * au) / norm
            pl = math.exp(-0.5 * al * al) / norm
            d3S0[row] = -_he3(au) * pu + _he3(al) * pl
    return {"dddK": dddK, "dddKz": dddKz, "d3S0": d3S0,
            "weight": HERMITE_WEIGHT_ORDER_3, "drift": drift,
            "nodes": nodes, "n": n, "dim": dim}


def objects_order3(co: dict, obj: dict, co3: dict) -> dict:
    """Order-3 candidate values from the frozen recursions, one order further.

        h_1^(3) = -S_0^(2)                                  (closed form)
        h_j^(3) = sum_(i=0..3) C(3,i) K_i h_(j-1)^(3-i)
        S_0^(3) = phi'''(u+e) - phi'''(l+e)                 (closed form)
        S_r^(3) = sum_(i=0..3) C(3,i) J_i h_r^(3-i)
        W_(r,0)^(3) = S_r^(3)
        W_(r,j)^(3) = sum_(i=0..3) C(3,i) K_i W_(r,j-1)^(3-i)

    `J_i = Kz_i + e K_i + i K_(i-1)` is the frozen Leibniz expansion of `J_e`,
    continued to i = 3 with no new structure.
    """
    e = co["drift"]
    Kop = {0: co["K"], 1: co["dK"], 2: co["ddK"], 3: co3["dddK"]}
    Kzop = {0: co["Kz"], 1: co["dKz"], 2: co["ddKz"], 3: co3["dddKz"]}

    def J(i: int, v):
        out = Kzop[i] @ v + e * (Kop[i] @ v)
        if i >= 1:
            out = out + i * (Kop[i - 1] @ v)
        return out

    h = {(j, k): obj["h"][j, k] for j in range(1, 5) for k in range(3)}
    h[1, 3] = -obj["S"][0, 2]
    for j in range(2, 5):
        h[j, 3] = sum(comb(3, i) * (Kop[i] @ h[j - 1, 3 - i]) for i in range(4))

    S = {(r, k): obj["S"][r, k] for r in range(5) for k in range(3)}
    S[0, 3] = co3["d3S0"]
    for r in range(1, 5):
        S[r, 3] = sum(comb(3, i) * J(i, h[r, 3 - i]) for i in range(4))

    W = {(r, j, k): obj["W"][r, j, k]
         for (r, j) in [(a, b) for a in range(4) for b in range(4 - a)]
         for k in range(3)}
    for r in range(4):
        W[r, 0, 3] = S[r, 3]
        for j in range(1, 4 - r):
            W[r, j, 3] = sum(comb(3, i) * (Kop[i] @ W[r, j - 1, 3 - i])
                             for i in range(4))
    return {"h3": {j: h[j, 3] for j in range(1, 5)},
            "S3": {r: S[r, 3] for r in range(5)},
            "W3": {(r, j): W[r, j, 3]
                   for r in range(4) for j in range(4 - r)}}
