#!/usr/bin/env python3
"""P4ZA Phase 2 / 19 -- the 96-cell claim/evidence coverage graph.

Every cell must terminate in exactly ONE governed coverage path:

    scientific claim -> required gate -> accepted evidence artifact
                     -> producer/runtime identity -> disposition

No cell may be uncovered, ambiguously double-counted, silently inherited, or
upgraded from INCONCLUSIVE without new evidence.  Corroboration is recorded but
never confers a disposition.
"""
from __future__ import annotations
import hashlib, json, subprocess
from pathlib import Path

NS = Path(__file__).resolve().parent.parent
REPO = NS.parent.parent.parent
P4Z = NS.parent / "p4z_location_family_feasibility"
P4X = Path("/Users/suzhe/ReBaseGuard-p4x/level4/closure_proofs/"
           "p4x_generalization_boundary/production/results/c2_cell_ledger.json")


def sha(p: Path) -> str: return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    zadj = json.loads((P4Z/"production"/"adjudication.json").read_text())
    aadj_p = NS/"production"/"adjudication_p4za.json"
    aadj = json.loads(aadj_p.read_text()) if aadj_p.exists() else {"cells": []}
    px = {(c["layer"],c["detector"],c["family"],c["m"]): c
          for c in json.loads(P4X.read_text())["cells"]}
    a_by = {(c["configuration"], c["m"]): c for c in aadj["cells"]}

    z_hash = sha(P4Z/"production"/"adjudication.json")
    a_hash = sha(aadj_p) if aadj_p.exists() else None
    x_hash = sha(P4X)
    z_rt = json.loads((P4Z/"production"/"mac_runtime_contract.json").read_text())["runtime_hash"]

    cells, counts = [], {"COVERED_PASS":0,"COVERED_FAIL":0,"INCONCLUSIVE":0,"UNCOVERED":0}
    for zc in zadj["cells"]:
        key = (zc["configuration"], zc["m"])
        claim = (f"Gamma_{{{zc['detector']},{zc['m']},{zc['family']}}} at layer "
                 f"{zc['layer']}: two-route correspondence")
        entry = {"layer":zc["layer"],"detector":zc["detector"],
                 "family":zc["family"],"m":zc["m"],
                 "claim":claim,
                 "required_gate":"relative <= 0.03 AND |z| <= 4.0, with both "
                                 "routes meeting r* and scale stability",
                 "corroborating_evidence":[]}
        # every cell records P4X as corroboration, never as disposition
        h = px.get(key[0].split("/")[0:1] and (zc["layer"],zc["detector"],zc["family"],zc["m"]))
        if h:
            entry["corroborating_evidence"].append({
                "source":"P4X","artifact":"c2_cell_ledger.json","sha256":x_hash,
                "disposition":h["gate_result"],
                "relative_discrepancy":h["relative_discrepancy"],"z":h["z"],
                "confers_disposition":False})

        if zc["gate_result"] == "PASS":
            entry["authoritative_source"]="P4Z"
            entry["evidence_artifact"]="p4z .../production/adjudication.json"
            entry["evidence_sha256"]=z_hash
            entry["producer_identity"]="P4Z producer hash cfe18348..., one per block"
            entry["runtime_identity"]=z_rt
            entry["disposition"]="COVERED_PASS"
        elif key in a_by and a_by[key].get("gate_result") in ("PASS","FAIL","INCONCLUSIVE"):
            r = a_by[key]
            entry["authoritative_source"]="P4ZA"
            entry["evidence_artifact"]="p4za .../production/adjudication_p4za.json"
            entry["evidence_sha256"]=a_hash
            entry["producer_identity"]="P4ZA producer hash, one per block"
            entry["runtime_identity"]=z_rt
            entry["p4za_cause"]=r["p4za_cause"]
            entry["disposition"]={"PASS":"COVERED_PASS","FAIL":"COVERED_FAIL",
                                  "INCONCLUSIVE":"INCONCLUSIVE"}[r["gate_result"]]
            entry["reasons"]=r["reasons"]
            # P4Z's own superseded reading is corroboration only
            entry["corroborating_evidence"].append({
                "source":"P4Z (superseded for this cell)","artifact":"adjudication.json",
                "sha256":z_hash,"disposition":zc["gate_result"],
                "reasons":zc["reasons"],"confers_disposition":False})
        else:
            entry["authoritative_source"]=None
            entry["disposition"]="UNCOVERED"
        counts[entry["disposition"]]+=1
        cells.append(entry)

    dup = [c for c in cells if c["authoritative_source"] is None and c["disposition"]!="UNCOVERED"]
    doc = {"schema":"rebaseguard.p4za-claim-coverage.v1","result_bearing":True,
        "cells_total":len(cells),"counts":counts,
        "conservation":{"expected":96,"accounted":sum(counts.values()),
                        "conserved":sum(counts.values())==96==len(cells)},
        "rules":{"one_authoritative_source_per_cell":True,
                 "corroboration_confers_no_disposition":True,
                 "no_inconclusive_upgraded_without_new_evidence":True,
                 "historical_evidence_used_as_sole_authority":False},
        "sources":{"P4Z":{"cells":counts_by(cells,"P4Z"),"sha256":z_hash},
                   "P4ZA":{"cells":counts_by(cells,"P4ZA"),"sha256":a_hash},
                   "P4X":{"cells":0,"role":"corroboration only","sha256":x_hash}},
        "ambiguous":dup,"cells":cells}
    out = NS/"results"/"claim_coverage.json"
    out.write_text(json.dumps(doc,indent=2,sort_keys=True)+"\n")
    print(f"96-cell coverage: {counts}")
    print(f"authoritative sources: P4Z {doc['sources']['P4Z']['cells']}, "
          f"P4ZA {doc['sources']['P4ZA']['cells']}, P4X {doc['sources']['P4X']['cells']} (corroboration only)")
    print(f"conserved: {doc['conservation']['conserved']}   ambiguous: {len(dup)}")
    print(f"-> {out}")
    return 0


def counts_by(cells, src):
    return sum(1 for c in cells if c.get("authoritative_source") == src)


if __name__ == "__main__":
    raise SystemExit(main())
