"""Cell-308 MB-S successor campaign (r1) -- the launchd launcher (architecture section 5). No science.

`launch execute | resume | recover` installs a TRANSIENT LaunchAgent (a plist in the spool's launch directory, never
~/Library/LaunchAgents) with a unique label org.rebaseguard.mbs308.<mode>.<utc>:
  ProgramArguments  the pinned interpreter with -I -S -B, the driver, the mode;
  RunAtLoad true, KeepAlive false, AbandonProcessGroup true, ProcessType Standard;
  StandardOutPath / StandardErrorPath under ~/Library/Logs/ReBaseGuard/mbs308/ (never /private/tmp);
  WorkingDirectory the worktree; EnvironmentVariables MBS308_LAUNCH_LABEL = the label (the driver's execute / resume
  refuse unless XPC_SERVICE_NAME equals it, the parent is launchd and `launchctl print` names this pid).
It is started with `launchctl bootstrap gui/<uid> <plist>`: the job is launchd's child, outside the hosting app's
process tree, session and coalition. The launcher then records the label, pid, PPID, PGID, SID, uid, the process start
time and the boot UUID, and PROVES detachment by test, not by PPID = 1: the job is not a descendant of the launcher or
of the launcher's ancestors, its session differs from the launcher's, and launchd names it as the running job.

`execute` is refused unless the driver's `preflight` passes first (run synchronously here); `resume` is refused unless
`status` prints CONSUMED_INTERRUPTED. With --wait (default) the launcher waits for the job, then boots it out and
removes the plist; with --no-wait it returns after the detachment proof and `cleanup <label>` boots out a finished job.
The launcher never computes and never touches a ref.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import plistlib
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve()
CODE = HERE.parent
REPO = HERE.parents[4]
sys.path.insert(0, str(CODE))
import mbs308_host as HOST  # noqa: E402

DRIVER = CODE / "mbs308_driver.py"
PYTHON = "/Library/Frameworks/Python.framework/Versions/3.14/bin/python3.14"
LABEL_PREFIX = "org.rebaseguard.mbs308."
LOG_DIR = Path.home() / "Library/Logs/ReBaseGuard/mbs308"
MODES = ("execute", "resume", "recover")
ENV = {"PATH": "/usr/bin:/bin:/usr/sbin", "LC_ALL": "C"}


class LaunchRefused(Exception):
    def __init__(self, code: str, detail: str = ""):
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = code


def utc_compact() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def _run(args: list, timeout: int = 60) -> subprocess.CompletedProcess:
    return subprocess.run(args, capture_output=True, text=True, env=ENV, stdin=subprocess.DEVNULL, timeout=timeout)


# ------------------------------------------------------------------ process relations (the detachment proof)
def ancestors(pid: int, limit: int = 64) -> list:
    """[pid, ppid, ppid(ppid), ...] up to and including 1 (or the first unreadable link)."""
    chain = [int(pid)]
    while len(chain) < limit and chain[-1] > 1:
        pp = HOST.process_ppid(chain[-1])
        if pp is None:
            break
        chain.append(pp)
    return chain


def getsid(pid: int) -> int | None:
    try:
        return os.getsid(int(pid))
    except OSError:
        return None


def prove_detached(job_pid: int, launcher_pid: int, label: str) -> dict:
    """Detachment by test, never by PPID = 1 alone: (a) the job is not a descendant of the launcher or of any of the
    launcher's ancestors other than launchd (pid 1); (b) its session differs from the launcher's; (c) launchd names the
    job as running with this pid. PPID is recorded, not relied on."""
    job_chain = ancestors(job_pid)
    launcher_chain = [p for p in ancestors(launcher_pid) if p > 1]
    not_descendant = not any(p in job_chain[1:] for p in launcher_chain)
    sid_job, sid_launcher = getsid(job_pid), getsid(launcher_pid)
    other_session = sid_job is not None and sid_launcher is not None and sid_job != sid_launcher
    lpid = HOST.launchd_job_pid(label) if label else None
    named = lpid == int(job_pid)
    return {"job_pid": int(job_pid), "job_ancestors": job_chain, "launcher_pid": int(launcher_pid),
            "launcher_ancestors": launcher_chain, "not_descendant_of_launcher_tree": not_descendant,
            "job_sid": sid_job, "launcher_sid": sid_launcher, "session_differs": other_session,
            "launchctl_pid": lpid, "launchd_names_job_running": named,
            "ppid_recorded_not_relied_on": HOST.process_ppid(job_pid),
            "detached": bool(not_descendant and other_session and named)}


# ------------------------------------------------------------------ plist, bootstrap, record, bootout
def make_plist(label: str, program: list, workdir: Path, log_dir: Path, env_extra: dict | None = None) -> dict:
    env = {"MBS308_LAUNCH_LABEL": label, "PATH": "/usr/bin:/bin:/usr/sbin", "HOME": str(Path.home())}
    env.update(env_extra or {})
    return {"Label": label, "ProgramArguments": [str(x) for x in program], "RunAtLoad": True, "KeepAlive": False,
            "AbandonProcessGroup": True, "ProcessType": "Standard", "WorkingDirectory": str(workdir),
            "StandardOutPath": str(log_dir / f"{label}.out.log"), "StandardErrorPath": str(log_dir / f"{label}.err.log"),
            "EnvironmentVariables": env}


def bootout(label: str) -> bool:
    return _run(["/bin/launchctl", "bootout", f"gui/{os.getuid()}/{label}"]).returncode == 0


def job_loaded(label: str) -> bool:
    return _run(["/bin/launchctl", "print", f"gui/{os.getuid()}/{label}"]).returncode == 0


def launch(program: list, label: str, plist_dir: Path, log_dir: Path, workdir: Path, record_dir: Path | None = None,
           env_extra: dict | None = None, wait_s: float = 15.0) -> dict:
    """Install and bootstrap the transient LaunchAgent; return the launch record with the detachment proof. On any
    failure after the bootstrap the job is booted out and the plist removed."""
    if not label.startswith(LABEL_PREFIX):
        raise LaunchRefused("LABEL", "the label must carry the campaign prefix")
    plist_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    path = plist_dir / f"{label}.plist"
    with open(path, "xb") as fh:
        plistlib.dump(make_plist(label, program, workdir, log_dir, env_extra), fh)
    boot = _run(["/bin/launchctl", "bootstrap", f"gui/{os.getuid()}", str(path)])
    if boot.returncode != 0:
        path.unlink(missing_ok=True)
        raise LaunchRefused("BOOTSTRAP_FAILED", boot.stderr.strip()[:200])
    try:
        pid, t_end = None, time.time() + wait_s
        while pid is None and time.time() < t_end:
            pid = HOST.launchd_job_pid(label)
            if pid is None:
                time.sleep(0.1)
        if pid is None:
            raise LaunchRefused("NOT_RUNNING", "launchd never reported the job running")
        me = os.getpid()
        rec = {"label": label, "plist": str(path), "program": [str(x) for x in program], "uid": os.getuid(),
               "pid": pid, "ppid": HOST.process_ppid(pid), "pgid": os.getpgid(pid), "sid": getsid(pid),
               "start_time": HOST.process_start(pid), "boot_uuid": HOST.boot_session_uuid(),
               "command_sha256": HOST.process_command_sha256(pid),
               "launcher": {"pid": me, "pgid": os.getpgid(0), "sid": os.getsid(0), "ppid": os.getppid()},
               "launched_utc": utc_compact(), "detachment": prove_detached(pid, me, label)}
        if not rec["detachment"]["detached"]:
            raise LaunchRefused("NOT_DETACHED", json.dumps(rec["detachment"])[:300])
        if record_dir is not None:
            record_dir.mkdir(parents=True, exist_ok=True)
            (record_dir / f"{label}.launch.json").write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n")
        return rec
    except BaseException:
        bootout(label)
        path.unlink(missing_ok=True)
        raise


def wait_and_cleanup(label: str, plist: str, poll_s: float = 2.0, timeout_s: float | None = None) -> dict:
    """Wait until launchd no longer runs the job, then boot it out and remove the plist."""
    t0 = time.time()
    while HOST.launchd_job_pid(label) is not None:
        if timeout_s is not None and time.time() - t0 > timeout_s:
            break
        time.sleep(poll_s)
    info = _run(["/bin/launchctl", "print", f"gui/{os.getuid()}/{label}"]).stdout
    last = None
    for ln in info.splitlines():
        if "last exit code" in ln:
            last = ln.split("=", 1)[-1].strip()
    out = {"label": label, "last_exit": last, "booted_out": bootout(label)}
    Path(plist).unlink(missing_ok=True)
    return out


# ------------------------------------------------------------------ the campaign modes
def driver_cmd(mode: str) -> list:
    return [PYTHON, "-I", "-S", "-B", str(DRIVER), mode]


def pre_launch(mode: str) -> dict:
    """execute: the driver's preflight must pass (synchronously, before anything is launched); resume: status must be
    CONSUMED_INTERRUPTED. recover: no gate (the driver itself refuses what it must)."""
    if mode == "execute":
        p = _run(driver_cmd("preflight"), timeout=1900)
        if p.returncode != 0 or "MBS308 PREFLIGHT PASS" not in p.stdout:
            raise LaunchRefused("PREFLIGHT_FAILED", (p.stdout.strip().splitlines() or ["(no output)"])[-1][:300])
        return {"preflight": "PASS"}
    if mode == "resume":
        p = _run(driver_cmd("status"))
        if p.stdout.strip() != "CONSUMED_INTERRUPTED":
            raise LaunchRefused("RESUME_NOT_APPLICABLE", p.stdout.strip()[:80])
        return {"status": "CONSUMED_INTERRUPTED"}
    return {}


def spool_launch_dir() -> Path:
    gd = _run(["/usr/bin/git", "-C", str(REPO), "rev-parse", "--path-format=absolute", "--git-dir"]).stdout.strip()
    return Path(gd) / "mbs308-spool" / "launch"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=(*MODES, "cleanup"))
    ap.add_argument("label", nargs="?")
    ap.add_argument("--no-wait", action="store_true")
    a = ap.parse_args(argv)
    if a.mode == "cleanup":
        if not a.label or not a.label.startswith(LABEL_PREFIX):
            print("MBS308 LAUNCH REFUSED LABEL")
            return 2
        if HOST.launchd_job_pid(a.label) is not None:
            print("MBS308 LAUNCH REFUSED STILL_RUNNING")
            return 2
        print(json.dumps(wait_and_cleanup(a.label, str(spool_launch_dir() / f"{a.label}.plist"), timeout_s=0)))
        return 0
    if os.path.realpath(sys.executable) != os.path.realpath(PYTHON):
        print("MBS308 LAUNCH REFUSED INTERPRETER")
        return 2
    try:
        gate = pre_launch(a.mode)
        label = f"{LABEL_PREFIX}{a.mode}.{utc_compact()}"
        d = spool_launch_dir()
        rec = launch(driver_cmd(a.mode), label, d, LOG_DIR, REPO, record_dir=LOG_DIR)
        rec["gate"] = gate
        rec["launcher_sha256"] = hashlib.sha256(HERE.read_bytes()).hexdigest()
        (LOG_DIR / f"{label}.launch.json").write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n")
        print(f"MBS308 LAUNCHED {label} pid {rec['pid']} (detached: {rec['detachment']['detached']})")
    except LaunchRefused as e:
        print(f"MBS308 LAUNCH REFUSED {e}")
        return 2
    if a.no_wait:
        return 0
    out = wait_and_cleanup(label, rec["plist"])
    print(f"MBS308 LAUNCH FINISHED {label}: last exit {out['last_exit']}; booted out {out['booted_out']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
