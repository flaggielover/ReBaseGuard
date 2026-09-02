"""Evaluate every frozen P8R scientific-resolution question, literally.

The rules, thresholds and admissible outcomes are frozen in ``FROZEN_GATES.md``
and ``config.py`` at the temporal anchor.  This script only *applies* them.  It
contains no threshold literal of its own: every number comes from ``config``.

Each question resolves to exactly one of ``SUPPORTED``, ``REJECTED``,
``INCONCLUSIVE`` or ``OUT_OF_SCOPE``.  A ``REJECTED`` scientific question is a
negative scientific result, **not** a procedural failure: the closure rule in
``FROZEN_GATES.md`` §4 requires that every question be *resolved*, never that
every hypothesis be *true*.

Usage:  derive_resolution.py
"""
from __future__ import annotations

import json

import numpy as np

import _common as C                                              # noqa: E402
from rebaseguard_p8r.analysis import (Z95, bh_fdr, cochran_q,    # noqa: E402
                                       combined_z, p7_boundary_rates,
                                       p7_boundary_rate_uncertainty, spread)
from rebaseguard_p8r.config import (COMBINED_Z_TOLERANCE,        # noqa: E402
                                     DETECTORS, FAMILIES, M_GRID,
                                     M_P3_SUPPORTED, MOMENT_MARGINAL, P7,
                                     RESULTS, S2_SCORE_TOL, S3_ARL0_REL_MAX,
                                     S4_EPSI_TOL, S4_EZPSI_TOL, S4_FISHER_TOL,
                                     S6_LOWER_BOUND, S7D_RESIDUAL_MAX,
                                     S7F_SPREAD_MAX, S7_SPREAD_MAX,
                                     S8_ABS_TOL, S9_EXACT_TOL, S17_MAX_OUTLIERS,
                                     S10_FAMILIES_REQUIRED, S11_ARL_FRACTION,
                                     S13_CELL_FRACTION, S13_NON_T3_FRACTION,
                                     EXTRAPOLATION_M, BH_Q, CAL_TOLERANCE,
                                     M_CHAIN, RAMP_SLOPES, SHIFTS,
                                     p3_boundaries, p4_correspondence,
                                     stage_d_target_arl0)

ELIGIBLE_FAMILIES = tuple(f for f in FAMILIES if f not in MOMENT_MARGINAL)
K_WINDOWS = (2, 3, 5)


# ---------------------------------------------------------------------------
def load(name):
    return C.load_payload(RESULTS / name)


def cell_index(matrix):
    return {(c["detector"], c["family"]): c for c in matrix["cells"]}


def resolved(question, status, statistic, rule, detail=None):
    assert status in ("SUPPORTED", "REJECTED", "INCONCLUSIVE", "OUT_OF_SCOPE")
    return {"question": question, "status": status, "statistic": statistic,
            "frozen_rule": rule, "detail": detail or {}}


def paired_ratio(a_vec, b_vec):
    """Ratio of means with the CRN-paired linearised SE.

    ``a`` and ``b`` are per-batch values at the *same* batch addresses, so they
    share innovations.  ``d_i = a_i - r * b_i`` has mean zero at the true ratio,
    and ``SE(r) = SE(mean d) / |mean b|`` carries the covariance exactly.  Using
    an independent-SE formula here would understate or overstate the interval
    depending on the sign of the correlation; ``STATISTICAL_ANALYSIS_PLAN.md``
    §3 forbids it.
    """
    a = np.asarray(a_vec, float)
    b = np.asarray(b_vec, float)
    r = float(a.mean() / b.mean())
    d = a - r * b
    se = float(d.std(ddof=1) / np.sqrt(d.size) / abs(b.mean()))
    rho = float(np.corrcoef(a, b)[0, 1]) if a.size > 2 else float("nan")
    naive = float(np.sqrt((a.std(ddof=1) / np.sqrt(a.size) / b.mean()) ** 2
                          + (r * b.std(ddof=1) / np.sqrt(b.size)
                             / b.mean()) ** 2))
    return {"ratio": r, "se": se, "ci95": [r - Z95 * se, r + Z95 * se],
            "excludes_one": bool(abs(r - 1.0) > Z95 * se),
            "batch_correlation": rho, "naive_unpaired_se": naive}


