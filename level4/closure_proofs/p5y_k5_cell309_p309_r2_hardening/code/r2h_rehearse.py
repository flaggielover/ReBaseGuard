#!/usr/bin/env python3
"""ONE-COMMAND, RESULT-FREE rehearsal of the full r2-line qualification on a synthetic freeze (never qualification).

  python3 r2h_rehearse.py run    --source SRC --commit C --root NEW_DIR [--gates all|light] [--workers 4]
                                 [--require-durable-host]
  python3 r2h_rehearse.py status --root DIR          (read-only: classify a rehearsal, finished or not)

SRC is the repository to clone (a path or an https URL); C the exact package commit (e.g. the hardening branch head).

What `run` does, in order, refusing on the first failure (nothing is retried, resumed or repaired):
  1. ROOT must not exist: it is created exclusively, so a second start -- or a restart after an interruption -- into
     the same root is refused; an interrupted rehearsal stays INTERRUPTED for ever (`status` shows it).
  2. Host and runtime prerequisites are measured and recorded (CPU, RAM, free disk, filesystem type, interpreter,
     glibc, boot id, machine identity as sha256).  --require-durable-host turns the durable-host rules into refusals
     (see DURABLE_HOST_EXECUTION_PACKET.md); without it the rehearsal is labelled DEVELOPMENT_ONLY.
  3. A fresh clone of SRC at C (no remote left), its exact refs and ancestry (does C descend from r2 101ef2cb?), a
     clean-tree check, and no protected ref.
  4. A synthetic, non-target freeze made by the package's own unmodified generators (params, manifest, placeholder
     check), its record-only child and a checkpoint commit; the topology is witnessed with git.
  5. Every permitted gate (all 19, or `light`: all but the decoy batteries QC06, QC08-QC10) runs through the
     package's own items_table() / run_item() -- the runner's own lambdas and (hardened) record writes -- in order,
     into ROOT/attempt.  The runner's main(), its launcher and Q-HOST are not used (no systemd unit; Q-HOST is
     exercised by the package's worker-tier drill on the durable host).  A self-guard refuses the driver's execute /
     seal-only / validate-grant modes and the launcher in every subprocess; nothing reads a target input.
  6. After each gate: a GATE_LEDGER row (durable append) binding the record's sha256, the order and the timing.
  7. After the last gate: no protected ref and no grant / result file in the clone; a durable summary binding every
     record and the provenance; then the independent validator (code/r2h_validator.py rehearsal) is run over ROOT
     and its verdict is written to ROOT/VALIDATION.json.
A rehearsal PASSES only if the validator says PASS.  An interruption at any point leaves ROOT classified INTERRUPTED.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import platform
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent))
import r2h_replica as RP  # noqa: E402

VALIDATOR = HERE.parent / "r2h_validator.py"
R2_HEAD = "101ef2cb17e5eab2892212178278da45b98004ed"
GATES = ["QC01", "QC02", "QC03", "QC04", "QC05", "QC06", "QC07", "QC08", "QC09", "QC10", "QC11", "QC12", "QC13",
         "QC14", "QC15", "QC16", "QC17", "QC_U2", "QC_D5"]
HEAVY = {"QC06", "QC08", "QC09", "QC10"}
REFUSED_MODES = {"execute", "seal-only", "validate-grant"}
DURABLE_FS = {"ext4", "xfs", "btrfs", "zfs", "ext3"}
MIN = {"cpus": 4, "ram_gb": 8.0, "disk_gb": 40.0, "python": "3.11.15"}


def utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def fsync_dir(d: Path) -> None:
    fd = os.open(str(d), os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic_create(path: Path, data: bytes) -> str:
    tmp = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
    try:
        view = memoryview(data)
        while view:
            view = view[os.write(fd, view):]
        os.fsync(fd)
    finally:
        os.close(fd)
    os.link(tmp, path)
    os.unlink(tmp)
    fsync_dir(path.parent)
    return sha(data)


def append(ledger: Path, row: dict) -> None:
    fd = os.open(ledger, os.O_WRONLY | os.O_CREAT | os.O_APPEND | os.O_NOFOLLOW, 0o644)
    try:
        os.write(fd, (json.dumps(row, sort_keys=True) + "\n").encode())
        os.fsync(fd)
    finally:
        os.close(fd)


def fs_type(path: Path) -> str | None:
    best, typ = "", None
    try:
        for line in Path("/proc/mounts").read_text().splitlines():
            parts = line.split()
            if len(parts) > 2 and str(path).startswith(parts[1]) and len(parts[1]) > len(best):
                best, typ = parts[1], parts[2]
    except OSError:
        pass
    return typ


def host_facts(root: Path) -> dict:
    def read(p):
        try:
            return Path(p).read_text().strip()
        except OSError:
            return None
    mem = read("/proc/meminfo") or ""
    avail = next((int(l.split()[1]) / 1e6 for l in mem.splitlines() if l.startswith("MemAvailable:")), 0.0)
    try:
        glibc = os.confstr("CS_GNU_LIBC_VERSION")
    except (ValueError, OSError, AttributeError):
        glibc = None
    exe = os.path.realpath(sys.executable)
    return {"utc": utc(), "boot_id": read("/proc/sys/kernel/random/boot_id"),
            "machine_id_sha256": sha((read("/etc/machine-id") or "").encode()),
            "hostname_sha256": sha(socket.gethostname().encode()), "kernel": platform.release(),
            "cpus_affinity": len(os.sched_getaffinity(0)), "ram_available_gb": round(avail, 1),
            "disk_free_gb": round(shutil.disk_usage(root.parent).free / 1e9, 1), "filesystem": fs_type(root.parent),
            "python": platform.python_version(), "interpreter": exe,
            "interpreter_sha256": sha(Path(exe).read_bytes()), "glibc": glibc,
            "pid1": read("/proc/1/comm"), "in_container": os.path.exists("/.dockerenv") or os.path.exists(
                "/run/.containerenv") or bool(read("/run/systemd/container")),
            "uptime_h": round(float((read("/proc/uptime") or "0").split()[0]) / 3600, 2)}


def durable_checks(f: dict) -> dict:
    return {"cpus": f["cpus_affinity"] >= MIN["cpus"], "ram": f["ram_available_gb"] >= MIN["ram_gb"],
            "disk": f["disk_free_gb"] >= MIN["disk_gb"], "python_exact": f["python"] == MIN["python"],
            "filesystem_durable": (f["filesystem"] or "") in DURABLE_FS, "pid1_systemd": f["pid1"] == "systemd",
            "not_in_container": not f["in_container"]}


def run(a) -> int:
    root = Path(a.root).resolve()
    root.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.mkdir(root)                                    # exclusive: no second start, no restart, no resume
    except FileExistsError:
        print(f"REHEARSAL REFUSED: {root} exists -- a rehearsal is never restarted or resumed; classify it with "
              f"`status --root {root}` and start a new one in a new root")
        return 2
    fsync_dir(root.parent)
    facts = host_facts(root)
    dchk = durable_checks(facts)
    if a.require_durable_host and not all(dchk.values()):
        atomic_create(root / "REFUSED.json", (json.dumps({"utc": utc(), "refused": "durable-host prerequisites",
                                                          "checks": dchk, "host": facts}, indent=1) + "\n").encode())
        print(f"REHEARSAL REFUSED: durable-host prerequisites {[k for k, v in dchk.items() if not v]}")
        return 2
    scratch = root / "p309_scratch"
    scratch.mkdir()
    built = RP.build(a.source, a.commit, root / "package")
    clone = root / "package"
    anc = subprocess.run(["git", "-C", str(clone), "merge-base", "--is-ancestor", R2_HEAD, "HEAD"]).returncode == 0
    topo = RP.synthetic_freeze(clone, scratch)
    gates = GATES if a.gates == "all" else [g for g in GATES if g not in HEAVY]
    prov = {"schema": "P309_R2H_REHEARSAL_PROVENANCE/1", "kind": "RESULT-FREE REHEARSAL (synthetic freeze; never "
            "qualification evidence)", "label": "DURABLE_HOST" if a.require_durable_host else "DEVELOPMENT_ONLY",
            "utc_start": utc(), "source": a.source, "commit": a.commit, "package": built,
            "descends_from_r2_101ef2cb": anc, "synthetic_freeze": topo["F"],
            "topology": {k: v for k, v in topo.items() if k != "generators"}, "generators": topo["generators"],
            "gates": gates, "workers": a.workers, "host": facts, "durable_host_checks": dchk,
            "tool_sha256": {p.name: sha(p.read_bytes()) for p in (HERE, VALIDATOR, HERE.parent / "r2h_replica.py")},
            "new_target_evaluations": 0}
    ledger = root / "GATE_LEDGER.jsonl"
    psha = atomic_create(root / "PROVENANCE.json", (json.dumps(prov, indent=1, sort_keys=True) + "\n").encode())
    append(ledger, {"utc": utc(), "event": "RUN_START", "provenance_sha256": psha, "boot_id": facts["boot_id"],
                    "new_target_evaluations": 0})
    # ---- the package's own runner functions, imported from the clone (never main(), never the launcher)
    for k in [k for k in os.environ if k.startswith("P309_")]:
        del os.environ[k]
    os.environ["P309_SCRATCH_ROOT"] = str(scratch)
    fns = clone / RP.NS2
    sys.path.insert(0, str(fns / "code"))
    import p309_qualify as Q  # noqa: E402
    if Path(Q.__file__).resolve().parent != (fns / "code").resolve():
        raise SystemExit("the runner was not imported from the fresh clone")
    real_run = Q.run

    def guarded(cmd, cwd, timeout=6 * 3600):
        flat = [str(c) for c in cmd]
        for i, c in enumerate(flat):
            if c.endswith("p309_driver.py") and i + 1 < len(flat) and flat[i + 1] in REFUSED_MODES:
                raise RuntimeError("self-guard: a driver target / grant mode was refused")
            if c.endswith(("p309_launch.py", "p309_qualify.py")):
                raise RuntimeError("self-guard: the launcher / runner main is never started by a rehearsal")
        return real_run(cmd, cwd, timeout)
    Q.run = guarded
    att = root / "attempt"
    att.mkdir()
    (att / "evidence").mkdir()
    Q.ATT["dir"], Q.ATT["label"] = att, "rehearsal (synthetic freeze; not qualification)"
    freeze = Q.D.recorded_freeze()
    if freeze != topo["F"]:
        raise SystemExit("the clone's recorded freeze is not the synthetic F'")
    Q.E.log("code/p309_qualify.py", f"{Q.RUN_START} attempt_rehearsal at the recorded freeze {freeze[:12]} "
            "(result-free rehearsal; not qualification)", klass="GOVERNANCE", notes="r2h_rehearse.py")
    m = Q.mirror(freeze) if any(g in gates for g in ("QC01", "QC02", "QC03", "QC04", "QC05", "QC06", "QC07", "QC08")) \
        else None
    table = Q.items_table(m, freeze, a.workers)
    for g in gates:
        now = Path("/proc/sys/kernel/random/boot_id").read_text().strip()
        if now != facts["boot_id"]:                      # cannot happen in-process; recorded defensively
            append(ledger, {"utc": utc(), "event": "INTERRUPTION_DETECTED", "detail": "boot id changed"})
            return 3
        t0 = time.time()
        res = Q.run_item(g, table[g], freeze)
        rec = att / f"{g}.json"
        append(ledger, {"utc": utc(), "event": "GATE_RECORDED", "gate": g, "sha256": sha(rec.read_bytes()),
                        "pass": bool(res.get("pass")), "wall_s": round(time.time() - t0, 1),
                        "new_target_evaluations": 0})
    refs = RP.git(clone, "for-each-ref", "--format=%(refname)").split()
    leaked = [r for r in refs if r.startswith(RP.PROTECTED)]
    grants = [str(p) for p in clone.rglob("*") if p.name in ("P309_GRANT.json", "P309_RESULT.json")]
    summary = {"schema": "P309_R2H_REHEARSAL_SUMMARY/1", "utc": utc(), "provenance_sha256": psha,
               "files": {g: sha((att / f"{g}.json").read_bytes()) for g in gates},
               "gates": {g: bool(json.loads((att / f"{g}.json").read_text()).get("pass")) for g in gates},
               "protected_refs_in_clone": leaked, "grant_or_result_files_in_clone": grants,
               "statement": "result-free rehearsal on a synthetic freeze; NEW TARGET EVALUATIONS = 0"}
    summary["pass"] = all(summary["gates"].values()) and not leaked and not grants
    ssha = atomic_create(root / "REHEARSAL_SUMMARY.json", (json.dumps(summary, indent=1, sort_keys=True) + "\n").encode())
    append(ledger, {"utc": utc(), "event": "SUMMARY_RECORDED", "sha256": ssha, "pass": summary["pass"],
                    "new_target_evaluations": 0})
    v = subprocess.run([sys.executable, str(VALIDATOR), "rehearsal", str(root), "--out", str(root / "VALIDATION.json")],
                       capture_output=True, text=True)
    verdict = json.loads((root / "VALIDATION.json").read_text())["verdict"]
    print(json.dumps({"rehearsal": str(root), "validator_verdict": verdict, "gates": summary["gates"]}, indent=1))
    return 0 if verdict == "PASS" else 1


def status(a) -> int:
    root = Path(a.root)
    if not root.exists():
        print(json.dumps({"verdict": "NOT_STARTED"}))
        return 1
    p = subprocess.run([sys.executable, str(VALIDATOR), "rehearsal", str(root)], capture_output=True, text=True)
    out = json.loads(p.stdout)
    try:
        prov = json.loads((root / "PROVENANCE.json").read_text())
        boot = Path("/proc/sys/kernel/random/boot_id").read_text().strip()
        if out["verdict"] == "INTERRUPTED" and prov["host"]["boot_id"] != boot:
            out["reasons"].append("INTERRUPTED: the host rebooted since the rehearsal started (boot id changed)")
    except (OSError, ValueError, KeyError):
        pass
    print(json.dumps({k: out[k] for k in ("verdict", "reasons") if k in out}, indent=1))
    return 0 if out["verdict"] == "PASS" else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="mode", required=True)
    r = sp.add_parser("run")
    r.add_argument("--source", required=True)
    r.add_argument("--commit", required=True)
    r.add_argument("--root", required=True)
    r.add_argument("--gates", choices=("all", "light"), default="all")
    r.add_argument("--workers", type=int, default=4)
    r.add_argument("--require-durable-host", action="store_true")
    s = sp.add_parser("status")
    s.add_argument("--root", required=True)
    a = ap.parse_args()
    return run(a) if a.mode == "run" else status(a)


if __name__ == "__main__":
    sys.exit(main())
