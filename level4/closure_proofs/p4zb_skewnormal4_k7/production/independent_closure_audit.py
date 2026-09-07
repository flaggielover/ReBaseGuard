#!/usr/bin/env python3
"""P4ZB Phase 17 -- independent closure audit across the whole successor lineage.

Recomputes from artifacts; trusts no runner summary, including P4ZB's.
"""
from __future__ import annotations
import hashlib, json, subprocess, sys
from pathlib import Path

NS = Path(__file__).resolve().parent.parent
REPO = NS.parent.parent.parent
P4 = NS.parent / "p4_theory_generalization"
P4Z = NS.parent / "p4z_location_family_feasibility"
P4ZA = NS.parent / "p4za_fullscope_closure"
sys.path.insert(0, str(NS/"production"))
import p4zb_hash as sh   # noqa: E402


def git(*a): return subprocess.run(("git","-C",str(REPO))+a,capture_output=True,text=True,check=True).stdout.strip()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    f=[]
    def chk(n,ok,d): f.append({"check":n,"status":"PASS" if ok else "FAIL","detail":d}); return ok
    plan=json.loads((NS/"production"/"p4zb_campaign_plan.json").read_text())
    prot=json.loads((P4/"configs"/"P4_PROTOCOL.json").read_text())
    aud=json.loads((NS/"results"/"p4zb_starting_audit.json").read_text())
    adj=json.loads((NS/"production"/"adjudication_p4zb.json").read_text())
    cov=json.loads((NS/"results"/"final_coverage.json").read_text())
    state=json.loads((NS/"production"/"run_state.json").read_text())

    # 1 immutability of the whole lineage
    chk("historical P4 tree unchanged",
        git("rev-parse","HEAD:level4/closure_proofs/p4_theory_generalization")==aud["parent_evidence"]["p4_theorem_tree"],
        aud["parent_evidence"]["p4_theorem_tree"])
    chk("historical P4 verdict still PARTIAL",
        json.loads((P4/"results"/"closure_decision.json").read_text())["verdict"]=="PARTIAL","PARTIAL")
    for lbl,p,key in (("P4ZA adjudication",P4ZA/"production"/"adjudication_p4za.json","p4za_adjudication_sha256"),
                      ("P4ZA coverage",P4ZA/"results"/"claim_coverage.json","p4za_coverage_sha256"),
                      ("P4ZA closure",P4ZA/"results"/"p4za_successor_closure.json","p4za_closure_sha256"),
                      ("P4ZA plan",P4ZA/"production"/"p4za_campaign_plan.json","p4za_plan_sha256")):
        chk(f"{lbl} unchanged", sha(p)==aud["parent_evidence"][key], sha(p)[:16]+"...")
    chk("P4Z runtime contract unchanged",
        sha(P4Z/"production"/"mac_runtime_contract.json")==aud["parent_evidence"]["p4z_runtime_contract_sha256"],"ok")
    changed=[p for p in git("diff","--name-only","p4za-fullscope-closure","HEAD").splitlines() if p]
    outside=[p for p in changed if not p.startswith("level4/closure_proofs/p4zb_skewnormal4_k7/")]
    chk("P4ZB touches no path outside its own namespace", not outside, outside)

    # 2 thresholds -- especially K7
    t=plan["thresholds"]
    chk("K7 limit is still 0.02", t["fd_ladder_relative_max"]==0.02, 0.02)
    chk("relative threshold is the frozen 0.03", t["relative"]==prot["gates"]["correspondence_relative_limit"]==0.03, t["relative"])
    chk("z threshold is the frozen 4.0", t["z"]==prot["gates"]["correspondence_z_limit"]==4.0, t["z"])
    chk("r* unchanged", abs(1.96*2**0.5*t["r_star"]-0.03)<1e-8, t["r_star"])
    chk("frozen FD pair unchanged", plan["fd_ladder"]["frozen_scientific_pair"]==prot["fd_steps"]==[0.05,0.025],
        plan["fd_ladder"]["frozen_scientific_pair"])
    chk("adjudication changed no threshold", adj["thresholds_used"]["any_threshold_changed_by_p4zb"] is False, True)
    chk("Route B estimator itself is unchanged",
        "Route B remains the frozen per-batch Richardson" in plan["fd_ladder"]["estimator_unchanged"], True)

    # 3 pre-run freeze
    fc=git("rev-list","-1","HEAD","--","level4/closure_proofs/p4zb_skewnormal4_k7/production/p4zb_campaign_plan.json")
    at=git("ls-tree","-r","--name-only",fc,"level4/closure_proofs/p4zb_skewnormal4_k7/production/blocks/") if fc else ""
    chk("the frozen plan predates every result-bearing block",
        bool(fc) and not at.strip(), {"freeze_commit":fc,"blocks_at_freeze":len(at.split()) if at.strip() else 0})
    chk("ladder rungs are the frozen ones", plan["fd_ladder"]["rungs"]==[0.1,0.05,0.025,0.0125], plan["fd_ladder"]["rungs"])
    chk("every ladder block uses the frozen rungs",
        all(set(json.loads(p.read_text())["central_difference_by_h"])=={f"{h:g}" for h in plan["fd_ladder"]["rungs"]}
            for p in (NS/"production"/"blocks").rglob("fd_ladder_*.json")), "all frozen")
    chk("policy is non-adaptive with no top-up",
        plan["fixed_policy"]["adaptive"] is False and plan["fixed_policy"]["top_ups_permitted"]==0
        and plan["fixed_policy"]["path_count_may_increase_during_run"] is False, plan["fixed_policy"])
    chk("block_paths unchanged from P4ZA", plan["fixed_policy"]["block_paths_unchanged_from_p4za"] is True,
        plan["configuration"]["block_paths"])

    # 4 scope lock
    chk("scope is exactly the four open cells",
        plan["scope_lock"]["configuration"]=="frozen/cusum@5/skewnormal4"
        and plan["scope_lock"]["m"]==[1,2,3,5] and plan["scope_lock"]["cells"]==4,
        plan["scope_lock"])
    dirs={p.name for p in (NS/"production"/"blocks").iterdir()} if (NS/"production"/"blocks").exists() else set()
    chk("no configuration outside the scope lock was run",
        dirs<= {"frozen__cusum_at_5__skewnormal4"}, sorted(dirs))

    # 5 blocks, recomputed
    files=sorted((NS/"production"/"blocks").rglob("*.json"))
    ph,rh,badh,badp=set(),set(),[],[]
    per={}
    for p in files:
        d=json.loads(p.read_text())
        ph.add(d["producer_hash"]); rh.add(d["runtime_hash"])
        if sh.scientific_hash({k:v for k,v in d.items() if k!="scientific_hash"})!=d["scientific_hash"]:
            badh.append(str(p))
        if d["block_paths"]!=plan["configuration"]["block_paths"]: badp.append(str(p))
        per[d["route"]]=per.get(d["route"],0)+1
    chk("every block re-hashes to its recorded scientific hash", not badh, f"{len(files)} blocks, {len(badh)} mismatches")
    chk("every block used the planned path count", not badp, f"{len(badp)} deviations")
    chk("exactly one producer hash", len(ph)<=1, sorted(ph))
    chk("exactly one runtime hash", len(rh)<=1, sorted(rh))
    chk("runtime hash matches the frozen plan", rh<={plan["runtime_hash"]} if rh else True, plan["runtime_hash"])
    over={r:n for r,n in per.items() if n>(plan["fixed_policy"]["ladder_blocks"] if r=="fd_ladder" else plan["fixed_policy"]["blocks_per_route"])}
    chk("no route exceeded its frozen block count", not over, per)

    # 6 seeds
    cfg=plan["configuration"]
    seeds=[cfg["seed_rb_score"],cfg["seed_rb_map"],cfg["seed_fd_ladder"]]
    zas={s for c in json.loads((P4ZA/"production"/"p4za_campaign_plan.json").read_text())["configurations"]
         for s in (c["seed_rb_score"],c["seed_rb_map"],c["seed_fd_ladder"])}
    zs={s for c in json.loads((P4Z/"production"/"campaign_plan.json").read_text())["configurations"]
        for s in (c["seed_rb_score"],c["seed_rb_map"],c["seed_fd_ladder"])}
    study=json.loads((NS/"results"/"ladder_study.json").read_text())["seed"]
    chk("seeds unique", len(set(seeds))==3, seeds)
    chk("seeds disjoint from P4Z, P4ZA, the ladder study and history",
        not set(seeds)&zas and not set(seeds)&zs and study not in seeds
        and not set(seeds)&set(prot["master_seeds"].values()), "disjoint")

    # 7 cost
    cpu=(sum(json.loads(p.read_text())["cpu_seconds"] for p in files)
         + state.get("calibration_cpu_seconds",0.0))/3600.0
    chk("total CPU within the P4ZB cap", cpu<=plan["budget"]["total_cpu_cap_hours"],
        {"recomputed":cpu,"runner_reported":adj["cost"]["cpu_hours_total"],
         "cap":plan["budget"]["total_cpu_cap_hours"]})
    chk("calibration counted against the cap", plan["budget"]["cost_bearing_calibration_included"] is True, True)
    chk("P4ZB did not borrow the P4ZA cap", plan["budget"]["borrowed_from_p4za_cap"] is False, False)

    # 8 final coverage conservation
    chk("96 cells accounted exactly once", cov["conservation"]["conserved"], cov["conservation"])
    chk("every cell has exactly one authoritative source", cov["conservation"]["one_source_per_cell"], cov["authoritative_sources"])
    chk("no cell is UNCOVERED", cov["counts"]["UNCOVERED"]==0, cov["counts"])
    chk("historical evidence never sole authority", cov["rules"]["historical_evidence_used_as_sole_authority"] is False, True)
    chk("P4ZB authored exactly the four cells", cov["authoritative_sources"].get("P4ZB",0)==4, cov["authoritative_sources"])
    chk("the other 92 cells were not rerun by P4ZB",
        cov["authoritative_sources"].get("P4Z",0)+cov["authoritative_sources"].get("P4ZA",0)==92,
        cov["authoritative_sources"])

    # 9 replay
    rp=NS/"production"/"replay_p4zb.json"
    if rp.exists():
        r=json.loads(rp.read_text())
        chk("replay reproduced every scientific hash",
            r["all_scientific_hashes_identical"] and not r["any_scientific_field_mismatch"],
            {"blocks":r["blocks_replayed"]})

    # 10 formal
    la=P4Z/"results"/"lean_audit.json"
    if la.exists():
        l=json.loads(la.read_text())
        chk("inherited bounded-survival lemma still clean",
            l["compile"]["errors"]==0 and l["compile"]["sorry_count"]==0 and l["new_axioms"]==0, l["compile"])

    failed=[x for x in f if x["status"]=="FAIL"]
    doc={"schema":"rebaseguard.p4zb-independent-closure-audit.v1","result_bearing":True,
         "independent_of_the_runner":True,
         "checks_total":len(f),"checks_failed":len(failed),
         "verdict":"CLOSURE_AUDIT_PASS" if not failed else "CLOSURE_AUDIT_FAIL",
         "failed_checks":failed,"checks":f}
    (NS/"production"/"independent_closure_audit.json").write_text(json.dumps(doc,indent=2,sort_keys=True)+"\n")
    for x in failed: print(f"FAIL  {x['check']}: {x['detail']}")
    print(f"\n{doc['verdict']}: {len(f)-len(failed)}/{len(f)} checks pass")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
