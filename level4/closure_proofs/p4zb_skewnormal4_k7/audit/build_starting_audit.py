#!/usr/bin/env python3
"""P4ZB Phase 0 -- reconstruct the four open cells and the model that explains them.

Reads P4ZA and P4Z artifacts only.  Writes into none of them.  Fails closed if
the 4-cell reconstruction is not exact.
"""
from __future__ import annotations
import glob, hashlib, json, math, subprocess
from pathlib import Path
import numpy as np

NS = Path(__file__).resolve().parent.parent
REPO = NS.parent.parent.parent
P4 = NS.parent / "p4_theory_generalization"
P4Z = NS.parent / "p4z_location_family_feasibility"
P4ZA = NS.parent / "p4za_fullscope_closure"
TARGET = "frozen/cusum@5/skewnormal4"


def sha(p: Path) -> str: return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*a): return subprocess.run(("git","-C",str(REPO))+a,capture_output=True,text=True,check=True).stdout.strip()


def main() -> int:
    adj = json.loads((P4ZA/"production"/"adjudication_p4za.json").read_text())
    cov = json.loads((P4ZA/"results"/"claim_coverage.json").read_text())
    clo = json.loads((P4ZA/"results"/"p4za_successor_closure.json").read_text())
    plan = json.loads((P4ZA/"production"/"p4za_campaign_plan.json").read_text())
    prot = json.loads((P4/"configs"/"P4_PROTOCOL.json").read_text())

    assert cov["counts"] == {"COVERED_PASS":92,"COVERED_FAIL":0,"INCONCLUSIVE":4,"UNCOVERED":0}, cov["counts"]
    assert cov["conservation"]["conserved"] is True
    assert clo["verdict"] == "P4ZA_INCONCLUSIVE"
    open_cells = [c for c in adj["cells"] if c["gate_result"] == "INCONCLUSIVE"]
    assert len(open_cells) == 4
    assert {c["configuration"] for c in open_cells} == {TARGET}
    assert sorted(c["m"] for c in open_cells) == [1,2,3,5]

    cfg = next(c for c in plan["configurations"] if c["id"] == TARGET)
    d = P4ZA/"production"/"blocks"/TARGET.replace("/","__").replace("@","_at_")
    lad = [json.loads(Path(f).read_text()) for f in sorted(glob.glob(str(d/"fd_ladder_*.json")))]
    rungs = [0.1, 0.05, 0.025]

    cells = []
    for c in sorted(open_cells, key=lambda x: x["m"]):
        m = str(c["m"])
        D = {h: float(np.mean([x["central_difference_by_h"][f"{h:g}"][m] for x in lad])) for h in rungs}
        Dse = {h: float(np.std([x["central_difference_by_h"][f"{h:g}"][m] for x in lad], ddof=1)/math.sqrt(len(lad))) for h in rungs}
        A = np.array([[1,h**2,h**4] for h in rungs])
        G,a,b = np.linalg.solve(A, np.array([D[h] for h in rungs]))
        Rf = (4*D[0.025]-D[0.05])/3.0
        Rc = (4*D[0.05]-D[0.1])/3.0
        modelled_residual = -4*b*(0.025**4)
        cells.append({
            "configuration": TARGET, "m": c["m"],
            "p4za_gate_result": c["gate_result"], "p4za_reasons": c["reasons"],
            "p4za_relative_drift": c["fd_ladder"]["relative_drift"],
            "p4za_T_B": c["fd_ladder"]["T_B"],
            "p4za_empirical_order_p": c["fd_ladder"]["empirical_order_p"],
            "p4za_richardson_coarse_pair": c["fd_ladder"]["richardson_coarse_pair"],
            "p4za_richardson_frozen_pair": c["fd_ladder"]["richardson_frozen_pair"],
            "rb_score_relative_se": c["rb_score"]["relative_se"],
            "rb_map_relative_se": c["rb_map"]["relative_se"],
            "rb_score_mean": c["rb_score"]["mean"], "rb_map_mean": c["rb_map"]["mean"],
            "k5_ok": c["preconditions"]["K5_rb_score"] and c["preconditions"]["K5_rb_map"],
            "k6_ok": c["preconditions"]["K6_rb_score"] and c["preconditions"]["K6_rb_map"],
            "k7_ok": c["preconditions"]["K7_fd_ladder"],
            "central_differences": {f"{h:g}": D[h] for h in rungs},
            "central_difference_se": {f"{h:g}": Dse[h] for h in rungs},
            "three_point_fit": {"Gamma": float(G), "a": float(a), "b": float(b),
                                "b_over_a": float(b/a),
                                "note": "exact fit on 3 rungs; NOT an independent "
                                        "validation, which needs a 4th rung"},
            "modelled_residual_of_frozen_richardson": float(modelled_residual),
            "modelled_residual_relative": float(abs(modelled_residual)/abs(Rf)),
            "p4za_T_B_over_modelled_residual": float(abs(Rc-Rf)/abs(modelled_residual)),
        })

    doc = {
        "schema": "rebaseguard.p4zb-starting-audit.v1", "result_bearing": False,
        "scope_lock": {"only_configuration": TARGET, "only_m": [1,2,3,5],
                       "cells": 4, "everything_else": "historical/corroborating"},
        "reconciliation": {"p4za_coverage": cov["counts"],
            "p4za_conserved": cov["conservation"]["conserved"],
            "p4za_verdict": clo["verdict"],
            "open_cells": 4, "open_configuration": TARGET,
            "open_m": sorted(c["m"] for c in open_cells),
            "reconstruction_exact": True},
        "frozen_inputs_unchanged": {
            "k7_limit": adj["thresholds_used"]["fd_ladder_relative_max"],
            "relative": adj["thresholds_used"]["relative"],
            "z": adj["thresholds_used"]["z"],
            "r_star": adj["thresholds_used"]["r_star"],
            "fd_frozen_pair": prot["fd_steps"],
            "p4za_ladder_rungs": plan["fd_ladder"]["rungs"],
            "p4za_truncation_rule": plan["fd_ladder"]["truncation_rule"]},
        "parent_evidence": {
            "p4za_branch": "p4za-fullscope-closure",
            "p4za_head": git("rev-parse","HEAD"),
            "p4za_adjudication_sha256": sha(P4ZA/"production"/"adjudication_p4za.json"),
            "p4za_coverage_sha256": sha(P4ZA/"results"/"claim_coverage.json"),
            "p4za_closure_sha256": sha(P4ZA/"results"/"p4za_successor_closure.json"),
            "p4za_plan_sha256": sha(P4ZA/"production"/"p4za_campaign_plan.json"),
            "p4za_audit_sha256": sha(P4ZA/"production"/"independent_closure_audit.json"),
            "p4z_runtime_contract_sha256": sha(P4Z/"production"/"mac_runtime_contract.json"),
            "p4_theorem_tree": git("rev-parse","HEAD:level4/closure_proofs/p4_theory_generalization"),
            "p4_protocol_sha256": sha(P4/"configs"/"P4_PROTOCOL.json")},
        "target_configuration": {k: cfg[k] for k in
            ("id","layer","detector","detector_kind","threshold","family",
             "max_steps","block_paths","blocks","ladder_blocks","regime",
             "calibration_relative_sd_per_path")},
        "cells": cells,
    }
    (NS/"results"/"p4zb_starting_audit.json").write_text(json.dumps(doc,indent=2,sort_keys=True)+"\n")
    print(f"P4ZA coverage {cov['counts']}  verdict {clo['verdict']}")
    print(f"open cells: {len(open_cells)}, all {TARGET}, m={sorted(c['m'] for c in open_cells)}")
    print(f"K7 limit (unchanged): {doc['frozen_inputs_unchanged']['k7_limit']}")
    for c in cells:
        print(f"  m={c['m']}: drift={c['p4za_relative_drift']:.5f} p={c['p4za_empirical_order_p']:.3f} "
              f"b/a={c['three_point_fit']['b_over_a']:.2f} "
              f"modelled residual={c['modelled_residual_relative']*100:.4f}% "
              f"T_B/residual={c['p4za_T_B_over_modelled_residual']:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
