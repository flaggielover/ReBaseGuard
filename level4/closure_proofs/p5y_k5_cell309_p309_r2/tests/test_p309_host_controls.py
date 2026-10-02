"""r2 delta review C11 (with C2, C5 and C14): the P9-P11 controls as reproducible tests, on the real /proc and real
processes.

  python3 tests/test_p309_host_controls.py   -> evidence/host/HOST_CONTROLS.json; exit 0 iff every case passes

Every process it starts is a TEST process of its own, from a literal program, with its working directory in a TEST
directory under P309_SCRATCH_ROOT.  Each is SIGKILLed and reaped before its case ends.  Apart from those, the only
signal is the one the case S01 expects: the real Q-HOST monitor's SIGTERM to this process, its parent.

* P01 (P9) a TEST busy process, recognised by a TEST pattern and by its cwd under a TEST foreign root, is tagged
  foreign through the real /proc path; it blocks the gate's decision and the monitor's.  Inside a P309 unit (the
  worker-tier drill) the unit's own processes are excluded from sampling by design, so there the classification of
  its /proc record is checked instead.
* P02 (C2) cross-uid, root only (it needs setpriv): a TEST busy process under one TEST uid, cwd in a mode-700 TEST
  root, command line matching no pattern, observed by the gate run under another TEST uid.  It must be tagged
  unattributable and block the gate and the monitor; with its uid configured it is tagged foreign.  As the worker's
  P309 user (not root) the case is recorded as not applicable.
* Q01-Q06 (P10) the runner's Q-HOST refusals: no launch record; blockers; another mode; a record outside its scratch
  root; a drill record for a repository outside it; not inside the unit.  Each is refused by qhost_preflight, called
  in a child process with its own environment (this process's environment is never changed), and creates nothing in
  qualification/.
* N01-N06 (P11, A16; follow-up V2, V4, W3) the launcher's refusals: an unknown mode; missing launch settings; root as
  the unit user; --print-only blocked (no systemd here, or the drill's own unit loaded on the worker), with the record
  written under the TEST scratch root and redacted (C9: the TEST foreign root appears only as its sha256), and the
  launcher_not_unit_user blocker when the launcher's uid is not the unit user's; a foreign root with whitespace, or
  with "$", ";", ":" or "(" (only [A-Za-z0-9._/+@,=~-] is accepted).
* U01-U03 (follow-up W6; worker tier only) the in-unit refusals of qhost_preflight, reached from inside the launched
  unit with altered copies under the launch's scratch root: a host configuration file whose bytes differ (U01); a
  launch record whose configuration hash differs (U02); a launch record whose baseline names another boot (U03).  The
  unit-property and instance-id branches cannot be forced from inside a correct unit and are exercised nowhere.  On the
  cloud tier, where no unit exists, the case records "not applicable".
* S01 (P10) the monitor FAIL -> SIGTERM path: a real monitor whose baseline names another boot signals this process,
  its parent, exactly once, writes one failed row and exits 1.
* K01 (C5; follow-up FU2) kill_own_descendants: a TEST tree three deep plus two descendants that keep starting
  children during the call, every process ignoring SIGTERM, is dead at once; the caller survives, and a TEST process
  outside the caller's tree is untouched.
* A01 (C5; follow-up FU2 (b)) the runner's abort end to end, in a child process: the runner's own _qhost_abort is
  installed with the attempt pointed at a TEST directory and the host_rerun label (nothing is written in
  qualification/); a real monitor with a failing baseline signals it; the abort kills a SIGTERM-ignoring TEST tree
  that keeps starting children, writes QHOST_FAIL.json and the failed result, logs its own row, and exits 3.  A TEST
  process outside the child's tree is untouched.  The abort's row goes to the namespace ledger (a test may not
  redirect the guard's ledger: QC12 T7), so this control first logs a row saying that the next row comes from this
  TEST control and that no host re-run ran.
* B01-B03 (C14) the manifest generator's runtime equals the driver's runtime_identity; check_bindings accepts it and
  refuses another glibc or another interpreter binary.
"""
from __future__ import annotations

