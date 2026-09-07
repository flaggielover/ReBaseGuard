#!/usr/bin/env python3
"""Derive and freeze the P4ZA campaign plan from artifacts.

Nothing here is taken from a prompt.  The cells come from the P4Z adjudication,
the thresholds from the frozen P4 protocol, and the per-configuration variance
from P4Z's Stage-0 measurements -- which are PRECISION statistics, the class of
information the frozen K3 trigger discipline explicitly permits a sizing rule to
read.  No discrepancy, z, or gate outcome enters this file.
"""
from __future__ import annotations
import hashlib, json, math, subprocess
from pathlib import Path

NS = Path(__file__).resolve().parent.parent
REPO = NS.parent.parent.parent
P4 = NS.parent / "p4_theory_generalization"
P4Z = NS.parent / "p4z_location_family_feasibility"

R_STAR = 0.010823063
TARGET_REL_SE = R_STAR          # the FROZEN precondition itself
SAFETY_VARIANCE = 4.0           # expected achieved relSE = r*/2
BLOCKS = 200
LADDER = (0.1, 0.05, 0.025)     # frozen after the Phase-5 calibration
LADDER_BLOCKS = 40
FD_STEPS = (0.05, 0.025)        # frozen P4 convention, unchanged
SEEDS = {"rb_score": 4190001, "rb_map": 4190002, "fd_ladder": 4190003}
SEED_STRIDE = 100


def sha(p: Path) -> str: return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*a): return subprocess.run(("git","-C",str(REPO))+a,capture_output=True,text=True,check=True).stdout.strip()


