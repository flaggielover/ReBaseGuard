"""NON-CERTIFIED, OPERATOR-ONLY float diagnostic of the CUSUM kernel K_e across the K5 front.

FORECAST / DESIGN INPUT ONLY. No source term (h_1, S_r, reward), no candidate of any DAG object, no K1 record and no
value of R_(D,m) or of any derivative of R is formed. Only the survival kernel K_e, its atom split and scalar operator
functionals (expected run lengths, return probabilities, eigenvalues) are computed.

Objects, on the frozen collocation grid (tensor Chebyshev on [0, 5]^2, Gauss-Legendre in z, the R3 cut points):
    K_e        (K_e f)(p, m)   = int_{m-c}^{c-p} phi(z+e) f(max(0, p+z-k), max(0, m-z-k)) dz
    k_a        (k_a)(p, m)     = int_{m-k}^{k-p} phi(z+e) dz  (mass sent to the atom a = (0,0); 0 if the window is empty)
    Khat_e     K_e with the atom window removed, so K_e = Khat_e + k_a (x) delta_a exactly (rank one)
    C_T(e)     max_x (I - Khat_e)^-1 1 (x) = sup_x E_x[tau ^ T_a]           (taboo / atom-killed constant)
    p_e        ((I - Khat_e)^-1 k_a)(a) = P_a(T_a < tau)                    (return-before-alarm probability)
    D_e        1 - p_e                                                     (renewal defect)
    ARL(a)     ((I - K_e)^-1 1)(a), checked against (I - Khat)^-1 1 (a) / D_e (Sherman-Morrison at the atom)
    spectral   Perron eigenvalue, second eigenvalue, spectral radius of Khat, spectral projector norm,
               ||(I - K)^-1 (I - P)||_inf (spectral deflation), eigenvector condition number.
"""
from __future__ import annotations

import json
import math
import sys

import numpy as np

K_, H_, C_ = 0.5, 5.0, 5.5


def bary_rows(values, nodes, w):
    d = values[:, None] - nodes[None, :]
    ex = np.abs(d) < 2e-14
    d = np.where(ex, 1.0, d)
    t = w[None, :] / d
    t = t / t.sum(axis=1, keepdims=True)
    hit = ex.any(axis=1)
    if hit.any():
        t[hit] = ex[hit].astype(float)
    return t


def kernel_split(drift: float, degree: int = 12, quad: int = 400):
    n = degree + 1
    x = np.cos(np.pi * np.arange(n) / degree)
    nodes = 0.5 * H_ * (1.0 - x)
    w = (-1.0) ** np.arange(n)
    w[[0, -1]] *= 0.5
    gn, gw = np.polynomial.legendre.leggauss(quad)
    dim = n * n
    K = np.zeros((dim, dim))
    Kh = np.zeros((dim, dim))
    ka = np.zeros(dim)
    norm = math.sqrt(2 * math.pi)
    for i, p in enumerate(nodes):
        for j, m in enumerate(nodes):
            ell, upper = m - C_, C_ - p
            beta, alpha = m - K_, K_ - p
            cuts = sorted({ell, upper} | ({beta, alpha} if beta < alpha else set()))
            rowK = np.zeros((n, n))
            rowH = np.zeros((n, n))
            for a, b in zip(cuts[:-1], cuts[1:]):
                mid, rad = 0.5 * (a + b), 0.5 * (b - a)
                z = mid + rad * gn
                y = z + drift
                dens = rad * gw * np.exp(-0.5 * y * y) / norm
                wp = bary_rows(np.maximum(0.0, p + z - K_), nodes, w)
                wm = bary_rows(np.maximum(0.0, m - z - K_), nodes, w)
                piece = np.einsum("q,qa,qb->ab", dens, wp, wm)
                rowK += piece
                if not (beta < alpha and a >= beta - 1e-15 and b <= alpha + 1e-15):
                    rowH += piece
            if beta < alpha:
                ka[i * n + j] = 0.5 * (math.erf((alpha + drift) / math.sqrt(2)) - math.erf((beta + drift) / math.sqrt(2)))
            K[i * n + j] = rowK.ravel()
            Kh[i * n + j] = rowH.ravel()
    return K, Kh, ka, nodes, n