import datetime
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

FNS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FNS / "code"))
import p309_env as E  # noqa: E402
import p309_host as H  # noqa: E402

CODE = FNS / "code"
R = {}
BUSY = "import sys\nwhile True:\n    pass\n"                       # a TEST busy loop (no cell, no repository)
LEAF = "import signal, time\nsignal.signal(signal.SIGTERM, signal.SIG_IGN)\ntime.sleep(600)\n"
TREE = """
import json, os, signal, subprocess, sys, time
sys.path.insert(0, os.environ["P309_TEST_CODE"])
import p309_host as H
TOKEN = sys.argv[1]
signal.signal(signal.SIGTERM, signal.SIG_IGN)
LEAF = "import signal, time\\nsignal.signal(signal.SIGTERM, signal.SIG_IGN)\\ntime.sleep(600)\\n"
FORKER = '''
import signal, subprocess, sys, time
signal.signal(signal.SIGTERM, signal.SIG_IGN)
LEAF = "import signal, time\\\\nsignal.signal(signal.SIGTERM, signal.SIG_IGN)\\\\ntime.sleep(600)\\\\n"
for _ in range(40):
    subprocess.Popen([sys.executable, "-S", "-c", LEAF, sys.argv[1]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(0.005)
time.sleep(600)
'''
MID = '''
import signal, subprocess, sys, time
signal.signal(signal.SIGTERM, signal.SIG_IGN)
LEAF = "import signal, time\\\\nsignal.signal(signal.SIGTERM, signal.SIG_IGN)\\\\ntime.sleep(600)\\\\n"
c = subprocess.Popen([sys.executable, "-S", "-c", LEAF, sys.argv[1]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(c.pid, flush=True)
time.sleep(600)
'''
m = subprocess.Popen([sys.executable, "-S", "-c", MID, TOKEN], stdout=subprocess.PIPE, text=True)
leaf2 = subprocess.Popen([sys.executable, "-S", "-c", LEAF, TOKEN], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
forkers = [subprocess.Popen([sys.executable, "-S", "-c", FORKER, TOKEN], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) for _ in range(2)]
leaf1 = int(m.stdout.readline())
time.sleep(0.15)
killed = H.kill_own_descendants()
time.sleep(0.5)
def state(pid):
    st = H.read("/proc/%d/stat" % pid)
    return None if st is None else st.rsplit(")", 1)[-1].split()[0]
live = []
for p in os.listdir("/proc"):
    if p.isdigit() and int(p) != os.getpid() and TOKEN in (H.read("/proc/%s/cmdline" % p) or "").split(chr(0)):
        if state(int(p)) not in (None, "Z", "X"):
            live.append(int(p))
print("TREE_RESULT " + json.dumps({"killed": len(killed), "named_in_killed": all(x in killed for x in [m.pid, leaf1, leaf2.pid]
                                   + [f.pid for f in forkers]), "live_with_token": live,
                                   "caller_alive": state(os.getpid()) not in ("Z", "X")}))
"""
ABORT = """
import json, os, signal, subprocess, sys, time
from pathlib import Path
sys.path[:0] = [os.environ["P309_TEST_CODE"]]
import p309_qualify as QQ
T = Path(os.environ["P309_TEST_DIR"])
QQ.ATT["dir"], QQ.ATT["label"] = T / "attempt", "host_rerun"
QQ.ATT["dir"].mkdir()
QQ.QHOST["file"] = T / "QHOST_MONITOR.jsonl"
signal.signal(signal.SIGTERM, QQ._qhost_abort)
LEAF = "import signal, time\\nsignal.signal(signal.SIGTERM, signal.SIG_IGN)\\ntime.sleep(600)\\n"
FORKER = '''
import signal, subprocess, sys, time
signal.signal(signal.SIGTERM, signal.SIG_IGN)
LEAF = "import signal, time\\\\nsignal.signal(signal.SIGTERM, signal.SIG_IGN)\\\\ntime.sleep(600)\\\\n"
while True:                                   # follow-up W7: still forking when the abort comes
    subprocess.Popen([sys.executable, "-S", "-c", LEAF, sys.argv[1]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(0.05)
'''
forkers = [subprocess.Popen([sys.executable, "-S", "-c", FORKER, sys.argv[1]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) for _ in range(2)]
leaf = subprocess.Popen([sys.executable, "-S", "-c", LEAF, sys.argv[1]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
cfg = dict(QQ.H.load_config([]), foreign_uids=[4242])
base = dict(QQ.H.provenance(cfg, with_imds=False), boot_id="TEST-another-boot")
with open(str(QQ.QHOST["file"]), "w") as fh:
    mon = subprocess.Popen([sys.executable, "-B", os.environ["P309_TEST_CODE"] + "/p309_host.py", "qhost-monitor",
                            "--parent", str(os.getpid()), "--interval", "2"], stdin=subprocess.PIPE, stdout=fh,
                           stderr=subprocess.STDOUT, universal_newlines=True)
    mon.stdin.write(json.dumps({"cfg": cfg, "baseline": base}))
    mon.stdin.close()
time.sleep(120)
print("ABORT_NOT_REACHED")
sys.exit(9)
"""
Q_CODE = """
import json, os, sys
sys.path[:0] = [os.environ["P309_TEST_CODE"]]
import p309_qualify as QQ
try:
    QQ.qhost_preflight(("official", "drill"))
    print("Q_RESULT " + json.dumps({"refused": None}))
except QQ.H.HostError as exc:
    print("Q_RESULT " + json.dumps({"refused": str(exc)[:200]}))
"""


