"""P5Y Gate-2E: PILOT-SR-METRIC.

Evaluates the Gate-2D objects under a PROPOSITION-DERIVED ABSOLUTE metric.

Execution order is enforced (the Gate-2D defect):
    metric (frozen constants) -> direction audit -> acceptance precondition
    -> representation guard -> ONLY THEN the precision grid.
"""
from __future__ import annotations

import json, math, resource, statistics, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
G2D = ROOT / "level4" / "closure_proofs" / "p5y_gate2d_sr_realcandidate"
R3 = ROOT / "level4" / "closure_proofs" / "p5x_global_nonlinear_dynamics" / "compute_optimization_r3_sr_symbolic"
for p in (str(R3), str(ROOT / "rebaseguard-proof" / "src"), str(G2D)):
    if p not in sys.path:
        sys.path.insert(0, p)

from flint import arb                                                        # noqa: E402
from rebaseguard_certify.arb_backend import ball_record, rational, workprec   # noqa: E402
import sr_local as L                                                         # noqa: E402
from r3_gate import unit_candidate                                           # noqa: E402
import sr_realcandidate as G2DM                                              # noqa: E402

# ---------------- FROZEN METRIC CONSTANTS (derived in GATE2E_PREREGISTRATION.md
# ---------------- section 5-7, from inputs that all predate Gate-2D)
BOUNDARY = 2.0                    # P5X-T4 / H3b, Checkpoint A
SLACK_R = 2.0                     # = BOUNDARY; the only theorem-backed constant
ALPHA = 0.1                       # P5X Checkpoint A: the 0.2 half-width rule
W_TARGET = ALPHA * SLACK_R        # 0.2
LEDGER = {"B_cover": 0.25, "B_candidate": 0.20, "B_kernel": 0.20,
          "B_other": 0.20, "B_rounding": 0.05, "B_interval": 0.05}
RESERVE_FRACTION = 1.0 - sum(LEDGER.values())          # 0.05, non-redistributable
LOCAL_GATE_COMPONENTS = ("B_candidate", "B_kernel", "B_interval", "B_rounding")
C_SR_QUARTER = 187.7472                                # Gate-2B, e = 1/4
C_SR_ZERO = 1205.9371382854872                         # Gate-2B, e = 0
C_SR_CERTIFIED_CAP = 25000 / 19                        # certified SR component
N_PANELS = 30                                          # n_z + 2, n_z = 28 (Gate-1/2B)
E_ABS_RAW = 0.7978845608                               # E|raw| = sqrt(2/pi), upper
PATCH = (17, 11); GRID = 64; E_NUM, E_DEN = 1, 4
DEGREE = 8; CAND_DEGREE = 16
PRECISIONS = (256, 384, 512)
EPS_P1 = arb(1) / arb(1000)
P1_TARGET = arb("1e-9")
GATE2A_NZ = 28
MAX_COMPLEXITY_SCORE = 100_000
TIMING_REPEATS = 5

B_ABS = {k: v * W_TARGET for k, v in LEDGER.items()}
LOCAL_GATE_BUDGET = sum(B_ABS[k] for k in LOCAL_GATE_COMPONENTS)          # 0.100
W_PANEL_MAX = LOCAL_GATE_BUDGET / (0.5 * C_SR_QUARTER * N_PANELS)        # 3.5511e-5
DELTA_CANDIDATE_MAX = 2 * B_ABS["B_candidate"] / (C_SR_QUARTER * E_ABS_RAW)  # 5.3411e-4


def direction_audit():
    """C_SR must be an UPPER bound on ||(I-K)^{-1}||, cross-checked and monotone."""
    cov = json.loads((ROOT / "level4/closure_proofs/p5y_gate2b_sr_cover/results/"
                      "sr_cover.json").read_text())
    rep = cov["representative"]
    seq = [rep[k]["C_SR"] for k in ("0", "1/4", "1/2", "1", "2", "e_star")]
    return {"type": "UPPER",
            "justification": "C = min_t t / H_t(0) with H_t a LOWER Bellman envelope of "
                             "the hit probability; a lower bound on hitting gives an upper "
                             "bound on sup_x E_x[tau] = ||(I-K_e)^{-1}||_inf",
            "C_SR_0": C_SR_ZERO, "certified_cap": C_SR_CERTIFIED_CAP,
            "cross_check_le_certified": bool(C_SR_ZERO <= C_SR_CERTIFIED_CAP),
            "monotone_decreasing_in_e": bool(seq == sorted(seq, reverse=True)),
            "sequence": seq,
            "PASS": bool(C_SR_ZERO <= C_SR_CERTIFIED_CAP and seq == sorted(seq, reverse=True))}