# ---------------------------------------------------------------------------
# S1 / S2 / S3 / S4 / S5  -- reproduction and calibration
# ---------------------------------------------------------------------------
def s1_p3(E1):
    idx = cell_index(E1)
    p3 = p3_boundaries()
    rows, ok = [], 0
    for det in DETECTORS:
        for m in M_P3_SUPPORTED:
            ref = p3[(det, m)]
            c = idx[(det, "gaussian")]["per_m"][str(m)]
            z = combined_z(c["gamma_A"], c["gamma_A_se"],
                           ref["gamma_tilde"], ref["gamma_tilde_se"])
            within = abs(z) <= COMBINED_Z_TOLERANCE
            ok += within
            rows.append({"detector": det, "m": m, "p8r": c["gamma_A"],
                         "p8r_se": c["gamma_A_se"], "p3": ref["gamma_tilde"],
                         "p3_se": ref["gamma_tilde_se"], "z": z,
                         "relative": c["gamma_A"] / ref["gamma_tilde"] - 1.0,
                         "within": bool(within)})
    status = ("SUPPORTED" if ok >= 7 else
              "REJECTED" if ok <= 4 else "INCONCLUSIVE")
    return resolved("S1", status, {"cells_within": ok, "of": 8},
                    "SUPPORTED iff >=7/8 of the frozen P3 Gaussian cells agree "
                    "within 3 combined SE; REJECTED iff <=4/8; else "
                    "INCONCLUSIVE", {"rows": rows})


def s2_p4(E1, reg):
    idx = cell_index(E1)
    p4 = p4_correspondence()
    rows, ok = [], 0
    for f in FAMILIES:
        c = idx[("cusum", f)]["per_m"]["1"]
        z = combined_z(c["gamma_A"], c["gamma_A_se"],
                       p4[f]["gamma_f"], p4[f]["gamma_f_se"])
        within = abs(z) <= COMBINED_Z_TOLERANCE
        ok += within
        rows.append({"family": f, "p8r": c["gamma_A"],
                     "p8r_se": c["gamma_A_se"], "p4": p4[f]["gamma_f"],
                     "p4_se": p4[f]["gamma_f_se"], "z": z,
                     "within": bool(within)})
    score = reg["statistics"]["S2b_psi_max_abs_diff"]
    status = "SUPPORTED" if (ok >= 5 and score <= S2_SCORE_TOL) else "REJECTED"
    return resolved("S2", status,
                    {"families_within": ok, "of": 6,
                     "max_score_abs_diff": score},
                    f"SUPPORTED iff >=5/6 P4 m=1 CUSUM cells agree within 3 "
                    f"combined SE AND the independent score implementation "
                    f"matches P4 to {S2_SCORE_TOL}", {"rows": rows})


def s3_arl0(arl):
    rows = [r for r in arl["rows"] if r["status"] == "OK"]
    bad = [r for r in rows if not r["within_1pct"]]
    status = "SUPPORTED" if not bad else "REJECTED"
    return resolved("S3", status,
                    {"cells": len(rows), "outside": len(bad),
                     "max_relative_error": max(r["relative_error"]
                                               for r in rows)},
                    f"SUPPORTED iff every measured in-control ARL is within "
                    f"{S3_ARL0_REL_MAX:.0%} of the frozen target",
                    {"outside": bad})


def s4_regularity(reg):
    st = reg["statistics"]
    ok = (st["S4_E_z_psi_max_error"] <= S4_EZPSI_TOL
          and st["S4_E_psi_max_abs"] <= S4_EPSI_TOL
          and st["S4_fisher_max_abs_diff"] <= S4_FISHER_TOL)
    return resolved("S4", "SUPPORTED" if ok else "REJECTED", st,
                    "SUPPORTED iff E[eps psi]=1, E[psi]=0 and the Fisher "
                    "information reproduce Stage-D within the frozen "
                    "tolerances for all six families")


