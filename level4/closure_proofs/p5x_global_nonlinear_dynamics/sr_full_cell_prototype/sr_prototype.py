"""SR m=1 full-cell prototype: candidate solve, certified residual, enclosure.

Implements PROTOTYPE_PROTOCOL.md sections 3-4.  The candidate is NOT proof
evidence; only the residual it produces is.  All certified quantities are Arb
balls evaluated with the R6 stable-tail evaluator.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
from flint import arb, ctx

_NS = Path(__file__).resolve().parents[1]
for _p in (_NS / "compute_optimization_r6_minimal_evaluator",
           _NS / "compute_optimization_r4_xi_reformulation",
           Path(__file__).resolve().parents[5] / "rebaseguard-proof" / "src"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from minimal_evaluator import COUNTERS, I_k, live_limits, sr_constants  # noqa: E402
from rebaseguard_certify.arb_backend import rational                    # noqa: E402

DEGREE = 16
SQRT2 = math.sqrt(2.0)


# ----------------------------------------------------------- exact rho_1

def rho1_arb(l: arb, u: arb, e: arb) -> arb:
    """rho_{1,e} = phi(u+e) - phi(l+e) - e[(1-Phi(u+e)) + Phi(l+e)], stable form.

    1 - Phi(u+e) cancels catastrophically if computed as 1 - Phi; both tail
    probabilities are taken on their accurate erfc branch, exactly as R6 does.
    """
    r2 = arb(2).sqrt()
    tp = arb(2) * arb.pi()
    U, L = u + e, l + e
    phi_u = (-U * U / arb(2)).exp() / tp.sqrt()
    phi_l = (-L * L / arb(2)).exp() / tp.sqrt()
    tail_u = ((U / r2).erfc() / arb(2)) if U.lower() >= 0 else \
             (arb(1) - (-U / r2).erfc() / arb(2))
    tail_l = ((-L / r2).erfc() / arb(2)) if L.upper() <= 0 else \
             (arb(1) - (L / r2).erfc() / arb(2))
    return phi_u - phi_l - e * (tail_u + tail_l)


def _rho1_float(l: float, u: float, e: float) -> float:
    U, L = u + e, l + e
    pf = 1.0 / math.sqrt(2.0 * math.pi)
    return (pf * math.exp(-U * U / 2) - pf * math.exp(-L * L / 2)
            - e * (math.erfc(U / SQRT2) / 2 + math.erfc(-L / SQRT2) / 2))


# --------------------------------------------------- float model for the solve

def _limits_float(zp: float, zm: float, A: float, c: float):
    return math.log(1.0 / A + zm) - 0.5, 0.5 - math.log(1.0 / A + zp)


def _I_k_float(k: int, l: float, u: float, e: float) -> float:
    """R6 regime-split evaluator in float64 (candidate solve only)."""
    a, b = l + e - k, u + e - k
    pref = math.exp(min(k * k / 2 - k * e, 700.0))
    if b <= 0:
        d = (math.erfc(-b / SQRT2) - math.erfc(-a / SQRT2)) / 2
    elif a >= 0:
        d = (math.erfc(a / SQRT2) - math.erfc(b / SQRT2)) / 2
    else:
        d = (1 - math.erfc(b / SQRT2) / 2) - math.erfc(-a / SQRT2) / 2
    return pref * d


def solve_candidate(e0: float, A: float, c: float, degree: int = DEGREE):
    """Collocation solve of (I - K_{e0}) ghat = rho_1.  NOT proof evidence."""
    n = degree + 1
    t = 0.5 * (1.0 - np.cos(np.pi * np.arange(n) / (n - 1)))     # Cheb-Lobatto on [0,1]
    M = np.zeros((n * n, n * n))
    rhs = np.zeros(n * n)
    for ci, zp in enumerate(t):
        for cj, zm in enumerate(t):
            row = ci * n + cj
            l, u = _limits_float(zp, zm, A, c)
            rhs[row] = _rho1_float(l, u, e0)
            Pk = {}
            for k in range(-degree, degree + 1):
                Pk[k] = _I_k_float(k, l, u, e0)
            ap, am = 1.0 / A + zp, 1.0 / A + zm
            for i in range(n):
                for j in range(n):
                    col = i * n + j
                    basis = (zp ** i) * (zm ** j)
                    kern = (ap ** i) * (am ** j) * math.exp(-(i + j) / 2.0) * Pk[i - j]
                    M[row, col] = basis - kern
    coef = np.linalg.solve(M, rhs)
    return coef.reshape(n, n), float(np.linalg.cond(M))


# ------------------------------------------------------- certified residual

def residual_on_cell(coef_arb, zp: arb, zm: arb, e: arb, A: arb) -> arb:
    """ghat - K_e ghat - rho_1 as a ball over the whole cell (and e-cell)."""
    n = len(coef_arb)
    inv = arb(1) / A
    Pb = [arb(1)] * n
    Qb = [arb(1)] * n
    Pk_ = [arb(1)] * n
    Qk_ = [arb(1)] * n
    for i in range(1, n):
        Pb[i] = Pb[i - 1] * zp
        Pk_[i] = Pk_[i - 1] * (inv + zp)
    for j in range(1, n):
        Qb[j] = Qb[j - 1] * zm
        Qk_[j] = Qk_[j - 1] * (inv + zm)
    l, u = live_limits(zp, zm, A)
    G: dict[int, arb] = {}
    g_val = arb(0)
    for i in range(n):
        for j in range(n):
            c = coef_arb[i][j]
            g_val += c * Pb[i] * Qb[j]
            G[i - j] = G.get(i - j, arb(0)) + c * Pk_[i] * Qk_[j] * (-arb(i + j) / arb(2)).exp()
    kg = arb(0)
    for k, gg in G.items():
        v, _ = I_k(k, l, u, e)
        kg += gg * v
    return g_val - kg - rho1_arb(l, u, e)


def eval_candidate(coef_arb, zp: arb, zm: arb) -> arb:
    n = len(coef_arb)
    out = arb(0)
    pi_ = arb(1)
    for i in range(n):
        qj = arb(1)
        for j in range(n):
            out += coef_arb[i][j] * pi_ * qj
            qj *= zm
        pi_ *= zp
    return out


# ---------------------------------------------- well-conditioned candidate solve

def solve_candidate_cheb(e0: float, A: float, c: float, degree: int = DEGREE):
    """Same collocation system and the SAME polynomial space as
    `solve_candidate`, but with the unknowns carried in a Chebyshev basis.

    The candidate is explicitly NOT proof evidence (PROTOTYPE_PROTOCOL.md §3);
    only the residual it produces is certified.  The monomial-basis solve is
    numerically meaningless here (condition number ~6e19), so the identical
    system is solved stably and converted back to monomials for the kernel.
    Returns (monomial coefficients, condition number).
    """
    from numpy.polynomial import chebyshev as Cheb
    n = degree + 1
    t = 0.5 * (1.0 - np.cos(np.pi * np.arange(n) / (n - 1)))
    U = np.zeros((n, n))                       # T_a = sum_i U[a,i] zeta^i  on [0,1]
    for a in range(n):
        ca = np.zeros(a + 1)
        ca[a] = 1.0
        mono = Cheb.cheb2poly(ca)              # in s = 2*zeta - 1
        p = np.zeros(n)
        for d, m in enumerate(mono):           # (2z-1)^d expanded in z
            for r in range(d + 1):
                p[r] += m * math.comb(d, r) * (2.0 ** r) * ((-1.0) ** (d - r))
        U[a] = p
    idx = [(ci, cj) for ci in range(n) for cj in range(n)]
    M = np.zeros((n * n, n * n))
    rhs = np.zeros(n * n)
    for row, (ci, cj) in enumerate(idx):
        zp, zm = t[ci], t[cj]
        l, u = _limits_float(zp, zm, A, c)
        rhs[row] = _rho1_float(l, u, e0)
        ap, am = 1.0 / A + zp, 1.0 / A + zm
        Km = np.empty((n, n))
        for i in range(n):
            for j in range(n):
                Km[i, j] = (ap ** i) * (am ** j) * math.exp(-(i + j) / 2.0) * \
                           _I_k_float(i - j, l, u, e0)
        Kab = U @ Km @ U.T                      # (K_e T_a x T_b)(zeta_c)
        sp, sm = 2 * zp - 1, 2 * zm - 1
        Tp = np.array([Cheb.chebval(sp, np.eye(n)[a]) for a in range(n)])
        Tm = np.array([Cheb.chebval(sm, np.eye(n)[a]) for a in range(n)])
        M[row] = (np.outer(Tp, Tm) - Kab).ravel()
    cc = np.linalg.solve(M, rhs).reshape(n, n)
    return U.T @ cc @ U, float(np.linalg.cond(M))
