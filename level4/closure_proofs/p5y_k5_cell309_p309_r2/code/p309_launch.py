"""P309-r2 launcher (R2-I6; plan section 7; review conditions P10, P11; addendum 2, F5).

Starts ONE detached, fail-closed run in a transient systemd system unit, and never retries:

  python3 -B code/p309_launch.py --mode {drill|official|host-rerun} --host-config HOST.json [--print-only]

Before anything starts it requires all of these, in order, refusing on the first that fails:
  0. the unit user is not root, does not own a foreign root, and is not a configured cell-308 uid (A16); every
     foreign root is an absolute path of the characters [A-Za-z0-9._/+@,=~-] only (follow-up V2, W3: systemd would
     quote any other character in its property output, which the redaction could then miss, and ":" separates
     P309_FOREIGN_ROOTS);
  1. P309_SCRATCH_ROOT is valid (P7); for an official run or a host re-run it must be empty;
  2. the durability preflight passes (owner message 1, section 5.B; P15);
  3. the cross-campaign exclusion gate passes (owner message 3, item 4; P9);
  4. the isolation check passes (owner message 3, items 2 and 5);
  5. no unit named p309-r2-* is loaded (no stale or concurrent P309 run); a failing systemctl is a blocker (A16);
  6. the launcher itself runs as the unit user, since the gate and the isolation check are evaluated as the
     launcher's user (follow-up V4; a blocker, recorded like the others).

The unit:
* Its name is p309-r2-drill-<utc>, p309-r2-qualify-<utc> or p309-r2-hostrerun-<utc>, fixed by the mode. A drill can
  never carry the official name, nor the reverse. The host re-run (QC10 on an owner-named host, rev. 2c A14) runs
  only in its own mode, under the same gates and Q-HOST (review C7).
* It runs as the P309 user (`--uid`/`--gid`; P12).
* Its properties are Restart=no, KillMode=control-group with KillSignal=SIGKILL and TimeoutStopSec=10s (the heavy
  jobs ignore SIGTERM; review C5), MemoryMax, OOMScoreAdjust and a low CPU and IO weight, plus ProtectSystem=strict
  with ReadWritePaths for the P309 repository and scratch root only, PrivateTmp and InaccessiblePaths for every foreign
  root (P9, P11).
* Its environment is a fixed hermetic set (git with GIT_CONFIG_GLOBAL=/dev/null, TMPDIR, P309_SCRATCH_ROOT,
  P309_FOREIGN_ROOTS, P309_HOST_CONFIG, P309_LAUNCH_RECORD). Nothing is inherited.
* The program is the pinned interpreter with `-B` and the frozen script. argv[0] is not altered.

The gate results, the host configuration and the exact unit command are written to
<P309_SCRATCH_ROOT>/launch_<utc>.json before the start; the unit gets its path as P309_LAUNCH_RECORD, and the runner's
Q-HOST refuses to start without it.  The record is redacted (review C9): foreign roots and the cell-308 patterns appear
only as sha256, in the configuration and in the unit command.  It binds the configuration file by its sha256; the
runner reads that file itself (P309_HOST_CONFIG) and refuses if its bytes differ.
--print-only stops after printing them. That is the only form used where systemd is absent, such as the cloud
development tier.
"""
import json
import os
import pwd
import re
import subprocess
import sys
import time
from pathlib import Path

FNS = Path(__file__).resolve().parents[1]
REPO = FNS.parents[2]
sys.path.insert(0, str(FNS / "code"))
import p309_host as H  # noqa: E402

UNIT_PREFIX = "p309-r2-"
UNIT_NAME = {"drill": "p309-r2-drill-", "official": "p309-r2-qualify-", "host-rerun": "p309-r2-hostrerun-"}
SCRIPT = {"drill": ["code/p309_topology_drill.py", "--tier", "worker"],
          "official": ["code/p309_qualify.py", "--workers", "4"],
          "host-rerun": ["code/p309_qualify.py", "--host-rerun", "--workers", "4"]}
LAUNCH_KEYS = H.LAUNCH_KEYS


def refuse(msg: str) -> int:
    print(json.dumps({"launched": False, "refused": msg}))
    return 2


def unit_name(mode: str, stamp: str) -> str:
    name = UNIT_NAME[mode] + stamp
    other = [m for m in UNIT_NAME if m != mode]
    if not re.fullmatch(r"p309-r2-(drill|qualify|hostrerun)-\d{8}T\d{6}Z", name) or any(
            name.startswith(UNIT_NAME[o]) for o in other):
        raise H.HostError("unit name does not match its mode")
    return name


