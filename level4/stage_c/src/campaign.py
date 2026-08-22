"""Stage C campaign runner: resumable, checkpointed, per-cell.

Every cell writes a JSON checkpoint keyed by a hash of its configuration.  A
rerun skips cells whose checkpoint already exists and whose config hash matches,
so an interrupted campaign resumes without recomputation and a changed config
never silently reuses stale output.
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Callable, Sequence

import numpy as np

from rebaseguard_level4 import metrics, provenance
from rebaseguard_level4.multicycle import (
    MultiCycleConfig,
    simulate_multicycle,
    stream_provenance,
)

STAGE_C = Path(__file__).resolve().parents[1]
RESULTS = STAGE_C / "results"
CELLS = RESULTS / "cells"

# The mandated dense grid.  Never edited: additions go in EXTRA_RHO.
PROTOCOL_RHO = (0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.065, 0.067, 0.07,
                0.075, 0.08, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.75, 1.00)
# Added points, recorded as additions (the two ReBaseGuard policy values).
EXTRA_RHO = (0.029796, 0.053743)


def full_rho_grid() -> tuple[float, ...]:
    return tuple(sorted(set(PROTOCOL_RHO) | set(EXTRA_RHO)))


def config_hash(payload: dict[str, Any]) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                      default=str)
    return hashlib.sha256(blob.encode()).hexdigest()


def cell_path(kind: str, key: dict[str, Any]) -> Path:
    return CELLS / f"{kind}_{config_hash(key)[:16]}.json"


def run_cell(kind: str, key: dict[str, Any],
             compute: Callable[[], dict[str, Any]],
             *, force: bool = False, verbose: bool = True) -> dict[str, Any]:
    """Compute a cell, or load its checkpoint if one already matches."""
    path = cell_path(kind, key)
    if path.exists() and not force:
        cached = json.loads(path.read_text())
        if cached.get("config_hash") == config_hash(key):
            if verbose:
                print(f"    [cached] {kind} {key}", flush=True)
            return cached
    started = time.time()
    payload = compute()
    payload.update({
        "kind": kind, "key": key, "config_hash": config_hash(key),
        "seconds": time.time() - started,
        "utc_timestamp": provenance.build_manifest(
            gate="stage-c", stage=kind, config=key)["utc_timestamp"],
    })
    CELLS.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=float))
    if verbose:
        print(f"    [ran]    {kind} {key}  ({payload['seconds']:.0f}s)",
              flush=True)
    return payload


# --------------------------------------------------------- in-control cells --

def in_control_cell(*, rho: float, n_replicates: int, n_cycles: int,
                    burn_in: int, master_seed: int,
                    n_bootstrap: int, acurve=None, a_batches=None,
                    lags: Sequence[int] = (1, 2, 3),
                    quantiles: Sequence[float] = (0.01, 0.05, 0.25, 0.5,
                                                  0.75, 0.95, 0.99),
                    ) -> dict[str, Any]:
    """One rho of the in-control sweep, using the FROZEN Stage A simulator."""
    cfg = MultiCycleConfig(n_replicates=n_replicates, n_cycles=n_cycles,
                           burn_in=burn_in, rho=float(rho), m=1,
                           master_seed=master_seed)
    table = simulate_multicycle(cfg)
    retained = table.post_burn_in()
    e_prev = retained.by_replicate("e_prev")
    e_next = retained.by_replicate("e_next")
    tau = retained.by_replicate("tau").astype(float)
    direction = retained.by_replicate("direction").astype(float)

    per_rep = {
        # PRIMARY A: stationary reference MSE, on the reference actually used
        # to monitor the cycle (e_prev), which is what pairs with A(e).
        "reference_mse": (e_prev ** 2).mean(axis=1),
        "reference_mse_enext": (e_next ** 2).mean(axis=1),
        # PRIMARY B
        "cycle_arl": tau.mean(axis=1),
        "median_tau": np.median(tau, axis=1),
        # secondary diagnostics
        "reference_mean": e_prev.mean(axis=1),
        "reference_sd": e_prev.std(axis=1, ddof=1),
        "alternation_rate": (direction[:, 1:] != direction[:, :-1]).mean(axis=1),
        "central_mass_0p5": (np.abs(e_prev) <= 0.5).mean(axis=1),
        "offcenter_mass_1p0": (np.abs(e_prev) > 1.0).mean(axis=1),
        "offcenter_mass_1p5": (np.abs(e_prev) > 1.5).mean(axis=1),
        "tau_sd": tau.std(axis=1, ddof=1),
    }
    for lag in lags:
        per_rep[f"acf_e_lag{lag}"] = np.array(
            [metrics.autocorrelation(row, [lag])[0] for row in e_prev])
        per_rep[f"acf_direction_lag{lag}"] = np.array(
            [metrics.autocorrelation(row, [lag])[0] for row in direction])
    for q in quantiles:
        per_rep[f"e_quantile_{q:g}"] = np.quantile(e_prev, q, axis=1)

    # ---- ARL decomposition: ARL = E_pi[A(e)], computed per replicate so the
    # comparison against the direct mean(tau) is naturally PAIRED (both come
    # from the same cycles), which is far tighter than independent SEs.
    decomposition: dict[str, Any] = {}
    if acurve is not None:
        a_of_e = acurve(e_prev)
        per_rep["arl_decomposition"] = a_of_e.mean(axis=1)
        per_rep["arl_paired_gap"] = tau.mean(axis=1) - a_of_e.mean(axis=1)
        decomposition = {
            "out_of_grid_fraction": acurve.out_of_range_fraction(e_prev),
            "arl_direct_pooled": float(tau.mean()),
            "arl_decomp_pooled": float(a_of_e.mean()),
        }
        # A's own Monte Carlo error is systematic across replicates, so the
        # replicate bootstrap cannot see it.  Re-evaluate the decomposition once
        # per A-batch and take the spread.
        if a_batches is not None:
            per_batch = []
            for curve_b in a_batches:
                per_batch.append(float(curve_b(e_prev).mean()))
            arr = np.asarray(per_batch)
            decomposition["arl_decomp_batch_means"] = arr.tolist()
            decomposition["arl_decomp_se_from_A"] = float(
                arr.std(ddof=1) / np.sqrt(arr.size))

    estimates = {}
    for i, (name, values) in enumerate(sorted(per_rep.items())):
        estimates[name] = metrics.bootstrap_estimate(
            values, metric=name, master_seed=master_seed, metric_index=i,
            n_bootstrap=n_bootstrap).as_dict()

    # keep the per-replicate vectors: paired comparisons across rho need them
    return {
        "config": cfg.as_dict(),
        "streams": stream_provenance(cfg),
        "statistical_unit": "replicate",
        "n_two_arm_ties": table.n_ties,
        "estimates": estimates,
        "per_replicate": {k: v.tolist() for k, v in per_rep.items()},
        "decomposition": decomposition,
        "e_hist": _histogram(retained.e_prev),
        "e_prev_sample": _thin(retained.e_prev, 20_000, master_seed),
        "tau_hist": _tau_histogram(retained.tau),
        "pooled": {
            "n": int(retained.e_prev.size),
            "mean_e_prev": float(retained.e_prev.mean()),
            "mse_e_prev": float((retained.e_prev ** 2).mean()),
            "arl": float(retained.tau.mean()),
        },
    }


def _thin(values: np.ndarray, cap: int, seed: int) -> list[float]:
    """A reproducible thinned sample of the stationary reference errors.

    Kept so the ARL decomposition and the stationary-density figures can be
    rebuilt from the checkpoint without rerunning the campaign.
    """
    if values.size <= cap:
        return values.tolist()
    rng = np.random.default_rng([seed, 0xC0FFEE])
    idx = rng.choice(values.size, size=cap, replace=False)
    return values[np.sort(idx)].tolist()


HIST_EDGES = np.linspace(-6.0, 6.0, 481)


def _histogram(values: np.ndarray) -> dict[str, Any]:
    """Fixed-bin histogram of the stationary reference error.

    Stored instead of the raw 10^6 samples: it is what the density figures and
    the mass diagnostics need, and it keeps a checkpoint at kilobytes rather
    than megabytes.
    """
    counts, _ = np.histogram(values, bins=HIST_EDGES)
    return {"edges": HIST_EDGES.tolist(), "counts": counts.tolist(),
            "n": int(values.size),
            "n_below": int(np.sum(values < HIST_EDGES[0])),
            "n_above": int(np.sum(values > HIST_EDGES[-1]))}


def _tau_histogram(tau: np.ndarray) -> dict[str, Any]:
    edges = np.concatenate([np.arange(0, 201, 5), [300, 500, 1000, 2000, 100000]])
    counts, _ = np.histogram(tau, bins=edges)
    return {"edges": edges.tolist(), "counts": counts.tolist(),
            "n": int(tau.size)}
