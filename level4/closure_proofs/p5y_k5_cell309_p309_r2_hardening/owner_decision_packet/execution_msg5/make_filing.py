"""Assemble the AF-3 governance-only filing for r2 (task 7, step 4): byte-for-byte copies of the accepted records,
the review's .sha256 in r2's format, and R2_INCORPORATION_RECORD_C1.json binding the H-A fast-forward evidence.

usage: make_filing.py <session repo> <hardening commit with the records> <evidence dir> <history supplement> <out dir>
"""
import datetime
import hashlib
import json
import subprocess
import sys
from pathlib import Path

repo, hb, evd, hist, out = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3]), Path(sys.argv[4]), Path(sys.argv[5])
out.mkdir(parents=True, exist_ok=True)
HNS = "level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/"
GOV = "level4/closure_proofs/p5y_k5_cell309_p309_r2/governance/"


def show(rel):
    return subprocess.run(["git", "-C", str(repo), "show", f"{hb}:{rel}"], capture_output=True, check=True).stdout


h = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
COPIES = {  # r2 name <- hardening source (bytes unchanged)
    "REVIEW_R2_DELTA_FOLLOWUP_5.md": HNS + "formal_review_followup_5/REVIEW_FORMAL_DELTA_FOLLOWUP_5.md",
    "REVIEW_R2_DELTA_FOLLOWUP_5_EXEC_LEDGER.jsonl": HNS + "formal_review_followup_5/REVIEW_FORMAL_DELTA_FOLLOWUP_5_EXEC_LEDGER.jsonl",
    "R2_DELTA_FOLLOWUP_5_RECORD.md": HNS + "formal_review_followup_5/FORMAL_DELTA_REVIEW_RECORD.md",
    "OWNER_DECISIONS_R2_MSG5_VERBATIM.md": HNS + "owner_decision_packet/owner_reply_msg5/OWNER_DECISIONS_R2_MSG5_VERBATIM.md",
    "OWNER_DECISIONS_R2_RECORD_1.json": HNS + "owner_decision_packet/owner_reply_msg5/OWNER_DECISIONS_R2_RECORD_1.json",
}
filed = {}
for name, src in COPIES.items():
    b = show(src)
    (out / name).write_bytes(b)
    filed[name] = {"sha256": h(b), "source": f"{hb[:8]}:{src}", "bytes_identical_to_source": True}
review = (out / "REVIEW_R2_DELTA_FOLLOWUP_5.md").read_bytes()
(out / "REVIEW_R2_DELTA_FOLLOWUP_5.sha256").write_text(f"{h(review)}  {GOV}REVIEW_R2_DELTA_FOLLOWUP_5.md\n")
filed["REVIEW_R2_DELTA_FOLLOWUP_5.sha256"] = {"sha256": h((out / "REVIEW_R2_DELTA_FOLLOWUP_5.sha256").read_bytes()),
                                              "content": "sha256 of REVIEW_R2_DELTA_FOLLOWUP_5.md, r2's .sha256 format"}
hb_ = hist.read_bytes()
(out / "R2_DEVELOPMENT_HISTORY_SUPPLEMENT_1.md").write_bytes(hb_)
filed["R2_DEVELOPMENT_HISTORY_SUPPLEMENT_1.md"] = {"sha256": h(hb_), "source": "new (OD-R2-0(C) additive history)"}
brief_src = HNS + "formal_review_followup_5/BRIEF_FORMAL_DELTA_REVIEW_FOLLOWUP_5.md"
brief = show(brief_src)
ev = {k: json.loads((evd / f).read_text()) for k, f in {"pre": "FF_PRECHECK_1.json", "prepush": "FF_PREPUSH.json",
                                                        "post": "FF_POSTCHECK.json",
                                                        "fresh": "R2_FRESH_CLONE_VERIFICATION.json"}.items()}
rec = {
    "schema": "P309_R2_INCORPORATION_RECORD/1",
    "authorization": {"decision": "OD-R2-H = H-A; F-DRILL-ORDER = FD-A; AF-3 = AUTHORIZE",
                      "owner_record": GOV + "OWNER_DECISIONS_R2_MSG5_VERBATIM.md",
                      "owner_message_sha256": filed["OWNER_DECISIONS_R2_MSG5_VERBATIM.md"] and
                      json.loads(show(COPIES["OWNER_DECISIONS_R2_RECORD_1.json"]))["message_sha256"]},
    "formal_review": {"record": GOV + "R2_DELTA_FOLLOWUP_5_RECORD.md", "review": GOV + "REVIEW_R2_DELTA_FOLLOWUP_5.md",
                      "disposition": "FORMAL_DELTA_REVIEW_ACCEPTED_WITH_NONBLOCKING_FOLLOWUPS",
                      "condition_applied": "C1 (blocking-before-incorporation): fast-forward of r2 from 101ef2cb to "
                                           "a119e978, nothing else in the same step"},
    "fast_forward": {
        "branch": "claude/p5y-k5-cell309-p309-r2", "from": "101ef2cb17e5eab2892212178278da45b98004ed",
        "to": "a119e9789e2a1d42b584fff8a2301946a37f1bcb", "new_commit_created": False, "forced": False,
        "push_output": "101ef2cb..a119e978  claude/p5y-k5-cell309-p309-r2 -> claude/p5y-k5-cell309-p309-r2",
        "commits_entering_r2": ev["pre"]["range_commits"], "paths_entering_r2": ev["pre"]["range_paths"],
        "precheck_before_branch": ev["pre"]["checks"], "precheck_before_push": ev["prepush"]["checks"],
        "postcheck": ev["post"]["checks"], "tree": ev["post"].get("r2_tree")},
    "independent_verification_fresh_clone": {"checks": ev["fresh"]["checks"], "ok": ev["fresh"]["ok"],
                                             "head": ev["fresh"]["head"], "tree": ev["fresh"]["tree"],
                                             "evidence_commit": ev["fresh"]["evidence_commit"]},
    "this_filing": {"kind": "separate additive governance-only commit after the verified fast-forward (AF-3); "
                            "no existing governance record changed",
                    "files": filed,
                    "repin_supplement": GOV + "R2_REPIN_LIST_SUPPLEMENT_5.json (already in r2: it entered with the "
                                        "reviewed candidate a119e978)"},
    "not_filed_here": {"BRIEF_FORMAL_DELTA_REVIEW_FOLLOWUP_5.md": {
        "kept_at": f"{hb[:8]}:{brief_src} (first committed in 5a0d444a, before it was issued)",
        "sha256": h(brief),
        "reason": "it lists, verbatim, the marker words the reviewer was told to avoid, so filing it in governance/ "
                  "would fail code/p309_placeholder_check.py; its bytes are not altered; this record binds it by "
                  "commit and sha256"}},
    "does_not_authorize": ["freeze", "qualification", "grant", "Γ309 evaluation", "any target evaluation",
                           "Cell 309 adoption", "scientific-status change", "r5 change", "r6",
                           "incorporation of the SF1-A delta (not answered by the owner)"],
    "utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "statement": "NEW Γ309 TARGET EVALUATIONS = 0; no grant; no freeze; no qualification; Cell 309 OPEN",
}
(out / "R2_INCORPORATION_RECORD_C1.json").write_text(json.dumps(rec, indent=1, ensure_ascii=False) + "\n")
print(json.dumps({k: v["sha256"][:12] for k, v in filed.items()}, indent=1))
print("brief sha256", h(brief))
