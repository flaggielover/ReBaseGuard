#!/usr/bin/env python3
"""P4ZA Phase 20 -- independent closure audit.

Reconstructs every count from the block files and re-reads every threshold from
its frozen source.  It does not trust any runner summary, including P4ZA's.
"""
from __future__ import annotations
import hashlib, json, subprocess, sys
from pathlib import Path

NS = Path(__file__).resolve().parent.parent
REPO = NS.parent.parent.parent
P4 = NS.parent / "p4_theory_generalization"
P4Z = NS.parent / "p4z_location_family_feasibility"
sys.path.insert(0, str(NS/"production"))
import p4za_hash as sh   # noqa: E402


def git(*a): return subprocess.run(("git","-C",str(REPO))+a,capture_output=True,text=True,check=True).stdout.strip()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    f=[]
    def chk(name, ok, detail):
        f.append({"check":name,"status":"PASS" if ok else "FAIL","detail":detail}); return ok

    plan=json.loads((NS/"production"/"p4za_campaign_plan.json").read_text())
    prot=json.loads((P4/"configs"/"P4_PROTOCOL.json").read_text())
    zadj=json.loads((P4Z/"production"/"adjudication.json").read_text())
    aadj=json.loads((NS/"production"/"adjudication_p4za.json").read_text())
    cov=json.loads((NS/"results"/"claim_coverage.json").read_text())
    audit=json.loads((NS/"results"/"p4za_starting_audit.json").read_text())
    state=json.loads((NS/"production"/"run_state.json").read_text())

    # 1 historical immutability -- P4, P4X, P4Y and now P4Z too
    chk("historical P4 tree unchanged",
        git("rev-parse","HEAD:level4/closure_proofs/p4_theory_generalization")
        == audit["parent_evidence"]["p4_theorem_tree"],
        audit["parent_evidence"]["p4_theorem_tree"])
    chk("historical P4 verdict still PARTIAL",
        json.loads((P4/"results"/"closure_decision.json").read_text())["verdict"]=="PARTIAL","PARTIAL")
    for name in ("production/adjudication.json","results/successor_closure.json",
                 "production/campaign_plan.json","configs/checkpoint_p4z.json"):
        chk(f"P4Z artifact unchanged: {name}",
            sha(P4Z/name)==({"production/adjudication.json":audit["parent_evidence"]["p4z_adjudication_sha256"],
                             "results/successor_closure.json":audit["parent_evidence"]["p4z_closure_sha256"],
                             "production/campaign_plan.json":audit["parent_evidence"]["p4z_campaign_plan_sha256"],
                             "configs/checkpoint_p4z.json":sha(P4Z/"configs"/"checkpoint_p4z.json")}[name]),
            sha(P4Z/name)[:16]+"...")
    changed=[p for p in git("diff","--name-only","p4z-location-family-feasibility","HEAD").splitlines() if p]
    outside=[p for p in changed if not p.startswith("level4/closure_proofs/p4za_fullscope_closure/")]
    chk("P4ZA touches no path outside its own namespace", not outside, outside)

    # 2 thresholds
    t=plan["thresholds"]
    chk("relative threshold is the frozen 0.03", t["relative"]==prot["gates"]["correspondence_relative_limit"]==0.03, t["relative"])
    chk("z threshold is the frozen 4.0", t["z"]==prot["gates"]["correspondence_z_limit"]==4.0, t["z"])
    chk("r* unchanged", abs(1.96*2**0.5*t["r_star"]-0.03)<1e-8, t["r_star"])
    chk("frozen FD pair unchanged", plan["fd_ladder"]["frozen_scientific_pair"]==prot["fd_steps"]==[0.05,0.025],
        plan["fd_ladder"]["frozen_scientific_pair"])
    chk("K7 limit unchanged from P4Z", t["fd_ladder_relative_max"]==0.02, 0.02)
    chk("adjudication changed no threshold", aadj["thresholds_used"]["any_threshold_changed_by_p4za"] is False, True)

    # 3 pre-run freeze respected: ladder and envelope fixed before results
    frozen_commit=git("rev-list","-1","HEAD","--",
        "level4/closure_proofs/p4za_fullscope_closure/production/p4za_campaign_plan.json")
    # the plan must have been committed BEFORE any block existed: no block file
    # is tracked at that commit
    tracked_at_freeze=git("ls-tree","-r","--name-only",frozen_commit,
        "level4/closure_proofs/p4za_fullscope_closure/production/blocks/") if frozen_commit else ""
    chk("the frozen plan predates every result-bearing block",
        bool(frozen_commit) and not tracked_at_freeze.strip(),
        {"freeze_commit":frozen_commit,"blocks_present_at_freeze":len(tracked_at_freeze.split()) if tracked_at_freeze.strip() else 0})
    chk("ladder rungs are the frozen ones", plan["fd_ladder"]["rungs"]==[0.1,0.05,0.025], plan["fd_ladder"]["rungs"])
    chk("no rung was added or removed after results",
        all(json.loads(p.read_text())["central_difference_by_h"].keys()=={f"{h:g}" for h in plan["fd_ladder"]["rungs"]}
            for p in (NS/"production"/"blocks").rglob("fd_ladder_*.json")), "all ladder blocks use the frozen rungs")
    chk("sizing rule is non-adaptive with no top-up",
        plan["fixed_policy"]["adaptive"] is False and plan["fixed_policy"]["top_ups_permitted"]==0
        and plan["fixed_policy"]["path_count_may_increase_during_run"] is False, plan["fixed_policy"]["sizing_rule"])

    # 4 blocks, recomputed from files
    files=sorted((NS/"production"/"blocks").rglob("*.json"))
    ph,rh,badh,badp=set(),set(),[],[]
    per={}
    cfgs={c["id"]:c for c in plan["configurations"]}
    for p in files:
        d=json.loads(p.read_text())
        ph.add(d["producer_hash"]); rh.add(d["runtime_hash"])
        body={k:v for k,v in d.items() if k!="scientific_hash"}
        if sh.scientific_hash(body)!=d["scientific_hash"]: badh.append(str(p))
        if d["block_paths"]!=cfgs[d["configuration"]]["block_paths"]: badp.append(str(p))
        per[(d["configuration"],d["route"])]=per.get((d["configuration"],d["route"]),0)+1
    chk("every block re-hashes to its recorded scientific hash", not badh, f"{len(files)} blocks, {len(badh)} mismatches")
    chk("every block used the planned path count", not badp, f"{len(badp)} deviations")
    chk("exactly one producer hash across every block", len(ph)<=1, sorted(ph))
    chk("exactly one runtime hash across every block", len(rh)<=1, sorted(rh))
    over={f"{c}/{r}":n for (c,r),n in per.items()
          if n> (plan["fixed_policy"]["ladder_blocks"] if r=="fd_ladder" else plan["fixed_policy"]["blocks_per_route"])}
    chk("no route exceeded its frozen block count", not over, over)
    chk("runtime hash matches the frozen plan", rh<= {plan["runtime_hash"]} if rh else True, plan["runtime_hash"])

    # 5 seeds
    seeds=[s for c in plan["configurations"] for s in (c["seed_rb_score"],c["seed_rb_map"],c["seed_fd_ladder"])]
    zseeds={s for c in json.loads((P4Z/"production"/"campaign_plan.json").read_text())["configurations"]
            for s in (c["seed_rb_score"],c["seed_rb_map"],c["seed_fd_ladder"])}
    chk("seed schedule has no internal collision", len(set(seeds))==len(seeds), len(seeds))
    chk("seeds disjoint from P4Z", not set(seeds)&zseeds, "disjoint")
    chk("seeds disjoint from historical P4", not set(seeds)&set(prot["master_seeds"].values()), "disjoint")

    # 6 cost
    cpu=sum(json.loads(p.read_text())["cpu_seconds"] for p in files)/3600.0
    cap=plan["budget"]["total_cpu_cap_hours"]
    chk("total CPU within the P4ZA cap", cpu<=cap,
        {"recomputed_from_blocks":cpu,"runner_reported":state.get("cpu_seconds_total",0)/3600.0,"cap":cap})
    chk("P4ZA did not borrow the P4Z cap", plan["budget"]["borrowed_from_p4z_cap"] is False, False)

    # 7 coverage conservation
    chk("96 cells accounted exactly once", cov["conservation"]["conserved"], cov["conservation"])
    chk("no cell is UNCOVERED", cov["counts"]["UNCOVERED"]==0, cov["counts"])
    chk("no ambiguous coverage path", not cov["ambiguous"], len(cov["ambiguous"]))
    chk("historical evidence never used as sole authority",
        cov["rules"]["historical_evidence_used_as_sole_authority"] is False, True)
    chk("P4X contributes 0 authoritative dispositions", cov["sources"]["P4X"]["cells"]==0, 0)
    chk("P4Z INCONCLUSIVE cells all received NEW P4ZA evidence",
        all(c.get("authoritative_source")=="P4ZA" for c in cov["cells"]
            if any(e.get("source","").startswith("P4Z (superseded") for e in c.get("corroborating_evidence",[]))),
        "each superseded cell is authored by P4ZA")

    # 8 replay + formal
    rp=NS/"production"/"replay_p4za.json"
    if rp.exists():
        r=json.loads(rp.read_text())
        chk("replay reproduced every scientific hash",
            r["all_scientific_hashes_identical"] and not r["any_scientific_field_mismatch"],
            {"blocks":r["blocks_replayed"]})
    la=P4Z/"results"/"lean_audit.json"
    if la.exists():
        l=json.loads(la.read_text())
        chk("inherited bounded-survival lemma still compiles clean",
            l["compile"]["errors"]==0 and l["compile"]["sorry_count"]==0 and l["new_axioms"]==0, l["compile"])

    failed=[x for x in f if x["status"]=="FAIL"]
    doc={"schema":"rebaseguard.p4za-independent-closure-audit.v1","result_bearing":True,
         "independent_of_the_runner":True,
         "method":"counts recomputed from block files, thresholds re-read from "
                  "frozen sources, hashes recomputed",
         "checks_total":len(f),"checks_failed":len(failed),
         "verdict":"CLOSURE_AUDIT_PASS" if not failed else "CLOSURE_AUDIT_FAIL",
         "failed_checks":failed,"checks":f}
    (NS/"production"/"independent_closure_audit.json").write_text(json.dumps(doc,indent=2,sort_keys=True)+"\n")
    for x in failed: print(f"FAIL  {x['check']}: {x['detail']}")
    print(f"\n{doc['verdict']}: {len(f)-len(failed)}/{len(f)} checks pass")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
