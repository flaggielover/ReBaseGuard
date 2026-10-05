"""Assemble the owner's message-6 governance-only filing for r2: byte-for-byte copies of the accepted SF1-A review
record and of the owner's message 6, the review's .sha256 in r2's format, and R2_SF1A_INCORPORATION_RECORD.json
binding the fast-forward's evidence (pre, pre-push, push, post, fresh clone, fast checks).

usage: make_filing_sf1a.py <session repo> <hardening commit with the records> <evidence dir> <out dir>
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

repo, hb, evd, out = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3]), Path(sys.argv[4])
out.mkdir(parents=True, exist_ok=True)
HNS = "level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/"
NS2 = "level4/closure_proofs/p5y_k5_cell309_p309_r2/"
GOV = NS2 + "governance/"
OLD, NEW = "b66a45f097989764176075802c953df4b72c2aef", "716946e8d9a6744d0b49de6acc802605b6eb1bf8"


def show(rel):
    return subprocess.run(["git", "-C", str(repo), "show", f"{hb}:{rel}"], capture_output=True, check=True).stdout


h = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
COPIES = {  # r2 name <- hardening source (bytes unchanged)
    "BRIEF_SF1A_DELTA_REVIEW.md": HNS + "sf1a_review/BRIEF_SF1A_DELTA_REVIEW.md",
    "REVIEW_SF1A_DELTA.md": HNS + "sf1a_review/REVIEW_SF1A_DELTA.md",
    "REVIEW_SF1A_DELTA_EXEC_LEDGER.jsonl": HNS + "sf1a_review/REVIEW_SF1A_DELTA_EXEC_LEDGER.jsonl",
    "OWNER_DECISIONS_R2_MSG6_VERBATIM.md": HNS + "owner_decision_packet/owner_reply_msg6/OWNER_DECISIONS_R2_MSG6_VERBATIM.md",
}
filed = {}
for name, src in COPIES.items():
    b = show(src)
    (out / name).write_bytes(b)
    filed[GOV + name] = {"sha256": h(b), "source": f"{hb[:8]}:{src}", "bytes_identical_to_source": True}
review = (out / "REVIEW_SF1A_DELTA.md").read_bytes()
assert h(review) == "1f95ca2f81953a8643fc41cfc7a4bf6dcfd2175adccefce5670db39f141828a2"
assert h((out / "BRIEF_SF1A_DELTA_REVIEW.md").read_bytes()) == "59c2544d85c2c1f10a2219566c5840479f9fe9868a2e04b6a8462c662db40c66"
(out / "REVIEW_SF1A_DELTA.sha256").write_text(f"{h(review)}  {GOV}REVIEW_SF1A_DELTA.md\n")
filed[GOV + "REVIEW_SF1A_DELTA.sha256"] = {"sha256": h((out / "REVIEW_SF1A_DELTA.sha256").read_bytes()),
                                           "content": "sha256 of REVIEW_SF1A_DELTA.md, in r2's .sha256 format"}
msg_md = (out / "OWNER_DECISIONS_R2_MSG6_VERBATIM.md").read_text()
body = msg_md.split("```text\n", 1)[1].rsplit("\n```", 1)[0]
msg_sha = h(body.encode())
assert f"sha256: `{msg_sha}`" in msg_md
ev = {k: json.loads((evd / f).read_text()) for k, f in {
    "pre": "FF_SF1A_PRECHECK_1.json", "prepush": "FF_SF1A_PREPUSH.json", "post": "FF_SF1A_POSTCHECK.json",
    "fresh": "R2_FRESH_CLONE_VERIFICATION_716946e8.json", "fast": "FAST_CHECKS_r2_716946e8_fresh.json"}.items()}
for k in ("pre", "prepush", "post", "fresh"):
    assert ev[k]["ok"] is True, k
assert ev["fast"]["all_rc0"] is True and ev["fast"]["commit"] == NEW
push_out = (evd / "FF_SF1A_PUSH_OUTPUT.txt").read_text()
assert f"HEAD:refs/heads/claude/p5y-k5-cell309-p309-r2\t{OLD[:8]}..{NEW[:8]}" in push_out and "+" not in push_out.split("\t")[0]
fast_tail = {k: v["tail"] for k, v in ev["fast"]["steps"].items()}
rec = {
    "schema": "P309_R2_INCORPORATION_RECORD/1",
    "what": "the owner's SF1-A incorporation (message 6): a fast-forward of r2 from b66a45f0 to 716946e8, nothing "
            "else in that step; then this separate governance-only commit",
    "authorization": {"owner_record": GOV + "OWNER_DECISIONS_R2_MSG6_VERBATIM.md", "owner_message_sha256": msg_sha,
                      "answers": "the line left unanswered by message 5 (OWNER_DECISIONS_R2_RECORD_1.json, "
                                 "not_answered_or_pending: 'SF1-A incorporation into r2')",
                      "earlier_authority": GOV + "OWNER_DECISIONS_R2_MSG5_VERBATIM.md (SF1: SELECT SF1-A)"},
    "review": {"brief": GOV + "BRIEF_SF1A_DELTA_REVIEW.md", "review": GOV + "REVIEW_SF1A_DELTA.md",
               "review_sha256": h(review), "exec_ledger": GOV + "REVIEW_SF1A_DELTA_EXEC_LEDGER.jsonl",
               "disposition": "SF1A_DELTA_REVIEW_ACCEPTED_WITH_NONBLOCKING_FOLLOWUPS",
               "sf1_ruling": "SF1: RESOLVED",
               "condition_applied": "C-B1 (blocking-before-incorporation): incorporate exactly 716946e8 on top of "
                                    "b66a45f0 (a fast-forward); no hardening-branch file, tool, test or evidence "
                                    "enters r2 in the same step",
               "conditions_carried_forward": {
                   "C-F1 (before-freeze)": "the worker-tier drill (formal review 5, C3) on bytes that include SF1-A",
                   "C-A1..C-A5 (advisory)": "residual write-free-probe limits recorded as accepted limits; extra "
                                            "tests (symlinked ledger, ledger bytes/mtime unchanged); fs_probe docstring "
                                            "under SF2; unit evidence self-binding; matrix S09 rc normalization"},
               "hardening_evidence": f"{hb[:8]}:{HNS}sf1a_review/evidence/"},
    "fast_forward": {
        "branch": "claude/p5y-k5-cell309-p309-r2", "from": OLD, "to": NEW, "new_commit_created": False,
        "forced": False, "pushed_from": "the local SF1-A branch claude/p309-r2-sf1a-20261005 at 716946e8, as "
                                        "HEAD:refs/heads/claude/p5y-k5-cell309-p309-r2",
        "push_output": push_out.strip().split("\n"),
        "local_side_effect": "`push -u` set the local SF1-A branch's upstream (local git config) to origin r2; no ref "
                             "other than origin r2 changed",
        "commits_entering_r2": ev["pre"]["range_commits"], "paths_entering_r2": ev["pre"]["range_paths"],
        "numstat": ev["pre"]["numstat"], "added_lines": ev["pre"]["added_lines"],
        "runner_sha256": {"before": ev["pre"]["runner_sha256_old"], "after": ev["pre"]["runner_sha256_new"]},
        "tree": ev["fresh"]["tree"],
        "precheck": ev["pre"]["checks"], "precheck_before_push": ev["prepush"]["checks"],
        "postcheck": ev["post"]["checks"], "refs_changed_on_origin": ev["post"]["refs_changed_since_pre"]},
    "independent_verification_fresh_clone": {
        "checks": ev["fresh"]["checks"], "first_parent_chain": ev["fresh"]["first_parent_chain"],
        "ast_changed_definitions": ev["fresh"]["ast_changed_definitions"],
        "pinned_functions_byte_identical": ev["fresh"]["pinned_functions_byte_identical"],
        "r2_subtrees_other_than_runner": ev["fresh"]["r2_subtrees_other_than_runner"]},
    "fast_checks_on_the_fresh_clone": {
        "commit": ev["fast"]["commit"],
        "steps_rc": {k: v["rc"] for k, v in ev["fast"]["steps"].items()},
        "content": {
            "QC12 T1-T14 PASS": "[FAIL]" not in fast_tail["QC12_static_check"],
            "static controls 22/22, T14a PASS": "T14a_main_preflight_after_the_attempt" in fast_tail["static_controls"]
            and "[FAIL]" not in fast_tail["static_controls"],
            "scanner pins all current": "P309 SCAN PINS: all current" in fast_tail["scan_pins_list"],
            "scan-allowance controls PASS": "[FAIL]" not in fast_tail["scan_allowance_test"],
            "unresolved-marker check pass": '"pass": true' in fast_tail["placeholder_check"],
            "manifest identical": "MANIFEST IDENTICAL" in fast_tail["manifest_check"],
            "QC15 A1-A10 true": '"ok": true' in fast_tail["QC15_self_audit"] and "false" not in fast_tail["QC15_self_audit"]}},
    "unchanged": {"scientific logic, target logic, gate logic": "every r2 file but the runner is the same blob as at "
                                                                "b66a45f0; in the runner only fs_probe differs (AST); "
                                                                "the 9 pinned functions are byte-identical",
                  "scanner pins": "config/ unchanged; p309_scan_pins.py --list: all current"},
    "filed_in_this_commit": filed,
    "sf1_status": "SF1: RESOLVED for the incorporated r2 bytes (r2 716946e8 and its governance-only child; runner "
                  "sha256 540df0552bfc31512289e30eaf1ead57bf82a4ac806f38080439c05c43f9a3af), as message 6 states "
                  "once the incorporation and this filing are complete",
    "not_authorized": ["freeze", "formal qualification", "worker-tier execution before its host prerequisites are met",
                       "grant issuance or consumption", "Gamma(309) evaluation", "any target evaluation",
                       "Cell 309 adoption", "scientific-status change", "r5 modification", "creation of r6",
                       "unrelated hardening", "any additional mutation of r2"],
    "statement": "NEW Γ309 TARGET EVALUATIONS = 0; no grant; OD-R2-0(D) OPEN; Cell 309 OPEN",
}
rec["fast_checks_on_the_fresh_clone"]["content_ok"] = all(rec["fast_checks_on_the_fresh_clone"]["content"].values())
assert rec["fast_checks_on_the_fresh_clone"]["content_ok"]
(out / "R2_SF1A_INCORPORATION_RECORD.json").write_text(json.dumps(rec, indent=1, ensure_ascii=False) + "\n")
print("filed", sorted(p.name for p in out.iterdir()))
