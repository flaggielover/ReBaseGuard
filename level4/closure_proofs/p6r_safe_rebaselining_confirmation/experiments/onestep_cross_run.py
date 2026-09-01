"""Compute the declared cross-chain one-step statistic (post-anchor; see module docstring)."""
from __future__ import annotations

import json

import numpy as np

import _p6r_paths as P                                              # noqa: F401
from _p6r_paths import PRECOMMIT, RESULTS

from rebaseguard_p6c.calibrate import SawCalibration                # noqa: E402
from rebaseguard_p6c.policy import ConstantPolicy                   # noqa: E402
from rebaseguard_p6c.runner import run_incontrol                    # noqa: E402
from rebaseguard_p6c.saw import SawPolicy                           # noqa: E402
from rebaseguard_p6r.onestep import one_step_risk_gain, per_replicate_sums
from rebaseguard_p6r.onestep_cross import cross_chain_gain          # noqa: E402

DET, M, K, FAMILY, PAIR = "cusum", 3, 3, "eval", "p6r_confirm_paired"
N_IC, N_CYC, BURN = 8000, 100, 15


def main():
    cal = SawCalibration(**json.loads(
        (P.P6 / "results" / "calibration.json").read_text())[f"{DET}_m{M}"]["final"])
    sel = json.loads((PRECOMMIT / "baseline_selection.json").read_text())
    rho_t = float(sel["cells"][f"{DET}_m{M}"]["rho_selected"])
    rho_a = float(sel["adjudication_control_rho"])
    out = {"note": ("The cross-chain statistic declared in REPAIRED_PROTOCOL.md "
                    "section 9.  Computed AFTER the Checkpoint A anchor because "
                    "the Checkpoint A code computed the control's own gain "
                    "instead.  Formula unchanged from the declaration."),
           "cell": {"detector": DET, "m": M, "k": K},
           "rho_tune": rho_t, "rho_adj": rho_a, "blocks": {}}

    for name, pol in (("SAW_M", SawPolicy(cal, k=K, mode="full")),
                      (f"FIXED_TUNE_rho{rho_t:g}",
                       ConstantPolicy(rho=rho_t, m=M, k=K)),
                      (f"FIXED_ADJ_rho{rho_a:g}",
                       ConstantPolicy(rho=rho_a, m=M, k=K))):
        _, res = run_incontrol(policy=pol, detector=DET, m=M, family=FAMILY,
                               n_rep=N_IC, n_cycles=N_CYC, burn_in=BURN, e0=0.0,
                               cell_tag="P", pair_tag=PAIR)
        own = one_step_risk_gain(per_replicate_sums(res, nu=1.0 / K), seed=21)
        cross = cross_chain_gain(res, cal, K, seed=22)
        out["blocks"][name] = {
            "chain_of": name,
            "own_policy_gain_over_best_constant": own,
            "SAW_M_rule_gain_on_this_chain": cross,
        }
        print(f"{name}: own G={own['G']:+.5f}  SAW-rule G on this chain="
              f"{cross['G']:+.5f} [{cross['bca_lo']:+.5f},{cross['bca_hi']:+.5f}] "
              f"(rho_mean {cross['rho_mean_counterfactual']:.4f})", flush=True)

    (RESULTS / "p6r_onestep_cross.json").write_text(json.dumps(out, indent=1))
    print("wrote p6r_onestep_cross.json")


if __name__ == "__main__":
    main()