def diagnose(drift: float, degree: int = 12) -> dict:
    K, Kh, ka, nodes, n = kernel_split(drift, degree)
    dim = n * n
    I = np.eye(dim)
    a = 0                                   # node (0,0) is index 0 (nodes[0] = 0)
    ea = np.zeros(dim); ea[a] = 1.0
    one = np.ones(dim)
    inf = lambda M: float(np.abs(M).sum(axis=1).max())
    rank_one_defect = float(np.abs(K - Kh - np.outer(ka, ea)).max())
    Gh = np.linalg.inv(I - Kh)
    G = np.linalg.inv(I - K)
    taboo = Gh @ one
    h = Gh @ ka
    p_ret = float(h[a])
    D = 1.0 - p_ret
    arl = G @ one
    sm = Gh + np.outer(h, ea @ Gh) / D         # Sherman-Morrison at the atom
    # spectral data
    vals, vecs = np.linalg.eig(K)
    order = np.argsort(-np.abs(vals))
    lam = float(vals[order[0]].real)
    lam2 = complex(vals[order[1]])
    r = np.real(vecs[:, order[0]]); r = r / r[np.argmax(np.abs(r))]
    lv, lvec = np.linalg.eig(K.T)
    li = int(np.argmax(lv.real))
    l = np.real(lvec[:, li]); l = l / l.sum()
    P = np.outer(r, l) / float(l @ r)
    Q = I - P
    rho_Kh = float(np.max(np.abs(np.linalg.eigvals(Kh))))
    # sensitivity (eigenvalue condition number, 2-norm) and a Jordan-proximity check
    kappa_eig = float(np.linalg.norm(l) * np.linalg.norm(r) / abs(l @ r))
    renewal_lambda_check = None
    try:
        # the Perron root solves delta_a (lam - Khat)^-1 k_a = 1
        f = lambda z: float(ea @ np.linalg.solve(z * I - Kh, ka)) - 1.0
        lo_, hi_ = max(rho_Kh + 1e-9, 0.5), 1.0 + 1e-12
        for _ in range(80):
            mid = 0.5 * (lo_ + hi_)
            (lo_, hi_) = (mid, hi_) if f(mid) > 0 else (lo_, mid)
        renewal_lambda_check = 0.5 * (lo_ + hi_)
    except np.linalg.LinAlgError:
        pass
    arg = int(np.argmax(taboo))
    return {
        "e": drift, "degree": degree, "dim": dim,
        "rank_one_split_defect_max": rank_one_defect,
        "taboo_C_T": float(taboo.max()), "taboo_argmax_state": [float(nodes[arg // n]), float(nodes[arg % n])],
        "taboo_at_atom": float(taboo[a]),
        "p_return": p_ret, "D_renewal_defect": D, "one_over_D": 1.0 / D,
        "ARL_atom": float(arl[a]), "ARL_sup": float(arl.max()), "resolvent_inf": inf(G),
        "sherman_morrison_defect_inf": inf(sm - G),
        "ARL_atom_identity_defect": float(arl[a] - taboo[a] / D),
        "perron": lam, "gap": 1 - lam, "one_over_gap": 1 / (1 - lam),
        "renewal_root": renewal_lambda_check,
        "second_eig": [lam2.real, lam2.imag], "second_eig_abs": abs(lam2),
        "spectral_radius_Khat": rho_Kh,
        "spectral_projector_inf": inf(P), "eigvec_condition_2norm": kappa_eig,
        "spectral_deflated_resolvent_inf": inf(G @ Q),
        "resolvent_on_range_P_inf": inf(G @ P),
    }


def main():
    es = [float(t) for t in sys.argv[1].split(",")] if len(sys.argv) > 1 else [0.0, 0.0057, 0.0114, 0.0228, 0.05, 0.0964, 0.1135, 0.125]
    degs = [int(t) for t in sys.argv[2].split(",")] if len(sys.argv) > 2 else [12]
    out = {"schema": "rebaseguard.p5y.k5.perron-deflation.operator-float-diagnostic.v1", "certified": False,
           "use": "DESIGN / FORECAST INPUT ONLY (operator only; no source, no candidate, no R value)", "rows": []}
    for d in degs:
        for e in es:
            out["rows"].append(diagnose(e, d))
    json.dump(out, sys.stdout, indent=1)
    print()


if __name__ == "__main__":
    main()
