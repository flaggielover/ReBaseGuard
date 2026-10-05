"""OWNER_DECISION_EVIDENCE_MAP.json = the git-computed sources (make_evidence_map.py output) + one structured entry per
decision, with consistency checks (each decision in exactly one phase; every cited source anchor resolves; every
dependency names a known item).  Nothing here records or infers an owner answer: status is the repository's.

usage: make_decision_map.py <sources_raw.json> <out.json>
"""
import json
import sys
from pathlib import Path

src = json.loads(Path(sys.argv[1]).read_text())
G = ("incorporation", "freeze", "worker_tier_drill", "qualification", "grant", "target_evaluation")


def gates(*on):
    return {g: g in on for g in G}


D = [
    ("OD-R2-0(A)", "A", [("R2_PACKET", "OD-R2-0(A)"), ("MSG_4", "msg4 decides none of OD-R2-0..6")],
     ["CONFIRM", "CORRECT"], "CONFIRM", gates("freeze", "qualification"), [], True),
    ("OD-R2-0(B)", "A", [("R2_PACKET", "OD-R2-0(B)"), ("R2_PACKET", "OD-R2-0 carry-over table")],
     ["CONFIRM ALL ROWS", "CONFIRM EXCEPT <row>"], "CONFIRM ALL ROWS", gates("freeze", "qualification"), [], True),
    ("OD-R2-0(C)", "A", [("R2_PACKET", "OD-R2-0(C)"), ("R2_PACKET", "OD-R2-0 liabilities")],
     ["ACKNOWLEDGE", "ACKNOWLEDGE WITH ADDITIONS", "DECLINE"], "ACKNOWLEDGE WITH ADDITIONS",
     gates("freeze", "qualification"), [], True),
    ("OD-R2-0(D)", "D", [("R2_PACKET", "OD-R2-0(D)"), ("FORMAL_RECORD", "C1"), ("FORMAL_RECORD", "C2"),
                         ("FORMAL_RECORD", "C3"), ("DURABLE_HOST_PACKET", "prerequisites P0"),
                         ("R2_HOST_SESSION", "owner-gated after 8d (incl. gate step 9 pre-freeze follow-up review)")],
     ["AUTHORIZE (packet text verbatim)", "DECLINE"], "leave OPEN until prerequisites P-1..P-11 hold",
     gates("freeze", "qualification"),
     ["OD-R2-0(A)", "OD-R2-0(B)", "OD-R2-0(C)", "OD-R2-1", "OD-R2-1b", "OD-R2-2", "OD-R2-3", "OD-R2-4", "OD-R2-5",
      "OD-R2-6(iii)", "OD-R2-H", "SF1", "AF-3"], False),
    ("OD-R2-1", "A", [("R2_PACKET", "OD-R2-1"), ("R2_AMENDMENTS", "§A provisional OD-R2-1 (b) names")],
     ["(b)", "(a)", "(c)"], "(b)", gates("freeze", "qualification", "grant", "target_evaluation"), [], True),
    ("OD-R2-1b", "A", [("R2_PACKET", "OD-R2-1b")], ["CONFIRM", "NAME OTHERS"], "CONFIRM",
     gates("freeze", "qualification", "grant", "target_evaluation"), ["OD-R2-1"], True),
    ("OD-R2-2", "A", [("R2_PACKET", "OD-R2-2")], ["RATIFY", "OTHER NAMES", "DECLINE EXTENSION"], "RATIFY",
     gates("freeze", "qualification", "grant", "target_evaluation"), ["OD-R2-1"], True),
    ("OD-R2-3", "A", [("R2_PACKET", "OD-R2-3"), ("R2_HOST_SESSION", "8a audit"), ("R2_HOST_SESSION", "8b verdict + STOP"),
                      ("MSG_4", "msg4 item 13"), ("DURABLE_HOST_PACKET", "P0.4 IMDS")],
     ["APPROVE AUDIT ONLY", "APPROVE", "DECLINE"], "APPROVE AUDIT ONLY (+ ask about a dedicated host)",
     gates("worker_tier_drill", "freeze", "qualification"), [], True),
    ("OD-R2-4", "C", [("R2_PACKET", "OD-R2-4"), ("R2_PACKET", "OD-R2-4 world-readable checkout"),
                      ("R2_HOST_SESSION", "8c bootstrap"), ("DURABLE_HOST_PACKET", "P0.5 operator data")],
     ["per mutation M1..M5 and limits: CONSENT | DECLINE"],
     "after 8a: M1, M2, M3, M5 CONSENT; M4 only with the cell-308 operator per window; request operator data now",
     gates("worker_tier_drill", "freeze", "qualification"), ["OD-R2-3"], False),
    ("OD-R2-5", "A", [("R2_PACKET", "OD-R2-5"), ("MSG_1_3", "msg3 §3 exclusive heavy compute"),
                      ("MSG_1_3", "msg3 §8 do not interrupt")],
     ["(i)", "(ii) with message 3 amendment"], "(i)", gates("worker_tier_drill", "freeze", "qualification"), [], True),
    ("OD-R2-6(i)", "E", [("R2_PACKET", "OD-R2-6"), ("R2_AMENDMENTS", "§C execute on a shared host"),
                         ("R2_FREEZE_PARAMS", "OD-R2-6 answer file"), ("R2_FREEZE_PARAMS", "answer fields read")],
     ["DEFER", "(a) qualification host", "(b) dedicated host", "(c) shared worker + §C amendment"],
     "DEFER (lean (b))", gates("grant", "target_evaluation"), ["OD-R2-6(ii)"], False),
    ("OD-R2-6(ii)", "A", [("R2_PACKET", "OD-R2-6 also to decide")], ["REQUIRE", "DO NOT REQUIRE"], "REQUIRE",
     gates("grant"), [], True),
    ("OD-R2-6(iii)", "A", [("R2_PACKET", "OD-R2-6 freeze field"), ("R2_FREEZE_PARAMS", "no host named by default")],
     ["NO HOST AT FREEZE", "NAME A HOST AT FREEZE"], "NO HOST AT FREEZE", gates("freeze"), [], True),
    ("OD-R2-H", "B", [("AID_TASK2", "OD-R2-H (proposed)"), ("FORMAL_RECORD", "C1"), ("FORMAL_RECORD", "disposition"),
                      ("FORMAL_REVIEW", "line 2 disposition")],
     ["H-A (fast-forward 101ef2cb -> a119e978 under C1, nothing else)", "H-B (do not incorporate yet)"], "H-A",
     gates("incorporation", "freeze", "worker_tier_drill", "qualification"), [], True),
    ("F-DRILL-ORDER", "B", [("AID_TASK2", "F-DRILL-ORDER (proposed action)"), ("F_DRILL_ORDER_REVIEW", "current order"),
                            ("F_DRILL_ORDER_REVIEW", "corrected order"), ("FORMAL_RECORD", "re-pin ruling")],
     ["FD-A (adopted by H-A incorporation; recorded closed)", "FD-B (leave; only with H-B)"], "FD-A",
     gates("worker_tier_drill", "freeze", "qualification"), ["OD-R2-H"], True),
    ("SF1", "A", [("FORMAL_REVIEW", "SF1 remedy"), ("FORMAL_RECORD", "SF1 ruling"), ("FORMAL_RECORD", "C2"),
                  ("FORMAL_PACKET", "S1-SF1 proposed fix")],
     ["SF1-A (probe extension under its own reviewed delta)", "SF1-B (recorded host-preparation check)"],
     "SF1-A, before the 8d drill", gates("freeze", "qualification"), [], True),   # the path choice; SF1-A's resolution follows H-A
    ("AF-1", "C", [("R2_PACKET", "OD-R2-4 world-readable checkout"), ("MSG_1_3", "msg3 §6 do not alter cell 308")],
     ["AMEND MESSAGE 3 §6 (with operator consent)", "DO NOT AMEND", "NOT TRIGGERED"], "decide only if 8a triggers it",
     gates("worker_tier_drill", "freeze", "qualification"), ["OD-R2-3"], False),
    ("AF-2", "C", [("DURABLE_HOST_PACKET", "P0.4 IMDS")],
     ["COMMISSION REVIEWED PORTABILITY CHANGE", "USE AN IMDS HOST", "NOT TRIGGERED"], "decide only if the host lacks IMDS",
     gates("worker_tier_drill", "freeze", "qualification"), ["OD-R2-3"], False),
    ("AF-3", "C", [("FORMAL_RECORD", "filing into r2 governance"), ("MSG_4", "msg4 decides none of OD-R2-0..6")],
     ["AUTHORIZE separate governance-only filing after the fast-forward", "DO NOT FILE"],
     "AUTHORIZE, after the fast-forward", gates("freeze", "qualification"), ["OD-R2-H"], False),
    ("AF-4", "E", [("MSG_1_3", "msg1 READY_FOR_OWNER_GRANT_DECISION"),
                   ("R2_HOST_SESSION", "owner-gated after 8d (incl. gate step 9 pre-freeze follow-up review)")],
     ["grant / do not grant (after a passed, reviewed qualification)"], "not answerable now",
     gates("grant", "target_evaluation"), ["OD-R2-0(D)", "OD-R2-6(i)", "OD-R2-6(ii)"], False),
    ("AF-5", "E", [("R2_PACKET", "OD-R2-0 carry-over table")], ["r3 / no r3 (only after a failed r2 qualification)"],
     "not answerable now", gates(), ["OD-R2-0(D)"], False),
]
known = {d[0] for d in D}
problems = []
decisions = []
for did, phase, cites, options, rec, gt, deps, now in D:
    if phase not in "ABCDE":
        problems.append(f"{did}: bad phase")
    for s, a in cites:
        if s not in src["sources"] or (a and src["sources"][s]["anchors"].get(a) is None):
            problems.append(f"{did}: unresolved source {s}:{a}")
    for x in deps:
        if x not in known:
            problems.append(f"{did}: unknown dependency {x}")
    decisions.append({"id": did, "phase": phase, "repository_status": "OPEN", "decidable_now": now,
                      "sources": [{"source": s, "anchor": a, "line": src["sources"][s]["anchors"].get(a),
                                   "commit": src["sources"][s]["commit"], "path": src["sources"][s]["path"]}
                                  for s, a in cites],
                      "options": options, "recommendation_only": rec, "gates": gt, "depends_on": deps,
                      "additional_finding": did.startswith("AF-")})
