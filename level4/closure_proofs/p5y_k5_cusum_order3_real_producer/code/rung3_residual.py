"""Certified midpoint residual of the NEW rung F_r:3, backend-agnostic.

Differentiate the frozen resolvent equation (I - K_e) F_r = S_r three times in e (Leibniz; the candidates are
state-only polynomials, constant in e):

    F_r''' = K_0 F_r''' + K_3 F_r + 3 K_2 F_r' + 3 K_1 F_r'' + S_r'''

so the residual of the degree-12 candidate G_r at e0 is

    res_G = G - K_0 G - K_3 Fhat - 3 K_2 Dhat - 3 K_1 Hhat - Src3,   Src3 = Sclosed_3 (r = 0) | Shat_r:3 (r >= 1)

It is the frozen H_r pattern (cusum_layer2.all_residuals "H_r"), one order further:

    truncation  Z_RANGE (sG eps_z0 + sF eps_z3 + 3 sD eps_z2 + 3 sH eps_z1)  [+ reward_allow[3] for r = 0]
    envelope    k_1 sG + k_4 sF + 3 k_3 sD + 3 k_2 sH        >= sup_cell ||d_e res_G||
                (d_e res_G = -K_1 G - K_4 Fhat - 3 K_3 Dhat - 3 K_2 Hhat; the source is fixed, its e-variation is
                 owned once by the source node, exactly as for F_r, D_r, H_r)

`cert` must provide: P, sup, K(poly, i), vec(poly), z_range, eps_zi(i), reward_allow, norms["k"], certify(...).
The real CUSUM certifier provides them from the frozen Layer 2; the manufactured backend from exact matrices.
The TERMS table is the single source of the Leibniz expansion; the tests check it against the reference kernel.
"""
from __future__ import annotations

from math import comb

RUNG = 3
# (coefficient, operator derivative order i, candidate key family, candidate derivative order n - i)
TERMS = tuple((comb(RUNG, i), i, {0: "G", 1: "H", 2: "D", 3: "F"}[i]) for i in range(RUNG + 1))


def g_residual(cert, r: int) -> dict:
    """Certified {delta_mid, delta_cell, ...} for G_r against its defining order-3 equation at e0."""
    from flint import arb
    k_ = cert.norms["k"]
    res = cert.vec(cert.P["G", r, 0])
    extra = arb(0)
    env = arb(0)
    for c, i, fam in TERMS:
        poly = cert.P[fam, r, 0]
        s = cert.sup[fam, r, 0]
        res = res - cert.K(poly, i).scale(arb(c))
        extra = extra + arb(c) * cert.z_range * s * cert.eps_zi(i)
        env = env + arb(c) * k_[i + 1] * s
    src = cert.P["Sclosed", 0, 3] if r == 0 else cert.P["S", r, 3]
    res = res - cert.vec(src)
    if r == 0:
        extra = extra + cert.reward_allow[3]
    return cert.certify(f"G_{r}", res, extra, env)
