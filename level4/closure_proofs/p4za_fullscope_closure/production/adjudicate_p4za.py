#!/usr/bin/env python3
"""P4ZA gate adjudication.  Frozen criteria, applied mechanically.

Thresholds are read from the frozen plan, which reads them from the frozen P4
protocol.  Statistics are rounded AWAY FROM ZERO at 12 dp before comparison
against exact limits, which is conservative for every `<=` gate.
"""
from __future__ import annotations
import json, math
from pathlib import Path
import numpy as np

NS = Path(__file__).resolve().parent.parent
BLOCK_DIR = NS/"production"/"blocks"
ROUND_DP = 12


def _up(v):
    if not math.isfinite(v): return v
    s = 10**ROUND_DP
    return math.ceil(abs(v)*s)/s*(1.0 if v>=0 else -1.0)


def _blocks(cid, route):
    d = BLOCK_DIR/cid.replace("/","__").replace("@","_at_")
    return [json.loads(p.read_text()) for p in sorted(d.glob(f"{route}_*.json"))] if d.exists() else []


def _sum(docs, m):
    if len(docs) < 2: return None
    v = np.array([d["block_mean"][str(m)] for d in docs], float)
    mean = float(v.mean()); se = float(v.std(ddof=1)/math.sqrt(v.size))
    dev = (v-mean)**2; tot = float(dev.sum()); o = np.sort(dev)[::-1]
    return {"mean":mean,"mc_se":se,"blocks":int(v.size),
            "relative_se":abs(se/mean) if mean else math.inf,
            "top1_share_of_block_variance":float(o[0]/tot) if tot>0 else 0.0,
            "top5_share_of_block_variance":float(o[:5].sum()/tot) if tot>0 else 0.0,
            "paths":int(sum(d["block_paths"] for d in docs)),
            "cpu_seconds":float(sum(d["cpu_seconds"] for d in docs))}


def _ladder(cid, m, plan):
    docs = _blocks(cid,"fd_ladder")
    if len(docs) < 2: return None
    r = plan["fd_ladder"]["rungs"]
    ck, fk = f"{r[0]:g}/{r[1]:g}", f"{r[1]:g}/{r[2]:g}"
    co = np.array([d["richardson_by_pair"][ck][str(m)] for d in docs])
    fi = np.array([d["richardson_by_pair"][fk][str(m)] for d in docs])
    # empirical order over the three rungs, reported as a diagnostic
    d1 = np.array([d["central_difference_by_h"][f"{r[0]:g}"][str(m)] for d in docs]) - \
         np.array([d["central_difference_by_h"][f"{r[1]:g}"][str(m)] for d in docs])
    d2 = np.array([d["central_difference_by_h"][f"{r[1]:g}"][str(m)] for d in docs]) - \
         np.array([d["central_difference_by_h"][f"{r[2]:g}"][str(m)] for d in docs])
    ratio = float(d1.mean()/d2.mean()) if d2.mean() else float("nan")
    t_b = abs(float(co.mean())-float(fi.mean()))
    scale = max(abs(float(co.mean())), abs(float(fi.mean())))
    return {"richardson_coarse_pair":float(co.mean()),
            "richardson_frozen_pair":float(fi.mean()),
            "coarse_pair":ck,"frozen_pair":fk,
            "T_B":t_b,"relative_drift":t_b/scale if scale>0 else math.inf,
            "empirical_order_p": math.log2(ratio) if ratio>0 else float("nan"),
            "ladder_blocks":int(len(docs)),
            "rule":"T_B = |R(coarse adjacent pair) - R(frozen pair)|, the standard "
                   "Richardson error estimate; NOT divided by 15, which is a "
                   "conservative factor of 15 against the idealised h^4 relation"}


