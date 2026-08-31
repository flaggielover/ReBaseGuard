"""Stopped-path simulation for the two evidence routes.

The residual coordinate is ``Z_t = eps_t - e``.

* **Route A** evaluates the score formula at ``e = 0``.  It needs no coupling
  to any other parameter value, so it runs in ``compact`` mode: innovations are
  drawn only for the paths that are still alive.
* **Route B** evaluates the conditional-mean map at ``e = +-h`` and differences
  it.  At ``h = 0.0125`` an uncoupled difference is hopeless, so the two runs
  must share the innovation stream path by path and step by step.  That is
  ``aligned`` mode: the innovation for step ``s`` is the same ``n_paths`` vector
  regardless of ``e``, drawn from a counter-based generator keyed on
  ``(seed, batch, step)``.

Both modes are exactly reproducible from ``(seed, batch)``; only ``aligned``
mode couples different ``e`` values.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .detectors import Detector
from .families import Family


@dataclass(frozen=True, slots=True)
class StoppedBatch:
    """Per-path stopped quantities for one batch at one parameter value."""

    e: float
    tau: np.ndarray            # stopping time, >= 1
    window: np.ndarray         # (n_paths, m_max) last increments, newest last
    score_sum: np.ndarray      # sum_{t<=tau} psi(Z_t)
    total: np.ndarray          # T_tau = sum_{t<=tau} Z_t
    unstopped: int
    max_steps_used: int

    def window_mean(self, m: int) -> np.ndarray:
        """``A_m = (1/min(m,tau)) sum_{r=0}^{min(m,tau)-1} Z_{tau-r}``."""
        m_max = self.window.shape[1]
        if m > m_max:
            raise ValueError(f"window buffer holds only {m_max} increments")
        w = np.minimum(m, self.tau)
        block = self.window[:, m_max - m:]
        keep = np.arange(m)[None, :] >= (m - w)[:, None]
        return np.where(keep, block, 0.0).sum(axis=1) / w

    def fixed_window_mean(self, m: int) -> np.ndarray:
        """``B_m`` -- the same numerator over the fixed denominator ``m``."""
        return self.window_mean(m) * np.minimum(m, self.tau) / m

    def short_correction(self, m: int) -> np.ndarray:
        """``1{tau<m} (1/tau - 1/m) T_tau S_tau`` -- the generalised
        random-denominator correction.  For the Gaussian score this is
        ``(1/tau - 1/m) T_tau^2 >= 0``; in general its sign is the sign of
        ``T_tau S_tau`` and is not determined."""
        short = self.tau < m
        factor = np.where(short, 1.0 / np.maximum(self.tau, 1) - 1.0 / m, 0.0)
        return factor * self.total * self.score_sum


class _State:
    __slots__ = ("e", "up", "down", "tau", "score_sum", "total", "window",
                 "active")

    def __init__(self, detector: Detector, e: float, n: int, m_max: int):
        self.e = e
        self.up, self.down = detector.new_state(n)
        self.tau = np.zeros(n, dtype=np.int64)
        self.score_sum = np.zeros(n)
        self.total = np.zeros(n)
        self.window = np.zeros((n, m_max))
        self.active = np.ones(n, dtype=bool)


def _advance(state: _State, detector: Detector, family: Family,
             eps: np.ndarray, idx: np.ndarray, step: int) -> None:
    z = eps - state.e
    state.up[idx], state.down[idx], crossed = detector.step(
        state.up[idx], state.down[idx], z, step
    )
    state.score_sum[idx] += family.psi(z)
    state.total[idx] += z
    if state.window.shape[1] > 1:
        state.window[idx, :-1] = state.window[idx, 1:]
    state.window[idx, -1] = z
    if crossed.any():
        done = idx[crossed]
        state.tau[done] = step
        state.active[done] = False


#: Philox emits four 64-bit words per counter increment, so a draw of ``n``
#: doubles advances the counter by roughly ``n/4``.  Consecutive ``(batch,
#: step)`` streams must therefore be separated by far more than ``n_paths``
#: counter values or they overlap and the "independent" innovations of
#: successive steps become shifted copies of each other.  ``STREAM_STRIDE``
#: reserves 2**64 counter values per stream, which is unreachable for any
#: batch size this campaign can run.
STREAM_STRIDE = 1 << 64


def stream_counter(batch: int, step: int) -> int:
    """Non-overlapping Philox counter for the innovation draw of one step."""
    return ((batch << 32) | step) * STREAM_STRIDE


def simulate_group(
    *,
    family: Family,
    detector: Detector,
    e_values: tuple[float, ...],
    n_paths: int,
    seed: int,
    batch: int,
    m_max: int,
    mode: str,
    max_steps: int = 250_000,
) -> list[StoppedBatch]:
    """Simulate one batch at each requested ``e``.

    ``mode='aligned'`` couples the ``e`` values through a counter-based stream;
    ``mode='compact'`` is only valid for a single ``e``.
    """
    if mode not in {"aligned", "compact"}:
        raise ValueError(f"unknown mode: {mode}")
    if mode == "compact" and len(e_values) != 1:
        raise ValueError("compact mode couples nothing and takes one e value")

    states = [_State(detector, e, n_paths, m_max) for e in e_values]
    compact_rng = np.random.Generator(np.random.PCG64([seed, batch]))
    steps_used = 0

    for step in range(1, max_steps + 1):
        if not any(state.active.any() for state in states):
            break
        steps_used = step
        if mode == "aligned":
            bits = np.random.Philox(key=seed, counter=stream_counter(batch, step))
            draw = family.sample(np.random.Generator(bits), (n_paths,))
            for state in states:
                idx = np.flatnonzero(state.active)
                if idx.size:
                    _advance(state, detector, family, draw[idx], idx, step)
        else:
            state = states[0]
            idx = np.flatnonzero(state.active)
            draw = family.sample(compact_rng, (int(idx.size),))
            _advance(state, detector, family, draw, idx, step)

    return [
        StoppedBatch(
            e=state.e,
            tau=state.tau,
            window=state.window,
            score_sum=state.score_sum,
            total=state.total,
            unstopped=int(state.active.sum()),
            max_steps_used=steps_used,
        )
        for state in states
    ]