def acceptance_precondition(eps_cand, budget=None):
    b = DELTA_CANDIDATE_MAX if budget is None else budget
    return {"eps_cand": float(eps_cand), "delta_candidate_max": b,
            "ratio": float(eps_cand) / b,
            "PASS": bool(float(eps_cand) <= b)}


def representation_guard(cands):
    rows = []
    for name, c in cands.items():
        dp = len(c) - 1
        dm = max(len(r) - 1 for r in c)
        zd = CAND_DEGREE * DEGREE
        rows.append({"object": name, "deg_a": dp, "deg_b": dm,
                     "terms": sum(1 for r in c for x in r),
                     "composed_z_degree": zd,
                     "score": (dp + 1) * (dm + 1) * (zd + 1)})
    mx = max(max(r["deg_a"], r["deg_b"]) for r in rows)
    tot = max(r["score"] for r in rows)
    return {"rows": rows, "max_bidegree": mx, "score_per_composition": tot,
            "budget": MAX_COMPLEXITY_SCORE,
            "no_high_degree_object": bool(mx <= CAND_DEGREE),
            "PASS": bool(mx <= CAND_DEGREE and tot <= MAX_COMPLEXITY_SCORE)}


def run_cell(bits, cand, eps_cand, geo, e, h_z, tag):
    with workprec(bits):
        core_lo, core_hi = geo["core"]
        z_c = (core_lo + core_hi) / arb(2)
        up_c = (geo["yp"][0] + geo["yp"][1]) / arb(2) + z_c - rational(1, 2)
        um_c = (geo["ym"][0] + geo["ym"][1]) / arb(2) - z_c - rational(1, 2)
        a_p = L.softplus_taylor(up_c, DEGREE); a_m = L.softplus_taylor(um_c, DEGREE)
        comp_deg = CAND_DEGREE * DEGREE
        N = L.centred_gaussian_moments(z_c - h_z, z_c + h_z, z_c, e, comp_deg)
        M = L.softplus_derivative_bound_tight(DEGREE + 1)
        H_used = h_z + (geo["yp"][1] - geo["yp"][0]) / arb(2)
        E_used = M * (H_used ** (DEGREE + 1)) / arb(math.factorial(DEGREE + 1))
        comp = L.compose_candidate(cand, a_p, a_m, comp_deg + 1)
        cl = list(comp)
        acc = arb(0)
        for k, ck in enumerate(cl[: len(N)]):
            acc += ck * N[k]
        sup_g = sum(abs(c) for row in cand for c in row)
        rem_width = float((arb(CAND_DEGREE) * arb(2) * E_used * N[0].abs_upper()
                           * sup_g).upper())
        rad = float(acc.rad()); ab = float(acc.abs_upper())
        N0 = float(N[0].abs_upper())
        cand_term = float(eps_cand) * N0
        w_panel = rem_width + rad + cand_term
        p2_old = (float((arb(0, arb(rem_width)) + acc).rad() / acc.abs_upper())
                  if ab > 0 else float("inf"))
        dig_av = bits * math.log10(2)
        dig_keep = -math.log10(rad / ab) if (ab > 0 and rad > 0) else float("inf")
        times = []
        for _ in range(TIMING_REPEATS):
            tt = time.process_time()
            c2 = L.compose_candidate(cand, a_p, a_m, comp_deg + 1)
            s = arb(0)
            for k, ck in enumerate(list(c2)[: len(N)]):
                s += ck * N[k]
            times.append(time.process_time() - tt)
        tot = w_panel if w_panel > 0 else 1e-300
        return {"object": tag, "bits": bits,
                "acc_abs": ab, "acc_enclosure": ball_record(acc),
                "eps_cand": float(eps_cand),
                "err_kernel_rem_width": rem_width,
                "err_interval_radius": rad,
                "err_candidate_propagated": cand_term,
                "w_panel_total_ABS": w_panel,
                "w_panel_max_ABS": W_PANEL_MAX,
                "budget_ratio": w_panel / W_PANEL_MAX,
                "ABS_PASS": bool(w_panel <= W_PANEL_MAX),
                "share_kernel": rem_width / tot, "share_interval": rad / tot,
                "share_candidate": cand_term / tot,
                "P2_old_DIAGNOSTIC_ONLY": p2_old,
                "digits_lost": dig_av - dig_keep if dig_keep != float("inf") else 0.0,
                "E_d": float(E_used.upper()),
                "P1_repaired_pass": bool(E_used <= (arb(1) - EPS_P1) * P1_TARGET),
                "t_compose_median": statistics.median(times),
                "t_spread": (max(times) - min(times)) / statistics.median(times)}