def adjudicate() -> dict:
    plan = json.loads((NS/"production"/"p4za_campaign_plan.json").read_text())
    t = plan["thresholds"]
    assert t["relative"] == 0.03 and t["z"] == 4.0
    cells, counts = [], {"PASS":0,"FAIL":0,"INCONCLUSIVE":0}
    for cfg in plan["configurations"]:
        A_docs, B_docs = _blocks(cfg["id"],"rb_score"), _blocks(cfg["id"],"rb_map")
        for m in cfg["m_affected"]:
            a, b = _sum(A_docs,m), _sum(B_docs,m)
            lad = _ladder(cfg["id"],m,plan)
            row = {"configuration":cfg["id"],"layer":cfg["layer"],
                   "detector":cfg["detector"],"family":cfg["family"],"m":m,
                   "p4za_cause":cfg["p4za_cause"],
                   "rb_score":a,"rb_map":b,"fd_ladder":lad}
            if a is None or b is None or lad is None:
                row["gate_result"]="INCONCLUSIVE"; row["reasons"]=["missing blocks"]
                counts["INCONCLUSIVE"]+=1; cells.append(row); continue
            full = a["blocks"]>=plan["fixed_policy"]["blocks_per_route"] and \
                   b["blocks"]>=plan["fixed_policy"]["blocks_per_route"]
            reasons=[]
            if not full:
                row["gate_result"]="INCONCLUSIVE"
                row["reasons"]=[f"block counts {a['blocks']}/{b['blocks']} below "
                                f"the frozen {plan['fixed_policy']['blocks_per_route']}"]
                counts["INCONCLUSIVE"]+=1; cells.append(row); continue
            k6a=_up(a["relative_se"])>t["r_star"]; k6b=_up(b["relative_se"])>t["r_star"]
            k5a=_up(a["top1_share_of_block_variance"])>t["top1_share_max"] or \
                _up(a["top5_share_of_block_variance"])>t["top5_share_max"]
            k5b=_up(b["top1_share_of_block_variance"])>t["top1_share_max"] or \
                _up(b["top5_share_of_block_variance"])>t["top5_share_max"]
            k7=_up(lad["relative_drift"])>t["fd_ladder_relative_max"]
            if k6a: reasons.append("K6 rb_score relative SE above r*")
            if k6b: reasons.append("K6 rb_map relative SE above r*")
            if k5a: reasons.append("K5 rb_score block variance not scale stable")
            if k5b: reasons.append("K5 rb_map block variance not scale stable")
            if k7: reasons.append("K7 Richardson drift above the ladder limit")
            se_b = math.hypot(b["mc_se"], lad["T_B"])
            diff = abs(a["mean"]-b["mean"]); scale = max(abs(a["mean"]),abs(b["mean"]))
            rel = _up(diff/scale) if scale>0 else math.inf
            comb = math.hypot(a["mc_se"], se_b)
            z = _up(diff/comb) if comb>0 else math.inf
            row["correspondence"]={"se_a":a["mc_se"],"se_b_mc":b["mc_se"],
                "T_B":lad["T_B"],"se_b_total":se_b,"absolute_difference":diff,
                "relative_discrepancy":rel,"combined_se":comb,"z":z,
                "relative_limit":t["relative"],"z_limit":t["z"],
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

    stp = NS/"production"/"run_state.json"
    state = json.loads(stp.read_text()) if stp.exists() else {}
    cpu = state.get("cpu_seconds_total",0.0)/3600.0
    doc = {"schema":"rebaseguard.p4za-adjudication.v1","result_bearing":True,
        "thresholds_used":{**{k:t[k] for k in
            ("relative","z","r_star","fd_ladder_relative_max","top1_share_max","top5_share_max")},
            "source":"frozen P4 protocol via the frozen P4ZA plan",
            "any_threshold_changed_by_p4za":False},
        "rounding_policy":"test statistics rounded AWAY FROM ZERO at 12 dp "
                          "before comparison against exact limits",
        "truncation_rule":plan["fd_ladder"]["truncation_rule"],
        "counts":counts,"cells_total":len(cells),
        "by_cause":{c:{r:sum(1 for x in cells if x["p4za_cause"]==c and x["gate_result"]==r)
                       for r in ("PASS","FAIL","INCONCLUSIVE")} for c in ("K3","K7")},
        "cost":{"cpu_hours_total":cpu,"cap_hours":plan["budget"]["total_cpu_cap_hours"],
                "COST_CAP":"PASS" if cpu<=plan["budget"]["total_cpu_cap_hours"] else "FAIL"},
        "cells":cells}
    return doc


def main() -> int:
    d = adjudicate()
    (NS/"production"/"adjudication_p4za.json").write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")
    print(f"cells {d['cells_total']}  PASS {d['counts']['PASS']}  FAIL {d['counts']['FAIL']}  "
          f"INCONCLUSIVE {d['counts']['INCONCLUSIVE']}")
    print(f"by cause: {d['by_cause']}")
    print(f"CPU {d['cost']['cpu_hours_total']:.4f} h of {d['cost']['cap_hours']} -> {d['cost']['COST_CAP']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
