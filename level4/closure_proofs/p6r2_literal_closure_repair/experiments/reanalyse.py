"""Regenerate the corrected derived analysis from FROZEN P6R raw arrays.

Consumes ``p6r_safe_rebaselining_confirmation/results/p6r_perrep_*.npz`` and
``p6r_scalars_*.json`` read-only.  Runs no simulation and touches no P6R file.

Corrections applied, and only these:
  G6A  the F3 family is built by the literal declared rule
  G6B  Rdelta uses the corrected two-block BCa acceleration
  G6C/G12  zero-denominator comparisons are first-class undefined AT SOURCE

Everything else -- estimand, seeds, resample count, BCa, normal intervals, ratio
resampling, the tail floor, BH q -- is inherited unchanged, so every defined
effect must reproduce P6R exactly.  ``regression_vs_p6r`` records that check.

    python experiments/reanalyse.py [eval|replay]
"""
from __future__ import annotations

import json
import sys
import time

import numpy as np

import _p6r2_paths as P                                              # noqa: F401
from _p6r2_paths import P6R, RESULTS

from rebaseguard_p6r import onestep as OS                            # noqa: E402
from rebaseguard_p6r2 import effects as EF                           # noqa: E402
from rebaseguard_p6r2 import families as FAM                         # noqa: E402
from rebaseguard_p6r2.undefined import (STATUS_UNDEFINED,            # noqa: E402
                                        assert_no_nonfinite,
                                        sanitise_for_strict_json)

MEANS = ["Arl0", "Fap100", "Rms", "Mad", "Q95e", "Tail0.2", "Tail0.5", "Tail1.0",
         "OutCal0.75", "OutCal0.5", "OutCal0.25", "OutCal0.1",
         "C_acq_fresh_acquisition_count",
         "C_prop_proportional_fresh_contribution",
         "C_quad_effective_squared_weight_contribution",
         "Wbar_mean_algebraic_reuse_weight"]
F1_METRICS = ["Arl0", "Fap100", "Rms", "Mad", "Q95e", "Tail1.0", "OutCal0.25",
              "Dmean", "Dmed", "Dq95", "Dtail50", "Rdelta", "Coll", "onestep_G"]
CELLS8 = ("P", "RC1_sr_m3", "RC2_cusum_m1", "RC2_cusum_m2", "RC2_cusum_m5",
          "RC2_sr_m1", "RC2_sr_m2", "RC2_sr_m5")


def _load(family, tag):
    z = np.load(P6R / "results" / f"p6r_perrep_{family}_{tag}.npz")
    s = json.loads((P6R / "results" / f"p6r_scalars_{family}_{tag}.json").read_text())
    return z, s


def _delay(z, arm, shift):
    return np.asarray(z[f"DELAY|{arm}|{shift}"], float)


def compare(z, method, control, shift, *, seed=0):
    """Every declared effect for one (method, control) pair at one shift."""
    out = {}
    for i, m in enumerate(MEANS):
        km, kc = f"{method}|{m}", f"{control}|{m}"
        if km not in z.files:
            continue
        out[m] = EF.ratio_of_means(z[km], z[kc], metric=m, seed=seed + i)

    dm, dc = _delay(z, method, shift), _delay(z, control, shift)
    out["Dmean"] = EF.ratio_of_means(dm, dc, metric="Dmean", seed=seed + 90)
    out["Dmed"] = EF.ratio_of_quantiles(dm, dc, 0.5, metric="Dmed", seed=seed + 91)
    out["Dq95"] = EF.ratio_of_quantiles(dm, dc, 0.95, metric="Dq95", seed=seed + 92)
    for L in (50, 100):
        r = EF.ratio_of_means((dm > L).astype(float), (dc > L).astype(float),
                              metric=f"Dtail{L}", seed=seed + 93 + L)
        out[f"Dtail{L}"] = EF.apply_tail_gate(r, int((dm > L).sum()),
                                              int((dc > L).sum()))
    out["Coll"] = EF.ratio_of_ratios(
        z[f"{method}|Coll_num"], z[f"{method}|Coll_den"],
        z[f"{control}|Coll_num"], z[f"{control}|Coll_den"],
        metric="Coll", seed=seed + 95)
    # G6B: corrected two-block acceleration
    out["Rdelta"] = EF.rdelta_two_block(dm, dc, z[f"{method}|Arl0"],
                                        z[f"{control}|Arl0"], seed=seed + 96)
    return out


