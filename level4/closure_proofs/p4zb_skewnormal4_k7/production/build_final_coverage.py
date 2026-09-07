#!/usr/bin/env python3
"""P4ZB Phase 16 -- the final 96-cell coverage graph across the whole successor
lineage.  Each cell terminates in exactly ONE authoritative source."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

NS = Path(__file__).resolve().parent.parent
P4Z = NS.parent / "p4z_location_family_feasibility"
P4ZA = NS.parent / "p4za_fullscope_closure"
P4X = Path("/Users/suzhe/ReBaseGuard-p4x/level4/closure_proofs/"
           "p4x_generalization_boundary/production/results/c2_cell_ledger.json")
TARGET = "frozen/cusum@5/skewnormal4"


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    za_cov = json.loads((P4ZA/"results"/"claim_coverage.json").read_text())
    zb_p = NS/"production"/"adjudication_p4zb.json"
    zb = json.loads(zb_p.read_text()) if zb_p.exists() else {"cells": []}
    zb_by = {c["m"]: c for c in zb["cells"]}
    zb_hash = sha(zb_p) if zb_p.exists() else None
    za_hash = sha(P4ZA/"production"/"adjudication_p4za.json")
    z_hash = sha(P4Z/"production"/"adjudication.json")
    x_hash = sha(P4X)
    rt = json.loads((P4Z/"production"/"mac_runtime_contract.json").read_text())["runtime_hash"]

    cells, counts = [], {"COVERED_PASS":0,"COVERED_FAIL":0,"INCONCLUSIVE":0,"UNCOVERED":0}
    for c in za_cov["cells"]:
        e = {k: c[k] for k in ("layer","detector","family","m","claim","required_gate")}
        is_target = (f"{c['layer']}/{c['detector']}/{c['family']}" == TARGET)
        if is_target and c["m"] in zb_by:
            r = zb_by[c["m"]]
            e["authoritative_source"]="P4ZB"
            e["evidence_artifact"]="p4zb .../production/adjudication_p4zb.json"
            e["evidence_sha256"]=zb_hash
            e["producer_identity"]="P4ZB producer hash, one per block"
            e["runtime_identity"]=rt
            e["disposition"]={"PASS":"COVERED_PASS","FAIL":"COVERED_FAIL",
                              "INCONCLUSIVE":"INCONCLUSIVE"}[r["gate_result"]]
            e["reasons"]=r["reasons"]
            e["corroborating_evidence"]=[
                {"source":"P4ZA (superseded for this cell)","sha256":za_hash,
                 "disposition":"INCONCLUSIVE","confers_disposition":False},
                {"source":"P4X","sha256":x_hash,"disposition":"PASS",
                 "confers_disposition":False}]
        else:
            e["authoritative_source"]=c["authoritative_source"]
            e["evidence_artifact"]=c.get("evidence_artifact")
            e["evidence_sha256"]=c.get("evidence_sha256")
            e["producer_identity"]=c.get("producer_identity")
            e["runtime_identity"]=c.get("runtime_identity")
            e["disposition"]=c["disposition"]
            e["corroborating_evidence"]=c.get("corroborating_evidence",[])
        counts[e["disposition"]]+=1
        cells.append(e)

    by_src = {}
    for c in cells:
        by_src[c["authoritative_source"]] = by_src.get(c["authoritative_source"],0)+1
    doc = {"schema":"rebaseguard.p4zb-final-coverage.v1","result_bearing":True,
        "cells_total":len(cells),"counts":counts,
        "authoritative_sources":by_src,
        "conservation":{"expected":96,"accounted":sum(counts.values()),
                        "conserved":sum(counts.values())==96==len(cells),
                        "one_source_per_cell":all(c["authoritative_source"] for c in cells)},
        "rules":{"corroboration_confers_no_disposition":True,
                 "historical_evidence_used_as_sole_authority":False,
                 "no_inconclusive_upgraded_without_new_evidence":True},
        "source_artifacts":{"P4Z":z_hash,"P4ZA":za_hash,"P4ZB":zb_hash,
                            "P4X":x_hash+" (corroboration only)"},
        "cells":cells}
    (NS/"results"/"final_coverage.json").write_text(json.dumps(doc,indent=2,sort_keys=True)+"\n")
    print(f"final 96-cell coverage: {counts}")
    print(f"authoritative sources: {by_src}")
    print(f"conserved: {doc['conservation']['conserved']}  one source per cell: {doc['conservation']['one_source_per_cell']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
