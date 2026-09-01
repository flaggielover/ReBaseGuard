"""Stage 2 -- pilot and screen, on TUNE seeds only.

Two things happen here, in this order, and the order matters:

  1. the PILOT measures ``Coll`` for the BASELINES ONLY, and gate G-E's
     threshold is written from those numbers before any SAW ``Coll`` exists
     (EXPERIMENT_PROTOCOL.md section 8);
  2. the SCREEN runs every registered policy on in-control + reference + cost
     metrics and applies the early-stop rules ES1-ES5.

Screening may ELIMINATE, never SELECT (COMPUTE_PLAN.md section 2).
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))
from _registry import (RESULTS, RHO_GRID, baselines, load_calibration,  # noqa: E402
                       oracles, saw_family)

from rebaseguard_p6c.chain import simulate_policy_chain            # noqa: E402
from rebaseguard_p6c.policy import ConstantPolicy                  # noqa: E402
from rebaseguard_p6c.runner import run_incontrol                   # noqa: E402
from rebaseguard_p6c.seeds import generator                        # noqa: E402
from rebaseguard_p6c import metrics as M                           # noqa: E402

DETECTORS = ("cusum", "sr")
M_GRID = (1, 2, 3, 5)
FAMILY = "tune"
N_REP, N_CYCLES, BURN_IN = 4000, 60, 15
PAIR = "screen_paired"


def median_abs_zbar(detector, m):
    """TUNE-measured median |zbar| at the reference rho; sets B6/B11's threshold."""
    rng = generator(family=FAMILY, detector=detector, m=m,
                    policy_id="q_zbar", cell_tag="pilot")
    res = simulate_policy_chain(detector=detector,
                                policy=ConstantPolicy(rho=0.2, m=m),
                                n_rep=1500, n_cycles=60, burn_in=15, e0=0.0,
                                rng=rng)
    return float(np.median(np.abs(res.post(res.zbar))))


def summarise(out, res):
    """Scalar summary of one cell (means over replicates) + the R1-R3 pieces."""
    s = {k: float(np.mean(v)) for k, v in out.items()}
    s["n_rep"] = int(res.tau.shape[0])
    s["tau1"] = float(res.tau[:, 0].mean())
    s["tau2"] = float(res.tau[:, 1].mean())
    s["Coll"] = s["tau2"] / s["tau1"]
    s["tau_by_cycle"] = res.tau.mean(axis=0).round(3).tolist()
    s["rms_by_cycle"] = np.sqrt((res.e_start ** 2).mean(axis=0)).round(5).tolist()
    s["rho_mean"] = float(res.post(res.rho).mean())
    s["rho_p05"] = float(np.quantile(res.post(res.rho), 0.05))
    s["rho_p95"] = float(np.quantile(res.post(res.rho), 0.95))
    return s


def run_group(policies, detector, m, cb):
    rows = {}
    per_rep = {}
    for pid, pol in policies.items():
        out, res = run_incontrol(policy=pol, detector=detector, m=m, family=FAMILY,
                                 n_rep=N_REP, n_cycles=N_CYCLES, burn_in=BURN_IN,
                                 e0=0.0, c_beta=cb, pair_tag=PAIR)
        rows[pid] = summarise(out, res)
        rows[pid]["policy_name"] = pol.name
        rows[pid]["policy_class"] = pol.policy_class
        per_rep[pid] = {k: np.asarray(v) for k, v in out.items()}
        per_rep[pid]["Coll"] = res.tau[:, 1] / res.tau[:, 0]
    return rows, per_rep


def main():
    t0 = time.time()
    cal = load_calibration()
    corr = json.loads((RESULTS / "correspondence.json").read_text())

    pilot = {}
    screen = {}
    for det in DETECTORS:
        cb = {b: corr["c_beta"][det][b]["c"] for b in ("0.75", "0.5", "0.25", "0.1")}
        for m in M_GRID:
            key = f"{det}_m{m}"
            q = median_abs_zbar(det, m)
            base = baselines(det, m, q)
            # ---- PILOT: baselines only, and G-E is set from these numbers ----
            brows, bper = run_group(base, det, m, cb)
            pilot[key] = {"q_zbar": q, "rows": brows}
            print(f"pilot {key} done ({time.time()-t0:.0f}s)", flush=True)
            # ---- SCREEN: SAW family + oracles, same seeds -------------------
            fam = saw_family(cal, det, m)
            orc = oracles(cal, det, m)
            srows, sper = run_group({**fam, **orc}, det, m, cb)
            screen[key] = {"q_zbar": q, "rows": {**brows, **srows}}
            np.savez_compressed(
                RESULTS / f"screen_perrep_{key}.npz",
                **{f"{pid}|{mt}": arr
                   for pid, d in {**bper, **sper}.items()
                   for mt, arr in d.items()})
            print(f"screen {key} done ({time.time()-t0:.0f}s)", flush=True)

    (RESULTS / "pilot.json").write_text(json.dumps(pilot, indent=1))
    (RESULTS / "screen.json").write_text(json.dumps(screen, indent=1))

    # --- gate G-E, from baseline Coll only ---------------------------------
    coll = {k: {p: v["rows"][p]["Coll"] for p in v["rows"]
                if p.startswith(("B0", "B2", "B3"))} for k, v in pilot.items()}
    b3 = [c["B3_full_reuse"] for c in coll.values()]
    b2best = [max(v for p, v in c.items() if p.startswith("B2")) for c in coll.values()]
    (RESULTS / "gate_e.json").write_text(json.dumps({
        "execution_order": [
            "1. baselines B0/B2/B3 measured for Coll (this file)",
            "2. G-E threshold written from those numbers",
            "3. only then is Coll computed for SAW",
        ],
        "baseline_coll": coll,
        "B3_full_reuse_coll_range": [min(b3), max(b3)],
        "B2_best_coll_range": [min(b2best), max(b2best)],
        "threshold": None,
        "note": "threshold filled by set_gate_e.py from these numbers alone",
    }, indent=1))
    print(f"total {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