def onestep_record(z, arm, nu, seed=11):
    g = OS.one_step_risk_gain(
        {"s_u2": z[f"{arm}|onestep_s_u2"], "s_risk": z[f"{arm}|onestep_s_risk"],
         "n_cyc": z[f"{arm}|onestep_n_cyc"], "nu": nu}, seed=seed)
    return {
        "metric": "onestep_G", "statistic": "cluster_bootstrap_gain",
        "status": "OK", "relative_effect": g["G"],
        "bca_interval": [g["bca_lo"], g["bca_hi"]],
        "normal_interval": [g["normal_lo"], g["normal_hi"]],
        "boot_sd": g["boot_sd"],
        "p_value": (1.0 / g["n_boot"] if g["resolved"] else 1.0),
        "p_value_kind": ("resolution indicator (1/B when the BCa interval "
                         "excludes zero), NOT a percentile bootstrap p-value"),
        "p_adjusted": None,
        "verdict": ("PRACTICALLY_MATERIAL" if g["resolved"] and abs(g["G"]) >= 0.10
                    else "STATISTICALLY_RESOLVED" if g["resolved"] else "INCONCLUSIVE"),
        "n_pairs": g["n_clusters"], "n_boot": g["n_boot"],
        "z0": g["z0"], "accel": g["accel"], "pair_corr": None,
        "tail_flag": None, "n_events_method": None, "n_events_control": None,
        "method_mean": g["R_adapt"], "control_mean": g["R_star"],
        "detail": g,
    }