def t(name, ok, got=None):
    R[name] = {"pass": bool(ok), "got": got}
    print(f"[{'PASS' if ok else 'FAIL'}] {name}", flush=True)


def scratch(sub: str) -> Path:
    return E.scratch_dir("host_controls") / sub


def stop(p) -> None:
    """SIGKILL and reap one TEST child of this process"""
    if p.poll() is None:
        p.kill()
    p.wait(timeout=30)


def in_unit() -> bool:
    return (H.read("/proc/self/cgroup") or "").strip().endswith(".service")


# ------------------------------------------------------------------------------------------------ P01 (P9)
def case_p01() -> None:
    root = scratch("P01_TEST_foreign_root")
    root.mkdir(parents=True, exist_ok=True)
    cfg = dict(H.load_config([]), foreign_patterns=["TEST-foreign-busy-proc"], foreign_roots=[str(root)],
               foreign_uids=[4242])
    p = subprocess.Popen([sys.executable, "-c", BUSY, "TEST-foreign-busy-proc"], cwd=str(root),
                         stdin=subprocess.DEVNULL)
    try:
        time.sleep(0.5)
        snap = H._snapshot().get(p.pid)
        t("P01a_snapshot_classifies_foreign", snap is not None and H.classify(snap, cfg) == "foreign")
        if in_unit():
            t("P01b_own_unit_excluded_by_design", not [r for r in H.processes(cfg, 1.0) if r["pid"] == p.pid])
            return
        rows = [r for r in H.processes(cfg, 3.0) if r["pid"] == p.pid]
        busy = rows[0] if rows else {}
        t("P01b_real_proc_row_foreign_and_busy", busy.get("tag") == "foreign" and (busy.get("cpu_fraction") or 0) > 0.5,
          busy)
        acc = {"readable": True, "hidepid": False, "foreign_visible": 1}
        g = H.gate_checks(acc, rows, (0.0, 0.0), 64.0, {"/x": 999.0}, cfg, 0)
        t("P01c_gate_blocks", not g["no_foreign_campaign_process_active"])
        t("P01d_monitor_blocks", not H.monitor_verdict({"pass": True}, rows, cfg)[0])
    finally:
        stop(p)


