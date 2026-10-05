"""Build the sources part of OWNER_DECISION_EVIDENCE_MAP.json: every source of the owner decision packet, located by
commit, path, sha256, git blob and the line of each anchor, computed from git (only the anchors' search text is typed).

usage: make_evidence_map.py <session repo> <out.json>
"""
import datetime
import hashlib
import json
import subprocess
import sys
from pathlib import Path

repo, out = Path(sys.argv[1]), Path(sys.argv[2])
R2, HB = "101ef2cb17e5eab2892212178278da45b98004ed", "bbe0b2533b77fc2255542dc49cdec8a8d4557cd0"
NS2 = "level4/closure_proofs/p5y_k5_cell309_p309_r2/"
HNS = "level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/"
HOST_SESSION_FILE = "R2_" + "AW" + "S_SESSION_INSTRUCTIONS.md"     # the r2 host-side session instructions


def git(*a):
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, check=True).stdout


SOURCES = {
    "R2_PACKET": (R2, NS2 + "governance/OWNER_DECISION_PACKET_R2.md", {
        "OD-R2-0": "## OD-R2-0: authority and carry-over", "OD-R2-0(A)": "* **(A) Confirm the record.**",
        "OD-R2-0(B)": "* **(B) Confirm the carry-over.**", "OD-R2-0(C)": "* **(C) Acknowledge the r1-era events.**",
        "OD-R2-0(D)": "* **(D) Authorize, or decline, the r2 stage.**",
        "OD-R2-0 carry-over table": "### Carry-over table", "OD-R2-0 liabilities": "### Liabilities for acknowledgement",
        "OD-R2-1": "## OD-R2-1 and OD-R2-1b", "OD-R2-1b": "**OD-R2-1b.**", "OD-R2-2": "## OD-R2-2:",
        "OD-R2-3": "## OD-R2-3:", "OD-R2-4": "## OD-R2-4:", "OD-R2-4 world-readable checkout": "**A world-readable cell-308 checkout fails isolation.**",
        "OD-R2-5": "## OD-R2-5:", "OD-R2-6": "## OD-R2-6:",
        "OD-R2-6 also to decide": "**Also to decide:**", "OD-R2-6 freeze field": "Also to settle: whether the frozen field"}),
    "MSG_1_3": (R2, NS2 + "governance/OWNER_INSTRUCTIONS_R2_VERBATIM.md", {
        "msg1 §4 host suitability gate": "4. HOST SUITABILITY GATE", "msg1 §5B no retry": "Do NOT introduce qualification retry/resume",
        "msg1 §10 autonomy": "10. AUTONOMY", "msg1 READY_FOR_OWNER_GRANT_DECISION": "READY_FOR_OWNER_GRANT_DECISION",
        "msg3 shared host": "## Message 3:", "msg3 §3 exclusive heavy compute": "3. Heavy computation must be mutually exclusive",
        "msg3 §6 do not alter cell 308": "6. Do not alter the cell-308 campaign", "msg3 §8 do not interrupt": "8. If cell 308 currently needs"}),
    "MSG_4": (R2, NS2 + "governance/OWNER_INSTRUCTIONS_R2_MSG4_VERBATIM.md", {
        "msg4 decides none of OD-R2-0..6": "It decides none of OD-R2-0", "msg4 item 7": "7. DO NOT make any decision reserved for OD-R2-0",
        "msg4 item 13": "13. DO NOT use the Cloud Session itself as an official durable host"}),
    "R2_AMENDMENTS": (R2, NS2 + "governance/P309_R2_AMENDMENTS.md", {
        "§A provisional OD-R2-1 (b) names": "## A. r2's production names", "§C execute on a shared host": "## C. The execute gating rule"}),
    "R2_HOST_SESSION": (R2, NS2 + "governance/" + HOST_SESSION_FILE, {
        "8a audit": "## 1. Step 8a", "8b verdict + STOP": "**STOP** until OD-R2-3 and OD-R2-4 are answered.",
        "8c bootstrap": "## 3. Step 8c", "8d worker-tier drill": "## 4. Step 8d",
        "owner-gated after 8d (incl. gate step 9 pre-freeze follow-up review)": "## 7. What remains owner-gated after 8d"}),
    "R2_BOOTSTRAP": (R2, NS2 + "governance/R2_BOOTSTRAP.md", {"STOP until OD-R2-3/4": "**STOP** until OD-R2-3 and OD-R2-4"}),
    "R2_FREEZE_PARAMS": (R2, NS2 + "code/make_freeze_params.py", {
        "OD-R2-6 answer file": 'OD_R2_6_ANSWER = "governance/OWNER_OD_R2_6_ANSWER.json"',
        "answer fields read": 'a["description"], "host_id_sha256"',
        "no host named by default": "no execution host is proposed: owner decision OD-R2-6 was not answered"}),
    "R2_REVIEW_FU4": (R2, NS2 + "governance/REVIEW_R2_DELTA_FOLLOWUP_4.md", {"verdict line": "R2_DELTA_FOLLOWUP_4_ACCEPTED"}),
    "AID_TASK2": (HB, HNS + "OWNER_DECISIONS_OD_R2.md", {
        "no answers in r2": "owner answers present in r2", "OD-R2-H (proposed)": "## Proposed additional decision (not in the packet): OD-R2-H",
        "F-DRILL-ORDER (proposed action)": "## Proposed owner action (not an OD in the packet): F-DRILL-ORDER",
        "consolidated table": "## Consolidated table"}),
    "DURABLE_HOST_PACKET": (HB, HNS + "DURABLE_HOST_EXECUTION_PACKET.md", {
        "prerequisites P0": "## 0. Prerequisites", "P0.4 IMDS": "| P0.4 |", "P0.5 operator data": "| P0.5 |",
        "filesystem requirements": "## 2. Filesystem requirements"}),
    "FAILURE_MATRIX": (HB, HNS + "R2_FAILURE_MATRIX.json", {}),
    "FORMAL_RECORD": (HB, HNS + "formal_review_followup_5/FORMAL_DELTA_REVIEW_RECORD.md", {
        "disposition": "**Final disposition: FORMAL_DELTA_REVIEW_ACCEPTED_WITH_NONBLOCKING_FOLLOWUPS**",
        "C1": "| C1 | **blocking-before-incorporation**", "C2": "| C2 | **before-freeze**", "C3": "| C3 | **before-freeze**",
        "SF1 ruling": "- **SF1 ruling: `SF1: NON_BLOCKING`.**", "re-pin ruling": "- **Re-pin ruling: `RE-PIN: ACCEPTED`.**",
        "owner decisions gating": "**Owner decisions that still gate the official qualification.**",
        "filing into r2 governance": "these files can be copied into r2's `governance/`"}),
    "FORMAL_REVIEW": (HB, HNS + "formal_review_followup_5/REVIEW_FORMAL_DELTA_FOLLOWUP_5.md", {
        "line 2 disposition": "FORMAL_DELTA_REVIEW_ACCEPTED_WITH_NONBLOCKING_FOLLOWUPS",
        "SF1 remedy": "- **SF1 (non-blocking): ledger appendability is not probed.**",
        "C1": "- **C1 — blocking-before-incorporation.**", "C2": "- **C2 — before-freeze.**", "C3": "- **C3 — before-freeze.**"}),
    "FORMAL_PACKET": (HB, HNS + "r2_candidate_followup/FORMAL_DELTA_REVIEW_PACKET.md", {"S1-SF1 proposed fix": "| S1-SF1 |"}),
    "F_DRILL_ORDER_REVIEW": (HB, HNS + "r2_candidate/F_DRILL_ORDER_REVIEW.md", {
        "current order": "## 2. The exact current order", "corrected order": "## 4. The proposed and applied corrected order"}),
    "PROBE_REVIEW": (HB, HNS + "r2_candidate_followup/FILESYSTEM_PRELAUNCH_PROBE_REVIEW.md", {}),
    "REPIN_SUPPLEMENT_5": ("a119e9789e2a1d42b584fff8a2301946a37f1bcb", NS2 + "governance/R2_REPIN_LIST_SUPPLEMENT_5.json", {}),
}
res = {"schema": "P309_R2_OWNER_DECISION_EVIDENCE_MAP/1",
       "built_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
       "refs": {"r2": R2, "candidate": "a119e9789e2a1d42b584fff8a2301946a37f1bcb",
                "r1": "c902fe2fe33003ac7e4e61f29c10c81682fc940c", "main": "1cb453826313c189f0bdafd5b84120c1edb74da9",
                "hardening_formal_record": HB},
       "sources": {}, "missing_anchors": []}
for sid, (commit, path, anchors) in SOURCES.items():
    text = git("show", f"{commit}:{path}")
    lines = text.splitlines()
    ent = {"commit": commit, "path": path, "sha256": hashlib.sha256(text.encode()).hexdigest(),
           "git_blob": git("rev-parse", f"{commit}:{path}").strip(),
           "last_commit_touching": git("log", "-1", "--format=%h %cI", commit, "--", path).strip(), "anchors": {}}
    for name, needle in anchors.items():
        hits = [i + 1 for i, l in enumerate(lines) if needle in l]
        ent["anchors"][name] = hits[0] if hits else None
        if not hits:
            res["missing_anchors"].append(f"{sid}: {name}")
    res["sources"][sid] = ent
res["owner_answer_files_in_r2"] = [p for p in git("ls-tree", "-r", "--name-only", R2, NS2 + "governance/").split()
                                   if "ANSWER" in p.upper() or "OWNER_OD" in p.upper()]
out.write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
print("sources", len(res["sources"]), "missing anchors:", res["missing_anchors"], "answer files in r2:",
      res["owner_answer_files_in_r2"])
