"""P7 analysis primitives: response-curve interpolants and derived quantities.

Every function here is deterministic given the two result files; no randomness,
no fitting beyond the local polynomial fits that are named in the docstrings.
"""
from __future__ import annotations

import json

import numpy as np

from .config import RESULTS


def load_curves() -> dict:
    return json.loads((RESULTS / "response_curves.json").read_text())


class ResponseCurves:
    """Even run-length response ``A`` and odd reuse-drift responses ``g_m``.

    ``A`` is interpolated in ``|x|`` with a shape-preserving monotone cubic and
    held flat beyond the grid; ``g_m`` likewise, with the odd extension
    ``g(-x) = -g(x)``.  Both extensions are conservative: ``A`` and ``|g|`` are
    already nearly flat at the right edge of the grid.  The fraction of sample
    points that fall outside the grid is reported by every consumer.
    """

    def __init__(self, rows: list[dict], m_grid):
        rows = [r for r in rows if not r["symmetry_check"]]
        rows.sort(key=lambda r: r["x"])
        self.x = np.array([r["x"] for r in rows])
        assert self.x[0] == 0.0 and (np.diff(self.x) > 0).all()
        self.arl = np.array([r["arl"] for r in rows])
        self.arl_se = np.array([r["arl_se"] for r in rows])
        self.m_grid = tuple(int(m) for m in m_grid)
        self.g_grid = {m: np.array([r["g"][str(m)] for r in rows])
                       for m in self.m_grid}
        self.g_se = {m: np.array([r["g_se"][str(m)] for r in rows])
                     for m in self.m_grid}
        self.gamma_tilde = {int(k): v for k, v in rows[0]["gamma_tilde"].items()}
        self.gamma_tilde_se = {int(k): v
                               for k, v in rows[0]["gamma_tilde_se"].items()}
        from scipy.interpolate import PchipInterpolator
        self._A = PchipInterpolator(self.x, self.arl, extrapolate=False)
        self._G = {m: PchipInterpolator(self.x, self.g_grid[m],
                                        extrapolate=False)
                   for m in self.m_grid}

    def A(self, x):
        """Run-length response, even, held flat outside the grid."""
        ax = np.clip(np.abs(np.asarray(x, dtype=float)), 0.0, self.x[-1])
        return self._A(ax)

    def g(self, m, x):
        ax = np.clip(np.abs(np.asarray(x, dtype=float)), 0.0, self.x[-1])
        return np.sign(x) * self._G[int(m)](ax)

    def out_of_grid_fraction(self, x) -> float:
        return float(np.mean(np.abs(np.asarray(x)) > self.x[-1]))

    # ---- derived scalars -------------------------------------------------
    def arl_curvature(self, r: float = 0.05) -> tuple[float, float]:
        """``(c2, A''(0))`` from the even fit ``A(x) ~ A(0)(1 - c2 x^2)`` on |x|<=r.

        Least squares in ``x^2`` through the grid points inside ``r``; ``A`` is
        even so no linear term is admissible.
        """
        sel = (self.x > 0) & (self.x <= r)
        y = 1.0 - self.arl[sel] / self.arl[0]
        c2 = float(np.sum(y * self.x[sel] ** 2) / np.sum(self.x[sel] ** 4))
        return c2, -2.0 * c2 * float(self.arl[0])

    def linearisation_radius(self, m: int, tol: float = 0.10) -> float:
        """Largest grid ``r`` with ``|g_m(x)/x + GammaTilde| <= tol*GammaTilde``."""
        gt = self.gamma_tilde[int(m)]
        r = 0.0
        for xi, gi in zip(self.x[1:], self.g_grid[int(m)][1:]):
            if abs(gi / xi + gt) <= tol * gt:
                r = float(xi)
            else:
                break
        return r

    def c_r(self, m: int, r: float) -> float:
        """``inf_{0<|x|<=r} (-g_m(x)/x)`` over the grid points inside ``r``."""
        sel = (self.x > 0) & (self.x <= r + 1e-12)
        return float(np.min(-self.g_grid[int(m)][sel] / self.x[sel]))

    def g_sup(self, m: int) -> float:
        return float(np.max(np.abs(self.g_grid[int(m)])))


