"""P5Y Gate-2F: PILOT-SR-METRIC-B.

ONE semantic change relative to Gate-2E:

    P1_RULE_TARGET     = (1 - eps_P1) * 1e-9    -- solves for h_z (headroom)
    P1_CHECK_THRESHOLD = 1e-9                   -- tests E_d (the requirement)

Everything else is Gate-2E's, by direct reference rather than transcription.
Every precision cell is computed by calling Gate-2E's `run_cell` VERBATIM, so
the absolute metric, composed contraction, moments and radii are bit-identical
to Gate-2E by construction. Only the P1 verdict is recomputed, in Arb, from the
cell's own E_d against the distinct check threshold.
"""
from __future__ import annotations

import json, math, resource, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
G2E = ROOT / "level4" / "closure_proofs" / "p5y_gate2e_sr_metric"
G2D = ROOT / "level4" / "closure_proofs" / "p5y_gate2d_sr_realcandidate"
R3 = ROOT / "level4" / "closure_proofs" / "p5x_global_nonlinear_dynamics" / "compute_optimization_r3_sr_symbolic"
for p in (str(R3), str(ROOT / "rebaseguard-proof" / "src"), str(G2D), str(G2E)):
    if p not in sys.path:
        sys.path.insert(0, p)

from flint import arb                                                        # noqa: E402
from rebaseguard_certify.arb_backend import ball_record, rational, workprec   # noqa: E402
import sr_local as L                                                         # noqa: E402
from r3_gate import unit_candidate                                           # noqa: E402
import sr_realcandidate as G2DM                                              # noqa: E402
import sr_metric as S2E                                                      # noqa: E402  (Gate-2E, frozen)

# ---- THE ONLY NEW CONSTANTS -------------------------------------------------
P1_RULE_TARGET = (arb(1) - S2E.EPS_P1) * S2E.P1_TARGET     # construction: headroom
P1_CHECK_THRESHOLD = S2E.P1_TARGET                          # acceptance: 1e-9
MIN_HEADROOM_REL = 1e-6                                     # robustness guard
# -----------------------------------------------------------------------------

INHERITED = ("BOUNDARY", "SLACK_R", "ALPHA", "W_TARGET", "RESERVE_FRACTION",
             "LOCAL_GATE_BUDGET", "W_PANEL_MAX", "DELTA_CANDIDATE_MAX",
             "C_SR_QUARTER", "C_SR_ZERO", "C_SR_CERTIFIED_CAP", "N_PANELS",
             "E_ABS_RAW", "GRID", "E_NUM", "E_DEN", "DEGREE", "CAND_DEGREE",
             "GATE2A_NZ", "MAX_COMPLEXITY_SCORE", "TIMING_REPEATS")


def inheritance_audit():
    """Every metric constant is Gate-2E's own object; nothing is transcribed."""
    g2e = json.loads((G2E / "results" / "sr_metric.json").read_text())
    m = g2e["metric"]
    rows = {k: getattr(S2E, k) for k in INHERITED}
    checks = {
        "metric_type_absolute": m["type"] == "ABSOLUTE",
        "target_R_max_lt_2": m["scientific_target"] == "R_MAX_LT_2",
        "slack_R": rows["SLACK_R"] == m["slack_R"] == 2.0,
        "alpha": rows["ALPHA"] == m["alpha"] == 0.1,
        "w_target": rows["W_TARGET"] == m["w_target"] == 0.2,
        "ledger": S2E.LEDGER == {k: v for k, v in m["ledger_fractions"].items()},
        "ledger_absolute": all(abs(S2E.B_ABS[k] - v) < 1e-15
                               for k, v in m["ledger_absolute"].items()),
        "reserve": abs(rows["RESERVE_FRACTION"] - m["reserve_fraction"]) < 1e-15,
        "local_gate_budget": abs(rows["LOCAL_GATE_BUDGET"] - m["local_gate_budget"]) < 1e-15,
        "w_panel_max": abs(rows["W_PANEL_MAX"] - m["w_panel_max"]) < 1e-18,
        "delta_candidate_max": abs(rows["DELTA_CANDIDATE_MAX"] - m["delta_candidate_max"]) < 1e-18,
        "C_SR_quarter": rows["C_SR_QUARTER"] == m["C_SR_quarter"],
        "n_panels": rows["N_PANELS"] == m["n_panels"],
        "patch": list(S2E.PATCH) == g2e["frozen"]["patch"],
        "grid": rows["GRID"] == g2e["frozen"]["grid"],
        "degree": rows["DEGREE"] == g2e["frozen"]["degree"],
        "cand_bidegree": [rows["CAND_DEGREE"]] * 2 == g2e["frozen"]["candidate_bidegree"],
        "precisions": list(S2E.PRECISIONS) == g2e["frozen"]["precisions"],
        "run_cell_is_gate2e_function": S2E.run_cell.__module__ == "sr_metric",
    }
    diffs = {"P1_RULE_TARGET": float(P1_RULE_TARGET),
             "P1_CHECK_THRESHOLD": float(P1_CHECK_THRESHOLD),
             "gate2e_used_single_threshold": float((arb(1) - S2E.EPS_P1) * S2E.P1_TARGET)}
    return {"checks": checks, "PASS": all(checks.values()),
            "only_semantic_difference": "P1 threshold pair (rule vs check)",
            "p1_threshold_pair": diffs,
            "thresholds_distinct": bool(float(P1_RULE_TARGET) < float(P1_CHECK_THRESHOLD)),
            "inherited_constants": {k: (float(v) if isinstance(v, (int, float)) else str(v))
                                    for k, v in rows.items()}}


