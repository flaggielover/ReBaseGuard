"""Supervisor of one executor attempt and its recovery mode (EXECUTOR_SPEC_R2.md R2-2; EXECUTOR_SPEC_R3.md R3-2 / R3-3).

    python -B code/supervisor.py launch  --namespace ROOT --slot N --mode real|governed_manufactured|manufactured|burn|diskfull
                                         [--fixture-id XF..] [--cpu-soft S --cpu-hard H --wall W]
    python -B code/supervisor.py recover --namespace ROOT

LAUNCH (SCIENCE_PREREGISTRATION_R4.completion_semantics, retry_policy.slots_and_ledger):
  governed modes (real; governed_manufactured for qualification), EXECUTOR_SPEC_R4.md R4-1: BEFORE anything exists, the
  slot must be free and inside the preregistered namespace, the guard policy must be EXTERNAL_AUTHORIZATION, and THE
  single authoritative verification (authorization_interface.prelaunch_decision: the frozen prelaunch_verify.verify in
  process, defaults) must PASS; otherwise PRELAUNCH_REFUSED with no slot, no RUN_STATE and no VOID. Only then:
  creates <ROOT>/slot-N (refused if it exists) and writes RUN_STATE.json atomically (pid, exact argv, boot id, start
  epoch, authorization sha256, slot, attempt_uid, protocol sha256, executor identity); launches code/executor_cli.py
  with RLIMIT_CPU (soft, hard) set before exec; runs a wall watchdog (SIGUSR1 -> the executor seals VOID of cost;
  SIGKILL 60 s later); derives the failure class ONLY by the frozen probe_rules.failure_class from its own evidence
  (never self-declared by the executor); writes exactly one terminal marker:
    RUN_COMPLETE.json  only if the child exited 0 AND a valid scientific seal of this attempt exists and no VOID seal;
    RUN_FAILED.json    otherwise (pid, arithmetic_started, supervisor_evidence, failure class, VOID seal sha256,
                       traceback with every digit masked).
RECOVER: classifies every slot A/B/C/D/E from persisted evidence (lifecycle.classify) and applies the frozen action
  (lifecycle.recovery_action). It never launches the executor, never recomputes a sealed address, never infers
  completion from process absence (a slot whose supervisor is alive on the same boot with the exact argv is LIVE), and
  writes nothing for a torn state (E: ADJUDICATION_REQUIRED). A second pass changes nothing.
The overrides of the CPU and wall limits exist for QUALIFICATION only; the defaults are the frozen ceilings.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import resource
import secrets
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import paths  # noqa: F401

import lifecycle as LC  # noqa: E402
import probe_rules as PR  # noqa: E402

CLI = Path(__file__).resolve().parent / "executor_cli.py"
SCIENCE_FILE = paths.PROTOCOL_NS / "protocol/SCIENCE_PREREGISTRATION_R4.json"
AUTH_ACTIVE = paths.PROTOCOL_NS / "protocol/AUTHORIZATION_ACTIVE.json"


def _sha_file(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() and not path.is_symlink() else None


def executor_identity() -> str:
    import authorization_interface as AI
    return AI.executor_identity()["executor_identity_sha256"]


def pid_alive_with_argv(pid, argv) -> bool:
    """Exact /proc/<pid>/cmdline equality (never pgrep -f)."""
    try:
        raw = Path(f"/proc/{int(pid)}/cmdline").read_bytes()
    except (OSError, TypeError, ValueError):
        return False
    return [a.decode(errors="replace") for a in raw.split(b"\0") if a] == list(argv or [])


def own_cmdline() -> list:
    """The supervisor's exact argv as the kernel reports it (what a waiter compares with /proc/<pid>/cmdline)."""
    try:
        return [a.decode(errors="replace") for a in Path("/proc/self/cmdline").read_bytes().split(b"\0") if a]
    except OSError:
        return [sys.executable, *sys.argv]


def seal_summary(slot: Path, mode: str, uid: str) -> dict:
    sci, void = LC.seal_names(mode)
    out = {"scientific": None, "void": None}
    for key, name in (("scientific", sci), ("void", void)):
        if (slot / name).exists():
            ok, why = LC.seal_valid(slot / name, uid)
            out[key] = {"name": name, "sha256": LC.sha((slot / name).read_bytes()), "valid": ok, "why": why}
    return out


GOVERNED = ("real", "governed_manufactured")


