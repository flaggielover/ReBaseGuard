"""P5X feasibility probe — NON-AUTHORITATIVE, FLOATING POINT, NOT A CERTIFICATE.

Purpose
-------
Test one thing only: whether the frozen P5 selection map

    R_{D,m}(e) = E_e[ Rbar ],   Rbar = (1/w) sum_{r<w} raw_{tau-r},  w = min(m,tau)

and its second moment can be evaluated from **two-dimensional** Fredholm
objects on the compact pre-alarm detector-state square, for every m >= 1 and
every entering error e --- i.e. whether the Level-1..3 Arb certificate
architecture (`rebaseguard-proof/proofs/`, `closure/04_ARB_CERTIFICATE.md`)
extends to e != 0 and m > 1 with **no dimension blow-up**.

If it does, a rigorous interval-arithmetic enclosure of R and S is an
engineering problem rather than a research problem, and P5's open hypotheses
(H2)/(H3a)/(H3b) become certifiable rather than measurable.

This module is *evidence for a proof plan*.  It is ordinary double precision
with a bilinear collocation discretisation and NO rigorous error control.  It
establishes nothing and is excluded from every P5X scientific claim.  See
`../FEASIBILITY_AUDIT.md` section 6 and `../PROOF_OBLIGATIONS.md`.

Reduction under test (stated exactly in `../FROZEN_THEOREM.md` as P5X-T1)
------------------------------------------------------------------------
Pre-alarm state x = (x+, x-) in E_D = [0, b_D)^2, innovations z ~ N(-e, 1),
continuation interval (l(x), u(x)) = (x- - c_D, c_D - x+), reset state
x0 = (0,0), post-innovation map q(x, z).

    (K_e f)(x)    = int_l^u f(q(x,z)) phi(z+e) dz
    (K_{z,e} f)(x)= int_l^u z f(q(x,z)) phi(z+e) dz
    rho_{1,e}(x)  = E[z ; alarm from x]      (closed form)
    rho_{2,e}(x)  = E[z^2 ; alarm from x]    (closed form)
    h_1 = 1 - K_e 1,   h_j = K_e h_{j-1}          (h_j(x) = P_x(tau = j))
    S_0 = rho_{1,e},   S_j = K_{z,e} h_j
    g_0 = (I-K_e)^{-1} S_0,   g_r = (I-K_e)^{-1} S_r   (r >= 1)
    E[Z_i 1{tau=t}] = (K_e^{i-1} S_{t-i})(x0)

    E_e[A_m] = (1/m) sum_{r<m} ( g_r(x0) - sum_{t=r+1}^{m-1} E[Z_{t-r} 1{tau=t}] )
             + sum_{t=1}^{m-1} (1/t) sum_{i=1}^{t} E[Z_i 1{tau=t}]
    R_{D,m}(e) = e + E_e[A_m]

For m = 1 the second moment is available from the same solve:
    E[Rbar^2 | e] = g^{(2)}(x0) + 2 e g_0(x0) + e^2 ,  g^{(2)} = (I-K_e)^{-1} rho_{2,e}.
"""
from __future__ import annotations

import numpy as np
from scipy.sparse import csr_matrix, identity
from scipy.sparse.linalg import splu
from scipy.special import ndtr

K_FROZEN = 0.5
H_FROZEN = 5.0
SR_THRESHOLD = 520.886133602749

CUSUM = "cusum"
SR = "sr"


def phi(x: np.ndarray) -> np.ndarray:
    return np.exp(-0.5 * x * x) / np.sqrt(2.0 * np.pi)


def detector_spec(detector: str) -> tuple[float, float]:
    """Return (b_D, c_D): state-square side and one-step alarm margin."""
    if detector == CUSUM:
        return H_FROZEN, H_FROZEN + K_FROZEN
    if detector == SR:
        log_a = float(np.log(SR_THRESHOLD))
        return log_a, log_a + 0.5
    raise ValueError(f"unknown detector {detector!r}")


