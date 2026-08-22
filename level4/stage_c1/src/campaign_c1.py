"""Stage C.1 confirmatory campaign runner.

Uses the UNMODIFIED Stage C detection simulator.  Stage C.1 changes only the
replicate structure (many change events per replicate, so a per-replicate mean
exists) and the seeds.  Nothing about the detector, the change-insertion
convention or the reference update is touched.
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any, Callable, Sequence

import numpy as np

STAGE_C1 = Path(__file__).resolve().parents[1]
ROOT = STAGE_C1.parents[1]
sys.path.insert(0, str(ROOT / "level4" / "stage_c" / "src"))
sys.path.insert(0, str(ROOT / "level4" / "src"))

from detection import DetectionConfig, simulate_detection   # noqa: E402  (Stage C, unmodified)

RESULTS = STAGE_C1 / "results"
CELLS = RESULTS / "cells"

SEED_SMOKE = 20260931
SEED_CONFIRM = 20260901
SEED_ADVERSARIAL = 20260902

SHIFTS = (0.25, 0.5, 1.0, 1.5)
RHO_FRESH = 0.0
RHO_FULL = 1.0
RHO_EXPLORATORY = (0.25, 0.30)


def rho_rbg() -> float:
    """The Stage C policy value, taken verbatim -- never re-derived here."""
    sys.path.insert(0, str(ROOT / "level4" / "stage_c" / "src"))
    import policy
    return policy.rho_safe(0.2, variant=policy.CONSERVATIVE).rho


def config_hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True,
                                     separators=(",", ":"),
                                     default=str).encode()).hexdigest()


def run_cell(key: dict[str, Any], compute: Callable[[], dict[str, Any]],
             *, force: bool = False, verbose: bool = True) -> dict[str, Any]:
    path = CELLS / f"c1_{config_hash(key)[:16]}.json"
    if path.exists() and not force:
        cached = json.loads(path.read_text())
        if cached.get("config_hash") == config_hash(key):
            if verbose:
                print(f"    [cached] {key}", flush=True)
            return cached
    t0 = time.time()
    payload = compute()
    payload.update({"key": key, "config_hash": config_hash(key),
                    "seconds": time.time() - t0})
    CELLS.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=float))
    if verbose:
        print(f"    [ran]    {key}  ({payload['seconds']:.0f}s)", flush=True)
    return payload


def arm(*, rho: float, shift: float, n_replicates: int, n_events: int,
        burn_in: int, cycles_between: int, master_seed: int) -> dict[str, Any]:
    """One (policy, shift) arm; returns per-replicate mean detection delays."""
    cfg = DetectionConfig(
        n_replicates=n_replicates, burn_in=burn_in, n_cycles_after=1,
        rho=float(rho), shift=float(shift), master_seed=master_seed,
        n_changes=n_events, cycles_between=cycles_between)
    res = simulate_detection(cfg)
    delays = res.detection_delays().astype(float)          # (N, K)
    tau = res.by_replicate("tau").astype(float)
    e_prev = res.by_replicate("e_prev")
    return {
        "rho": float(rho), "shift": float(shift),
        "n_replicates": n_replicates, "n_events": n_events,
        "burn_in": burn_in, "cycles_between": cycles_between,
        "master_seed": master_seed,
        "per_replicate_mean_delay": delays.mean(axis=1).tolist(),
        "per_replicate_median_delay": np.median(delays, axis=1).tolist(),
        "grand_mean_delay": float(delays.mean()),
        "delay_sd_across_events": float(delays.std(ddof=1)),
        "n_two_arm_ties": res.n_ties,
        "burnin_mean_tau": float(tau[:, :burn_in].mean()),
        "mean_abs_e_at_change": float(np.abs(
            e_prev[:, burn_in::(1 + cycles_between)]).mean()),
        "recovery_abs_e_by_offset": np.abs(
            e_prev[:, burn_in:burn_in + min(cycles_between + 1, 12)]
        ).mean(axis=0).tolist(),
    }
