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

`execute` is refused unless the driver's `preflight` passes first (run synchronously here, with the timeout RULE
PRE_CAP_S + 100 s, PRE_CAP_S read from the driver's own bytes, so the driver's own PRE_CAP refusal always comes first);
`resume` is refused unless `status` prints CONSUMED_INTERRUPTED. With --wait (default) the launcher waits for the job,
then boots it out and removes the plist; with --no-wait it returns after the detachment proof and `cleanup <label>` boots out a finished job.
The launcher never computes and never touches a ref.
"""
from __future__ import annotations

import argparse
import ast
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


def driver_literal(name: str):
    """A module-level literal of the driver, read from its bytes: the launcher never imports the driver (that would
    load the science). No such literal: the launcher refuses to load."""
    for node in ast.parse(DRIVER.read_text()).body:
        if isinstance(node, ast.Assign) and [getattr(t, "id", None) for t in node.targets] == [name]:
            return ast.literal_eval(node.value)
    raise RuntimeError(f"the driver defines no literal {name}")


# CONSTANTS_RATIFICATION_MBS308 item 31 (research 3c2a7854): the preflight timeout is the RULE PRE_CAP_S + 100 s; it
# follows the driver's PRE_CAP_S
PRE_CAP_S = driver_literal("PRE_CAP_S")


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
    """Install and bootstrap the transient LaunchAgent; return the launch record (with the job identity and the
    detachment proof when launchd reported the job). R2: after the bootstrap the launcher NEVER boots the job out --
    the job may already have passed the marker; a job that is not properly launched is refused by the driver's own
    launchd check (XPC_SERVICE_NAME = label, PPID 1, launchctl pid = self). Only a bootstrap failure removes the plist."""
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
        me = os.getpid()
        rec = {"label": label, "plist": str(path), "program": [str(x) for x in program], "uid": os.getuid(),
               "pid": pid, "observed": pid is not None, "boot_uuid": HOST.boot_session_uuid(),
               "launcher": {"pid": me, "pgid": os.getpgid(0), "sid": os.getsid(0), "ppid": os.getppid()},
               "launched_utc": utc_compact()}
        if pid is not None:
            rec.update({"ppid": HOST.process_ppid(pid), "pgid": os.getpgid(pid), "sid": getsid(pid),
                        "start_time": HOST.process_start(pid), "command_sha256": HOST.process_command_sha256(pid),
                        "identity": HOST.identity(pid), "detachment": prove_detached(pid, me, label)})
        if record_dir is not None:
            record_dir.mkdir(parents=True, exist_ok=True)
            (record_dir / f"{label}.launch.json").write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n")
        return rec
    except BaseException:
        raise                    # never boot out after the bootstrap (R2): the job may have passed the marker


def wait_and_cleanup(label: str, plist: str, identity: dict | None, poll_s: float = 2.0) -> dict:
    """R2: wait until the RECORDED job identity (pid, start time, boot UUID, command sha256) is positively DEAD
    (HOST.identity_state), then boot the job out and remove the plist. A failing, timed-out or unparseable
    `launchctl print` never decides anything; without a recorded identity nothing is booted out."""
    if not identity:
        raise LaunchRefused("NO_IDENTITY", "the job's identity was never recorded: it is never booted out here")
    while HOST.identity_state(identity) != "DEAD":
        time.sleep(poll_s)
    info = _run(["/bin/launchctl", "print", f"gui/{os.getuid()}/{label}"]).stdout
    last = None
    for ln in info.splitlines():
        if "last exit code" in ln:
            last = ln.split("=", 1)[-1].strip()
    out = {"label": label, "last_exit": last, "booted_out": bootout(label)}
    Path(plist).unlink(missing_ok=True)
    return out


def cleanup(label: str, record_dir: Path) -> dict:
    """Boot out a finished job: only with its launch record and only when the recorded identity is DEAD (R2)."""
    try:
        rec = json.loads((record_dir / f"{label}.launch.json").read_text())
    except (OSError, ValueError):
        raise LaunchRefused("NO_RECORD", "no launch record: the job is never booted out without its identity")
    ident = rec.get("identity")
    if not ident:
        raise LaunchRefused("NO_IDENTITY", "the launch record carries no job identity")
    st = HOST.identity_state(ident)
    if st != "DEAD":
        raise LaunchRefused("STILL_RUNNING" if st == "ALIVE" else "IDENTITY_UNKNOWN", st)
    return wait_and_cleanup(label, rec["plist"], ident)


# ------------------------------------------------------------------ the campaign modes
def driver_cmd(mode: str) -> list:
    return [PYTHON, "-I", "-S", "-B", str(DRIVER), mode]


def pre_launch(mode: str) -> dict:
    """execute: the driver's preflight must pass (synchronously, before anything is launched); resume: status must be
    CONSUMED_INTERRUPTED. recover: no gate (the driver itself refuses what it must)."""
    if mode == "execute":
        p = _run(driver_cmd("preflight"), timeout=PRE_CAP_S + 100)
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
        try:
            print(json.dumps(cleanup(a.label, LOG_DIR)))
        except LaunchRefused as e:
            print(f"MBS308 LAUNCH REFUSED {e}")
            return 2
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
        det = (rec.get("detachment") or {}).get("detached")
        print(f"MBS308 LAUNCHED {label} pid {rec['pid']} (detached: {det}; never booted out by the launcher while "
              "its recorded identity lives)")
    except LaunchRefused as e:
        print(f"MBS308 LAUNCH REFUSED {e}")
        return 2
    if a.no_wait or not rec.get("identity"):
        return 0
    out = wait_and_cleanup(label, rec["plist"], rec["identity"])
    print(f"MBS308 LAUNCH FINISHED {label}: last exit {out['last_exit']}; booted out {out['booted_out']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
