"""Candidate Route-B estimators for the P4X R0 pilot.

Every method here estimates the *same* quantity as the frozen Priority-4
Route B --

    Gamma_{D,m,f} = -d/de E_e[A_m] at e = 0

-- by a common-random-number central difference of the conditional-mean map,
with the Richardson combination ``(4 D(h/2) - D(h))/3`` formed per block.  No
method changes the theorem, the target quantity, the detector, the family, the
window, or the meaning of the original 3% / |z| <= 4 tolerance.  The frozen
Priority-4 simulator is imported read-only.

Methods
-------
``baseline``    the frozen Route-B estimator, re-run under a fresh seed
                namespace.  This is the reference for every variance ratio.
``reflection``  for a *symmetric* family under a *reflection-equivariant*
                detector, the ``-h`` run is the exact mirror of the ``+h`` run,
                so it need not be simulated.  Same estimand, same variance,
                half the innovations.  The mirror identity is verified
                numerically rather than assumed.
``coarse_h``    the identical estimator at a larger finite-difference step.
                Central-difference variance scales as ``1/h^2``; the ``O(h^2)``
                bias is removed to ``O(h^4)`` by the same Richardson
                combination and is measured by the step ladder, never assumed.
``g2_control``  a control variate built from Corollary G2: the same window mean
                evaluated at a *deterministic* horizon, whose expectation is
                known exactly.  Included because it is the only analytically
                known quantity available on these paths; the pilot measures
                whether it carries any usable variance.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

_P4 = Path(__file__).resolve().parents[3] / "p4_theory_generalization"
if str(_P4 / "src") not in sys.path:
    sys.path.insert(0, str(_P4 / "src"))

from rebaseguard_p4_general.detectors import Detector  # noqa: E402
from rebaseguard_p4_general.families import Family  # noqa: E402
from rebaseguard_p4_general.simulate import simulate_group  # noqa: E402


@dataclass(frozen=True, slots=True)
class BlockResult:
    """One block's per-``m`` Richardson value, plus per-path diagnostics."""

    richardson: dict[int, float]
    per_step: dict[float, dict[int, float]]
    decoupled_fraction: float
    #: per-path estimator contributions at the coarse step, m = 1, kept only
    #: when explicitly requested (they are what the tail diagnostic needs)
    contributions: np.ndarray | None
    innovations_drawn: int


def _window_difference(plus, minus, m: int, step: float) -> np.ndarray:
    """Per-path contribution ``-(A_m(+h) - A_m(-h)) / (2h)``.

    On any path where the two runs stop at the same time with the same window
    length, ``Z^+ - Z^- = -2h`` identically, so the contribution is exactly
    ``1``.  All of this estimator's variance therefore lives on the set where
    the shifted runs decouple.
    """
    return -((plus.window_mean(m) - minus.window_mean(m)) / (2.0 * step))


def _reflect(batch):
    """Mirror a stopped batch: ``tau`` unchanged, residual quantities negated.

    Valid only for a symmetric family under a reflection-equivariant detector,
    where the run at ``(-e, -eps)`` is pathwise the mirror of ``(+e, +eps)``.
    """
    return type(batch)(
        e=-batch.e, tau=batch.tau, window=-batch.window,
        score_sum=-batch.score_sum, total=-batch.total,
        unstopped=batch.unstopped, max_steps_used=batch.max_steps_used,
    )


def run_block(
    *,
    family: Family,
    detector: Detector,
    m_grid: tuple[int, ...],
    paths: int,
    seed: int,
    block: int,
    fd_steps: tuple[float, float],
    max_steps: int,
    method: str,
    keep_contributions: bool = False,
) -> BlockResult:
    """Simulate one block under one candidate method."""
    coarse, fine = fd_steps
    if not np.isclose(coarse, 2.0 * fine):
        raise ValueError("fd_steps must be (h, h/2) for Richardson extrapolation")

    m_max = max(m_grid)
    per_step: dict[float, dict[int, float]] = {}
    decoupled = 0.0
    contributions = None
    drawn = 0

    for step in fd_steps:
        if method == "reflection":
            # Only the +h run is simulated; the -h run is its exact mirror.
            (plus,) = simulate_group(
                family=family, detector=detector, e_values=(step,),
                n_paths=paths, seed=seed, batch=block, m_max=m_max,
                mode="aligned", max_steps=max_steps,
            )
            minus = _reflect(plus)
            drawn += paths * plus.max_steps_used
        else:
            plus, minus = simulate_group(
                family=family, detector=detector, e_values=(step, -step),
                n_paths=paths, seed=seed, batch=block, m_max=m_max,
                mode="aligned", max_steps=max_steps,
            )
            drawn += paths * plus.max_steps_used

        per_step[step] = {
            m: float(_window_difference(plus, minus, m, step).mean())
            for m in m_grid
        }
        if step == coarse:
            decoupled = float((plus.tau != minus.tau).mean())
            if keep_contributions:
                contributions = _window_difference(plus, minus, 1, step)

    richardson = {
        m: (4.0 * per_step[fine][m] - per_step[coarse][m]) / 3.0
        for m in m_grid
    }
    return BlockResult(richardson, per_step, decoupled, contributions, drawn)


def g2_control(
    *,
    family: Family,
    detector: Detector,
    m: int,
    paths: int,
    seed: int,
    block: int,
    step: float,
    horizon: int,
) -> tuple[float, float]:
    """Corollary-G2 control variate at a deterministic horizon.

    Under deterministic stopping ``tau == n``, Corollary G2(a) gives
    ``E_e[A_m] = -e`` exactly, so this statistic has known expectation ``1``.
    Returns ``(mean, variance)`` of the per-path control.
    """
    plus, minus = simulate_group(
        family=family, detector=Detector("deterministic", float(horizon)),
        e_values=(step, -step), n_paths=paths, seed=seed, batch=block,
        m_max=m, mode="aligned", max_steps=horizon,
    )
    values = _window_difference(plus, minus, m, step)
    return float(values.mean()), float(values.var(ddof=1))


def batch_summary(values: list[float]) -> dict[str, float]:
    """Block-mean summary, matching the frozen Priority-4 convention."""
    arr = np.asarray(values, dtype=float)
    n = arr.size
    sd = float(arr.std(ddof=1)) if n > 1 else float("nan")
    return {
        "mean": float(arr.mean()),
        "block_sd": sd,
        "se": sd / np.sqrt(n) if n > 1 else float("nan"),
        "blocks": int(n),
    }


def hill_tail_index(x: np.ndarray, k: int | None = None) -> dict[str, float]:
    """Hill estimator of the tail index ``alpha`` of ``|x|``.

    ``alpha >= 2`` means the summand has finite variance and block means
    converge at ``n^{-1/2}``.  ``alpha < 2`` means it does not, and the
    convergence rate degrades to ``n^{1/alpha - 1}``.
    """
    a = np.abs(np.asarray(x, dtype=float))
    a = a[np.isfinite(a) & (a > 0)]
    a.sort()
    n = a.size
    if n < 100:
        return {"alpha": float("nan"), "k": 0, "n": n}
    if k is None:
        k = max(50, int(0.005 * n))
    k = min(k, n - 1)
    top = a[-(k + 1):]
    alpha = 1.0 / float(np.mean(np.log(top[1:] / top[0])))
    return {
        "alpha": alpha,
        "k": int(k),
        "n": int(n),
        "implied_block_mean_rate_exponent": (
            -0.5 if alpha >= 2.0 else (1.0 / alpha - 1.0)
        ),
    }