# --------------------------------------------------------------------------------------------- P02 (C2)
def case_p02() -> None:
    if os.getuid() != 0 or not H.shutil.which("setpriv"):
        t("P02_cross_uid_not_applicable_without_root", True, {"uid": os.getuid()})
        return
    busy_uid, observer_uid = 64011, 64012
    root = scratch("P02_TEST_foreign_root")
    root.mkdir(parents=True, exist_ok=True)
    os.chown(str(root), busy_uid, busy_uid)
    os.chmod(str(root), 0o700)
    p = subprocess.Popen(["setpriv", "--reuid", "64011", "--regid", "64011", "--clear-groups", "--",
                          sys.executable, "-c", BUSY, "TEST-cross-uid-busy"], cwd=str(root), stdin=subprocess.DEVNULL)
    try:
        time.sleep(1.0)
        res = {}
        for label, uids in (("unconfigured", [4242]), ("configured", [busy_uid])):
            cfg = {"foreign_patterns": ["TEST-pattern-that-matches-nothing"], "foreign_uids": uids, "sample_s": 3.0}
            with open(str(CODE / "p309_host.py"), "rb") as src:
                o = subprocess.run(["setpriv", "--reuid", "64012", "--regid", "64012", "--clear-groups", "--",
                                    sys.executable, "-I", "-S", "-B", "-", "gate", "--config-json", json.dumps(cfg)],
                                   stdin=src, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd="/",
                                   universal_newlines=True, timeout=120)
            doc = json.loads(o.stdout)
            rows = [r for r in doc.get("processes", []) if r["pid"] == p.pid]
            res[label] = {"row": rows[0] if rows else None, "gate_blocks": not doc["checks"][
                "no_foreign_campaign_process_active"], "monitor_blocks": not H.monitor_verdict(
                {"pass": True}, rows, dict(H.load_config([]), **cfg))[0], "observer_uid": observer_uid}
        u, c = res["unconfigured"], res["configured"]
        t("P02a_unattributable_when_uid_not_configured", (u["row"] or {}).get("tag") == "unattributable", u)
        t("P02b_gate_blocks_unattributable", u["gate_blocks"])
        t("P02c_monitor_blocks_unattributable", u["monitor_blocks"])
        t("P02d_foreign_when_uid_configured", (c["row"] or {}).get("tag") == "foreign" and c["gate_blocks"]
          and c["monitor_blocks"], c)
    finally:
        stop(p)


# --------------------------------------------------------------------------------------------- Q (P10)
def case_q() -> None:
    qdir = FNS / "qualification"
    sr = Path(os.environ["P309_SCRATCH_ROOT"])
    d = scratch("Q_records")
    d.mkdir(parents=True, exist_ok=True)
    good = {"schema": "P309_R2_LAUNCH/2", "mode": "official", "unit": "p309-r2-qualify-20261001T000000Z",
            "blockers": [], "scratch_root": str(sr), "host_config": {}, "preflight": {"provenance": {}}}
    cases = {"Q01_no_launch_record": None,
             "Q02_blockers_refused": dict(good, blockers=["gate"]),
             "Q03_other_mode_refused": dict(good, mode="host-rerun"),
             "Q04_record_outside_its_scratch_root": dict(good, scratch_root=str(d / "elsewhere")),
             "Q05_drill_record_for_a_repository_outside_it": dict(good, mode="drill"),
             "Q06_not_inside_the_unit": good}
    before = sorted(p.name for p in qdir.iterdir()) if qdir.exists() else None
    for name, rec in cases.items():
        env = {k: v for k, v in os.environ.items() if k not in ("INVOCATION_ID", "P309_LAUNCH_RECORD")}
        env["P309_TEST_CODE"] = str(CODE)
        if rec is not None:
            path = d / (name + ".json")
            path.write_text(json.dumps(rec))
            env["P309_LAUNCH_RECORD"] = str(path)
        p = subprocess.run([sys.executable, "-B", "-c", Q_CODE], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, universal_newlines=True, timeout=300, env=env)
        res = next((json.loads(x[len("Q_RESULT "):]) for x in p.stdout.splitlines() if x.startswith("Q_RESULT ")), {})
        t(name, p.returncode == 0 and bool(res.get("refused")), res or p.stderr[-300:])
    after = sorted(p.name for p in qdir.iterdir()) if qdir.exists() else None
    t("Q07_refusals_created_nothing_in_qualification", before == after, after)