def run_pilot(candidate_budget=None, panel_budget=None):
    """Enforced order.  Returns as soon as a stage fails; the grid is the LAST stage."""
    out = {"stages_run": []}
    with workprec(512):
        A, b_sr, c_sr = G2DM.sr_constants()
        e = rational(E_NUM, E_DEN)
        geo = L.patch_geometry(*PATCH, grid=GRID)
        core_lo, core_hi = geo["core"]
        patch_half = (geo["yp"][1] - geo["yp"][0]) / arb(2)
        M = L.softplus_derivative_bound_tight(DEGREE + 1)
        target = (arb(1) - EPS_P1) * P1_TARGET
        H_max = ((target * arb(math.factorial(DEGREE + 1)) / M).log() / arb(DEGREE + 1)).exp()
        h_z = arb(float((H_max - patch_half).lower()))
        n_z = int(math.ceil(float(((core_hi - core_lo) / (arb(2) * h_z)).upper())))
        cand1, eps1, det1 = G2DM.build_hhat1(e, b_sr, c_sr)
    out["p1_repair"] = {"eps_P1": float(EPS_P1), "n_z": n_z,
                        "n_z_expected": GATE2A_NZ,
                        "panel_count_unchanged": bool(n_z == GATE2A_NZ),
                        "PASS": bool(n_z == GATE2A_NZ)}

    out["stages_run"].append("direction_audit")
    out["direction_audit"] = direction_audit()
    if not out["direction_audit"]["PASS"]:
        out["decision"] = "SR_METRIC_FAIL_NO_JUSTIFIED_METRIC"; return out

    out["stages_run"].append("acceptance_precondition")
    out["acceptance_precondition"] = acceptance_precondition(eps1, candidate_budget)
    if not out["acceptance_precondition"]["PASS"]:
        out["decision"] = "SR_METRIC_FAIL_CANDIDATE"; return out

    out["stages_run"].append("representation_guard")
    ctrl = unit_candidate()
    with workprec(512):
        bf, cf = float(b_sr), float(c_sr)
    cand2 = G2DM.build_hhat2(E_NUM / E_DEN, bf, cf, 256)
    out["representation_guard"] = representation_guard(
        {"hhat_1": cand1, "hhat_2": cand2, "unit_candidate": ctrl})
    if not out["representation_guard"]["PASS"]:
        out["decision"] = "SR_METRIC_FAIL_ARCHITECTURE"; return out

    out["stages_run"].append("precision_grid")
    pmax = W_PANEL_MAX if panel_budget is None else panel_budget
    cells = {}
    for name, c, eps in (("hhat_1", cand1, eps1),
                         ("hhat_2_probe", cand2, arb(0)),
                         ("unit_candidate_control", ctrl, arb(0))):
        cells[name] = [run_cell(b, c, eps, geo, e, h_z, name) for b in PRECISIONS]
        for cell in cells[name]:
            cell["w_panel_max_ABS"] = pmax
            cell["budget_ratio"] = cell["w_panel_total_ABS"] / pmax
            cell["ABS_PASS"] = bool(cell["w_panel_total_ABS"] <= pmax)
    out["cells"] = cells
    sel = next((c["bits"] for c in cells["hhat_1"]
                if c["ABS_PASS"] and c["P1_repaired_pass"]), None)
    out["selected_safe_precision"] = sel
    out["decision"] = ("SR_METRIC_PASS_ABSOLUTE" if sel else "SR_METRIC_FAIL_CANDIDATE")
    return out


