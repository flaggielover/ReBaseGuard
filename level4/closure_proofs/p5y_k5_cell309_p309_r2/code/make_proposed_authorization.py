"""Prepare the PROPOSED execution grant for the owner's separate decision (owner decisions: "prepare the complete
proposed execution grant ... Then STOP").  This tool never writes the grant file and never commits anything: it writes
a proposal under handoff/ (the path deliberately avoids the word the push procedure refuses).

  python3 code/make_proposed_authorization.py

Precondition: HEAD is the qualification-review commit (or record / grant-window commits on top of it, rev. 2c A8 as
amended) whose review says QUALIFICATION_ACCEPTED.  The cell interval is read here from the pinned cells.json (a structural read, ledgered, after
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
    fz = D.recorded_freeze()                              # R4 B7(c): the independently recorded freeze
    m = D.load_manifest()
    pins = D.pin_table(m)
    head = git("rev-parse", "HEAD")
    # the check_grant chain read backwards from HEAD: [window / record commits] <- Rv <- [records] <- Q <- [records]
    # <- FR <- F (rev. 2c A8 as amended for R4 B5); the grant commit will be HEAD's child
    seq, c = [], head
    while c != fz:
        seq.append((c, D._chain_kind(c, REPO)))
        pl = git("rev-list", "--parents", "-n", "1", c).split()
        if len(pl) != 2 or len(seq) > 256:
            print("REFUSED: a merge or root commit, or no path to the recorded freeze")
            return 2
        c = pl[1]
    i = 0
    while i < len(seq) and seq[i][1] in ("record", "window"):
        i += 1
    j = i + 1
    while j < len(seq) and seq[j][1] == "record":
        j += 1
    k = j + 1
    while k < len(seq) and seq[k][1] == "record":
        k += 1
    if i >= len(seq) or j >= len(seq) or k != len(seq) - 1 or seq[k][1] != "freeze_record":
        print("REFUSED: HEAD is not freeze -> record -> qualification -> review (plus record / window commits)")
        return 2
    review_c, qual_c = seq[i][0], seq[j][0]
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
        "schema": "P309_GRANT/1", "campaign": "p5y_k5_cell309_p309_r2", "cell": D.TARGET_CELL, "detector": "CUSUM",
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
                                          "re-run is repeated there before execute",
                           "host_rerun_commit": "<only if the owner names another host: the grant-window commit of "
                                                "qualification/host_rerun/<host id>/QC10_HOST_RERUN.json, which must be "
                                                "a PASS (delta-2 E6); a failed host re-run blocks the grant>"},
        "runtime": {"python": platform.python_version()},
        "marker_ref": G.PRODUCTION_MARKER,
        "exactly_once": fp["exactly_once"], "executions_authorized": 1,
        "in_band_verification": "genuine certificates only; no mutant battery; no shifted or widened probe",
        "non_reattribution": "Stage-1 material of the cell is bound to it and never reused for another cell",
        "outcome_table": fp["outcome_table"],
        "u2": fp["u2"], "independence_statement": fp["independence_statement"], "efficacy": fp["efficacy"],
        "disclosed_liabilities": fp["disclosed_liabilities"],
        "incident_review_conditions_verbatim": fp["reviews"]["incident_independence"]["conditions_verbatim"] + "\n"
                                               + fp["reviews"]["delta_incident_independence"]["conditions_verbatim"]
                                               + "\n" + fp["reviews"]["delta2_incident_independence"][
                                                   "conditions_verbatim"]
                                               + "\n" + fp["reviews"]["delta3_incident_independence"][
                                                   "conditions_verbatim"]
                                               + "\n" + fp["reviews"]["delta4_incident_independence"][
                                                   "conditions_verbatim"]
                                               + "\n" + fp["reviews"]["delta5_incident_independence"][
                                                   "conditions_verbatim"],
        "prefreeze_review_conditions_verbatim": fp["reviews"]["prefreeze_r4"]["conditions_verbatim"] + "\n"
                                                + fp["reviews"]["prefreeze_r4_followup"]["conditions_verbatim"]
                                                + "\n" + fp["reviews"]["prefreeze_r4_followup_2"][
                                                    "conditions_verbatim"]
                                                + "\n" + fp["reviews"]["prefreeze_r4_followup_3"][
                                                    "conditions_verbatim"]
                                                + "\n" + fp["reviews"]["prefreeze_r4_followup_4"][
                                                    "conditions_verbatim"],
        "horizon_notice": "a run longer than the grant's remaining validity turns the per-call expiry check into "
                          "EXECUTION_INDETERMINATE or a silent SRK loss; not_after_utc must be at least 14 days after "
                          "execute starts, and a longer horizon is the owner's choice (delta-2 E7)",
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
            "post_execution_checks": "GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null python3 -I -S -B "
                                     "code/p309_postexec.py (the git environment fixed in advance, delta-5 I3; "
                                     "P1-P10; P10 = review-mode "
                                     "re-verification; refuses to start without these flags)",
            "grant_validation": "BEFORE the grant commit (R4 follow-up F2): on the named host, in the named "
                                "worktree, with the branch attached and HEAD at the would-be parent of the grant "
                                "commit, save the candidate grant as a file OUTSIDE the worktree and run `python3 -I "
                                "-S -B code/p309_driver.py validate-grant --grant <that file>`. It creates no commit "
                                "and no ref and runs nothing of Stage 1 or 2. It checks the candidate's CONTENT and "
                                "the chain below it (execute's shared grant-content checks, the chain walk from HEAD, "
                                "the guard's field parser and the guard's checks 2, 3, 5-9), and runs execute's "
                                "read-only pre-marker checks under execute's conditions: the interpreter flags, the "
                                "host git configuration, the branch, not-evaluated, the result paths, a clean tree, "
                                "the input bindings and the governance state. It does NOT check what only execute "
                                "checks: the guard's check 4 (the grant commit itself: the only change of a "
                                "single-parent commit on this HEAD), the consumer-cover agreement and the historical "
                                "control. A PASS therefore does NOT guarantee admission. Only on `P309 VALIDATE-GRANT "
                                "PASS`: commit the ledger lines it wrote as ONE ledger-only commit, then copy the "
                                "candidate byte-identically to the grant path and commit it ALONE on top (single "
                                "parent, attached branch, nothing pushed past it). A grant commit that execute refuses "
                                "is TERMINAL: it cannot be repaired or superseded without a new owner decision (a "
                                "second grant commit breaks the chain). execute re-evaluates the 14-day horizon and the "
                                "expiry when it starts, so the grant commit and execute should follow a PASS promptly "
                                "(delta-4 H4)",
            "host_git": "execute's git ignores the host's system and global git configuration and commits with the "
                        "fixed identity p309-execute and no signature; the repository's own configuration, in the "
                        "local or worktree scope, may hold only the keys matching the driver's REPO_CONFIG_ALLOWED "
                        "(listed exactly in host_git_allowed_keys) and the hooks directory must hold no hook; git >= "
                        "2.32; validate-grant reports any violation before the grant commit (rev. 2c A40). "
                        "seal-only runs the same check before its first git call (A43). execute repeats it after the "
                        "historical control, just before its first git write (a refusal there is before the marker, "
                        "so no marker is created, but it spends the grant, as any execute refusal does, and a failing "
                        "historical control is then not recorded), and after the marker just before the evidence "
                        "persist: a refusal there "
                        "writes the evidence to the emergency file and exits 4 (UNSEALED); remove the hook or key, "
                        "then run seal-only, which refuses until the host is clean (A44). The guard's git also "
                        "ignores the host's system and global configuration (A45)",
            "host_git_allowed_keys": list(D.REPO_CONFIG_ALLOWED),
            "execution_procedure": "on the named host, in the named worktree, on the named branch with HEAD attached "
                                   "at the grant commit (made after a validate-grant PASS, above); remove every "
                                   "__pycache__ from the campaign namespace first (check_clean refuses ignored "
                                   "objects); run nothing ledgered between the grant commit and execute; then "
                                   "`python3 -I -S -B code/p309_driver.py execute`; after a seal, "
                                   "`GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null python3 -I -S -B "
                                   "code/p309_postexec.py`; never run execute twice (R4 NB15)",
            "execution_review": "research protocol_prep/P309_REVIEW_BRIEFS.md section 3 (brief committed before "
                                "issue)", "adjudication": "package section H; the protocol section 5 table verbatim",
            "adjudication_review": "research protocol_prep/P309_REVIEW_BRIEFS.md section 4"},
        "issued_utc": "<SET BY THE OWNER, ISO-8601 UTC YYYY-MM-DDTHH:MM:SSZ, not in the future>",
        "not_after_utc": "<SET BY THE OWNER, ISO-8601 UTC YYYY-MM-DDTHH:MM:SSZ, at least 14 days after execute starts>",
        "grant_rules": "the driver refuses before the marker (exit 2, nothing consumed) unless: every field above is "
                       "exact (geometry the exact strings, cell the integer, verifier_id / guard_id the pinned "
                       "sha256, marker_ref the production marker NAME, host id, worktree and runtime of the execution "
                       "host); not_after_utc >= now + 14 days at arming (rev. 2c amendment, R4 B3); issued_utc not in "
                       "the future; authority a non-empty reference to the owner's grant instruction (only the "
                       "proposal's own placeholder text is refused; quoting the owner, with < > or ->, is allowed); "
                       "execution_host.worktree present; the grant "
                       "commit is the only change of a single-parent commit on top of this chain, HEAD attached to "
                       "the branch, and no ref points past it",
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
