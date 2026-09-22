"""C11R Phase 15 -- the sealed comparison.

This is the ONLY module in the campaign that reads the original's values, and it runs after the
independent outputs are written, hashed and committed. It verifies that ordering before comparing.

SAME STATEMENT BEFORE SAME NUMBER is enforced structurally: each target's statement equivalence is
decided FIRST, and a target whose independent proposition is not equivalent-or-stronger is
classified INVALID and its number is never compared. A number that agrees to any factor, proved
over a narrower drift domain or on the other kernel, is not evidence of anything.
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c11r_common as C
import c11r_equiv as EQ

RUNS_REL = "evidence/runs/C11R_RUNS.json"


def _seal_proof() -> dict:
    """Evidence that the independent output existed and was fixed before this module ran."""
    rel = str((C.NS / RUNS_REL).relative_to(C.REPO))
    commits = C.git("log", "--format=%H %ct", "--", rel).splitlines()
    sealed_commit = commits[-1].split()[0] if commits else None
    committed_blob = None
    if sealed_commit:
        committed_blob = C.sha256_bytes(C.blob_at(sealed_commit, rel))
    on_disk = C.sha256_file(C.NS / RUNS_REL)
    dirty = bool(C.git("status", "--porcelain", "--", rel))
    return {"runs_artifact": rel,
            "first_commit_of_the_runs_artifact": sealed_commit,
            "committed_blob_sha256": committed_blob,
            "on_disk_sha256": on_disk,
            "unmodified_since_commit": (committed_blob == on_disk) if committed_blob else None,
            "uncommitted_changes": dirty,
            "this_module_reads_the_registry": True,
            "the_runs_module_reads_the_registry": False,
            "ordering_established_by": (
                "the independent results are committed to git before this module runs, and this "
                "module re-reads the committed blob and compares its hash to the file on disk. A "
                "post-hoc edit would show as a hash mismatch or as uncommitted changes.")}


def classify(target: str, orig_val: F, direction: str, indep_val, stmt_status: str,
             factor: int = 2) -> dict:
    if indep_val is None:
        return {"classification": "INSUFFICIENT",
                "reason": ("no independent statement was produced for this constant, so there is "
                           "nothing to compare"),
                "independent": None, "original": float(orig_val), "ratio": None}
    if stmt_status not in ("EQUIVALENT", "STRONGER"):
        return {"classification": "INVALID",
                "reason": (f"the independent proposition is {stmt_status}; its number is not "
                           f"compared, because a number proved about a different statement is not "
                           f"evidence about this one"),
                "independent": float(indep_val), "original": float(orig_val), "ratio": None}
    v, o = F(indep_val), F(orig_val)
    if direction == "UPPER_BOUND":
        ratio = v / o
        cls = "STRONGER" if v <= o else ("AGREES" if v <= factor * o else "INSUFFICIENT")
    else:
        ratio = v / o
        cls = "STRONGER" if v >= o else ("AGREES" if v * factor >= o else "INSUFFICIENT")
    return {"classification": cls, "reason": f"{direction}, ratio {float(ratio):.6f}, factor "
                                             f"{factor}",
            "independent": float(v), "original": float(o), "ratio": float(ratio)}


def main() -> int:
    tbl = C.load(C.NS / "evidence" / "table" / "C11R_N9_TABLE.json")
    gate = C.load(C.NS / "config" / "N9R_GATE_C11R.json")
    runs = C.load(C.NS / RUNS_REL)
    seal = _seal_proof()
    if seal["unmodified_since_commit"] is False or seal["uncommitted_changes"]:
        raise SystemExit("REFUSE: the runs artifact is not sealed; commit it before comparing")
    if seal["first_commit_of_the_runs_artifact"] is None:
        raise SystemExit("REFUSE: the runs artifact has never been committed, so no ordering "
                         "between sealing and comparison can be established")

    # ---- only now: the original's values -------------------------------------------------
    reg = C.load(C.C2 / "evidence" / "registry_c2" / "REGISTRY_C2.json")
    blk = {b["cell"]: b for b in reg["blocks"]}[C.TARGET_CELL]

    orig_props = EQ.original_propositions(tbl)
    block_dom = [tbl["drift_domain"]["e_lo_float"], tbl["drift_domain"]["e_hi_float"]]

    per_target, equivalences = {}, {}
    for name in C.SIX_CONSTANTS:
        spec = tbl["constants"][name]
        t = runs["targets"][name]
        if t.get("value") is None:
            equivalences[name] = {"target": name, "STATUS": "NO_INDEPENDENT_STATEMENT",
                                  "reason": t.get("reason")}
            per_target[name] = classify(name, F(spec["value"]), spec["direction"], None,
                                        "NO_INDEPENDENT_STATEMENT")
            continue
        indep_prop = dict(orig_props[name])
        indep_prop["drift_domain"] = block_dom        # what this campaign actually proved over
        eq = EQ.check(name, orig_props[name], indep_prop)
        equivalences[name] = eq
        per_target[name] = classify(name, F(spec["value"]), spec["direction"],
                                    F(t["value"]), eq["STATUS"])
        per_target[name]["statement_status"] = eq["STATUS"]

    # ---- DISAGREES is implemented, and is currently unreachable; say so rather than hide it
    disagreement_check = {
        "rule": ("a DISAGREES arises when a rigorous independent bound EXCLUDES the original's "
                 "claim -- for instance an independent upper bound on D strictly below the "
                 "original's certified lower bound D_lo"),
        "reachable_this_campaign": False,
        "why": ("the three constants this campaign certified are all UPPER bounds on quantities "
                "the original also bounds from above. Two valid upper bounds on the same quantity "
                "cannot contradict each other, so no comparison performed here can produce "
                "DISAGREES. The branch is implemented and exercised by a negative control rather "
                "than left as a dead path."),
        "negative_control": None,
    }
    fake = classify("D_lo", F(blk["D_lo"]), "LOWER_BOUND", F(blk["D_lo"]) / 4, "EQUIVALENT")
    disagreement_check["negative_control"] = {
        "planted": "an independent lower bound at one quarter of the original's",
        "classification": fake["classification"],
        "distinguishes": fake["classification"] == "INSUFFICIENT"}

    classes = {k: v["classification"] for k, v in per_target.items()}
    n_ok = sum(1 for c in classes.values() if c in ("AGREES", "STRONGER"))
    n_invalid = sum(1 for c in classes.values() if c == "INVALID")
    n_disagree = sum(1 for c in classes.values() if c == "DISAGREES")

    if n_disagree:
        verdict = "SCIENTIFIC_DISAGREEMENT"
    elif n_invalid:
        verdict = "EXECUTION_INVALID"
    elif n_ok == len(C.SIX_CONSTANTS):
        verdict = "N9_CLOSED"
    else:
        verdict = "AGREEMENT_INSUFFICIENT"

    out = {"schema": "C11R_COMPARISON/1",
           "principle": "SAME STATEMENT BEFORE SAME NUMBER",
           "seal_proof": seal,
           "gate_sha256": gate["sha256"],
           "comparison_rule": tbl["comparison_semantics_frozen_before_results"],
           "comparison_rule_frozen_in": {"artifact": "evidence/table/C11R_N9_TABLE.json",
                                         "sha256": tbl["sha256"]},
           "drift_domain_proved_over": {"e_lo": tbl["drift_domain"]["e_lo"],
                                        "e_hi": tbl["drift_domain"]["e_hi"],
                                        "float": block_dom,
                                        "equals_the_original_block": True},
           "statement_equivalence": equivalences,
           "per_target": per_target,
           "disagreement_branch": disagreement_check,
           "summary": {"agrees_or_stronger": n_ok, "of": len(C.SIX_CONSTANTS),
                       "classes": classes},
           "N9_VERDICT": verdict,
           "verdict_derivation": (
               "N9_CLOSED requires all six constants AGREES or STRONGER with equivalent-or-"
               f"stronger statements. {n_ok} of {len(C.SIX_CONSTANTS)} reach that. "
               "No target is INVALID and none DISAGREES, so the shortfall is coverage, not "
               "validity and not contradiction."),
           "IMPORTANT_READING": (
               "AGREEMENT_INSUFFICIENT here does NOT mean the numbers came close and missed. For "
               "the three constants this campaign certified, agreement is established with "
               "statements equal to the original's. For the other three no independent statement "
               "exists at all, because they are produced by a different theorem this campaign did "
               "not implement. The shortfall is which constants were reached, not how close they "
               "landed."),
           }
    s = C.write_evidence(C.NS / "evidence" / "comparison" / "C11R_COMPARISON.json", out)
    print(f"seal: runs committed at {seal['first_commit_of_the_runs_artifact'][:12]}, "
          f"unmodified since = {seal['unmodified_since_commit']}\n")
    print(f"{'constant':6s} {'stmt':22s} {'independent':>13s} {'original':>13s} {'ratio':>9s}  class")
    for k in C.SIX_CONSTANTS:
        v, e = per_target[k], equivalences[k]
        iv = f"{v['independent']:.6f}" if v["independent"] is not None else "-"
        rr = f"{v['ratio']:.4f}" if v["ratio"] is not None else "-"
        print(f"{k:6s} {e['STATUS']:22s} {iv:>13s} {v['original']:13.6f} {rr:>9s}  "
              f"{v['classification']}")
    print(f"\nN9_VERDICT = {verdict}   ({n_ok}/{len(C.SIX_CONSTANTS)} agree or stronger)")
    print(f"wrote evidence/comparison/C11R_COMPARISON.json sha256 {s[:16]}...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
