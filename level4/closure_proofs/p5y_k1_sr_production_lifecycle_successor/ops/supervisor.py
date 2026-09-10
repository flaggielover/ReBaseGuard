"""Main process of the ONE sanctioned systemd service for ONE production run.

  acquire campaign flock -> PRE-START RECOVERY (settle every unsettled run with
  the best CPU evidence, reclaim a DEAD frozen ledger lock, quarantine orphan
  results / temp files, refuse unexpected state, continuity, halt, phase, disk)
  -> open_run (SHADOW escrow) -> spawn the bound child -> MONITOR (exact cgroup
  CPU into the ledger every poll, heartbeat, worker loss, disk, stop request)
  -> kill every remaining run process -> read EXACT final CPU -> SETTLE.

The supervisor imports no science and schedules nothing.
"""
from __future__ import annotations

import argparse
import ctypes
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from opscommon import (OPS_NS, OpsRefusal, CgroupCPU, ProcTreeCPU, RuntimeDir, boot_id,   # noqa: E402
                       children_of, descendants_of, free_gib, frozen_accounting,
                       frozen_budget, host_spec, ledger_path, load_contract, online_cpus,
                       prod_ns, sha256_file, unit_state, write_json_atomic)
import ledger_ops as LO                                                                     # noqa: E402
import locks as LK                                                                          # noqa: E402
import runtime_state as RS                                                                  # noqa: E402

EXIT_OK, EXIT_OTHER, EXIT_HALT, EXIT_REFUSED, EXIT_BUSY = 0, 1, 20, 30, 75


def unit_name(contract, role, run_id) -> str:
    return f"{contract['service']['unit_prefix']}{role.lower()}-{run_id}.service"


def service_mode(contract) -> bool:
    return contract["mode"] == "PRODUCTION" or bool(contract.get("synthetic", {}).get("service_mode"))


def say(msg):
    print(f"[supervisor {time.strftime('%H:%M:%S')}] {msg}", flush=True)


# ------------------------------------------------------------ identity gates
def verify_ops_source(contract):
    if contract["mode"] != "PRODUCTION":
        return {"ops_source": "SYNTHETIC_CONTROL (not bound)"}
    man = json.loads((OPS_NS / "config/OPS_SOURCE_MANIFEST.json").read_text())
    want = (OPS_NS / "config/OPS_SOURCE_MANIFEST_HASH").read_text().strip()
    if sha256_file(OPS_NS / "config/OPS_SOURCE_MANIFEST.json") != want:
        raise OpsRefusal("OPS_SOURCE_MANIFEST hash mismatch")
    for rel, h in man["files"].items():
        if sha256_file(OPS_NS / rel) != h:
            raise OpsRefusal(f"ops source drift: {rel}")
    return {"ops_source_manifest": want}


def verify_parent(contract, spec) -> dict:
    ns, par = prod_ns(spec), contract["parent"]
    checks = {
        "production_authorization_sha256": sha256_file(ns / "config/LAUNCH_AUTHORIZATION.json"),
        "shard_manifest_sha256": sha256_file(ns / "config/SHARD_MANIFEST.json"),
        "protocol_sha256": sha256_file(ns / "config/protocol.json"),
    }
    import hashlib
    files = {r: sha256_file(ns / r) for r in sorted(("driver/production_launcher.py",
                                                     "driver/production_provenance.py"))}
    checks["production_closure_sha256"] = hashlib.sha256(
        "".join(f"{k}:{v}\n" for k, v in files.items()).encode()).hexdigest()
    for k, got in checks.items():
        if got != par[k]:
            raise OpsRefusal(f"parent identity drift: {k} {got} != {par[k]}")
    if spec["producer_binding"] == "GIT_COMMIT":
        head = subprocess.check_output(["git", "-C", spec["production_root"], "rev-parse",
                                        "HEAD"]).decode().strip()
        if head != par["commit"]:
            raise OpsRefusal(f"production worktree HEAD {head} != parent {par['commit']}")
        checks["runtime_policy"] = RS.verify_git_policy(spec["production_root"])
    return checks