def main():
    t_all = time.time(); c0 = time.process_time()
    out = {"schema": "rebaseguard.p5y.gate2e.srmetric.v1", "binding": False,
           "pilot": "PILOT-SR-METRIC",
           "generated_utc": datetime.now(timezone.utc).isoformat(),
           "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                        capture_output=True, text=True).stdout.strip(),
           "gate2d_remains": "SR_REALCANDIDATE_FAIL_REPRESENTATION",
           "metric": {"scientific_target": "R_MAX_LT_2", "type": "ABSOLUTE",
                      "boundary": BOUNDARY, "slack_R": SLACK_R, "alpha": ALPHA,
                      "w_target": W_TARGET,
                      "ledger_fractions": LEDGER, "ledger_absolute": B_ABS,
                      "reserve_fraction": RESERVE_FRACTION,
                      "local_gate_components": list(LOCAL_GATE_COMPONENTS),
                      "local_gate_budget": LOCAL_GATE_BUDGET,
                      "C_SR_quarter": C_SR_QUARTER, "n_panels": N_PANELS,
                      "E_abs_raw": E_ABS_RAW,
                      "w_panel_max": W_PANEL_MAX,
                      "delta_candidate_max": DELTA_CANDIDATE_MAX,
                      "derivation_inputs_all_predate_gate2d": True,
                      "scale_aware_fallback_invoked": False,
                      "fallback_rejected_reason":
                          "P2_rel <= 1e-8 * max(1,|acc|) mixes a dimensionless "
                          "quantity with one carrying the panel integral's units"},
           "frozen": {"patch": list(PATCH), "grid": GRID, "e": f"{E_NUM}/{E_DEN}",
                      "degree": DEGREE, "candidate_bidegree": [CAND_DEGREE, CAND_DEGREE],
                      "precisions": list(PRECISIONS), "timing_repeats": TIMING_REPEATS}}
    res = run_pilot()
    out.update(res)
    # candidate identity against Gate-2D
    g2d = json.loads((G2D / "results" / "sr_realcandidate.json").read_text())
    out["candidate_identity_vs_gate2d"] = {
        "gate2d_eps_cand": g2d["genuine_candidate"]["eps_cand"],
        "this_gate_eps_cand": out["acceptance_precondition"]["eps_cand"],
        "identical": bool(abs(g2d["genuine_candidate"]["eps_cand"]
                              - out["acceptance_precondition"]["eps_cand"]) < 1e-18),
        "rebuilt_by_importing_gate2d_module": True, "refitted": False}
    if "cells" in out:
        out["absolute_vs_relative_demonstration"] = {
            "hhat_1": {"w_panel_total_ABS": out["cells"]["hhat_1"][0]["w_panel_total_ABS"],
                       "P2_old": out["cells"]["hhat_1"][0]["P2_old_DIAGNOSTIC_ONLY"],
                       "acc_abs": out["cells"]["hhat_1"][0]["acc_abs"]},
            "unit_candidate": {"w_panel_total_ABS": out["cells"]["unit_candidate_control"][0]["w_panel_total_ABS"],
                               "P2_old": out["cells"]["unit_candidate_control"][0]["P2_old_DIAGNOSTIC_ONLY"],
                               "acc_abs": out["cells"]["unit_candidate_control"][0]["acc_abs"]}}
        a = out["absolute_vs_relative_demonstration"]
        a["absolute_ratio_h1_over_unit"] = (a["hhat_1"]["w_panel_total_ABS"]
                                            / a["unit_candidate"]["w_panel_total_ABS"])
        a["relative_P2_ratio_h1_over_unit"] = (a["hhat_1"]["P2_old"]
                                               / a["unit_candidate"]["P2_old"])
    cpu = time.process_time() - c0
    out["runtime"] = {"wall_seconds": time.time() - t_all, "cpu_seconds": cpu,
                      "cpu_hours": cpu / 3600.0, "cap_cpu_seconds": 540,
                      "within_cap": bool(cpu <= 540),
                      "peak_rss_mib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 * 1024)}
    out["GATE2E_DECISION"] = out.pop("decision")
    (HERE / "results" / "sr_metric.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: out[k] for k in
                      ("metric", "stages_run", "direction_audit", "p1_repair",
                       "acceptance_precondition", "representation_guard",
                       "candidate_identity_vs_gate2d",
                       "absolute_vs_relative_demonstration",
                       "selected_safe_precision", "GATE2E_DECISION", "runtime")
                      if k in out}, indent=1, default=str))


if __name__ == "__main__":
    main()