def loaded_p309_units() -> list:
    """systemctl's read-only unit listing, filtered to the P309 prefix (None if systemctl is absent or fails: A16)."""
    if not H.shutil.which("systemctl"):
        return None
    try:
        p = subprocess.run(["systemctl", "list-units", "--all", "--no-legend", "--plain"], stdin=subprocess.DEVNULL,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if p.returncode != 0:
        return None
    return [l.split()[0] for l in p.stdout.splitlines() if l.split() and l.split()[0].startswith(UNIT_PREFIX)]


def unit_user_check(launch: dict, cfg: dict) -> None:
    """A16: the unit user exists, is not root, owns no foreign root and is not a configured cell-308 uid"""
    try:
        uid = pwd.getpwnam(launch["unit_user"]).pw_uid
    except KeyError:
        raise H.HostError("the unit user does not exist")
    if uid == 0:
        raise H.HostError("the unit user is root")
    if uid in (cfg.get("foreign_uids") or []):
        raise H.HostError("the unit user is a configured cell-308 uid")
    if not all(re.fullmatch(r"/[A-Za-z0-9._/+@,=~-]*", f) for f in cfg["foreign_roots"]):
        raise H.HostError("a foreign root is not an absolute path of the characters [A-Za-z0-9._/+@,=~-]")
    for f in cfg["foreign_roots"]:
        try:
            if os.stat(f).st_uid == uid:
                raise H.HostError("the unit user owns a foreign root")
        except OSError:
            continue


def redact_argv(argv: list, cfg: dict) -> list:
    """the unit command as it may be recorded: every foreign root as sha256 (review C9)"""
    out = []
    for a in argv:
        for f in sorted(cfg["foreign_roots"], key=len, reverse=True):
            a = a.replace(f, "sha256:" + H.sha(f)) if isinstance(a, str) else a   # an unset interpreter stays None
        out.append(a)
    return out


def unit_argv(mode: str, name: str, cfg: dict, launch: dict, scratch: str, record: str, host_config: str) -> list:
    foreign = list(cfg["foreign_roots"])
    env = {"LC_ALL": "C", "PATH": "/usr/bin:/bin", "HOME": os.path.join(scratch, "home"),
           "TMPDIR": os.path.join(scratch, "tmp"), "P309_SCRATCH_ROOT": scratch,
           "P309_FOREIGN_ROOTS": os.pathsep.join(foreign), "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null",
           "GIT_TERMINAL_PROMPT": "0", "GIT_OPTIONAL_LOCKS": "0", "PYTHONDONTWRITEBYTECODE": "1",
           "PYTHONNOUSERSITE": "1", "P309_LAUNCH_RECORD": record, "P309_HOST_CONFIG": host_config}
    props = ["Restart=no", "KillMode=control-group", "KillSignal=SIGKILL", "SendSIGKILL=yes", "TimeoutStopSec=10s",
             "MemoryMax=%s" % launch["memory_max"],
             "OOMScoreAdjust=%d" % int(launch["oom_score_adjust"]), "CPUWeight=%d" % int(launch["cpu_weight"]),
             "IOWeight=%d" % int(launch["io_weight"]), "ProtectSystem=strict", "PrivateTmp=yes",
             "NoNewPrivileges=yes", "ReadWritePaths=%s %s" % (str(REPO), scratch),
             "WorkingDirectory=%s" % str(FNS)]
    props += ["InaccessiblePaths=-%s" % f for f in foreign]
    argv = ["systemd-run", "--unit=" + name, "--uid=" + launch["unit_user"], "--gid=" + launch["unit_group"],
            "--no-block"]
    for p in props:
        argv += ["--property=" + p]
    for k in sorted(env):
        argv += ["--setenv=%s=%s" % (k, env[k])]
    script = SCRIPT[mode]
    return argv + ["--", cfg["interpreter"], "-B", str(FNS / script[0])] + script[1:]


def main() -> int:
    argv = sys.argv[1:]
    if "--mode" not in argv or "--host-config" not in argv:
        print(__doc__)
        return 2
    mode = argv[argv.index("--mode") + 1]
    if mode not in UNIT_NAME:
        return refuse("unknown mode")
    host_config = os.path.realpath(argv[argv.index("--host-config") + 1])
    try:
        cfg, launch = H.load_launch_config(host_config, str(REPO), mode != "drill")
        unit_user_check(launch, cfg)
        stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        name = unit_name(mode, stamp)
        scratch = H.scratch_root(dict(os.environ), str(REPO), cfg)
    except (H.HostError, OSError, ValueError) as exc:
        return refuse(str(exc))
    record = {"schema": "P309_R2_LAUNCH/2", "utc": H.utc(), "mode": mode, "unit": name,
              "host_config": H.redacted_config(cfg), "host_config_sha256": H.config_sha256(cfg),
              "host_config_file": host_config, "host_config_file_sha256": H.file_sha256(host_config),
              "launch_settings": launch, "scratch_root": scratch}
    record["preflight"] = H.durability_preflight(cfg, dict(os.environ), str(REPO))
    record["gate"] = H.exclusion_gate(cfg)
    record["isolation"] = H.isolation(cfg)
    units = loaded_p309_units()
    record["p309_units_loaded"] = units
    out = os.path.join(scratch, "launch_%s.json" % stamp)
    real_argv = unit_argv(mode, name, cfg, launch, scratch, out, host_config)
    record["argv"] = redact_argv(real_argv, cfg)
    blockers = [k for k in ("preflight", "gate", "isolation") if not record[k]["pass"]]
    if units is None or units:
        blockers.append("p309_units_loaded" if units else "systemctl_unavailable")
    if os.getuid() != pwd.getpwnam(launch["unit_user"]).pw_uid:
        blockers.append("launcher_not_unit_user")
    record["blockers"] = blockers
    with open(out, "x") as fh:                    # exclusive: a launch record is never overwritten
        fh.write(json.dumps(record, indent=1, sort_keys=True, default=str) + "\n")
    if "--print-only" in argv:
        print(json.dumps({"launched": False, "print_only": True, "record": out, "blockers": blockers,
                          "argv": record["argv"]}, indent=1))
        return 0 if not blockers else 1
    if blockers:
        return refuse("blocked by %s (record %s)" % (blockers, out))
    for d in ("home", "tmp"):                     # the unit's HOME and TMPDIR, inside the scratch root
        os.mkdir(os.path.join(scratch, d))
    p = subprocess.run(real_argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       universal_newlines=True, timeout=60)
    print(json.dumps({"launched": p.returncode == 0, "unit": name, "record": out, "rc": p.returncode,
                      "stderr_tail": p.stderr[-400:], "watch": "journalctl -u %s -f" % name}, indent=1))
    return 0 if p.returncode == 0 else 1          # never retried: a failed start is reported, not repeated


if __name__ == "__main__":
    sys.exit(main())
