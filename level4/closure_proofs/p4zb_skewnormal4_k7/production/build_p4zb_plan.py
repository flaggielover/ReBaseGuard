#!/usr/bin/env python3
"""Derive and freeze the P4ZB plan.  Four cells only."""
from __future__ import annotations
import hashlib, json, subprocess
from pathlib import Path

NS = Path(__file__).resolve().parent.parent
REPO = NS.parent.parent.parent
P4 = NS.parent / "p4_theory_generalization"
P4Z = NS.parent / "p4z_location_family_feasibility"
P4ZA = NS.parent / "p4za_fullscope_closure"

LADDER = (0.1, 0.05, 0.025, 0.0125)
FROZEN_PAIR = (0.05, 0.025)
LADDER_BLOCKS = 40
BLOCKS = 200
SEEDS = {"rb_score": 4390001, "rb_map": 4390002, "fd_ladder": 4390003}


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*a): return subprocess.run(("git","-C",str(REPO))+a,capture_output=True,text=True,check=True).stdout.strip()


def main() -> int:
    aud = json.loads((NS/"results"/"p4zb_starting_audit.json").read_text())
    zaplan = json.loads((P4ZA/"production"/"p4za_campaign_plan.json").read_text())
    prot = json.loads((P4/"configs"/"P4_PROTOCOL.json").read_text())
    tgt = aud["target_configuration"]
    assert tgt["id"] == "frozen/cusum@5/skewnormal4"

    plan = {
        "schema": "rebaseguard.p4zb-campaign-plan.v1",
        "derived_from": {
            "p4zb_starting_audit_sha256": sha(NS/"results"/"p4zb_starting_audit.json"),
            "ladder_study_sha256": sha(NS/"results"/"ladder_study.json"),
            "p4za_plan_sha256": sha(P4ZA/"production"/"p4za_campaign_plan.json"),
            "p4_protocol_sha256": sha(P4/"configs"/"P4_PROTOCOL.json"),
            "note": "no value is taken from a prompt"},
        "scope_lock": {
            "configuration": tgt["id"], "m": [1,2,3,5], "cells": 4,
            "cells_not_rerun": 92,
            "cells_not_rerun_reason":
                "44 authored by P4Z and 48 by P4ZA, all COVERED_PASS on full "
                "evidence; P4ZB reruns nothing that already has a governed "
                "disposition"},
        "configuration": {
            "id": tgt["id"], "layer": tgt["layer"],
            "detector_kind": tgt["detector_kind"], "threshold": tgt["threshold"],
            "detector": tgt["detector"], "family": tgt["family"],
            "max_steps": tgt["max_steps"],
            "block_paths": tgt["block_paths"],      # unchanged from P4ZA
            "blocks": BLOCKS, "ladder_blocks": LADDER_BLOCKS,
            "m_grid": [1,2,3,5],
            "seed_rb_score": SEEDS["rb_score"],
            "seed_rb_map": SEEDS["rb_map"],
            "seed_fd_ladder": SEEDS["fd_ladder"]},
        "fd_ladder": {
            "rungs": list(LADDER),
            "frozen_scientific_pair": list(FROZEN_PAIR),
            "estimator_unchanged":
                "Route B remains the frozen per-batch Richardson at (0.05, "
                "0.025). P4ZB changes only how its TRUNCATION RESIDUAL is "
                "bounded, exactly as P4ZA did.",
            "truncation_rule":
                "T_B = |R(0.05,0.025) - R(0.025,0.0125)|, the standard adjacent-"
                "pair Richardson error estimate, rounded outward. Same FORM as "
                "P4ZA's rule -- adjacent pairs, raw difference, no divisor -- "
                "with the single change that the reference neighbour is the "
                "FINER pair rather than the coarser one.",
            "why_the_finer_neighbour":
                "The residual of R(0.05,0.025) must be estimated against a MORE "
                "accurate value, not a less accurate one. Under the validated "
                "h^4 model the coarse neighbour differs from the frozen pair by "
                "15x the residual it stands for, while the fine neighbour "
                "differs by 0.9375x it. P4ZA declared that 15x in advance as a "
                "deliberate conservatism; P4ZB removes it by changing WHICH "
                "MEASUREMENT is used, not by applying an algebraic divisor.",
            "model_dependence":
                "NONE. The rule is the standard empirical estimate and does not "
                "assume the h^4 relation. The h^4 model is reported as a "
                "diagnostic only.",
            "noise_is_conservative":
                "The (0.025,0.0125) rung pair has measured SNR ~2.5, so T_B "
                "carries Monte Carlo noise. Noise inflates |difference| in "
                "expectation, which makes the K7 threshold HARDER to satisfy, "
                "not easier. The ladder block count is left at P4ZA's 40 rather "
                "than raised, so this conservatism is retained.",
            "rung_0_00625_excluded":
                "measured SNR 0.0-0.1: the paired difference is consistent with "
                "zero, so the rung carries no information and would only add "
                "noise"},
        "thresholds": {
            "relative": prot["gates"]["correspondence_relative_limit"],
            "z": prot["gates"]["correspondence_z_limit"],
            "r_star": zaplan["thresholds"]["r_star"],
            "fd_ladder_relative_max": zaplan["thresholds"]["fd_ladder_relative_max"],
            "top1_share_max": zaplan["thresholds"]["top1_share_max"],
            "top5_share_max": zaplan["thresholds"]["top5_share_max"],
            "source": "frozen P4 protocol and the P4ZA plan; NONE changed",
            "any_threshold_changed_by_p4zb": False},
        "fixed_policy": {
            "blocks_per_route": BLOCKS, "ladder_blocks": LADDER_BLOCKS,
            "adaptive": False, "top_ups_permitted": 0,
            "path_count_may_increase_during_run": False,
            "block_paths_unchanged_from_p4za": True},
        "budget": {"total_cpu_cap_hours": 4.5,
                   "borrowed_from_p4za_cap": False,
                   "cost_bearing_calibration_included": True,
                   "ladder_study_cpu_seconds": json.loads((NS/"results"/"ladder_study.json").read_text())["cpu_seconds"]},
        "execution": {"workers": 1, "blas_threads": 1},
        "runtime_contract_reused_from_p4z": True,
        "runtime_hash": json.loads((P4Z/"production"/"mac_runtime_contract.json").read_text())["runtime_hash"],
    }
    seeds = [SEEDS[k] for k in SEEDS]
    zas = {s for c in zaplan["configurations"] for s in
           (c["seed_rb_score"],c["seed_rb_map"],c["seed_fd_ladder"])}
    zs = {s for c in json.loads((P4Z/"production"/"campaign_plan.json").read_text())["configurations"]
          for s in (c["seed_rb_score"],c["seed_rb_map"],c["seed_fd_ladder"])}
    assert len(set(seeds))==3
    assert not set(seeds)&zas and not set(seeds)&zs
    assert not set(seeds)&set(prot["master_seeds"].values())
    assert 4290001 not in seeds, "must differ from the ladder-study seed"

    out = NS/"production"/"p4zb_campaign_plan.json"
    out.write_text(json.dumps(plan,indent=2,sort_keys=True)+"\n")
    print(f"scope: {plan['scope_lock']['configuration']} m={plan['scope_lock']['m']} "
          f"({plan['scope_lock']['cells']} cells)")
    print(f"ladder {LADDER}, frozen pair {FROZEN_PAIR}, T_B from the FINER neighbour")
    print(f"block_paths {tgt['block_paths']:,} x {BLOCKS} blocks; ladder {LADDER_BLOCKS} blocks")
    print(f"K7 limit {plan['thresholds']['fd_ladder_relative_max']} (unchanged)  cap {plan['budget']['total_cpu_cap_hours']} CPU-h")
    print(f"-> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
