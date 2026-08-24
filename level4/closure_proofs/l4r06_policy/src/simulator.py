"""Frozen-semantics shifted multi-cycle simulator for the L4R-06 campaign.

The existing Stage C detector is intentionally scoped to m=1. This isolated
implementation extends the already-frozen multi-cycle oracle to cycle-boundary
mean shifts while importing its detector, stream, scaling, direction, and
re-baselining primitives unchanged. Delta=0 equivalence is a hard gate.
"""
from __future__ import annotations

import sys
from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

from config import ROOT

sys.path.insert(0, str(ROOT / "level4/src"))

from rebaseguard_level4.frozen import (  # noqa: E402
    H_FROZEN,
    K_FROZEN,
    alarm_direction,
    count_ties,
    cusum_update,
    fresh_statistic_scale,
    rebaseline,
)
from rebaseguard_level4.streams import (  # noqa: E402
    STREAM_FRESH,
    STREAM_OBS,
    PerRowStream,
)


@dataclass(frozen=True, slots=True)
class ArmConfig:
    n_replicates: int
    n_events: int
    burn_in: int
    cycles_between: int
    rho: float
    m: int
    shift: float
    master_seed: int
    k: float = K_FROZEN
    h: float = H_FROZEN
    max_steps: int = 100_000_000

    @property
    def stride(self) -> int:
        return 1 + self.cycles_between

    @property
    def total_cycles(self) -> int:
        return self.burn_in + self.n_events * self.stride

    def validate(self) -> None:
        if self.k != K_FROZEN or self.h != H_FROZEN:
            raise ValueError("detector k/h differ from frozen values")
        if self.n_replicates < 1 or self.n_events < 1:
            raise ValueError("need positive replicates and events")
        if self.burn_in < 0 or self.cycles_between < 0:
            raise ValueError("burn-in/spacing cannot be negative")
        if self.m < 1 or not 0.0 <= self.rho <= 1.0 or self.shift < 0.0:
            raise ValueError("invalid m, rho, or shift")

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _acf(cross: np.ndarray, left: np.ndarray, right: np.ndarray,
         left2: np.ndarray, right2: np.ndarray, count: np.ndarray) -> np.ndarray:
    safe = np.maximum(count, 1)
    mean_left = left / safe
    mean_right = right / safe
    cov = cross / safe - mean_left * mean_right
    var_left = left2 / safe - mean_left ** 2
    var_right = right2 / safe - mean_right ** 2
    denom = np.sqrt(np.maximum(var_left * var_right, 0.0))
    return np.divide(cov, denom, out=np.zeros_like(cov), where=denom > 0.0)


