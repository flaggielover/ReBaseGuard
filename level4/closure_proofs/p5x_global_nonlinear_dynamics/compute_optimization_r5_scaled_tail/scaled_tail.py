"""P5X R5: numerically stable tail-scaled evaluation of the exact R4 integral

    I_k(l,u,e) = int_l^u e^{kz} phi(z+e) dz = e^{k^2/2-ke}[Phi(u+e-k)-Phi(l+e-k)]

Implements exactly the formulas frozen in SCALED_TAIL_DERIVATION.md sections
3-5 and R5_FROZEN_SPEC.md section 2, and nothing more.  The R4 xi/zeta
recurrence, live limits and patch geometry are IMPORTED from xi_kernel, never
reimplemented (Q10).
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from flint import arb

_R4 = Path(__file__).resolve().parents[1] / "compute_optimization_r4_xi_reformulation"
if str(_R4) not in sys.path:
    sys.path.insert(0, str(_R4))
_PROOF_SRC = Path(__file__).resolve().parents[5] / "rebaseguard-proof" / "src"
if str(_PROOF_SRC) not in sys.path:
    sys.path.insert(0, str(_PROOF_SRC))

from xi_kernel import live_limits, sr_constants, y_to_zeta, zeta_patch  # noqa: E402,F401
from rebaseguard_certify.arb_backend import rational  # noqa: E402

HUGE_LOG10, TINY_LOG10 = 20.0, -20.0
ERFCX_BRANCH_T = 2

# Evaluation modes.  "frozen" is the Checkpoint-G specification and is the ONLY
# one the gate verdict is computed from.  The other two are POST-HOC diagnostic
# variants, added during implementation after measuring that Arb's hypgeom_u
# degrades badly on ball arguments (defect D12).
MODE_FROZEN, MODE_EXPBRANCH, MODE_MINIMAL = "frozen", "expbranch", "minimal"
MODE = MODE_FROZEN


def set_mode(m: str) -> None:
    global MODE
    assert m in (MODE_FROZEN, MODE_EXPBRANCH, MODE_MINIMAL)
    MODE = m

COUNTERS = {
    "z_panels": 0,
    "softplus_approximations": 0,
    "erfcx_calls": 0,
    "erfc_calls": 0,
    "hypgeom_u_calls": 0,
    "huge_tiny_products": 0,
    "max_abs_log10": 0.0,
    "max_raw_prefactor_log10": -math.inf,
    "min_tail_factor": math.inf,
    "regime_B": 0, "regime_C": 0, "regime_D": 0,
}


def reset_counters() -> None:
    COUNTERS.update({k: (0 if isinstance(v, int) else v) for k, v in COUNTERS.items()})
    COUNTERS["max_abs_log10"] = 0.0
    COUNTERS["max_raw_prefactor_log10"] = -math.inf
    COUNTERS["min_tail_factor"] = math.inf
    for k in ("z_panels", "softplus_approximations", "erfcx_calls", "erfc_calls",
              "hypgeom_u_calls", "huge_tiny_products", "regime_B", "regime_C", "regime_D"):
        COUNTERS[k] = 0


def _log10(x: arb) -> float:
    m = abs(float(x.mid()))
    return math.log10(m) if m > 0 else -math.inf


def _track(x: arb) -> arb:
    lg = _log10(x)
    if math.isfinite(lg):
        COUNTERS["max_abs_log10"] = max(COUNTERS["max_abs_log10"], abs(lg))
    return x


def _mul(x: arb, y: arb) -> arb:
    """Multiply with Q4 instrumentation: flag any huge x tiny product."""
    lx, ly = _log10(x), _log10(y)
    if (lx > HUGE_LOG10 and ly < TINY_LOG10) or (ly > HUGE_LOG10 and lx < TINY_LOG10):
        COUNTERS["huge_tiny_products"] += 1
    _track(x); _track(y)
    return _track(x * y)


# ------------------------------------------------------------------- erfcx

def erfcx(t: arb) -> arb:
    """Scaled complementary error function, e^{t^2} erfc(t), for t >= 0.

    Frozen two-branch construction (R5_FROZEN_SPEC.md section 2):
      t <= 2 : exp(t^2) erfc(t)                    max intermediate e^4 = 54.6
      t >  2 : U(1/2, 1/2, t^2) / sqrt(pi)         Arb's rigorous Tricomi U
    The branch is taken only on a PROVED bound, so it is deterministic.
    """
    COUNTERS["erfcx_calls"] += 1
    if MODE == MODE_EXPBRANCH:            # POST-HOC variant: exp branch for all t
        COUNTERS["erfc_calls"] += 1
        v = _mul((t * t).exp(), t.erfc())
        m = abs(float(v.mid()))
        if m > 0:
            COUNTERS["min_tail_factor"] = min(COUNTERS["min_tail_factor"], m)
        return v
    if t.lower() > ERFCX_BRANCH_T:
        COUNTERS["hypgeom_u_calls"] += 1
        half = rational(1, 2)
        v = (t * t).hypgeom_u(half, half) / arb.pi().sqrt()
    else:
        COUNTERS["erfc_calls"] += 1
        v = (t * t).exp() * t.erfc()
    m = abs(float(v.mid()))
    if m > 0:
        COUNTERS["min_tail_factor"] = min(COUNTERS["min_tail_factor"], m)
    return v


def _Phi_accurate(w: arb) -> arb:
    """Phi(w) on the branch that avoids cancellation: erfc, never 1+erf."""
    COUNTERS["erfc_calls"] += 1
    r2 = arb(2).sqrt()
    if w.upper() <= 0:
        return (-w / r2).erfc() / arb(2)
    if w.lower() >= 0:
        return arb(1) - (w / r2).erfc() / arb(2)
    return (arb(1) + (w / r2).erf()) / arb(2)      # |w| small: no cancellation


# ------------------------------------------------------------- the integral

def I_k_minimal(k: int, l: arb, u: arb, e: arb):
    """POST-HOC variant: R4's exact structure, with Phi on its accurate erfc
    branch instead of (1+erf)/2.  This is the MINIMAL repair implied by the
    section-1 diagnostic; it forms a huge x tiny product by construction."""
    kk = arb(k)
    a, b = l + e - kk, u + e - kk
    r2 = arb(2).sqrt()
    pref = (kk * kk / arb(2) - kk * e).exp()
    COUNTERS["max_raw_prefactor_log10"] = max(
        COUNTERS["max_raw_prefactor_log10"], _log10(pref))
    # the difference must be regime-split too: computing it as
    # (1-x) - (1-y) in the both-positive case re-creates the cancellation.
    COUNTERS["erfc_calls"] += 2
    if b.upper() <= 0:
        d, reg = ((-b / r2).erfc() - (-a / r2).erfc()) / arb(2), "M-B"
    elif a.lower() >= 0:
        d, reg = ((a / r2).erfc() - (b / r2).erfc()) / arb(2), "M-C"
    else:
        d, reg = _Phi_accurate(b) - _Phi_accurate(a), "M-D"
    return _mul(pref, d), reg


def I_k_scaled(k: int, l: arb, u: arb, e: arb):
    """Stable I_k.  Returns (value, regime).  Frozen formulas, frozen selector."""
    if MODE == MODE_MINIMAL:
        return I_k_minimal(k, l, u, e)
    kk = arb(k)
    a, b = l + e - kk, u + e - kk
    r2 = arb(2).sqrt()

    def T(x: arb) -> arb:
        E = kk * x - (x + e) * (x + e) / arb(2)           # exponent identity, section 3
        pref = E.exp()
        COUNTERS["max_raw_prefactor_log10"] = max(
            COUNTERS["max_raw_prefactor_log10"], _log10(pref))
        return _mul(pref, erfcx(abs(x + e - kk) / r2))

    if b.upper() <= 0:                                    # regime B
        COUNTERS["regime_B"] += 1
        return (T(u) - T(l)) / arb(2), "B"
    if a.lower() >= 0:                                    # regime C
        COUNTERS["regime_C"] += 1
        return (T(l) - T(u)) / arb(2), "C"
    COUNTERS["regime_D"] += 1                             # regime D
    pref = (kk * kk / arb(2) - kk * e).exp()
    COUNTERS["max_raw_prefactor_log10"] = max(
        COUNTERS["max_raw_prefactor_log10"], _log10(pref))
    return _mul(pref, _Phi_accurate(b) - _Phi_accurate(a)), "D"


def I_k_direct(k: int, l: arb, u: arb, e: arb) -> arb:
    """R4's evaluator, kept verbatim as the rigorous reference path."""
    from rebaseguard_certify.arb_backend import gaussian_cdf
    kk = arb(k)
    return (kk * kk / arb(2) - kk * e).exp() * (gaussian_cdf(u + e - kk)
                                                - gaussian_cdf(l + e - kk))


# ------------------------------------------------------------ the k-sum

def compute_Gk(coeffs, zp: arb, zm: arb, A: arb) -> dict[int, arb]:
    """R4's G_k assembly (xi_kernel section 14), reused unchanged.

    Verified identical to xi_kernel.kernel_apply's own G_k by self-test S12.
    """
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


def kernel_apply_scaled(coeffs, zp: arb, zm: arb, e: arb, A: arb, direct: bool = False):
    """(K_e f)(zeta) with the stable I_k.  `direct=True` selects R4's path."""
    l, u = live_limits(zp, zm, A)
    G = compute_Gk(coeffs, zp, zm, A)
    total = arb(0)
    regimes: dict[int, str] = {}
    for k, g in G.items():
        if direct:
            Ik, reg = I_k_direct(k, l, u, e), "R4"
        else:
            Ik, reg = I_k_scaled(k, l, u, e)
        regimes[k] = reg
        total += g * Ik
    return total, G, regimes