def fixture_spec(fid: str) -> dict:
    proto = json.loads((paths.NS / "config/EXECUTOR_QUALIFICATION_PROTOCOL.json").read_text())
    return next(f for f in proto["fixtures"] if f["id"] == fid)


def governed_prelaunch(slot: Path, mode: str, fixture_id=None) -> dict:
    """R4-1: the single authoritative pre-arithmetic launch decision, taken while slot-N does NOT exist."""
    import authorization_interface as AI
    import executor_core as EC
    import input_adapters as IA
    p = EC.prereg()
    if str(slot.parent) != p["output_namespace"]:
        return {"permitted": False, "problems": ["slot outside the preregistered output namespace"], "decision": None}
    policy = EC.guard_policy()
    if policy != "EXTERNAL_AUTHORIZATION":
        return {"permitted": False, "problems": [f"guard policy {policy!r}: no verification attempted"], "decision": None}
    binding = IA.RealInputAdapter().bind() if mode == "real" else IA.ManufacturedInputAdapter().bind(fixture_spec(fixture_id))
    ctx = EC.standard_context(binding, slot, executor_binding_sha256=EC.amendment_binding())
    ok, problems, decision = AI.prelaunch_decision(ctx)           # THE single authoritative verification
    return {"permitted": ok, "problems": problems, "decision": decision}


def supervise(slot: Path, mode: str, *, cpu_soft: int, cpu_hard: int, wall: float, fixture_id=None, cli: Path = CLI,
              argv=None) -> dict:
    """`cli` differs from code/executor_cli.py only in qualification mutant tests (a mutant-shadowing wrapper)."""
    slot = Path(slot)
    if slot.exists() or slot.is_symlink():
        raise LC.MarkerError(f"SLOT_EXISTS: {slot}")
    decision = None
    if mode in GOVERNED:
        pre = governed_prelaunch(slot, mode, fixture_id)
        if not pre["permitted"]:
            return {"terminal": None, "prelaunch": "PRELAUNCH_REFUSED", "failure_class": "PRELAUNCH_REFUSED",
                    "problems": [LC.mask_digits(x) for x in pre["problems"][:6]], "slot_created": slot.exists(),
                    "arithmetic_started": False}
        decision = pre["decision"]
    slot.parent.mkdir(parents=True, exist_ok=True)
    slot.mkdir()
    uid = secrets.token_hex(16)
    boot0 = LC.boot_id()
    state = LC.build_run_state(pid=os.getpid(), argv=list(argv if argv is not None else own_cmdline()), boot=boot0,
                               start_epoch=time.time(),
                               authorization_sha256=decision["authorization_sha256"] if decision else "NOT_APPLICABLE_MANUFACTURED",
                               slot=slot.name, attempt_uid=uid, protocol_sha256=_sha_file(SCIENCE_FILE),
                               executor_identity_sha256=executor_identity(), mode="real" if mode == "real" else "manufactured",
                               prelaunch_decision=decision)
    LC.write_new(slot, LC.RUN_STATE, state)

    def limits():
        resource.setrlimit(resource.RLIMIT_CPU, (int(cpu_soft), int(cpu_hard)))

    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", NUMEXPR_NUM_THREADS="1",
               PYTHONHASHSEED="0")
    cmd = [sys.executable, "-B", str(cli), mode, "--output-dir", str(slot), "--attempt-uid", uid]
    if decision is not None:
        cmd += ["--decision-sha256", state["prelaunch_decision_sha256"]]
    if fixture_id:
        cmd += ["--fixture-id", fixture_id]
    # child output goes to a private temporary directory OUTSIDE the namespace: the executor admits only RUN_STATE in
    # its slot, and prelaunch P11 admits only slot-N directories in the namespace root
    diag = Path(tempfile.mkdtemp(prefix=f"k5exec-{slot.name}-"))
    w0 = time.time()
    with open(diag / "child_stderr.log", "w") as err, open(diag / "child_stdout.log", "w") as so:
        child = subprocess.Popen(cmd, env=env, stdout=so, stderr=err, preexec_fn=limits)
        wall_timeout, sent = False, None
        while True:
            pid, status, ru = os.wait4(child.pid, os.WNOHANG)
            if pid == child.pid:
                break
            now = time.time()
            if now - w0 >= wall and sent is None:
                wall_timeout, sent = True, now
                child.send_signal(signal.SIGUSR1)
            elif sent is not None and now - sent > 60:
                child.send_signal(signal.SIGKILL)
            time.sleep(0.2)
    child.returncode = os.waitstatus_to_exitcode(status)
    stderr_text = (diag / "child_stderr.log").read_text()
    shutil.rmtree(diag, ignore_errors=True)
    return finish(slot, state, status=status, ru=ru, wall_seconds=time.time() - w0, wall_timeout=wall_timeout,
                  cpu_soft=cpu_soft, stderr_text=stderr_text)