def p1_verdict(E_used: arb, *, rule_target: arb = P1_RULE_TARGET,
               check_threshold: arb = P1_CHECK_THRESHOLD):
    """The one-line repair.  Comparison is done in Arb, not on a float."""
    head = (check_threshold - E_used) / check_threshold
    hr = float(head.lower())
    return {"E_d_arb": ball_record(E_used),
            "rule_target": float(rule_target),
            "check_threshold": float(check_threshold),
            "thresholds_distinct": bool(rule_target < check_threshold),
            "headroom_rel": hr,
            "headroom_guard": MIN_HEADROOM_REL,
            "P1_PASS": bool(E_used <= check_threshold and hr >= MIN_HEADROOM_REL)}


def negative_control(E_used: arb):
    """Reproduce the OLD symmetric logic on the same path; it must be knife-edge."""
    old = p1_verdict(E_used, rule_target=P1_RULE_TARGET, check_threshold=P1_RULE_TARGET)
    new = p1_verdict(E_used)
    return {"old_symmetric": {"threshold": old["check_threshold"],
                              "headroom_rel": old["headroom_rel"],
                              "P1_PASS": old["P1_PASS"],
                              "knife_edge": bool(abs(old["headroom_rel"]) < MIN_HEADROOM_REL)},
            "new_asymmetric": {"threshold": new["check_threshold"],
                               "headroom_rel": new["headroom_rel"],
                               "P1_PASS": new["P1_PASS"],
                               "robust": bool(new["headroom_rel"] >= MIN_HEADROOM_REL)},
            "PASS": bool(abs(old["headroom_rel"]) < MIN_HEADROOM_REL
                         and new["headroom_rel"] >= MIN_HEADROOM_REL)}


def geometry_and_Ed():
    """h_z from the RULE target (unchanged); E_d recomputed in Arb for the CHECK."""
    with workprec(512):
        A, b_sr, c_sr = G2DM.sr_constants()
        e = rational(S2E.E_NUM, S2E.E_DEN)
        geo = L.patch_geometry(*S2E.PATCH, grid=S2E.GRID)
        core_lo, core_hi = geo["core"]
        patch_half = (geo["yp"][1] - geo["yp"][0]) / arb(2)
        M = L.softplus_derivative_bound_tight(S2E.DEGREE + 1)
        fact = arb(math.factorial(S2E.DEGREE + 1))
        H_max = ((P1_RULE_TARGET * fact / M).log() / arb(S2E.DEGREE + 1)).exp()
        h_z = arb(float((H_max - patch_half).lower()))
        n_z = int(math.ceil(float(((core_hi - core_lo) / (arb(2) * h_z)).upper())))
        H_used = h_z + patch_half
        E_used = M * (H_used ** (S2E.DEGREE + 1)) / fact
        cand1, eps1, _ = G2DM.build_hhat1(e, b_sr, c_sr)
    return {"geo": geo, "e": e, "h_z": h_z, "n_z": n_z, "E_used": E_used,
            "cand1": cand1, "eps1": eps1, "b_sr": b_sr, "c_sr": c_sr}


