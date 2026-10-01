"""P309-r2 host package (R2-I4, R2-I6; plan sections 6-8; addenda 1 and 2; review conditions P7, P9-P12, P15, F8).

Read-only functions for the compute host that P309-r2 may share with the cell-308 campaign (owner message 3):

  audit(cfg)                     the read-only worker audit (gate step 8a); safe to feed to a system python on stdin
  provenance(cfg)                host identity and runtime facts (identities only as sha256)
  continuity(base, now, cfg)     Q-HOST: still the same host, not rebooted, not suspended, same runtime
  exclusion_gate(cfg)            the cross-campaign exclusion gate before every heavy run (owner message 3, item 4)
  isolation(cfg)                 no campaign state shared with another checkout (owner message 3, items 2 and 5)
  durability_preflight(cfg)      the fail-closed durability gate (owner message 1, section 5.B; P15)
  scratch_root(env, repo, cfg)   P309_SCRATCH_ROOT validation (P7)
  qhost_monitor(...)             Q-HOST sampling during a run (P10); rows on standard output; signals only its parent
  monitor_liveness(...)          Q-HOST: the monitor lived to the stop and left no gap (review C4)
  kill_own_descendants()         the runner's abort: SIGKILL its own process tree at once (review C5)
  unit_properties()              `systemctl show` of the calling process's own P309 unit, redacted (review C9)

What it never does:
* write anything except its own standard output: no file, no directory, no ref;
* signal, renice or otherwise touch any process, with two exceptions: the Q-HOST monitor's single SIGTERM to its own
  parent, the P309 runner; and kill_own_descendants(), which the runner calls on a Q-HOST abort to stop its own
  descendants (never another process);
* read inside a foreign (cell-308) checkout. A foreign root is only stat()ed at its top directory, and access() is
  asked whether this user could read it;
* run git anywhere but in the P309 repository;
* record a foreign process's command line, working directory or environment. Foreign processes appear only as pid,
  uid, a tag, a CPU fraction and the sha256 of their command line. Foreign roots and the cell-308 patterns appear in a
  record only as sha256 (redacted_config; review C9);
* record a secret. The hostname, machine-id and cloud instance id appear only as sha256 values.

It must run on the worker's system python 3.6 or later (step 8a), so it avoids newer syntax.

  python3 p309_host.py {audit|gate|isolation|provenance|preflight|scratch} [--config PATH | --config-json JSON]
  python3 p309_host.py qhost-monitor --parent PID --interval S < {"cfg": ..., "baseline": ...}   (runner only; the
                                     configuration arrives on standard input, never on the command line: review C9)
  python3 - audit --config-json '{...}' < p309_host.py      # step 8a: nothing is written on the worker

Exit status: 0 if the subcommand passes (audit and provenance always pass), 1 if it fails, 2 on a usage error.
"""
import hashlib
import json
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
import time
import urllib.request

SCHEMA = "P309_R2_HOST/1"
HEAVY_P309 = re.compile(r"p309_qualify\.py|p309_driver\.py\s+(_job|decoy)|p309_topology_drill\.py|"
                        r"p309-r2-(drill|qualify|hostrerun)")
BURSTABLE = re.compile(r"^(t2|t3|t3a|t4g)\.")
DEFAULTS = {"p309_repo": None, "p309_roots": [], "foreign_roots": [], "foreign_patterns": [r"cell[_-]?308"],
            "foreign_heavy_patterns": [], "load_baseline": 0.0, "load_margin": 0.5, "heavy_cpu_fraction": 0.05,
            "ram_floor_gb": 8, "disk_floor_gb": 40, "min_cpus": 4, "sample_s": 60.0, "suspend_tolerance_s": 5.0,
            "monitor_heavy_cpu_fraction": 0.5, "monitor_aggregate_cpu_fraction": 1.0, "monitor_gap_tolerance_s": 30.0,
            "foreign_uids": [],
            "python_version": "3.11.15", "interpreter": None, "glibc": None,
            "branch": "refs/heads/claude/p5y-k5-cell309-p309-r2",  # q309: literal-ok (branch name, not a cell reference)
            "require_empty_scratch": False}


LAUNCH_KEYS = ("unit_user", "unit_group", "memory_max", "oom_score_adjust", "cpu_weight", "io_weight")
REDACTED_KEYS = ("foreign_roots", "foreign_patterns", "foreign_heavy_patterns")


class HostError(Exception):
    """A refusal that must fail loudly (P7: every consumer)."""


# ---------------------------------------------------------------------------------------------------------- basics
def sha(x):
    return hashlib.sha256(x.encode() if isinstance(x, str) else x).hexdigest()


def read(path, default=None):
    try:
        with open(path, "rb") as fh:
            return fh.read().decode("utf-8", "replace")
    except OSError:
        return default


def file_sha256(path):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as fh:
            for block in iter(lambda: fh.read(1 << 20), b""):
                h.update(block)
    except OSError:
        return None
    return h.hexdigest()


def utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def real(p):
    return os.path.realpath(p)


def under(path, roots):
    if not path:
        return False
    rp = real(path)
    return any(rp == real(r) or rp.startswith(real(r) + os.sep) for r in roots)


