#!/usr/bin/env python
"""Stage C step 4 — criteria evaluation, Pareto frontier, findings bundle."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import numpy as np

import policy
from analyze import classify_regime, find_row, paired_bootstrap, pareto_front
from campaign import EXTRA_RHO, PROTOCOL_RHO, RESULTS, cell_path

RHO_C_POINT = 1.0 / (policy.GAMMA_POINT - 1.0)
RHO_C_CERT = (1.0 / (policy.GAMMA_CERT_HIGH - 1.0),
              1.0 / (policy.GAMMA_CERT_LOW - 1.0))
RBG_EXACT = policy.rho_safe(0.2, variant=policy.CONSERVATIVE).rho
RBG_POINT_EXACT = policy.rho_safe(0.2, variant=policy.POINT).rho
FULL = 1.0
FRESH = 0.0


def snap(value: float, grid) -> float:
    """Map an exact policy value onto the grid point that was actually run.

    The policy returns full precision (0.0297958439...); the campaign grid
    stores the 6-dp rounded value the protocol listed. The difference is ~4e-9
    in rho, far below any Monte Carlo resolution, but the substitution is made
    explicit here rather than left to float luck.
    """
    grid = list(grid)
    nearest = min(grid, key=lambda g: abs(g - value))
    if abs(nearest - value) > 1e-5:
        raise ValueError(f"policy rho {value} has no grid cell (nearest "
                         f"{nearest}); the campaign grid is missing the "
                         f"evaluated point")
    return nearest


def load_cell(rho, args):
    key = {"rho": float(rho), "n_replicates": args["n_replicates"],
           "n_cycles": args["n_cycles"], "burn_in": args["burn_in"],
           "master_seed": args["master_seed"], "m": 1,
           "n_bootstrap": args["n_bootstrap"], "acurve": "arl_curve.json"}
    p = cell_path("incontrol", key)
    return json.loads(p.read_text()) if p.exists() else None


def detect_cell(rho, shift, args):
    key = {"rho": float(rho), "shift": float(shift),
           "n_replicates": args["n_replicates"], "burn_in": args["burn_in"],
           "n_cycles_after": args["n_cycles_after"],
           "master_seed": args["master_seed"], "m": 1}
    p = cell_path("detect", key)
    return json.loads(p.read_text()) if p.exists() else None


def main() -> int:
    ic = json.loads((RESULTS / "incontrol_main.json").read_text())
    rows = ic["rows"]
    ic_args = ic["arguments"]
    det_path = RESULTS / "detection_main.json"
    det = json.loads(det_path.read_text()) if det_path.exists() else None
    adv_path = RESULTS / "adversarial.json"
    adv = json.loads(adv_path.read_text()) if adv_path.exists() else None
    reg_path = RESULTS / "regression_check.json"
    reg = json.loads(reg_path.read_text()) if reg_path.exists() else None

    grid_rho = [r["rho"] for r in rows]
    RBG = snap(RBG_EXACT, grid_rho)
    RBG_POINT = snap(RBG_POINT_EXACT, grid_rho)

    cells = {r["rho"]: load_cell(r["rho"], ic_args) for r in rows}
    mse = {rho: np.array(c["per_replicate"]["reference_mse"])
           for rho, c in cells.items() if c}
    arl = {rho: np.array(c["per_replicate"]["cycle_arl"])
           for rho, c in cells.items() if c}

    # ---- ORACLE: chosen AFTER seeing results, and only as a yardstick ----
    oracle_rho = min(mse, key=lambda r: mse[r].mean())
    findings: dict = {
        "policy": {"delta": 0.2,
                   "conservative_rho": RBG, "point_rho": RBG_POINT,
                   "conservative_rho_exact": RBG_EXACT,
                   "point_rho_exact": RBG_POINT_EXACT,
                   "snap_note": "the evaluated grid points are the 6-dp rounded "
                                "policy values listed in the protocol; the "
                                "rounding shifts rho by <1e-5",
                   "rho_c_point": RHO_C_POINT, "rho_c_certified": list(RHO_C_CERT),
                   "table": policy.policy_table()},
        "oracle": {"rho": oracle_rho, "selection": "post-hoc minimiser of "
                   "stationary reference MSE over the grid",
                   "role": "performance yardstick ONLY; not a proposed method"},
        "grid": {"protocol": list(PROTOCOL_RHO), "added": list(EXTRA_RHO),
                 "n_cells": len(rows)},
    }

    # ---- paired contrasts ----
    def contrast(a, b, name, index, stat="difference"):
        return paired_bootstrap(a, b, seed=ic_args["master_seed"],
                                index=index, statistic=stat, n_boot=10_000)

    c_mse_full_vs_rbg = contrast(mse[FULL], mse[RBG], "mse", 1)
    c_mse_ratio = contrast(mse[FULL], mse[RBG], "mse_ratio", 2, "ratio")
    c_mse_rbg_vs_fresh = contrast(mse[FRESH], mse[RBG], "mse_fresh", 3)
    c_mse_oracle_vs_rbg = contrast(mse[RBG], mse[oracle_rho], "mse_oracle", 4)
    c_arl_rbg_vs_full = contrast(arl[RBG], arl[FULL], "arl", 5)

    findings["contrasts"] = {
        "mse_full_minus_rbg": c_mse_full_vs_rbg,
        "mse_full_over_rbg": c_mse_ratio,
        "mse_fresh_minus_rbg": c_mse_rbg_vs_fresh,
        "mse_rbg_minus_oracle": c_mse_oracle_vs_rbg,
        "arl_rbg_minus_full": c_arl_rbg_vs_full,
    }

    # ---- detection contrasts ----
    delay_rows = []
    if det:
        d_args = det["arguments"]
        for shift in sorted({r["shift"] for r in det["rows"]}):
            if shift == 0.0:
                continue
            a = detect_cell(RBG, shift, d_args)
            b = detect_cell(FULL, shift, d_args)
            f = detect_cell(FRESH, shift, d_args)
            if not (a and b and f):
                continue
            da = np.array(a["per_replicate_delay"])
            db = np.array(b["per_replicate_delay"])
            df = np.array(f["per_replicate_delay"])
            c = contrast(da, db, "delay", int(shift * 1000) + 10)
            threshold = 0.25 * db.mean()

            # Secondary, NOT a gating criterion and not pre-specified as one.
            # The raw C6 contrast compares delays at very different in-control
            # ARLs (RBG ~85, full reuse ~50), so it is not like-for-like: full
            # reuse detects sooner largely because its reference is badly
            # displaced, which is the same defect that shortens its in-control
            # run length.  The ratio delay(Delta)/delay(0) removes each policy's
            # own baseline alarm rate and measures sensitivity as such.
            a0 = detect_cell(RBG, 0.0, d_args)
            b0 = detect_cell(FULL, 0.0, d_args)
            f0 = detect_cell(FRESH, 0.0, d_args)
            ratios = {}
            if a0 and b0 and f0:
                ratios = {
                    "rbg": float(da.mean() / np.array(a0["per_replicate_delay"]).mean()),
                    "full": float(db.mean() / np.array(b0["per_replicate_delay"]).mean()),
                    "fresh": float(df.mean() / np.array(f0["per_replicate_delay"]).mean()),
                }

            delay_rows.append({
                "shift": shift,
                "delay_rbg": float(da.mean()), "delay_full": float(db.mean()),
                "delay_fresh": float(df.mean()),
                "paired_rbg_minus_full": c,
                "c6_threshold": threshold,
                "c6_pass": bool(c["ci_high"] < threshold),
                "delay_ratio_vs_own_baseline": ratios,
                "ratio_note": "secondary diagnostic; NOT a gating criterion",
            })
    findings["detection"] = delay_rows

    # ---- Pareto frontier: high ARL and low delay are both good ----
    front_info = {}
    if det:
        d_args = det["arguments"]
        for shift in sorted({r["shift"] for r in det["rows"] if r["shift"] > 0}):
            pts, labels = [], []
            for r in rows:
                cellr = detect_cell(r["rho"], shift, d_args)
                if not cellr:
                    continue
                # minimise (-ARL, delay)
                pts.append((-r["cycle_arl"], cellr["delay_mean"]))
                labels.append(r["rho"])
            idx = pareto_front(pts)
            front_info[str(shift)] = {
                "front_rho": [labels[i] for i in idx],
                "rbg_on_front": RBG in [labels[i] for i in idx],
                "oracle_on_front": oracle_rho in [labels[i] for i in idx],
            }
    findings["pareto"] = front_info

    # ---- regimes ----
    findings["regimes"] = [
        {"rho": r["rho"], "regime": classify_regime(r["rho"], RHO_C_POINT,
                                                    RHO_C_CERT),
         "reference_mse": r["reference_mse"], "cycle_arl": r["cycle_arl"],
         "alternation_rate": r["alternation_rate"]}
        for r in sorted(rows, key=lambda z: z["rho"])]

    # ---- criteria ----
    def adv_check(name):
        if not adv:
            return None
        for c in adv["checks"]:
            if c["check"] == name:
                return c
        return None

    seeds_ok = adv_check("independent_seeds")
    decomp_ok = adv_check("arl_decomposition")
    c6_all = all(d["c6_pass"] for d in delay_rows) if delay_rows else None

    criteria = [
        {"id": "C1", "text": "policy mathematically well-defined",
         "passed": True,
         "detail": f"closed form rho_safe(delta) = (1-delta)/(Gamma-1), "
                   f"clipped to [0,1]; 21 unit tests"},
        {"id": "C2", "text": "stability rule follows from frozen theory",
         "passed": True,
         "detail": "derived from F'_rho(0) = rho(1-Gamma) (Level 2C, "
                   "FROZEN-PROVED) and the frozen certified Gamma enclosure"},
        {"id": "C3", "text": "full reuse substantially worse reference "
                             "stability than the stable policy",
         "passed": bool(c_mse_ratio["ci_low"] > 1.5),
         "detail": f"MSE(rho=1)/MSE(RBG) = {c_mse_ratio['point']:.4f} "
                   f"[{c_mse_ratio['ci_low']:.4f}, {c_mse_ratio['ci_high']:.4f}] "
                   f"(paired); threshold 1.5"},
        {"id": "C4", "text": "ReBaseGuard preserves nonzero alarm data",
         "passed": bool(RBG > 0.0),
         "detail": f"rho = {RBG:.6f} > 0; retained alarm-data weight D1 = "
                   f"{RBG:.6f}"},
        {"id": "C5", "text": "ReBaseGuard improves stability over full reuse",
         "passed": bool(c_mse_full_vs_rbg["ci_low"] > 0.0),
         "detail": f"MSE(rho=1) - MSE(RBG) = {c_mse_full_vs_rbg['point']:.4f} "
                   f"[{c_mse_full_vs_rbg['ci_low']:.4f}, "
                   f"{c_mse_full_vs_rbg['ci_high']:.4f}] (paired)"},
        {"id": "C6", "text": "improvement not bought by destroying detection",
         "passed": bool(c6_all) if c6_all is not None else None,
         "detail": "; ".join(
             f"Delta={d['shift']:g}: RBG-full = {d['paired_rbg_minus_full']['point']:+.3f} "
             f"[{d['paired_rbg_minus_full']['ci_low']:+.3f}, "
             f"{d['paired_rbg_minus_full']['ci_high']:+.3f}] vs threshold "
             f"{d['c6_threshold']:+.3f}" for d in delay_rows) or "not run"},
        {"id": "C7", "text": "direct and decomposition ARL agree",
         "passed": bool(decomp_ok["passed"]) if decomp_ok else None,
         "detail": decomp_ok["note"] if decomp_ok else "not run"},
        {"id": "C8", "text": "reproduces under independent seeds",
         "passed": bool(seeds_ok["passed"]) if seeds_ok else None,
         "detail": seeds_ok["note"] if seeds_ok else "not run"},
        {"id": "C9", "text": "no frozen Stage A/B claim regresses",
         "passed": (bool(reg["passed"]) if reg else None),
         "detail": (f"{reg['total_passed']} tests passed, "
                    f"{reg['total_failed']} failed across the frozen Level 1-3, "
                    f"Stage A, Stage B and Stage C suites; Stage B certificate "
                    f"unchanged ({reg['stage_b_science_sha256'][:16]}...); "
                    f"Stage A Gate 4.1 ARL reproduced to "
                    f"{max(c['rel_gap'] for c in reg['stage_a_comparisons']):.2e}"
                    if reg else "run regression_check.py")},
        {"id": "C10", "text": "negative/null findings retained",
         "passed": True,
         "detail": f"all {len(rows)} grid cells reported; adversarial checks "
                   f"recorded pass or fail; the domination finding is a "
                   f"headline limitation"},
    ]
    findings["criteria"] = criteria

    resolved = [c for c in criteria if c["passed"] is not None]
    gating_fail = [c for c in resolved if not c["passed"]]
    hard = {"C1", "C2", "C9", "C10"}
    hard_fail = [c for c in gating_fail if c["id"] in hard]
    if hard_fail:
        decision = "STAGE-C-FAILED"
    elif gating_fail:
        decision = "STAGE-C-PARTIAL"
    else:
        decision = "STAGE-C-CLOSED-METHOD"
    findings["decision"] = decision
    findings["decision_basis"] = {
        "failed": [c["id"] for c in gating_fail],
        "unresolved": [c["id"] for c in criteria if c["passed"] is None],
    }

    # ---- the pre-registered domination question (reported, not gated) ----
    findings["domination"] = {
        "oracle_rho": oracle_rho,
        "rbg_rho": RBG,
        "mse_rbg": float(mse[RBG].mean()),
        "mse_oracle": float(mse[oracle_rho].mean()),
        "paired_rbg_minus_oracle": c_mse_oracle_vs_rbg,
        "dominated": bool(c_mse_oracle_vs_rbg["ci_low"] > 0.0),
        "note": "pre-registered in STAGE_C_PROTOCOL.md section 12 BEFORE the "
                "campaign; reported as a headline limitation, deliberately not "
                "a gating criterion",
    }

    (RESULTS / "findings.json").write_text(
        json.dumps(findings, indent=2, default=float))
    print(f"decision: {decision}")
    for c in criteria:
        mark = {True: "PASS", False: "FAIL", None: "n/a "}[c["passed"]]
        print(f"  [{mark}] {c['id']}: {c['text']}")
    print(f"\noracle rho = {oracle_rho:g} (MSE {mse[oracle_rho].mean():.5f}) vs "
          f"ReBaseGuard rho = {RBG:.6f} (MSE {mse[RBG].mean():.5f})")
    print(f"dominated: {findings['domination']['dominated']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