def simulate_arm(config: ArmConfig, *, retain_trace: bool = False) -> dict[str, Any]:
    config.validate()
    r, m = config.n_replicates, config.m
    obs = PerRowStream(config.master_seed, STREAM_OBS, r)
    fresh = PerRowStream(config.master_seed, STREAM_FRESH, r)
    fresh_scale = fresh_statistic_scale(m)

    e = np.zeros(r)
    plus = np.zeros(r)
    minus = np.zeros(r)
    tau = np.zeros(r, dtype=np.int64)
    buf = np.zeros((r, m))
    pos = np.zeros(r, dtype=np.int64)
    completed = np.zeros(r, dtype=np.int64)

    delay_sum = np.zeros(r)
    delay_count = np.zeros(r, dtype=np.int64)
    retained_count = np.zeros(r, dtype=np.int64)
    sum_e = np.zeros(r)
    sum_e2 = np.zeros(r)
    sum_tau = np.zeros(r)
    sum_direction = np.zeros(r)
    sum_direction2 = np.zeros(r)

    have_previous = np.zeros(r, dtype=bool)
    previous_e = np.zeros(r)
    previous_direction = np.zeros(r)
    lag_count = np.zeros(r, dtype=np.int64)
    e_cross = np.zeros(r); e_left = np.zeros(r); e_right = np.zeros(r)
    e_left2 = np.zeros(r); e_right2 = np.zeros(r)
    d_cross = np.zeros(r); d_left = np.zeros(r); d_right = np.zeros(r)
    d_left2 = np.zeros(r); d_right2 = np.zeros(r)

    trace = None
    if retain_trace:
        shape = (r, config.total_cycles)
        trace = {
            "e_prev": np.zeros(shape),
            "e_next": np.zeros(shape),
            "tau": np.zeros(shape, dtype=np.int64),
            "direction": np.zeros(shape, dtype=np.int8),
        }

    ties = 0

    def apply_due_shift(rows: np.ndarray) -> None:
        if config.shift == 0.0 or rows.size == 0:
            return
        indices = completed[rows]
        due = (indices >= config.burn_in) & (
            (indices - config.burn_in) % config.stride == 0
        )
        if np.any(due):
            e[rows[due]] -= config.shift

    # Match Stage C's boundary convention even for protocol-independent tests
    # with burn_in=0: the first change occurs before the first observation.
    apply_due_shift(np.arange(r, dtype=np.int64))

    for _ in range(config.max_steps):
        active = np.flatnonzero(completed < config.total_cycles)
        if active.size == 0:
            break
        x = obs.draw(active)
        z = x - e[active]
        new_plus, new_minus, up, down = cusum_update(
            plus[active], minus[active], z, config.k, config.h
        )
        plus[active] = new_plus
        minus[active] = new_minus
        tau[active] += 1
        buf[active, pos[active]] = z
        pos[active] = (pos[active] + 1) % m

        crossed = up | down
        if m > 1:
            crossed &= tau[active] >= m
        if not np.any(crossed):
            continue

        ties += count_ties(up & crossed, down & crossed)
        done = active[crossed]
        col = completed[done]
        old_e = e[done].copy()
        direction = alarm_direction(up[crossed], down[crossed]).astype(float)
        window = buf[done].sum(axis=1)
        mu_reuse = old_e + window / m
        mu_fresh = fresh.draw(done) * fresh_scale
        new_e = rebaseline(mu_reuse, mu_fresh, config.rho)

        event = (col >= config.burn_in) & (
            (col - config.burn_in) % config.stride == 0
        )
        if np.any(event):
            event_rows = done[event]
            delay_sum[event_rows] += tau[event_rows]
            delay_count[event_rows] += 1

        retained = col >= config.burn_in
        if np.any(retained):
            rows = done[retained]
            values_e = old_e[retained]
            values_d = direction[retained]
            retained_count[rows] += 1
            sum_e[rows] += values_e
            sum_e2[rows] += values_e ** 2
            sum_tau[rows] += tau[rows]
            sum_direction[rows] += values_d
            sum_direction2[rows] += values_d ** 2

            paired = have_previous[rows]
            if np.any(paired):
                pr = rows[paired]
                cur_e = values_e[paired]; prev_e = previous_e[pr]
                cur_d = values_d[paired]; prev_d = previous_direction[pr]
                lag_count[pr] += 1
                e_cross[pr] += prev_e * cur_e
                e_left[pr] += prev_e; e_right[pr] += cur_e
                e_left2[pr] += prev_e ** 2; e_right2[pr] += cur_e ** 2
                d_cross[pr] += prev_d * cur_d
                d_left[pr] += prev_d; d_right[pr] += cur_d
                d_left2[pr] += prev_d ** 2; d_right2[pr] += cur_d ** 2
            previous_e[rows] = values_e
            previous_direction[rows] = values_d
            have_previous[rows] = True

        if trace is not None:
            trace["e_prev"][done, col] = old_e
            trace["e_next"][done, col] = new_e
            trace["tau"][done, col] = tau[done]
            trace["direction"][done, col] = direction.astype(np.int8)

        e[done] = new_e
        plus[done] = 0.0
        minus[done] = 0.0
        tau[done] = 0
        pos[done] = 0
        completed[done] += 1
        apply_due_shift(done)
    else:
        raise RuntimeError("L4R-06 arm exceeded max_steps")

    if not np.all(delay_count == config.n_events):
        raise RuntimeError("not every replicate produced every frozen event")
    if not np.all(retained_count == config.n_events * config.stride):
        raise RuntimeError("retained cycle count mismatch")

    mean_e = sum_e / retained_count
    variance_e = np.maximum(sum_e2 / retained_count - mean_e ** 2, 0.0)
    per_rep = {
        "mean_delay": delay_sum / delay_count,
        "reference_mse": sum_e2 / retained_count,
        "reference_mean": mean_e,
        "reference_sd": np.sqrt(variance_e),
        "cycle_arl": sum_tau / retained_count,
        "reference_acf1": _acf(
            e_cross, e_left, e_right, e_left2, e_right2, lag_count
        ),
        "direction_acf1": _acf(
            d_cross, d_left, d_right, d_left2, d_right2, lag_count
        ),
    }
    result: dict[str, Any] = {
        "schema": "rebaseguard.l4r06-arm.v1",
        "config": config.as_dict(),
        "statistical_unit": "replicate cluster",
        "per_replicate": {name: values.tolist() for name, values in per_rep.items()},
        "grand_mean_delay": float(per_rep["mean_delay"].mean()),
        "n_two_arm_ties": int(ties),
        "completed_events": int(delay_count.sum()),
        "finite": all(bool(np.all(np.isfinite(values))) for values in per_rep.values()),
    }
    if trace is not None:
        result["_trace"] = trace
    return result