def finish(slot: Path, state: dict, *, status, ru, wall_seconds, wall_timeout, cpu_soft, stderr_text) -> dict:
    sig = os.WTERMSIG(status) if os.WIFSIGNALED(status) else None
    code = os.WEXITSTATUS(status) if os.WIFEXITED(status) else None
    refusal = next((ln for ln in stderr_text.splitlines() if ln.startswith("EXECUTOR_REFUSAL:")), None)
    events, _ = LC.read_events(slot)
    names = [e.get("event") for e in events if e.get("attempt_uid") == state["attempt_uid"]]
    started = "ARITHMETIC_STARTED" in names
    seals = seal_summary(slot, state["mode"], state["attempt_uid"])
    cost = refusal is not None and ("CPU_RLIMIT" in refusal or "WALL_TIMEOUT" in refusal)
    disk = "No space left on device" in stderr_text or (refusal is not None and "ENOSPC" in refusal)
    integrity = refusal is not None and code in (3, 4) and not cost and not disk
    child_cpu = ru.ru_utime + ru.ru_stime
    evidence = {"boot_id_changed": LC.boot_id() != state["boot_id"], "child_cpu_seconds": child_cpu,
                "wall_seconds": wall_seconds, "wall_timeout": wall_timeout, "signal": sig, "exit_code": code,
                "cpu_soft_limit_reached": child_cpu >= cpu_soft or (refusal is not None and "CPU_RLIMIT" in refusal),
                "kernel_oom_record": False, "enospc": disk,
                "integrity_refusal": LC.mask_digits(refusal) if integrity else None}
    sci, void = seals["scientific"], seals["void"]
    valid_complete = (code == 0 and sci is not None and sci["valid"] and void is None
                      and names == ["VALIDATED", "ARITHMETIC_STARTED", "SEALED"])
    if code == 0 and not valid_complete:
        evidence["integrity_refusal"] = "SEALED_RECORD_INVALID_OR_INCONSISTENT"
    base = {"pid": state["pid"], "attempt_uid": state["attempt_uid"], "slot": state["slot"],
            "protocol_sha256": state["protocol_sha256"], "executor_identity_sha256": state["executor_identity_sha256"],
            "authorization_sha256": state["authorization_sha256"]}
    if valid_complete:
        rec = json.loads((slot / sci["name"]).read_text())
        marker = dict(base, schema=LC.COMPLETE_SCHEMA, sealed_record=sci["name"], sealed_record_sha256=sci["sha256"],
                      scientific_hash=rec["scientific_hash"],
                      qualification_gates=rec["scientific"]["producer_qualification"]["gates"],
                      addresses_sha256=sorted(a["address_sha256"] for a in rec["scientific"]["addresses"].values()),
                      recovered=False)
        LC.write_terminal(slot, LC.RUN_COMPLETE, marker)
        return {"terminal": LC.RUN_COMPLETE, "failure_class": None, "marker": marker, "events": names,
                "arithmetic_started": started, "seals": seals, "evidence": evidence}
    marker = dict(base, schema=LC.FAILED_SCHEMA, arithmetic_started=started, supervisor_evidence=evidence,
                  failure_class=PR.failure_class(evidence),
                  void_record_sha256=void["sha256"] if void else None,
                  traceback=LC.mask_digits(stderr_text[-2000:]), recovered=False)
    LC.write_terminal(slot, LC.RUN_FAILED, marker)
    return {"terminal": LC.RUN_FAILED, "failure_class": marker["failure_class"], "marker": marker, "events": names,
            "arithmetic_started": started, "seals": seals, "evidence": evidence}


