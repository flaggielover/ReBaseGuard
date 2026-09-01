"""Checkpoint A — freeze the repaired protocol.  TUNE ONLY.  No EVAL, no REPLAY.

Produces, in this order:

  1. ``precommit/calibration_audit.json``   the per-cell diagnostics Q3 requires
  2. ``precommit/s1_sensitivity.json``      the predeclared sparse-cell check
  3. ``precommit/baseline_selection.json``  rule S1 run on TUNE, per cell
  4. ``precommit/PRECOMMIT_MANIFEST.json``  the frozen constants + document hashes

Nothing here touches the EVAL or REPLAY seed families.  ``tests/test_p6r_scope.py``
asserts that.

    python experiments/precommit_freeze.py
"""
from __future__ import annotations

import hashlib
import json
import time

import numpy as np

import _p6r_paths as P                                            # noqa: F401
from _p6r_paths import PRECOMMIT, RESULTS, ROOT

from rebaseguard_p6c.calibrate import SawCalibration               # noqa: E402
from rebaseguard_p6c.chain import simulate_policy_chain            # noqa: E402
from rebaseguard_p6c.policy import ConstantPolicy                  # noqa: E402
from rebaseguard_p6c.saw import SawPolicy                          # noqa: E402
from rebaseguard_p6c.seeds import generator                        # noqa: E402
from rebaseguard_p6r import select as SEL                          # noqa: E402
from rebaseguard_p6r import stats_r as ST                          # noqa: E402
from rebaseguard_p6r.audit import (S1_SPARSE_THRESHOLD,            # noqa: E402
                                   audit_calibration)

DETECTORS = ("cusum", "sr")
M_GRID = (1, 2, 3, 5)
FAMILY = "tune"                       # THE ONLY family this script may touch
PRECOMMIT_DOCS = ("ADJUDICATION_RECORD.md", "THEOREM_SCOPE.md",
                  "REPAIRED_PROTOCOL.md", "NOVELTY_SCOPE.md", "README.md")


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# 2. predeclared s1 sensitivity for sparse cells
# ---------------------------------------------------------------------------

def s1_sensitivity(aud, n_rep=1500, n_cycles=60, burn_in=15):
    """Perturb ``s1`` to {0.5x, 2x, s0} and measure the effect on decisions.

    Declared in REPAIRED_PROTOCOL.md section 8 BEFORE execution.  Reported for
    EVERY cell, so that a stable primary cell cannot be used to excuse an
    unstable secondary one.
    """
    out = {}
    for key, c in aud["cells"].items():
        det, m, k = c["detector"], c["m"], c["k"]
        base = SawCalibration(
            detector=det, m=m, k=k, g0=c["g0"], g1=c["g1"], s0=c["s0"],
            s1=c["s1"], n_obs=c["n_calibration_cycles"],
            iterations=c["iterations_reached"], converged=c["converged"],
            seed_family="tune", resid_var=float("nan"), r2=c["r2"])
        variants = {"fitted": c["s1"], "half": 0.5 * c["s1"],
                    "double": 2.0 * c["s1"], "equal_to_s0": c["s0"]}
        rows = {}
        for name, s1 in variants.items():
            cal = SawCalibration(**{**base.to_dict(), "s1": float(s1)})
            rng = generator(family=FAMILY, detector=det, m=m,
                            policy_id=f"s1sens_{name}", cell_tag="precommit")
            res = simulate_policy_chain(detector=det,
                                        policy=SawPolicy(cal, k=k, mode="full"),
                                        n_rep=n_rep, n_cycles=n_cycles,
                                        burn_in=burn_in, e0=0.0, rng=rng)
            rho = res.post(res.rho)
            rows[name] = {"rho_mean": float(rho.mean()),
                          "rms": float(np.sqrt((res.post(res.e_start) ** 2).mean())),
                          "arl0": float(res.post(res.tau).mean())}
        ref = rows["fitted"]
        out[key] = {
            "n_obs_behind_s1": c["n_obs_behind_s1"],
            "s1_sparse": c["s1_sparse"],
            "s1_is_fallback_equal_to_s0": c["s1_is_fallback_equal_to_s0"],
            "variants": rows,
            "max_abs_rel_change_rho_mean": max(
                abs(v["rho_mean"] / ref["rho_mean"] - 1.0) for v in rows.values()),
            "max_abs_rel_change_rms": max(
                abs(v["rms"] / ref["rms"] - 1.0) for v in rows.values()),
            "max_abs_rel_change_arl0": max(
                abs(v["arl0"] / ref["arl0"] - 1.0) for v in rows.values()),
        }
        print(f"  s1-sensitivity {key} done", flush=True)
    return {"threshold_for_sparse": S1_SPARSE_THRESHOLD, "cells": out,
            "note": ("Reported for every cell.  Primary-cell stability does NOT "
                     "excuse an unstable secondary cell.")}


# ---------------------------------------------------------------------------
# 3. rule S1, on TUNE only
# ---------------------------------------------------------------------------