# ------------------------------------------------------------------------- U (follow-up W6; worker tier only)
def case_u() -> None:
    rec_path, conf_path = os.environ.get("P309_LAUNCH_RECORD"), os.environ.get("P309_HOST_CONFIG")
    if not (os.environ.get("INVOCATION_ID") and rec_path and conf_path and in_unit()):
        t("U00_in_unit_refusals_not_applicable_outside_a_unit", True, {"in_unit": in_unit()})
        return
    d = scratch("U_records")
    d.mkdir(parents=True, exist_ok=True)
    rec = json.loads(Path(rec_path).read_text())
    conf_copy = d / "host_config_altered.json"
    conf_copy.write_text(Path(conf_path).read_text() + "\n")          # same content, other bytes
    rec_hash = d / "record_config_hash.json"
    rec_hash.write_text(json.dumps(dict(rec, host_config_sha256="0" * 64)))
    rec_boot = d / "record_other_boot.json"
    prov = dict(rec["preflight"]["provenance"], boot_id="TEST-another-boot")
    rec_boot.write_text(json.dumps(dict(rec, preflight=dict(rec["preflight"], provenance=prov))))
    for name, record, conf, want in (("U01_altered_config_file_refused", rec_path, str(conf_copy), "configuration file"),
                                     ("U02_altered_config_hash_refused", str(rec_hash), conf_path, "configuration differs"),
                                     ("U03_other_boot_refused", str(rec_boot), conf_path, "host changed")):
        env = dict(os.environ, P309_TEST_CODE=str(CODE), P309_LAUNCH_RECORD=record, P309_HOST_CONFIG=conf)
        p = subprocess.run([sys.executable, "-B", "-c", Q_CODE], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, universal_newlines=True, timeout=300, env=env)
        res = next((json.loads(x[len("Q_RESULT "):]) for x in p.stdout.splitlines() if x.startswith("Q_RESULT ")), {})
        t(name, p.returncode == 0 and want in (res.get("refused") or ""), res or p.stderr[-300:])


# --------------------------------------------------------------------------------------- N (P11, A16)
def launcher(mode: str, conf: dict, sr: Path, *extra) -> dict:
    path = sr / "host.json"
    path.write_text(json.dumps(conf))
    env = {k: os.environ[k] for k in ("PATH", "LC_ALL", "HOME") if k in os.environ}
    env.update({"P309_SCRATCH_ROOT": str(sr), "PYTHONDONTWRITEBYTECODE": "1"})
    p = subprocess.run([sys.executable, "-B", str(CODE / "p309_launch.py"), "--mode", mode, "--host-config", str(path),
                        *extra], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       universal_newlines=True, timeout=600, env=env)
    return {"rc": p.returncode, "out": p.stdout, "err": p.stderr[-400:]}