def live_run_processes(spec, exclude=()) -> list:
    root = str(Path(spec["production_root"]).resolve())
    hits = []
    for d in Path("/proc").iterdir():
        if not d.name.isdigit() or int(d.name) in exclude:
            continue
        try:
            cmd = (d / "cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace")
        except OSError:
            continue
        if root in cmd and any(x in cmd for x in ("produce_entry.py", "synthetic_entry.py",
                                                  "production_launcher.py")):
            hits.append((int(d.name), cmd[:160]))
    return hits


def owners_of(spec, contract):
    M, _ = frozen_accounting(spec)
    return M.gate_shards(M.load_shard_manifest(prod_ns(spec) / "config/SHARD_MANIFEST.json",
                                               contract["parent"]["shard_manifest_sha256"]))


# ------------------------------------------------------------- pre-start
def prestart(contract, role, rt, lock, *, allow_complete=False) -> dict:
    """Deterministic recovery + every operational gate. Holds the campaign lock."""
    spec = host_spec(contract, role)
    M, GB = frozen_accounting(spec)
    io = LO.LedgerIO(ledger_path(spec), M, GB, frozen_budget(spec, contract))
    report = {"ops": verify_ops_source(contract), "parent": verify_parent(contract, spec)}
    me = [os.getpid()] + descendants_of(os.getpid())
    live = live_run_processes(spec, exclude=me)
    if live:
        raise OpsRefusal(f"LIVE run processes exist outside the campaign lock: {live[:3]}")
    report["ledger_lock"] = LK.reclaim_ledger_lock(Path(str(io.path) + ".lock"), contract,
                                                   campaign_lock=lock)
    st = io.read()
    report["continuity"] = LO.check_continuity(rt, st)
    settled = []
    for run_id in LO.unsettled_runs(st, role):
        run = st[LO.OPS_FIELD]["runs"][run_id]
        if service_mode(contract) and run.get("unit"):
            _, active = unit_state(run["unit"])
            if active in ("active", "activating", "deactivating", "reloading"):
                raise OpsRefusal(f"previous run unit {run['unit']} is still {active}")
        u, kind = LO.resolve_cpu_evidence(contract, rt, run_id, run,
                                          service_mode=service_mode(contract))
        settled.append(LO.settle_run(io, rt, role, run_id, u, kind))
    report["recovered_runs"] = settled
    st = io.read()
    owners = owners_of(spec, contract)
    tree = RS.classify_tree(spec, role, st, owners)
    if tree["unexpected"] or tree["mismatch"]:
        raise OpsRefusal(f"UNEXPECTED runtime state: {tree['unexpected'][:5]} "
                         f"mismatch {tree['mismatch'][:5]}")
    q = RS.quarantine(rt, spec, tree["orphan_results"] + tree["stale_tmp"],
                      "torn attempt artefact: never admissible")
    if q:
        LO.append_continuity(rt, "QUARANTINED", st, {"files": q})
    report["quarantined"] = q
    halt = LO.halt_state(st, role)
    if halt:
        raise OpsRefusal(f"HALTED: {halt}")
    if st and st.get("open_reservations"):
        raise OpsRefusal(f"open reservations after recovery: {sorted(st['open_reservations'])}")
    owned = sorted(c for c, r in owners.items() if r == role)
    done = set(int(c) for c in (st or {}).get("completed_cells", {}))
    report["pending"] = [c for c in owned if c not in done]
    if not report["pending"] and not allow_complete:
        raise OpsRefusal(f"SHARD_COMPLETE: {role} has completed all {len(owned)} owned cells")
    if role == "VULTR":
        remote = len((st or {}).get("remote_completed_cells", {}))
        if remote != contract["parent"]["aws_cells"]:
            raise OpsRefusal(f"HANDOFF_NOT_IMPORTED: remote completions {remote}")
    for p in (spec["production_root"], rt.root):
        g = free_gib(p)
        if g < contract["stop_conditions"]["free_disk_min_gib"]:
            raise OpsRefusal(f"DISK: {g:.2f} GiB free at {p}")
    report["state"], report["io"] = st, io
    return report


# ------------------------------------------------------------------- run
_STOP = {"reason": None}


def _on_signal(signum, _frame):
    _STOP["reason"] = f"STOP_SIGNAL_{signal.Signals(signum).name}"