def tune_selection(detector, m, k):
    d100, dq95, ev = [], [], []
    for rho in SEL.RHO_FINE:
        rng = generator(family=FAMILY, detector=detector, m=m,
                        policy_id=f"S1_rho{rho:g}", cell_tag="baseline_selection")
        res = simulate_policy_chain(
            detector=detector, policy=ConstantPolicy(rho=rho, m=m, k=k),
            n_rep=SEL.N_SELECT, n_cycles=SEL.SELECT_SHIFT_CYCLE + 1,
            burn_in=SEL.SELECT_SHIFT_CYCLE, e0=0.0, shift=SEL.SELECT_SHIFT,
            shift_cycle=SEL.SELECT_SHIFT_CYCLE, rng=rng)
        d = res.tau[:, SEL.SELECT_SHIFT_CYCLE].astype(float)
        d100.append(float((d > 100).mean()))
        dq95.append(float(np.quantile(d, 0.95)))
        ev.append(int((d > 100).sum()))
    sel = SEL.select_rho(d100, dq95)
    sel.update(detector=detector, m=m, k=k, family=FAMILY,
               n_rep_per_point=SEL.N_SELECT, n_events_100=ev,
               shift=SEL.SELECT_SHIFT, shift_cycle=SEL.SELECT_SHIFT_CYCLE)
    return sel


def diagnostics_incontrol(detector, m, k):
    """TUNE Arl0-argmax and Rms-argmin over the same grid, as recorded diagnostics."""
    arl, rms = [], []
    for rho in SEL.RHO_FINE:
        rng = generator(family=FAMILY, detector=detector, m=m,
                        policy_id=f"S1diag_rho{rho:g}", cell_tag="baseline_selection")
        res = simulate_policy_chain(
            detector=detector, policy=ConstantPolicy(rho=rho, m=m, k=k),
            n_rep=4000, n_cycles=60, burn_in=15, e0=0.0, rng=rng)
        arl.append(float(res.post(res.tau).mean()))
        rms.append(float(np.sqrt((res.post(res.e_start) ** 2).mean())))
    g = np.asarray(SEL.RHO_FINE, float)
    return {"arl0_tune": arl, "rms_tune": rms,
            "rho_argmax_arl0": float(g[int(np.argmax(arl))]),
            "rho_argmin_rms": float(g[int(np.argmin(rms))]),
            "rho_argmax_arl0_smoothed": float(
                g[int(np.argmax(SEL.moving_average(arl)))]),
            "rho_argmin_rms_smoothed": float(
                g[int(np.argmin(SEL.moving_average(rms)))])}


def main():
    t0 = time.time()
    PRECOMMIT.mkdir(exist_ok=True)
    RESULTS.mkdir(exist_ok=True)

    aud = audit_calibration()
    (PRECOMMIT / "calibration_audit.json").write_text(json.dumps(aud, indent=1))
    print("calibration audit done", flush=True)

    sens = s1_sensitivity(aud)
    (PRECOMMIT / "s1_sensitivity.json").write_text(json.dumps(sens, indent=1))
    print(f"s1 sensitivity done ({time.time()-t0:.0f}s)", flush=True)

    sel = {}
    for det in DETECTORS:
        for m in M_GRID:
            key = f"{det}_m{m}"
            row = tune_selection(det, m, m)
            row["diagnostics"] = diagnostics_incontrol(det, m, m)
            sel[key] = row
            print(f"S1 {key}: rho*_TUNE = {row['rho_selected']:.2f} "
                  f"(unsmoothed argmin {row['rho_argmin_unsmoothed']:.2f}, "
                  f"Arl0 argmax {row['diagnostics']['rho_argmax_arl0_smoothed']:.2f}, "
                  f"Rms argmin {row['diagnostics']['rho_argmin_rms_smoothed']:.2f}) "
                  f"[{time.time()-t0:.0f}s]", flush=True)
    (PRECOMMIT / "baseline_selection.json").write_text(json.dumps(
        {"rule": "S1", "grid": list(SEL.RHO_FINE),
         "family": FAMILY,
         "adjudication_control_rho": SEL.ADJUDICATION_CONTROL_RHO,
         "n_rep_per_point": SEL.N_SELECT,
         "smoothing_halfwidth": SEL.SMOOTH_HALFWIDTH,
         "cells": sel}, indent=1))

    manifest = {
        "checkpoint": "A",
        "purpose": "temporal anchor: frozen protocol, TUNE-only evidence",
        "contains_eval_results": False,
        "contains_replay_results": False,
        "documents": {d: _sha(ROOT / d) for d in PRECOMMIT_DOCS
                      if (ROOT / d).exists()},
        "frozen_constants": {
            "rho_grid": list(SEL.RHO_FINE),
            "selection_rule": "S1",
            "n_rep_selection": SEL.N_SELECT,
            "smoothing_halfwidth": SEL.SMOOTH_HALFWIDTH,
            "adjudication_control_rho": SEL.ADJUDICATION_CONTROL_RHO,
            "n_boot": ST.N_BOOT,
            "alpha": ST.ALPHA,
            "bh_q": ST.BH_Q,
            "tail_event_floor": ST.TAIL_EVENT_FLOOR,
            "materiality_relative": 0.10,
            "primary_cell": {"detector": "cusum", "m": 3, "k": 3, "shift": 1.0},
            "in_control": {"n_rep": 8000, "n_cycles": 100, "burn_in": 15},
            "delay": {"n_rep": 60000, "shift_cycle": 15},
            "cost_primary": "C_acq = k_j * 1{rho_j < 1}  (fresh-sample acquisition cost)",
            "cost_sensitivities": ["(1-rho_j)*k_j", "(1-rho_j)^2*k_j"],
        },
        "selected_rho_tune": {k: v["rho_selected"] for k, v in sel.items()},
        "calibration_summary": aud["summary"],
        "seconds": time.time() - t0,
    }
    (PRECOMMIT / "PRECOMMIT_MANIFEST.json").write_text(json.dumps(manifest, indent=1))
    print(f"precommit frozen in {time.time()-t0:.0f}s", flush=True)
    print("selected rho*_TUNE:", manifest["selected_rho_tune"])


if __name__ == "__main__":
    main()