def case_n() -> None:
    sr = scratch("N_launch")
    sr.mkdir(parents=True, exist_ok=True)
    sr = Path(os.path.realpath(str(sr)))
    froot = scratch("N_TEST_foreign_root")
    froot.mkdir(parents=True, exist_ok=True)
    launch = {"unit_user": "nobody", "unit_group": "nogroup", "memory_max": "8G", "oom_score_adjust": 500,
              "cpu_weight": 20, "io_weight": 20}
    conf = dict(launch, foreign_roots=[str(froot)], foreign_uids=[4242], sample_s=3.0, p309_roots=[str(sr)],
                interpreter=sys.executable)
    r1 = launcher("no-such-mode", conf, sr)
    t("N01_unknown_mode_refused", r1["rc"] == 2 and '"refused"' in r1["out"], r1["out"][-200:])
    r2 = launcher("drill", {k: v for k, v in conf.items() if k != "unit_user"}, sr)
    t("N02_missing_launch_setting_refused", r2["rc"] == 2 and "launch settings missing" in r2["out"], r2["out"][-200:])
    r3 = launcher("drill", dict(conf, unit_user="root"), sr)
    t("N03_root_unit_user_refused", r3["rc"] == 2 and "root" in r3["out"], r3["out"][-200:])
    before = set(os.listdir(str(sr)))
    r4 = launcher("drill", conf, sr, "--print-only")
    new = sorted(set(os.listdir(str(sr))) - before)
    recs = [n for n in new if n.startswith("launch_") and n.endswith(".json")]
    body = (sr / recs[0]).read_text() if len(recs) == 1 else ""
    rec = json.loads(body) if body else {}
    t("N04a_print_only_blocked", r4["rc"] == 1 and bool(rec.get("blockers")), rec.get("blockers"))
    t("N04b_record_redacted", bool(body) and str(froot) not in body and H.sha(str(froot)) in body,
      {"record": recs, "sha_present": H.sha(str(froot)) in body})
    t("N04c_record_binds_the_config_file", rec.get("host_config_file_sha256") == H.file_sha256(str(sr / "host.json")))
    t("N04d_launcher_not_unit_user_is_a_blocker", "launcher_not_unit_user" in (rec.get("blockers") or []),
      rec.get("blockers"))                      # this test never runs as the unit user it names ("nobody")
    r5 = launcher("drill", dict(conf, foreign_roots=[str(froot) + " x"]), sr)
    t("N05_foreign_root_with_whitespace_refused", r5["rc"] == 2 and "characters" in r5["out"], r5["out"][-200:])
    r6 = [launcher("drill", dict(conf, foreign_roots=[str(froot) + ch + "x"]), sr) for ch in ("$", ";", ":", "(")]
    t("N06_foreign_root_with_shell_or_separator_character_refused", all(
        r["rc"] == 2 and "characters" in r["out"] for r in r6), [r["out"][-80:] for r in r6])


# --------------------------------------------------------------------------------------- S01 (P10)
def case_s01() -> None:
    got = []
    old = signal.signal(signal.SIGTERM, lambda signum, frame: got.append(signum))
    try:
        cfg = dict(H.load_config([]), foreign_uids=[4242])
        base = dict(H.provenance(cfg, with_imds=False), boot_id="TEST-another-boot")
        out = scratch("S01_monitor.jsonl")
        with open(str(out), "w") as fh:
            m = subprocess.Popen([sys.executable, "-B", str(CODE / "p309_host.py"), "qhost-monitor", "--parent",
                                  str(os.getpid()), "--interval", "2"], stdin=subprocess.PIPE, stdout=fh,
                                 stderr=subprocess.STDOUT, universal_newlines=True)
            m.stdin.write(json.dumps({"cfg": cfg, "baseline": base}))
            m.stdin.close()
            try:
                rc = m.wait(timeout=120)
            except subprocess.TimeoutExpired:
                stop(m)
                rc = None
        time.sleep(0.2)
        events = [json.loads(x) for x in out.read_text().splitlines() if x.startswith("{")]
        rows = [r for r in events if r.get("kind") == "sample"]
        t("S01_monitor_fail_sends_one_sigterm_to_its_parent", rc == 1 and got == [signal.SIGTERM] and len(rows) == 1
          and [r.get("kind") for r in events] == ["sample_start", "sample"] and events[0]["m"] <= rows[0]["m"]
          and rows[0]["pass"] is False and rows[0]["continuity"]["same_boot"] is False, {"rc": rc, "signals": got,
                                                                                        "rows": len(rows)})
    finally:
        signal.signal(signal.SIGTERM, old)