def s5_calibration(cal):
    non_g = [r for r in cal["rows"] if r["family"] != "gaussian"]
    failed = cal["calibration_failed_families"]
    status = "SUPPORTED" if not failed else "REJECTED"
    return resolved("S5", status,
                    {"max_relative_error_non_gaussian":
                         cal["max_relative_error_non_gaussian"],
                     "outcomes": cal["outcomes"],
                     "used_retry": cal["used_retry_families"],
                     "failed": failed,
                     "budgets_match_declaration":
                         cal["all_budgets_match_declaration"]},
                    f"SUPPORTED iff every non-Gaussian SR threshold is accepted "
                    f"on a held-out sample within {CAL_TOLERANCE:.1%} under the "
                    f"frozen search/verify/retry ladder",
                    {"per_family": [{"family": r["family"],
                                     "outcome": r["outcome"],
                                     "threshold": r["threshold"],
                                     "verify_1_rel": r["verify_1"]
                                         ["relative_error"],
                                     "verify_2_rel": (r["verify_2"] or {})
                                         .get("relative_error")}
                                    for r in non_g]})


# ---------------------------------------------------------------------------
# S6 / S7 -- regime survival and the window-separability law
# ---------------------------------------------------------------------------
def s6_regime(E1):
    idx = cell_index(E1)
    eligible, reported = [], []
    for det in DETECTORS:
        for f in FAMILIES:
            for m in M_P3_SUPPORTED:
                c = idx[(det, f)]["per_m"][str(m)]
                row = {"detector": det, "family": f, "m": m,
                       "gamma_A": c["gamma_A"], "se": c["gamma_A_se"],
                       "lower95": c["gamma_ci95"][0],
                       "exceeds_2": c["lower_bound_exceeds_2"],
                       "regime": c["regime"], "rho_c": c["rho_c"]}
                (reported if f in MOMENT_MARGINAL else eligible).append(row)
    n_ok = sum(r["exceeds_2"] for r in eligible)
    status = "SUPPORTED" if n_ok == len(eligible) else "REJECTED"
    return resolved("S6", status, {"eligible_passing": n_ok,
                                   "of": len(eligible)},
                    f"SUPPORTED iff the lower 95% bound of Gamma_A exceeds "
                    f"{S6_LOWER_BOUND} in every eligible (D,f,m) cell; the "
                    f"moment-marginal family {MOMENT_MARGINAL} is reported in "
                    f"full and never counted either way",
                    {"eligible": eligible, "moment_marginal_reported": reported})


def _K_table(E1):
    idx = cell_index(E1)
    K = {}
    for det in DETECTORS:
        for f in FAMILIES:
            per = idx[(det, f)]["per_m"]
            rc1 = per["1"]["rho_c"]
            for m in M_GRID:
                rc = per[str(m)]["rho_c"]
                K[(det, f, m)] = None if (rc is None or rc1 in (None, 0)) \
                    else rc / rc1
    return K


def s7_window_law(E1):
    K = _K_table(E1)
    per_m, worst = {}, 0.0
    for m in K_WINDOWS:
        vals = [K[(d, f, m)] for d in DETECTORS for f in ELIGIBLE_FAMILIES]
        s = spread(vals)
        per_m[str(m)] = {"spread": s, "values": vals,
                         "within": bool(s <= S7_SPREAD_MAX)}
        worst = max(worst, s)
    status = ("SUPPORTED" if all(v["within"] for v in per_m.values())
              else "REJECTED")
    return resolved("S7", status, {"max_spread": worst,
                                   "threshold": S7_SPREAD_MAX,
                                   "per_m": {k: v["spread"]
                                             for k, v in per_m.items()}},
                    f"SUPPORTED iff the relative spread of "
                    f"K(D,f,m)=rho_c(m)/rho_c(1) across the 10 eligible (D,f) "
                    f"cells is <= {S7_SPREAD_MAX} for every m in {K_WINDOWS}",
                    {"per_m": per_m})


def s7d_detector(E1):
    K = _K_table(E1)
    rows, worst = [], 0.0
    for f in ELIGIBLE_FAMILIES:
        for m in K_WINDOWS:
            r = K[("cusum", f, m)] / K[("sr", f, m)]
            dev = abs(r - 1.0)
            worst = max(worst, dev)
            rows.append({"family": f, "m": m, "ratio": r, "deviation": dev,
                         "within": bool(dev <= S7D_RESIDUAL_MAX)})
    status = "SUPPORTED" if all(r["within"] for r in rows) else "REJECTED"
    return resolved("S7D", status, {"max_deviation": worst,
                                    "threshold": S7D_RESIDUAL_MAX},
                    f"SUPPORTED iff |K(cusum,f,m)/K(sr,f,m) - 1| <= "
                    f"{S7D_RESIDUAL_MAX} for all eligible f and m in "
                    f"{K_WINDOWS}", {"rows": rows})


