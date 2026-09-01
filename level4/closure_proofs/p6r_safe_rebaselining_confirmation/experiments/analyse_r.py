"""Apply the REPAIRED statistical procedure to the confirmation artifacts.

Reads only ``results/p6r_perrep_*.npz`` and ``results/p6r_scalars_*.json``.
Runs no simulation.  Every interval it emits is a 10,000-resample BCa interval
with a normal interval beside it, every ratio is bootstrapped as a ratio, every
declared family carries BH-adjusted p-values, and every tail estimate is gated
on the 200-event floor.

    python experiments/analyse_r.py [eval|replay]
"""
from __future__ import annotations

import json
import sys
import time

import numpy as np

import _p6r_paths as P                                             # noqa: F401
from _p6r_paths import PRECOMMIT, RESULTS

from rebaseguard_p6r import onestep as OS                          # noqa: E402
from rebaseguard_p6r import stats_r as ST                          # noqa: E402
from rebaseguard_p6r.costs import (ACQUISITION, PROPORTIONAL,      # noqa: E402
                                   QUADRATIC, COST_LABELS)

MATERIALITY = 0.10

#: metric -> how its paired relative effect is formed
MEANS = ["Arl0", "Fap100", "Rms", "Mad", "Q95e", "Tail0.2", "Tail0.5", "Tail1.0",
         "OutCal0.75", "OutCal0.5", "OutCal0.25", "OutCal0.1",
         ACQUISITION, PROPORTIONAL, QUADRATIC,
         "Wbar_mean_algebraic_reuse_weight"]
#: BH family F1 at the primary cell
F1_METRICS = ["Arl0", "Fap100", "Rms", "Mad", "Q95e", "Tail1.0", "OutCal0.25",
              "Dmean", "Dmed", "Dq95", "Dtail50", "Rdelta", "Coll", "onestep_G"]


def _load(family, tag):
    z = np.load(RESULTS / f"p6r_perrep_{family}_{tag}.npz")
    s = json.loads((RESULTS / f"p6r_scalars_{family}_{tag}.json").read_text())
    return z, s


def _arm_ids(z):
    return sorted({k.split("|")[0] for k in z.files if not k.startswith("DELAY|")})


def _delay(z, arm, shift):
    return np.asarray(z[f"DELAY|{arm}|{shift}"], float)


def compare(z, method, control, shift, *, seed=0, tail_thresholds=(50, 100)):
    """Every declared effect for one (method, control) pair at one shift."""
    eff = {}
    for i, mname in enumerate(MEANS):
        key_m, key_c = f"{method}|{mname}", f"{control}|{mname}"
        if key_m not in z.files:
            continue
        eff[mname] = ST.paired_ratio_of_means(
            z[key_m], z[key_c], metric=mname, materiality=MATERIALITY,
            seed=seed + i)

    dm, dc = _delay(z, method, shift), _delay(z, control, shift)
    eff["Dmean"] = ST.paired_ratio_of_means(dm, dc, metric="Dmean",
                                            materiality=MATERIALITY, seed=seed + 90)
    eff["Dmed"] = ST.paired_ratio_of_quantiles(dm, dc, 0.5, metric="Dmed",
                                               materiality=MATERIALITY, seed=seed + 91)
    eff["Dq95"] = ST.paired_ratio_of_quantiles(dm, dc, 0.95, metric="Dq95",
                                               materiality=MATERIALITY, seed=seed + 92)
    for L in tail_thresholds:
        e = ST.paired_ratio_of_means((dm > L).astype(float), (dc > L).astype(float),
                                     metric=f"Dtail{L}", materiality=MATERIALITY,
                                     seed=seed + 93 + L)
        eff[f"Dtail{L}"] = ST.apply_tail_gate(e, int((dm > L).sum()),
                                              int((dc > L).sum()))

    eff["Coll"] = ST.paired_ratio_of_ratios(
        z[f"{method}|Coll_num"], z[f"{method}|Coll_den"],
        z[f"{control}|Coll_num"], z[f"{control}|Coll_den"],
        metric="Coll", materiality=MATERIALITY, seed=seed + 95)
    eff["Rdelta"] = ST.paired_ratio_across_blocks(
        dm, dc, z[f"{method}|Arl0"], z[f"{control}|Arl0"],
        metric="Rdelta", materiality=MATERIALITY, seed=seed + 96)
    return eff


def onestep_block(z, arm, nu, *, seed=0):
    sums = {"s_u2": z[f"{arm}|onestep_s_u2"], "s_risk": z[f"{arm}|onestep_s_risk"],
            "n_cyc": z[f"{arm}|onestep_n_cyc"], "nu": nu}
    out = OS.one_step_risk_gain(sums, seed=seed)
    out["curve"] = OS.constant_policy_risk_curve(
        sums, np.round(np.linspace(0.0, 0.6, 61), 3))
    return out


def _absolutes(z, s, arm, shifts):
    a = {m: float(np.mean(z[f"{arm}|{m}"])) for m in MEANS
         if f"{arm}|{m}" in z.files}
    a["Coll"] = float(z[f"{arm}|Coll_num"].mean() / z[f"{arm}|Coll_den"].mean())
    for sh in shifts:
        d = _delay(z, arm, sh)
        a[f"Dmean@{sh}"] = float(d.mean())
        a[f"Dmed@{sh}"] = float(np.median(d))
        a[f"Dq95@{sh}"] = float(np.quantile(d, 0.95))
        a[f"Dtail50@{sh}"] = float((d > 50).mean())
        a[f"Dtail100@{sh}"] = float((d > 100).mean())
        a[f"n_events_50@{sh}"] = int((d > 50).sum())
        a[f"n_events_100@{sh}"] = int((d > 100).sum())
        a[f"Rdelta@{sh}"] = float(d.mean() / a["Arl0"])
    a.update({k: v for k, v in s["scalars"][arm].items() if k != "tau_by_cycle"})
    a["tau_by_cycle_first20"] = s["scalars"][arm]["tau_by_cycle"]
    return a