# --------------------------------------------------------------------------------------- K01 (C5; FU2)
def outside(token: str):
    """one TEST process outside the tree under test, started by this process"""
    return subprocess.Popen([sys.executable, "-S", "-c", LEAF, token], stdin=subprocess.DEVNULL)


def live_with(token: str) -> list:
    out = []
    for p in os.listdir("/proc"):
        if p.isdigit() and token in (H.read("/proc/%s/cmdline" % p) or "").split("\0"):
            st = (H.read("/proc/%s/stat" % p) or "").rsplit(")", 1)[-1].split()
            if st and st[0] not in ("Z", "X"):
                out.append(int(p))
    return out


def kill_token(token: str) -> list:
    """SIGKILL the live TEST processes that carry this run's random token: only processes this test started carry it"""
    out = []
    for pid in live_with(token):
        try:
            os.kill(pid, signal.SIGKILL)
            out.append(pid)
        except OSError:
            pass
    return out


def case_k01() -> None:
    nonce = os.urandom(6).hex()
    tree_tok, out_tok = "TEST-K01-tree-" + nonce, "TEST-K01-outside-" + nonce
    o = outside(out_tok)
    try:
        env = dict(os.environ, P309_TEST_CODE=str(CODE))
        p = subprocess.run([sys.executable, "-c", TREE, tree_tok], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, universal_newlines=True, timeout=180, env=env)
        res = {}
        for line in p.stdout.splitlines():
            if line.startswith("TREE_RESULT "):
                res = json.loads(line[len("TREE_RESULT "):])
        t("K01_sigterm_ignoring_forking_tree_killed_at_once", p.returncode == 0 and res.get("named_in_killed") and
          res.get("live_with_token") == [] and res.get("caller_alive") and res.get("killed", 0) >= 5,
          res or p.stderr[-400:])
        t("K01b_outside_process_untouched", o.poll() is None and live_with(out_tok) == [o.pid])
        t("K01c_no_tree_process_left", live_with(tree_tok) == [], live_with(tree_tok))
    finally:
        stop(o)
        kill_token(tree_tok)                    # only on a failure is anything left to kill


