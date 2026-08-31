"""Targeted independent replay for the final P7 adjudication.

This is intentionally smaller than the production campaign.  It uses a seed
family absent from both production and the campaign's own adversarial replay,
and attacks only the headline ARL/FAP, finite-cycle, and delay-tail claims.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

CAMPAIGN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CAMPAIGN / "src"))

from rebaseguard_p7 import CUSUM, CUSUM_THRESHOLD, SR, SR_THRESHOLD  # noqa: E402
from rebaseguard_p7.chain import simulate_chain  # noqa: E402
from rebaseguard_p7.config import DETECTOR_CODE, RESULTS  # noqa: E402


SEED_FAMILY = 20260917
IN_CONTROL_N_REP = 2_500
IN_CONTROL_N_CYCLES = 40
DELAY_N_REP = 30_000
DELAY_SHIFT_CYCLE = 25


def threshold(detector: str) -> float:
    return CUSUM_THRESHOLD if detector == CUSUM else SR_THRESHOLD


def seed(detector: str, m: int, rho: float, stage: int) -> np.random.SeedSequence:
    return np.random.SeedSequence(
        [SEED_FAMILY, stage, DETECTOR_CODE[detector], m, int(round(rho * 1e7))]
    )


def main() -> None:
    production = json.loads((RESULTS / "consequences.json").read_text())
    prod_index = {
        (c["detector"], c["m"], round(c["rho"], 10)): c
        for c in production["cells"]
    }

    in_control = []
    for detector in (CUSUM, SR):
        for m in (1, 2, 3, 5):
            for rho in (0.0, 1.0):
                result = simulate_chain(
                    detector=detector,
                    m=m,
                    rho=rho,
                    n_rep=IN_CONTROL_N_REP,
                    n_cycles=IN_CONTROL_N_CYCLES,
                    burn_in=12,
                    e0=0.0,
                    threshold=threshold(detector),
                    rng=np.random.Generator(np.random.PCG64(seed(detector, m, rho, 71))),
                )
                per_rep = result.tau[:, 12:].mean(axis=1)
                post = result.tau[:, 12:]
                prod = prod_index[(detector, m, rho)]
                combined_se = np.sqrt(
                    (per_rep.std(ddof=1) / np.sqrt(IN_CONTROL_N_REP)) ** 2
                    + prod["arl_se"] ** 2
                )
                row = {
                    "detector": detector,
                    "m": m,
                    "rho": rho,
                    "arl": float(per_rep.mean()),
                    "arl_se": float(per_rep.std(ddof=1) / np.sqrt(IN_CONTROL_N_REP)),
                    "production_arl": prod["arl"],
                    "z_vs_production": float((per_rep.mean() - prod["arl"]) / combined_se),
                    "fap100": float((post <= 100).mean()),
                    "cycle_1_arl": float(result.tau[:, 0].mean()),
                    "cycle_2_arl": float(result.tau[:, 1].mean()),
                }
                in_control.append(row)
                print(
                    f"IC {detector} m={m} rho={rho:g}: ARL={row['arl']:.2f} "
                    f"FAP100={row['fap100']:.3f} c1={row['cycle_1_arl']:.1f} "
                    f"c2={row['cycle_2_arl']:.1f} z={row['z_vs_production']:+.2f}",
                    flush=True,
                )

    delay = []
    for detector, m in ((CUSUM, 1), (SR, 5)):
        result = simulate_chain(
            detector=detector,
            m=m,
            rho=1.0,
            n_rep=DELAY_N_REP,
            n_cycles=DELAY_SHIFT_CYCLE + 1,
            burn_in=12,
            e0=0.0,
            shift=1.0,
            shift_cycle=DELAY_SHIFT_CYCLE,
            threshold=threshold(detector),
            rng=np.random.Generator(np.random.PCG64(seed(detector, m, 1.0, 72))),
        )
        values = result.tau[:, DELAY_SHIFT_CYCLE].astype(float)
        effective_error = result.e_start[:, DELAY_SHIFT_CYCLE]
        blind = np.abs(effective_error) < 0.2
        row = {
            "detector": detector,
            "m": m,
            "rho": 1.0,
            "shift": 1.0,
            "mean": float(values.mean()),
            "mean_se": float(values.std(ddof=1) / np.sqrt(DELAY_N_REP)),
            "median": float(np.median(values)),
            "q95": float(np.quantile(values, 0.95)),
            "p_gt_100": float(np.mean(values > 100)),
            "p_gt_100_se": float(
                np.sqrt(np.mean(values > 100) * (1.0 - np.mean(values > 100)) / DELAY_N_REP)
            ),
            "p_entering_reference_within_0p2_of_post_change_mean": float(blind.mean()),
            "mean_delay_inside_0p2": float(values[blind].mean()),
            "mean_delay_outside_0p2": float(values[~blind].mean()),
            "p_gt_100_inside_0p2": float(np.mean(values[blind] > 100)),
            "p_gt_100_outside_0p2": float(np.mean(values[~blind] > 100)),
            "max_delay": int(values.max()),
        }
        delay.append(row)
        print(
            f"DELAY {detector} m={m}: mean={row['mean']:.2f} "
            f"median={row['median']:.0f} q95={row['q95']:.0f} "
            f"P>100={row['p_gt_100']:.4f} blind={row['p_entering_reference_within_0p2_of_post_change_mean']:.3f}",
            flush=True,
        )

    counts = json.loads((RESULTS / "boundary_verdict.json").read_text())[
        "families_peaking_at_boundary_per_metric"
    ]
    output = {
        "purpose": "independent targeted replay for final P7 adjudication",
        "seed_family": SEED_FAMILY,
        "production_seed_family": 20260831,
        "campaign_adversarial_seed_family": 20260901,
        "in_control_n_rep": IN_CONTROL_N_REP,
        "in_control_n_cycles": IN_CONTROL_N_CYCLES,
        "delay_n_rep": DELAY_N_REP,
        "delay_shift_cycle": DELAY_SHIFT_CYCLE,
        "in_control": in_control,
        "delay": delay,
        "boundary_counts_recomputed_from_frozen_result": counts,
        "boundary_threshold": 4,
        "boundary_criterion_met": max(counts.values()) >= 4,
    }
    path = RESULTS / "independent_adjudication_replay.json"
    path.write_text(json.dumps(output, indent=1) + "\n")
    print("wrote", path)


if __name__ == "__main__":
    main()
