"""Supervisor of one executor attempt (EXECUTOR_SPEC_R2.md R2-2).

    python -B code/supervisor.py --state-dir S -- <executor_cli arguments>
        [--cpu-soft 9000 --cpu-hard 10800 --wall 14400]    (overrides are for QUALIFICATION only)

Launches code/executor_cli.py as a child with RLIMIT_CPU (soft, hard) set before exec, runs a wall watchdog (SIGTERM, so
the executor seals VOID; SIGKILL 60 s later), and records the wait status, the child's CPU seconds from wait4 rusage and
the boot id before and after. The failure class is derived only by the frozen probe_rules.failure_class from this
supervisor evidence, never self-declared by the executor. Markers in the state dir: RUN_STATE.json (child pid) and then
RUN_COMPLETE.json (sealed) or RUN_FAILED.json (refused, VOID or killed).
"""
from __future__ import annotations

import argparse
import json
import os
import resource
import signal
import subprocess
import sys
import time
from pathlib import Path

import paths  # noqa: F401

import probe_rules as PR  # noqa: E402

CLI = Path(__file__).resolve().parent / "executor_cli.py"
SEALS = {"SCIENTIFIC_RECORD_SEALED.json", "MANUFACTURED_RECORD_SEALED.json", "VOID_RECORD_SEALED.json",
         "MANUFACTURED_VOID_RECORD_SEALED.json"}


def boot_id() -> str | None:
    try:
        return Path("/proc/sys/kernel/random/boot_id").read_text().strip()
    except OSError:
        return None


def _write(path: Path, obj: dict) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, indent=1, sort_keys=True) + "\n")
    os.replace(tmp, path)


def supervise(cli_args: list, state_dir: Path, *, cpu_soft: int, cpu_hard: int, wall: float, cli: Path = CLI) -> dict:
    """`cli` differs from code/executor_cli.py only in the qualification V01 test (a mutant-shadowing wrapper)."""
    state_dir.mkdir(parents=True, exist_ok=True)
    out_dir = Path(cli_args[cli_args.index("--output-dir") + 1])
    boot0 = boot_id()

    def limits():
        resource.setrlimit(resource.RLIMIT_CPU, (int(cpu_soft), int(cpu_hard)))

    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", NUMEXPR_NUM_THREADS="1",
               PYTHONHASHSEED="0")
    stderr_path = state_dir / "child_stderr.log"
    w0 = time.time()
    with open(stderr_path, "w") as err, open(state_dir / "child_stdout.log", "w") as so:
        child = subprocess.Popen([sys.executable, "-B", str(cli), *cli_args], env=env, stdout=so, stderr=err,
                                 preexec_fn=limits)
        _write(state_dir / "RUN_STATE.json", {"child_pid": child.pid, "supervisor_pid": os.getpid(), "boot_id": boot0,
                                             "started_unix": w0, "cpu_soft": cpu_soft, "cpu_hard": cpu_hard, "wall": wall})
        wall_timeout, term_sent = False, None
        while True:
            pid, status, ru = os.wait4(child.pid, os.WNOHANG)
            if pid == child.pid:
                break
            now = time.time()
            if now - w0 >= wall and term_sent is None:
                wall_timeout, term_sent = True, now
                child.send_signal(signal.SIGTERM)
            elif term_sent is not None and now - term_sent > 60:
                child.send_signal(signal.SIGKILL)
            time.sleep(0.2)
    child.returncode = os.waitstatus_to_exitcode(status)
    sig = os.WTERMSIG(status) if os.WIFSIGNALED(status) else None
    code = os.WEXITSTATUS(status) if os.WIFEXITED(status) else None
    child_cpu = ru.ru_utime + ru.ru_stime
    err_text = stderr_path.read_text()
    refusal = next((ln for ln in err_text.splitlines() if ln.startswith("EXECUTOR_REFUSAL:")), None)
    sealed = sorted(p.name for p in out_dir.glob("*_SEALED.json")) if out_dir.exists() else []
    log = out_dir / "ATTEMPT_LOG.jsonl"
    events = [json.loads(x)["event"] for x in log.read_text().splitlines()] if log.exists() else []
    evidence = {"boot_id_changed": boot_id() != boot0, "child_cpu_seconds": child_cpu, "wall_seconds": time.time() - w0,
                "wall_timeout": wall_timeout, "signal": sig, "exit_code": code,
                "cpu_soft_limit_reached": child_cpu >= cpu_soft or (refusal is not None and "CPU_RLIMIT" in refusal),
                "kernel_oom_record": False, "enospc": "No space left on device" in err_text,
                "integrity_refusal": refusal if code == 3 else None}
    success = code == 0 and any(s in sealed for s in ("SCIENTIFIC_RECORD_SEALED.json", "MANUFACTURED_RECORD_SEALED.json"))
    result = {"evidence": evidence, "sealed_files": sealed, "events": events,
              "arithmetic_started": "ARITHMETIC_STARTED" in events,
              "failure_class": None if success else PR.failure_class(evidence), "refusal": refusal}
    _write(state_dir / ("RUN_COMPLETE.json" if success else "RUN_FAILED.json"), result)
    return result


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    sep = argv.index("--")
    ap = argparse.ArgumentParser()
    ap.add_argument("--state-dir", required=True)
    ceil = PR.load_prereg()["cpu_ceiling"]
    ap.add_argument("--cpu-soft", type=int, default=ceil["per_attempt_cpu_seconds_soft"])
    ap.add_argument("--cpu-hard", type=int, default=ceil["per_attempt_cpu_seconds_rlimit"])
    ap.add_argument("--wall", type=float, default=ceil["per_attempt_wall_seconds"])
    a = ap.parse_args(argv[:sep])
    r = supervise(argv[sep + 1:], Path(a.state_dir), cpu_soft=a.cpu_soft, cpu_hard=a.cpu_hard, wall=a.wall)
    print(json.dumps({k: r[k] for k in ("sealed_files", "failure_class", "arithmetic_started")}))
    return 0 if r["failure_class"] is None else 1


if __name__ == "__main__":
    sys.exit(main())
