"""Read-only pre-launch check for the P309-r2 worker-tier drill (8d) on r2 501f48cb.  Part of the host-side packet
(WORKER_TIER_DRILL_8D.md section 2).  Not r2 code; it changes nothing on the host.

usage (as the P309 user, with the pinned interpreter, from anywhere outside the clone):
  <INTERP> -B prelaunch_readonly_check_8d.py --clone <CLONE> --host-config <HOST_CONFIG> --scratch <RUN_SCRATCH>
           --check-record <CHECK_DIR>/launch_<utc>.json --verdict <VERDICT_8B_final.json> --remote [--max-age-h 3]
(without --remote, C13 and C14 are false: origin must be checked)

What it reads, and nothing else:
  * git (with GIT_OPTIONAL_LOCKS=0, so `status` never writes the index) in <CLONE>: HEAD, tree, branch, status,
    common dir, alternates, configuration, local refs; with --remote, `git ls-remote origin` (network; for a private
    repository, set GIT_ASKPASS to the P309-only helper in this command's environment: it is passed to ls-remote only,
    and appears in no git configuration);
  * the working-tree bytes of the four reviewed r2 tools and the two ledgers;
  * the host configuration file, the A-02d check record and the 8b-final verdict record (JSON);
  * `systemctl list-units` (read-only), /proc, the IMDS (through r2's own p309_host.provenance, loaded from the clone
    without writing bytecode).
Output: one JSON document on standard output.  Exit 0 iff every check passes; 1 otherwise; 2 on a usage error.
"""
import datetime
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True

R2_COMMIT = "501f48cb31fd3f80d5c6dd33f1eef6b8f01b2853"
R2_TREE = "d7e2c8329b73d68ae07ca37192eb495674e572c9"
BRANCH_REF = "refs/heads/claude/p5y-k5-cell309-p309-r2"
NS = "level4/closure_proofs/p5y_k5_cell309_p309_r2"
P = "p309_"
TOOLS = {  # path in the namespace -> sha256 of the bytes at 501f48cb
    "code/" + P + "qualify.py": "540df0552bfc31512289e30eaf1ead57bf82a4ac806f38080439c05c43f9a3af",
    "code/" + P + "host.py": "ec9c8416159cf9e2e7372f97ce179a290def987007dc144591833615ca251f65",
    "code/" + P + "launch.py": "cd7e4ab920b3dae105f5a96d019a7c7f02b7563286ab64483438991fcf3485fb",
    "code/" + P + "topology_drill.py": "ef4ce1bf4a8dd7e9b0bfcb5947ccf1578e7797757daae29b22c6a6d5289ff0c1",
}
COMMITTED_DRILLS = ["20261001T132113Z", "20261001T132325Z", "20261001T143415Z", "20261001T160409Z",
                    "20261001T171235Z", "20261001T202159Z", "20261001T222108Z_INTERRUPTED", "20261001T224858Z",
                    "20261002T025624Z", "20261002T052554Z"]
# r2's exactly-once refs: every ref under refs/p5y-k5-cell309 (both production namespaces, markers, pending results)
PROTECTED_REF = re.compile(r"^refs/p5y-k5-cell309")
COUNTERS = ("new_target_evaluations", "target_equivalent_proxies", "target_informed_optimisation")
LAUNCH_KEYS = ("unit_user", "unit_group", "memory_max", "oom_score_adjust", "cpu_weight", "io_weight")
GIT_ENV = {"LC_ALL": "C", "GIT_PAGER": "cat", "GIT_TERMINAL_PROMPT": "0", "GIT_OPTIONAL_LOCKS": "0",
           "PATH": "/usr/bin:/bin", "HOME": os.environ.get("HOME", "/nonexistent")}


def arg(name, default=None):
    a = sys.argv[1:]
    return a[a.index(name) + 1] if name in a else default


def git(repo, *args, askpass=False):
    env = dict(GIT_ENV)
    if askpass and os.environ.get("GIT_ASKPASS"):   # the P309-only credential helper (F-2), for ls-remote only
        env["GIT_ASKPASS"] = os.environ["GIT_ASKPASS"]
    p = subprocess.run(["git", "-C", repo] + list(args), stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, universal_newlines=True, timeout=120, env=env)
    return p.stdout.strip() if p.returncode == 0 else None


def sha_file(path):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as fh:
            for b in iter(lambda: fh.read(1 << 20), b""):
                h.update(b)
    except OSError:
        return None
    return h.hexdigest()