# --------------------------------------------------------------------------------------- A01 (C5; FU2 (b))
def case_a01() -> None:
    nonce = os.urandom(6).hex()
    tree_tok, out_tok = "TEST-A01-tree-" + nonce, "TEST-A01-outside-" + nonce
    d = scratch("A01_" + nonce)
    d.mkdir(parents=True)
    qdir = FNS / "qualification"
    before = sorted(x.name for x in qdir.iterdir()) if qdir.exists() else None
    ledger = FNS / "ledger" / "ZERO_TARGET_LEDGER.jsonl"
    E.log("tests/test_p309_host_controls.py", "A01 (C5, follow-up FU2 (b)): the NEXT row, 'HOST_RERUN ABORTED BY "
          "Q-HOST', is written by the runner's own _qhost_abort inside this TEST control's child process; no host "
          "re-run ran and nothing is written in qualification/", klass="GOVERNANCE", notes="TEST control; attempt "
          "pointed at a TEST directory; token " + nonce)
    led_before = ledger.read_bytes() if ledger.exists() else b""
    o = outside(out_tok)
    try:
        env = dict(os.environ, P309_TEST_CODE=str(CODE), P309_TEST_DIR=str(d))
        p = subprocess.run([sys.executable, "-B", "-c", ABORT, tree_tok], stdin=subprocess.DEVNULL,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=300, env=env)
        time.sleep(0.5)
        fail = json.loads((d / "attempt" / "QHOST_FAIL.json").read_text()) if (d / "attempt" / "QHOST_FAIL.json").exists() else {}
        res = json.loads((d / "attempt" / "QC10_HOST_RERUN.json").read_text()) if (
            d / "attempt" / "QC10_HOST_RERUN.json").exists() else {}
        led_after = ledger.read_bytes() if ledger.exists() else b""
        rows = [json.loads(x) for x in led_after[len(led_before):].decode().splitlines() if x.strip()] if \
            led_after.startswith(led_before) else None
        mon = [json.loads(x) for x in (d / "QHOST_MONITOR.jsonl").read_text().splitlines() if
               x.startswith("{") and json.loads(x).get("kind") == "sample"] if (
            d / "QHOST_MONITOR.jsonl").exists() else []
        t("A01a_abort_exits_3", p.returncode == 3 and "ABORT_NOT_REACHED" not in p.stdout,
          {"rc": p.returncode, "tail": (p.stdout + p.stderr)[-300:]})
        t("A01b_abort_records_fail_and_result", fail.get("signal") == signal.SIGTERM and
          fail.get("descendants_killed", 0) >= 3 and res.get("pass") is False and len(mon) == 1 and
          mon[0]["pass"] is False, {"fail": fail, "result": res, "monitor_rows": len(mon)})
        t("A01c_abort_logs_exactly_its_own_row", rows is not None and len(rows) == 1 and rows[0]["purpose"].startswith(
            "HOST_RERUN ABORTED BY Q-HOST") and rows[0]["script"] == "code/p309_qualify.py" and
          rows[0]["new_target_evaluations"] == 0, rows)
        t("A01d_tree_dead_outside_untouched", live_with(tree_tok) == [] and o.poll() is None and
          live_with(out_tok) == [o.pid], {"tree_live": live_with(tree_tok)})
        after = sorted(x.name for x in qdir.iterdir()) if qdir.exists() else None
        t("A01e_nothing_in_qualification", before == after, after)
    finally:
        stop(o)
        kill_token(tree_tok)                    # only on a failure is anything left to kill


# --------------------------------------------------------------------------------------- B (C14)
def case_b() -> None:
    import make_freeze_manifest as MFM
    import p309_driver as D
    rt = D.runtime_identity()
    t("B01_generator_and_driver_runtime_agree", MFM.runtime_identity() == rt and bool(rt["interpreter_sha256"]), rt)

    def bind(**over):
        try:
            D.check_bindings({"code_pins": [], "data_pins": [], "_sha256": "TEST", "runtime": dict(rt, **over)})
            return "accepted"
        except D.Refusal as exc:
            return exc.code
    t("B02_same_runtime_accepted", bind() == "accepted")
    t("B03_other_glibc_or_binary_refused", bind(glibc="glibc 0.0") == "RUNTIME" and bind(
        interpreter_sha256="0" * 64) == "RUNTIME")


if __name__ == "__main__":
    E.log("tests/test_p309_host_controls.py", "r2 host controls (C11): TEST processes on the real /proc, the "
          "runner's Q-HOST refusals, the launcher's refusals, the monitor's SIGTERM path, kill_own_descendants, "
          "the C14 runtime binding", klass="GOVERNANCE", notes="TEST processes only, each killed and reaped; no "
          "other process signalled; no cell value")
    for case in (case_p01, case_p02, case_q, case_u, case_n, case_s01, case_k01, case_a01, case_b):
        try:
            case()
        except Exception as exc:  # noqa: BLE001 - a crashed case is a recorded FAIL
            t(case.__name__ + "_crashed", False, f"{type(exc).__name__}: {exc}"[:400])
    ok = all(v["pass"] for v in R.values())
    out = {"utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "all_pass": ok,
           "uid": os.getuid(), "in_unit": in_unit(), "cases": len(R), "results": R}
    (E.evidence_dir("host") / "HOST_CONTROLS.json").write_text(json.dumps(out, indent=1, sort_keys=True,
                                                                          default=str) + "\n")
    sys.exit(0 if ok else 1)
