"""Checkpoint B — the repaired confirmation campaign.

REFUSES TO RUN until ``results/precommit_anchor.json`` records the Checkpoint A
commit SHA.  That is the mechanical form of the ordering discipline which
repairs blocking defect 3: no confirmation EVAL may precede the temporal anchor.

    python experiments/confirm_eval.py            # EVAL: cell P + RC1..RC4
    python experiments/confirm_eval.py replay     # RC5: primary cell only
"""
from __future__ import annotations

import json
import sys
import time

import numpy as np

import _p6r_paths as P                                             # noqa: F401
from _p6r_paths import PRECOMMIT, RESULTS

from rebaseguard_p6c.calibrate import SawCalibration                # noqa: E402
from rebaseguard_p6c.policy import ConstantPolicy                   # noqa: E402
from rebaseguard_p6c.runner import run_delay, run_incontrol         # noqa: E402
from rebaseguard_p6c.saw import SawPolicy                           # noqa: E402
from rebaseguard_p6r import costs as CO                             # noqa: E402
from rebaseguard_p6r import onestep as OS                           # noqa: E402

PRIMARY = ("cusum", 3, 3, 1.0)
RC1 = [("sr", 3)]
RC2 = [(d, m) for d in ("cusum", "sr") for m in (1, 2, 5)]
RC3_SHIFTS = (0.5, 2.0)
RC4_M0 = (20, 50, 100)
PAIR = "p6r_confirm_paired"

N_IC, N_CYC, BURN = 8000, 100, 15
N_D, SHIFT_CYCLE = 60000, 15
TAIL_RADII = (0.2, 0.5, 1.0)
BETAS = ("0.75", "0.5", "0.25", "0.1")


def _require_anchor():
    f = RESULTS / "precommit_anchor.json"
    if not f.exists():
        raise SystemExit(
            "REFUSING TO RUN: results/precommit_anchor.json does not exist.\n"
            "The Checkpoint A commit must be created and its SHA recorded "
            "BEFORE any confirmation EVAL (adjudication blocking defect 3).")
    a = json.loads(f.read_text())
    if not a.get("commit_sha") or len(a["commit_sha"]) < 7:
        raise SystemExit("REFUSING TO RUN: precommit_anchor.json has no commit SHA.")
    return a


def _calibration(det, m):
    cal = json.loads((P.P6 / "results" / "calibration.json").read_text())
    return SawCalibration(**cal[f"{det}_m{m}"]["final"])


def arms(det, m, k, rho_tune, rho_adj, reduced=False):
    a = {
        "B3_full_reuse": ConstantPolicy(rho=1.0, m=m, k=k, name=f"B3(m={m})"),
        "B0_fresh_only": ConstantPolicy(rho=0.0, m=m, k=k, name=f"B0(m={m})"),
        f"FIXED_TUNE_rho{rho_tune:g}": ConstantPolicy(
            rho=rho_tune, m=m, k=k, name=f"FIXED_TUNE(rho={rho_tune:g},m={m})"),
        "SAW_M": SawPolicy(_calibration(det, m), k=k, mode="full",
                           name=f"SAW_M(m={m},k={k})"),
    }
    if not reduced:
        a[f"FIXED_ADJ_rho{rho_adj:g}"] = ConstantPolicy(
            rho=rho_adj, m=m, k=k, name=f"FIXED_ADJ(rho={rho_adj:g},m={m})")
    return a


def _ic_block(policy, det, m, family, cb, e0=0.0, m0=5, tag="ic"):
    out, res = run_incontrol(policy=policy, detector=det, m=m, family=family,
                             n_rep=N_IC, n_cycles=N_CYC, burn_in=BURN, e0=e0,
                             m0=m0, c_beta=cb, cell_tag=tag, pair_tag=PAIR)
    per = {k: np.asarray(v, float) for k, v in out.items()}
    per.update({k: np.asarray(v, float) for k, v in CO.per_replicate_costs(res).items()})
    per["Coll_num"] = res.tau[:, 1].astype(float)
    per["Coll_den"] = res.tau[:, 0].astype(float)
    nu = 1.0 / float(res.k[0, 0])
    sums = OS.per_replicate_sums(res, nu=nu)
    per["onestep_s_u2"] = sums["s_u2"]
    per["onestep_s_risk"] = sums["s_risk"]
    per["onestep_n_cyc"] = sums["n_cyc"]
    scal = {"nu": nu, "rho_mean": float(res.post(res.rho).mean()),
            "rho_p05": float(np.quantile(res.post(res.rho), 0.05)),
            "rho_p95": float(np.quantile(res.post(res.rho), 0.95)),
            "tau1": float(res.tau[:, 0].mean()), "tau2": float(res.tau[:, 1].mean()),
            "tau_by_cycle": res.tau.mean(axis=0)[:20].round(3).tolist()}
    return per, scal


