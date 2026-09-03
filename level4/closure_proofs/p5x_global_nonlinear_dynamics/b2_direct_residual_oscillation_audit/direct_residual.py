"""P5X: exact residual r and its exact gradient, combined BEFORE enclosure.

    r      = ghat - rho_1 - K_e ghat
    dr/dz+ = ghat_x - (K^{E+} ghat_x) + [ ghat(q(.,u)) - u ] phi(u+e) / w+
    dr/dz- = ghat_y - (K^{E-} ghat_y) + [ ghat(q(.,l)) - l ] phi(l+e) / w-

The two boundary contributions -- one from rho_1's moving limit, one from the
kernel's -- are ALGEBRAICALLY COMBINED into a single bracket before any interval
evaluation.  Uses the R8-corrected w^- on the minus chart.
"""
from __future__ import annotations
import sys
from pathlib import Path
from flint import arb

_NS = Path(__file__).resolve().parents[1]
for _p in (_NS / "sr_full_cell_prototype", _NS / "compute_optimization_r6_minimal_evaluator",
           _NS / "compute_optimization_r4_xi_reformulation",
           Path(__file__).resolve().parents[5] / "rebaseguard-proof" / "src"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
import sr_prototype as SP                                        # noqa: E402
from minimal_evaluator import I_k, live_limits, sr_constants     # noqa: E402

HALF = None


def _pows(w, n):
    P = [arb(1)] * (n + 1)
    for i in range(1, n + 1):
        P[i] = P[i - 1] * w
    return P


def ghat_at_image(ca, zp, zm, z, A):
    """ghat evaluated at the updated state q(zeta, z)."""
    n = len(ca) - 1
    half = arb(1) / arb(2)
    a1 = (arb(1) / A + zp) * (z - half).exp()
    a2 = (arb(1) / A + zm) * (-z - half).exp()
    Pa, Qa = _pows(a1, n), _pows(a2, n)
    return sum((ca[i][j] * Pa[i] * Qa[j] for i in range(n + 1) for j in range(n + 1)), arb(0))


def _weighted_kernel(ca, zp, zm, e, A, l, u, shift, axis):
    """(K^{E+/-} ghat_{x/y})(zeta) via the R6 closed form.

    E^+ = e^{z-1/2} shifts k by +1; E^- = e^{-z-1/2} shifts k by -1; both carry
    a constant factor e^{-1/2}.  No z-panels, no softplus.
    """
    n = len(ca) - 1
    half = arb(1) / arb(2)
    P, Q = _pows(arb(1) / A + zp, n), _pows(arb(1) / A + zm, n)
    G: dict[int, arb] = {}
    for i in range(n + 1):
        for j in range(n + 1):
            if axis == 0:
                if i < 1:
                    continue
                ii, jj, c = i - 1, j, ca[i][j] * arb(i)
            else:
                if j < 1:
                    continue
                ii, jj, c = i, j - 1, ca[i][j] * arb(j)
            k = ii - jj + shift
            G[k] = G.get(k, arb(0)) + c * P[ii] * Q[jj] * (-arb(ii + jj) / arb(2)).exp()
    tot = sum((g * I_k(k, l, u, e)[0] for k, g in G.items()), arb(0))
    return tot * (-half).exp()


def grad_r(ca, zp, zm, e, A):
    """Exact (dr/dzeta+, dr/dzeta-), terms combined before evaluation."""
    n = len(ca) - 1
    l, u = live_limits(zp, zm, A)
    wp, wm = arb(1) / A + zp, arb(1) / A + zm
    TP = (arb(2) * arb.pi()).sqrt()
    Pz, Qz = _pows(zp, n), _pows(zm, n)
    gx = sum((ca[i][j] * arb(i) * Pz[i - 1] * Qz[j]
              for i in range(1, n + 1) for j in range(n + 1)), arb(0))
    gy = sum((ca[i][j] * arb(j) * Pz[i] * Qz[j - 1]
              for i in range(n + 1) for j in range(1, n + 1)), arb(0))
    Kx = _weighted_kernel(ca, zp, zm, e, A, l, u, 1, 0)
    Ky = _weighted_kernel(ca, zp, zm, e, A, l, u, -1, 1)
    phiu = (-(u + e) * (u + e) / arb(2)).exp() / TP
    phil = (-(l + e) * (l + e) / arb(2)).exp() / TP
    bu = (ghat_at_image(ca, zp, zm, u, A) - u) * phiu / wp      # COMBINED bracket
    bl = (ghat_at_image(ca, zp, zm, l, A) - l) * phil / wm      # COMBINED, uses w^-
    return gx - Kx + bu, gy - Ky + bl, {"gx": gx, "Kx": Kx, "bu": bu,
                                        "gy": gy, "Ky": Ky, "bl": bl}
