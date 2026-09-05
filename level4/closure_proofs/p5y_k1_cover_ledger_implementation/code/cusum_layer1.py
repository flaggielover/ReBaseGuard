"""Layer 1: NON-RIGOROUS float construction of the complete CUSUM raw-variable
DAG, extended to derivative order two.

Nothing in this module is evidence. It only produces candidate values that
Layer 2 rounds to exact dyadic Chebyshev polynomials and then certifies. A
candidate may be arbitrarily bad; the certificate is what bounds the truth.

The float grid, node placement, Chebyshev degree and quadrature order are the
FROZEN ones inherited from ra_certifier / p5y_k1_cusum_kernel. Nothing is
adapted, refined or tuned per cell: `DEGREE_ADAPTATION_ALLOWED` is false.

Objects built here (raw variable; the unknown is F = R itself):

    h_1 = 1 - K 1,            h_1' = -S_0,        h_1'' = -S_0'
    h_j^(k) = sum_i C(k,i) K_i h_(j-1)^(k-i)            j = 2..4
    S_0 = phi(u+e) - phi(l+e)                          closed form, all orders
    S_r^(k) = sum_i C(k,i) J_i h_r^(k-i)               r = 1..4
    F_r     = (I-K)^-1 S_r
    D_r     = (I-K)^-1 (K_1 F_r + S_r')
    H_r     = (I-K)^-1 (K_2 F_r + 2 K_1 D_r + S_r'')
    W_(r,0)^(k) = S_r^(k);  W_(r,j+1)^(k) = sum_i C(k,i) K_i W_(r,j)^(k-i)

with the operators, under e-free state limits,

    K_i  f = int f(q(x,z)) phi^(i)(z+e) dz
    Kz_i f = int f(q(x,z)) z phi^(i)(z+e) dz
    J_0 = Kz_0 + e K_0 ; J_1 = Kz_1 + K_0 + e K_1 ; J_2 = Kz_2 + 2 K_1 + e K_2

which is the exact Leibniz expansion of J_e = K_(z,e) + e K_e.
"""
from __future__ import annotations

import math
from math import comb

import numpy as np

# Frozen geometry (ra_certifier.K_FROZEN / H_FROZEN / DEGREE / QUADRATURE).
K_FROZEN = 0.5
H_FROZEN = 5.0
C_CUSUM = H_FROZEN + K_FROZEN                 # 11/2
DEGREE = 12
QUADRATURE = 400
SCALE_BITS = 50

# W indices actually required by the frozen all-m assembly: j >= 1 and r+j <= 3.
W_INDICES = tuple((r, j) for r in range(4) for j in range(1, 4 - r))


def _barycentric_weights(degree: int) -> np.ndarray:
    w = (-1.0) ** np.arange(degree + 1)
    w[[0, -1]] *= 0.5
    return w


def _basis(value: float, nodes: np.ndarray, weights: np.ndarray) -> np.ndarray:
    d = value - nodes
    exact = np.flatnonzero(np.abs(d) < 2e-14)
    if exact.size:
        out = np.zeros_like(nodes)
        out[exact[0]] = 1.0
        return out
    t = weights / d
    return t / np.sum(t)


def dyadic_candidate(values: np.ndarray, n: int, *, scale_bits: int = SCALE_BITS) -> dict:
    """Degree-12 exact-dyadic Chebyshev payload; numpy only, no scipy.

    Byte-identical to SpectralCandidate.to_chebyshev_dyadic for the frozen h;
    a focused test asserts that equality so this local copy cannot drift.
    """
    from numpy.polynomial.chebyshev import chebvander2d
    degree = n - 1
    x = np.cos(np.pi * np.arange(n) / degree)
    nodes = 0.5 * H_FROZEN * (1.0 - x)
    normalized = 2.0 * nodes / H_FROZEN - 1.0
    xx, yy = np.meshgrid(normalized, normalized, indexing="ij")
    vals = np.asarray(values, dtype=float).reshape(n, n)
    vander = chebvander2d(xx.ravel(), yy.ravel(), [degree, degree])
    coeff = np.linalg.solve(vander.reshape((vals.size, vals.size)),
                            vals.ravel()).reshape(vals.shape)
    scale = 1 << scale_bits
    return {"schema": "rebaseguard.chebyshev-candidate.v1", "degree": degree,
            "scale_bits": scale_bits, "h_num": int(round(H_FROZEN * 2)), "h_den": 2,
            "numerators": np.rint(coeff * scale).astype(np.int64).tolist()}


