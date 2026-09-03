"""Non-binding high-accuracy numerical reference for h(x) = E_x[tau], two-sided SR.

Solves (I - K_e) h = 1 on the live region with h = 0 after alarm, by building the
sparse transition operator on a uniform y-grid with bilinear interpolation and a
per-state Gauss-Legendre rule in z.  DIAGNOSTIC ONLY.
"""
from __future__ import annotations
import numpy as np
from scipy.sparse import csr_matrix, identity
from scipy.sparse.linalg import spsolve
from scipy.special import ndtr

A = 4581762885148045 / 8796093022208
LOGA = np.log(A); C_SR = LOGA + 0.5; B_SR = np.log1p(A)


def build(e: float, G: int = 128, NZ: int = 160):
    d = B_SR / G
    yc = (np.arange(G) + 0.5) * d                       # cell centres
    YP, YM = np.meshgrid(yc, yc, indexing="ij")
    yp, ym = YP.ravel(), YM.ravel()
    l = ym - C_SR
    u = C_SR - yp
    xg, wg = np.polynomial.legendre.leggauss(NZ)
    z = 0.5 * (u[:, None] + l[:, None]) + 0.5 * (u - l)[:, None] * xg[None, :]
    wz = 0.5 * (u - l)[:, None] * wg[None, :] * np.exp(-0.5 * (z + e) ** 2) / np.sqrt(2 * np.pi)
    qp = np.log1p(np.exp(np.clip(yp[:, None] + z - 0.5, -700, 700)))
    qm = np.log1p(np.exp(np.clip(ym[:, None] - z - 0.5, -700, 700)))
    # bilinear interpolation onto the cell-centre grid, clamped at the edges
    fp = np.clip(qp / d - 0.5, 0, G - 1 - 1e-12)
    fm = np.clip(qm / d - 0.5, 0, G - 1 - 1e-12)
    i0 = fp.astype(np.int64); j0 = fm.astype(np.int64)
    a = fp - i0; b = fm - j0
    i1 = np.minimum(i0 + 1, G - 1); j1 = np.minimum(j0 + 1, G - 1)
    rows = np.repeat(np.arange(G * G), NZ)
    data = np.concatenate([((1-a)*(1-b)*wz).ravel(), (a*(1-b)*wz).ravel(),
                           ((1-a)*b*wz).ravel(), (a*b*wz).ravel()])
    cols = np.concatenate([(i0*G+j0).ravel(), (i1*G+j0).ravel(),
                           (i0*G+j1).ravel(), (i1*G+j1).ravel()])
    K = csr_matrix((data, (np.tile(rows, 4), cols)), shape=(G*G, G*G))
    return K, yc, d


def solve_h(e: float, G: int = 128, NZ: int = 160):
    K, yc, d = build(e, G, NZ)
    h = spsolve((identity(G*G, format="csr") - K).tocsc(), np.ones(G*G))
    return h.reshape(G, G), K, yc
