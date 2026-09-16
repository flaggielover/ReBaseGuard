"""Named manufactured fixtures for the order-3 producer qualification. NON-SCIENTIFIC, pure functions of their spec.

Each fixture returns (system, e0, rho, seed, noise). The families cover the Phase-7 list:
positive / negative / identically-zero R''' (m = 1), sign crossing inside the cell, very small positive / negative,
parity near zero (cell [0, 2 rho] with an even K and odd sources), narrow and wide cells, ill-conditioned 3x3
resolvents, CUSUM-like C*rho = 0.3133 amplification with C ~ 1233, and random chains.
"""
from __future__ import annotations

from fractions import Fraction as Fr

import manufactured_chain as MC

CRHO = Fr(3133, 10000)


def _scalar_const_K(k0: Fr, s0_coeffs, e0: Fr, label: str) -> MC.ChainSystem:
    """K = k0 constant, J = 1/3, h_1 = 1/2 + t/5, S_0 given in t = e - e0: F_0''' = S_0''' / (1 - k0)."""
    return MC.scalar_chain([k0], [Fr(1, 3)], [Fr(1, 2), Fr(1, 5)], s0_coeffs, e0, label)


def build(spec: dict):
    kind = spec["kind"]
    e0, rho = Fr(spec["e0"]), Fr(spec["rho"])
    seed, noise = int(spec.get("seed", 0)), Fr(spec.get("noise", "0"))
    if kind == "random":
        sysm = MC.random_chain(seed, int(spec["n"]), deg=int(spec.get("deg", 3)), centre=e0,
                               k0=Fr(spec.get("k0", "1/4")))
    elif kind == "target_R3_m1":
        base = MC.random_chain(seed, int(spec["n"]), deg=int(spec.get("deg", 3)), centre=e0)
        sysm = MC.with_target_R3_m1(base, e0, Fr(spec["target"]))
    elif kind == "identically_zero_R3_m1":
        sysm = _scalar_const_K(Fr(3, 10), [Fr(1), Fr(-1, 2), Fr(1, 7)], e0, "zero_R3_m1")
    elif kind == "constant_R3_m1":
        eps = Fr(spec["value"])
        k0 = Fr(3, 10)
        sysm = _scalar_const_K(k0, [Fr(1), Fr(-1, 2), Fr(1, 7), eps * (1 - k0) / 6], e0, f"const_R3_m1={eps}")
    elif kind == "parity_near_zero":
        # K even in e (centre 0), sources odd in e: F_0 odd, F_0''' even. Cell [0, 2 rho].
        sysm = MC.scalar_chain([Fr(1, 4), Fr(0), Fr(1, 10)], [Fr(1, 3), Fr(0), Fr(1, 20)],
                               [Fr(0), Fr(1, 2), Fr(0), Fr(1, 9)], [Fr(0), Fr(1), Fr(0), Fr(-1, 3)],
                               Fr(0), "parity_near_zero")
    elif kind == "controlled_K3":
        # K_1(e0) = K_2(e0) = 0 and K_3(e0) = 1: an F error reaches the third derivative only through K_3.
        sysm = MC.scalar_chain([Fr(3, 10), Fr(0), Fr(0), Fr(1, 6), Fr(1, 24)], [Fr(1, 3)], [Fr(1, 2), Fr(1, 5)],
                               [Fr(1), Fr(-1, 2), Fr(1, 7), Fr(1, 5)], e0, "controlled_K3")
    elif kind == "controlled_K1":
        # every coefficient positive, so the cell norms are nearly attained at e0.
        sysm = MC.scalar_chain([Fr(3, 10), Fr(1, 5), Fr(1, 20), Fr(1, 30)], [Fr(1, 3)], [Fr(1, 2), Fr(1, 5)],
                               [Fr(1), Fr(-1, 2), Fr(1, 7), Fr(1, 5)], e0, "controlled_K1")
    elif kind == "ill_conditioned":
        sysm = MC.ill_conditioned_chain(seed, C_target=int(spec["C_target"]), centre=e0)
    elif kind == "cusum_like_crho":
        # C ~ C_target and rho = 0.3133 / C_target, as on every CUSUM cover cell <= 324.
        C_t = int(spec["C_target"])
        sysm = MC.scalar_chain([1 - Fr(1001, 1000 * C_t), Fr(1, 2 * C_t), Fr(1, 8 * C_t)], [Fr(1, 3), Fr(1, 7)],
                               [Fr(1, 2), Fr(1, 5)], [Fr(1, C_t), Fr(-1, 3), Fr(1, 11), Fr(1, 5)], e0,
                               f"cusum_like_C{C_t}")
        rho = CRHO / C_t
    else:
        raise ValueError(kind)
    return sysm, e0, rho, seed, noise