def overlaps(a, b):
    a, b = real(a), real(b)
    return a == b or a.startswith(b + os.sep) or b.startswith(a + os.sep)


def load_config(argv):
    cfg = dict(DEFAULTS)
    if "--config" in argv:
        with open(argv[argv.index("--config") + 1]) as fh:
            cfg.update(json.load(fh))
    if "--config-json" in argv:
        cfg.update(json.loads(argv[argv.index("--config-json") + 1]))
    unknown = sorted(set(cfg) - set(DEFAULTS))
    if unknown:
        raise HostError("unknown config keys: %s" % unknown)
    return cfg


def config_sha256(cfg):
    """the identity of a complete host configuration (canonical JSON)"""
    return sha(json.dumps(cfg, sort_keys=True))


def redacted_config(cfg):
    """the configuration as it may be recorded (review C9): foreign roots and the cell-308 patterns as sha256 only"""
    out = dict(cfg)
    for k in REDACTED_KEYS:
        out[k] = [sha(v) for v in cfg.get(k) or []]
    return out


def load_launch_config(path, p309_repo, require_empty):
    """the host configuration file as the launcher and the runner both read it: (cfg, launch settings)"""
    with open(path) as fh:
        raw = json.load(fh)
    launch = {k: raw.pop(k) for k in LAUNCH_KEYS if k in raw}
    if set(launch) != set(LAUNCH_KEYS):
        raise HostError("launch settings missing: %s" % sorted(set(LAUNCH_KEYS) - set(launch)))
    cfg = load_config(["--config-json", json.dumps(raw)])
    cfg["p309_repo"] = p309_repo
    cfg["require_empty_scratch"] = bool(require_empty)
    return cfg, launch


def _done(p):
    return {"rc": p.returncode, "out": p.stdout.strip()}


def system_reads():
    """The only non-git-repository commands this module runs: fixed, read-only argvs, each only if its program
    exists.  Returns {name: {"rc", "out"} or None}."""
    out = {}
    try:
        out["virt"] = _done(subprocess.run(["systemd-detect-virt"], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, universal_newlines=True, timeout=30)) if shutil.which(
            "systemd-detect-virt") else None
        out["container"] = _done(subprocess.run(["systemd-detect-virt", "--container"], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, universal_newlines=True, timeout=30)) if shutil.which(
            "systemd-detect-virt") else None
        out["boots"] = _done(subprocess.run(["journalctl", "--list-boots", "--no-pager"], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, universal_newlines=True, timeout=30)) if shutil.which(
            "journalctl") else None
        out["kernel_log"] = _done(subprocess.run(["journalctl", "-k", "--since", "-30d", "--no-pager"], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, universal_newlines=True, timeout=30)) if shutil.which(
            "journalctl") else None
        out["uu_active"] = _done(subprocess.run(["systemctl", "is-active", "unattended-upgrades.service"], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, universal_newlines=True, timeout=30)) if shutil.which(
            "systemctl") else None
        out["dnf_auto_timer"] = _done(subprocess.run(["systemctl", "is-enabled", "dnf-automatic.timer"], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, universal_newlines=True, timeout=30)) if shutil.which(
            "systemctl") else None
        out["git_version"] = _done(subprocess.run(["git", "version"], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, universal_newlines=True, timeout=30)) if shutil.which(
            "git") else None
    except (OSError, subprocess.TimeoutExpired) as exc:
        out["error"] = type(exc).__name__
    return out