def collocation(drift: float, degree: int = DEGREE, quad: int = QUADRATURE) -> dict:
    """Frozen collocation grid and the six discrete operators through order two.

    Weight factors, with y = z + e:
        K   : phi(y)            Kz   : z phi(y)
        dK  : -y phi(y)         dKz  : -y z phi(y)
        ddK : (y^2-1) phi(y)    ddKz : (y^2-1) z phi(y)
    """
    n = degree + 1
    x = np.cos(np.pi * np.arange(n) / degree)
    nodes = 0.5 * H_FROZEN * (1.0 - x)
    bary = _barycentric_weights(degree)
    gn, gw = np.polynomial.legendre.leggauss(quad)
    dim = n * n
    K = np.zeros((dim, dim)); Kz = np.zeros((dim, dim))
    dK = np.zeros((dim, dim)); dKz = np.zeros((dim, dim))
    ddK = np.zeros((dim, dim)); ddKz = np.zeros((dim, dim))
    h1 = np.zeros(dim); S0 = np.zeros(dim); dS0 = np.zeros(dim); ddS0 = np.zeros(dim)
    norm = math.sqrt(2.0 * math.pi)

    def Phi(t):
        return 0.5 * (1.0 + math.erf(t / math.sqrt(2.0)))

    for i, p in enumerate(nodes):
        for j, m in enumerate(nodes):
            row = i * n + j
            ell, upper = m - C_CUSUM, C_CUSUM - p
            mid, rad = 0.5 * (ell + upper), 0.5 * (upper - ell)
            for node, weight in zip(gn, gw, strict=True):
                z = mid + rad * node
                y = z + drift
                dens = rad * weight * math.exp(-0.5 * y * y) / norm
                wp = _basis(max(0.0, p + z - K_FROZEN), nodes, bary)
                wm = _basis(max(0.0, m - z - K_FROZEN), nodes, bary)
                interp = np.outer(wp, wm).ravel()
                K[row] += dens * interp
                Kz[row] += z * dens * interp
                dK[row] += (-y) * dens * interp
                dKz[row] += (-y) * z * dens * interp
                ddK[row] += (y * y - 1.0) * dens * interp
                ddKz[row] += (y * y - 1.0) * z * dens * interp
            au, al = upper + drift, ell + drift
            pu = math.exp(-0.5 * au * au) / norm
            pl = math.exp(-0.5 * al * al) / norm
            h1[row] = 1.0 - Phi(au) + Phi(al)
            S0[row] = pu - pl
            dS0[row] = -au * pu + al * pl
            ddS0[row] = (au * au - 1.0) * pu - (al * al - 1.0) * pl
    return dict(nodes=nodes, n=n, K=K, Kz=Kz, dK=dK, dKz=dKz, ddK=ddK, ddKz=ddKz,
                h1=h1, S0=S0, dS0=dS0, ddS0=ddS0, drift=drift, dim=dim)


def build_objects(co: dict) -> dict:
    """The whole raw DAG at the collocation nodes, orders 0..2."""
    K, Kz, dK, dKz, ddK, ddKz = (co["K"], co["Kz"], co["dK"], co["dKz"],
                                 co["ddK"], co["ddKz"])
    e = co["drift"]
    Kop = {0: K, 1: dK, 2: ddK}

    def J(i, v):
        """J_i v = Kz_i v + e K_i v + i K_(i-1) v."""
        if i == 0:
            return Kz @ v + e * (K @ v)
        if i == 1:
            return dKz @ v + e * (dK @ v) + (K @ v)
        if i == 2:
            return ddKz @ v + e * (ddK @ v) + 2.0 * (dK @ v)
        raise ValueError("order > 2")

    # h objects, orders 0..2
    h = {(1, 0): co["h1"], (1, 1): -co["S0"], (1, 2): -co["dS0"]}
    for j in range(2, 5):
        for k in range(3):
            h[j, k] = sum(comb(k, i) * (Kop[i] @ h[j - 1, k - i]) for i in range(k + 1))

    # S objects, orders 0..2
    S = {(0, 0): co["S0"], (0, 1): co["dS0"], (0, 2): co["ddS0"]}
    for r in range(1, 5):
        for k in range(3):
            S[r, k] = sum(comb(k, i) * J(i, h[r, k - i]) for i in range(k + 1))

    op = np.eye(co["dim"]) - K
    F, D, H = {}, {}, {}
    for r in range(5):
        F[r] = np.linalg.solve(op, S[r, 0])
        D[r] = np.linalg.solve(op, dK @ F[r] + S[r, 1])
        H[r] = np.linalg.solve(op, ddK @ F[r] + 2.0 * (dK @ D[r]) + S[r, 2])

    # finite kernel powers W_(r,j) = K^j S_r, orders 0..2
    W = {}
    for r in range(4):
        for k in range(3):
            W[r, 0, k] = S[r, k]
        for j in range(1, 4 - r):
            for k in range(3):
                W[r, j, k] = sum(comb(k, i) * (Kop[i] @ W[r, j - 1, k - i])
                                 for i in range(k + 1))
    return {"h": h, "S": S, "F": F, "D": D, "H": H, "W": W,
            "cond": float(np.linalg.cond(op))}