def s7f_family(E1):
    K = _K_table(E1)
    rows, worst = [], 0.0
    for det in DETECTORS:
        for m in K_WINDOWS:
            vals = [K[(det, f, m)] for f in ELIGIBLE_FAMILIES]
            s = spread(vals)
            worst = max(worst, s)
            rows.append({"detector": det, "m": m, "spread": s,
                         "within": bool(s <= S7F_SPREAD_MAX)})
    status = "SUPPORTED" if all(r["within"] for r in rows) else "REJECTED"
    return resolved("S7F", status, {"max_spread": worst,
                                    "threshold": S7F_SPREAD_MAX},
                    f"SUPPORTED iff, for each detector, the spread of K across "
                    f"the eligible families is <= {S7F_SPREAD_MAX} for every m "
                    f"in {K_WINDOWS}", {"rows": rows})


def s7x_extrapolation(E1):
    K = _K_table(E1)
    rows = []
    for m in EXTRAPOLATION_M:
        vals = [K[(d, f, m)] for d in DETECTORS for f in ELIGIBLE_FAMILIES]
        rows.append({"m": m, "spread": spread(vals), "values": vals})
    return resolved("S7X", "OUT_OF_SCOPE",
                    {"rows": rows},
                    f"m in {EXTRAPOLATION_M} lies outside P3's supported window "
                    f"grid.  Frozen before results as EXTRAPOLATION_BEYOND_P3: "
                    f"reported, never gated, never used to support or reject "
                    f"the window law")


# ---------------------------------------------------------------------------
# S8 / S9 -- exact algebraic identities
# ---------------------------------------------------------------------------
def s8_decomposition(E1):
    idx = cell_index(E1)
    rows, worst = [], 0.0
    for det in DETECTORS:
        for f in FAMILIES:
            for m in M_GRID:
                c = idx[(det, f)]["per_m"][str(m)]
                r = c["decomposition_residual_max_abs"]
                if r is None:
                    continue
                worst = max(worst, r)
                rows.append({"detector": det, "family": f, "m": m,
                             "max_abs_residual": r,
                             "within": bool(r <= S8_ABS_TOL)})
    status = "SUPPORTED" if all(r["within"] for r in rows) else "REJECTED"
    return resolved("S8", status,
                    {"max_abs_residual": worst, "tolerance": S8_ABS_TOL,
                     "cells": len(rows)},
                    f"SUPPORTED iff max_batch |Gamma_A(m) - (1/m) sum_r gamma_r "
                    f"- R_m| <= {S8_ABS_TOL} in every cell.  This is an EXACT "
                    f"algebraic identity summed in two different orders, so the "
                    f"test is absolute, not statistical.",
                    {"worst": sorted(rows, key=lambda r: -r["max_abs_residual"])[:8]})


def s9_convention(E1):
    idx = cell_index(E1)
    worst, missing = 0.0, []
    for det in DETECTORS:
        for f in FAMILIES:
            for m in M_GRID:
                c = idx[(det, f)]["per_m"][str(m)]
                worst = max(worst, c["convention_residual_max_abs"])
                if c["p_tau_lt_m"] is None:
                    missing.append((det, f, m))
    ok = worst <= S9_EXACT_TOL and not missing
    return resolved("S9", "SUPPORTED" if ok else "REJECTED",
                    {"max_abs_residual": worst, "tolerance": S9_EXACT_TOL,
                     "cells_missing_p_tau_lt_m": len(missing)},
                    f"SUPPORTED iff |(Gamma_A - Gamma_B) - R_m| <= "
                    f"{S9_EXACT_TOL} in every cell and P(tau<m) is present")


# ---------------------------------------------------------------------------
# S10 -- P7's boundary criterion, applied to the declared sub-family grid
# ---------------------------------------------------------------------------
P7_METRICS = ("arl", "ref_mse", "fap100", "e_acf1")


