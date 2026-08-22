"""GATE 4.1 -- repeated-cycle simulator (the Multi-Cycle Oracle).

One *cycle* is::

    E_j  ->  monitor with reference E_j  ->  stopping time tau_j
         ->  selected alarm data (terminal window W_{tau,m}, direction)
         ->  re-baselining rule  ->  E_{j+1}

The detector recursion is literally the frozen one (``frozen.cusum_update``);
the only Level 4 additions are the reference offset ``Z_t = X_t - E_j``, the
minimum-dwell convention for ``m >= 2`` and the re-baselining rule.  The
detector state is fully reset at every cycle boundary, per the frozen model.

Statistical unit
----------------
The **replicate** is the statistical unit.  Cycles within a replicate are a
serially dependent Markov chain and are *not* independent observations; all
inference in ``metrics.py`` aggregates within a replicate first and then
resamples replicates.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

import numpy as np

from .frozen import (
    H_FROZEN,
    K_FROZEN,
    alarm_direction,
    count_ties,
    cusum_update,
    fresh_statistic_scale,
    rebaseline,
)
from .streams import STREAM_FRESH, STREAM_OBS, PerRowStream


@dataclass(frozen=True, slots=True)
class MultiCycleConfig:
    """A complete, hashable description of one multi-cycle experiment."""

    n_replicates: int
    n_cycles: int          # retained cycles per replicate (after burn-in)
    burn_in: int           # discarded leading cycles per replicate
    rho: float
    m: int
    master_seed: int
    e0: float = 0.0
    k: float = K_FROZEN
    h: float = H_FROZEN
    max_steps: int = 20_000_000
    detector: str = "frozen_two_sided_cusum"
    policy: str = "mixed_reuse"   # rho=0 -> fresh, rho=1 -> full reuse

    def validate(self) -> None:
        if self.detector != "frozen_two_sided_cusum":
            raise ValueError("Gate 4.1 targets the frozen two-sided CUSUM only")
        if self.k != K_FROZEN or self.h != H_FROZEN:
            raise ValueError("k and h are frozen at 1/2 and 5")
        if self.n_replicates < 1 or self.n_cycles < 1 or self.burn_in < 0:
            raise ValueError("invalid replicate/cycle configuration")
        if self.m < 1:
            raise ValueError("m must be a positive integer")
        if not 0.0 <= self.rho <= 1.0:
            raise ValueError("rho must lie in [0, 1]")

    @property
    def policy_label(self) -> str:
        if self.rho == 0.0:
            return "fresh"
        if self.rho == 1.0:
            return "full_reuse"
        return "partial_reuse"

    def as_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["policy_label"] = self.policy_label
        return payload


@dataclass(slots=True)
class CycleTable:
    """Cycle-level raw output.  All arrays are flat, length R*(burn_in+n_cycles)."""

    replicate: np.ndarray
    cycle_index: np.ndarray        # 0-based, counted from the first cycle ever run
    in_burn_in: np.ndarray
    e_prev: np.ndarray             # E_j, reference error monitored during the cycle
    e_next: np.ndarray             # E_{j+1}
    tau: np.ndarray                # stopping time of the cycle
    direction: np.ndarray          # +1 up-arm alarm, -1 down-arm alarm
    mu_reuse: np.ndarray           # stopping-selected statistic (1/m) sum X_{tau-r}
    mu_fresh: np.ndarray           # independent matched-information statistic
    window_sum: np.ndarray         # W_{tau,m} = sum_{r=0}^{m-1} Z_{tau-r}
    t_tau: np.ndarray              # T_tau = sum_{t=1}^{tau} Z_t (terminal increment incl.)
    z_tau: np.ndarray              # the innovation that fired the alarm
    s_plus_terminal: np.ndarray    # detector state summary, post-update
    s_minus_terminal: np.ndarray
    config: MultiCycleConfig
    n_ties: int
    n_steps_simulated: int

    @property
    def shape(self) -> tuple[int, int]:
        total = self.config.burn_in + self.config.n_cycles
        return self.config.n_replicates, total

    def columns(self) -> dict[str, np.ndarray]:
        return {
            "replicate": self.replicate,
            "cycle_index": self.cycle_index,
            "in_burn_in": self.in_burn_in,
            "e_prev": self.e_prev,
            "e_next": self.e_next,
            "tau": self.tau,
            "direction": self.direction,
            "mu_reuse": self.mu_reuse,
            "mu_fresh": self.mu_fresh,
            "window_sum": self.window_sum,
            "t_tau": self.t_tau,
            "z_tau": self.z_tau,
            "s_plus_terminal": self.s_plus_terminal,
            "s_minus_terminal": self.s_minus_terminal,
            "rho": np.full(self.replicate.size, self.config.rho),
            "m": np.full(self.replicate.size, self.config.m, dtype=np.int32),
        }

    def post_burn_in(self) -> "CycleTable":
        """A view restricted to retained cycles, reshaped (R, n_cycles)."""
        keep = ~self.in_burn_in.astype(bool)
        return CycleTable(
            **{
                name: getattr(self, name)[keep]
                for name in (
                    "replicate", "cycle_index", "in_burn_in", "e_prev", "e_next",
                    "tau", "direction", "mu_reuse", "mu_fresh", "window_sum",
                    "t_tau", "z_tau", "s_plus_terminal", "s_minus_terminal",
                )
            },
            config=self.config,
            n_ties=self.n_ties,
            n_steps_simulated=self.n_steps_simulated,
        )

    def by_replicate(self, name: str) -> np.ndarray:
        """Reshape one retained-cycle column to (n_replicates, n_cycles)."""
        return getattr(self, name).reshape(
            self.config.n_replicates, self.config.n_cycles
        )


def simulate_multicycle(config: MultiCycleConfig) -> CycleTable:
    """Run the multi-cycle oracle.  Deterministic given ``config``."""
    config.validate()
    r = config.n_replicates
    m = config.m
    k, h = config.k, config.h
    rho = config.rho
    total_cycles = config.burn_in + config.n_cycles
    fresh_scale = fresh_statistic_scale(m)

    obs = PerRowStream(config.master_seed, STREAM_OBS, r)
    fresh = PerRowStream(config.master_seed, STREAM_FRESH, r)

    e = np.full(r, float(config.e0))
    plus = np.zeros(r)
    minus = np.zeros(r)
    t = np.zeros(r, dtype=np.int64)
    tsum = np.zeros(r)
    # Circular buffer of the last m residuals.  The minimum-dwell rule tau >= m
    # guarantees every slot has been overwritten with a current-cycle residual
    # before any alarm can fire, so no clearing at cycle boundaries is needed.
    buf = np.zeros((r, m))
    pos = np.zeros(r, dtype=np.int64)
    completed = np.zeros(r, dtype=np.int64)

    shape = (r, total_cycles)
    out_e_prev = np.zeros(shape)
    out_e_next = np.zeros(shape)
    out_tau = np.zeros(shape, dtype=np.int64)
    out_dir = np.zeros(shape, dtype=np.int8)
    out_mu_reuse = np.zeros(shape)
    out_mu_fresh = np.zeros(shape)
    out_window = np.zeros(shape)
    out_t_tau = np.zeros(shape)
    out_z_tau = np.zeros(shape)
    out_splus = np.zeros(shape)
    out_sminus = np.zeros(shape)

    ties = 0
    steps = 0
    for _ in range(config.max_steps):
        active = np.flatnonzero(completed < total_cycles)
        if active.size == 0:
            break
        steps += 1
        x = obs.draw(active)
        e_active = e[active]
        z = x - e_active
        new_plus, new_minus, up, down = cusum_update(
            plus[active], minus[active], z, k, h
        )
        plus[active] = new_plus
        minus[active] = new_minus
        t[active] += 1
        tsum[active] += z
        buf[active, pos[active]] = z
        pos[active] = (pos[active] + 1) % m

        crossed = up | down
        if m > 1:
            crossed = crossed & (t[active] >= m)
        if not crossed.any():
            continue

        ties += count_ties(up & crossed, down & crossed)
        done = active[crossed]
        direction = alarm_direction(up[crossed], down[crossed])
        window = buf[done].sum(axis=1)
        mu_reuse = e[done] + window / m
        mu_fresh = fresh.draw(done) * fresh_scale
        e_new = rebaseline(mu_reuse, mu_fresh, rho)

        col = completed[done]
        out_e_prev[done, col] = e[done]
        out_e_next[done, col] = e_new
        out_tau[done, col] = t[done]
        out_dir[done, col] = direction
        out_mu_reuse[done, col] = mu_reuse
        out_mu_fresh[done, col] = mu_fresh
        out_window[done, col] = window
        out_t_tau[done, col] = tsum[done]
        out_z_tau[done, col] = z[crossed]
        out_splus[done, col] = new_plus[crossed]
        out_sminus[done, col] = new_minus[crossed]

        e[done] = e_new
        plus[done] = 0.0
        minus[done] = 0.0
        t[done] = 0
        tsum[done] = 0.0
        pos[done] = 0
        completed[done] += 1
    else:
        unfinished = int(np.count_nonzero(completed < total_cycles))
        raise RuntimeError(
            f"{unfinished} replicates did not complete {total_cycles} cycles "
            f"within max_steps={config.max_steps}"
        )

    replicate = np.repeat(np.arange(r, dtype=np.int32), total_cycles)
    cycle_index = np.tile(np.arange(total_cycles, dtype=np.int32), r)
    in_burn_in = cycle_index < config.burn_in
    return CycleTable(
        replicate=replicate,
        cycle_index=cycle_index,
        in_burn_in=in_burn_in,
        e_prev=out_e_prev.ravel(),
        e_next=out_e_next.ravel(),
        tau=out_tau.ravel(),
        direction=out_dir.ravel(),
        mu_reuse=out_mu_reuse.ravel(),
        mu_fresh=out_mu_fresh.ravel(),
        window_sum=out_window.ravel(),
        t_tau=out_t_tau.ravel(),
        z_tau=out_z_tau.ravel(),
        s_plus_terminal=out_splus.ravel(),
        s_minus_terminal=out_sminus.ravel(),
        config=config,
        n_ties=ties,
        n_steps_simulated=steps,
    )


def stream_provenance(config: MultiCycleConfig) -> list[dict[str, Any]]:
    """The stream records that go into the run manifest."""
    obs = PerRowStream(config.master_seed, STREAM_OBS, config.n_replicates)
    fresh = PerRowStream(config.master_seed, STREAM_FRESH, config.n_replicates)
    return [
        {"role": "physical_observations_X", **obs.provenance()},
        {"role": "fresh_statistic_Y", **fresh.provenance()},
    ]
