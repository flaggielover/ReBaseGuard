#!/usr/bin/env python3
"""Result-free REHEARSAL of the frozen r1 qualification gates in an isolated scratch replica (not qualification).

  python3 p309_rehearsal.py --iso REPLICA --out NEW_DIR --gates all|QC11,QC_D5,... --harness frozen|repaired
                            [--workers 4] [--run-start-line]

What it is.  The r1 runner (code/p309_qualify.py) may not be launched (owner rule A27 / R4 B8: no retry, no
resumption; it would also write r1's live evidence).  This tool imports the runner's gate FUNCTIONS from a scratch
replica of r1 at the attempt's launch commit and runs them with the runner's own item table, in the runner's order,
into a NEW directory under the scratchpad.  It never calls the runner's main() or host_rerun().

  --harness frozen    the frozen QC11 sandbox builder (reproduces r1's Q11 failure)
  --harness repaired  r2's reviewed QC11 repair (sandbox base = recorded freeze F after a freeze; review P6 a/b/c),
                      ported to r1's names; swapped in for QC11 and QC-D5 only and restored byte-for-byte after

Safety (refused otherwise): the replica lies under the scratchpad root, is not the session repository, has only
local (filesystem) remotes, sits at an accepted launch commit with a clean tree, and holds no exactly-once /
production / test ref; the output directory is new.  Every gate subprocess passes a self-guard that refuses the
driver's target / grant modes.  After the run the replica is re-checked for protected refs.

Write protocol (the repair this tool demonstrates): each gate record is written to a temporary file (O_EXCL), fully
written and fsynced, then linked to its final name (never overwrites), then the directory is fsynced; only after
that is a row appended to GATE_LEDGER.jsonl (O_APPEND, fsync).  The summary is written last, the same way.  An
interruption therefore leaves either no record or a complete one (plus at most a .tmp file), and a ledger row
never precedes its record.  A rerun into an existing output directory is refused: no resumption.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import platform
import socket
import subprocess
import sys
import time
from pathlib import Path

SCRATCH_ROOT = Path("/tmp/claude-0")
SESSION_REPO = Path(__file__).resolve().parents[4]
NS_R1 = "level4/closure_proofs/p5y_k5_cell309_p309_r1"
LAUNCH_COMMITS = {"c950054ae0aa8f9e5d7171b520af3f601238a017": "r1 attempt_1 launch HEAD (FR + checkpoint record)"}
FREEZE_F = "4c754a73767903a5ad5dddff725f1e173a0a6876"
GATES = ["QC01", "QC02", "QC03", "QC04", "QC05", "QC06", "QC07", "QC08", "QC09", "QC10", "QC11", "QC12", "QC13",
         "QC14", "QC15", "QC16", "QC17", "QC_U2", "QC_D5"]
HARNESS_REL = NS_R1 + "/tests/test_p309_exactly_once.py"
REFUSED_DRIVER_MODES = {"execute", "seal-only", "validate-grant"}
PROTECTED_REF_PREFIXES = ("refs/p5y-k5-cell30", "refs/p309-cell309", "refs/rlr-tail/")


def utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha_file(p: Path) -> str:
    return sha_bytes(p.read_bytes())


def fsync_dir(d: Path) -> None:
    fd = os.open(d, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic_create(path: Path, data: bytes) -> str:
    """write `data` to `path` exactly once: tmp (O_EXCL) -> full write -> fsync -> link (fails if path exists)"""
    tmp = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
    try:
        view = memoryview(data)
        while view:
            n = os.write(fd, view)
            view = view[n:]
        os.fsync(fd)
    finally:
        os.close(fd)
    os.link(tmp, path)                 # FileExistsError if a record already exists: never overwritten
    os.unlink(tmp)
    fsync_dir(path.parent)
    return sha_bytes(data)


def ledger_append(ledger: Path, row: dict) -> None:
    line = (json.dumps(row, sort_keys=True) + "\n").encode()
    fd = os.open(ledger, os.O_WRONLY | os.O_CREAT | os.O_APPEND | os.O_NOFOLLOW, 0o644)
    try:
        os.write(fd, line)
        os.fsync(fd)
    finally:
        os.close(fd)


def record_gate(att: Path, ledger: Path, k: str, res: dict) -> str:
    """the per-gate commit point: the record (atomic, never overwritten), then its ledger row"""
    data = (json.dumps(res, indent=1, sort_keys=True, default=str) + "\n").encode()
    digest = atomic_create(att / f"{k}.json", data)
    ledger_append(ledger, {"utc": utc(), "event": "GATE_RECORDED", "gate": k, "file": f"attempt/{k}.json",
                           "sha256": digest, "pass": bool(res.get("pass")), "new_target_evaluations": 0})
    return digest


def record_summary(out: Path, ledger: Path, summary: dict) -> str:
    digest = atomic_create(out / "REHEARSAL_SUMMARY.json",
                           (json.dumps(summary, indent=1, sort_keys=True) + "\n").encode())
    ledger_append(ledger, {"utc": utc(), "event": "SUMMARY_RECORDED", "file": "REHEARSAL_SUMMARY.json",
                           "sha256": digest, "pass": summary["pass"], "new_target_evaluations": 0})
    return digest


def record_start(out: Path, ledger: Path, prov: dict) -> None:
    atomic_create(out / "PROVENANCE.json", (json.dumps(prov, indent=1, sort_keys=True) + "\n").encode())
    ledger_append(ledger, {"utc": utc(), "event": "RUN_START", "gates": prov["gates"], "harness": prov["harness"],
                           "provenance_sha256": sha_file(out / "PROVENANCE.json"), "new_target_evaluations": 0})


def git(repo: Path, *a: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, check=True).stdout.strip()


class RefusedRehearsal(SystemExit):
    pass


def refuse(why: str) -> None:
    print(f"P309 REHEARSAL REFUSED: {why}", file=sys.stderr)
    raise RefusedRehearsal(2)


def preconditions(iso: Path, out: Path) -> dict:
    iso, out = iso.resolve(), out.resolve()
    for p, what in ((iso, "replica"), (out, "output")):
        if SCRATCH_ROOT not in p.parents:
            refuse(f"the {what} {p} is not under {SCRATCH_ROOT}")
        if p == SESSION_REPO or SESSION_REPO in p.parents or p in SESSION_REPO.parents:
            refuse(f"the {what} overlaps the session repository")
    if not (iso / ".git").is_dir():
        refuse("the replica is not a standalone clone")
    for url in git(iso, "remote", "-v").split():
        if "://" in url or "@" in url:
            refuse(f"the replica has a network remote ({url}); only local filesystem remotes are accepted")
    head = git(iso, "rev-parse", "HEAD")
    if head not in LAUNCH_COMMITS:
        refuse(f"the replica HEAD {head} is not an accepted launch commit")
    if git(iso, "status", "--porcelain", "--untracked-files=all"):
        refuse("the replica working tree is not clean")
    refs = git(iso, "for-each-ref", "--format=%(refname)").split()
    bad = [r for r in refs if r.startswith(PROTECTED_REF_PREFIXES)]
    if bad:
        refuse(f"the replica holds protected refs {bad[:3]}")
    if out.exists():
        refuse(f"the output {out} exists (no resumption: a new run needs a new directory)")
    return {"iso": str(iso), "head": head, "tree": git(iso, "rev-parse", "HEAD^{tree}"),
            "launch_commit_role": LAUNCH_COMMITS[head]}


def repaired_harness(iso: Path) -> bytes:
    """r2's QC11 repair ported to r1: r2's file with r2 names mapped back to r1 and the two r2-only lines reverted"""
    r2 = (Path(__file__).resolve().parents[1] / "repair" / "test_p309_exactly_once.R2_PORTED_TO_R1.py.txt").read_bytes()
    return r2


def guard_cmd(cmd: list) -> None:
    flat = [str(c) for c in cmd]
    for k, c in enumerate(flat):
        if c.endswith("p309_driver.py") and k + 1 < len(flat) and flat[k + 1] in REFUSED_DRIVER_MODES:
            raise RuntimeError(f"self-guard: driver mode {flat[k + 1]} refused")
        if c in ("p309_launch.py", "p309_qualify.py") or c.endswith(("/p309_launch.py", "/p309_qualify.py")):
            raise RuntimeError("self-guard: the official runner / launcher is never started")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--iso", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--gates", default="all")
    ap.add_argument("--harness", choices=("frozen", "repaired", "mutant"), required=True)
    ap.add_argument("--harness-file", help="--harness mutant: the mutant harness (data file) swapped in for QC11/QC-D5")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--run-start-line", action="store_true",
                    help="append the runner's RUN START line to the replica's ledger (full rehearsals; QC13 reads it)")
    a = ap.parse_args()
    iso, out = Path(a.iso).resolve(), Path(a.out).resolve()
    gates = GATES if a.gates == "all" else [g for g in GATES if g in a.gates.split(",")]
    if a.gates != "all" and len(gates) != len(a.gates.split(",")):
        refuse(f"unknown gate in {a.gates}")
    prov = preconditions(iso, out)
    os.makedirs(out.parent, exist_ok=True)
    os.mkdir(out)                                         # exclusive
    att = out / "attempt"
    os.mkdir(att)
    os.mkdir(att / "evidence")
    ledger = out / "GATE_LEDGER.jsonl"

    fns = iso / NS_R1
    sys.path.insert(0, str(fns / "code"))
    import p309_qualify as Q  # noqa: E402  (the frozen gate functions, from the replica)
    import p309_driver as D  # noqa: E402
    if Path(Q.__file__).resolve().parent != (fns / "code").resolve():
        refuse(f"imported the runner from {Q.__file__}, not from the replica")
    freeze = D.recorded_freeze()
    if freeze != FREEZE_F:
        refuse(f"the replica's recorded freeze {freeze} is not F {FREEZE_F}")
    real_run = Q.run

    def guarded_run(cmd, cwd, timeout=6 * 3600):
        guard_cmd(cmd)
        return real_run(cmd, cwd, timeout)
    Q.run = guarded_run
    Q.ATT["dir"], Q.ATT["label"] = att, "rehearsal (scratch replica; not qualification)"
    Q.SCRATCH = out / "mirror_root"                       # the runner's hard-coded scratch path is not shared

    harness = fns / "tests" / "test_p309_exactly_once.py"
    frozen_bytes = harness.read_bytes()
    frozen_blob = git(iso, "rev-parse", f"HEAD:{HARNESS_REL}")
    if a.harness == "mutant":
        if not a.harness_file:
            refuse("--harness mutant needs --harness-file")
        repaired = Path(a.harness_file).read_bytes()
    else:
        repaired = repaired_harness(iso) if a.harness == "repaired" else None
    files_used = {rel: sha_file(fns / rel) for rel in ("code/p309_qualify.py", "code/p309_driver.py",
                                                       "tests/test_p309_exactly_once.py",
                                                       "tests/test_p309_site_backstop.py",
                                                       "tests/test_p309_d5_exception.py")}
    prov.update({
        "schema": "P309_REHEARSAL_PROVENANCE/1", "kind": "REHEARSAL (scratch replica; not qualification evidence)",
        "utc_start": utc(), "recorded_freeze": freeze, "gates": gates, "harness": a.harness,
        "harness_frozen_sha256": sha_bytes(frozen_bytes), "harness_frozen_blob": frozen_blob,
        "harness_repaired_sha256": sha_bytes(repaired) if repaired else None, "files_used_sha256": files_used,
        "orchestrator_sha256": sha_file(Path(__file__)), "session_repo_head": git(SESSION_REPO, "rev-parse", "HEAD"),
        "runtime": {"python": platform.python_version(), "implementation": platform.python_implementation(),
                    "executable": sys.executable, "platform": platform.platform(), "machine": platform.machine(),
                    "hostname_sha256": sha_bytes(socket.gethostname().encode()),
                    "boot_id": Path("/proc/sys/kernel/random/boot_id").read_text().strip(),
                    "host_id_sha256": D.G.host_id(), "nproc": os.cpu_count(), "workers": a.workers},
        "new_target_evaluations": 0})
    record_start(out, ledger, prov)
    if a.run_start_line:
        Q.E.log("code/p309_qualify.py", f"{Q.RUN_START} attempt_1 at the recorded freeze {freeze[:12]} (the single "
                "qualification run; R4 B8, delta-2 E6)", klass="GOVERNANCE",
                notes="REHEARSAL in a scratch replica (no retry, no resumption of the official attempt)")

    m = Q.mirror(freeze) if any(g in gates for g in ("QC01", "QC02", "QC03", "QC04", "QC05", "QC06", "QC07",
                                                      "QC08")) else None
    w = a.workers
    items = {   # the runner's own item table (code/p309_qualify.py main), verbatim apart from `a.workers` -> w
        "QC01": lambda: Q.qc_research_simple(m, "tests/test_srk_port_identity.py"),
        "QC02": lambda: Q.qc_research_simple(m, "tests/test_srk_envelope.py"),
        "QC03": lambda: Q.qc_research_simple(m, "tests/test_srk_fsm_truth.py"),
        "QC04": lambda: Q.qc_research_simple(m, "tests/test_srk_assembly_twosided.py", opt=True),
        "QC05": lambda: Q.qc05(m),
        "QC06": lambda: Q.qc06(m),
        "QC07": lambda: Q.qc07(m),
        "QC08": lambda: Q.qc08(m, w),
        "QC09": lambda: Q.qc09(w),
        "QC10": lambda: Q.qc10(w),
        "QC11": lambda: Q.qc_formal("tests/test_p309_exactly_once.py", flags=True),
        "QC12": lambda: Q.qc_formal("code/p309_static_check.py", flags=True),
        "QC13": lambda: Q.qc13(freeze),
        "QC14": lambda: {**(lambda r: {"pass": r["rc"] == 0, "runs": [r]})(Q.run(
            [Q.PY, "-B", str(Q.FNS / "code" / "p309_driver.py"), "rehearse", "--out", str(att / "QC14_REHEARSE.json")],
            Q.FNS)), "rehearse": json.loads((att / "QC14_REHEARSE.json").read_text()) if (
            att / "QC14_REHEARSE.json").exists() else None},
        "QC15": lambda: Q.qc_formal("code/p309_self_audit.py", "QUALIFICATION"),
        "QC16": Q.qc16,
        "QC17": Q.qc17,
        "QC_U2": Q.qc_u2,
        "QC_D5": Q.qc_d5,
    }
    results = {}
    for k in gates:
        swap = repaired is not None and k in ("QC11", "QC_D5")
        t0 = time.time()
        try:
            if swap:
                harness.write_bytes(repaired)
            try:
                res = items[k]()
            except Exception as exc:  # noqa: BLE001 - a crashed gate is a recorded FAIL (as in the runner)
                res = {"pass": False, "error": f"{type(exc).__name__}: {exc}"[:800]}
        finally:
            if swap:
                harness.write_bytes(frozen_bytes)
                if sha_file(harness) != sha_bytes(frozen_bytes) or git(iso, "status", "--porcelain", "--",
                                                                       HARNESS_REL):
                    raise SystemExit("P309 REHEARSAL: the frozen harness was not restored byte-for-byte")
        res.update({"qc": k, "freeze_commit": freeze, "utc": utc(), "wall_s": round(time.time() - t0, 1),
                    "harness": (a.harness if swap else "frozen") if k in ("QC11", "QC_D5") else "n/a"})
        record_gate(att, ledger, k, res)
        results[k] = res
        print(f"[{'PASS' if res.get('pass') else 'FAIL'}] {k} ({res['wall_s']} s)", flush=True)

    refs = git(iso, "for-each-ref", "--format=%(refname)").split()
    leaked = [r for r in refs if r.startswith(PROTECTED_REF_PREFIXES)]
    gate_pass = {k: bool(v.get("pass")) and v.get("freeze_commit") == freeze for k, v in results.items()}
    summary = {"schema": "P309_REHEARSAL_SUMMARY/1", "kind": prov["kind"], "utc": utc(), "freeze_commit": freeze,
               "gates_requested": gates, "gates": gate_pass,
               "pass": len(gate_pass) == len(gates) and all(gate_pass.values()) and not leaked,
               "files": {k: sha_file(att / f"{k}.json") for k in results},
               "provenance_sha256": sha_file(out / "PROVENANCE.json"),
               "replica_protected_refs_after": leaked,
               "replica_status_after": git(iso, "status", "--porcelain", "--untracked-files=all").splitlines(),
               "statement": "rehearsal only; the official r1 attempt is not retried or resumed; no target input "
                            "read; NEW TARGET EVALUATIONS = 0"}
    record_summary(out, ledger, summary)
    print(json.dumps({"pass": summary["pass"], "gates": gate_pass}, indent=1))
    return 0 if summary["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
