#!/usr/bin/env python3
"""P4ZA Phase 0 -- independent reconstruction of the P4Z 96-cell universe.

Reads only P4Z and P4X result artifacts and the frozen P4 protocol.  Writes
nothing into any of them.  Fails loudly if the counts do not reconcile exactly.
"""
from __future__ import annotations
import hashlib, json, subprocess
from pathlib import Path

NS = Path(__file__).resolve().parent.parent
REPO = NS.parent.parent.parent
P4 = NS.parent / "p4_theory_generalization"
P4Z = NS.parent / "p4z_location_family_feasibility"
P4X_LEDGER = Path("/Users/suzhe/ReBaseGuard-p4x/level4/closure_proofs/"
                  "p4x_generalization_boundary/production/results/c2_cell_ledger.json")
P4X_PROD = P4X_LEDGER.parent / "production_results.json"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def git(*a): return subprocess.run(("git","-C",str(REPO))+a,capture_output=True,text=True,check=True).stdout.strip()


def main() -> int:
    adj = json.loads((P4Z/"production"/"adjudication.json").read_text())
    clo = json.loads((P4Z/"results"/"successor_closure.json").read_text())
    plan = json.loads((P4Z/"production"/"campaign_plan.json").read_text())
    prot = json.loads((P4/"configs"/"P4_PROTOCOL.json").read_text())
    px = json.loads(P4X_LEDGER.read_text())
    pxprod = json.loads(P4X_PROD.read_text())
    pxi = {(c["layer"],c["detector"],c["family"],c["m"]): c for c in px["cells"]}

    # --- reconciliation, fail closed -----------------------------------
    assert adj["cells_total"] == 96, adj["cells_total"]
    assert adj["counts"] == {"PASS":44,"FAIL":0,"INCONCLUSIVE":52}, adj["counts"]
    assert adj["unresolved_residue"]["by_result"] == {"PASS":8,"FAIL":0,"INCONCLUSIVE":0}
    assert len(pxi) == 96 and px["cells_failed"] == 0

    cells = []
    k3=k7=0
    for c in adj["cells"]:
        key = (c["layer"],c["detector"],c["family"],c["m"])
        h = pxi[key]
        if c["gate_result"] == "INCONCLUSIVE":
            if any("below the frozen 200" in r for r in c["reasons"]):
                cause, k3 = "K3", k3+1
            elif any("K7" in r for r in c["reasons"]):
                cause, k7 = "K7", k7+1
            else:
                raise SystemExit(f"unclassified INCONCLUSIVE cause: {c['reasons']}")
        else:
            cause = None
        thr = next(t for k,t in prot["layers"][c["layer"]]["detectors"]
                   if f"{k}@{t:g}" == c["detector"])
        row = {
            "layer": c["layer"], "detector": c["detector"], "detector_threshold": thr,
            "family": c["family"], "m": c["m"],
            "p4z_disposition": c["gate_result"],
            "p4z_inconclusive_cause": cause,
            "p4z_reasons": c["reasons"],
            "p4z_is_historical_residue": c["is_historically_unresolved"],
            "p4x_disposition": h["gate_result"],
            "p4x_relative_discrepancy": h["relative_discrepancy"],
            "p4x_z": h["z"],
            "p4x_route_a": {k: h["route_a"][k] for k in
                ("estimate","se","relative_se","paths","meets_r_star",
                 "stage2_paths","stage2_shards","precision_status")},
            "p4x_route_b": {k: h["route_b"][k] for k in
                ("estimate","se","relative_se","paths","meets_r_star",
                 "stage2_paths","stage2_shards","precision_status")},
        }
        if c["gate_result"] != "INCONCLUSIVE" or cause == "K7":
            # P4Z ran BOTH routes to the full frozen block count on these
            row["p4z_full_precision"] = {
                "rb_score": {k: c["rb_score"][k] for k in ("mean","mc_se","relative_se","blocks")},
                "rb_map": {k: c["rb_map"][k] for k in ("mean","mc_se","relative_se","blocks")},
                "relative_discrepancy": c["correspondence"]["relative_discrepancy"],
                "z_with_T_B": c["correspondence"]["z"],
                "T_B": c["correspondence"]["T_B"],
            }
        cells.append(row)

    assert k3 == 32 and k7 == 20, (k3, k7)

    doc = {
        "schema": "rebaseguard.p4za-starting-audit.v1",
        "result_bearing": False,
        "purpose": "independent reconstruction of the P4Z 96-cell universe and "
                   "the historical evidence covering its INCONCLUSIVE cells",
        "reconciliation": {
            "p4z_cells_total": adj["cells_total"],
            "p4z_counts": adj["counts"],
            "p4z_residue": adj["unresolved_residue"],
            "inconclusive_partition": {"K3": k3, "K7": k7, "total": k3+k7},
            "p4x_cells_total": len(pxi),
            "p4x_passed": px["cells_passed"],
            "p4x_failed": px["cells_failed"],
            "p4x_precondition_not_met": px["cells_precondition_not_met"],
            "all_counts_reconcile": True,
        },
        "parent_evidence": {
            "p4z_branch": "p4z-location-family-feasibility",
            "p4z_head": git("rev-parse","HEAD"),
            "p4z_verdict": clo["verdict"],
            "p4z_adjudication_sha256": sha(P4Z/"production"/"adjudication.json"),
            "p4z_closure_sha256": sha(P4Z/"results"/"successor_closure.json"),
            "p4z_campaign_plan_sha256": sha(P4Z/"production"/"campaign_plan.json"),
            "p4z_runtime_contract_sha256": sha(P4Z/"production"/"mac_runtime_contract.json"),
            "p4z_independent_adjudication_sha256": sha(P4Z/"production"/"independent_adjudication.json"),
            "p4x_cell_ledger_sha256": sha(P4X_LEDGER),
            "p4x_production_results_sha256": sha(P4X_PROD),
            "p4x_checkpoint_commit": pxprod["checkpoint_commit"],
            "p4_theorem_tree": git("rev-parse","HEAD:level4/closure_proofs/p4_theory_generalization"),
            "p4_protocol_sha256": sha(P4/"configs"/"P4_PROTOCOL.json"),
        },
        "p4x_obligation_status": {
            k: v["status"] for k, v in pxprod["obligations"].items()
        },
        "frozen_thresholds": {
            "relative": prot["gates"]["correspondence_relative_limit"],
            "z": prot["gates"]["correspondence_z_limit"],
            "r_star": 0.010823063,
            "fd_steps": prot["fd_steps"],
            "changed_by_p4za": False,
        },
        "cells": cells,
    }
    out = NS/"results"/"p4za_starting_audit.json"
    out.write_text(json.dumps(doc, indent=2, sort_keys=True)+"\n")
    print(f"96 cells reconstructed: {adj['counts']}")
    print(f"INCONCLUSIVE partition: K3={k3} K7={k7}")
    print(f"P4X disposition of the 52: "
          f"{ {r['p4x_disposition'] for r in cells if r['p4z_disposition']=='INCONCLUSIVE'} }")
    print(f"-> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
