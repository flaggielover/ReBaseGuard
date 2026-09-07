#!/usr/bin/env python3
"""P4ZB four-cell adjudication.  Frozen criteria, applied mechanically."""
from __future__ import annotations
import json, math, sys
from pathlib import Path
import numpy as np

NS = Path(__file__).resolve().parent.parent
BLOCK_DIR = NS/"production"/"blocks"/"frozen__cusum_at_5__skewnormal4"
ROUND_DP = 12


def _up(v):
    if not math.isfinite(v): return v
    s=10**ROUND_DP
    return math.ceil(abs(v)*s)/s*(1.0 if v>=0 else -1.0)


def _blocks(route):
    return [json.loads(p.read_text()) for p in sorted(BLOCK_DIR.glob(f"{route}_*.json"))] if BLOCK_DIR.exists() else []


def _sum(docs,m):
    if len(docs)<2: return None
    v=np.array([d["block_mean"][str(m)] for d in docs],float)
    mean=float(v.mean()); se=float(v.std(ddof=1)/math.sqrt(v.size))
    dev=(v-mean)**2; tot=float(dev.sum()); o=np.sort(dev)[::-1]
    return {"mean":mean,"mc_se":se,"blocks":int(v.size),
            "relative_se":abs(se/mean) if mean else math.inf,
            "top1_share_of_block_variance":float(o[0]/tot) if tot>0 else 0.0,
            "top5_share_of_block_variance":float(o[:5].sum()/tot) if tot>0 else 0.0,
            "paths":int(sum(d["block_paths"] for d in docs)),
            "cpu_seconds":float(sum(d["cpu_seconds"] for d in docs))}


def _ladder(m, plan):
    docs=_blocks("fd_ladder")
    if len(docs)<2: return None
    r=plan["fd_ladder"]["rungs"]                       # 0.1, 0.05, 0.025, 0.0125
    frozen=f"{r[1]:g}/{r[2]:g}"                        # 0.05/0.025   -- the frozen pair
    finer=f"{r[2]:g}/{r[3]:g}"                         # 0.025/0.0125 -- the reference
    coarser=f"{r[0]:g}/{r[1]:g}"                       # 0.1/0.05     -- diagnostic only
    F=np.array([d["richardson_by_pair"][frozen][str(m)] for d in docs])
    N=np.array([d["richardson_by_pair"][finer][str(m)] for d in docs])
    C=np.array([d["richardson_by_pair"][coarser][str(m)] for d in docs])
    D={h:np.array([d["central_difference_by_h"][f"{h:g}"][str(m)] for d in docs]) for h in r}
    d1=(D[r[1]]-D[r[2]]).mean(); d2=(D[r[2]]-D[r[3]]).mean()
    t_b=abs(float(F.mean())-float(N.mean()))
    scale=max(abs(float(F.mean())),abs(float(N.mean())))
    return {"richardson_frozen_pair":float(F.mean()),
            "richardson_finer_neighbour":float(N.mean()),
            "richardson_coarser_neighbour":float(C.mean()),
            "frozen_pair":frozen,"reference_pair":finer,"diagnostic_pair":coarser,
            "T_B":t_b,"relative_drift":t_b/scale if scale>0 else math.inf,
            "empirical_order_p":math.log2(d1/d2) if d2 and d1/d2>0 else float("nan"),
            "p4za_style_coarse_drift":abs(float(C.mean())-float(F.mean()))/scale,
            "ladder_blocks":int(len(docs)),
            "rule":"T_B = |R(frozen pair) - R(finer neighbour)|, the standard "
                   "adjacent-pair Richardson error estimate against a MORE "
                   "accurate reference; no divisor, no model assumption"}