def ntp_status():
    """timedatectl's NTPSynchronized property (read-only): True, False, or None if unknown"""
    if not shutil.which("timedatectl"):
        return None
    try:
        p = subprocess.run(["timedatectl", "show", "-p", "NTPSynchronized", "--value"], stdin=subprocess.DEVNULL,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return {"yes": True, "no": False}.get(p.stdout.strip()) if p.returncode == 0 else None


_GIT_ENV = {"LC_ALL": "C", "GIT_PAGER": "cat", "GIT_TERMINAL_PROMPT": "0", "GIT_OPTIONAL_LOCKS": "0",
            "GIT_CONFIG_NOSYSTEM": "1", "PATH": "/usr/bin:/bin"}


def git_read(repo, *args):
    """git -C <repo> <args> for the P309 repository only (a registered git runner: every caller's verb is classified;
    the callers use only read-only queries).  Returns stdout, or None on failure."""
    try:
        p = subprocess.run(["git", "-C", repo, *args], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, universal_newlines=True, timeout=60, env=dict(_GIT_ENV))
    except (OSError, subprocess.TimeoutExpired):
        return None
    return p.stdout.strip() if p.returncode == 0 else None


# ----------------------------------------------------------------------------------------------- cloud metadata
def imds():
    """AWS IMDSv2, read-only, link-local only, 1 s timeouts.  The instance id is returned only as sha256."""
    base = "http://169.254.169.254/latest/"
    direct = urllib.request.build_opener(urllib.request.ProxyHandler({}))   # never through a proxy
    try:
        req = urllib.request.Request(base + "api/token", method="PUT",
                                     headers={"X-aws-ec2-metadata-token-ttl-seconds": "60"})
        tok = direct.open(req, timeout=1).read().decode()
    except Exception as exc:  # noqa: BLE001  (any failure means "no IMDS")
        return {"available": False, "error": type(exc).__name__}

    def get(path):
        r = urllib.request.Request(base + "meta-data/" + path, headers={"X-aws-ec2-metadata-token": tok})
        try:
            return direct.open(r, timeout=1).read().decode()
        except Exception:  # noqa: BLE001
            return None
    iid = get("instance-id")
    return {"available": True, "instance_id_sha256": sha(iid) if iid else None, "instance_type": get("instance-type"),
            "instance_life_cycle": get("instance-life-cycle"),
            "scheduled_maintenance": get("events/maintenance/scheduled"),
            "spot_instance_action": get("spot/instance-action")}


# ------------------------------------------------------------------------------------------------- provenance
def _clocks():
    """(CLOCK_BOOTTIME, CLOCK_MONOTONIC) in seconds, or (None, None) where unavailable"""
    try:
        return time.clock_gettime(time.CLOCK_BOOTTIME), time.clock_gettime(time.CLOCK_MONOTONIC)
    except (AttributeError, OSError):
        return None, None


def provenance(cfg, with_imds=True):
    boottime, mono = _clocks()
    mid = (read("/etc/machine-id") or "").strip()
    try:
        glibc = os.confstr("CS_GNU_LIBC_VERSION")
    except (AttributeError, ValueError, OSError):
        glibc = None
    doc = {"utc": utc(), "boot_id": (read("/proc/sys/kernel/random/boot_id") or "").strip() or None,
           "machine_id_sha256": sha(mid) if mid else None, "hostname_sha256": sha(socket.gethostname()),
           "etc_hostname_sha256": sha((read("/etc/hostname") or "").strip()) if read("/etc/hostname") else None,
           "kernel": platform.release(), "arch": platform.machine(), "glibc": glibc,
           "python": {"version": platform.python_version(), "implementation": platform.python_implementation(),
                      "executable": real(sys.executable), "executable_sha256": file_sha256(real(sys.executable))},
           "suspended_s": round(boottime - mono, 3) if boottime is not None and mono is not None else None,
           "ntp_synchronized": ntp_status()}
    if with_imds:
        doc["cloud"] = imds()
    return doc


def continuity(base, now, cfg):
    """Q-HOST (P10): the run is still on the host it started on, with no reboot, suspend or runtime change."""
    tol = float(cfg["suspend_tolerance_s"])
    bc, nc = base.get("cloud") or {}, now.get("cloud") or {}
    checks = {
        "same_boot": bool(base.get("boot_id")) and base.get("boot_id") == now.get("boot_id"),
        "same_machine_id": bool(base.get("machine_id_sha256")) and base.get("machine_id_sha256") == now.get(
            "machine_id_sha256"),
        "same_hostname": base.get("hostname_sha256") == now.get("hostname_sha256"),
        "same_instance": bc.get("instance_id_sha256") == nc.get("instance_id_sha256") or (
            not (bc.get("instance_id_sha256") and nc.get("instance_id_sha256")) and bool(base.get("boot_id"))
            and base.get("boot_id") == now.get("boot_id")
            and base.get("machine_id_sha256") == now.get("machine_id_sha256")
            and base.get("hostname_sha256") == now.get("hostname_sha256")),
        "same_interpreter": base.get("python") == now.get("python"),
        "same_glibc": base.get("glibc") == now.get("glibc"),
        "no_suspend": base.get("suspended_s") is not None and now.get("suspended_s") is not None
        and now["suspended_s"] - base["suspended_s"] <= tol,
    }
    return {"checks": checks, "pass": all(checks.values()),
            "instance_unverified": not (bc.get("instance_id_sha256") and nc.get("instance_id_sha256"))}


# ------------------------------------------------------------------------------------------------- processes
def proc_access():
    """P9: refuse when /proc is unreadable, mounted with hidepid, or shows no process of another user."""
    try:
        pids = [p for p in os.listdir("/proc") if p.isdigit()]
    except OSError:
        return {"readable": False, "hidepid": None, "foreign_visible": 0}
    hidepid = None
    for line in (read("/proc/self/mountinfo") or "").splitlines():
        parts = line.split(" - ")
        if len(parts) == 2 and line.split()[4] == "/proc":
            hidepid = bool(re.search(r"hidepid=(?!0\b|off\b)", parts[1]))
    me = os.getuid()
    foreign = 0
    for p in pids:
        try:
            if os.stat("/proc/" + p).st_uid != me:
                foreign += 1
        except OSError:
            continue
    return {"readable": bool(pids), "hidepid": hidepid, "foreign_visible": foreign}


def _own_tree():
    pids, pid = set(), os.getpid()
    while pid and pid not in pids:
        pids.add(pid)
        st = (read("/proc/%d/stat" % pid) or "").rsplit(")", 1)[-1].split()
        pid = int(st[1]) if len(st) > 1 else 0
    return pids


def _snapshot():
    hz = os.sysconf("SC_CLK_TCK")
    out = {}
    for p in os.listdir("/proc"):
        if not p.isdigit():
            continue
        st = (read("/proc/%s/stat" % p) or "").rsplit(")", 1)[-1].split()
        if len(st) < 13:
            continue
        try:
            uid = os.stat("/proc/" + p).st_uid
        except OSError:
            continue
        cmd = (read("/proc/%s/cmdline" % p) or "").replace("\0", " ").strip()
        try:
            cwd, cwd_ok = os.readlink("/proc/%s/cwd" % p), True
        except OSError:
            cwd, cwd_ok = "", False
        out[int(p)] = {"cpu_s": (int(st[11]) + int(st[12])) / hz, "uid": uid, "cmd": cmd, "cwd": cwd, "cwd_ok": cwd_ok,
                       "cgroup": (read("/proc/%s/cgroup" % p) or "").strip()}
    return out


def classify(rec, cfg, own_uid=None):
    """foreign (the cell-308 campaign: a configured uid, a pattern, or a cwd under a foreign root), p309, other
    ReBaseGuard, or -- review C2 -- unattributable: another non-root user's process whose cwd this user cannot read.
    Under the separate P309 user (P12) that is how a cell-308 process without a matching command line looks; it is
    never silently dropped."""
    if not rec["cmd"]:                     # a kernel thread or a zombie: no user work
        return None
    text = rec["cmd"] + " " + rec["cwd"]
    if rec["uid"] in (cfg.get("foreign_uids") or []):
        return "foreign"
    if any(re.search(p, text, re.I) for p in cfg["foreign_patterns"]) or under(rec["cwd"], cfg["foreign_roots"]):
        return "foreign"
    if under(rec["cwd"], cfg["p309_roots"]) or re.search(r"p309", rec["cmd"]):
        return "p309"
    if re.search(r"rebaseguard|closure_proofs", text, re.I):
        return "other-rebaseguard"
    if not rec.get("cwd_ok", True) and rec["uid"] not in (0, own_uid if own_uid is not None else os.getuid()):
        return "unattributable"
    return None


def processes(cfg, sample_s):
    """Sample /proc twice; return tagged rows (pid, uid, tag, cpu_fraction, cmd_sha256, heavy flags) and nothing else."""
    mine, own_cg = _own_tree(), (read("/proc/self/cgroup") or "").strip()
    s0 = _snapshot()
    if sample_s:
        time.sleep(sample_s)
    s1 = _snapshot()
    rows = []
    for pid, r in sorted(s1.items()):
        if pid in mine or (own_cg and r["cgroup"] == own_cg and own_cg.endswith(".service")):
            continue
        tag = classify(r, cfg, os.getuid())
        if not tag:
            continue
        frac = (r["cpu_s"] - s0[pid]["cpu_s"]) / sample_s if sample_s and pid in s0 else None
        rows.append({"pid": pid, "uid": r["uid"], "tag": tag,
                     "cpu_fraction": None if frac is None else round(frac, 3), "cmd_sha256": sha(r["cmd"]),
                     "heavy_pattern": bool(any(re.search(p, r["cmd"], re.I) for p in cfg["foreign_heavy_patterns"])
                                           if tag in ("foreign", "unattributable") else HEAVY_P309.search(r["cmd"]))})
    return rows


# ---------------------------------------------------------------------------------------------- disk / memory
def mem_available_gb():
    for line in (read("/proc/meminfo") or "").splitlines():
        if line.startswith("MemAvailable:"):
            return int(line.split()[1]) / 1e6
    return 0.0


def free_gb(roots):
    out = {}
    for r in roots:
        try:
            out[r] = round(shutil.disk_usage(r).free / 1e9, 1)
        except OSError:
            out[r] = None
    return out


# ----------------------------------------------------------------------------------------------- the gate
def gate_checks(acc, rows, loads, mem_gb, disk, cfg, own_uid=None):
    """the exclusion gate's decision, from observations only (pure; tested in tests/test_p309_host.py).  At the start a
    foreign (cell-308) or unattributable process is active if it uses more than heavy_cpu_fraction, matches a heavy
    pattern, or appeared during the sample (no CPU fraction yet): the strict reading of "no cell-308 worker or process
    is active".  The cell-308 campaign's uids must be configured, and must not include this user (review C2, P12)."""
    heavy = float(cfg["heavy_cpu_fraction"])
    l1, l5 = loads
    lim = float(cfg["load_baseline"]) + float(cfg["load_margin"])
    uids = cfg.get("foreign_uids") or []
    return {
        "foreign_uids_configured": bool(uids) and (own_uid if own_uid is not None else os.getuid()) not in uids,
        "proc_readable": acc["readable"],
        "proc_not_hidepid": acc["hidepid"] is False,
        "foreign_processes_visible": acc["foreign_visible"] > 0,
        "no_foreign_campaign_process_active": not [r for r in rows if r["tag"] in ("foreign", "unattributable") and (
            r["cpu_fraction"] is None or r["cpu_fraction"] > heavy or r["heavy_pattern"])],
        "no_other_rebaseguard_heavy_process": not [r for r in rows if r["tag"] == "other-rebaseguard" and (
            r["cpu_fraction"] or 0) > heavy],
        "no_stale_p309_worker": not [r for r in rows if r["tag"] == "p309" and r["heavy_pattern"]],
        "load_at_baseline": l1 <= lim and l5 <= lim,
        "ram_available": mem_gb >= float(cfg["ram_floor_gb"]),
        "disk_available": bool(disk) and all(v is not None and v >= float(cfg["disk_floor_gb"]) for v in disk.values()),
    }


def exclusion_gate(cfg):
    """Owner message 3, item 4: refuse heavy compute unless the shared host is free of the cell-308 campaign's work
    and of stale work."""
    acc = proc_access()
    sample = float(cfg["sample_s"])
    rows = processes(cfg, sample) if acc["readable"] else []
    l1, l5, _ = os.getloadavg()
    lim = float(cfg["load_baseline"]) + float(cfg["load_margin"])
    disk = free_gb(cfg["p309_roots"])
    checks = gate_checks(acc, rows, (l1, l5), mem_available_gb(), disk, cfg)
    counts = {}
    for r in rows:
        counts[r["tag"]] = counts.get(r["tag"], 0) + 1
    return {"schema": SCHEMA, "kind": "exclusion_gate", "utc": utc(), "sample_s": sample, "proc": acc,
            "boot_id": (read("/proc/sys/kernel/random/boot_id") or "").strip(), "loadavg": [round(l1, 2), round(l5, 2)],
            "load_limit": lim, "mem_available_gb": round(mem_available_gb(), 1), "disk_free_gb": disk,
            "counts_by_tag": counts, "processes": rows[:80], "checks": checks, "pass": all(checks.values())}


# ------------------------------------------------------------------------------------------------ isolation
def foreign_stat(root):
    """The top directory only: mode, owner and group as one sha256, and whether this user could read it."""
    try:
        st = os.stat(root)
    except OSError as exc:
        return {"exists": False, "error": type(exc).__name__}
    return {"exists": True, "meta_sha256": sha("%o:%d:%d" % (st.st_mode, st.st_uid, st.st_gid)),
            "world_readable": bool(st.st_mode & 0o004) and bool(st.st_mode & 0o001),
            "readable_by_this_user": os.access(root, os.R_OK | os.X_OK)}


def isolation(cfg):
    repo, roots, foreign = cfg["p309_repo"], cfg["p309_roots"] or [cfg["p309_repo"]], cfg["foreign_roots"]
    if not repo or any(overlaps(r, f) for r in roots + [repo] for f in foreign):     # before any git call (A16)
        return {"schema": SCHEMA, "kind": "isolation", "utc": utc(), "refused": "the P309 repository or a P309 root "
                "overlaps a foreign root (no git was run)", "checks": {"p309_roots_disjoint_from_foreign_roots": False},
                "pass": False}
    common = git_read(repo, "rev-parse", "--path-format=absolute", "--git-common-dir") or ""
    alt = read(os.path.join(common, "objects", "info", "alternates"), "") if common else ""
    refs = (git_read(repo, "for-each-ref", "--format=%(objectname) %(refname)") or "").splitlines()
    conf = (git_read(repo, "config", "--list", "--show-scope") or "").splitlines()
    fstat = {sha(f): foreign_stat(f) for f in foreign}
    checks = {
        "p309_repo_is_toplevel": real(git_read(repo, "rev-parse", "--show-toplevel") or "/nonexistent") == real(repo),
        "p309_roots_disjoint_from_foreign_roots": not any(overlaps(r, f) for r in roots + [repo] for f in foreign),
        "p309_git_dir_inside_p309_repo": bool(common) and real(common).startswith(real(repo) + os.sep),
        "p309_no_alternates": not alt.strip(),
        "p309_has_no_foreign_campaign_ref": not [r for r in refs if re.search(r"cell[_-]?308", r, re.I)],
        "p309_on_r2_branch": git_read(repo, "symbolic-ref", "-q", "HEAD") == cfg["branch"],
        "p309_config_has_no_credential": not [c for c in conf if re.search(
            r"(credential\.|\.extraheader|//[^/\s]*:[^/\s]*@)", c, re.I)],
        "foreign_roots_unreadable": all(v.get("exists") and not v.get("readable_by_this_user") for v in fstat.values()),
    }
    return {"schema": SCHEMA, "kind": "isolation", "utc": utc(), "foreign_roots": fstat,
            "p309": {"head": git_read(repo, "rev-parse", "HEAD"), "refs_sha256": sha("\n".join(refs))},
            "checks": checks, "pass": all(checks.values())}


# ---------------------------------------------------------------------------------------- P309_SCRATCH_ROOT (P7)
def scratch_root(env, repo, cfg):
    """Return the validated P309_SCRATCH_ROOT, or raise HostError (never fall back)."""
    s = env.get("P309_SCRATCH_ROOT")
    if not s or not os.path.isabs(s):
        raise HostError("P309_SCRATCH_ROOT is unset or not absolute")
    if real(s) != s:
        raise HostError("P309_SCRATCH_ROOT is not a resolved path")
    if not os.path.isdir(s):
        raise HostError("P309_SCRATCH_ROOT is not an existing directory")
    if repo and overlaps(s, repo):
        raise HostError("P309_SCRATCH_ROOT overlaps the repository")
    foreign = list(cfg.get("foreign_roots") or [])
    if "P309_FOREIGN_ROOTS" in env:                  # set-but-empty is refused, as in the verifier's sandbox helper
        listed = env["P309_FOREIGN_ROOTS"].split(os.pathsep)
        if not all(listed) or not all(os.path.isabs(f) for f in listed):
            raise HostError("P309_FOREIGN_ROOTS is empty or holds a relative path")
        foreign += listed
    if any(overlaps(s, f) for f in foreign):
        raise HostError("P309_SCRATCH_ROOT overlaps a foreign root")
    if cfg.get("require_empty_scratch") and os.listdir(s):
        raise HostError("P309_SCRATCH_ROOT is not empty")
    return s


# ------------------------------------------------------------------------------------------ durability preflight
def _auto_update():
    apt = {}
    d = "/etc/apt/apt.conf.d"
    for name in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        txt = read(os.path.join(d, name)) or ""
        for key in ("Unattended-Upgrade::Automatic-Reboot", "APT::Periodic::Unattended-Upgrade"):
            for m in re.finditer(re.escape(key) + r'\s+"([^"]*)"', txt):
                apt["%s:%s" % (name, key)] = m.group(1)
    nr = read("/etc/needrestart/needrestart.conf") or ""
    sr = system_reads()
    uu, dnf = sr.get("uu_active"), sr.get("dnf_auto_timer")
    return {"apt": apt,
            "automatic_reboot": any(k.endswith("Automatic-Reboot") and v.lower() in ("true", "1") for k, v in apt.items()),
            "unattended_upgrades_active": bool(uu and uu.get("out") == "active"),
            "dnf_automatic_enabled": bool(dnf and dnf.get("out") == "enabled"),
            "needrestart_mode": (re.findall(r"^\s*\$nrconf\{restart\}\s*=\s*'(\w)'", nr, re.M) or [None])[-1],
            "reboot_required": os.path.exists("/var/run/reboot-required")}


def _container():
    c = system_reads().get("container")
    return {"systemd_detect_virt_container": (c or {}).get("out") if c else None,
            "in_container": bool(os.path.exists("/.dockerenv") or os.path.exists("/run/.containerenv")
                                 or (read("/run/systemd/container") or "").strip() or (c and c.get("rc") == 0))}


def durability_preflight(cfg, env=None, repo=None):
    """Owner message 1, section 5.B and P15: fail closed unless the host can carry a ~6 h single attempt durably."""
    prov = provenance(cfg)
    au, ct, cloud = _auto_update(), _container(), prov.get("cloud") or {}
    itype = cloud.get("instance_type") or ""
    try:
        scratch = scratch_root(env if env is not None else dict(os.environ), repo or cfg["p309_repo"], cfg)
        scratch_ok = True
    except HostError as exc:
        scratch, scratch_ok = str(exc), False
    checks = {
        "pid1_is_systemd": (read("/proc/1/comm") or "").strip() == "systemd",
        "not_in_container": not ct["in_container"],
        "systemd_run_available": bool(shutil.which("systemd-run")),
        "no_automatic_reboot": not au["automatic_reboot"] and au["needrestart_mode"] != "a",
        "upgrades_held": not au["unattended_upgrades_active"] and not au["dnf_automatic_enabled"],
        "no_pending_reboot": not au["reboot_required"],
        "cloud_metadata_available": bool(cloud.get("available")),
        "no_scheduled_maintenance": cloud.get("scheduled_maintenance") in ("[]", "", None) and bool(
            cloud.get("available")),
        "not_spot": cloud.get("instance_life_cycle") not in ("spot",) and bool(cloud.get("available")),
        "not_burstable": bool(itype) and not BURSTABLE.match(itype),
        "enough_cpus": len(os.sched_getaffinity(0)) >= int(cfg["min_cpus"]),
        "ram_available": mem_available_gb() >= float(cfg["ram_floor_gb"]),
        "disk_available": all(v is not None and v >= float(cfg["disk_floor_gb"])
                              for v in free_gb(cfg["p309_roots"]).values()) and bool(cfg["p309_roots"]),
        "python_exact": prov["python"]["version"] == cfg["python_version"],
        "interpreter_pinned": bool(cfg["interpreter"]) and prov["python"]["executable"] == real(cfg["interpreter"]),
        "glibc_pinned": bool(cfg["glibc"]) and prov["glibc"] == cfg["glibc"],
        "ntp_synchronized": prov["ntp_synchronized"] is True,
        "machine_id_present": bool(prov["machine_id_sha256"]),
        "hostname_static": prov["etc_hostname_sha256"] == prov["hostname_sha256"],
        "scratch_root_valid": scratch_ok,
    }
    return {"schema": SCHEMA, "kind": "durability_preflight", "utc": utc(), "provenance": prov, "auto_update": au,
            "container": ct, "scratch_root": scratch, "checks": checks, "pass": all(checks.values())}


# ----------------------------------------------------------------------------------------------------- audit
def audit(cfg):
    """Gate step 8a (F8): everything an operator needs for the HOST verdict, read-only, identities hashed."""
    info = read("/proc/cpuinfo") or ""
    flags = re.search(r"^flags\s*:\s*(.+)$", info, re.M)
    rows = processes(cfg, 5.0) if proc_access()["readable"] else []
    sr = system_reads()
    boots, klog = sr.get("boots"), sr.get("kernel_log")
    osr = dict(re.findall(r'^(PRETTY_NAME|VERSION_ID|ID)="?([^"\n]*)"?$', read("/etc/os-release") or "", re.M))
    counts = {}
    for r in rows:
        counts[r["tag"]] = counts.get(r["tag"], 0) + 1
    return {"schema": SCHEMA, "kind": "audit", "utc": utc(), "read_only": True,
            "provenance": provenance(cfg), "os": osr, "pid1": (read("/proc/1/comm") or "").strip(),
            "cpu": {"models": sorted(set(re.findall(r"^model name\s*:\s*(.+)$", info, re.M))),
                    "logical_cpus": os.cpu_count(), "affinity_cpus": len(os.sched_getaffinity(0)),
                    "hypervisor_flag": bool(flags and " hypervisor" in " " + flags.group(1)),
                    "loadavg": [round(x, 2) for x in os.getloadavg()]},
            "mem_available_gb": round(mem_available_gb(), 1),
            "mem_total_gb": round(int((re.search(r"^MemTotal:\s+(\d+)", read("/proc/meminfo") or "MemTotal: 0",
                                                 re.M)).group(1)) / 1e6, 1),
            "disk_free_gb": free_gb(cfg["p309_roots"] or [os.path.expanduser("~")]),
            "boots": {"uptime_h": round(float((read("/proc/uptime") or "0").split()[0]) / 3600, 2),
                      "journal_boot_count": len(boots["out"].splitlines()) if boots and boots.get("rc") == 0 else None},
            "oom_events_30d": len([l for l in (klog or {}).get("out", "").splitlines()
                                   if re.search(r"out of memory|oom-kill|killed process", l, re.I)])
            if klog and klog.get("rc") == 0 else None,
            "auto_update": _auto_update(), "container": _container(),
            "virt": (sr.get("virt") or {}).get("out"),
            "tools": {"git": (sr.get("git_version") or {}).get("out"),
                      "systemd_run": bool(shutil.which("systemd-run")), "python3_11": bool(shutil.which("python3.11"))},
            "proc": proc_access(), "rebaseguard_processes": {"counts_by_tag": counts, "rows": rows[:80]},
            "foreign_roots": {sha(f): foreign_stat(f) for f in cfg["foreign_roots"]}}


# --------------------------------------------------------------------------------------------- Q-HOST monitor
def monitor_verdict(cont, rows, cfg):
    """one Q-HOST sample's decision (pure; tested in tests/test_p309_host.py): continuity holds, and no foreign
    (cell-308) or unattributable process, nor other ReBaseGuard process outside this unit, does heavy work -- a
    heavy-job pattern, or a CPU fraction above monitor_heavy_cpu_fraction -- and the foreign and unattributable
    processes together use at most monitor_aggregate_cpu_fraction of a core (A8).  A process first seen in this sample
    (no CPU fraction yet) is judged at the next sample.  Returns (ok, foreign pids, other pids)."""
    heavy, agg = float(cfg["monitor_heavy_cpu_fraction"]), float(cfg["monitor_aggregate_cpu_fraction"])
    fr = [r for r in rows if r["tag"] in ("foreign", "unattributable")]
    busy = [r["pid"] for r in fr if (r["cpu_fraction"] or 0) > heavy or r["heavy_pattern"]]
    if sum(r["cpu_fraction"] or 0 for r in fr) > agg:
        busy = sorted(set(busy) | {r["pid"] for r in fr if (r["cpu_fraction"] or 0) > 0})
    other = [r["pid"] for r in rows if r["tag"] == "other-rebaseguard" and (r["cpu_fraction"] or 0) > heavy]
    return cont["pass"] and not busy and not other, busy, other


def monitor_liveness(times, started, stopped, alive_at_stop, interval, tol):
    """Q-HOST liveness (pure; review C4): the monitor was alive when the runner stopped it, wrote at least one sample,
    and no gap between the start, the samples and the stop exceeds the interval plus the tolerance."""
    pts = [float(started)] + [float(t) for t in times] + [float(stopped)]
    gaps = [b - a for a, b in zip(pts, pts[1:])]
    limit = float(interval) + float(tol)
    checks = {"alive_at_stop": bool(alive_at_stop), "samples_present": bool(times),
              "samples_in_order": all(g >= 0 for g in gaps), "no_gap_over_limit": all(g <= limit for g in gaps)}
    return {"checks": checks, "max_gap_s": round(max(gaps), 1) if gaps else None, "limit_s": limit,
            "pass": all(checks.values())}


def qhost_monitor(cfg, baseline, parent, interval):
    """Q-HOST (P10): sample every <= `interval` s (at most 60) until the parent exits.  Each sample is one JSON row on
    standard output (the runner points it into the attempt): continuity against the baseline, and whether the
    cell-308 campaign or
    other ReBaseGuard heavy work is active (excluding this unit's own cgroup).  On a failed sample it signals the parent
    (SIGTERM) once and stops; the parent stops its own process tree (kill_own_descendants), records Q-HOST FAIL and
    exits, and the unit's KillMode=control-group with KillSignal=SIGKILL stops anything left.  It writes nothing else
    and signals no process but its own parent."""
    import signal as _signal
    interval = min(float(interval), 60.0)
    while True:
        if os.getppid() != parent:
            return 0
        t0 = time.time()
        now = provenance(cfg)
        cont = continuity(baseline, now, cfg)
        rows = processes(cfg, min(20.0, interval / 2))
        ok, busy, other = monitor_verdict(cont, rows, cfg)
        sys.stdout.write(json.dumps({"utc": utc(), "t": round(time.time(), 3), "pass": ok, "continuity": cont["checks"], "instance_unverified": cont["instance_unverified"], "foreign_active_pids":
                                     busy, "other_heavy_pids": other, "suspended_s": now.get("suspended_s"),
                                     "ntp_synchronized": now.get("ntp_synchronized")}, sort_keys=True) + "\n")
        sys.stdout.flush()
        if not ok:
            os.kill(parent, _signal.SIGTERM)
            return 1
        time.sleep(max(0.0, interval - (time.time() - t0)))


def _children_map():
    kids = {}
    for p in os.listdir("/proc"):
        if p.isdigit():
            st = (read("/proc/%s/stat" % p) or "").rsplit(")", 1)[-1].split()
            if len(st) > 1:
                kids.setdefault(int(st[1]), []).append(int(p))
    return kids


def kill_own_descendants():
    """review C5: stop the calling process's own descendants at once, whatever signals they ignore.  First SIGSTOP the
    whole tree (repeated until no new descendant appears, so none can fork away), then SIGKILL every stopped pid.
    It never signals the caller itself or any process outside its tree.  Returns the pids signalled."""
    import signal as _signal
    me, seen = os.getpid(), []
    for _ in range(20):
        kids, stack, new = _children_map(), [os.getpid()], []
        while stack:
            for c in kids.get(stack.pop(), []):
                if c != me and c not in seen and c not in new:
                    new.append(c)
                    stack.append(c)
        for c in new:
            try:
                os.kill(c, _signal.SIGSTOP)
            except OSError:
                pass
        seen += new
        if not new:
            break
    for c in seen:
        try:
            os.kill(c, _signal.SIGKILL)
        except OSError:
            pass
    return seen


UNIT_RE = re.compile(r"/(p309-r2-(?:drill|qualify|hostrerun)-\d{8}T\d{6}Z)\.service$")
UNIT_PROPS = ("Id", "User", "Group", "Restart", "KillMode", "KillSignal", "SendSIGKILL", "TimeoutStopUSec", "MemoryMax",
              "OOMScoreAdjust", "CPUWeight", "IOWeight", "ProtectSystem", "PrivateTmp", "NoNewPrivileges",
              "ReadWritePaths", "InaccessiblePaths", "WorkingDirectory", "Environment")


def unit_properties():
    """review C9: the effective properties of the P309 unit this process runs in (`systemctl show`, read-only), with
    every inaccessible path and the foreign-roots variable as sha256.  None outside such a unit."""
    unit = None
    for line in (read("/proc/self/cgroup") or "").splitlines():
        m = UNIT_RE.search(line.strip())
        if m:
            unit = m.group(1) + ".service"
    if not unit or not shutil.which("systemctl"):
        return None
    try:
        p = subprocess.run(["systemctl", "show", "--no-pager", "-p", ",".join(UNIT_PROPS), "--", unit],
                           stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           universal_newlines=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if p.returncode != 0:
        return None
    props = dict(l.split("=", 1) for l in p.stdout.splitlines() if "=" in l)
    if "InaccessiblePaths" in props:
        props["InaccessiblePaths"] = [sha(x.lstrip("-")) for x in props["InaccessiblePaths"].split()]
    if "Environment" in props:
        props["Environment"] = [("P309_FOREIGN_ROOTS=sha256:" + sha(x.split("=", 1)[1]))
                                if x.startswith("P309_FOREIGN_ROOTS=") else x for x in props["Environment"].split()]
    return props


# ------------------------------------------------------------------------------------------------------ CLI
def main(argv):
    if argv and argv[0] == "qhost-monitor":
        doc = json.loads(sys.stdin.read())
        cfg = load_config(["--config-json", json.dumps(doc["cfg"])])
        return qhost_monitor(cfg, doc["baseline"], int(argv[argv.index("--parent") + 1]),
                             float(argv[argv.index("--interval") + 1]))
    if not argv or argv[0] not in ("audit", "gate", "isolation", "provenance", "preflight", "scratch"):
        sys.stderr.write(__doc__)
        return 2
    try:
        cfg = load_config(argv)
        cmd = argv[0]
        if cmd == "audit":
            doc = audit(cfg)
        elif cmd == "gate":
            doc = exclusion_gate(cfg)
        elif cmd == "isolation":
            doc = isolation(cfg)
        elif cmd == "provenance":
            doc = provenance(cfg)
        elif cmd == "preflight":
            doc = durability_preflight(cfg)
        else:
            doc = {"scratch_root": scratch_root(dict(os.environ), cfg["p309_repo"], cfg), "pass": True}
    except HostError as exc:
        sys.stdout.write(json.dumps({"schema": SCHEMA, "refused": str(exc), "pass": False}) + "\n")
        return 1
    sys.stdout.write(json.dumps(doc, indent=1, sort_keys=True, default=str) + "\n")
    return 0 if doc.get("pass", True) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