def analyse(family="eval"):
    t0 = time.time()
    man = json.loads((RESULTS / f"p6r_confirm_manifest_{family}.json").read_text())
    sel = json.loads((PRECOMMIT / "baseline_selection.json").read_text())
    out = {"family": family, "materiality": MATERIALITY,
           "precommit_anchor": man["precommit_anchor"],
           "n_boot": ST.N_BOOT, "bh_q": ST.BH_Q,
           "tail_event_floor": ST.TAIL_EVENT_FLOOR,
           "selected_rho_tune": man["selected_rho_tune"],
           "cost_labels": COST_LABELS, "cells": {}}

    for cell in man["cells"]:
        tag = cell["tag"]
        z, s = _load(family, tag)
        arms = _arm_ids(z)
        method = "SAW_M"
        ctl_tune = next(a for a in arms if a.startswith("FIXED_TUNE"))
        ctl_adj = next((a for a in arms if a.startswith("FIXED_ADJ")), None)
        shifts = cell["shifts"]
        row = {"meta": cell, "arms": arms,
               "control_tune": ctl_tune, "control_adj": ctl_adj,
               "absolutes": {a: _absolutes(z, s, a, shifts) for a in arms},
               "comparisons": {}, "onestep": {}, "bh": {}}

        for sh in shifts:
            row["comparisons"][f"vs_FIXED_TUNE@{sh}"] = {
                k: v.to_dict() for k, v in
                compare(z, method, ctl_tune, sh, seed=1000).items()}
            if ctl_adj:
                row["comparisons"][f"vs_FIXED_ADJ@{sh}"] = {
                    k: v.to_dict() for k, v in
                    compare(z, method, ctl_adj, sh, seed=2000).items()}
            for ref in ("B3_full_reuse", "B0_fresh_only"):
                if ref in arms:
                    row["comparisons"][f"vs_{ref}@{sh}"] = {
                        k: v.to_dict() for k, v in
                        compare(z, method, ref, sh, seed=3000).items()}

        nu = float(s["scalars"][method]["nu"])
        row["onestep"]["on_SAW_chain"] = onestep_block(z, method, nu, seed=11)
        row["onestep"]["on_FIXED_TUNE_chain"] = onestep_block(z, ctl_tune, nu, seed=12)

        # --- BH family F1, primary cell only ---------------------------------
        if tag in ("P", "P_replay"):
            eff = {k: ST.Effect(**v) for k, v in
                   row["comparisons"][f"vs_FIXED_TUNE@{cell['shifts'][0]}"].items()}
            g = row["onestep"]["on_SAW_chain"]
            eff["onestep_G"] = ST.Effect(
                metric="onestep_G", statistic="cluster_bootstrap_gain",
                rel=g["G"], bca_lo=g["bca_lo"], bca_hi=g["bca_hi"],
                normal_lo=g["normal_lo"], normal_hi=g["normal_hi"],
                boot_sd=g["boot_sd"],
                p_value=(1.0 / g["n_boot"] if g["resolved"] else 1.0),
                n_pairs=g["n_clusters"], n_boot=g["n_boot"], z0=g["z0"],
                accel=g["accel"], pair_corr=float("nan"),
                verdict=(ST.PRACTICALLY_MATERIAL if g["resolved"] and abs(g["G"]) >= MATERIALITY
                         else ST.STATISTICALLY_RESOLVED if g["resolved"]
                         else ST.INCONCLUSIVE))
            row["comparisons"][f"vs_FIXED_TUNE@{cell['shifts'][0]}"]["onestep_G"] = \
                eff["onestep_G"].to_dict()
            row["bh"]["F1_primary_cell_metrics"] = ST.bh_family(
                {k: eff[k] for k in F1_METRICS if k in eff})
            if len(cell["shifts"]) > 1:
                f3 = {}
                for sh in cell["shifts"][1:]:
                    d = row["comparisons"][f"vs_FIXED_TUNE@{sh}"]
                    f3[f"Dtail100@{sh}"] = ST.Effect(**d["Dtail100"])
                    f3[f"Dq95@{sh}"] = ST.Effect(**d["Dq95"])
                row["bh"]["F3_delta_scope"] = ST.bh_family(f3)
        out["cells"][tag] = row
        print(f"analysed {tag} ({time.time()-t0:.0f}s)", flush=True)

    # --- BH family F2, the replication family ------------------------------
    rep = {}
    for tag, row in out["cells"].items():
        if tag == "P" or tag.startswith("RC1") or tag.startswith("RC2"):
            d = row["comparisons"]["vs_FIXED_TUNE@1.0"]
            rep[tag] = ST.Effect(**d["Dtail100"])
    if rep:
        out["bh_F2_replication"] = ST.bh_family(rep)
    # --- BH family F4, the finite-reference family -------------------------
    fin = {t: ST.Effect(**r["comparisons"]["vs_FIXED_TUNE@1.0"]["Dtail100"])
           for t, r in out["cells"].items() if t.startswith("RC4")}
    if fin:
        out["bh_F4_finite_reference"] = ST.bh_family(fin)

    (RESULTS / f"p6r_analysis_{family}.json").write_text(json.dumps(out, indent=1))
    print(f"wrote p6r_analysis_{family}.json ({time.time()-t0:.0f}s)")
    return out


if __name__ == "__main__":
    analyse(sys.argv[1] if len(sys.argv) > 1 else "eval")
