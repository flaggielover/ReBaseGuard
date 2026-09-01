"""The frozen policy registry: baselines B0-B11, SAW and its ablations, oracles.

Frozen at `EXPERIMENT_PROTOCOL.md` section 3.  Nothing is added to this set
after a comparison result has been seen.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT / "src", ROOT.parent / "p7_statistical_consequences" / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from rebaseguard_p6c.calibrate import SawCalibration                 # noqa: E402
from rebaseguard_p6c.policy import (                                 # noqa: E402
    CappedReusePolicy, ConfidenceGatedPolicy, ConstantPolicy,
    OracleResetPolicy, OracleShiftAwarePolicy, OvershootPolicy,
    TauThresholdWindowPolicy, WindowDispersionPolicy, ZbarThresholdPolicy,
)
from rebaseguard_p6c.saw import (                                    # noqa: E402
    OracleSawPolicy, OracleTailSawPolicy, SawPolicy, SawTailPolicy,
)

RESULTS = ROOT / "results"

#: frozen fixed-rho grid (EXPERIMENT_PROTOCOL section 3)
RHO_GRID = (0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.75)
#: the declared reference rho for heuristic baselines that need one
RHO_REF = 0.20
#: preregistered beta for SAW-T's radius
BETA_T = 0.25


def load_calibration():
    return json.loads((RESULTS / "calibration.json").read_text())


def calib_for(cal, detector, m) -> SawCalibration:
    return SawCalibration.from_dict(cal[f"{detector}_m{m}"]["final"])


def c_beta_for(detector, beta=BETA_T) -> float:
    corr = json.loads((RESULTS / "correspondence.json").read_text())
    return float(corr["c_beta"][detector][str(beta)]["c"])


def baselines(detector, m, q_zbar):
    """B0-B11.  ``q_zbar`` is the TUNE-measured median |zbar| at the reference rho."""
    out = {
        "B0_fresh_only": ConstantPolicy(rho=0.0, m=m, name=f"B0_fresh_only(m={m})"),
        "B3_full_reuse": ConstantPolicy(rho=1.0, m=m, name=f"B3_full_reuse(m={m})"),
    }
    for r in RHO_GRID:
        out[f"B2_rho{r:g}"] = ConstantPolicy(rho=r, m=m, name=f"B2_rho{r:g}(m={m})")
    out["B5_tau_window"] = TauThresholdWindowPolicy(
        rho=RHO_REF, m_short=1, m_long=m, tau_split=20)
    out["B6_zbar_two_level"] = ZbarThresholdPolicy(
        m=m, rho_lo=0.05, rho_hi=0.5, q=q_zbar)
    out["B7_overshoot"] = OvershootPolicy(m=m, rho_hi=0.5, a=1.0)
    out["B8_window_disp"] = WindowDispersionPolicy(m=m, rho_hi=0.5, a=1.0)
    out["B9_fresh_inject_2m"] = ConstantPolicy(rho=RHO_REF, m=m, k=2 * m,
                                               name=f"B9_fresh2m(m={m})")
    out["B9_fresh_inject_4m"] = ConstantPolicy(rho=RHO_REF, m=m, k=4 * m,
                                               name=f"B9_fresh4m(m={m})")
    out["B10_capped"] = CappedReusePolicy(m=m, rho=0.5, n_max=3)
    out["B11_conf_gate"] = ConfidenceGatedPolicy(m=m, rho_hi=0.5, q=q_zbar)
    return out


def saw_family(cal, detector, m, k=None, with_ablations=True):
    c = calib_for(cal, detector, m)
    entry = cal[f"{detector}_m{m}"]
    k = m if k is None else k
    cb = c_beta_for(detector)
    out = {
        "SAW_M": SawPolicy(c, k=k, mode="full", name=f"SAW_M(m={m},k={k})"),
        "SAW_T": SawTailPolicy(c, cb, k=k, mode="full",
                               name=f"SAW_T(m={m},k={k})"),
    }
    if with_ablations:
        no_tau = SawCalibration(**{**c.to_dict(),
                                   "g0": entry["g0_no_tau"], "g1": 0.0,
                                   "s0": entry["s0_no_tau"],
                                   "s1": entry["s1_no_tau"]})
        out["SAW_A_no_tau"] = SawPolicy(no_tau, k=k, mode="full",
                                        name=f"SAW_A_no_tau(m={m},k={k})")
        out["SAW_A_naive"] = SawPolicy(c, k=k, mode="naive",
                                       name=f"SAW_A_naive(m={m},k={k})")
        out["SAW_A_flat"] = SawPolicy(c, k=k, mode="flat", v_bar=entry["v_bar"],
                                      name=f"SAW_A_flat(m={m},k={k})")
    return out


def oracles(cal, detector, m, k=None):
    c = calib_for(cal, detector, m)
    k = m if k is None else k
    cb = c_beta_for(detector)
    return {
        "Z1_oracle_saw": OracleSawPolicy(c, k=k, name=f"Z1_oracle_saw(m={m},k={k})"),
        "Z2_oracle_tail": OracleTailSawPolicy(c, cb, k=k,
                                              name=f"Z2_oracle_tail(m={m},k={k})"),
        "Z3_oracle_reset": OracleResetPolicy(m=m, c=0.3, k_fresh=m),
    }


def shift_oracle(m):
    return {"Z4_oracle_shift": OracleShiftAwarePolicy(m=m, rho=RHO_REF, guard=0.3)}