ids = [d["id"] for d in decisions]
if len(ids) != len(set(ids)):
    problems.append("duplicate decision id")
required = ["OD-R2-0(A)", "OD-R2-0(B)", "OD-R2-0(C)", "OD-R2-0(D)", "OD-R2-1", "OD-R2-1b", "OD-R2-2", "OD-R2-3",
            "OD-R2-4", "OD-R2-5", "OD-R2-6(i)", "OD-R2-6(ii)", "OD-R2-6(iii)", "OD-R2-H", "F-DRILL-ORDER", "SF1"]
missing = [r for r in required if r not in ids]
out = dict(src)
out["schema"] = "P309_R2_OWNER_DECISION_EVIDENCE_MAP/1"
out["statement"] = ("No decision is recorded or inferred: repository_status is OPEN for every item (no owner answer "
                    "file in r2; message 4 decides none of OD-R2-0..6). recommendation_only is a recommendation, "
                    "never an answer. Nothing here authorizes incorporation, freeze, qualification, grant or Γ(309).")
out["decisions"] = decisions
out["phases"] = {p: [d["id"] for d in decisions if d["phase"] == p] for p in "ABCDE"}
out["consistency"] = {"problems": problems, "required_items_missing": missing,
                      "every_decision_in_exactly_one_phase": all(sum(d["id"] in v for v in out["phases"].values()) == 1
                                                                 for d in decisions),
                      "owner_answer_files_in_r2": src["owner_answer_files_in_r2"]}
Path(sys.argv[2]).write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
print(json.dumps(out["phases"], ensure_ascii=False))
print("problems:", problems, "missing:", missing, "one phase each:", out["consistency"]["every_decision_in_exactly_one_phase"])
