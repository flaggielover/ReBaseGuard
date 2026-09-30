"""Prepare the PROPOSED execution grant for the owner's separate decision (owner decisions: "prepare the complete
proposed execution grant ... Then STOP").  This tool never writes the grant file and never commits anything: it writes
a proposal under handoff/ (the path deliberately avoids the word the push procedure refuses).

  python3 code/make_proposed_authorization.py

Precondition: HEAD is the qualification-review commit (or a checkpoint-record commit on top of it) whose review says
QUALIFICATION_ACCEPTED.  The cell interval is read here from the pinned cells.json (a structural read, ledgered, after
the freeze; incident review C4).  The owner sets issued_utc, not_after_utc and the authority text, and makes the grant
commit: the file authorization/P309_GRANT.json, alone, as the only change of a commit whose parent is HEAD.
"""
from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from fractions import Fraction as F
from pathlib import Path

FNS = Path(__file__).resolve().parents[1]
REPO = FNS.parents[2]
sys.path.insert(0, str(FNS / "code"))
import p309_env as E  # noqa: E402
import p309_driver as D  # noqa: E402
import p309_guard as G  # noqa: E402


def git(*a) -> str:
    return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True, check=True).stdout.strip()


def main() -> int:
    fz = D.freeze_commit()
    m = D.load_manifest()
    pins = D.pin_table(m)
    head = git("rev-parse", "HEAD")
    # find the qualification and review commits on the first-parent chain back to the freeze
    chain, c = [], head
    for _ in range(64):
        if not D._only(c, (D.CHECKPOINT_LEDGER_REL,), REPO):
            c = git("rev-parse", f"{c}^")
            continue
        if c == fz:
            break
        chain.append(c)
        c = git("rev-parse", f"{c}^")
    if len(chain) != 2:
        print("REFUSED: HEAD is not freeze -> qualification -> review (plus record commits)")
        return 2
    review_c, qual_c = chain
    if not D.verdict_ok(git("show", f"{review_c}:{D.QREVIEW_REL}"), "QUALIFICATION_ACCEPTED"):
        print("REFUSED: the qualification review is not QUALIFICATION_ACCEPTED")
        return 2
    q = json.loads(git("show", f"{qual_c}:{D.QUAL_REL}"))
    if q.get("pass") is not True or q.get("freeze_commit") != fz:
        print("REFUSED: the qualification report is not a PASS at the freeze commit")
        return 2
    E.exposure(head, "cells.json (pinned) entry for the target cell", content="the cell interval (two exact "
               "rationals; structural); nothing else", necessity="the proposed grant names the cell interval and Ew "
               "(incident review C4: after the freeze, ledgered)", carried_309_numbers=True)
    cells = json.loads(D.read_pinned(pins, D.data_rel(m, "cells_json")))
    rows = [c for c in cells if c["detector"] == "CUSUM" and c["index"] == D.TARGET_CELL]
    lo, hi = D.cover_interval(rows[0])                   # the canonical sum form (FE-9)
    import srk_certify as S
    wb, _ = S.cell_blocks(lo, hi)
    fp = json.loads((FNS / "freeze" / "P309_FREEZE.json").read_text())
    grant = {
        "schema": "P309_GRANT/1", "campaign": "p5y_k5_cell309_p309_r1", "cell": D.TARGET_CELL, "detector": "CUSUM",
        "m": 5, "route": "P309 package 1", "closure_only": True,
        "closure_criterion": "Gamma < 0, exact and strict (protocol rev. 2b section 4.6)",
        "adoption": "NOT AUTHORIZED", "floor_change": "NOT AUTHORIZED", "r6": "NOT AUTHORIZED",
        "k5_or_p5y_closure": "NOT AUTHORIZED",
        "geometry": {"h": "5", "k": "1/2"},
        "cell_interval": [D.fs(lo), D.fs(hi)], "drift_hull_Ew": [D.fs(wb[0]), D.fs(wb[1])],
        "ew_overlap_note": "Ew may overlap a neighbouring cell's drift range; that overlap confers no licence to reuse "
                           "(protocol section 1: non-re-attribution)",
        "frozen_commit": fz, "freeze_tree": git("rev-parse", f"{fz}^{{tree}}"),
        "frozen_manifest_path": D.MANIFEST_REL, "frozen_manifest_sha256": m["_sha256"],
        "qualification_commit": qual_c, "qualification_review_commit": review_c,
        "driver_path": D.NS_REL + "/code/p309_driver.py",
        "driver_sha256": pins[D.NS_REL + "/code/p309_driver.py"][0],
        "verifier_id": "sha256:" + pins[D.VARIANT_REL][0],
        "guard_id": "sha256:" + pins[D.NS_REL + "/code/p309_guard.py"][0],
        "evaluator": "python3 -I -S -B " + D.NS_REL + "/code/p309_driver.py execute (on the named host, in the named "
                     "worktree, with HEAD at this grant commit)",
        "execution_host": {"host_id_sha256": G.host_id(), "worktree": str(REPO),
                           "description": "the proposed host: this isolated cloud environment (rev. 2c A14); isolated "
                                          "from the other live campaign's machine (owner decisions: execution "
                                          "host); if the owner names another host, QC10's host "
                                          "re-run is repeated there before execute"},
        "runtime": {"python": platform.python_version()},
        "marker_ref": G.PRODUCTION_MARKER,
        "exactly_once": fp["exactly_once"], "executions_authorized": 1,
        "in_band_verification": "genuine certificates only; no mutant battery; no shifted or widened probe",
        "non_reattribution": "Stage-1 material of the cell is bound to it and never reused for another cell",
        "outcome_table": fp["outcome_table"],
        "u2": fp["u2"], "independence_statement": fp["independence_statement"], "efficacy": fp["efficacy"],
        "disclosed_liabilities": fp["disclosed_liabilities"],
        "incident_review_conditions_verbatim": fp["reviews"]["incident_independence"]["conditions_verbatim"] + "\n"
                                               + fp["reviews"]["delta_incident_independence"]["conditions_verbatim"],
        "u2_check_conditions_verbatim": fp["reviews"]["u2_check"]["conditions_verbatim"],
        "delta_review": fp["reviews"]["delta_incident_independence"],
        "prefreeze_review": fp["reviews"]["prefreeze_r4"],
        "qualification_review": {"path": D.QREVIEW_REL, "commit": review_c,
                                 "verdict_line": git("show", f"{review_c}:{D.QREVIEW_REL}").splitlines()[1]},
        "procedures": {
            "historical_control": "driver: post-grant, pre-marker; rev. 2c A12; CONTROL_FAILED -> exit 3, not consumed",
            "stage1a": "protocol 2 + rev. 2c; freeze/P309_FREEZE.json stage1a", "stage1b": "protocol 3 + rev. 2c A4-A5",
            "stage2": "protocol 4 + rev. 2c A11-A13", "cpu_budget": fp["stage1a"]["budget"],
            "cpu_budget_stage1b": fp["stage1b"]["budget"],
            "failure_and_recovery": "package section I; exit codes " + json.dumps(fp["exactly_once"]["exit_codes"]),
            "recording": "package section E (from memory: object store + pending ref, emergency file, private-index "
                         "seal commit, O_EXCL materialization)",
            "post_execution_checks": "code/p309_postexec.py (P1-P10; P10 = review-mode re-verification)",
            "execution_review": "research protocol_prep/P309_REVIEW_BRIEFS.md section 3 (brief committed before "
                                "issue)", "adjudication": "package section H; the protocol section 5 table verbatim",
            "adjudication_review": "research protocol_prep/P309_REVIEW_BRIEFS.md section 4"},
        "issued_utc": "<SET BY THE OWNER>", "not_after_utc": "<SET BY THE OWNER, ISO-8601 UTC, e.g. 2026-10-31T23:59:59Z>",
        "granted_after": review_c,
        "authority": "<THE OWNER'S GRANT INSTRUCTION, verbatim reference>",
    }
    out = FNS / "handoff"
    out.mkdir(exist_ok=True)
    data = json.dumps(grant, indent=1, sort_keys=True, ensure_ascii=False) + "\n"
    (out / "PROPOSED_EXECUTION_AUTHORIZATION_P309.json").write_text(data)
    print(json.dumps({"proposal": str((out / "PROPOSED_EXECUTION_AUTHORIZATION_P309.json").relative_to(REPO)),
                      "sha256": hashlib.sha256(data.encode()).hexdigest(), "frozen_commit": fz,
                      "qualification_commit": qual_c, "review_commit": review_c}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