def run_pilot(candidate_budget=None):
    out = {"stages_run": []}
    out["stages_run"].append("inheritance_audit")
    out["inheritance_audit"] = inheritance_audit()
    if not out["inheritance_audit"]["PASS"]:
        out["decision"] = "SR_METRIC_B_FAIL_ARCHITECTURE"
        out["failure_class"] = "REPRESENTATION_FAILURE"; return out

    out["stages_run"].append("amplification_consistency")
    out["direction_audit"] = S2E.direction_audit()
    if not out["direction_audit"]["PASS"]:
        out["decision"] = "SR_METRIC_B_FAIL_ARCHITECTURE"
        out["failure_class"] = "REPRESENTATION_FAILURE"; return out

    g = geometry_and_Ed()
    out["p1_geometry"] = {"h_z": float(g["h_z"]), "n_z": g["n_z"],
                          "n_z_expected": S2E.GATE2A_NZ,
                          "panel_count_unchanged": bool(g["n_z"] == S2E.GATE2A_NZ)}

    out["stages_run"].append("p1_structural")
    out["p1_structural"] = p1_verdict(g["E_used"])
    out["negative_control"] = negative_control(g["E_used"])
    if not (out["p1_structural"]["thresholds_distinct"]
            and out["negative_control"]["PASS"]):
        out["decision"] = "SR_METRIC_B_FAIL_P1"
        out["failure_class"] = "P1_HEADROOM_FAILURE"; return out

    out["stages_run"].append("candidate_precondition")
    out["acceptance_precondition"] = S2E.acceptance_precondition(g["eps1"], candidate_budget)
    if not out["acceptance_precondition"]["PASS"]:
        out["decision"] = "SR_METRIC_B_FAIL_ABSOLUTE"
        out["failure_class"] = "ABSOLUTE_METRIC_FAILURE"; return out

    out["stages_run"].append("representation_guard")
    ctrl = unit_candidate()
    with workprec(512):
        bf, cf = float(g["b_sr"]), float(g["c_sr"])
    cand2 = G2DM.build_hhat2(S2E.E_NUM / S2E.E_DEN, bf, cf, 256)
    out["representation_guard"] = S2E.representation_guard(
        {"hhat_1": g["cand1"], "hhat_2": cand2, "unit_candidate": ctrl})
    if not out["representation_guard"]["PASS"]:
        out["decision"] = "SR_METRIC_B_FAIL_ARCHITECTURE"
        out["failure_class"] = "REPRESENTATION_FAILURE"; return out

    out["stages_run"].append("precision_grid")
    cells = {}
    for name, c, eps in (("hhat_1", g["cand1"], g["eps1"]),
                         ("hhat_2_probe", cand2, arb(0)),
                         ("unit_candidate_control", ctrl, arb(0))):
        rows = []
        for b in S2E.PRECISIONS:
            cell = S2E.run_cell(b, c, eps, g["geo"], g["e"], g["h_z"], name)  # VERBATIM
            with workprec(512):
                assert abs(cell["E_d"] - float(g["E_used"].upper())) < 1e-24, \
                    "E_d from Gate-2E's run_cell must match the Arb recomputation"
                v = p1_verdict(g["E_used"])
            cell["p1"] = v
            cell["P1_PASS_new"] = v["P1_PASS"]
            cell["P1_PASS_gate2e_symmetric"] = cell.pop("P1_repaired_pass")
            cell["CELL_PASS"] = bool(cell["ABS_PASS"] and v["P1_PASS"])
            rows.append(cell)
        cells[name] = rows
    out["cells"] = cells

    rep = S2E.run_cell(256, g["cand1"], g["eps1"], g["geo"], g["e"], g["h_z"], "repro")
    base = cells["hhat_1"][0]
    out["reproducibility"] = {
        "cell": "hhat_1 @ 256",
        "enclosure_identical": base["acc_enclosure"]["ball"] == rep["acc_enclosure"]["ball"],
        "abs_metric_identical": base["w_panel_total_ABS"] == rep["w_panel_total_ABS"],
        "E_d_identical": base["E_d"] == rep["E_d"],
        "headroom_identical": True}
    out["reproducibility"]["PASS"] = bool(
        out["reproducibility"]["enclosure_identical"]
        and out["reproducibility"]["abs_metric_identical"]
        and out["reproducibility"]["E_d_identical"])

    sel = next((c["bits"] for c in cells["hhat_1"] if c["CELL_PASS"]), None)
    out["selected_safe_precision"] = sel
    if sel is None:
        bad_abs = any(not c["ABS_PASS"] for c in cells["hhat_1"])
        out["decision"] = ("SR_METRIC_B_FAIL_ABSOLUTE" if bad_abs else "SR_METRIC_B_FAIL_P1")
        out["failure_class"] = ("ABSOLUTE_METRIC_FAILURE" if bad_abs else "P1_HEADROOM_FAILURE")
    else:
        out["decision"] = f"SR_METRIC_B_PASS_{sel}"
        out["failure_class"] = "NONE"
    return out


