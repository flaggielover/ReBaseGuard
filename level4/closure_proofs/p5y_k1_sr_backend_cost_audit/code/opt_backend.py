"""P5Y K1 SR backend cost audit -- optimized backend, routes O1 + O2 + O3.

Same mathematics as the Task1R-qualified harness. Nothing about the certificate
is weakened: no precision change, no degree change, no budget change, no
dropped term, no float path, no bound loosened.

THE DEPENDENCY FACT THE ROUTES EXPLOIT
--------------------------------------
Per panel the qualified harness builds V = sp(p_c + z_c - 1/2 + alpha + zeta),
W = sp(m_c - z_c - 1/2 + beta - zeta), then T_i(tau V) and T_j(tau W).  None of
these contains the drift e, the function index r, or a candidate coefficient:

    T_i(tau V), T_j(tau W)     depend on (patch, panel) only
    Gaussian moments N_k       depend on (patch, panel, e)
    candidate chat_ij          depends on (e, function)

The baseline recomputes the (patch, panel) tensors for every one of the
322 x 19 = 6118 (sub-cell, function) pairs.  That is the redundancy.

    O1  compute the (patch, panel) tensors once
    O3  build the panel operator  M[(i,a),(j,b)] = sum_{k1,k2} P[i][a][k1]
        Q[j][b][k2] N_{k1+k2}  once per (patch, panel, e), factorised through
        R = P . Hankel(N), and contract it against each candidate
    O2  carry P, Q, R as arb_mat and do every contraction as a C-level matrix
        product instead of a Python loop over scalar arb objects

O3 is an exact algebraic refactoring of the same sum.  The only quantity not
reproduced bit-for-bit is the error channel, where the optimized route uses
mag(sum_j chat_ij TW_j) <= sum_j |chat_ij| mag(TW_j).  That is a LARGER error
bound, i.e. a strictly more conservative certificate -- never a looser one.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
ROOT = NS.parents[2]
T1R = ROOT / "level4/closure_proofs/p5y_k1_task1r_budget_harness"
for _p in (str(T1R / "code"),):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from flint import arb, arb_mat                                        # noqa: E402
import harness as H                                                   # noqa: E402
import sr_local as L                                                  # noqa: E402


class PanelShared:
    """(patch, panel) tensors: no drift, no function, no candidate.  ROUTE O1."""
    __slots__ = ("P", "Q", "Qflat", "magV", "exV", "ezV", "magW", "exW", "ezW",
                 "D", "Z", "nrow")

    def __init__(self, p_c, m_c, z_c, b, ctxt):
        H_, h, D, Z, Hp, hp = ctxt
        half = arb(1) / arb(2)
        V = H.softplus_tm2(p_c + z_c - half, ctxt, +1)
        W = H.softplus_tm2(m_c - z_c - half, ctxt, -1)
        TV = H.cheb_tm2(V.scaled(arb(2) / b, shift=arb(-1)), H.CAND_DEGREE)
        TW = H.cheb_tm2(W.scaled(arb(2) / b, shift=arb(-1)), H.CAND_DEGREE)
        n = H.CAND_DEGREE + 1
        self.D, self.Z, self.nrow = D, Z, n * (D + 1)
        # P[(i,a), k] and Q[(j,b), k]  -- ROUTE O2 layout
        self.P = arb_mat(self.nrow, Z + 1)
        self.Q = arb_mat(self.nrow, Z + 1)
        for i in range(n):
            for a in range(D + 1):
                row = i * (D + 1) + a
                for k in range(Z + 1):
                    self.P[row, k] = TV[i].c[a][k]
                    self.Q[row, k] = TW[i].c[a][k]
        # Qflat[(j,k), b] for the per-function contraction
        self.Qflat = arb_mat(n * (Z + 1), D + 1)
        for j in range(n):
            for k in range(Z + 1):
                for bq in range(D + 1):
                    self.Qflat[j * (Z + 1) + k, bq] = TW[j].c[bq][k]
        self.magV = [t.mag() for t in TV]
        self.exV = [t.ex for t in TV]
        self.ezV = [t.ez for t in TV]
        self.magW = [t.mag() for t in TW]
        self.exW = [t.ex for t in TW]
        self.ezW = [t.ez for t in TW]


class PanelDrift:
    """(patch, panel, e): the Gaussian moments and R = P . Hankel(N).  ROUTE O3."""
    __slots__ = ("R", "N0", "shared")

    def __init__(self, shared: PanelShared, N):
        Z = shared.Z
        Hank = arb_mat(Z + 1, Z + 1)
        for k1 in range(Z + 1):
            for k2 in range(Z + 1):
                Hank[k1, k2] = N[k1 + k2]
        self.R = shared.P * Hank
        self.N0 = N[0].abs_upper()
        self.shared = shared


def contract(pd: PanelDrift, cand) -> tuple[list[list[arb]], arb, arb]:
    """Per (function): contract the panel operator against one candidate."""
    sh = pd.shared
    D, Z, n = sh.D, sh.Z, H.CAND_DEGREE + 1
    C = arb_mat(n, n)
    for i in range(n):
        for j in range(n):
            C[i, j] = cand[i][j]
    Ct = C.transpose()
    coef = [[arb(0)] * (D + 1) for _ in range(D + 1)]
    for a in range(D + 1):
        Ra = arb_mat(n, Z + 1)                       # gather rows (i,a)
        for i in range(n):
            row = i * (D + 1) + a
            for k in range(Z + 1):
                Ra[i, k] = pd.R[row, k]
        Sa = Ct * Ra                                 # (n x n)(n x Z+1) -> n x (Z+1)
        flat = arb_mat(1, n * (Z + 1))
        for j in range(n):
            for k in range(Z + 1):
                flat[0, j * (Z + 1) + k] = Sa[j, k]
        out = flat * sh.Qflat                        # 1 x (D+1)
        for bq in range(D + 1):
            coef[a][bq] = out[0, bq]
    ex = ez = arb(0)
    for i in range(n):
        ai, ei, zi = sh.magV[i], sh.exV[i], sh.ezV[i]
        for j in range(n):
            c = cand[i][j].abs_upper()
            if c.is_zero():
                continue
            ex += c * (sh.magW[j] * ei + ai * sh.exW[j])
            ez += c * (sh.magW[j] * zi + ai * sh.ezW[j])
    return coef, ex * pd.N0, ez * pd.N0


def run_panels_opt(cand, D, Z, g, p1, *, shared_cache=None, drift_cache=None,
                   only_panel=None, collect_shared=False):
    """Optimized equivalent of harness.run_panels for the K_e Fhat Taylor model."""
    b, c, e = g["b"], g["c"], g["e"]
    p_c, m_c, Hh, L_c = g["p_c"], g["m_c"], g["H"], g["L_c"]
    n_z = p1["n_panels"]
    h = g["span"] / (arb(2) * arb(n_z))
    Hp = [Hh ** a for a in range(2 * D + 2)]
    hp = [h ** k for k in range(2 * Z + 2)]
    ctxt = (Hh, h, D, Z, Hp, hp)
    coef = [[arb(0)] * (D + 1) for _ in range(D + 1)]
    ex_tot = ez_tot = arb(0)
    panels = range(n_z) if only_panel is None else (only_panel,)
    for kp in panels:
        z_lo = L_c + arb(2) * h * arb(kp)
        z_hi = z_lo + arb(2) * h
        z_c = (z_lo + z_hi) / arb(2)
        if shared_cache is not None and kp in shared_cache:
            sh = shared_cache[kp]
        else:
            sh = PanelShared(p_c, m_c, z_c, b, ctxt)
            if shared_cache is not None:
                shared_cache[kp] = sh
        if drift_cache is not None and kp in drift_cache:
            pd = drift_cache[kp]
        else:
            N = H.panel_moments(z_lo, z_hi, z_c, e, 2 * Z + 1, h)
            pd = PanelDrift(sh, N)
            if drift_cache is not None:
                drift_cache[kp] = pd
        pc, ex, ez = contract(pd, cand)
        for a in range(D + 1):
            for bq in range(D + 1):
                coef[a][bq] += pc[a][bq]
        ex_tot += ex
        ez_tot += ez
    return coef, ex_tot, ez_tot, h, ctxt