def main() -> int:
    adj = json.loads((P4Z/"production"/"adjudication.json").read_text())
    st = json.loads((P4Z/"production"/"run_state.json").read_text())
    zplan = json.loads((P4Z/"production"/"campaign_plan.json").read_text())
    prot = json.loads((P4/"configs"/"P4_PROTOCOL.json").read_text())
    zcfg = {c["id"]: c for c in zplan["configurations"]}
    s0 = st["stage0_configurations"]

    need = {}
    for c in adj["cells"]:
        if c["gate_result"] != "INCONCLUSIVE":
            continue
        cause = "K3" if any("below the frozen 200" in r for r in c["reasons"]) else "K7"
        e = need.setdefault(c["configuration"], {"cause": cause, "m": []})
        e["m"].append(c["m"])
        if e["cause"] != cause:
            raise SystemExit(f"mixed cause in {c['configuration']}")
    assert len(need) == 13, len(need)
    assert sum(len(v["m"]) for v in need.values()) == 52

    configs = []
    for i, (cid, info) in enumerate(sorted(need.items())):
        z = zcfg[cid]
        relsd = s0[cid]["measured_relative_sd_per_path"]
        n = SAFETY_VARIANCE * (relsd / TARGET_REL_SE) ** 2
        block_paths = math.ceil(n / BLOCKS)
        configs.append({
            "index": i, "id": cid, "layer": z["layer"],
            "detector_kind": z["detector_kind"], "threshold": z["threshold"],
            "detector": z["detector"], "family": z["family"],
            "max_steps": z["max_steps"], "regime": z["regime"],
            "p4za_cause": info["cause"], "m_affected": sorted(info["m"]),
            "calibration_relative_sd_per_path": relsd,
            "calibration_source": "P4Z Stage-0 measured per-path relative sd "
                                  "(a precision statistic)",
            "block_paths": block_paths, "blocks": BLOCKS,
            "paths": block_paths * BLOCKS,
            "expected_relative_se": relsd / math.sqrt(block_paths * BLOCKS),
            "seed_rb_score": SEEDS["rb_score"] + SEED_STRIDE * i,
            "seed_rb_map": SEEDS["rb_map"] + SEED_STRIDE * i,
            "seed_fd_ladder": SEEDS["fd_ladder"] + SEED_STRIDE * i,
            "ladder_blocks": LADDER_BLOCKS,
        })

    seeds = [s for c in configs for s in
             (c["seed_rb_score"], c["seed_rb_map"], c["seed_fd_ladder"])]
    assert len(set(seeds)) == len(seeds)
    assert not set(seeds) & set(prot["master_seeds"].values())
    zseeds = {s for c in zplan["configurations"] for s in
              (c["seed_rb_score"], c["seed_rb_map"], c["seed_fd_ladder"])}
    assert not set(seeds) & zseeds, "P4ZA seeds must be disjoint from P4Z's"

    plan = {
        "schema": "rebaseguard.p4za-campaign-plan.v1",
        "derived_from": {
            "p4z_adjudication_sha256": sha(P4Z/"production"/"adjudication.json"),
            "p4z_run_state_sha256": sha(P4Z/"production"/"run_state.json"),
            "p4z_campaign_plan_sha256": sha(P4Z/"production"/"campaign_plan.json"),
            "p4_protocol_sha256": sha(P4/"configs"/"P4_PROTOCOL.json"),
            "ladder_calibration_sha256": sha(NS/"results"/"ladder_calibration.json"),
            "note": "no value in this plan is taken from a prompt; the variance "
                    "calibration reads precision statistics only",
        },
        "scope": {
            "configurations": len(configs),
            "cells": sum(len(c["m_affected"]) for c in configs),
            "cells_by_cause": {"K3": sum(len(c["m_affected"]) for c in configs if c["p4za_cause"]=="K3"),
                               "K7": sum(len(c["m_affected"]) for c in configs if c["p4za_cause"]=="K7")},
            "p4z_cells_not_recomputed": 44,
            "p4z_cells_not_recomputed_reason":
                "already PASS on full P4Z evidence; P4ZA does not rerun a "
                "successful campaign",
        },
        "fixed_policy": {
            "blocks_per_route": BLOCKS, "ladder_blocks": LADDER_BLOCKS,
            "adaptive": False, "top_ups_permitted": 0,
            "path_count_may_increase_during_run": False,
            "sizing_rule": f"N = {SAFETY_VARIANCE} * (measured_relative_sd / {TARGET_REL_SE})^2",
            "target_relative_se": TARGET_REL_SE,
            "target_rationale":
                "r* IS the frozen precondition. P4Z additionally targeted "
                "0.0025, which for these configurations would cost 67.9 CPU-h. "
                "Targeting r* with a x4 variance safety factor gives an "
                "expected achieved relSE of r*/2 -- a 2x margin on the frozen "
                "precondition, not a knife edge.",
            "variance_safety_factor": SAFETY_VARIANCE,
        },
        "fd_ladder": {
            "rungs": list(LADDER),
            "frozen_scientific_pair": list(FD_STEPS),
            "coarse_rung_dropped": 0.2,
            "why_0_2_dropped":
                "measured implied order p = 0.88-1.39 between h=0.2 and h=0.1, "
                "against the O(h^2) prediction of 2; demonstrably outside the "
                "asymptotic regime at these operating points",
            "why_no_rung_below_0_025":
                "measured implied order collapses to -1.67..0.82 below h=0.025: "
                "the CRN difference is swamped by Monte Carlo noise, so a finer "
                "rung would add noise to T_B rather than information",
            "truncation_rule":
                "T_B = |R(0.1,0.05) - R(0.05,0.025)|, the standard Richardson "
                "error estimate (difference between successive extrapolations), "
                "rounded outward. The idealised h^4 relation would divide this "
                "by 15; P4ZA does NOT, which is a conservative factor of 15.",
            "adjacent_pairs_required": True,
            "p4z_defect_corrected":
                "P4Z's T_B differenced NON-adjacent pairs (0.2,0.1) vs "
                "(0.05,0.025), a factor 4 apart in h, and omitted the divisor. "
                "It measured how bad h=0.2 is, not how wrong R(0.05,0.025) is.",
        },
        "thresholds": {
            "relative": prot["gates"]["correspondence_relative_limit"],
            "z": prot["gates"]["correspondence_z_limit"],
            "r_star": R_STAR,
            "fd_ladder_relative_max": 0.02,
            "top1_share_max": 0.10, "top5_share_max": 0.30,
            "source": "frozen P4 protocol and the P4Z checkpoint; NONE changed",
            "any_threshold_changed_by_p4za": False,
        },
        "budget": {"total_cpu_cap_hours": 6.0,
                   "per_configuration_cpu_cap_hours": 2.0,
                   "borrowed_from_p4z_cap": False,
                   "note": "P4ZA does not borrow P4Z's unused cap"},
        "execution": {"workers": 1, "blas_threads": 1},
        "runtime_contract_reused_from_p4z": True,
        "runtime_hash": json.loads((P4Z/"production"/"mac_runtime_contract.json").read_text())["runtime_hash"],
        "configurations": configs,
    }
    out = NS/"production"/"p4za_campaign_plan.json"
    out.write_text(json.dumps(plan, indent=2, sort_keys=True)+"\n")
    tot = sum(c["paths"] for c in configs)
    print(f"{len(configs)} configurations, {plan['scope']['cells']} cells "
          f"({plan['scope']['cells_by_cause']})")
    print(f"total paths per route: {tot:,}   expected relSE = r*/2 = {R_STAR/2:.6f}")
    for c in configs:
        print(f"  {c['id']:32s} {c['p4za_cause']:3s} relsd={c['calibration_relative_sd_per_path']:7.3f} "
              f"block_paths={c['block_paths']:>9,d} exp_relSE={c['expected_relative_se']:.6f}")
    print(f"-> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