def child_argv(contract, role, run_id):
    spec = host_spec(contract, role)
    entry = contract["service"]["entry"] if contract["mode"] == "PRODUCTION" \
        else contract["synthetic"]["entry"]
    return [spec["python"], str(Path(spec["ops_root"]) / entry),
            "--contract", contract["_path"], "--role", role, "--run-id", run_id]


def become_subreaper():
    """Harness mode only (no dedicated cgroup): orphaned run processes must be
    re-parented to the supervisor so they are killed AND reaped (their CPU then
    reaches RUSAGE_CHILDREN). Verified, never assumed."""
    libc = ctypes.CDLL("libc.so.6", use_errno=True)
    u = ctypes.c_ulong
    if libc.prctl(ctypes.c_int(36), u(1), u(0), u(0), u(0)) != 0:
        raise OpsRefusal(f"PR_SET_CHILD_SUBREAPER failed errno={ctypes.get_errno()}")
    v = ctypes.c_int(0)
    libc.prctl(ctypes.c_int(37), ctypes.byref(v), u(0), u(0), u(0))
    if v.value != 1:
        raise OpsRefusal("child-subreaper flag not set")


def kill_all(cpu, child, timeout_s=120.0):
    me = os.getpid()
    try:
        child.kill()
    except ProcessLookupError:
        pass
    deadline = time.monotonic() + timeout_s
    while True:
        others = [p for p in cpu.procs() if p != me]
        for p in others:
            try:
                os.kill(p, signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass
        while True:                       # reap EVERYTHING (incl. reparented orphans)
            try:
                if os.waitpid(-1, os.WNOHANG)[0] == 0:
                    break
            except ChildProcessError:
                break
        if not [p for p in cpu.procs() if p != me]:
            break
        if time.monotonic() > deadline:
            raise OpsRefusal(f"run processes survive SIGKILL: {others[:5]}")
        time.sleep(0.1)
    child.wait()


def run(contract, role, run_id) -> int:
    spec = host_spec(contract, role)
    unit = unit_name(contract, role, run_id)
    smode = service_mode(contract)
    if smode:
        cpu = CgroupCPU(unit)
    else:
        become_subreaper()
        cpu = ProcTreeCPU()
    rt = RuntimeDir(spec).ensure()
    lock = LK.CampaignLock(rt, contract)
    try:
        lock.acquire(run_id=run_id, unit=unit)
    except OpsRefusal as exc:
        say(f"REFUSE {exc}")
        return EXIT_BUSY
    signal.signal(signal.SIGTERM, _on_signal)
    signal.signal(signal.SIGINT, _on_signal)
    try:
        try:
            pre = prestart(contract, role, rt, lock)
        except OpsRefusal as exc:
            say(f"REFUSE prestart: {exc}")
            write_json_atomic(rt.run_record(run_id), {"run_id": run_id, "status": "REFUSED",
                                                      "reason": str(exc)})
            return EXIT_REFUSED
        io = pre["io"]
        say(f"prestart ok: pending={len(pre['pending'])} recovered={len(pre['recovered_runs'])} "
            f"quarantined={len(pre['quarantined'])}")
        poll = contract["accounting"]["poll_interval_s"]
        e_stale = LO.e_stale_cpu_h(poll, spec["online_cpus"])
        boot = boot_id(contract)
        LO.open_run(io, rt, role, run_id, unit=unit if smode else None,
                    invocation_id=os.environ.get("INVOCATION_ID"), cpu_kind=cpu.kind,
                    e_stale=e_stale, boot=boot)
        argv = child_argv(contract, role, run_id)
        env = dict(contract["service"]["environment"][role])
        rec = {"run_id": run_id, "role": role, "unit": unit, "status": "RUNNING",
               "invocation_id": os.environ.get("INVOCATION_ID"), "argv": argv, "env": env,
               "cwd": spec["production_root"], "started_wall": time.time(), "boot_id": boot,
               "supervisor_pid": os.getpid(), "cpu_source": cpu.kind}
        write_json_atomic(rt.run_record(run_id), rec)
        with open(rt.log(run_id), "ab") as logf:
            child = subprocess.Popen(argv, cwd=spec["production_root"], env=env,
                                     stdout=logf, stderr=subprocess.STDOUT)
        rec["child_pid"] = child.pid
        write_json_atomic(rt.run_record(run_id), rec)
        workers = contract["parent"]["workers"][role]
        reason = None
        while True:
            rc = child.poll()
            if rc is not None:
                reason = f"CHILD_EXIT_{rc}"
                break
            if _STOP["reason"]:
                reason = _STOP["reason"]
                break
            try:
                u = cpu.usage_usec()
                upd = LO.update_shadow(io, role, run_id, u, boot)
                kids = children_of(child.pid)
                st = io.read()
                open_cells = [k for k in st["open_reservations"] if k.startswith(f"{role}:")]
                write_json_atomic(rt.root / "heartbeat.json", {
                    "run_id": run_id, "t_wall": time.time(), "u_usec": u, "children": len(kids),
                    "open_cell_reservations": len(open_cells),
                    "completed": len(st["completed_cells"]), "shadow": upd})
            except Exception as exc:                             # noqa: BLE001
                # never crash while run processes live: e.g. a launcher that died holding
                # the frozen ledger lock makes the shadow update time out
                rc = child.poll()
                reason = f"CHILD_EXIT_{rc}" if rc is not None else \
                    f"MONITOR_ERROR {type(exc).__name__}: {str(exc)[:200]}"
                break
            # the frozen scheduler builds the full pool BEFORE its first admission, so an
            # open cell reservation implies all `workers` processes existed
            if open_cells and len(kids) < workers:
                rc = child.poll()             # a dead launcher orphans its workers: not a worker loss
                reason = f"CHILD_EXIT_{rc}" if rc is not None else \
                    f"WORKER_LOST ({len(kids)}/{workers} alive, {len(open_cells)} open)"
                break
            if min(free_gib(spec["production_root"]), free_gib(rt.root)) < \
                    contract["stop_conditions"]["free_disk_min_gib"]:
                reason = "DISK_LOW"
                break
            t_end = time.monotonic() + poll
            while time.monotonic() < t_end and child.poll() is None and not _STOP["reason"]:
                time.sleep(0.05)
        say(f"run ending: {reason}")
        kill_all(cpu, child)
        u_final = cpu.usage_usec()
        rec.update({"status": "ENDED", "reason": reason, "child_returncode": child.returncode,
                    "final_u_usec": int(u_final), "final_evidence": "SUPERVISOR_FINAL",
                    "ended_wall": time.time()})
        write_json_atomic(rt.run_record(run_id), rec)
        try:
            LK.reclaim_ledger_lock(Path(str(io.path) + ".lock"), contract, campaign_lock=lock)
            s = LO.settle_run(io, rt, role, run_id, u_final, "SUPERVISOR_FINAL")
        except OpsRefusal as exc:
            # the EXACT final CPU is already persisted in the run record; the next
            # pre-start settles with it once the refusal (e.g. an AMBIGUOUS lock) is resolved
            rec.update({"status": "SETTLEMENT_DEFERRED", "deferred_reason": str(exc)})
            write_json_atomic(rt.run_record(run_id), rec)
            say(f"SETTLEMENT_DEFERRED: {exc}")
            return EXIT_REFUSED
        rec.update({"status": "SETTLED", "settlement": s})
        write_json_atomic(rt.run_record(run_id), rec)
        say(f"settled: measured={s['measured_run_cpu_h']:.6f} charge={s['unattributed_charge_cpu_h']:.6f} "
            f"completed_in_run={len(s['completed_in_run'])}")
        if child.returncode == 20 or (io.read()[LO.OPS_FIELD].get("halt")):
            return EXIT_HALT
        return EXIT_OK if reason == "CHILD_EXIT_0" else EXIT_OTHER
    finally:
        lock.release()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", default=None)
    ap.add_argument("--role", required=True, choices=("AWS", "VULTR"))
    ap.add_argument("--run-id", required=True)
    a = ap.parse_args(argv)
    return run(load_contract(a.contract), a.role, a.run_id)


if __name__ == "__main__":
    raise SystemExit(main())
