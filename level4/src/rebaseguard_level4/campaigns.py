"""Staged experiment campaigns for Gates 4.1 and 4.2.

A *campaign* is one grid of configurations run at one stage.  Stages exist so
that nothing expensive runs before something cheap has proved the pipeline
works:

    smoke  -- seconds; asserts the pipeline runs end to end and the invariants
              hold.  Too small for any scientific claim.
    pilot  -- minutes; enough to size the full run and to catch a metric that
              behaves differently at scale.
    full   -- the publication-oriented run.

Every cell writes: a Parquet table of cycle-level raw data, a JSON manifest
with complete provenance, and a JSON summary.  The campaign writes a combined
CSV of headline estimates.  Nothing is aggregated without its seeds being
recoverable from the manifest.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Sequence

import numpy as np

from . import metrics, provenance, storage
from .conditional import ConditionalConfig, estimate_conditional_map, score_gamma
from .multicycle import MultiCycleConfig, simulate_multicycle, stream_provenance

RESULTS = provenance.REPO_ROOT / "level4" / "results"
RAW = RESULTS / "raw"
PROCESSED = RESULTS / "processed"


def _repo_relative(path: Path) -> str:
    """Repo-relative path when possible, absolute otherwise.

    Campaign output normally lands inside the repository, but tests (and ad hoc
    runs) may direct it elsewhere; provenance must record a usable path either
    way rather than raising.
    """
    try:
        return str(path.relative_to(provenance.REPO_ROOT))
    except ValueError:
        return str(path)

# ------------------------------------------------------------ cost sizing --

def estimate_gate41_cost(
    *,
    n_replicates: int,
    n_cycles: int,
    burn_in: int,
    arl_estimate: float,
    seconds_per_step: float,
    bytes_per_cycle_row: int = 120,
) -> dict[str, Any]:
    """Runtime/storage estimate for one Gate 4.1 cell.

    ``seconds_per_step`` is the measured cost of one vectorised lockstep
    iteration at this replicate count; it must come from a pilot, never from a
    guess.
    """
    total_cycles = n_cycles + burn_in
    steps = total_cycles * arl_estimate
    rows = n_replicates * total_cycles
    return {
        "estimated_lockstep_iterations": float(steps),
        "estimated_runtime_seconds": float(steps * seconds_per_step),
        "estimated_raw_rows": int(rows),
        "estimated_raw_bytes_uncompressed": int(rows * bytes_per_cycle_row),
    }


# --------------------------------------------------------------- Gate 4.1 --

def run_gate41_campaign(
    *,
    stage: str,
    rho_values: Sequence[float],
    m_values: Sequence[int],
    n_replicates: int,
    n_cycles: int,
    burn_in: int,
    master_seed: int,
    n_bootstrap: int = 10_000,
    e0: float = 0.0,
    write_raw: bool = True,
    results_root: Path | None = None,
    progress: bool = True,
) -> dict[str, Any]:
    campaign_config = {
        "gate": "4.1",
        "stage": stage,
        "rho_values": list(rho_values),
        "m_values": list(m_values),
        "n_replicates": n_replicates,
        "n_cycles": n_cycles,
        "burn_in": burn_in,
        "master_seed": master_seed,
        "n_bootstrap": n_bootstrap,
        "e0": e0,
        "detector": "frozen_two_sided_cusum",
        "k": 0.5,
        "h": 5.0,
    }
    root = results_root or RESULTS
    campaign_id = provenance.experiment_id("gate4.1", stage, campaign_config)
    raw_dir = root / "raw" / campaign_id
    out_dir = root / "processed" / campaign_id

    cells: list[dict[str, Any]] = []
    headline: list[dict[str, Any]] = []
    for m in m_values:
        for rho in rho_values:
            cfg = MultiCycleConfig(
                n_replicates=n_replicates, n_cycles=n_cycles, burn_in=burn_in,
                rho=float(rho), m=int(m), master_seed=master_seed, e0=e0,
            )
            cell_id = provenance.experiment_id("gate4.1", stage, cfg.as_dict())
            started = time.time()
            table = simulate_multicycle(cfg)
            sim_seconds = time.time() - started
            summary = metrics.summarise(table, n_bootstrap=n_bootstrap)
            summary["burn_in_diagnostic"] = metrics.burn_in_diagnostic(table)

            raw_path = None
            if write_raw:
                raw_path = raw_dir / f"cycles_m{m}_rho{rho:g}.parquet"
                storage.write_parquet(
                    table.columns(), raw_path,
                    metadata={"experiment_id": cell_id, "gate": "4.1",
                              "stage": stage,
                              "proof_role": "NON-RIGOROUS DIAGNOSTIC"},
                )
            cell_manifest = provenance.build_manifest(
                gate="4.1", stage=stage, config=cfg.as_dict(),
                streams=stream_provenance(cfg),
                extra={
                    "campaign_id": campaign_id,
                    "simulation_seconds": sim_seconds,
                    "seconds_per_lockstep_iteration":
                        sim_seconds / max(table.n_steps_simulated, 1),
                    "n_lockstep_iterations": table.n_steps_simulated,
                    "raw_path": None if raw_path is None
                                else _repo_relative(raw_path),
                    "n_two_arm_ties": table.n_ties,
                },
            )
            provenance.write_manifest(cell_manifest, out_dir / f"{cell_id}.manifest.json")
            storage.write_json(summary, out_dir / f"{cell_id}.summary.json")
            cells.append({
                "cell_id": cell_id, "m": int(m), "rho": float(rho),
                "policy": cfg.policy_label,
                "simulation_seconds": sim_seconds,
                "n_lockstep_iterations": table.n_steps_simulated,
                "raw_path": None if raw_path is None else str(raw_path),
            })
            row: dict[str, Any] = {
                "cell_id": cell_id, "m": int(m), "rho": float(rho),
                "policy": cfg.policy_label,
                "n_replicates": n_replicates, "n_cycles": n_cycles,
                "burn_in": burn_in, "master_seed": master_seed,
            }
            for name in ("mean_reference_error", "sd_reference_error",
                         "rmse_reference_error", "cycle_arl", "median_tau",
                         "alternation_rate", "alarm_up_proportion",
                         "acf_e_lag1", "acf_e_lag2", "acf_e_lag3",
                         "acf_direction_lag1", "fraction_abs_e_gt_1"):
                est = summary["estimates"][name]
                row[name] = est["point"]
                row[f"{name}_ci_low"] = est["ci_low"]
                row[f"{name}_ci_high"] = est["ci_high"]
                row[f"{name}_replicate_sd"] = est["replicate_sd"]
            headline.append(row)
            if progress:
                print(f"  [4.1/{stage}] m={m:<3} rho={rho:<5g} "
                      f"ARL={row['cycle_arl']:8.2f} "
                      f"alt={row['alternation_rate']:.4f} "
                      f"sd(e)={row['sd_reference_error']:.4f} "
                      f"acf1={row['acf_e_lag1']:+.4f}  ({sim_seconds:.1f}s)",
                      flush=True)

    campaign_manifest = provenance.build_manifest(
        gate="4.1", stage=stage, config=campaign_config,
        extra={"campaign_id": campaign_id, "cells": cells},
    )
    provenance.write_manifest(campaign_manifest, out_dir / "campaign.manifest.json")
    storage.write_csv(headline, out_dir / "headline.csv")
    storage.write_json({"campaign_id": campaign_id,
                        "config": campaign_config,
                        "cells": cells,
                        "headline": headline},
                       out_dir / "campaign.summary.json")
    return {"campaign_id": campaign_id, "out_dir": out_dir, "raw_dir": raw_dir,
            "cells": cells, "headline": headline,
            "manifest": campaign_manifest}


# --------------------------------------------------------------- Gate 4.2 --

def run_gate42_map(
    *,
    stage: str,
    label: str,
    e_values: Sequence[float],
    n_paths_per_e: int,
    m: int,
    master_seed: int,
    rho_values: Sequence[float] = (1.0,),
    n_batches: int = 20,
    common_random_numbers: bool = True,
    seed_replicate: int = 0,
    results_root: Path | None = None,
    progress: bool = True,
) -> dict[str, Any]:
    cfg = ConditionalConfig(
        e_values=tuple(float(v) for v in e_values),
        n_paths_per_e=n_paths_per_e, m=m, master_seed=master_seed,
        n_batches=n_batches, rho_values=tuple(float(r) for r in rho_values),
        common_random_numbers=common_random_numbers,
        seed_replicate=seed_replicate,
    )
    root = results_root or RESULTS
    exp_id = provenance.experiment_id("gate4.2", stage, cfg.as_dict())
    out_dir = root / "processed" / exp_id
    started = time.time()
    result = estimate_conditional_map(cfg)
    seconds = time.time() - started
    result["label"] = label
    result["experiment_id"] = exp_id
    result["runtime_seconds"] = seconds

    manifest = provenance.build_manifest(
        gate="4.2", stage=stage, config=cfg.as_dict(),
        streams=[{"role": "conditional_map",
                  "rule": "SeedSequence([master_seed, STREAM_CONDITIONAL, "
                          "seed_replicate, grid_part, batch]); grid_part is 0 "
                          "under common random numbers, else e_index+1"}],
        extra={"label": label, "runtime_seconds": seconds,
               "n_grid_points": len(cfg.e_values),
               "n_paths_total": len(cfg.e_values) * n_paths_per_e},
    )
    provenance.write_manifest(manifest, out_dir / "manifest.json")
    storage.write_json(result, out_dir / "map.json")
    rows = [{k: v for k, v in r.items()
             if not isinstance(v, list)} for r in result["records"]]
    storage.write_csv(rows, out_dir / "map.csv")
    columns = {
        "e": np.array([r["e"] for r in result["records"]]),
        "F1": np.array([r["F1"] for r in result["records"]]),
        "F1_se": np.array([r["F1_se"] for r in result["records"]]),
        "mean_tau": np.array([r["mean_tau"] for r in result["records"]]),
    }
    storage.write_parquet(columns, root / "raw" / exp_id / "map_points.parquet",
                          metadata={"experiment_id": exp_id, "gate": "4.2"})
    if progress:
        print(f"  [4.2/{stage}] {label}: {len(cfg.e_values)} points x "
              f"{n_paths_per_e} paths, m={m}, CRN={common_random_numbers}, "
              f"seed_rep={seed_replicate} ({seconds:.0f}s)", flush=True)
    return {"experiment_id": exp_id, "out_dir": out_dir, "result": result,
            "manifest": manifest}


def run_gate42_gamma(
    *,
    stage: str,
    n_paths: int,
    m_values: Sequence[int],
    master_seed: int,
    n_batches: int = 20,
    seed_replicates: Sequence[int] = (0, 1),
    results_root: Path | None = None,
    progress: bool = True,
) -> dict[str, Any]:
    """Score/likelihood-ratio route to ``Gamma(m)`` and ``F_1'(0)``."""
    root = results_root or RESULTS
    config = {"gate": "4.2", "route": "score_likelihood_ratio",
              "n_paths": n_paths, "m_values": list(m_values),
              "master_seed": master_seed, "n_batches": n_batches,
              "seed_replicates": list(seed_replicates)}
    exp_id = provenance.experiment_id("gate4.2-gamma", stage, config)
    out_dir = root / "processed" / exp_id
    records = []
    started = time.time()
    for m in m_values:
        for rep in seed_replicates:
            rec = score_gamma(n_paths=n_paths, m=int(m), master_seed=master_seed,
                              n_batches=n_batches, seed_replicate=int(rep))
            records.append(rec)
            if progress:
                print(f"  [4.2/{stage}] score route m={m} seed_rep={rep}: "
                      f"Gamma={rec['gamma']:.4f}+/-{rec['gamma_se']:.4f}  "
                      f"F1'(0)={rec['F1_prime_0']:.4f}  ARL0={rec['arl_0']:.1f}",
                      flush=True)
    payload = {"experiment_id": exp_id, "config": config, "records": records,
               "runtime_seconds": time.time() - started}
    manifest = provenance.build_manifest(
        gate="4.2", stage=stage, config=config,
        extra={"route": "score_likelihood_ratio",
               "runtime_seconds": payload["runtime_seconds"]},
    )
    provenance.write_manifest(manifest, out_dir / "manifest.json")
    storage.write_json(payload, out_dir / "gamma.json")
    storage.write_csv([{k: v for k, v in r.items() if not isinstance(v, list)}
                       for r in records], out_dir / "gamma.csv")
    return {"experiment_id": exp_id, "out_dir": out_dir, "records": records}
