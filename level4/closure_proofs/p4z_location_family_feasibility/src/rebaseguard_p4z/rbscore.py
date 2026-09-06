"""Candidate A -- RB-SCORE: Rao-Blackwellised score route.

Estimand, unchanged from Theorem G1a of the frozen P4 ``THEOREM.md``:

    Gamma_{D,m,f} = E_0[ A_m S_tau^psi ],
    A_m = (1/w) sum_{r=0}^{w-1} Z_{tau-r},  w = min(m, tau),
    S_tau^psi = sum_{t=1}^{tau} psi(Z_t),   psi = -f'/f.

**Derivation.**  Decompose over the alarm step.  ``{tau >= n}`` is
``F_{n-1}``-measurable, and on it the event ``{tau = n}`` is exactly
``{Z_n notin I(u_{n-1}, d_{n-1})}`` because both frozen detectors are Markov in
their charts (``analytic.py``, bounded-survival lemma).  Writing
``P_{n-1} = sum_{t<n} psi(Z_t)`` and ``B_{n,m} = sum_{r=1}^{w-1} Z_{n-r}`` --
both ``F_{n-1}``-measurable -- and ``w = min(m, n)``,

    E[ 1{tau = n} A_m S_tau^psi | F_{n-1} ]
        = (1{tau >= n} / w) * ( P_{n-1} (J1 + B_{n,m} J0) + (J2 + B_{n,m} J3) )

with ``J0..J3`` the four alarm-set integrals of ``analytic.py`` evaluated at the
pre-step charts.  Summing over ``n`` and taking expectations,

    Gamma = sum_{n>=1} E[ 1{tau >= n} h_n ],        (RB)

so the per-path estimator is: run the ordinary frozen path, accumulate ``h_n``
from the pre-step state at every step ``n = 1..tau``, and stop.

**Exactness.**  (RB) is an identity, not an approximation.  The estimator is
unbiased for the same ``Gamma``; nothing about the detector recursion, the
window convention ``w = min(m, tau)``, the inclusion of the alarm-causing
increment, the random denominator, or the stopping rule is changed.  The
realised value of ``Z_tau`` is drawn (it is what stops the path) but never
enters the estimator's value -- which is the entire point, because it is the
only unbounded coordinate.

**Moments.**  ``|B_{n,m}| <= (m-1) c_D`` and ``|P_{n-1}| <= M (n-1)`` for a
bounded-score family, and ``|J0|, |J1|, |J2|, |J3|`` are bounded by ``1``,
``E|eps|``, ``1 + 2 c_D sup f`` and ``2 sup f``.  So ``|h_n| <= C n`` and the
per-path value is bounded by ``C tau^2``.  Discharge lemma L1 gives ``tau`` a
geometric tail uniformly on the ``e``-neighbourhood, so **every** moment of the
RB-SCORE per-path summand is finite -- against an infinite *second* moment for
the historical Route-A summand whenever ``E[eps^2] = infinity``.

**Neutrality control.**  Under a deterministic ``tau = n0`` the alarm set is
empty for ``n < n0`` and all of ``R`` at ``n0``, giving ``J0 = 1``, ``J1 = 0``,
``J2 = E[eps psi] = 1``, ``J3 = E[psi] = 0`` and hence
``h_{n0} = (P_{n0-1} B + 1) / w``.  Since ``E[psi(Z_t) Z_s] = 1{t = s}``, the
window contributes ``w - 1`` and ``Gamma = ((w-1) + 1)/w = 1`` exactly, for
every ``m`` and every family -- the exact statement of Corollary G2(b).  This
is a closed-form control on the implementation, not a measurement.
"""

from __future__ import annotations

import numpy as np

from .analytic import FamilyKit, alarm_bounds, alarm_integrals

K_FROZEN = 0.5


def rb_score_batch(
    *,
    family,
    kit: FamilyKit,
    detector_kind: str,
    threshold: float,
    m_grid: tuple[int, ...],
    n_paths: int,
    rng: np.random.Generator,
    max_steps: int,
    new_state,
    step_fn,
) -> tuple[dict[int, np.ndarray], int, int]:
    """Per-path RB-SCORE values for one batch.

    ``new_state`` and ``step_fn`` are the *frozen* detector callables; P4Z never
    reimplements the recursion.  Returns ``(values_by_m, unstopped, steps)``.
    """
    m_max = max(m_grid)
    up, down = new_state(n_paths)
    prefix = np.zeros(n_paths)
    window = np.zeros((n_paths, max(1, m_max - 1)))
    acc = {m: np.zeros(n_paths) for m in m_grid}
    active = np.ones(n_paths, dtype=bool)
    steps_used = 0

    for step in range(1, max_steps + 1):
        idx = np.flatnonzero(active)
        if idx.size == 0:
            break
        steps_used = step
        u, d = up[idx], down[idx]
        lower, upper = alarm_bounds(detector_kind, threshold, u, d, K_FROZEN)
        j0, j1, j2, j3 = alarm_integrals(kit, lower, upper)
        pre = prefix[idx]
        for m in m_grid:
            w = min(m, step)
            if w > 1:
                block = window[idx, window.shape[1] - (w - 1):]
                b = block.sum(axis=1)
            else:
                b = 0.0
            acc[m][idx] += (pre * (j1 + b * j0) + (j2 + b * j3)) / w
        z = family.sample(rng, (int(idx.size),))
        new_up, new_down, crossed = step_fn(u, d, z, step)
        up[idx], down[idx] = new_up, new_down
        prefix[idx] += family.psi(z)
        if window.shape[1] > 1:
            window[idx, :-1] = window[idx, 1:]
        window[idx, -1] = z
        if crossed.any():
            active[idx[crossed]] = False

    return acc, int(active.sum()), steps_used
