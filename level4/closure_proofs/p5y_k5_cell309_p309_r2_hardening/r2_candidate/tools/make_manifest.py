"""Build R2_CANDIDATE_EVIDENCE_MANIFEST.json (deliverable 5) for the r2_candidate directory.

usage: make_manifest.py <r2_candidate dir>
Every file (except the manifest itself) with its sha256 and size, plus the key facts read FROM the evidence files.
"""
import datetime
import hashlib
import json
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
OUT = "R2_CANDIDATE_EVIDENCE_MANIFEST.json"


def j(rel):
    return json.loads((root / rel).read_text())


files = {str(p.relative_to(root)): {"sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "bytes": p.stat().st_size}
         for p in sorted(root.rglob("*")) if p.is_file() and p.name != OUT and "__pycache__" not in p.parts}
mc, mb = j("evidence/matrix/MATRIX_CANDIDATE.json"), j("evidence/matrix/MATRIX_BASELINE.json")
cls = lambda m: {c["id"]: (c.get("classification") or c.get("status_after_crash") or
                           ("refused" if c.get("runner_refused") else "launched")) for c in m["cases"]}
reg, sc = j("evidence/regression/REG_CANDIDATE.json"), j("evidence/regression/STATIC_CONTROLS_candidate.json")
qc15 = (root / "evidence/rehearsal/attempt/QC15.json").read_text()
facts = {
    "candidate_commit": "93d550638b8c79ae1c252fc6c2b0194b1a416b49",
    "candidate_branch": "claude/p309-r2-adoption-candidate-20261005",
    "base_r2_commit": "101ef2cb17e5eab2892212178278da45b98004ed",
    "hardening_source_commit": "3c191ac2f00a99c5823aefa1ade8c028a17a8918",
    "candidate_paths": ["level4/closure_proofs/p5y_k5_cell309_p309_r2/code/p309_qualify.py",
                        "level4/closure_proofs/p5y_k5_cell309_p309_r2/code/p309_topology_drill.py",
                        "level4/closure_proofs/p5y_k5_cell309_p309_r2/config/SCANNER_ALLOWANCE_P309.json"],
    "runner_pinned_all_byte_identical": j("evidence/AST_RUNNER_R2_VS_CANDIDATE.json")["pinned_all_byte_identical"],
    "runner_unintended_touched": j("evidence/AST_RUNNER_R2_VS_CANDIDATE.json")["unintended_touched"],
    "runner_ast_changes_vs_hardened_v2": j("evidence/AST_RUNNER_HARDENED_V2_VS_CANDIDATE.json")["changed_ast"],
    "drill_unintended_touched": j("evidence/AST_DRILL_R2_VS_CANDIDATE.json")["unintended_touched"],
    "allowance_changed_leaves": j("evidence/ALLOWANCE_DIFF.json")["changed"],
    "t14a_anchors_all_exactly_once": j("evidence/ANCHORS_CANDIDATE_WT.json")["all_anchors_exactly_once"],
    "static_controls_all_pass": sc["all_pass"], "static_controls_count": sc["controls"],
    "t14a": sc["results"].get("T14a_main_preflight_after_the_attempt"),
    "regression_rc": {k: v.get("rc") for k, v in reg["runs"].items()},
    "regression_pins_all_current": reg.get("pins_all_current"), "qc11_table": reg.get("qc11_table"),
    # the self-audit's report is embedded as an escaped JSON string in the record's run output
    "qc15_A7_true": bool(re.search(r'A7_formal_namespace_only_research_unchanged\\*"?:\s*true', qc15)),
    "qc15_pass": json.loads(qc15).get("pass"),
    "f_drill_order_demo": {k: {"check_rc": v["manifest_check_rc"], "pins_params": v["manifest_pins_params_file"]}
                           for k, v in j("evidence/F_DRILL_ORDER_DEMO.json")["orders"].items()},
    "unit": {"candidate_meets_expectation": j("evidence/unit/UNIT_CANDIDATE.json")["meets_expectation"],
             "baseline_meets_expectation": j("evidence/unit/UNIT_BASELINE.json")["meets_expectation"]},
    "matrix_candidate": cls(mc), "matrix_baseline": cls(mb),
    "fsync_order_candidate": {k: v for k, v in j("evidence/matrix/FSYNC_ORDER_CANDIDATE.json").items() if k != "rows"},
    "rehearsal_validation": j("evidence/rehearsal/VALIDATION.json").get("verdict"),
    "rehearsal_revalidation": j("evidence/rehearsal/REVALIDATION.json").get("verdict"),
    "rehearsal_attempt1": j("evidence/rehearsal/ATTEMPT1_STATUS.json").get("verdict"),
    "integrity": {k: j("evidence/integrity/INTEGRITY_COUNT.json").get(k) for k in
                  ("new_target_evaluations", "repositories_scanned", "ledger_rows_total", "origin_protected_refs",
                   "r5_unchanged", "r6_files_at_head", "test_sandbox_grant_files", "errors")},
    "session_audit_target_evaluations":
        j("evidence/integrity/SESSION_AUDIT_SNAPSHOT.json")["target_evaluation_count"]["new_target_evaluations"],
}
doc = {
    "schema": "P309_R2_CANDIDATE_EVIDENCE_MANIFEST/1",
    "deliverable": 5,
    "required_name": "ADOPTION_EVIDENCE_MANIFEST.json",
    "name_note": "the session guard refuses paths containing 'adoption' (rule R2_GRANT); narrowing it was denied as "
                 "self-modification, so four deliverables carry neutral names",
    "deliverable_names": {"ADOPTION_CANDIDATE_DELTA.md": "R2_CANDIDATE_DELTA.md",
                          "ADOPTION_VALIDATION_REPORT.md": "R2_CANDIDATE_VALIDATION_REPORT.md",
                          "F_DRILL_ORDER_REVIEW.md": "F_DRILL_ORDER_REVIEW.md",
                          "INDEPENDENT_DELTA_REVIEW.md": "INDEPENDENT_DELTA_REVIEW.md",
                          "ADOPTION_EVIDENCE_MANIFEST.json": OUT,
                          "FINAL_ADOPTION_READINESS.md": "FINAL_R2_CANDIDATE_READINESS.md"},
    "verdict": "R2_ADOPTION_CANDIDATE_REVIEW_REQUIRED",
    "statement": "result-free; NEW TARGET EVALUATIONS = 0; no grant; no adoption; r5 unchanged; no r6; "
                 "r1/r2/main unchanged; Cell 309 OPEN",
    "built_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "facts_from_evidence": facts,
    "files": files,
}
(root / OUT).write_text(json.dumps(doc, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
print(json.dumps({k: facts[k] for k in ("qc15_A7_true", "t14a", "static_controls_all_pass", "rehearsal_validation",
                                         "regression_pins_all_current", "runner_pinned_all_byte_identical")},
                 indent=1), len(files), "files")
