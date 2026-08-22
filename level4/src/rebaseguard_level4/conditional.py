"""GATE 4.2 -- conditional nonlinear map estimator.

Estimates ``F_rho(e) = E[E_{j+1} | E_j = e]`` **without** using the stationary
multi-cycle chain.  For each grid point ``e`` we independently:

1. initialise a *fresh* monitoring cycle under the frozen model (detector state
   reset to (0, 0), reference offset exactly ``e``, so residuals are
   ``Z_t = X_t - e`` with ``X_t ~ N(0,1)``);
2. simulate to the exact frozen alarm stopping rule (with minimum dwell if
   ``m >= 2``);
3. apply the re-baselining rule;
4. record ``E_{j+1}``;
5. repeat over many independent paths.

Nothing here reads the Gate 4.1 chain, so the two gates are genuinely
independent estimators of the same object.

Two additional estimators are provided as *independent cross-checks*, not as
substitutes:

``score_gamma``
    A likelihood-ratio (change-of-measure) estimator run entirely at ``e = 0``.
    Because ``dP_{-e}/dP_0 = exp(-e T_tau - (e^2/2) tau)`` on the stopped
    sigma-field, ``F_1(e) = e + (1/m) E_0[W_{tau,m} L_e]``, whose derivative at
    zero is ``1 - Gamma(m)`` with ``Gamma(m) = (1/m) E_0[W_{tau,m} T_tau]``.
    At ``m = 1`` this is exactly the Level 1-3 target ``Gamma = E_0[Z_tau
    T_tau]``, so it links Gate 4.2 to the Arb certificate.

``lr_map``
    The same change of measure evaluated on a grid, giving ``F_1`` on the whole
    grid from a single ``e = 0`` sample.  Its variance grows quickly with
    ``|e|`` and it is reported only near zero.

Statistical unit
----------------
Unlike Gate 4.1, paths here are genuinely i.i.d., so the **path** is the
statistical unit and the ordinary i.i.d. standard error is correct.  Batch
means are still recorded so that a bootstrap cross-check and independent-seed
replication are available.

Common random numbers
---------------------
``common_random_numbers=True`` gives every grid point the same seed key, so
neighbouring ``e`` share their driving noise.  For each *fixed* ``e`` the draws
are still i.i.d. ``N(0,1)``, so **the target expectation is unchanged and each
pointwise estimate stays unbiased**; only the joint law across the grid is
altered, which is precisely what makes finite differences of the estimated map
far less noisy.  Every CRN result is replicated with independent seeds.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Sequence

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
from .streams import STREAM_CONDITIONAL, STREAM_FRESH, ScalarStream


@dataclass(slots=True)
class CycleBatch:
    """Raw single-cycle outcomes for one batch at one ``e``."""

    e: float
    tau: np.ndarray
    z_tau: np.ndarray
    t_tau: np.ndarray
    window_sum: np.ndarray
    mu_reuse: np.ndarray
    mu_fresh: np.ndarray
    direction: np.ndarray
    s_plus_terminal: np.ndarray
    s_minus_terminal: np.ndarray
    n_ties: int


def simulate_cycle_batch(
    *,
    e: float,
    n_paths: int,
    m: int,
    stream: ScalarStream,
    fresh_stream: ScalarStream,
    k: float = K_FROZEN,
    h: float = H_FROZEN,
    max_steps: int = 2_000_000,
) -> CycleBatch:
    """Independent single cycles started from the exact reference error ``e``."""
    if n_paths <= 0:
        raise ValueError("n_paths must be positive")
    if m < 1:
        raise ValueError("m must be a positive integer")

    plus = np.zeros(n_paths)
    minus = np.zeros(n_paths)
    total = np.zeros(n_paths)
    buf = np.zeros((n_paths, m))
    pos = np.zeros(n_paths, dtype=np.int64)
    active = np.ones(n_paths, dtype=bool)

    tau = np.zeros(n_paths, dtype=np.int64)
    z_tau = np.zeros(n_paths)
    t_tau = np.zeros(n_paths)
    window = np.zeros(n_paths)
    direction = np.zeros(n_paths, dtype=np.int8)
    s_plus = np.zeros(n_paths)
    s_minus = np.zeros(n_paths)
    ties = 0

    for step in range(1, max_steps + 1):
        idx = np.flatnonzero(active)
        if idx.size == 0:
            break
        x = stream.draw(idx.size)
        z = x - e
        new_plus, new_minus, up, down = cusum_update(plus[idx], minus[idx], z, k, h)
        plus[idx] = new_plus
        minus[idx] = new_minus
        total[idx] += z
        buf[idx, pos[idx]] = z
        pos[idx] = (pos[idx] + 1) % m

        crossed = up | down
        if m > 1 and step < m:
            continue                      # minimum dwell: tau_m = inf{t >= m : ...}
        if not crossed.any():
            continue
        ties += count_ties(up & crossed, down & crossed)
        done = idx[crossed]
        tau[done] = step
        z_tau[done] = z[crossed]
        t_tau[done] = total[done]
        window[done] = buf[done].sum(axis=1)
        direction[done] = alarm_direction(up[crossed], down[crossed])
        s_plus[done] = new_plus[crossed]
        s_minus[done] = new_minus[crossed]
        active[done] = False
    else:
        raise RuntimeError(
            f"{int(active.sum())} paths did not alarm within max_steps={max_steps}"
        )

    mu_reuse = e + window / m
    mu_fresh = fresh_stream.draw(n_paths) * fresh_statistic_scale(m)
    return CycleBatch(
        e=float(e), tau=tau, z_tau=z_tau, t_tau=t_tau, window_sum=window,
        mu_reuse=mu_reuse, mu_fresh=mu_fresh, direction=direction,
        s_plus_terminal=s_plus, s_minus_terminal=s_minus, n_ties=ties,
    )


@dataclass(frozen=True, slots=True)
class ConditionalConfig:
    e_values: tuple[float, ...]
    n_paths_per_e: int
    m: int
    master_seed: int
    n_batches: int = 10
    rho_values: tuple[float, ...] = (1.0,)
    common_random_numbers: bool = True
    seed_replicate: int = 0        # bump for an independent-seed replication
    k: float = K_FROZEN
    h: float = H_FROZEN
    max_steps: int = 2_000_000
    detector: str = "frozen_two_sided_cusum"

    def validate(self) -> None:
        if self.detector != "frozen_two_sided_cusum":
            raise ValueError("Gate 4.2 targets the frozen two-sided CUSUM only")
        if self.k != K_FROZEN or self.h != H_FROZEN:
            raise ValueError("k and h are frozen at 1/2 and 5")
        if self.n_paths_per_e % self.n_batches:
            raise ValueError("n_paths_per_e must be divisible by n_batches")
        if any(not 0.0 <= r <= 1.0 for r in self.rho_values):
            raise ValueError("every rho must lie in [0, 1]")

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _batch_key(config: ConditionalConfig, e_index: int, batch: int) -> tuple[int, ...]:
    """Seed key for one batch.  Under CRN the grid index is dropped."""
    grid_part = 0 if config.common_random_numbers else e_index + 1
    return (STREAM_CONDITIONAL, config.seed_replicate, grid_part, batch)


def estimate_conditional_map(config: ConditionalConfig) -> dict[str, Any]:
    """Estimate ``F_1`` and every requested ``F_rho`` on the grid."""
    config.validate()
    per_batch = config.n_paths_per_e // config.n_batches
    records: list[dict[str, Any]] = []
    ties_total = 0

    for e_index, e in enumerate(config.e_values):
        batch_mu_reuse: list[float] = []
        batch_tau: list[float] = []
        batch_dir: list[float] = []
        batch_frho: dict[float, list[float]] = {r: [] for r in config.rho_values}
        all_mu = np.empty(config.n_paths_per_e)
        all_tau = np.empty(config.n_paths_per_e)
        all_enext: dict[float, np.ndarray] = {
            r: np.empty(config.n_paths_per_e) for r in config.rho_values
        }
        for b in range(config.n_batches):
            key = _batch_key(config, e_index, b)
            obs = ScalarStream(config.master_seed, *key)
            fresh = ScalarStream(config.master_seed, STREAM_FRESH, *key)
            batch = simulate_cycle_batch(
                e=e, n_paths=per_batch, m=config.m, stream=obs,
                fresh_stream=fresh, k=config.k, h=config.h,
                max_steps=config.max_steps,
            )
            ties_total += batch.n_ties
            lo, hi = b * per_batch, (b + 1) * per_batch
            all_mu[lo:hi] = batch.mu_reuse
            all_tau[lo:hi] = batch.tau
            batch_mu_reuse.append(float(batch.mu_reuse.mean()))
            batch_tau.append(float(batch.tau.mean()))
            batch_dir.append(float((batch.direction > 0).mean()))
            for r in config.rho_values:
                e_next = rebaseline(batch.mu_reuse, batch.mu_fresh, r)
                all_enext[r][lo:hi] = e_next
                batch_frho[r].append(float(e_next.mean()))

        record: dict[str, Any] = {
            "e": float(e),
            "e_index": e_index,
            "n_paths": config.n_paths_per_e,
            "n_batches": config.n_batches,
            "F1": float(all_mu.mean()),
            "F1_se": float(all_mu.std(ddof=1) / np.sqrt(all_mu.size)),
            "F1_batch_means": batch_mu_reuse,
            "F1_batch_sd": (float(np.std(batch_mu_reuse, ddof=1))
                            if len(batch_mu_reuse) > 1 else float("nan")),
            "mean_tau": float(all_tau.mean()),
            "mean_tau_se": float(all_tau.std(ddof=1) / np.sqrt(all_tau.size)),
            "median_tau": float(np.median(all_tau)),
            "alarm_up_proportion": float(np.mean(batch_dir)),
            "seed_keys": [list(_batch_key(config, e_index, b))
                          for b in range(config.n_batches)],
        }
        for r in config.rho_values:
            arr = all_enext[r]
            record[f"F_rho_{r:g}"] = float(arr.mean())
            record[f"F_rho_{r:g}_se"] = float(arr.std(ddof=1) / np.sqrt(arr.size))
            record[f"F_rho_{r:g}_batch_means"] = batch_frho[r]
        records.append(record)

    return {
        "config": config.as_dict(),
        "statistical_unit": "path (i.i.d. within a grid point)",
        "n_two_arm_ties": ties_total,
        "records": records,
    }


# --------------------------------------------------- likelihood-ratio route --

def score_gamma(
    *,
    n_paths: int,
    m: int,
    master_seed: int,
    n_batches: int = 10,
    seed_replicate: int = 0,
    k: float = K_FROZEN,
    h: float = H_FROZEN,
    max_steps: int = 2_000_000,
) -> dict[str, Any]:
    """Estimate ``Gamma(m) = (1/m) E_0[W_{tau,m} T_tau]`` and ``F_1'(0) = 1 - Gamma``.

    Run entirely at ``e = 0``.  At ``m = 1`` this is literally the frozen
    Level 1-3 functional ``Gamma = E_0[Z_tau T_tau]``, which the Arb
    certificate encloses in ``[3.9243482, 27.8493821]``.
    """
    per_batch = n_paths // n_batches
    gammas = np.empty(n_paths)
    taus = np.empty(n_paths)
    t_sq = np.empty(n_paths)
    batch_means: list[float] = []
    keys: list[list[int]] = []
    for b in range(n_batches):
        key = (STREAM_CONDITIONAL, seed_replicate, 0, b)
        obs = ScalarStream(master_seed, *key)
        fresh = ScalarStream(master_seed, STREAM_FRESH, *key)
        batch = simulate_cycle_batch(
            e=0.0, n_paths=per_batch, m=m, stream=obs, fresh_stream=fresh,
            k=k, h=h, max_steps=max_steps,
        )
        lo, hi = b * per_batch, (b + 1) * per_batch
        gammas[lo:hi] = batch.window_sum * batch.t_tau / m
        taus[lo:hi] = batch.tau
        t_sq[lo:hi] = batch.t_tau ** 2
        batch_means.append(float(gammas[lo:hi].mean()))
        keys.append(list(key))
    gamma = float(gammas.mean())
    gamma_se = float(gammas.std(ddof=1) / np.sqrt(gammas.size))
    return {
        "m": m,
        "n_paths": n_paths,
        "n_batches": n_batches,
        "gamma": gamma,
        "gamma_se": gamma_se,
        "gamma_ci95": [gamma - 1.959963985 * gamma_se,
                       gamma + 1.959963985 * gamma_se],
        "gamma_batch_means": batch_means,
        "F1_prime_0": 1.0 - gamma,
        "F1_prime_0_se": gamma_se,
        "F1_prime_0_ci95": [1.0 - gamma - 1.959963985 * gamma_se,
                            1.0 - gamma + 1.959963985 * gamma_se],
        "arl_0": float(taus.mean()),
        "mean_t_tau_sq": float(t_sq.mean()),
        "wald_second_gap": float(t_sq.mean() - taus.mean()),
        "seed_keys": keys,
        "master_seed": master_seed,
        "seed_replicate": seed_replicate,
    }


def lr_map(
    e_values: Sequence[float],
    *,
    n_paths: int,
    m: int,
    master_seed: int,
    n_batches: int = 10,
    seed_replicate: int = 0,
    k: float = K_FROZEN,
    h: float = H_FROZEN,
    max_steps: int = 2_000_000,
) -> dict[str, Any]:
    """``F_1`` on a grid from one ``e = 0`` sample, by change of measure.

    ``F_1(e) = e + (1/m) E_0[ W_{tau,m} exp(-e T_tau - (e^2/2) tau) ]``.

    The importance weight has heavy tails, so an effective-sample-size
    diagnostic is returned with every grid point and the estimator is only
    trusted where the ESS stays a large fraction of ``n_paths``.
    """
    per_batch = n_paths // n_batches
    w_all = np.empty(n_paths)
    t_all = np.empty(n_paths)
    tau_all = np.empty(n_paths)
    for b in range(n_batches):
        key = (STREAM_CONDITIONAL, seed_replicate, 0, b)
        batch = simulate_cycle_batch(
            e=0.0, n_paths=per_batch, m=m,
            stream=ScalarStream(master_seed, *key),
            fresh_stream=ScalarStream(master_seed, STREAM_FRESH, *key),
            k=k, h=h, max_steps=max_steps,
        )
        lo, hi = b * per_batch, (b + 1) * per_batch
        w_all[lo:hi] = batch.window_sum
        t_all[lo:hi] = batch.t_tau
        tau_all[lo:hi] = batch.tau

    out = []
    for e in e_values:
        log_lr = -e * t_all - 0.5 * e * e * tau_all
        lr = np.exp(np.clip(log_lr, -700.0, 700.0))
        values = (w_all / m) * lr
        ess = float(lr.sum() ** 2 / np.dot(lr, lr))
        out.append({
            "e": float(e),
            "F1_lr": float(e + values.mean()),
            "F1_lr_se": float(values.std(ddof=1) / np.sqrt(values.size)),
            "effective_sample_size": ess,
            "ess_fraction": ess / n_paths,
        })
    return {
        "m": m, "n_paths": n_paths, "master_seed": master_seed,
        "seed_replicate": seed_replicate, "records": out,
        "note": "importance-sampling estimator; trust only where ess_fraction "
                "is close to 1",
    }