def gamma_eff(curves: ResponseCurves, m: int, e: np.ndarray) -> float:
    """``Gamma_eff = -E[e g_m(e)] / E[e^2]`` under an empirical reference law."""
    e = np.asarray(e, dtype=float)
    return float(-np.mean(e * curves.g(m, e)) / np.mean(e ** 2))


def bootstrap_ci(values: np.ndarray, n_boot: int = 10_000, alpha: float = 0.05,
                 seed: int = 20260831) -> tuple[float, float]:
    """Percentile bootstrap of the mean over the replicate axis."""
    rng = np.random.default_rng(seed)
    n = values.size
    idx = rng.integers(0, n, size=(n_boot, n))
    means = values[idx].mean(axis=1)
    return (float(np.quantile(means, alpha / 2)),
            float(np.quantile(means, 1 - alpha / 2)))


def ratio_ci(num: np.ndarray, den_mean: float, den_se: float,
             n_boot: int = 10_000, seed: int = 20260831) -> tuple[float, float]:
    """Percentile bootstrap for ``mean(num)/den`` with an independent denominator.

    The two cells are independent runs, so the denominator is resampled from its
    own normal sampling law rather than pretending it is fixed.
    """
    rng = np.random.default_rng(seed)
    n = num.size
    idx = rng.integers(0, n, size=(n_boot, n))
    num_b = num[idx].mean(axis=1)
    den_b = rng.normal(den_mean, den_se, size=n_boot)
    r = num_b / den_b
    return float(np.quantile(r, 0.025)), float(np.quantile(r, 0.975))


def verdict(rel_effect: float, lo: float, hi: float) -> str:
    """Pre-committed three-way label (EXPERIMENT_DESIGN.md section 7)."""
    if lo <= 0.0 <= hi:
        return "INCONCLUSIVE"
    if abs(rel_effect) > 0.10 and min(abs(lo), abs(hi)) > 0.05:
        return "PRACTICALLY_MATERIAL"
    return "STATISTICALLY_RESOLVED"


# ---------------------------------------------------------------------------
# Selection-bias decomposition  g_m(x) = -x + h_m(x)
#
# Writing z_t = eps_t - e with eps_t iid N(0,1), the reuse statistic is
# zbar_m = (1/w) sum_{r<w} eps_{tau-r} - e, so
#
#     g_m(x) = E_x[zbar_m] = -x + h_m(x),
#     h_m(x) = E_x[(1/w) sum_{r<w} eps_{tau-r}]
#
# is exactly the STOPPING-SELECTION BIAS: the mean of the last w raw innovations
# of the stopped path.  It is odd, bounded, and vanishes at x = 0.  In these
# terms the P1/P2 gain is GammaTilde = 1 - h'(0), so
#
#     lambda = rho (1 - GammaTilde) = rho h'(0),      rho_c = 1/|h'(0)|,
#
# i.e. the entire P3 multiplier is rho times the slope of the selection bias.
# ---------------------------------------------------------------------------

def h_grid(curves: "ResponseCurves", m: int) -> np.ndarray:
    return curves.g_grid[int(m)] + curves.x


def h(curves: "ResponseCurves", m: int, x) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    return curves.g(m, x) + np.clip(x, -curves.x[-1], curves.x[-1])


def beta_r(curves: "ResponseCurves", m: int, r: float) -> float:
    """``inf_{0<|x|<=r} (-h_m(x)/x)``; tends to ``GammaTilde - 1 = 1/rho_c``."""
    sel = (curves.x > 0) & (curves.x <= r + 1e-12)
    return float(np.min(-h_grid(curves, m)[sel] / curves.x[sel]))


def h_sup(curves: "ResponseCurves", m: int) -> float:
    return float(np.max(np.abs(h_grid(curves, m))))


def gamma_eff_from_h(curves: "ResponseCurves", m: int, e: np.ndarray) -> float:
    """``Gamma_eff = 1 - E[e h(e)]/E[e^2]``; identical to ``gamma_eff``."""
    e = np.asarray(e, dtype=float)
    return float(1.0 - np.mean(e * h(curves, m, e)) / np.mean(e ** 2))