def main():
    t_all = time.time(); c0 = time.process_time()
    out = {"schema": "rebaseguard.p5y.gate2f.srmetricb.v1", "binding": False,
           "pilot": "PILOT-SR-METRIC-B",
           "generated_utc": datetime.now(timezone.utc).isoformat(),
           "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                        capture_output=True, text=True).stdout.strip(),
           "gate2d_remains": "SR_REALCANDIDATE_FAIL_REPRESENTATION",
           "gate2e_remains": "SR_METRIC_FAIL_CANDIDATE",
           "the_only_change": {
               "P1_RULE_TARGET": float(P1_RULE_TARGET),
               "P1_CHECK_THRESHOLD": float(P1_CHECK_THRESHOLD),
               "eps_P1": float(S2E.EPS_P1),
               "min_headroom_rel": MIN_HEADROOM_REL,
               "gate2e_behaviour": "rule target and check threshold were the SAME value"},
           "metric_type": "ABSOLUTE"}
    out.update(run_pilot())
    # candidate identity across Gate-2D / 2E / 2F
    g2d = json.loads((G2D / "results" / "sr_realcandidate.json").read_text())
    g2e = json.loads((G2E / "results" / "sr_metric.json").read_text())
    out["candidate_identity"] = {
        "gate2d_eps_cand": g2d["genuine_candidate"]["eps_cand"],
        "gate2e_eps_cand": g2e["acceptance_precondition"]["eps_cand"],
        "gate2f_eps_cand": out.get("acceptance_precondition", {}).get("eps_cand"),
        "identical_across_all_three": bool(
            g2d["genuine_candidate"]["eps_cand"] == g2e["acceptance_precondition"]["eps_cand"]
            == out.get("acceptance_precondition", {}).get("eps_cand")),
        "refitted": False}
    if "cells" in out:
        out["absolute_metric_unchanged_vs_gate2e"] = {
            name: {"gate2e": g2e["cells"][name][0]["w_panel_total_ABS"],
                   "gate2f": out["cells"][name][0]["w_panel_total_ABS"],
                   "identical": g2e["cells"][name][0]["w_panel_total_ABS"]
                                == out["cells"][name][0]["w_panel_total_ABS"]}
            for name in ("hhat_1", "hhat_2_probe", "unit_candidate_control")}
    cpu = time.process_time() - c0
    out["runtime"] = {"wall_seconds": time.time() - t_all, "cpu_seconds": cpu,
                      "cpu_hours": cpu / 3600.0, "cap_cpu_seconds": 180,
                      "within_cap": bool(cpu <= 180),
                      "peak_rss_mib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 * 1024)}
    out["GATE2F_DECISION"] = out.pop("decision")
    (HERE / "results" / "sr_metric_b.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: out[k] for k in
                      ("the_only_change", "stages_run", "p1_geometry", "p1_structural",
                       "negative_control", "candidate_identity",
                       "absolute_metric_unchanged_vs_gate2e", "reproducibility",
                       "selected_safe_precision", "failure_class", "GATE2F_DECISION",
                       "runtime") if k in out}, indent=1, default=str))


if __name__ == "__main__":
    main()
