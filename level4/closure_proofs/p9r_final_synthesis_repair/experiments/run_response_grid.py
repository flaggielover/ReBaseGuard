#!/usr/bin/env python3
"""R4 (A6 repair) — the run-length response ``A(e)``, its mixture, and the
monotonicity audit.

This is the generator that P9's ``results/p9t2_mixture_check.json`` never had.

What it computes
----------------
1. ``A(e)`` on a uniform half-grid ``e in [0, L]`` for each frozen detector,
   by direct single-cycle simulation from the reset state.  ``A`` depends on
   the detector only, not on ``m`` or ``rho``, so one grid per detector serves
   every window.
2. For each ``m``, the stationary ``rho=0`` mixture
   ``E_{e~N(0,1/m)}[A(e)] = 2 * int_0^inf A(e) phi_{1/sqrt(m)}(e) de``
   (evenness of ``A`` is an exact lemma, corroborated in check 4), by composite
   Simpson on the half-grid, with a **three-part error budget**:
     * Monte Carlo: node standard errors propagated through the Simpson weights;
     * discretisation: Richardson estimate from the half-resolution grid;
     * truncation: rigorously bounded by ``2 * C_D * P(|e| > L)`` using the
       exact uniform bound ``sup_e A(e) <= C_D`` of ``THEORY.md`` Lemma L2.
   P9 left this error "unquantified"; here every component is reported.
3. A monotonicity audit that reports, per adjacent node pair, whether an
   *increase* is detected at three combined standard errors, **and** the
   minimum detectable increase at each pair, so the audit's power is visible
   instead of implied.
4. An evenness check at a subset of nodes, with independent seeds.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from scipy.stats import norm

P9R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(P9R / "src"))

from rebaseguard_p9r import DETECTORS, H_FROZEN, K_FROZEN, SR_THRESHOLD  # noqa: E402
from rebaseguard_p9r.chain import response_A                             # noqa: E402
from rebaseguard_p9r.provenance import seed_for, write_artifact          # noqa: E402

GRID_MAX = 8.0
N_INTERVALS = 320          # 321 nodes, step 0.025; even, so Simpson applies
M_GRID = (1, 2, 3, 5)
EVENNESS_STRIDE = 40


def uniform_bound(detector: str) -> dict:
    """Exact uniform bound ``sup_e A(e) <= C`` — THEORY.md Lemma L2.

    CUSUM: from any reachable state, ten consecutive innovations with
    ``Z >= 1`` (or ten with ``Z <= -1``) raise one arm by at least ``1 - k``
    each and force an inclusive crossing of ``h = 5``.  For every ``e`` at
    least one of the two directions has per-step probability ``>= Phi(-1)``.
    SR: a single innovation with ``Z >= log A + 1/2`` (or ``<= -(log A + 1/2)``)
    forces an inclusive crossing from any nonnegative state; for every ``e`` at
    least one direction has per-step probability ``>= Phi(-(log A + 1/2))``.
    """
    if detector == "cusum":
        block, p = 10, float(norm.cdf(-1.0))
        return {"block_length": block, "per_step_prob_lower_bound": p,
                "block_prob_lower_bound": p ** block,
                "bound": block / p ** block,
                "argument": "10 consecutive |Z|>=1 raise an arm by >= 1-k=0.5 "
                            "each, reaching h=5 from any reachable state"}
    block, p = 1, float(norm.cdf(-(np.log(SR_THRESHOLD) + 0.5)))
    return {"block_length": block, "per_step_prob_lower_bound": p,
            "block_prob_lower_bound": p,
            "bound": 1.0 / p,
            "argument": "one innovation with |Z| >= log A + 1/2 forces an "
                        "inclusive crossing from any state y >= 0"}


def simpson_weights(n_intervals: int, h: float) -> np.ndarray:
    w = np.ones(n_intervals + 1)
    w[1:-1:2] = 4.0
    w[2:-1:2] = 2.0
    return w * h / 3.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()

    n_intervals = 40 if args.quick else N_INTERVALS
    n_paths = 1500 if args.quick else 20000
    h = GRID_MAX / n_intervals
    nodes = np.linspace(0.0, GRID_MAX, n_intervals + 1)

    detectors_out = {}
    for det in DETECTORS:
        est = np.empty(nodes.size)
        se = np.empty(nodes.size)
        for i, e in enumerate(nodes):
            sd = seed_for("response", det, n_intervals, n_paths, i)
            est[i], se[i] = response_A(detector=det, e=float(e),
                                       n_rep=n_paths, seed=sd)

        # ---- monotonicity audit -----------------------------------------
        pairs = []
        n_increase_violations = 0
        for i in range(nodes.size - 1):
            diff = est[i + 1] - est[i]
            csd = float(np.sqrt(se[i] ** 2 + se[i + 1] ** 2))
            viol = bool(diff > 3.0 * csd)
            n_increase_violations += viol
            pairs.append({"i": i, "e_lo": float(nodes[i]),
                          "e_hi": float(nodes[i + 1]),
                          "diff": float(diff), "combined_se": csd,
                          "min_detectable_increase": 3.0 * csd,
                          "increase_detected_at_3se": viol})
        # global maximality at 0 (the premise P9R-T2b actually needs)
        max_excess = float(np.max((est - est[0]) / np.sqrt(se ** 2 + se[0] ** 2)))
        argmax_node = int(np.argmax(est))

        c = uniform_bound(det)
        mixtures = {}
        for m in M_GRID:
            sigma = 1.0 / np.sqrt(m)
            dens = norm.pdf(nodes, scale=sigma)
            w = simpson_weights(n_intervals, h)
            integral = 2.0 * float(np.sum(w * dens * est))
            mc_se = 2.0 * float(np.sqrt(np.sum((w * dens * se) ** 2)))
            # half-resolution Richardson estimate of the discretisation error
            coarse_nodes = nodes[::2]
            w2 = simpson_weights(n_intervals // 2, 2 * h)
            integral_2h = 2.0 * float(np.sum(
                w2 * norm.pdf(coarse_nodes, scale=sigma) * est[::2]))
            disc = abs(integral - integral_2h) / 15.0
            tail_mass = 2.0 * float(norm.sf(GRID_MAX / sigma))
            trunc = c["bound"] * tail_mass
            mixtures[str(m)] = {
                "m": m, "sigma": sigma,
                "mixture_E_A": integral,
                "mc_se": mc_se,
                "discretisation_richardson": disc,
                "truncation_upper_bound": trunc,
                "truncation_tail_mass": tail_mass,
                "total_error_budget": float(mc_se + disc + trunc),
                "A0": float(est[0]), "A0_se": float(se[0]),
                "deficit_vs_A0": float(est[0] - integral),
            }

        idx = list(range(0, nodes.size, EVENNESS_STRIDE))
        evenness = []
        for i in idx:
            sd = seed_for("response-even", det, n_intervals, n_paths, i)
            a_neg, s_neg = response_A(detector=det, e=-float(nodes[i]),
                                      n_rep=n_paths, seed=sd)
            csd = float(np.sqrt(se[i] ** 2 + s_neg ** 2))
            evenness.append({"e": float(nodes[i]), "A_pos": float(est[i]),
                             "A_neg": a_neg, "combined_se": csd,
                             "z": float((a_neg - est[i]) / csd) if csd else 0.0})

        detectors_out[det] = {
            "nodes": [float(x) for x in nodes],
            "A": [float(x) for x in est],
            "A_se": [float(x) for x in se],
            "uniform_bound": c,
            "mixtures": mixtures,
            "monotonicity": {
                "n_pairs": len(pairs),
                "n_increase_detected_at_3se": int(n_increase_violations),
                "max_min_detectable_increase":
                    float(max(p["min_detectable_increase"] for p in pairs)),
                "median_min_detectable_increase":
                    float(np.median([p["min_detectable_increase"] for p in pairs])),
                "argmax_node_index": argmax_node,
                "argmax_e": float(nodes[argmax_node]),
                "max_z_excess_over_A0": max_excess,
                "global_max_at_zero_at_3se": bool(max_excess <= 3.0),
                "pairs": pairs,
            },
            "evenness_check": {
                "rows": evenness,
                "max_abs_z": float(max(abs(r["z"]) for r in evenness)),
                "consistent_at_3se":
                    bool(max(abs(r["z"]) for r in evenness) <= 3.0),
            },
        }

    payload = {"grid": {"max": GRID_MAX, "n_intervals": n_intervals,
                        "step": h, "n_paths_per_node": n_paths,
                        "quadrature": "composite Simpson on the half-grid, "
                                      "doubled by the exact evenness lemma"},
               "detectors": detectors_out,
               "frozen_constants": {"cusum_k": K_FROZEN, "cusum_h": H_FROZEN,
                                    "sr_A": SR_THRESHOLD}}

    name = "response_grid_quick.json" if args.quick else "response_grid.json"
    write_artifact(name,
                   schema="rebaseguard.p9r.response-grid.v1",
                   generator="experiments/run_response_grid.py",
                   config={"grid_max": GRID_MAX, "n_intervals": n_intervals,
                           "n_paths_per_node": n_paths, "m_grid": list(M_GRID),
                           "evenness_stride": EVENNESS_STRIDE,
                           "quick": args.quick},
                   payload=payload)
    for det, d in detectors_out.items():
        mono = d["monotonicity"]
        print(f"{det}: A(0)={d['A'][0]:.2f}  argmax e={mono['argmax_e']:.3f}  "
              f"increases@3se={mono['n_increase_detected_at_3se']}/"
              f"{mono['n_pairs']}  global_max_at_0={mono['global_max_at_zero_at_3se']}")
        for m, mx in d["mixtures"].items():
            print(f"   m={m}: E[A]={mx['mixture_E_A']:.3f} "
                  f"+-{mx['total_error_budget']:.3f}  A(0)={mx['A0']:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