def _delay_block(policy, det, m, family, shift, e0=0.0, m0=5, tag="oc"):
    out, _ = run_delay(policy=policy, detector=det, m=m, family=family,
                       n_rep=N_D, shift=shift, shift_cycle=SHIFT_CYCLE, e0=e0,
                       m0=m0, cell_tag=tag, pair_tag=PAIR)
    return np.asarray(out["delay"], float)


def run_cell(det, m, k, family, rho_tune, rho_adj, shifts, cb,
             e0=0.0, m0=5, tag="ic", reduced=False):
    pol = arms(det, m, k, rho_tune, rho_adj, reduced=reduced)
    per, scal, delays = {}, {}, {}
    for pid, p in pol.items():
        per[pid], scal[pid] = _ic_block(p, det, m, family, cb, e0=e0, m0=m0, tag=tag)
        for s in shifts:
            delays[f"{pid}|{s}"] = _delay_block(p, det, m, family, s,
                                                e0=e0, m0=m0, tag=tag)
    return pol, per, scal, delays


def _save(tag, per, scal, delays, meta):
    np.savez_compressed(RESULTS / f"p6r_perrep_{tag}.npz",
                        **{f"{pid}|{mt}": arr for pid, d in per.items()
                           for mt, arr in d.items()},
                        **{f"DELAY|{kk}": vv for kk, vv in delays.items()})
    (RESULTS / f"p6r_scalars_{tag}.json").write_text(
        json.dumps({"meta": meta, "scalars": scal}, indent=1))


def main(family="eval"):
    anchor = _require_anchor()
    t0 = time.time()
    RESULTS.mkdir(exist_ok=True)
    sel = json.loads((PRECOMMIT / "baseline_selection.json").read_text())
    corr = json.loads((P.P6 / "results" / "correspondence.json").read_text())
    rho_adj = float(sel["adjudication_control_rho"])
    manifest = {"family": family, "precommit_anchor": anchor,
                "selected_rho_tune": {k: v["rho_selected"]
                                      for k, v in sel["cells"].items()},
                "adjudication_control_rho": rho_adj,
                "n_rep_ic": N_IC, "n_cycles_ic": N_CYC, "burn_in": BURN,
                "n_rep_delay": N_D, "shift_cycle": SHIFT_CYCLE, "cells": []}

    def cb_for(det):
        return {b: corr["c_beta"][det][b]["c"] for b in BETAS}

    det0, m0_, k0, sh0 = PRIMARY
    if family == "replay":
        plan = [("P_replay", det0, m0_, k0, (sh0,), 0.0, 5, False)]
    else:
        plan = [("P", det0, m0_, k0, (sh0,) + RC3_SHIFTS, 0.0, 5, False)]
        plan += [(f"RC1_{d}_m{m}", d, m, m, (1.0,), 0.0, 5, True) for d, m in RC1]
        plan += [(f"RC2_{d}_m{m}", d, m, m, (1.0,), 0.0, 5, True) for d, m in RC2]
        plan += [(f"RC4_m0{mm}", det0, m0_, k0, (1.0,), None, mm, True)
                 for mm in RC4_M0]

    for tag, det, m, k, shifts, e0, m0v, reduced in plan:
        rho_t = float(sel["cells"][f"{det}_m{m}"]["rho_selected"])
        pol, per, scal, delays = run_cell(
            det, m, k, family, rho_t, rho_adj, shifts, cb_for(det),
            e0=e0, m0=m0v, tag=tag, reduced=reduced)
        _save(f"{family}_{tag}", per, scal, delays,
              {"tag": tag, "detector": det, "m": m, "k": k, "family": family,
               "shifts": list(shifts), "e0": e0, "m0": m0v,
               "rho_tune": rho_t, "rho_adj": rho_adj,
               "arms": {pid: {"name": p.name, "class": p.policy_class}
                        for pid, p in pol.items()}})
        manifest["cells"].append({"tag": tag, "detector": det, "m": m, "k": k,
                                  "shifts": list(shifts), "e0": e0, "m0": m0v,
                                  "rho_tune": rho_t})
        print(f"{tag} done ({time.time()-t0:.0f}s)", flush=True)

    manifest["seconds"] = time.time() - t0
    (RESULTS / f"p6r_confirm_manifest_{family}.json").write_text(
        json.dumps(manifest, indent=1))
    print(f"total {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "eval")
