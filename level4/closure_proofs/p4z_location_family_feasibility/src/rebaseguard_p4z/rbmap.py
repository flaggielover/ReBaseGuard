"""Candidate B -- RB-MAP: Rao-Blackwellised conditional-mean map, differenced.

Estimand: the same ``Gamma_{D,m,f} = -g_m'(0)`` reached from the *other* side of
Theorem G1a, through the map ``g_m(e) = E_e[A_m]`` itself.  This is the role the
historical Route B played and it is the reason a two-route correspondence is
evidence about the score identity at all: RB-MAP never evaluates ``psi``, never
forms a likelihood ratio and never changes measure.  It runs the frozen detector
at shifted parameter values and differences the result.

**Derivation.**  Exactly as for RB-SCORE, but with the score prefix absent:

    g_m(e) = sum_{n>=1} E_e[ 1{tau_e >= n} (J1^{(e)} + B_{n,m} J0^{(e)}) / w ]

where ``J0^{(e)}, J1^{(e)}`` are the alarm-set mass and partial mean under
``f_e``, i.e. the same functionals evaluated at endpoints shifted by ``e``
(``analytic.alarm_integrals``).  Common random numbers couple ``+h`` and ``-h``
through the frozen Philox stream, and the frozen Richardson combination
``(4 D(h/2) - D(h)) / 3`` is applied per batch, unchanged.

**Moments.**  ``|J1^{(e)}| <= E|eps| + |e|`` and ``|J0^{(e)}| <= 1``, so the
accumulated map value is bounded by ``C tau`` and the differenced value by
``C tau / h``.  With L1's geometric ``tau`` this again has every moment finite,
uniformly in ``h``.  The historical Route-B summand does not: on the rare paths
where the two shifted runs stop at different times its value is
``O(Z_tau / h)``, which carries the family's full tail.

**Honest limitation.**  RB-MAP uses ``f`` and ``F`` analytically, where the
historical Route B used only the detector.  It is therefore *less* independent
than Route B was.  What it does **not** use is the score identity G1a, the score
function ``psi``, or any change of measure -- and G1a is the object under test.
So RB-MAP remains admissible independent evidence for the identity, at a
disclosed reduction in independence that ``VALIDITY_AUDIT.md`` records.
"""

from __future__ import annotations

import numpy as np

from .analytic import FamilyKit, alarm_bounds, alarm_integrals

K_FROZEN = 0.5


def rb_map_batch(
    *,
    family,
    kit: FamilyKit,
    detector_kind: str,
    threshold: float,
    m_grid: tuple[int, ...],
    e_values: tuple[float, ...],
    n_paths: int,
    seed: int,
    batch: int,
    max_steps: int,
    new_state,
    step_fn,
    stream_counter,
) -> dict[float, dict[int, np.ndarray]]:
    """Per-path RB estimates of ``g_m(e)`` at each ``e``, CRN-coupled."""
    m_max = max(m_grid)
    states: dict[float, dict] = {}
    for e in e_values:
        up, down = new_state(n_paths)
        states[e] = {
            "up": up, "down": down,
            "active": np.ones(n_paths, dtype=bool),
            "window": np.zeros((n_paths, max(1, m_max - 1))),
            "acc": {m: np.zeros(n_paths) for m in m_grid},
        }

    for step in range(1, max_steps + 1):
        if not any(s["active"].any() for s in states.values()):
            break
        bits = np.random.Philox(key=seed, counter=stream_counter(batch, step))
        draw = family.sample(np.random.Generator(bits), (n_paths,))
        for e in e_values:
            s = states[e]
            idx = np.flatnonzero(s["active"])
            if idx.size == 0:
                continue
            u, d = s["up"][idx], s["down"][idx]
            lower, upper = alarm_bounds(detector_kind, threshold, u, d, K_FROZEN)
            j0, j1, _, _ = alarm_integrals(kit, lower, upper, shift=e)
            win = s["window"]
            for m in m_grid:
                w = min(m, step)
                b = win[idx, win.shape[1] - (w - 1):].sum(axis=1) if w > 1 else 0.0
                s["acc"][m][idx] += (j1 + b * j0) / w
            z = draw[idx] - e
            new_up, new_down, crossed = step_fn(u, d, z, step)
            s["up"][idx], s["down"][idx] = new_up, new_down
            if win.shape[1] > 1:
                win[idx, :-1] = win[idx, 1:]
            win[idx, -1] = z
            if crossed.any():
                s["active"][idx[crossed]] = False

    return {e: states[e]["acc"] for e in e_values}


def rb_map_derivative_batch(
    *, fd_steps: tuple[float, float], m_grid: tuple[int, ...], **kwargs
) -> dict[int, np.ndarray]:
    """Per-path frozen Richardson combination ``(4 D(h/2) - D(h)) / 3``."""
    coarse, fine = fd_steps
    if not np.isclose(coarse, 2.0 * fine):
        raise ValueError("fd_steps must be (h, h/2), the frozen convention")
    out: dict[int, np.ndarray] = {}
    per_step: dict[float, dict[int, np.ndarray]] = {}
    for h in (coarse, fine):
        g = rb_map_batch(m_grid=m_grid, e_values=(h, -h), **kwargs)
        per_step[h] = {m: -(g[h][m] - g[-h][m]) / (2.0 * h) for m in m_grid}
    for m in m_grid:
        out[m] = (4.0 * per_step[fine][m] - per_step[coarse][m]) / 3.0
    return out
