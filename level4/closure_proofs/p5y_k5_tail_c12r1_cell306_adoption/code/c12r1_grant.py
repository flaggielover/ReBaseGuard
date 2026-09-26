"""C12-R1 -- the grant: written and committed ALONE, mechanically, only in the state the protocol permits.

Run once, in the qualified worktree, at HEAD = the commit preserving a QUALIFICATION_ACCEPTED review. It reuses the
driver's own checks (identity, no prior evaluation, clean tree, bindings, governance state), requires the chain
freeze -> qualification -> review exactly as the driver will later verify it, writes authorization/C12R1_GRANT.json
and commits that one file. It evaluates nothing. The user's overnight campaign instruction is the authorization it
records; the grant itself was frozen and qualified with the campaign (no separate authorization review).

    python3.14 -I -S -B c12r1_grant.py
"""
import datetime
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
spec = importlib.util.spec_from_file_location("c12r1_driver_for_grant", HERE.parent / "c12r1_cell306.py")
D = importlib.util.module_from_spec(spec)
spec.loader.exec_module(D)


def main() -> int:
    try:
        D.check_identity()
        D.check_not_evaluated()
        D.check_clean()
        D.check_bindings()
        D.check_governance_state()
        if (D.REPO / D.GRANT_REL).exists() or D.git("log", "--all", "--format=%H", "--", D.GRANT_REL).stdout.strip():
            raise D.Refusal("GRANT_EXISTS", "a grant already exists (tree, disk or history)")
        head = D.git("rev-parse", "HEAD").stdout.strip()
        qual_c = D.git("rev-parse", "HEAD^").stdout.strip()
        fz = D.freeze_commit()
        if D.git("rev-parse", "HEAD^^").stdout.strip() != fz:
            raise D.Refusal("CHAIN", "HEAD^^ is not the freeze commit")
        if D.git("diff-tree", "--no-commit-id", "--name-only", "-r", head).stdout.split() != [D.QREVIEW_REL]:
            raise D.Refusal("CHAIN", "HEAD is not the review commit (it must change only the review)")
        if not D.verdict_ok((D.REPO / D.QREVIEW_REL).read_text(), "line2", "QUALIFICATION_ACCEPTED"):
            raise D.Refusal("REVIEW_VERDICT", "the qualification review is not QUALIFICATION_ACCEPTED")
        qfiles = D.git("diff-tree", "--no-commit-id", "--name-only", "-r", qual_c).stdout.split()
        if not qfiles or any(not f.startswith(D.NS_REL + "/evidence/qualification/") for f in qfiles):
            raise D.Refusal("CHAIN", "HEAD^ is not the qualification-evidence commit")
        q = json.loads(D.git("show", f"{qual_c}:{D.QUAL_REL}").stdout)
        if q.get("pass") is not True or q.get("dry_run") is not False or q.get("freeze_commit") != fz:
            raise D.Refusal("CHAIN", "the qualification report is not a PASS at the freeze commit")
    except D.Refusal as e:
        print(f"C12R1 GRANT REFUSED {e}")
        return 2
    ns = D.REPO / D.NS_REL
    sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()   # noqa: E731
    grant = {
        "schema": "rebaseguard.p5y.k5.tail-c12r1.grant.v1", "exactly_once": True,
        "campaign": "C12-R1 -- cell-306 adoption under K5 tail adoption floor r2",
        "freeze_commit": fz, "qualification_commit": qual_c, "qualification_review_commit": head,
        "qualification_review_verdict": "QUALIFICATION_ACCEPTED",
        "driver_sha256": sha(ns / "code/c12r1_cell306.py"),
        "verifier_sha256": sha(ns / "code/c12r1_verify.py"),
        "r6_generator_sha256": sha(ns / "code/c12r1_r6_from_adjudication.py"),
        "grant_generator_sha256": sha(HERE),
        "protocol_sha256": sha(ns / "protocol/C12R1_PROTOCOL.md"),
        "freeze_record_sha256": sha(ns / "protocol/C12R1_FREEZE.json"),
        "qualified_identity": {"worktree": D.QUALIFIED_WORKTREE, "git_dir": D.QUALIFIED_GIT_DIR,
                               "common_dir": D.QUALIFIED_COMMON_DIR, "branch": D.QUALIFIED_BRANCH},
        "authorization": {
            "source": "the user's overnight K5 tail campaign instruction in chat (C12-R1 Phase A2): create the "
                      "prospective grant according to the qualified protocol after QUALIFICATION_ACCEPTED is preserved",
            "authorizes": "exactly one `python3.14 -I -S -B code/c12r1_cell306.py execute` at HEAD = this grant commit, "
                          "in the qualified worktree; `seal-only` only after an UNSEALED exit",
            "target": {"cell": 306, "m": 5, "quantity": "Gamma(5, 306; S_I2)", "evaluations": 1},
            "not_authorized": ["any second execute", "deleting or moving the exactly-once marker", "cells 307-309",
                               "modifying r5", "r6 outside c12r1_r6_from_adjudication.py after the accepted chain",
                               "changing any frozen threshold, input or code"],
            "host": "this machine only", "wall_clock_cap_seconds": D.WALL_CAP_S},
        "created_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    path = D.REPO / D.GRANT_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(grant, indent=1, sort_keys=True) + "\n")
    msg = ("p5y: K5 C12-R1 — GRANT for the one cell-306 execution (exactly once)\n\n"
           f"freeze {fz}\nqualification {qual_c}\nqualification review {head} (QUALIFICATION_ACCEPTED)\n"
           f"driver sha256 {grant['driver_sha256']}\n\nWritten and committed alone by code/c12r1_grant.py.\n\n"
           "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n")
    add = D.git("add", "--", D.GRANT_REL)
    com = subprocess.run(["/usr/bin/git", "-C", str(D.REPO), "commit", "-q", "--no-verify", "-F", "-", "--", D.GRANT_REL],
                         input=msg, capture_output=True, text=True)
    if add.returncode or com.returncode:
        print(f"C12R1 GRANT COMMIT FAILED: {(add.stderr + com.stderr)[:300]}")
        return 1
    print(f"C12R1 GRANT committed {D.git('rev-parse', 'HEAD').stdout.strip()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
