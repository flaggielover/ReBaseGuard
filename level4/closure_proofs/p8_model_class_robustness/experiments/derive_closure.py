"""Compute every preregistered P8 gate from the stored result artifacts.

Reads only ``results/*.json``; runs no simulation.  Writes
``results/closure_decision.json`` and the per-gate evidence files.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE / "src"))
sys.path.insert(0, str(HERE / "experiments"))
from rebaseguard_p8.analysis import (                               # noqa: E402
    Z95, cochran_q, combined_z, p7_boundary_rate_uncertainty,
    p7_boundary_rates, spread)
from rebaseguard_p8.config import (                                 # noqa: E402
    DETECTORS, FAMILIES, MOMENT_MARGINAL, RESULTS, p3_boundaries,
    p4_correspondence, stage_d_cusum_thresholds, stage_d_target_arl0)

ELIGIBLE = tuple(f for f in FAMILIES if f not in MOMENT_MARGINAL)
LAW_M = (2, 3, 5)
EXTRAP_M = (10, 20)


def load(name):
    p = RESULTS / name
    return json.loads(p.read_text()) if p.exists() else None


def matrix_index(mat):
    return {(c["detector"], c["family"]): c for c in mat["cells"]}


# --------------------------------------------------------------- G1 ----------
def gate_G1(mat) -> dict:
    idx = matrix_index(mat)
    p3 = p3_boundaries()
    rows_a = []
    for d in DETECTORS:
        for m in (1, 2, 3, 5):
            c = idx.get((d, "gaussian"))
            if c is None:
                continue
            r = c["per_m"][str(m)]
            ref = p3[(d, m)]
            z = combined_z(r["gamma_A"], r["gamma_A_se"],
                           ref["gamma_tilde"], ref["gamma_tilde_se"])
            rows_a.append({"detector": d, "m": m, "p8": r["gamma_A"],
                           "p8_se": r["gamma_A_se"], "p3": ref["gamma_tilde"],
                           "p3_se": ref["gamma_tilde_se"], "z": z,
                           "relative": r["gamma_A"] / ref["gamma_tilde"] - 1.0,
                           "pass": bool(abs(z) <= 3.0)})
    p4 = p4_correspondence()
    rows_b = []
    for f in FAMILIES:
        c = idx.get(("cusum", f))
        if c is None:
            continue
        r = c["per_m"]["1"]
        ref = p4[f]
        z = combined_z(r["gamma_A"], r["gamma_A_se"], ref["gamma_f"],
                       ref["gamma_f_se"])
        rows_b.append({"family": f, "p8": r["gamma_A"], "p8_se": r["gamma_A_se"],
                       "p4": ref["gamma_f"], "p4_se": ref["gamma_f_se"], "z": z,
                       "relative": r["gamma_A"] / ref["gamma_f"] - 1.0,
                       "moment_marginal": f in MOMENT_MARGINAL,
                       "pass": bool(abs(z) <= 3.0)})
    target = stage_d_target_arl0()
    thr = stage_d_cusum_thresholds()
    rows_c = []
    for f in FAMILIES:
        c = idx.get(("cusum", f))
        if c is None:
            continue
        rel = abs(c["arl0"] - target) / target
        rows_c.append({"family": f, "threshold": c["threshold"],
                       "threshold_matches_stage_d": c["threshold"] == thr[f],
                       "arl0": c["arl0"], "arl0_se": c["arl0_se"],
                       "target": target, "relative_error": rel,
                       "pass": bool(rel <= 0.01)})
    reg = load("family_regularity.json")
    return {
        "G1a": {"rows": rows_a, "n_pass": sum(r["pass"] for r in rows_a),
                "n": len(rows_a),
                "pass": bool(sum(r["pass"] for r in rows_a) >= 7
                             and len(rows_a) == 8)},
        "G1b": {"rows": rows_b, "n_pass": sum(r["pass"] for r in rows_b),
                "n": len(rows_b),
                "pass": bool(sum(r["pass"] for r in rows_b) >= 5
                             and len(rows_b) == 6)},
        "G1c": {"rows": rows_c, "pass": bool(rows_c and all(r["pass"]
                                                            for r in rows_c))},
        "G1d": {"pass": bool(reg["gates"]["G1d_pass"]),
                "evidence": reg["gates"]},
        "G1e": {"pass": bool(reg["gates"]["G1e_pass"]),
                "evidence": {k: v for k, v in reg["gates"].items()
                             if k.startswith("G1e")}},
    }


# --------------------------------------------------------------- G2 ----------
def gate_G2() -> dict:
    cal = load("sr_calibration.json")
    if cal is None:
        return {"pass": False, "reason": "sr_calibration.json missing"}
    return {"pass": bool(cal["gates"]["G2_pass"]), "evidence": cal["gates"],
            "rows": [{k: r[k] for k in ("family", "threshold", "label",
                                        "verification_arl0",
                                        "verification_se",
                                        "verification_relative_error",
                                        "n_iterations")}
                     for r in cal["rows"]]}


# --------------------------------------------------------------- G3 ----------
def gate_G3(mat) -> dict:
    rows = []
    for c in mat["cells"]:
        for m in (1, 2, 3, 5):
            r = c["per_m"][str(m)]
            rows.append({"detector": c["detector"], "family": c["family"],
                         "m": m, "gamma_A": r["gamma_A"],
                         "gamma_A_lower95": r["gamma_A_ci95"][0],
                         "regime": r["regime"], "rho_c": r["rho_c"],
                         "rho_c_interval": r["rho_c_interval"],
                         "exceeds_2": r["lower_bound_exceeds_2"],
                         "moment_marginal": c["moment_marginal"]})
    elig = [r for r in rows if not r["moment_marginal"]]
    marg = [r for r in rows if r["moment_marginal"]]
    return {"rows": rows, "n_eligible": len(elig),
            "n_eligible_pass": sum(r["exceeds_2"] for r in elig),
            "moment_marginal_rows_reported_not_counted": len(marg),
            "moment_marginal_n_exceeds_2": sum(r["exceeds_2"] for r in marg),
            "pass": bool(len(elig) == 40 and all(r["exceeds_2"] for r in elig))}


# --------------------------------------------------------------- G4 ----------
def gate_G4(mat) -> dict:
    idx = matrix_index(mat)
    out = {"per_m": {}, "detector_invariance": {}, "distribution_invariance": {},
           "extrapolation": {}}
    for m in LAW_M + EXTRAP_M:
        entries = []
        for d in DETECTORS:
            for f in ELIGIBLE:
                c = idx.get((d, f))
                if c is None:
                    continue
                r = c["per_m"][str(m)]
                entries.append({"detector": d, "family": f, "K": r["K"],
                                "K_se": r["K_se"], "K_ci95": r["K_ci95"]})
        if not entries:
            continue
        ks = np.array([e["K"] for e in entries])
        ses = np.array([e["K_se"] for e in entries])
        rec = {"m": m, "n_cells": len(entries), "entries": entries,
               "mean_K": float(ks.mean()), "min_K": float(ks.min()),
               "max_K": float(ks.max()), "spread": spread(ks),
               "homogeneity_DESCRIPTIVE_ONLY": cochran_q(ks, ses)}
        if m in LAW_M:
            rec["threshold"] = 0.10
            rec["pass"] = bool(rec["spread"] <= 0.10 and len(entries) == 10)
            out["per_m"][str(m)] = rec
        else:
            out["extrapolation"][str(m)] = rec
    # G4-D: detector invariance
    dets = []
    for f in ELIGIBLE:
        for m in LAW_M:
            a, b = idx.get(("cusum", f)), idx.get(("sr", f))
            if a is None or b is None:
                continue
            ka, kb = a["per_m"][str(m)]["K"], b["per_m"][str(m)]["K"]
            rel = ka / kb - 1.0
            dets.append({"family": f, "m": m, "K_cusum": ka, "K_sr": kb,
                         "relative_difference": rel,
                         "pass": bool(abs(rel) <= 0.03)})
    out["detector_invariance"] = {
        "rows": dets, "max_abs_relative": max((abs(r["relative_difference"])
                                               for r in dets), default=None),
        "pass": bool(dets and all(r["pass"] for r in dets) and len(dets) == 15)}
    # G4-F: distribution invariance, within each detector
    fam = {}
    for d in DETECTORS:
        per_m = {}
        for m in LAW_M:
            ks = [idx[(d, f)]["per_m"][str(m)]["K"] for f in ELIGIBLE
                  if (d, f) in idx]
            if len(ks) != 5:
                continue
            per_m[str(m)] = {"K": ks, "spread": spread(np.array(ks)),
                             "pass": bool(spread(np.array(ks)) <= 0.10)}
        fam[d] = per_m
    out["distribution_invariance"] = {
        "per_detector": fam,
        "pass": bool(all(len(v) == 3 and all(x["pass"] for x in v.values())
                         for v in fam.values()) and len(fam) == 2)}
    out["pass"] = bool(out["per_m"] and len(out["per_m"]) == 3
                       and all(v["pass"] for v in out["per_m"].values()))
    return out


# --------------------------------------------------------------- G5/G6 ------
def gate_G5_G6(tag: str = "E1") -> dict:
    from aggregate_gamma import load_cell, _bm
    rows = []
    for d in DETECTORS:
        for f in FAMILIES:
            cell = load_cell(d, f, tag)
            if cell is None:
                continue
            nb = cell["n_batches"]
            lag = np.array([[b["gamma_lag"][r] for r in range(cell["lag_depth"])]
                            for b in cell["batches"]])
            for m in cell["m_grid"]:
                gA = _bm(cell, ("gamma_A", str(m)))
                gB = _bm(cell, ("gamma_B", str(m)))
                Rm = _bm(cell, ("R_m", str(m)))
                res = gA - lag[:, :m].mean(axis=1) - Rm
                se = float(res.std(ddof=1) / np.sqrt(nb))
                mu = float(res.mean())
                conv = float(np.max(np.abs((gA - gB) - Rm)))
                rows.append({"detector": d, "family": f, "m": int(m),
                             "decomposition_residual": mu,
                             "decomposition_residual_se": se,
                             "decomposition_pass": bool(abs(mu) <= 4.0 * se
                                                        or abs(mu) < 1e-12),
                             "conventionA_minus_B_minus_Rm_max_abs": conv,
                             "convention_pass": bool(conv <= 1e-12),
                             "p_tau_lt_m": float(
                                 _bm(cell, ("p_tau_lt_m", str(m))).mean())})
    return {
        "G5": {"rows": rows, "n": len(rows),
               "n_pass": sum(r["decomposition_pass"] for r in rows),
               "max_abs_residual": max((abs(r["decomposition_residual"])
                                        for r in rows), default=None),
               "pass": bool(rows and all(r["decomposition_pass"] for r in rows))},
        "G6": {"n": len(rows),
               "max_abs_identity_error": max(
                   (r["conventionA_minus_B_minus_Rm_max_abs"] for r in rows),
                   default=None),
               "p_tau_lt_m_reported": bool(rows and
                                           all("p_tau_lt_m" in r for r in rows)),
               "pass": bool(rows and all(r["convention_pass"] for r in rows))},
    }


# --------------------------------------------------------------- G7/G8/G9 ---
P7_LADDER = (0.25, 0.5, 0.8, 1.0, 1.25, 1.5, 2.0, 4.0)
P7_METRICS = ("arl", "ref_mse", "fap100", "e_acf1")


def _chain(detector, family, tag="E3"):
    p = RESULTS / "chain" / f"{tag}_{detector}_{family}.json"
    return json.loads(p.read_text()) if p.exists() else None


def gate_G7(tag="E3") -> dict:
    per_family = {}
    for f in FAMILIES:
        subs, per_metric = {}, {mname: 0 for mname in P7_METRICS}
        n_sub = 0
        for d in DETECTORS:
            c = _chain(d, f, tag)
            if c is None:
                continue
            for m in (1, 5):
                rung = []
                for mult in P7_LADDER:
                    hit = [r for r in c["rows"] if r["m"] == m
                           and r["rho_over_rhoc"] is not None
                           and abs(r["rho_over_rhoc"] - mult) < 1e-9]
                    if hit:
                        rung.append((mult, hit[0]))
                # P7's ladder is "clipped to [0,1]" by its own design.  Some
                # P8 cells have a larger rho_c, so the 4x rung leaves the
                # admissible domain and is absent.  The criterion is applied to
                # the rungs that exist, provided both boundary brackets
                # (0.8-1.0 and 1.0-1.25) are present and at least 5 rungs
                # remain.  Recorded as a declared adaptation, not a silent one.
                if len(rung) < 5 or not all(
                        any(abs(x - t) < 1e-9 for x, _ in rung)
                        for t in (0.8, 1.0, 1.25)):
                    continue
                n_sub += 1
                info = {}
                for mname in P7_METRICS:
                    vals = [r[mname] for _, r in rung]
                    info[mname] = p7_boundary_rates([x for x, _ in rung], vals,
                                                    mname)
                    per_metric[mname] += int(info[mname]["peaks_at_boundary"])
                    # DESCRIPTIVE companion: P7's criterion is a bare max with
                    # no uncertainty margin.  Report, for EVERY metric that
                    # carries a replicate-level SE (peaking or not, so the test
                    # family has a fixed denominator), how many standard errors
                    # the boundary rate exceeds the best rate elsewhere by.
                    se_key = mname + "_se"
                    if se_key in rung[0][1]:
                        info[mname]["uncertainty_DESCRIPTIVE_ONLY"] = \
                            p7_boundary_rate_uncertainty(
                                [x for x, _ in rung], vals,
                                [r[se_key] for _, r in rung])
                info["_n_rungs"] = len(rung)
                info["_rungs"] = [x for x, _ in rung]
                subs[f"{d}_m{m}"] = info
        met = bool(n_sub and any(v >= n_sub / 2 for v in per_metric.values()))
        resolved = []
        for sub, info in subs.items():
            for mname, i in info.items():
                if not isinstance(i, dict):
                    continue
                u = i.get("uncertainty_DESCRIPTIVE_ONLY")
                if u and u["resolved_at_2se"]:
                    resolved.append({"sub_family": sub, "metric": mname, **u})
        per_family[f] = {
            "n_sub_families": n_sub,
            "families_peaking_at_boundary_per_metric": per_metric,
            "criterion_met": met,
            "peaks_resolved_at_2se_DESCRIPTIVE_ONLY": resolved,
            "n_peaks_resolved_at_2se": len(resolved),
            "verdict": ("OPERATIONAL_BOUNDARY" if met
                        else "LOCAL-MATHEMATICAL, NOT OPERATIONAL"),
            "reproduces_P7_verdict": bool(not met),
            "sub_families": subs}
    n_rep = sum(v["reproduces_P7_verdict"] for v in per_family.values())
    # BH-FDR over the whole family of one-sided boundary tests that carry a
    # replicate-level SE.  Preregistered: secondary metric families use BH at
    # q = 0.10 (EXPERIMENT_PROTOCOL.md section 8).  DESCRIPTIVE: gate G7 is
    # P7's count criterion and is unchanged by this.
    from scipy import stats as _st
    tests = []
    for f, v in per_family.items():
        for sub, info in v["sub_families"].items():
            for mname, i in info.items():
                if not isinstance(i, dict):
                    continue
                u = i.get("uncertainty_DESCRIPTIVE_ONLY")
                if u and u["difference_in_se"] is not None:
                    tests.append({"family": f, "sub_family": sub,
                                  "metric": mname,
                                  "difference_in_se": u["difference_in_se"],
                                  "p_one_sided": float(
                                      _st.norm.sf(u["difference_in_se"]))})
    from rebaseguard_p8.analysis import bh_fdr as _bh
    if tests:
        rej = _bh([t_["p_one_sided"] for t_ in tests], 0.10)
        for t_, r in zip(tests, rej):
            t_["bh_reject_q010"] = bool(r)
    survivors = [t_ for t_ in tests if t_.get("bh_reject_q010")]
    return {"criterion": ("P7 EXPERIMENT_DESIGN section 8 / "
                          "p7/experiments/make_report.py::boundary_verdict, "
                          "applied verbatim per innovation family"),
            "declared_adaptation": ("P7's ladder is clipped to rho in [0,1]. In "
                                    "cells whose rho_c is large enough that "
                                    "4*rho_c leaves the admissible domain, the "
                                    "criterion is applied to the rungs that "
                                    "exist (>=5, both boundary brackets "
                                    "present). The rungs used are recorded per "
                                    "sub-family."),
            "ladder": list(P7_LADDER), "metrics": list(P7_METRICS),
            "per_family": per_family, "n_families": len(per_family),
            "uncertainty_aware_companion_DESCRIPTIVE_ONLY": {
                "note": ("P7's criterion is a bare max over brackets with no "
                         "uncertainty margin, so at 4 sub-families per family it "
                         "can flip on Monte Carlo noise. This companion tests, "
                         "one-sided, whether the boundary rate really exceeds the "
                         "best rate elsewhere, over every (family, sub-family, "
                         "metric) with a replicate-level SE, with BH-FDR at "
                         "q = 0.10 across the whole family of tests. It does NOT "
                         "change gate G7."),
                "n_tests": len(tests),
                "survivors_after_bh": survivors,
                "n_survivors_after_bh": len(survivors),
                "tests": tests},
            "n_reproducing_P7_verdict": n_rep,
            "pass": bool(len(per_family) == 6 and n_rep >= 5)}


def gate_G8(mat, tag="E3") -> dict:
    idx = matrix_index(mat)
    rows = []
    for d in DETECTORS:
        for f in FAMILIES:
            c = _chain(d, f, tag)
            cm = idx.get((d, f))
            if c is None or cm is None:
                continue
            nominal = cm["arl0"]
            for m in (1, 5):
                hit = [r for r in c["rows"] if r["m"] == m
                       and abs(r["rho"] - 1.0) < 1e-12]
                base = [r for r in c["rows"] if r["m"] == m
                        and abs(r["rho"]) < 1e-12]
                if not hit or not base:
                    continue
                frac = hit[0]["arl"] / nominal
                rows.append({"detector": d, "family": f, "m": m,
                             "nominal_A_f0": nominal,
                             "arl_rho1": hit[0]["arl"],
                             "arl_rho1_se": hit[0]["arl_se"],
                             "arl_rho0_fresh_control": base[0]["arl"],
                             "fraction_of_nominal": frac,
                             "reuse_attributable_relative":
                                 hit[0]["arl"] / base[0]["arl"] - 1.0,
                             "pass": bool(frac < 0.50)})
    return {"rows": rows, "n": len(rows),
            "n_pass": sum(r["pass"] for r in rows),
            "pass": bool(len(rows) == 24 and all(r["pass"] for r in rows))}


def gate_G9(mat, tag="E3") -> dict:
    idx = matrix_index(mat)
    gam, ch = [], []
    for f in FAMILIES:
        a, b = idx.get(("cusum", f)), idx.get(("sr", f))
        if a and b:
            for m in (1, 2, 3, 5, 10, 20):
                ra, rb = a["per_m"][str(m)], b["per_m"][str(m)]
                r = ra["gamma_A"] / rb["gamma_A"]
                se = r * np.sqrt((ra["gamma_A_se"] / ra["gamma_A"]) ** 2
                                 + (rb["gamma_A_se"] / rb["gamma_A"]) ** 2)
                gam.append({"family": f, "m": m, "ratio_cusum_over_sr": float(r),
                            "se": float(se),
                            "ci95": [float(r - Z95 * se), float(r + Z95 * se)],
                            "consistent_with_1":
                                bool(abs(r - 1.0) <= Z95 * se)})
        ca, cb = _chain("cusum", f, tag), _chain("sr", f, tag)
        if ca and cb:
            for m in (1, 5):
                for rho in (0.0, 0.5, 1.0):
                    ha = [r for r in ca["rows"] if r["m"] == m
                          and abs(r["rho"] - rho) < 1e-12]
                    hb = [r for r in cb["rows"] if r["m"] == m
                          and abs(r["rho"] - rho) < 1e-12]
                    if ha and hb:
                        ch.append({"family": f, "m": m, "rho": rho,
                                   "arl_ratio_cusum_over_sr":
                                       ha[0]["arl"] / hb[0]["arl"],
                                   "ref_mse_ratio":
                                       ha[0]["ref_mse"] / hb[0]["ref_mse"]})
    n_cons = sum(r["consistent_with_1"] for r in gam)
    return {"gamma_ratios": gam, "chain_ratios": ch,
            "n_gamma_ratios": len(gam),
            "n_gamma_ratios_consistent_with_1": n_cons,
            "max_abs_gamma_ratio_deviation":
                max((abs(r["ratio_cusum_over_sr"] - 1.0) for r in gam),
                    default=None),
            "transfer_claim": ("NOT CLAIMED: the two frozen detectors are "
                               "compared and reported; no transfer to any "
                               "untested detector family is asserted"),
            "pass": bool(len(gam) == 36 and len(ch) == 36)}


# --------------------------------------------------------------- G10 --------
def gate_G10(mat_a, mat_b) -> dict:
    ia, ib = matrix_index(mat_a), matrix_index(mat_b)
    rows = []
    for key in ia:
        if key not in ib:
            continue
        for m in (1, 2, 3, 5, 10, 20):
            ra, rb = ia[key]["per_m"][str(m)], ib[key]["per_m"][str(m)]
            z = combined_z(ra["gamma_A"], ra["gamma_A_se"],
                           rb["gamma_A"], rb["gamma_A_se"])
            rows.append({"detector": key[0], "family": key[1], "m": m,
                         "E1": ra["gamma_A"], "E5": rb["gamma_A"], "z": z,
                         "relative": ra["gamma_A"] / rb["gamma_A"] - 1.0,
                         "moment_marginal": ia[key]["moment_marginal"],
                         "pass": bool(abs(z) <= 3.0)})
    elig = [r for r in rows if not r["moment_marginal"]]
    frac_all = sum(r["pass"] for r in rows) / len(rows) if rows else 0.0
    frac_el = sum(r["pass"] for r in elig) / len(elig) if elig else 0.0
    return {"rows": rows, "n": len(rows), "fraction_pass_all": frac_all,
            "fraction_pass_non_marginal": frac_el,
            "pass": bool(len(rows) == 72 and frac_all >= 0.90
                         and frac_el >= 0.95)}


# --------------------------------------------------------------- G11 --------
def _incontrol_arl(d, f, m, rho, tag="E3"):
    """The post-burn-in in-control chain ARL at the same cell and rho.

    This, not the drift run's own pre-change mean, is the correct control for
    the discrimination ratio: the drift run's cycles 0..19 include the
    ``e_0 = 0`` transient, whose first cycle starts from a perfect reference and
    biases the mean upward.
    """
    c = _chain(d, f, tag)
    if c is None:
        return None
    for r in c["rows"]:
        if r["m"] == m and abs(r["rho"] - rho) < 1e-12:
            return r["arl"]
    return None


def gate_G11(tag="E4") -> dict:
    rows, missing = [], []
    for d in DETECTORS:
        for f in FAMILIES:
            p = RESULTS / "drift" / f"{tag}_{d}_{f}.json"
            if not p.exists():
                missing.append(f"{d}:{f}")
                continue
            c = json.loads(p.read_text())
            for r in c["rows"]:
                rows.append({"detector": d, "family": f, **{
                    k: r[k] for k in ("m", "rho", "pattern", "size", "slope")},
                    "delay_mean": r["delay"]["mean"],
                    "delay_se": r["delay"]["se"],
                    "q50": r["delay"]["q50"], "q95": r["delay"]["q95"],
                    "p_gt_100": r["delay"]["p_gt_100"],
                    "n_tail_events": r["delay"]["n_tail_events"],
                    "tail_label": r["delay"]["tail_label"],
                    "pre_change_arl_incl_transient": r["pre_change_arl"],
                    "incontrol_arl_E3": _incontrol_arl(d, f, r["m"], r["rho"]),
                    "R_delta": (r["delay"]["mean"]
                                / _incontrol_arl(d, f, r["m"], r["rho"]))
                    if _incontrol_arl(d, f, r["m"], r["rho"]) else None})
    expected = 2 * 6 * 2 * 2 * 6
    return {"rows": rows, "n": len(rows), "expected": expected,
            "missing_cells": missing,
            "n_insufficient_tail":
                sum(r["tail_label"] == "INSUFFICIENT_TAIL_EVENTS" for r in rows),
            "pass": bool(not missing and len(rows) == expected)}


# --------------------------------------------------------------- G12-G15 ----
def gate_G12() -> dict:
    man = json.loads((RESULTS / "protected_tree_manifest_pre.json").read_text())
    import hashlib
    out = subprocess.run(["git", "ls-files", "-s"], cwd=ROOT,
                         capture_output=True, text=True).stdout
    rows = []
    for line in out.strip().split("\n"):
        meta, path = line.split("\t", 1)
        mode, blob, _ = meta.split()
        rows.append({"path": path, "blob": blob, "mode": mode})
    diffs = {}
    for name, rec in man["protected_trees"].items():
        sel = [r for r in rows if r["path"].startswith(rec["prefix"])]
        blob = "\n".join(f"{r['mode']} {r['blob']} {r['path']}"
                         for r in sorted(sel, key=lambda x: x["path"]))
        h = hashlib.sha256(blob.encode()).hexdigest()
        if h != rec["sha256"]:
            diffs[name] = {"expected": rec["sha256"], "actual": h,
                           "n_files_then": rec["n_files"], "n_files_now": len(sel)}
    dirty = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                           capture_output=True, text=True).stdout.strip()
    allowed = man["allowed_write_namespace"]
    outside = [l for l in dirty.split("\n") if l.strip()
               and allowed not in l and not l.strip().endswith("/")]
    return {"protected_tree_differences": diffs,
            "n_protected_trees": len(man["protected_trees"]),
            "worktree_entries_outside_p8": outside,
            "pass": bool(not diffs and not outside)}


def gate_G13() -> dict:
    r = subprocess.run(
        [sys.executable, "-m", "pytest", str(HERE / "tests" / "test_crn_identity.py"),
         "-q"], cwd=HERE, capture_output=True, text=True)
    return {"returncode": r.returncode, "tail": r.stdout.strip().split("\n")[-1],
            "pass": bool(r.returncode == 0)}


def gate_G14(mat) -> dict:
    """No hidden recalibration: thresholds are byte-identical to their source."""
    thr = stage_d_cusum_thresholds()
    cal = load("sr_calibration.json")
    sr_thr = {r["family"]: r["threshold"] for r in cal["rows"]} if cal else {}
    rows = []
    for c in mat["cells"]:
        if c["detector"] == "cusum":
            ok = float.hex(c["threshold"]) == float.hex(thr[c["family"]])
            src = "stage_d/results/d3_nongaussian.json"
        else:
            ok = (c["family"] in sr_thr
                  and float.hex(c["threshold"]) == float.hex(sr_thr[c["family"]]))
            src = "results/sr_calibration.json"
        rows.append({"detector": c["detector"], "family": c["family"],
                     "threshold_hex": float.hex(c["threshold"]),
                     "source": src, "provenance": c["threshold_provenance"],
                     "identical_to_source": bool(ok)})
    ch_rows = []
    for d in DETECTORS:
        for f in FAMILIES:
            for tag, sub in (("E3", "chain"), ("E4", "drift")):
                p = RESULTS / sub / f"{tag}_{d}_{f}.json"
                if p.exists():
                    c = json.loads(p.read_text())
                    ref = thr[f] if d == "cusum" else sr_thr.get(f)
                    ch_rows.append({"artifact": f"{sub}/{tag}_{d}_{f}",
                                    "identical_to_source":
                                        bool(ref is not None
                                             and float.hex(c["threshold"])
                                             == float.hex(ref))})
    return {"gamma_rows": rows, "chain_rows": ch_rows,
            "pass": bool(rows and all(r["identical_to_source"] for r in rows)
                         and all(r["identical_to_source"] for r in ch_rows))}


def gate_G15() -> dict:
    r = subprocess.run([sys.executable, "-m", "pytest", str(HERE / "tests"), "-q"],
                       cwd=HERE, capture_output=True, text=True)
    return {"returncode": r.returncode, "tail": r.stdout.strip().split("\n")[-1],
            "pass": bool(r.returncode == 0)}


# --------------------------------------------------------------- main -------
def main() -> None:
    mat = load("gamma_matrix_E1.json")
    mat5 = load("gamma_matrix_E5.json")
    g1 = gate_G1(mat)
    g56 = gate_G5_G6("E1")
    gates = {
        **{k: v for k, v in g1.items()},
        "G2": gate_G2(),
        "G3": gate_G3(mat),
        "G4": gate_G4(mat),
        "G5": g56["G5"],
        "G6": g56["G6"],
        "G7": gate_G7(),
        "G8": gate_G8(mat),
        "G9": gate_G9(mat),
        "G10": gate_G10(mat, mat5) if mat5 else {"pass": False,
                                                 "reason": "E5 missing"},
        "G11": gate_G11(),
        "G12": gate_G12(),
        "G13": gate_G13(),
        "G14": gate_G14(mat),
        "G15": gate_G15(),
    }
    flat = {"G1a": gates["G1a"]["pass"], "G1b": gates["G1b"]["pass"],
            "G1c": gates["G1c"]["pass"], "G1d": gates["G1d"]["pass"],
            "G1e": gates["G1e"]["pass"], "G2": gates["G2"]["pass"],
            "G3": gates["G3"]["pass"], "G4": gates["G4"]["pass"],
            "G4-D": gates["G4"]["detector_invariance"]["pass"],
            "G4-F": gates["G4"]["distribution_invariance"]["pass"],
            "G5": gates["G5"]["pass"], "G6": gates["G6"]["pass"],
            "G7": gates["G7"]["pass"], "G8": gates["G8"]["pass"],
            "G9": gates["G9"]["pass"], "G10": gates["G10"]["pass"],
            "G11": gates["G11"]["pass"], "G12": gates["G12"]["pass"],
            "G13": gates["G13"]["pass"], "G14": gates["G14"]["pass"],
            "G15": gates["G15"]["pass"]}
    spine = ("G1a", "G1b", "G1c", "G1d", "G1e", "G5", "G6", "G12", "G13",
             "G14", "G15")
    scientific = ("G2", "G3", "G4", "G4-D", "G4-F", "G7", "G8", "G9", "G10",
                  "G11")
    if all(flat.values()):
        verdict = "P8 = CLOSED_CANDIDATE"
    elif all(flat[k] for k in spine):
        verdict = "P8 = PARTIAL_CANDIDATE"
    else:
        verdict = "P8 = FAIL_CANDIDATE"
    out = {"schema": "rebaseguard.p8.closure-decision.v1",
           "gate_results": flat,
           "n_pass": sum(flat.values()), "n_gates": len(flat),
           "failed": [k for k, v in flat.items() if not v],
           "correctness_reproduction_integrity_spine": list(spine),
           "scientific_gates": list(scientific),
           "verdict": verdict,
           "verdict_authority": ("CANDIDATE ONLY. Not authoritative. Codex "
                                 "adjudicates independently."),
           "evidence": gates}
    (RESULTS / "closure_decision.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({"verdict": verdict, "gates": flat,
                      "failed": out["failed"]}, indent=1))


if __name__ == "__main__":
    main()