def adjudicate() -> dict:
    plan=json.loads((NS/"production"/"p4zb_campaign_plan.json").read_text())
    t=plan["thresholds"]; cfg=plan["configuration"]
    assert t["relative"]==0.03 and t["z"]==4.0 and t["fd_ladder_relative_max"]==0.02
    A_docs,B_docs=_blocks("rb_score"),_blocks("rb_map")
    cells,counts=[],{"PASS":0,"FAIL":0,"INCONCLUSIVE":0}
    for m in cfg["m_grid"]:
        a,b,lad=_sum(A_docs,m),_sum(B_docs,m),_ladder(m,plan)
        row={"configuration":cfg["id"],"layer":cfg["layer"],"detector":cfg["detector"],
             "family":cfg["family"],"m":m,"rb_score":a,"rb_map":b,"fd_ladder":lad}
        if a is None or b is None or lad is None:
            row["gate_result"]="INCONCLUSIVE"; row["reasons"]=["missing blocks"]
            counts["INCONCLUSIVE"]+=1; cells.append(row); continue
        if a["blocks"]<cfg["blocks"] or b["blocks"]<cfg["blocks"]:
            row["gate_result"]="INCONCLUSIVE"
            row["reasons"]=[f"block counts {a['blocks']}/{b['blocks']} below the frozen {cfg['blocks']}"]
            counts["INCONCLUSIVE"]+=1; cells.append(row); continue
        reasons=[]
        k6a=_up(a["relative_se"])>t["r_star"]; k6b=_up(b["relative_se"])>t["r_star"]
        k5a=_up(a["top1_share_of_block_variance"])>t["top1_share_max"] or _up(a["top5_share_of_block_variance"])>t["top5_share_max"]
        k5b=_up(b["top1_share_of_block_variance"])>t["top1_share_max"] or _up(b["top5_share_of_block_variance"])>t["top5_share_max"]
        k7=_up(lad["relative_drift"])>t["fd_ladder_relative_max"]
        if k6a: reasons.append("K6 rb_score relative SE above r*")
        if k6b: reasons.append("K6 rb_map relative SE above r*")
        if k5a: reasons.append("K5 rb_score block variance not scale stable")
        if k5b: reasons.append("K5 rb_map block variance not scale stable")
        if k7: reasons.append("K7 Richardson drift above the ladder limit")
        se_b=math.hypot(b["mc_se"],lad["T_B"])
        diff=abs(a["mean"]-b["mean"]); scale=max(abs(a["mean"]),abs(b["mean"]))
        rel=_up(diff/scale) if scale>0 else math.inf
        comb=math.hypot(a["mc_se"],se_b); z=_up(diff/comb) if comb>0 else math.inf
        row["correspondence"]={"se_a":a["mc_se"],"se_b_mc":b["mc_se"],"T_B":lad["T_B"],
            "se_b_total":se_b,"absolute_difference":diff,"relative_discrepancy":rel,
            "combined_se":comb,"z":z,"relative_limit":t["relative"],"z_limit":t["z"],
            "relative_ok":rel<=t["relative"],"z_ok":z<=t["z"],
            "rounding":f"statistics rounded away from zero at {ROUND_DP} dp"}
        row["preconditions"]={"K5_rb_score":not k5a,"K5_rb_map":not k5b,
            "K6_rb_score":not k6a,"K6_rb_map":not k6b,"K7_fd_ladder":not k7}
        if reasons: row["gate_result"]="INCONCLUSIVE"
        elif rel<=t["relative"] and z<=t["z"]: row["gate_result"]="PASS"
        else:
            row["gate_result"]="FAIL"
            if rel>t["relative"]: reasons.append("relative discrepancy above 0.03")
            if z>t["z"]: reasons.append("|z| above 4.0")
        row["reasons"]=reasons; counts[row["gate_result"]]+=1; cells.append(row)
    stp=NS/"production"/"run_state.json"
    st=json.loads(stp.read_text()) if stp.exists() else {}
    cpu=(st.get("cpu_seconds_total",0.0)+st.get("calibration_cpu_seconds",0.0))/3600.0
    doc={"schema":"rebaseguard.p4zb-adjudication.v1","result_bearing":True,
        "scope":{"configuration":cfg["id"],"m":cfg["m_grid"],"cells":len(cells)},
        "thresholds_used":{**{k:t[k] for k in ("relative","z","r_star",
            "fd_ladder_relative_max","top1_share_max","top5_share_max")},
            "source":"frozen P4 protocol via the frozen P4ZB plan",
            "any_threshold_changed_by_p4zb":False},
        "truncation_rule":plan["fd_ladder"]["truncation_rule"],
        "rounding_policy":"statistics rounded AWAY FROM ZERO at 12 dp",
        "counts":counts,"cells_total":len(cells),
        "cost":{"run_cpu_hours":st.get("cpu_seconds_total",0.0)/3600.0,
                "calibration_cpu_hours":st.get("calibration_cpu_seconds",0.0)/3600.0,
                "cpu_hours_total":cpu,"cap_hours":plan["budget"]["total_cpu_cap_hours"],
                "COST_CAP":"PASS" if cpu<=plan["budget"]["total_cpu_cap_hours"] else "FAIL"},
        "cells":cells}
    return doc


def main() -> int:
    d=adjudicate()
    (NS/"production"/"adjudication_p4zb.json").write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")
    print(f"cells {d['cells_total']}  PASS {d['counts']['PASS']}  FAIL {d['counts']['FAIL']}  INCONCLUSIVE {d['counts']['INCONCLUSIVE']}")
    print(f"CPU {d['cost']['cpu_hours_total']:.4f} h (run {d['cost']['run_cpu_hours']:.4f} + calib {d['cost']['calibration_cpu_hours']:.4f}) of {d['cost']['cap_hours']} -> {d['cost']['COST_CAP']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