def build_operators(detector: str, n_grid: int, e: float, n_quad: int = 24):
    """Bilinear-collocation matrices for K_e and K_{z,e}, plus absorbing rewards."""
    b_d, c_d = detector_spec(detector)
    axis = np.linspace(0.0, b_d, n_grid)
    XP, XM = np.meshgrid(axis, axis, indexing="ij")
    xp = XP.ravel()
    xm = XM.ravel()
    n = xp.size
    lo = xm - c_d
    hi = c_d - xp
    gx, gw = np.polynomial.legendre.leggauss(n_quad)

    if detector == CUSUM:
        # split at the two reset kinks so each panel is smooth
        brk = np.stack([lo, np.clip(K_FROZEN - xp, lo, hi),
                        np.clip(xm - K_FROZEN, lo, hi), hi], axis=1)
        brk = np.sort(brk, axis=1)
    else:
        brk = np.stack([lo, lo + (hi - lo) / 3.0, lo + 2.0 * (hi - lo) / 3.0, hi], axis=1)

    rows, cols, vk, vkz = [], [], [], []
    idx = np.arange(n)
    dx = b_d / (n_grid - 1)
    for panel in range(3):
        a = brk[:, panel]
        b = brk[:, panel + 1]
        mid = 0.5 * (a + b)
        half = 0.5 * (b - a)
        live = half > 1e-14
        for gi in range(n_quad):
            z = mid + half * gx[gi]
            w = np.where(live, half * gw[gi] * phi(z + e), 0.0)
            if detector == CUSUM:
                yp = np.maximum(0.0, xp + z - K_FROZEN)
                ym = np.maximum(0.0, xm - z - K_FROZEN)
            else:
                yp = np.logaddexp(0.0, xp + z - 0.5)
                ym = np.logaddexp(0.0, xm - z - 0.5)
            yp = np.clip(yp, 0.0, b_d)
            ym = np.clip(ym, 0.0, b_d)
            ci = np.clip((yp / dx).astype(np.int64), 0, n_grid - 2)
            cj = np.clip((ym / dx).astype(np.int64), 0, n_grid - 2)
            tx = yp / dx - ci
            ty = ym / dx - cj
            for di, dj, wt in ((0, 0, (1 - tx) * (1 - ty)), (1, 0, tx * (1 - ty)),
                               (0, 1, (1 - tx) * ty), (1, 1, tx * ty)):
                rows.append(idx)
                cols.append((ci + di) * n_grid + (cj + dj))
                vk.append(w * wt)
                vkz.append(w * z * wt)
    rows = np.concatenate(rows)
    cols = np.concatenate(cols)
    K = csr_matrix((np.concatenate(vk), (rows, cols)), shape=(n, n))
    Kz = csr_matrix((np.concatenate(vkz), (rows, cols)), shape=(n, n))

    au = hi + e
    al = lo + e
    rho1 = phi(au) - phi(al) - e * (1.0 - ndtr(au) + ndtr(al))
    rho2 = ((au * phi(au) + (1.0 - ndtr(au))) - 2.0 * e * phi(au) + e * e * (1.0 - ndtr(au))
            + (-al * phi(al) + ndtr(al)) + 2.0 * e * phi(al) + e * e * ndtr(al))
    return K, Kz, rho1, rho2, n


def selection_map(detector: str, e: float, m_list, n_grid: int = 101,
                  n_quad: int = 24, second_moment: bool = False) -> dict:
    """R_{D,m}(e) for each m in ``m_list`` (and, if asked, S_{D,1}(e))."""
    K, Kz, rho1, rho2, n = build_operators(detector, n_grid, e, n_quad)
    lu = splu((identity(n, format="csc") - K).tocsc())
    m_max = max(m_list)
    ones = np.ones(n)
    h = {1: ones - K @ ones}
    for j in range(2, m_max):
        h[j] = K @ h[j - 1]
    src = {0: rho1}
    for j in range(1, m_max):
        src[j] = Kz @ h[j]
    g = {r: lu.solve(src[r]) for r in range(m_max)}

    x0 = 0

    def ez(i: int, t: int) -> float:
        """E[Z_i ; tau = t] at the reset state, 1 <= i <= t."""
        v = src[t - i]
        for _ in range(i - 1):
            v = K @ v
        return float(v[x0])

    out: dict = {"detector": detector, "e": float(e), "n_grid": int(n_grid),
                 "n_quad": int(n_quad), "R": {}}
    for m in m_list:
        total = 0.0
        for r in range(m):
            total += (g[r][x0] - sum(ez(t - r, t) for t in range(r + 1, m))) / m
        for t in range(1, m):
            total += sum(ez(i, t) for i in range(1, t + 1)) / t
        out["R"][int(m)] = float(e + total)
    if second_moment:
        g2 = lu.solve(rho2)
        r1 = out["R"][1]
        m2 = float(g2[x0] + 2.0 * e * g[0][x0] + e * e)
        out["M2_m1"] = m2
        out["S_m1"] = m2 - r1 * r1
    return out
