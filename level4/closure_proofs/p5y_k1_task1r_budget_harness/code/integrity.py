"""Task-1R integrity: binding checkpoint + IMMUTABLE predecessor artifacts."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
ROOT = NS.parents[2]
K1_REL = "level4/closure_proofs/p5y_k1_binding_campaign"
K1 = ROOT / K1_REL

# Predecessor blobs pinned at the commit that recorded the Task-1 FAIL.
PREDECESSOR = {
    f"{K1_REL}/results/task1_F0_qualification.json":
        "87b3e75e9ab5630beed7c0176221dbe9",
    f"{K1_REL}/adjudication/TASK1_ADJUDICATION.json":
        "1f56dd357e789908de8d57b3bf5665c5",
    f"{K1_REL}/task1/task1_f0.py":
        "1a78fba1bf296c9e3ec4247f78b8fa88",
}


def _sha(path: str) -> str:
    raw = subprocess.run(["git", "-C", str(ROOT), "show", f"HEAD:{path}"],
                         capture_output=True, check=True).stdout
    return hashlib.sha256(raw).hexdigest()


def verify() -> dict:
    man = json.loads((K1 / "manifests/source_manifest.json").read_text())
    agg = hashlib.sha256()
    bad = []
    for rel, dig in man["file_sha256"].items():
        raw = subprocess.run(
            ["git", "-C", str(ROOT), "show",
             f'{man["anchor_commit"]}:{man["namespace"]}/{rel}'],
            capture_output=True, check=True).stdout
        if hashlib.sha256(raw).hexdigest() != dig:
            bad.append(rel)
        agg.update(rel.encode()); agg.update(b"\0")
        agg.update(dig.encode()); agg.update(b"\n")
    prot = json.loads((K1 / "manifests/protected_inputs.json").read_text())
    tbad = []
    for p, sha in prot["directory_tree_sha1"].items():
        out = subprocess.run(["git", "-C", str(ROOT), "ls-tree", "--full-tree",
                              "HEAD", p + "/"], capture_output=True, text=True,
                             check=True).stdout
        if not out.strip() or out.split()[2] != sha:
            tbad.append(p)
    pred_bad = [p for p, pre in PREDECESSOR.items() if not _sha(p).startswith(pre)]
    r = json.loads((K1 / "results/task1_F0_qualification.json").read_text())
    a = json.loads((K1 / "adjudication/TASK1_ADJUDICATION.json").read_text())
    ck = json.loads((K1 / "CHECKPOINT.json").read_text())
    prior = [str(p.relative_to(NS)) for d in ("results", "certificates")
             for p in (NS / d).rglob("*") if p.is_file() and p.name != ".gitkeep"]
    ok = (agg.hexdigest() == man["CHECKPOINT_HASH"] and not bad and not tbad
          and not pred_bad and not prior
          and ck["state"]["P5Y_K1_CHECKPOINT_STATUS"] == "FROZEN"
          and r["TASK1_VERDICT"] == "FAIL"
          and a["P5Y_K1_TASK1"] == "FAIL"
          and a["governing_failure_class"] == "IMPLEMENTATION_DEFECT")
    return {"k1_checkpoint_hash": agg.hexdigest(),
            "k1_anchor": man["anchor_commit"],
            "k1_blobs_verified": len(man["file_sha256"]), "k1_blob_mismatch": bad,
            "protected_trees_verified": len(prot["directory_tree_sha1"]),
            "protected_tree_mutated": tbad,
            "predecessor_blobs_verified": len(PREDECESSOR),
            "predecessor_mutated": pred_bad,
            "predecessor_verdict": r["TASK1_VERDICT"],
            "predecessor_governing_class": a["governing_failure_class"],
            "predecessor_delta_0": r["defect_certificate"]["delta_0"],
            "checkpoint_status": ck["state"]["P5Y_K1_CHECKPOINT_STATUS"],
            "prior_task1r_results": prior,
            "PASS": bool(ok)}


def frozen_scope_unchanged(H) -> dict:
    """Task-1R constants must equal the binding checkpoint's, field by field."""
    ck = json.loads((K1 / "CHECKPOINT.json").read_text())
    p1 = json.loads((K1 / "config/p1_rule.json").read_text())
    bl = json.loads((K1 / "config/budget_ledger.json").read_text())
    pr = json.loads((K1 / "config/precision_policy.json").read_text())
    cx = json.loads((K1 / "config/complexity_guard.json").read_text())
    t1 = ck["task1"]
    ch = {
        "detector": t1["detector"] == H.DETECTOR,
        "object": t1["object"] == H.OBJECT,
        "patch": tuple(t1["patch"]) == H.PATCH,
        "grid": t1["grid"] == H.GRID,
        "e": t1["e"].split()[0] == f"{H.E_NUM}/{H.E_DEN}",
        "bidegree": tuple(t1["candidate_bidegree"]) == (H.CAND_DEGREE, H.CAND_DEGREE),
        "scale_bits": t1["dyadic_scale_bits"] == H.SCALE_BITS,
        "B_candidate": bl["ledger_absolute"]["B_candidate"] == H.B_CANDIDATE,
        "LOCAL_GATE_BUDGET": bl["local_gate_budget"] == H.LOCAL_GATE_BUDGET,
        "no_redistribution": bl["redistribution_allowed"] is False,
        "eps_P1": p1["eps_P1"] == H.EPS_P1,
        "P1_check": p1["P1_CHECK_THRESHOLD"] == H.P1_CHECK_THRESHOLD,
        "P1_guard": p1["P1_HEADROOM_GUARD"] == H.P1_HEADROOM_GUARD,
        "P1_workprec": p1["P1_RULE_WORKPREC_BITS"] == H.P1_RULE_WORKPREC,
        "SR_bits": pr["SR_production_bits"] == H.PROD_BITS,
        "no_precision_escalation": pr["PRECISION_ESCALATION_ALLOWED"] is False,
        "no_degree_adaptation": pr["DEGREE_ADAPTATION_ALLOWED"] is False,
        "complexity_ceiling": cx["PRODUCTION_COMPLEXITY_CEILING"] == H.COMPLEXITY_CEILING,
        "m_set": ck["scope"]["m_values"] == [1, 2, 3, 5],
        "detectors": set(ck["scope"]["detectors"]) == {"CUSUM", "SR"},
        "budget_partition_sums_to_B_candidate": H.budget()["sums_to_B_candidate"],
        "reserve_not_redistributable": H.budget()["reserve_redistributable"] is False,
        "no_new_budget": H.budget()["new_budget_created"] is False,
    }
    return {"checks": ch, "PASS": all(ch.values())}