# ------------------------------------------------------------------ recovery (D3)
def recover(root: Path, *, current_boot=None, alive=pid_alive_with_argv) -> dict:
    """Classify every slot and apply the frozen action. Never launches, never recomputes, idempotent."""
    root = Path(root)
    current_boot = LC.boot_id() if current_boot is None else current_boot
    report = {}
    for slot in sorted(p for p in root.iterdir() if p.is_dir() and not p.is_symlink() and p.name.startswith("slot-")) \
            if root.exists() else []:
        c = LC.classify(slot, current_boot=current_boot, pid_alive_with_argv=alive)
        action = LC.recovery_action(c)
        c["action"] = action
        if action.startswith("WRITE_") or action.startswith("CONSUME_"):
            c["written"] = apply_recovery(slot, c, current_boot)
        report[slot.name] = c
    return report


def apply_recovery(slot: Path, c: dict, current_boot) -> str:
    state, _ = LC.load_json(slot / LC.RUN_STATE)
    state = state or {}
    base = {"pid": state.get("pid"), "attempt_uid": state.get("attempt_uid"), "slot": slot.name,
            "protocol_sha256": state.get("protocol_sha256"), "executor_identity_sha256": state.get("executor_identity_sha256"),
            "authorization_sha256": state.get("authorization_sha256"), "recovered": True}
    rebooted = state.get("boot_id") is not None and state.get("boot_id") != current_boot
    evidence = {"boot_id_changed": rebooted, "child_cpu_seconds": None, "wall_seconds": None, "wall_timeout": False,
                "signal": None, "exit_code": None, "cpu_soft_limit_reached": False, "kernel_oom_record": False,
                "enospc": False, "integrity_refusal": None, "supervisor_lost": not rebooted,
                "recovered_from_persisted_evidence": True}
    if c["class"] == "C":
        name = next(n for n in LC.ALL_SEALS if (slot / n).exists())
        rec = json.loads((slot / name).read_text())
        marker = dict(base, schema=LC.COMPLETE_SCHEMA, sealed_record=name, sealed_record_sha256=LC.sha((slot / name).read_bytes()),
                      scientific_hash=rec["scientific_hash"],
                      qualification_gates=rec["scientific"]["producer_qualification"]["gates"],
                      addresses_sha256=sorted(a["address_sha256"] for a in rec["scientific"]["addresses"].values()))
        LC.write_terminal(slot, LC.RUN_COMPLETE, marker)
        return LC.RUN_COMPLETE
    void = next((n for n in LC.ALL_SEALS if (slot / n).exists()), None) if c["class"] == "D" else None
    marker = dict(base, schema=LC.FAILED_SCHEMA, arithmetic_started=c["arithmetic_started"], supervisor_evidence=evidence,
                  failure_class=PR.failure_class(evidence),
                  void_record_sha256=LC.sha((slot / void).read_bytes()) if void else None,
                  traceback="recovered from persisted evidence; no process output available")
    LC.write_terminal(slot, LC.RUN_FAILED, marker)
    return LC.RUN_FAILED


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    ceil = PR.load_prereg()["cpu_ceiling"]
    la = sub.add_parser("launch")
    la.add_argument("--namespace", required=True)
    la.add_argument("--slot", type=int, required=True)
    la.add_argument("--mode", choices=("real", "governed_manufactured", "manufactured", "burn", "diskfull"), required=True)
    la.add_argument("--fixture-id")
    la.add_argument("--cpu-soft", type=int, default=ceil["per_attempt_cpu_seconds_soft"])
    la.add_argument("--cpu-hard", type=int, default=ceil["per_attempt_cpu_seconds_rlimit"])
    la.add_argument("--wall", type=float, default=ceil["per_attempt_wall_seconds"])
    rc = sub.add_parser("recover")
    rc.add_argument("--namespace", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "recover":
        r = recover(Path(a.namespace))
        print(json.dumps({k: {x: v[x] for x in ("class", "action", "live")} for k, v in r.items()}, indent=1))
        return 0 if all(v["action"] != "ADJUDICATION_REQUIRED" for v in r.values()) else 2
    r = supervise(Path(a.namespace) / PR.slot_dir(a.slot), a.mode, cpu_soft=a.cpu_soft, cpu_hard=a.cpu_hard,
                  wall=a.wall, fixture_id=a.fixture_id)
    print(json.dumps({k: r.get(k) for k in ("terminal", "failure_class", "arithmetic_started", "prelaunch", "problems")}))
    if r.get("prelaunch") == "PRELAUNCH_REFUSED":
        return 3
    return 0 if r["failure_class"] is None else 1


if __name__ == "__main__":
    sys.exit(main())