def load_json(path):
    try:
        with open(path) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def ledger_problems(path):
    try:
        raw = open(path, "rb").read()
    except OSError as exc:
        return ["%s unreadable: %s" % (os.path.basename(path), type(exc).__name__)]
    bad = [] if not raw or raw.endswith(b"\n") else ["%s: last row has no newline" % os.path.basename(path)]
    for i, line in enumerate(raw.decode("utf-8", "replace").splitlines()):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except ValueError:
            bad.append("%s row %d does not parse" % (os.path.basename(path), i + 1))
            continue
        if any(row.get(k, 0) != 0 for k in COUNTERS):
            bad.append("%s row %d has a nonzero target counter" % (os.path.basename(path), i + 1))
    return bad


def main():
    clone, host_config, scratch = arg("--clone"), arg("--host-config"), arg("--scratch")
    check_record, verdict_path = arg("--check-record"), arg("--verdict")
    if not all((clone, host_config, scratch, check_record, verdict_path)):
        sys.stderr.write(__doc__)
        return 2
    max_age_h = float(arg("--max-age-h", "3"))
    clone = os.path.realpath(clone)
    ns = os.path.join(clone, NS)
    c, info = {}, {"tool_sha256": sha_file(os.path.abspath(__file__)), "utc": datetime.datetime.now(
        datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}

    # 1. the exact commit, tree, branch and a clean clone
    c["C01_head_is_501f48cb"] = git(clone, "rev-parse", "HEAD") == R2_COMMIT
    c["C02_tree_is_d7e2c832"] = git(clone, "rev-parse", "HEAD^{tree}") == R2_TREE
    c["C03_on_the_r2_branch"] = git(clone, "symbolic-ref", "-q", "HEAD") == BRANCH_REF
    st = git(clone, "status", "--porcelain", "--untracked-files=all")
    info["status"] = st
    c["C04_clone_clean_incl_untracked"] = st == ""
    common = git(clone, "rev-parse", "--path-format=absolute", "--git-common-dir") or ""
    c["C05_git_dir_inside_clone"] = bool(common) and os.path.realpath(common).startswith(clone + os.sep)
    try:
        alt = open(os.path.join(common, "objects", "info", "alternates")).read().strip() if common else ""
    except OSError:
        alt = ""
    c["C06_no_alternates"] = not alt
    conf = (git(clone, "config", "--list", "--show-scope") or "").splitlines()
    # the same rule as r2's isolation check (p309_config_has_no_credential), over every scope git lists
    c["C07_no_credential_in_config"] = not [x for x in conf if re.search(
        r"(credential\.|\.extraheader|//[^/\s]*:[^/\s]*@)", x, re.I)]
    for rel, want in TOOLS.items():
        c["C08_bytes_%s" % rel.split("/")[-1].replace(".py", "")] = sha_file(os.path.join(ns, rel)) == want
    # 2. no prior attempt or trace
    c["C09_no_qualification_dir"] = not os.path.exists(os.path.join(ns, "qualification"))
    try:
        drills = sorted(os.listdir(os.path.join(ns, "evidence", "drill")))
    except OSError:
        drills = None
    info["evidence_drill"] = drills
    c["C10_only_the_committed_drill_records"] = drills == COMMITTED_DRILLS
    led = []
    for name in ("ZERO_TARGET_LEDGER.jsonl", "EXPOSURE_LEDGER.jsonl"):
        led += ledger_problems(os.path.join(ns, "ledger", name))
    info["ledger_problems"] = led
    c["C11_ledgers_parse_newline_zero_counters"] = not led
    refs = (git(clone, "for-each-ref", "--format=%(refname)") or "").splitlines()
    c["C12_no_protected_ref_local"] = not [r for r in refs if PROTECTED_REF.search(r)]
    rem = git(clone, "ls-remote", "origin", askpass=True) if "--remote" in sys.argv else None   # fail closed without --remote
    info["ls_remote_ok"] = rem is not None
    rows = [l.split("\t") for l in (rem or "").splitlines() if "\t" in l]
    c["C13_origin_r2_is_501f48cb"] = any(r[1] == BRANCH_REF and r[0] == R2_COMMIT for r in rows)
    c["C14_no_protected_ref_on_origin"] = rem is not None and not [r for r in rows if PROTECTED_REF.search(r[1])]
    # 3. the run's scratch root and the host configuration
    try:
        raw = load_json(host_config) or {}
        launch = {k: raw.get(k) for k in LAUNCH_KEYS}
        cfg = {k: v for k, v in raw.items() if k not in LAUNCH_KEYS}
    except AttributeError:
        launch, cfg = {}, {}
    foreign = list(cfg.get("foreign_roots") or [])
    rs = os.path.realpath(scratch)

    def overlaps(a, b):
        a, b = os.path.realpath(a), os.path.realpath(b)
        return a == b or a.startswith(b + os.sep) or b.startswith(a + os.sep)
    c["C15_scratch_absolute_resolved_existing"] = os.path.isabs(scratch) and rs == scratch and os.path.isdir(scratch)
    c["C16_scratch_empty"] = os.path.isdir(scratch) and not os.listdir(scratch)
    c["C17_scratch_disjoint_from_clone_and_foreign_roots"] = not overlaps(scratch, clone) and not any(
        overlaps(scratch, f) for f in foreign)
    c["C18_scratch_under_a_p309_root"] = any(rs == os.path.realpath(r) or rs.startswith(os.path.realpath(r) + os.sep)
                                             for r in cfg.get("p309_roots") or [])
    c["C19_launch_keys_present"] = all(launch.get(k) is not None for k in LAUNCH_KEYS)
    uids = cfg.get("foreign_uids") or []
    c["C20_foreign_uids_set_and_not_mine"] = bool(uids) and os.getuid() not in uids
    c["C21_running_as_unit_user"] = launch.get("unit_user") is not None and __import__("pwd").getpwuid(
        os.getuid()).pw_name == launch.get("unit_user")
    c["C22_running_the_pinned_interpreter"] = bool(cfg.get("interpreter")) and os.path.realpath(
        sys.executable) == os.path.realpath(cfg["interpreter"])
    import platform
    c["C23_python_3_11_15_cpython"] = platform.python_version() == "3.11.15" and \
        platform.python_implementation() == "CPython" and cfg.get("python_version") in (None, "3.11.15")
    try:
        glibc = os.confstr("CS_GNU_LIBC_VERSION")
    except (ValueError, OSError):
        glibc = None
    c["C24_glibc_as_configured"] = bool(cfg.get("glibc")) and glibc == cfg.get("glibc")
    # 4. no P309 unit loaded
    try:
        p = subprocess.run(["systemctl", "list-units", "--all", "--no-legend", "--plain"], stdin=subprocess.DEVNULL,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=30)
        units = [l.split()[0] for l in p.stdout.splitlines() if l.split() and l.split()[0].startswith("p309-r2-")] \
            if p.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        units = None
    info["p309_units_loaded"] = units
    c["C25_no_p309_unit_loaded"] = units == []
    # 5. the window's A-02d check record and host identity
    rec = load_json(check_record) or {}
    c["C26_check_record_no_blockers_mode_drill"] = rec.get("schema") == "P309_R2_LAUNCH/2" and \
        rec.get("blockers") == [] and rec.get("mode") == "drill"
    try:
        t = datetime.datetime.strptime(rec.get("utc", ""), "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=datetime.timezone.utc)
        age_h = (datetime.datetime.now(datetime.timezone.utc) - t).total_seconds() / 3600
    except ValueError:
        age_h = None
    info["check_record_age_h"] = None if age_h is None else round(age_h, 2)
    c["C27_check_record_recent"] = age_h is not None and 0 <= age_h <= max_age_h
    c["C28_check_record_dir_is_not_the_run_scratch"] = not overlaps(os.path.dirname(os.path.realpath(
        check_record)), scratch)
    if c["C08_bytes_" + P + "host"]:            # only the reviewed bytes are ever loaded
        spec = importlib.util.spec_from_file_location("p309host_ro", os.path.join(ns, "code", P + "host.py"))
        H = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(H)
        now = H.provenance(H.load_config([]))
    else:
        now = {}
    ver = load_json(verdict_path) or {}
    keys = ("machine_id_sha256", "hostname_sha256")
    rp = ((rec.get("preflight") or {}).get("provenance") or {})
    c["C29_verdict_is_accepted_for_worker_tier"] = ver.get("verdict") == "HOST_ACCEPTED_FOR_WORKER_TIER" and \
        ver.get("point") == "final"
    c["C30_identity_equals_8b_final"] = all(now.get(k) and now.get(k) == (ver.get("host") or {}).get(k) for k in keys) \
        and (now.get("cloud") or {}).get("instance_id_sha256") == (ver.get("host") or {}).get("instance_id_sha256")
    c["C31_identity_equals_check_record"] = all(now.get(k) == rp.get(k) for k in keys) and \
        (now.get("cloud") or {}).get("instance_id_sha256") == (rp.get("cloud") or {}).get("instance_id_sha256")
    c["C32_same_boot_as_check_record"] = bool(now.get("boot_id")) and now.get("boot_id") == rp.get("boot_id")
    c["C33_same_interpreter_and_glibc_as_check_record"] = now.get("python") == rp.get("python") and \
        now.get("glibc") == rp.get("glibc")
    info["identity_now"] = {k: now.get(k) for k in keys + ("boot_id",)}
    out = {"schema": "P309_R2_8D_PRELAUNCH_CHECK/1", "r2_commit": R2_COMMIT, "checks": c, "info": info,
           "pass": all(c.values()), "statement": "read-only; nothing was written, started or signalled; "
                                                 "NEW Γ309 TARGET EVALUATIONS = 0"}
    sys.stdout.write(json.dumps(out, indent=1, sort_keys=True) + "\n")
    return 0 if out["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