def main(family="eval"):
    t0 = time.time()
    man = json.loads((P6R / "results"
                      / f"p6r_confirm_manifest_{family}.json").read_text())
    old = json.loads((P6R / "results" / f"p6r_analysis_{family}.json").read_text())
    out = {
        "campaign": "P6R2 literal closure repair",
        "nature": ("post-adjudication deterministic/statistical repair over "
                   "frozen P6R raw evidence; no simulation, no reselection, "
                   "no retuning, no sample-size increase"),
        "family": family, "materiality": EF.MATERIALITY,
        "n_boot": EF.N_BOOT, "bh_q": FAM.BH_Q,
        "tail_event_floor": EF.TAIL_EVENT_FLOOR,
        "source_p6r_head": "73ecad84620e71b68db60612a7001707a2cbd741",
        "precommit_anchor": man["precommit_anchor"],
        "selected_rho_tune": man["selected_rho_tune"],
        "corrections": {
            "G6A": "F3 built by the literal declared rule (families.py)",
            "G6B": "Rdelta uses the two-block BCa acceleration (twoblock.py)",
            "G6C_G12": ("zero-denominator comparisons are first-class undefined "
                        "at source; JSON null, verdict NO_CLAIM"),
        },
        "cells": {}, "undefined_ledger": [],
    }

    for cell in man["cells"]:
        tag = cell["tag"]
        z, s = _load(family, tag)
        arms = sorted({k.split("|")[0] for k in z.files
                       if not k.startswith("DELAY|")})
        ctl_tune = next(a for a in arms if a.startswith("FIXED_TUNE"))
        ctl_adj = next((a for a in arms if a.startswith("FIXED_ADJ")), None)
        row = {"meta": cell, "arms": arms, "control_tune": ctl_tune,
               "control_adj": ctl_adj, "comparisons": {}, "onestep": {}, "bh": {}}
        for sh in cell["shifts"]:
            blocks = [("vs_FIXED_TUNE", ctl_tune, 1000)]
            if ctl_adj:
                blocks.append(("vs_FIXED_ADJ", ctl_adj, 2000))
            for ref in ("B3_full_reuse", "B0_fresh_only"):
                if ref in arms:
                    blocks.append((f"vs_{ref}", ref, 3000))
            for name, ctl, seed in blocks:
                key = f"{name}@{sh}"
                row["comparisons"][key] = compare(z, "SAW_M", ctl, sh, seed=seed)
                for m, r in row["comparisons"][key].items():
                    if r["status"] == STATUS_UNDEFINED:
                        out["undefined_ledger"].append(
                            {"family": family, "cell": tag, "comparison": key,
                             "metric": m, "control_arm": ctl,
                             "status": r["status"], "verdict": r["verdict"],
                             "reason": r["undefined_reason"]})

        nu = float(s["scalars"]["SAW_M"]["nu"])
        row["onestep"]["on_SAW_chain"] = onestep_record(z, "SAW_M", nu, seed=11)
        row["onestep"]["on_FIXED_TUNE_chain"] = onestep_record(z, ctl_tune, nu, seed=12)

        if tag in ("P", "P_replay"):
            sh0 = cell["shifts"][0]
            blk = row["comparisons"][f"vs_FIXED_TUNE@{sh0}"]
            blk["onestep_G"] = row["onestep"]["on_SAW_chain"]
            row["bh"]["F1_primary_cell_metrics"] = FAM.bh_over_defined(
                {k: blk[k] for k in F1_METRICS if k in blk})
            # ---- G6A: the LITERAL F3 family --------------------------------
            if len(cell["shifts"]) > 1:
                ev = {}
                for sh in cell["shifts"][1:]:
                    d = row["comparisons"][f"vs_FIXED_TUNE@{sh}"]["Dtail100"]
                    ev[float(sh)] = (d["n_events_method"], d["n_events_control"])
                membership = FAM.f3_membership(ev)
                members, excluded_detail = {}, []
                for d, info in membership.items():
                    src = row["comparisons"][f"vs_FIXED_TUNE@{d}"]
                    members[info["included_key"]] = src[info["included_metric"]]
                    excluded_detail.extend(info["excluded"])
                bh = FAM.bh_over_defined(members)
                bh["membership_rule"] = ("primary metric Dtail100 per Delta; the "
                                         "declared fallback Dq95 ONLY when the "
                                         "primary is sub-floor")
                bh["membership_detail"] = {str(k): v for k, v in membership.items()}
                bh["excluded_detail"] = excluded_detail
                row["bh"]["F3_delta_scope_literal"] = bh
        out["cells"][tag] = row
        print(f"reanalysed {tag} ({time.time()-t0:.0f}s)", flush=True)

    rep = {t: out["cells"][t]["comparisons"]["vs_FIXED_TUNE@1.0"]["Dtail100"]
           for t in out["cells"] if t in CELLS8}
    if rep:
        out["bh_F2_replication"] = FAM.bh_over_defined(rep)
    fin = {t: r["comparisons"]["vs_FIXED_TUNE@1.0"]["Dtail100"]
           for t, r in out["cells"].items() if t.startswith("RC4")}
    if fin:
        out["bh_F4_finite_reference"] = FAM.bh_over_defined(fin)

    # write BH-adjusted p back into every record that received one
    for name, fam in list(out.get("bh_F2_replication", {}).items() if False else []):
        pass
    for tag, row in out["cells"].items():
        for fname, fam in row["bh"].items():
            for k, padj in fam.get("p_adjusted", {}).items():
                for blk in row["comparisons"].values():
                    if k in blk and blk[k].get("p_adjusted") is None:
                        blk[k]["p_adjusted"] = padj
                        break

    # ---- regression against P6R for DEFINED effects ------------------------
    same, diff = 0, []
    for tag, row in out["cells"].items():
        oldrow = old["cells"].get(tag, {})
        for blk, comps in row["comparisons"].items():
            oldblk = oldrow.get("comparisons", {}).get(blk, {})
            for m, r in comps.items():
                o = oldblk.get(m)
                if o is None or r["status"] == STATUS_UNDEFINED:
                    continue
                if m == "Rdelta":
                    continue                     # deliberately changed by G6B
                if abs(float(o["rel"]) - r["relative_effect"]) < 1e-12:
                    same += 1
                else:
                    diff.append({"cell": tag, "comparison": blk, "metric": m,
                                 "p6r": o["rel"], "p6r2": r["relative_effect"]})
    out["regression_vs_p6r"] = {
        "definition": ("every DEFINED effect other than Rdelta must reproduce "
                       "P6R bit-for-bit: same arrays, same seeds, same code path"),
        "n_identical": same, "n_different": len(diff), "differences": diff[:20]}

    out["undefined_summary"] = {
        "n_undefined": len(out["undefined_ledger"]),
        "controls_involved": sorted({r["control_arm"]
                                     for r in out["undefined_ledger"]}),
        "metrics_involved": sorted({r["metric"] for r in out["undefined_ledger"]}),
    }

    clean = sanitise_for_strict_json(out)
    assert_no_nonfinite(clean)
    txt = json.dumps(clean, indent=1, allow_nan=False)      # strict JSON
    (RESULTS / f"p6r2_analysis_{family}.json").write_text(txt)
    print(f"wrote p6r2_analysis_{family}.json  "
          f"({out['undefined_summary']['n_undefined']} undefined, "
          f"{same} defined effects identical to P6R, {len(diff)} differ) "
          f"[{time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "eval")