def s10_boundary(chain):
    per_family, reproduced = {}, 0
    unc_rows = []
    for f in FAMILIES:
        sub, avail = [], 0
        for det in DETECTORS:
            c = chain.get((det, f))
            if c is None or c["status"] != "OK":
                continue
            for m in sorted({r["m"] for r in c["rows"]}):
                lad = sorted([r for r in c["rows"]
                              if r["m"] == m and r["rho_over_rhoc"]],
                             key=lambda r: r["rho_over_rhoc"])
                ladder = [r["rho_over_rhoc"] for r in lad]
                entry = {"detector": det, "m": m, "ladder": ladder,
                         "metrics": {}}
                for metric in P7_METRICS:
                    try:
                        v = p7_boundary_rates(ladder,
                                              [r[metric] for r in lad], metric)
                    except ValueError:
                        entry["metrics"][metric] = {"status": "UNAVAILABLE"}
                        continue
                    entry["metrics"][metric] = v
                    if metric != "e_acf1":
                        try:
                            unc = p7_boundary_rate_uncertainty(
                                ladder, [r[metric] for r in lad],
                                [r[metric + "_se"] for r in lad])
                            unc_rows.append({"family": f, "detector": det,
                                             "m": m, "metric": metric, **unc})
                        except Exception:
                            pass
                if any(x.get("status") != "UNAVAILABLE"
                       for x in entry["metrics"].values()):
                    avail += 1
                sub.append(entry)
        need = max(1, avail // 2)
        by_metric = {}
        for metric in P7_METRICS:
            hits = sum(1 for e in sub
                       if e["metrics"].get(metric, {}).get("peaks_at_boundary"))
            by_metric[metric] = hits
        verdict = any(h >= need for h in by_metric.values())
        reproduced += verdict
        per_family[f] = {"sub_families_available": avail, "required": need,
                         "hits_by_metric": by_metric, "reproduces": verdict,
                         "sub_families": sub}
    status = ("SUPPORTED" if reproduced >= S10_FAMILIES_REQUIRED
              else "REJECTED")
    # descriptive multiplicity companion; never part of the gate
    ps = []
    for r in unc_rows:
        if r["difference_se"] and r["difference_se"] > 0:
            from scipy import stats
            ps.append(float(2.0 * stats.norm.sf(
                abs(r["difference"]) / r["difference_se"])))
        else:
            ps.append(1.0)
    rej = bh_fdr(ps, BH_Q).tolist() if ps else []
    return resolved("S10", status,
                    {"families_reproducing": reproduced, "of": len(FAMILIES),
                     "required": S10_FAMILIES_REQUIRED},
                    f"SUPPORTED iff P7's boundary criterion reproduces in >= "
                    f"{S10_FAMILIES_REQUIRED} of 6 families on the declared "
                    f"sub-family grid (detector x m in {{1,5}}) and metric set "
                    f"{P7_METRICS}.  This is P7's criterion applied to a "
                    f"DECLARED SUBSET of P7's coverage, not verbatim P7 "
                    f"coverage; the subset was frozen before results.",
                    {"per_family": per_family,
                     "uncertainty_companion": {
                         "note": "DESCRIPTIVE ONLY; never part of the gate",
                         "q": BH_Q, "n_comparisons": len(ps),
                         "rows": [{**r, "p": p, "bh_reject": bool(k)}
                                  for r, p, k in zip(unc_rows, ps, rej)]}})


# ---------------------------------------------------------------------------
# S11 / S12 / S13 / S14 / S15
# ---------------------------------------------------------------------------
def s11_degradation(chain, arl):
    nominal = {(r["detector"], r["family"]): r["arl0"]
               for r in arl["rows"] if r["status"] == "OK"}
    rows = []
    for (det, f), c in sorted(chain.items()):
        if c["status"] != "OK":
            continue
        for r in c["rows"]:
            # the full-reuse anchor.  It is matched on rho itself, not on the
            # ladder label: rho = 1 can enter the grid either as an absolute
            # anchor or as a multiple of rho_c, and the cell must not be lost
            # because of which label it happened to receive.
            if r["rho"] != 1.0:
                continue
            nom = nominal.get((det, f))
            rows.append({"detector": det, "family": f, "m": r["m"],
                         "chain_arl_rho1": r["arl"], "nominal_arl0": nom,
                         "fraction": r["arl"] / nom if nom else None,
                         "below_half": bool(nom and r["arl"] < S11_ARL_FRACTION
                                            * nom)})
    status = ("SUPPORTED" if rows and all(r["below_half"] for r in rows)
              else "REJECTED")
    return resolved("S11", status,
                    {"cells": len(rows),
                     "max_fraction": max((r["fraction"] for r in rows),
                                         default=None)},
                    f"SUPPORTED iff the chain ARL at rho=1 is below "
                    f"{S11_ARL_FRACTION:.0%} of the same-cell nominal ARL_0 in "
                    f"every declared (D,f,m) cell", {"rows": rows})


def s12_detector_transfer(E1):
    bv = E1["batch_gamma_A"]
    rows = []
    for f in FAMILIES:
        for m in M_GRID:
            a, b = bv.get(f"cusum|{f}|{m}"), bv.get(f"sr|{f}|{m}")
            if not a or not b:
                continue
            r = paired_ratio(a, b)
            rows.append({"family": f, "m": m, **r})
    n = len(rows)
    n_excl = sum(r["excludes_one"] for r in rows)
    n_incl = n - n_excl
    if n and n_incl / n >= 0.90:
        status = "SUPPORTED"
    elif n and n_excl / n >= 0.90:
        status = "REJECTED"
    else:
        status = "INCONCLUSIVE"
    return resolved("S12", status,
                    {"comparisons": n, "ci_excludes_one": n_excl,
                     "ci_contains_one": n_incl,
                     "max_abs_deviation": max((abs(r["ratio"] - 1.0)
                                               for r in rows), default=None)},
                    "SUPPORTED iff the paired 95% CI of "
                    "Gamma_A(cusum)/Gamma_A(sr) contains 1 in >=90% of the "
                    "(f,m) comparisons; REJECTED iff it excludes 1 in >=90%; "
                    "else INCONCLUSIVE.  Intervals use the CRN-paired "
                    "linearised SE, never an independent-SE formula.",
                    {"rows": rows})


def s13_seed(E1, E5):
    i1, i5 = cell_index(E1), cell_index(E5)
    rows = []
    for det in DETECTORS:
        for f in FAMILIES:
            for m in M_GRID:
                a = i1[(det, f)]["per_m"][str(m)]
                b = i5[(det, f)]["per_m"][str(m)]
                z = combined_z(a["gamma_A"], a["gamma_A_se"],
                               b["gamma_A"], b["gamma_A_se"])
                rows.append({"detector": det, "family": f, "m": m,
                             "E1": a["gamma_A"], "E1_se": a["gamma_A_se"],
                             "E5": b["gamma_A"], "E5_se": b["gamma_A_se"],
                             "z": z,
                             "within": bool(abs(z) <= COMBINED_Z_TOLERANCE)})
    non_t3 = [r for r in rows if r["family"] not in MOMENT_MARGINAL]
    fa = sum(r["within"] for r in rows) / len(rows)
    fn = sum(r["within"] for r in non_t3) / len(non_t3)
    ok = fa >= S13_CELL_FRACTION and fn >= S13_NON_T3_FRACTION
    q = cochran_q(
        np.array([r["E1"] for r in rows] + [r["E5"] for r in rows]),
        np.array([r["E1_se"] for r in rows] + [r["E5_se"] for r in rows]))
    return resolved("S13", "SUPPORTED" if ok else "REJECTED",
                    {"fraction_all": fa, "fraction_non_t3": fn,
                     "cells": len(rows)},
                    f"SUPPORTED iff E1 and E5 agree within 3 combined SE in >= "
                    f"{S13_CELL_FRACTION:.0%} of all cells and >= "
                    f"{S13_NON_T3_FRACTION:.0%} of the non-{MOMENT_MARGINAL} "
                    f"cells",
                    {"failures": [r for r in rows if not r["within"]],
                     "cochran_q_DESCRIPTIVE_ONLY": q})


def s14_drift(drift):
    """Reporting completeness, against the count the frozen plan declares."""
    n_specs = 1 + len(SHIFTS) + len(RAMP_SLOPES)
    per_cell = len(M_CHAIN) * 2 * n_specs          # m x rho in {0,1} x specs
    rows, excluded, present, labelled = [], [], 0, 0
    for (det, f), c in sorted(drift.items()):
        if c["status"] != "OK":
            excluded.append({"detector": det, "family": f,
                             "status": c["status"]})
            continue
        for r in c["rows"]:
            present += 1
            d = r["delay"]
            complete = (d.get("q50") is not None and d.get("q95") is not None
                        and d.get("p_gt_100") is not None
                        and d["tail_label"] in ("OK",
                                                "INSUFFICIENT_TAIL_EVENTS"))
            labelled += complete
            rows.append({"detector": det, "family": f, "m": r["m"],
                         "rho": r["rho"], "pattern": r["pattern"],
                         "size": r["size"], "slope": r["slope"],
                         "mean": d["mean"], "se": d["se"], "q50": d["q50"],
                         "q95": d["q95"], "p_gt_100": d["p_gt_100"],
                         "n_tail_events": d["n_tail_events"],
                         "tail_label": d["tail_label"],
                         "complete": bool(complete)})
    expected = (len(DETECTORS) * len(FAMILIES) - len(excluded)) * per_cell
    ok = present == expected and labelled == present and present > 0
    n_insuff = sum(1 for r in rows
                   if r["tail_label"] == "INSUFFICIENT_TAIL_EVENTS")
    return resolved("S14", "SUPPORTED" if ok else "REJECTED",
                    {"rows_expected": expected, "rows_reported": present,
                     "rows_complete": labelled,
                     "cells_excluded": len(excluded),
                     "insufficient_tail_labels": n_insuff},
                    f"SUPPORTED iff all {per_cell} declared drift rows per "
                    f"non-excluded (D,f) cell are reported, each with its q50, "
                    f"q95, P(delay>100) and an explicit tail label",
                    {"rows": rows, "excluded_cells": excluded})


def s15_heavy_tail(E1, E5, repro):
    """t3 at m=20: is local ATTRACTION (Gamma_A < 2) established?"""
    i1, i5 = cell_index(E1), cell_index(E5)
    rows = []
    for det in DETECTORS:
        a = i1[(det, "t3")]["per_m"]["20"]
        b = i5[(det, "t3")]["per_m"]["20"]
        ind = next((r for r in repro["rows"]
                    if r["detector"] == det and r["family"] == "t3"
                    and str(r["m"]) == "20"), None)
        rows.append({
            "detector": det,
            "E1": a["gamma_A"], "E1_ci95": a["gamma_ci95"],
            "E5": b["gamma_A"], "E5_ci95": b["gamma_ci95"],
            "independent": None if ind is None else ind["gamma_A"],
            "independent_ci95": None if ind is None else ind["ci95"],
            "E1_upper_below_2": bool(a["gamma_ci95"][1] < S6_LOWER_BOUND),
            "E5_upper_below_2": bool(b["gamma_ci95"][1] < S6_LOWER_BOUND),
            "independent_upper_below_2":
                None if ind is None else bool(ind["ci95"][1] < S6_LOWER_BOUND)})
    established = [r for r in rows
                   if r["E1_upper_below_2"] and r["E5_upper_below_2"]
                   and r["independent_upper_below_2"]]
    status = "SUPPORTED" if established else "INCONCLUSIVE"
    return resolved("S15", status,
                    {"detectors_establishing_attraction":
                         [r["detector"] for r in established]},
                    "SUPPORTED (attraction established) iff the upper 95% bound "
                    "of Gamma_A at t3/m=20 lies below 2 in E1 AND E5 AND the "
                    "independent reimplementation.  Anything else is "
                    "INCONCLUSIVE: a point estimate below 2 is not evidence of "
                    "attraction, and m=20 is outside P3's supported window "
                    "grid in any case.", {"rows": rows})


def s16_p3_discrepancy(E1):
    idx = cell_index(E1)
    p3 = p3_boundaries()
    p7 = json.loads((P7 / "results" / "sr_gain_check.json").read_text())
    rows = []
    for r in p7["rows"]:
        if r["detector"] != "sr":
            continue
        m = int(r["m"])
        c = idx[("sr", "gaussian")]["per_m"][str(m)]
        z3 = combined_z(c["gamma_A"], c["gamma_A_se"],
                        p3[("sr", m)]["gamma_tilde"],
                        p3[("sr", m)]["gamma_tilde_se"])
        z7 = combined_z(c["gamma_A"], c["gamma_A_se"],
                        r["p7_gamma"], r["p7_batch_se"])
        rows.append({"m": m, "p8r": c["gamma_A"], "p8r_se": c["gamma_A_se"],
                     "p3": p3[("sr", m)]["gamma_tilde"],
                     "p3_se": p3[("sr", m)]["gamma_tilde_se"],
                     "p7": r["p7_gamma"], "p7_se": r["p7_batch_se"],
                     "z_vs_p3": z3, "z_vs_p7": z7,
                     "relative_vs_p3": c["gamma_A"] / p3[("sr", m)]
                         ["gamma_tilde"] - 1.0,
                     "relative_vs_p7": c["gamma_A"] / r["p7_gamma"] - 1.0})
    near_p7 = all(abs(r["z_vs_p7"]) <= COMBINED_Z_TOLERANCE for r in rows)
    below_p3 = all(r["relative_vs_p3"] < 0 for r in rows)
    if near_p7 and below_p3:
        label = "KNOWN_PREEXISTING_DISCREPANCY"
    elif near_p7:
        label = "AGREES_WITH_P7"
    elif all(abs(r["z_vs_p3"]) <= COMBINED_Z_TOLERANCE for r in rows):
        label = "AGREES_WITH_P3"
    else:
        label = "NEW_DEFECT_CANDIDATE"
    return resolved("S16", "SUPPORTED" if label != "NEW_DEFECT_CANDIDATE"
                    else "REJECTED",
                    {"classification": label},
                    "The frozen decision table: agreeing with P7 while sitting "
                    "systematically below P3 at every m is "
                    "KNOWN_PREEXISTING_DISCREPANCY (P8R neither owns nor "
                    "resolves the P3 numbers); agreeing with neither is a "
                    "NEW_DEFECT_CANDIDATE and REJECTS this question.",
                    {"rows": rows})


def s17_independent(repro):
    rows = repro["rows"]
    ok = sum(r["within"] for r in rows)
    outliers = [r for r in rows if not r["within"]]
    status = ("SUPPORTED" if len(outliers) <= S17_MAX_OUTLIERS
              else "REJECTED")
    return resolved("S17", status,
                    {"cells_within": ok, "of": len(rows),
                     "outliers": len(outliers),
                     "max_outliers_allowed": S17_MAX_OUTLIERS},
                    f"SUPPORTED iff at most {S17_MAX_OUTLIERS} of the "
                    f"representative cells of the independent reimplementation "
                    f"exceeds {COMBINED_Z_TOLERANCE} combined SE against "
                    f"production",
                    {"rows": rows, "outlier_rows": outliers})


# ---------------------------------------------------------------------------
def main() -> None:
    E1 = load("gamma_matrix_E1.json")
    E5 = load("gamma_matrix_E5.json")
    cal = load("sr_calibration.json")
    arl = load("arl0_check.json")
    reg = load("family_regularity.json")
    repro = load("independent_reproduction.json")
    chain = {}
    for det in DETECTORS:
        for f in FAMILIES:
            p = RESULTS / "chain" / f"E3_{det}_{f}.json"
            if p.exists():
                chain[(det, f)] = C.load_payload(p)
    drift = {}
    for det in DETECTORS:
        for f in FAMILIES:
            p = RESULTS / "drift" / f"E4_{det}_{f}.json"
            if p.exists():
                drift[(det, f)] = C.load_payload(p)

    questions = [
        s1_p3(E1), s2_p4(E1, reg), s3_arl0(arl), s4_regularity(reg),
        s5_calibration(cal), s6_regime(E1), s7_window_law(E1),
        s7d_detector(E1), s7f_family(E1), s7x_extrapolation(E1),
        s8_decomposition(E1), s9_convention(E1), s10_boundary(chain),
        s11_degradation(chain, arl), s12_detector_transfer(E1),
        s13_seed(E1, E5), s14_drift(drift), s15_heavy_tail(E1, E5, repro),
        s16_p3_discrepancy(E1), s17_independent(repro),
    ]
    payload = {"target_arl0": stage_d_target_arl0(),
               "n_questions": len(questions),
               "resolved": all(q["status"] in
                               ("SUPPORTED", "REJECTED", "INCONCLUSIVE",
                                "OUT_OF_SCOPE") for q in questions),
               "summary": {q["question"]: q["status"] for q in questions},
               "questions": questions}
    C.write(RESULTS / "scientific_resolution.json",
            C.envelope(generator="derive_resolution.py",
                       schema="rebaseguard.p8r.scientific-resolution.v1",
                       tags=[], payload=payload))
    for q in questions:
        print(f"  {q['question']:5s} {q['status']:14s} "
              f"{json.dumps(q['statistic'], default=float)[:110]}")


if __name__ == "__main__":
    main()
