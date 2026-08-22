"""Stage C — multi-cycle simulator with a post-change mean shift.

Why a mean shift is a one-line change
-------------------------------------
The frozen reference error is `e = R_j - mu_j` and the monitored innovation is
`z_t = X_t - R_j`.  With `X_t ~ N(mu, 1)`, write `X_t = mu + W_t`, `W ~ N(0,1)`:

    z_t = mu + W_t - R_j = W_t - (R_j - mu) = W_t - e .

So a change `mu: 0 -> Delta` at a cycle boundary is EXACTLY the substitution
`e -> e - Delta`, with the recursion, the alarm rule, the reuse rule and the
innovation law all untouched.  Nothing about the frozen semantics changes; the
detector is not told a change happened.

Consequently, with `shift = 0` this simulator must reproduce the frozen Stage A
`rebaseguard_level4.multicycle.simulate_multicycle` bit-for-bit, and
`tests/test_detection.py` asserts exactly that.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

import numpy as np

from rebaseguard_level4.frozen import (
    H_FROZEN,
    K_FROZEN,
    alarm_direction,
    count_ties,
    cusum_update,
    fresh_statistic_scale,
    rebaseline,
)
from rebaseguard_level4.streams import STREAM_FRESH, STREAM_OBS, PerRowStream


@dataclass(frozen=True, slots=True)
class DetectionConfig:
    n_replicates: int
    burn_in: int                 # in-control cycles before the first change
    n_cycles_after: int          # cycles observed after each change
    rho: float
    shift: float                 # Delta; 0.0 reproduces the in-control chain
    master_seed: int
    n_changes: int = 1           # repeated changes, for recovery behaviour
    cycles_between: int = 0      # extra in-control cycles between changes
    m: int = 1
    k: float = K_FROZEN
    h: float = H_FROZEN
    max_steps: int = 20_000_000

    def validate(self) -> None:
        if self.k != K_FROZEN or self.h != H_FROZEN:
            raise ValueError("k and h are frozen at 1/2 and 5")
        if self.m != 1:
            raise ValueError("Stage C is scoped to m = 1")
        if not 0.0 <= self.rho <= 1.0:
            raise ValueError("rho must lie in [0, 1]")
        if self.n_changes < 1 or self.n_cycles_after < 1:
            raise ValueError("need at least one change and one post-change cycle")

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class DetectionResult:
    replicate: np.ndarray
    cycle_index: np.ndarray
    change_index: np.ndarray      # -1 during burn-in, else which change is active
    cycles_since_change: np.ndarray
    e_prev: np.ndarray
    e_next: np.ndarray
    tau: np.ndarray
    direction: np.ndarray
    config: DetectionConfig
    n_ties: int

    @property
    def total_cycles(self) -> int:
        c = self.config
        return c.burn_in + c.n_changes * (c.n_cycles_after + c.cycles_between)

    def detection_delays(self) -> np.ndarray:
        """tau of the first cycle after each change: shape (replicates, changes)."""
        first = (self.cycles_since_change == 0) & (self.change_index >= 0)
        return self.tau[first].reshape(self.config.n_replicates,
                                       self.config.n_changes)

    def by_replicate(self, name: str) -> np.ndarray:
        return getattr(self, name).reshape(self.config.n_replicates,
                                           self.total_cycles)


def simulate_detection(config: DetectionConfig) -> DetectionResult:
    """Run the reference chain through one or more post-change regimes."""
    config.validate()
    r = config.n_replicates
    k, h, rho = config.k, config.h, config.rho
    fresh_scale = fresh_statistic_scale(config.m)
    total = config.burn_in + config.n_changes * (config.n_cycles_after
                                                 + config.cycles_between)

    obs = PerRowStream(config.master_seed, STREAM_OBS, r)
    fresh = PerRowStream(config.master_seed, STREAM_FRESH, r)

    # cycle -> (change_index, cycles_since_change); -1 while still in control
    change_of = np.full(total, -1, dtype=np.int64)
    since_of = np.full(total, -1, dtype=np.int64)
    cursor = config.burn_in
    for c in range(config.n_changes):
        block = config.n_cycles_after + config.cycles_between
        for j in range(block):
            if cursor + j < total:
                change_of[cursor + j] = c
                since_of[cursor + j] = j
        cursor += block

    e = np.zeros(r)
    plus = np.zeros(r)
    minus = np.zeros(r)
    t = np.zeros(r, dtype=np.int64)
    completed = np.zeros(r, dtype=np.int64)
    applied = np.zeros(r, dtype=np.int64)   # how many shifts each row has taken

    shape = (r, total)
    out_e_prev = np.zeros(shape)
    out_e_next = np.zeros(shape)
    out_tau = np.zeros(shape, dtype=np.int64)
    out_dir = np.zeros(shape, dtype=np.int8)
    ties = 0

    # Apply any shift due at cycle 0 (only if burn_in == 0).
    def apply_due_shifts() -> None:
        nonlocal e
        due = np.zeros(r, dtype=np.int64)
        idx = completed
        inside = idx < total
        due[inside] = np.where(change_of[idx[inside]] >= 0,
                               change_of[idx[inside]] + 1, 0)
        need = due > applied
        if np.any(need):
            e[need] -= config.shift * (due[need] - applied[need])
            applied[need] = due[need]

    apply_due_shifts()

    for _ in range(config.max_steps):
        active = np.flatnonzero(completed < total)
        if active.size == 0:
            break
        x = obs.draw(active)
        z = x - e[active]
        new_plus, new_minus, up, down = cusum_update(
            plus[active], minus[active], z, k, h)
        plus[active] = new_plus
        minus[active] = new_minus
        t[active] += 1

        crossed = up | down
        if not crossed.any():
            continue
        ties += count_ties(up & crossed, down & crossed)
        done = active[crossed]
        mu_reuse = e[done] + z[crossed]          # m = 1: the alarm observation
        mu_fresh = fresh.draw(done) * fresh_scale
        e_new = rebaseline(mu_reuse, mu_fresh, rho)

        col = completed[done]
        out_e_prev[done, col] = e[done]
        out_e_next[done, col] = e_new
        out_tau[done, col] = t[done]
        out_dir[done, col] = alarm_direction(up[crossed], down[crossed])

        e[done] = e_new
        plus[done] = 0.0
        minus[done] = 0.0
        t[done] = 0
        completed[done] += 1
        apply_due_shifts()
    else:
        raise RuntimeError("detection run did not complete within max_steps")

    return DetectionResult(
        replicate=np.repeat(np.arange(r, dtype=np.int32), total),
        cycle_index=np.tile(np.arange(total, dtype=np.int32), r),
        change_index=np.tile(change_of.astype(np.int32), r),
        cycles_since_change=np.tile(since_of.astype(np.int32), r),
        e_prev=out_e_prev.ravel(), e_next=out_e_next.ravel(),
        tau=out_tau.ravel(), direction=out_dir.ravel(),
        config=config, n_ties=ties,
    )
