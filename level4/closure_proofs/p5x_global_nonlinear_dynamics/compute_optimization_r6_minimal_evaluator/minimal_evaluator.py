"""P5X R6: the frozen minimal stable-tail evaluator.

Implements exactly R6_FROZEN_SPEC.md section 2 and nothing more.  Geometry, the
xi/zeta recurrence and the G_k assembly are IMPORTED from R4's xi_kernel (G9).
No erfcx, no hypgeom_u, no exponent folding.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from flint import arb

_NS = Path(__file__).resolve().parents[1]
for _p in (_NS / "compute_optimization_r4_xi_reformulation",
           Path(__file__).resolve().parents[5] / "rebaseguard-proof" / "src"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from xi_kernel import live_limits, sr_constants, y_to_zeta, zeta_patch  # noqa: E402,F401
from rebaseguard_certify.arb_backend import rational  # noqa: E402

HUGE_LOG10, TINY_LOG10 = 20.0, -20.0

COUNTERS = {"z_panels": 0, "softplus_approximations": 0, "erfc_calls": 0,
            "erf_calls": 0, "huge_tiny_products": 0, "max_abs_log10": 0.0,
            "max_raw_prefactor_log10": -math.inf, "min_tail_factor": math.inf,
            "regime_B": 0, "regime_C": 0, "regime_D": 0}


def reset_counters() -> None:
    for k, v in list(COUNTERS.items()):
        COUNTERS[k] = 0 if isinstance(v, int) else v
    COUNTERS["max_abs_log10"] = 0.0
    COUNTERS["max_raw_prefactor_log10"] = -math.inf
    COUNTERS["min_tail_factor"] = math.inf


def _log10(x: arb) -> float:
    m = abs(float(x.mid()))
    return math.log10(m) if m > 0 else -math.inf


def _mul(x: arb, y: arb) -> arb:
    """Multiply, recording the huge x tiny diagnostic (REPORTING ONLY, D13)."""
    lx, ly = _log10(x), _log10(y)
    if (lx > HUGE_LOG10 and ly < TINY_LOG10) or (ly > HUGE_LOG10 and lx < TINY_LOG10):
        COUNTERS["huge_tiny_products"] += 1
    for v in (lx, ly):
        if math.isfinite(v):
            COUNTERS["max_abs_log10"] = max(COUNTERS["max_abs_log10"], abs(v))
    return x * y


def _Phi(w: arb) -> arb:
    r2 = arb(2).sqrt()
    if w.upper() <= 0:
        COUNTERS["erfc_calls"] += 1
        return (-w / r2).erfc() / arb(2)
    if w.lower() >= 0:
        COUNTERS["erfc_calls"] += 1
        return arb(1) - (w / r2).erfc() / arb(2)
    COUNTERS["erf_calls"] += 1
    return (arb(1) + (w / r2).erf()) / arb(2)


def I_k(k: int, l: arb, u: arb, e: arb):
    """Frozen R6 evaluator.  Returns (value, regime)."""
    kk = arb(k)
    a, b = l + e - kk, u + e - kk
    r2 = arb(2).sqrt()
    pref = (kk * kk / arb(2) - kk * e).exp()
    COUNTERS["max_raw_prefactor_log10"] = max(
        COUNTERS["max_raw_prefactor_log10"], _log10(pref))
    if b.upper() <= 0:                                   # regime B
        COUNTERS["regime_B"] += 1
        COUNTERS["erfc_calls"] += 2
        d, reg = ((-b / r2).erfc() - (-a / r2).erfc()) / arb(2), "B"
    elif a.lower() >= 0:                                 # regime C
        COUNTERS["regime_C"] += 1
        COUNTERS["erfc_calls"] += 2
        d, reg = ((a / r2).erfc() - (b / r2).erfc()) / arb(2), "C"
    else:                                                # regime D
        COUNTERS["regime_D"] += 1
        d, reg = _Phi(b) - _Phi(a), "D"
    m = abs(float(d.mid()))
    if m > 0:
        COUNTERS["min_tail_factor"] = min(COUNTERS["min_tail_factor"], m)
    return _mul(pref, d), reg


def I_k_r4(k: int, l: arb, u: arb, e: arb) -> arb:
    """R4's evaluator, kept verbatim as the rigorous reference path."""
    from rebaseguard_certify.arb_backend import gaussian_cdf
    kk = arb(k)
    return (kk * kk / arb(2) - kk * e).exp() * (gaussian_cdf(u + e - kk)
                                                - gaussian_cdf(l + e - kk))


def compute_Gk(coeffs, zp: arb, zm: arb, A: arb) -> dict[int, arb]:
    """R4 xi_kernel section 14 G_k assembly, reused unchanged (G9)."""
    n_i, n_j = len(coeffs), len(coeffs[0])
    inv = arb(1) / A
    P = [arb(1)] * n_i
    Q = [arb(1)] * n_j
    for i in range(1, n_i):
        P[i] = P[i - 1] * (inv + zp)
    for j in range(1, n_j):
        Q[j] = Q[j - 1] * (inv + zm)
    G: dict[int, arb] = {}
    for i in range(n_i):
        for j in range(n_j):
            c = coeffs[i][j]
            cc = c if isinstance(c, arb) else arb(c)
            G[i - j] = G.get(i - j, arb(0)) + cc * P[i] * Q[j] * (-arb(i + j) / arb(2)).exp()
    return G


def kernel_apply(coeffs, zp: arb, zm: arb, e: arb, A: arb, r4: bool = False):
    """(K_e f)(zeta) with the frozen R6 I_k (or R4's, for the reference path)."""
    l, u = live_limits(zp, zm, A)
    G = compute_Gk(coeffs, zp, zm, A)
    total = arb(0)
    regimes: dict[int, str] = {}
    for k, g in G.items():
        v, reg = (I_k_r4(k, l, u, e), "R4") if r4 else I_k(k, l, u, e)
        regimes[k] = reg
        total += g * v
    return total, G, regimes
