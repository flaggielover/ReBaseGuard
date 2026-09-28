"""C1b report aggregator: reads NS/validation/C1B_{PW,PW9,...}_*.json and C1B_MC.json, forms per-drift ladder
minima of the certified inputs (every certified rung of every run is an independent valid certificate at that
same declared non-target drift), re-assembles RLR (LR-3) and Dv' r2 with the SAME inputs, and runs the
consistency checks against the NON-CERTIFIED Monte Carlo (each can fail).  Output NS/validation/C1B_SUMMARY.json.
Reads only this stream's own outputs; no kernel evaluation.
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parents[3]
sys.path.insert(0, str(NS / "code"))
sys.path.insert(0, str(HERE))
import ov_quarantine as Q  # noqa: E402

Q.install_import_guard()
import c1b_certpw as CP  # noqa: E402

VAL = NS / "validation"
UP = ("C_R", "tau", "C_T", "A_bar", "tau_a_up", "S2_up", "TN_up", "D1", "D2", "L1_up", "L2_up")
LO = ("tau_a_lo", "D_lo", "Lambda_lo")


def ex(v):
    if isinstance(v, dict) and "exact" in v:
        return F(v["exact"])
    return None


def gather(tags):
    """drift -> list of (file, record) for certified records of the given run tags (point runs only)."""
    out = {}
    for tag in tags:
        for p in sorted(VAL.glob(f"C1B_{tag}_POINT_e*.json")):
            d = json.loads(p.read_text())
            for r in d["records"]:
                if r.get("status") == "CERTIFIED":
                    out.setdefault(d["drift"], []).append((p.name, r))
    return out


def best_of(recs):
    b = {}
    for k in UP:
        vals = [ex(r[k]) for _, r in recs if ex(r.get(k)) is not None]
        b[k] = min(vals)
    for k in LO:
        vals = [ex(r[k]) for _, r in recs if ex(r.get(k)) is not None]
        b[k] = max(vals)
    b.update(CP.assemble(b))
    return b


def mc_checks(b, mc):
    k = 4
    s, D = mc["sigma"], mc["alarm"]
    lam_lo = (s["mean"] - k * s["se"]) / (D["mean"] + k * D["se"])
    chk = {
        "tau_a_lo<=MC+4se": float(b["tau_a_lo"]) <= s["mean"] + k * s["se"],
        "tau_a_up>=MC-4se": float(b["tau_a_up"]) >= s["mean"] - k * s["se"],
        "S2_up>=MC-4se": float(b["S2_up"]) >= mc["S2"]["mean"] - k * mc["S2"]["se"],
        "TN_up>=MC-4se": float(b["TN_up"]) >= mc["TN"]["mean"] - k * mc["TN"]["se"],
        "L1_up>=MC-4se": float(b["L1_up"]) >= mc["L1"]["mean"] - k * mc["L1"]["se"],
        "L2_up>=MC-4se": float(b["L2_up"]) >= mc["L2"]["mean"] - k * mc["L2"]["se"],
        "D_lo<=MC+4se": float(b["D_lo"]) <= D["mean"] + k * D["se"],
        "A_bar>=MC_Lambda_lo": float(b["A_bar"]) >= lam_lo,
    }
    return chk, all(chk.values())


def main(tags):
    res = {"schema": "C1B_SUMMARY/1", "run_tags": tags, "label": "certified ladder minima at declared non-target "
           "drifts; ratios reported ONLY at these drifts (rule S8)", "drifts": {}}
    mcf = VAL / "C1B_R2_MC.json"
    mc = json.loads(mcf.read_text())["drifts"] if mcf.exists() else {}
    for drift, recs in sorted(gather(tags).items(), key=lambda kv: float(F(kv[0]))):
        b = best_of(recs)
        ent = {"n_certified_records": len(recs), "sources": sorted({f for f, _ in recs}),
               "degrees": sorted({r["degree"] for _, r in recs}),
               "certified": {k: {"exact": f"{v.numerator}/{v.denominator}", "float": float(v)} for k, v in b.items()
                             if isinstance(v, F)}}
        fv = [r["float_values_at_atom"] for _, r in recs if "float_values_at_atom" in r][-1]
        ent["float_context_NONCERTIFIED"] = {"tau_a": fv["b0"], "S2": fv["b2"], "T_N": fv["xT"] - fv["b0"],
                                             "D": fv["d0"], "Dp": fv["d1"], "Dpp": fv["d2"], "Lambda": fv["W"],
                                             "sqrt_tau_S2": (fv["b0"] * fv["b2"]) ** 0.5}
        ctf = [r["C_T_float_NONCERTIFIED"] for _, r in recs if "C_T_float_NONCERTIFIED" in r]
        if ctf:
            # Dv' evaluated with the float (non-certified, most favourable) C_T but the certified other inputs:
            # guards the comparison against C_T enclosure slack (C_T is used by Dv' only)
            bb = dict(b)
            bb["C_T"] = F(min(ctf))
            ent["Dv_with_float_C_T_NONCERTIFIED"] = {k: float(v) for k, v in CP.assemble(bb).items()
                                                     if k in ("A1_Dv", "A2_Dv", "ratio_A1_Dv_over_RLR",
                                                              "ratio_A2_Dv_over_RLR", "rho1_Dv", "rho2_Dv")}
            ent["Dv_with_float_C_T_NONCERTIFIED"]["C_T_float"] = min(ctf)
        key = str(float(F(drift)))
        if key in mc:
            ent["MC_NONCERTIFIED"] = {kk: mc[key][kk] for kk in ("sigma", "L1", "L2", "S2", "TN", "alarm",
                                                                 "Lambda_renewal")}
            ent["MC_consistency"], ent["MC_consistency_all_pass"] = mc_checks(b, mc[key])
        res["drifts"][drift] = ent
        c = ent["certified"]
        print(drift, {k: round(c[k]["float"], 4) for k in ("tau", "C_T", "A_bar", "D_lo", "D1", "D2", "L1_up",
                                                           "L2_up", "rho1", "rho1_Dv", "rho2", "rho2_Dv", "A1_RLR",
                                                           "A1_Dv", "A2_RLR", "A2_Dv", "ratio_A1_Dv_over_RLR",
                                                           "ratio_A2_Dv_over_RLR")},
              "MC_ok" if ent.get("MC_consistency_all_pass") else "MC_n/a_or_FAIL", flush=True)
    # block-uniform records: certified constants + MC consistency at both block endpoints (each check can fail)
    res["blocks"] = {}
    for p in sorted(VAL.glob("C1B_R2_PW_BLOCK_*.json")):
        d = json.loads(p.read_text())
        recs = [(p.name, r) for r in d["records"] if r.get("status") == "CERTIFIED"]
        if not recs:
            res["blocks"][p.name] = {"status": "NOT_CERTIFIED"}
            continue
        b = best_of(recs)
        lo, hi = F(d["drift"]) - F(d["drift_radius"]), F(d["drift"]) + F(d["drift_radius"])
        ent = {"statement": d["statement"], "degrees": d["degrees"],
               "certified": {k: {"exact": f"{v.numerator}/{v.denominator}", "float": float(v)} for k, v in b.items()
                             if isinstance(v, F)}}
        for ep in (lo, hi):
            key = str(float(ep))
            if key in mc:
                ent[f"MC_consistency_at_{ep}"], ent[f"MC_consistency_at_{ep}_all_pass"] = mc_checks(b, mc[key])
        res["blocks"][p.name] = ent
        c = ent["certified"]
        print("BLOCK", p.name, {k: round(c[k]["float"], 4) for k in ("tau", "C_T", "A_bar", "D_lo", "D1", "D2", "L1_up",
              "L2_up", "rho1", "rho1_Dv", "A1_RLR", "A1_Dv", "A2_RLR", "A2_Dv", "ratio_A1_Dv_over_RLR",
              "ratio_A2_Dv_over_RLR")}, {k: v for k, v in ent.items() if k.endswith("all_pass")}, flush=True)
    # per-rung (i') ladder flags and provenance of every source file (C4)
    res["rung_flags"] = []
    res["source_provenance"] = {}
    for tag in tags:
        for p in sorted(VAL.glob(f"C1B_{tag}_*.json")):
            d = json.loads(p.read_text())
            pv = d.get("provenance", {})
            res["source_provenance"][p.name] = {"matches_pins": pv.get("matches_pins"), "flags": pv.get("flags")}
            for r in d.get("records", []):
                res["rung_flags"].append({"file": p.name, "degree": r.get("degree"), "status": r.get("status"),
                    "S2": "".join("T" if q["check"]["passed"] else "F" for q in r.get("S2_ladder", [])),
                    "L1": "".join("T" if q["check"]["passed"] else "F" for q in r.get("L1_ladder", [])),
                    "TN": (r.get("TN_check") or {}).get("certified")})
    sys.path.insert(0, str(HERE))
    import c1b_prov as PV
    res["provenance"] = PV.provenance({})
    out = VAL / "C1B_R2_SUMMARY.json"
    out.write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    Q.log_execution("streams/C_308/LR/cusum/c1b_report.py", f"C1b aggregation of own certified JSONs tags={tags}",
                    cells_touched=[], klass="NONTARGET_DRIFT_VALIDATION", notes="no kernel evaluation")
    print("wrote", out)


if __name__ == "__main__":
    main([x for x in sys.argv[1:]] or ["R2_PW"])
