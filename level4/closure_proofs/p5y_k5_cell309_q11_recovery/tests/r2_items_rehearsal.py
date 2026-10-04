#!/usr/bin/env python3
"""Post-freeze rehearsal of r2's light qualification items through r2's own item table (scratch replica only).

  python3 r2_items_rehearsal.py --replica R2_REPLICA_AT_SYNTHETIC_FREEZE --work NEW_SCRATCH_DIR --out RESULT.json

The replica is the one r2_postfreeze_rehearsal.py prepared (101ef2cb + synthetic F' + FR' + checkpoint commit).
Items: every item except QC06, QC08, QC09 and QC10 (the decoy batteries; their code path is byte-identical to r1's,
whose run is Run B) -- the same split as r2's own cloud-tier drill.  Each item runs through r2's items_table() /
run_item() (the runner's own lambdas and its exclusive record write); r2's main() is never called (it requires the
launch unit and Q-HOST on the approved host).  Every subprocess passes a self-guard refusing the driver's target /
grant modes and the launcher.  Verdicts come from the records' content.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

SCRATCH_ROOT = Path("/tmp/claude-0")
SESSION_REPO = Path(__file__).resolve().parents[4]
R2_HEAD = "101ef2cb17e5eab2892212178278da45b98004ed"
NS2 = "level4/closure_proofs/p5y_k5_cell309_p309_r2"
RECORD_REL = NS2 + "/ledger/FREEZE_RECORD.json"
ITEMS = ["QC01", "QC02", "QC03", "QC04", "QC05", "QC07", "QC11", "QC12", "QC13", "QC14", "QC15", "QC16", "QC17",
         "QC_U2", "QC_D5"]
PROTECTED = ("refs/p5y-k5-cell30", "refs/p309-cell309", "refs/rlr-tail/")
REFUSED_MODES = {"execute", "seal-only", "validate-grant"}


def git(repo: Path, *a: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, check=True).stdout.strip()


def utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--replica", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    clone, work = Path(a.replica).resolve(), Path(a.work).resolve()
    for p in (clone, work):
        if SCRATCH_ROOT not in p.parents or SESSION_REPO in p.parents or p == SESSION_REPO:
            raise SystemExit(f"refused: {p} is not a scratch path outside the session repository")
    for url in git(clone, "remote", "-v").split():
        if "://" in url or "@" in url:
            raise SystemExit("refused: the replica has a network remote")
    if subprocess.run(["git", "-C", str(clone), "merge-base", "--is-ancestor", R2_HEAD, "HEAD"]).returncode:
        raise SystemExit("refused: the replica does not descend from r2 101ef2cb")
    if len(git(clone, "log", "--format=%H", "HEAD", "--", RECORD_REL).split()) != 1:
        raise SystemExit("refused: the replica is not at a (synthetic) post-freeze topology")
    if [r for r in git(clone, "for-each-ref", "--format=%(refname)").split() if r.startswith(PROTECTED)]:
        raise SystemExit("refused: protected ref in the replica")
    work.mkdir(parents=True)
    (work / "scratch").mkdir()
    for k in [k for k in os.environ if k.startswith("P309_")]:
        del os.environ[k]
    os.environ["P309_SCRATCH_ROOT"] = str(work / "scratch")
    fns = clone / NS2
    sys.path.insert(0, str(fns / "code"))
    import p309_qualify as Q  # noqa: E402  (r2's runner module, from the replica)
    if Path(Q.__file__).resolve().parent != (fns / "code").resolve():
        raise SystemExit("refused: runner not imported from the replica")
    real_run = Q.run

    def guarded(cmd, cwd, timeout=6 * 3600):
        flat = [str(c) for c in cmd]
        for i, c in enumerate(flat):
            if c.endswith("p309_driver.py") and i + 1 < len(flat) and flat[i + 1] in REFUSED_MODES:
                raise RuntimeError("self-guard: driver target / grant mode refused")
            if c.endswith(("p309_launch.py", "p309_qualify.py")):
                raise RuntimeError("self-guard: launcher / runner main refused")
        return real_run(cmd, cwd, timeout)
    Q.run = guarded
    att = work / "attempt"
    att.mkdir()
    (att / "evidence").mkdir()
    Q.ATT["dir"], Q.ATT["label"] = att, "rehearsal (scratch r2 replica; not qualification)"
    freeze = Q.D.recorded_freeze()
    Q.E.log("code/p309_qualify.py", f"{Q.RUN_START} attempt_rehearsal at the recorded freeze {freeze[:12]} (scratch "
            "replica rehearsal; not qualification)", klass="GOVERNANCE", notes="independent post-freeze rehearsal")
    m = Q.mirror(freeze)
    table = Q.items_table(m, freeze, 4)
    t0, recs = time.time(), {}
    for k in ITEMS:
        recs[k] = Q.run_item(k, table[k], freeze)
    content = {}
    fl = att / "evidence" / "fc6" / "EXACTLY_ONCE_FLOWS.json"
    if fl.exists():
        d = json.loads(fl.read_text())
        bad = [n for n, x in d.get("results", {}).items() if x.get("pass") is not True]
        content["QC11"] = {"all_pass": d.get("all_pass"), "flows": d.get("flows"), "failed": bad}
    content["QC13_checks_not_true"] = sorted(k for k, x in (recs["QC13"].get("checks") or {}).items() if x is not True)
    content["QC_D5_parts"] = [bool(x.get("pass")) for x in recs["QC_D5"].get("parts", [])]
    content["QC17"] = {k: recs["QC17"].get(k) for k in ("cases", "mismatches")}
    refs_after = [r for r in git(clone, "for-each-ref", "--format=%(refname)").split() if r.startswith(PROTECTED)]
    res = {"schema": "P309_R2_ITEMS_REHEARSAL/1", "kind": "development rehearsal (scratch replica)",
           "replica_head": git(clone, "rev-parse", "HEAD"), "recorded_freeze": freeze, "items": ITEMS,
           "gates": {k: bool(v.get("pass")) and v.get("freeze_commit") == freeze for k, v in recs.items()},
           "errors": {k: v.get("error") for k, v in recs.items() if v.get("error")},
           "content": content, "records_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                                  for p in sorted(att.glob("*.json"))},
           "wall_s": round(time.time() - t0, 1), "python": platform.python_version(),
           "boot_id": Path("/proc/sys/kernel/random/boot_id").read_text().strip(),
           "replica_protected_refs_after": refs_after, "utc_end": utc(),
           "tool_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "new_target_evaluations": 0}
    res["pass"] = all(res["gates"].values()) and not refs_after and not content.get("QC11", {}).get("failed", [1])
    Path(a.out).write_text(json.dumps(res, indent=1, sort_keys=True, default=str) + "\n")
    print(json.dumps({"pass": res["pass"], "gates": res["gates"], "errors": res["errors"]}, indent=1))
    return 0 if res["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
