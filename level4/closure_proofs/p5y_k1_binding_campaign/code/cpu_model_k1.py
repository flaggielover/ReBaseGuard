"""P5Y K1 binding campaign -- CPU model and hard-cap derivation.

DESIGN ARTIFACT. Pure arithmetic over ALREADY-MEASURED gate primitives.
Executes no certified numerics, produces no production result, and is
non-result-bearing: running it cannot change any scientific verdict.
"""
from __future__ import annotations

import json
import math
import pathlib

# ---------------------------------------------------------------- primitives
# Every value below was MEASURED by a completed P5Y gate; none is invented here.
SR_ALL_SCOPE_CPU_H = 2227.792819637778      # Gate-2B /cost/cpu_sr_hours
CUSUM_ALL_SCOPE_CPU_H = 70.13078166378472   # Gate-2B /cost/cusum_total_hours
N_FUNCTIONS_ALL_SCOPE = 49                  # Gate-2B /frozen/n_functions  (24.5 units x 2)
N_FUNCTIONS_K1 = 19                         # Gate-1 MSHARE union, FIRST moment only
C3_DERIVATIVE_FACTOR = 1.17                 # H2/H3a rung  -> K4/K5, OUT of K1 scope
OVERHEAD_FACTOR = 1.15                      # assembly + resolvent + auditor replay
RATIO_PER_UNIT_M_GT_1 = 0.629               # Gate-2C-bis MEASURED m>1 per-function ratio
N_FUNCTIONS_M1 = 2                          # F_0, d_e F_0  (the only m=1 consumers)
SR_COVER_UPPER = 322                        # Gate-2B /cover/subcell_count_upper_bound
SR_COVER_LOWER = 309                        # Gate-2B /cover/subcell_count_lower_bound
BITS_384_TPANEL_FACTOR = 1.202              # Gate-2A measured t_panel(384)/t_panel(256)
COVER_ENVELOPE_SLACK = 1.25                 # monotone-envelope walk may understate cover
BETA_CAP = 1.5                              # governance-inherited (Gate-2C-bis)

PROGRAMME_CENTRAL_CARRIED = 3091.856205551252   # Gate-2B /cost/bands/central/cpu_hours


def programme_central() -> float:
    """Reproduce the carried programme central band from primitives."""
    base = SR_ALL_SCOPE_CPU_H + CUSUM_ALL_SCOPE_CPU_H
    return base * C3_DERIVATIVE_FACTOR * OVERHEAD_FACTOR


def k1_scope_factor() -> float:
    """Two factors removed BY SCOPE, not by optimism."""
    return (N_FUNCTIONS_K1 / N_FUNCTIONS_ALL_SCOPE) / C3_DERIVATIVE_FACTOR


def bands() -> dict:
    sr = SR_ALL_SCOPE_CPU_H * N_FUNCTIONS_K1 / N_FUNCTIONS_ALL_SCOPE
    cu = CUSUM_ALL_SCOPE_CPU_H * N_FUNCTIONS_K1 / N_FUNCTIONS_ALL_SCOPE
    central = (sr + cu) * OVERHEAD_FACTOR

    n_gt1 = N_FUNCTIONS_K1 - N_FUNCTIONS_M1
    f_share = (N_FUNCTIONS_M1 + n_gt1 * RATIO_PER_UNIT_M_GT_1) / N_FUNCTIONS_K1
    f_cover = SR_COVER_LOWER / SR_COVER_UPPER
    optimistic = central * f_share * f_cover
    conservative = central * BITS_384_TPANEL_FACTOR
    worst = conservative * COVER_ENVELOPE_SLACK
    cap = math.ceil(BETA_CAP * conservative)
    return {
        "sr_k1_cpu_hours": sr,
        "cusum_k1_cpu_hours": cu,
        "k1_scope_factor": k1_scope_factor(),
        "optimistic": optimistic,
        "central": central,
        "conservative": conservative,
        "worst_plausible": worst,
        "f_share_m_gt_1": f_share,
        "f_cover_lower": f_cover,
        "hard_cpu_cap": cap,
        "cap_over_worst": cap / worst,
        "cap_over_central": cap / central,
        "soft_expected_band": [central, conservative],
    }


def main() -> int:
    pc = programme_central()
    b = bands()
    out = {
        "schema": "rebaseguard.p5y.k1.cpumodel.v1",
        "binding": True,
        "result_bearing": False,
        "programme_central_recomputed": pc,
        "programme_central_carried": PROGRAMME_CENTRAL_CARRIED,
        "programme_central_reproduces": abs(pc - PROGRAMME_CENTRAL_CARRIED) < 1e-6,
        "primitives": {
            "SR_ALL_SCOPE_CPU_H": SR_ALL_SCOPE_CPU_H,
            "CUSUM_ALL_SCOPE_CPU_H": CUSUM_ALL_SCOPE_CPU_H,
            "N_FUNCTIONS_ALL_SCOPE": N_FUNCTIONS_ALL_SCOPE,
            "N_FUNCTIONS_K1": N_FUNCTIONS_K1,
            "C3_DERIVATIVE_FACTOR": C3_DERIVATIVE_FACTOR,
            "OVERHEAD_FACTOR": OVERHEAD_FACTOR,
            "RATIO_PER_UNIT_M_GT_1": RATIO_PER_UNIT_M_GT_1,
            "BITS_384_TPANEL_FACTOR": BITS_384_TPANEL_FACTOR,
            "COVER_ENVELOPE_SLACK": COVER_ENVELOPE_SLACK,
            "BETA_CAP": BETA_CAP,
        },
        "bands_cpu_hours": b,
    }
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
