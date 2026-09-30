"""MB-S r1: crash injection (architecture section 7). Fault points F1-F12, each by a REAL os._exit AND by a real SIGKILL
of the driver (a child process), plus the simulations: worker death, a simulated reboot, a stale lock, a stale pidfile,
a corrupt tmp, a truncated result.json, a wrong result hash, a stale pending ref naming a missing / a wrong blob, a
duplicate recover running concurrently, the memory watchdog and the awake-time EVAL_CAP. (Launcher death, the killed
process group / session and caffeinate death are in test_mbs308_launch.py.) For every case the test asserts the
classified state, the recovery action, that no second marker exists, that no verified checkpoint was recomputed, the
final state, and that a sealed result's certified bytes equal an uninterrupted run's. Synthetic evaluator, sandboxes.

    python3.14 -I -S -B test_mbs308_crash.py [t_name ...] [--out report.json]
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mbs308_testlib as T  # noqa: E402

TMP = T.SCRATCH / "t_crash"
_SB: dict = {}

# fault point -> (the classified state after the crash, the recover action, jobs recomputed by recover must be 0?)
EXPECT = {
    "F1": ("NO_TARGET_CONSUMED", "none", None),
    "F2": ("CONSUMED_INTERRUPTED", "resume", None),
    "F3": ("CONSUMED_INTERRUPTED", "resume", None),
    "F4": ("CONSUMED_INTERRUPTED", "resume", True),
    "F5": ("CONSUMED_INTERRUPTED", "resume", True),
    "F6": ("CONSUMED_INTERRUPTED", "resume", True),
    "F7": ("CONSUMED_INTERRUPTED", "resume", True),
    "F8": ("RESULT_DURABLE_UNSEALED", "seal-only", True),
    "F9": ("RESULT_DURABLE_UNSEALED", "seal-only", True),
    "F10": ("PENDING_RESULT", "seal-only", True),
    "F11": ("PENDING_RESULT", "seal-only", True),
    "F12": ("SEALED", "materialize", True),
}


def sb() -> T.Sandbox:
    if "sb" not in _SB:
        _SB["sb"] = T.Sandbox(TMP)
    return _SB["sb"]


def fresh() -> dict:
    if "base" not in _SB and not _SB.get("in_baseline"):    # the uninterrupted reference run comes first, always
        baseline()
    ch = sb().grant_chain()
    for f in ("joblog.txt", "worker_died.flag"):
        if (sb().tmp / f).exists():
            (sb().tmp / f).unlink()
    return ch


def status(**kw) -> str:
    r = T.child(sb(), "status", kw or None)
    return r["stdout"].strip().splitlines()[-1] if r["stdout"].strip() else "ERROR"


def classify(**kw) -> dict:
    return (T.child(sb(), "classify", kw or None)["out"] or {}).get("classified", {})


def counts() -> dict:
    return T.joblog_counts(sb().tmp / "joblog.txt")


def baseline() -> bytes:
    if "base" not in _SB:
        _SB["in_baseline"] = True
        fresh()
        r = T.child(sb(), "execute")
        assert r["out"] == {"rc": 0}, r
        _SB["base"] = T.certified_bytes(sb().sealed_record())
    return _SB["base"]


def one_marker(ch) -> bool:
    refs = sb().refs()
    return [r for r in refs if r.endswith("target-consumed")] == [T.PREFIX + "target-consumed"] and \
        refs[T.PREFIX + "target-consumed"] == ch["grant"]


def action_of(r: dict) -> str | None:
    for ln in r["stdout"].splitlines():
        if "MBS308 RECOVER state" in ln and "-> " in ln:
            return ln.split("-> ", 1)[1].strip()
    return None


def moved_locks(r: dict) -> int | None:
    for ln in r["stdout"].splitlines():
        if "stale campaign git lockfile(s) moved aside" in ln:
            return int(ln.split(": ", 1)[1].split()[0])
    return None


def sealed_ok() -> bool:
    rec = sb().sealed_record()
    return rec is not None and rec["status"] == "TARGET_EVALUATED" and T.certified_bytes(rec) == baseline() and \
        sb().materialized().is_file() and sb().materialized().read_bytes() == sb().sealed_raw()


def fault_case(point: str, how: str) -> dict:
    base = baseline()
    ch = fresh()
    at = 5 if point == "F3" else 1
    c = T.child(sb(), "execute", {"fault": {point: {"at": at, "how": how}}})
    died = (c["signal"] == 9) if how == "kill" else (c["rc"] == 86)
    st1 = status()
    ck_before = sb().ckpt_names()
    n_before = counts()
    r = recover()
    act = action_of(r)
    extra = None
    if point == "F1":
        extra = T.child(sb(), "execute")
    st2 = status()
    after = counts()
    recomputed_verified = [n for n in ck_before if after.get(n, 0) != n_before.get(n, 0)]
    newly = sum(after.values()) - sum(n_before.values())
    want_state, want_action, zero_new = EXPECT[point]
    rec = sb().sealed_record()
    ok = died and st1 == want_state and act == want_action and st2 == "SEALED" and sealed_ok() and one_marker(ch) \
        and not recomputed_verified and (not zero_new or (newly == 0 if point != "F1" else True)) \
        and rec is not None and T.certified_bytes(rec) == base
    if point == "F1":
        ok = ok and extra["out"] == {"rc": 0} and r["out"] == {"rc": 0}
    if point in ("F5", "F6", "F7"):
        ok = ok and any(n.startswith("result.json.tmp.rejected-") for n in os.listdir(sb().spool()))
    return {"ok": ok, "died": died, "state_after_crash": st1, "action": act, "final": st2,
            "checkpoints_before_recover": len(ck_before), "jobs_computed_by_recover": newly,
            "recomputed_verified": recomputed_verified, "attempt": rec and rec.get("lifecycle", {}).get("attempt")}


def recover(**spec) -> dict:
    return T.child(sb(), "recover", spec or None)


def _mk(point, how):
    def t():
        return fault_case(point, how)
    t.__name__ = f"t_{point}_{how}"
    return t


for _p in EXPECT:
    for _h in ("exit", "kill"):
        globals()[f"t_{_p}_{_h}"] = _mk(_p, _h)


# ====================================================================== simulations
def t_S01_worker_death():
    """A worker death is an execution failure (MB r1 rule): the pool breaks, the remaining workers (which ignore
    SIGTERM) are released by SIGKILL, and the attempt seals TARGET_EVALUATION_FAILED -> INDETERMINATE, promptly (no
    hang), whichever job dies and whatever the other workers are doing.

    R3 (REVIEW_IMPLEMENTATION_MBS308_DELTA, condition 2): the FIRST run decides the broken-pool release (mutant M33)
    without depending on timing. Every synthetic job sleeps 90 s and RLR.0.6, the first job of MB r1's job order, dies
    at once, so when the pool breaks the other worker is inside a 90 s job (or blocked on the call queue). It ignores
    SIGTERM, and concurrent.futures' terminate_broken joins it while holding the executor's shutdown lock, so only the
    SIGKILL release can end this run inside the 60 s bound. Its harness timeout (150 s) exceeds the 90 s sleep: an
    unreleased run ends (or is stopped) after the bound and fails it by assertion, never by an exception."""
    runs = {}
    ok = True
    plan = [({"worker_die": "RLR.0.6", "job_sleep": 90}, 150)] + \
        [({"worker_die": key}, 90) for key in ("C2B.2.20", "C2B.1.20", "C1B.2.4", "RLR.2.4", "RLR.0.6", "C2B.2.20",
                                               "C2B.0.20")]
    for spec, timeout in plan:
        ch = fresh()
        t0 = time.time()
        r = T.child(sb(), "execute", spec, timeout=timeout)
        rec = sb().sealed_record()
        st = status()
        r2 = recover()
        good = r["out"] == {"rc": 5} and rec is not None and rec["status"] == "TARGET_EVALUATION_FAILED" \
            and "BrokenProcessPool" in rec["target"]["error"] and st == "INDETERMINATE" \
            and action_of(r2) == "materialize" and one_marker(ch) and time.time() - t0 < 60
        tag = spec["worker_die"] + (f"+sleep{spec['job_sleep']}" if spec.get("job_sleep") else "")
        runs[tag + f"#{len(runs)}"] = {"ok": good, "seconds": round(time.time() - t0, 1), "rc": r["out"]}
        ok = ok and good
    return {"ok": ok, "runs": runs}


def t_S02_reboot_after_crash():
    ch = fresh()
    T.child(sb(), "execute", {"fault": {"F3": {"at": 4, "how": "kill"}}})
    names = sb().ckpt_names()
    before = counts()
    other = "00000000-0000-4000-8000-000000000001"
    c = classify(boot_uuid=other)
    r = recover(boot_uuid=other)
    after = counts()
    return {"ok": c["state"] == "CONSUMED_INTERRUPTED" and "BOOT_UUID_CHANGED" in c["why"]
            and action_of(r) == "resume" and status() == "SEALED" and sealed_ok() and one_marker(ch)
            and all(after.get(n) == before.get(n) for n in names), "classified": c["why"]}


def t_S03_stale_lock():
    ch = fresh()
    T.child(sb(), "execute", {"fault": {"F3": {"at": 4, "how": "kill"}}})
    h = T.Helper(120)
    try:
        code = str(sb().p(T.NS_REL + "/code"))
        if code not in sys.path:
            sys.path.insert(0, code)
        import mbs308_host as H
        live = H.identity(h.p.pid)
        lock = sb().spool() / "recover.lock"
        lock.write_text(json.dumps({"identity": live}))
        r_live = recover()
        st_live = status()
    finally:
        h.kill()
    lock.write_text(json.dumps({"identity": live}))       # now stale (the helper is dead)
    r = recover()
    aside = [n for n in os.listdir(sb().spool()) if n.startswith("recover.lock.rejected-stale-lock")]
    return {"ok": r_live["out"] == {"rc": 2, "refused": "LOCKED"} and st_live == "CONSUMED_INTERRUPTED"
            and r["out"] == {"rc": 0} and status() == "SEALED" and sealed_ok() and len(aside) == 1
            and not lock.exists() and one_marker(ch), "live_lock": r_live["out"], "stale_lock": r["out"]}


def t_S04_stale_pidfile():
    ch = fresh()
    T.child(sb(), "execute", {"fault": {"F3": {"at": 4, "how": "kill"}}})
    code = str(sb().p(T.NS_REL + "/code"))
    if code not in sys.path:
        sys.path.insert(0, code)
    import mbs308_state as Sm
    st = Sm.Store(sb().root, "refs/heads/" + T.BRANCH)
    rec, pst = Sm.read_pidfile(st)
    r = recover()
    return {"ok": pst == "STALE" and rec is not None and r["out"] == {"rc": 0} and status() == "SEALED"
            and sealed_ok() and one_marker(ch) and Sm.read_pidfile(st)[1] in ("ABSENT", "STALE"),
            "pidfile_after_crash": pst}


def t_S05_corrupt_tmp():
    ch = fresh()
    T.child(sb(), "execute", {"fault": {"F3": {"at": 4, "how": "exit"}}})
    (sb().spool()).mkdir(exist_ok=True)
    (sb().spool() / "result.json.tmp").write_bytes(b'{"complete": true, "status": "TARGET_EVALUATED", "trunc')
    st1 = status()
    r = recover()
    return {"ok": st1 == "CONSUMED_INTERRUPTED" and action_of(r) == "resume" and status() == "SEALED" and sealed_ok()
            and any(n.startswith("result.json.tmp.rejected-") for n in os.listdir(sb().spool())) and one_marker(ch),
            "state": st1}


def _after_f9() -> dict:
    ch = fresh()
    T.child(sb(), "execute", {"fault": {"F9": {"at": 1, "how": "exit"}}})
    return ch


def _durable_to_interrupted(mutate, label) -> dict:
    ch = _after_f9()
    p = sb().spool() / "result.json"
    mutate(p)
    c = classify()
    n0 = sum(counts().values())
    r = recover()
    rejected = [n for n in os.listdir(sb().spool()) if n.startswith("result.json.rejected-")]
    return {"ok": c["state"] == "CONSUMED_INTERRUPTED" and any(w.startswith("SPOOL_RESULT_REJECTED") for w in c["why"])
            and action_of(r) == "resume" and sum(counts().values()) == n0 and status() == "SEALED" and sealed_ok()
            and len(rejected) == 1 and one_marker(ch), "case": label, "classified": c["why"]}


def t_S06_truncated_result():
    return _durable_to_interrupted(lambda p: p.write_bytes(p.read_bytes()[: len(p.read_bytes()) // 2]), "truncated")


def t_S07_wrong_result_hash():
    def flip(p):
        b = p.read_bytes()
        i = b.index(b'"mechanical_outcome": "') + len(b'"mechanical_outcome": "')
        p.write_bytes(b[:i] + b"X" + b[i + 1:])
    return _durable_to_interrupted(flip, "wrong hash")


def _stale_pending(target: str, label: str) -> dict:
    ch = _after_f9()
    ref = sb().git_dir() / "refs/p5y-k5-cell308-mbs-r1/pending-result"
    ref.parent.mkdir(parents=True, exist_ok=True)
    ref.write_text(target + "\n")
    c = classify()
    n0 = sum(counts().values())
    r = recover()
    return {"ok": c["state"] == "RESULT_DURABLE_UNSEALED" and any(w.startswith("STALE_PENDING_REF") for w in c["why"])
            and action_of(r) == "seal-only" and sum(counts().values()) == n0 and status() == "SEALED" and sealed_ok()
            and sb().refs()[T.PREFIX + "pending-result"] != target and one_marker(ch),
            "case": label, "classified": c["why"]}


def t_S08_stale_pending_missing_blob():
    return _stale_pending("0123456789abcdef0123456789abcdef01234567", "missing blob")


def t_S09_stale_pending_wrong_blob():
    wrong = subprocess.run(["/usr/bin/git", "-C", str(sb().root), "hash-object", "-w", "--stdin"],
                           input=b'{"not": "a result"}\n', capture_output=True).stdout.decode().strip()
    return _stale_pending(wrong, "wrong blob")


def t_S10_concurrent_recover():
    ch = fresh()
    T.child(sb(), "execute", {"fault": {"F3": {"at": 5, "how": "kill"}}})
    names = sb().ckpt_names()
    before = counts()
    env = dict(T.GENV, MBS308_TEST_CHILD="1", MBS308_TEST_JOBLOG=str(sb().tmp / "joblog.txt"),
               MBS308_TEST_JOB_SLEEP="0.3", MBS308_TEST_DIEFLAG=str(sb().tmp / "worker_died.flag"))
    spec = json.dumps({"mbr1_git_dir": str(sb().mbr1_git_dir), "joblog": str(sb().tmp / "joblog.txt")})
    cmd = [T.PY, "-I", "-S", "-B", str(sb().p(T.NS_REL + "/tests/mbs308_child.py")), str(sb().root), "recover", spec]
    ps = [subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env) for _ in range(2)]
    outs = []
    for p in ps:
        o, e = p.communicate(timeout=300)
        line = [ln for ln in o.splitlines() if ln.startswith("{")]
        outs.append(json.loads(line[-1]) if line else {"stderr": e[-300:]})
    rcs = sorted(o.get("rc", -1) for o in outs)
    after = counts()
    return {"ok": rcs.count(0) == 1 and any(o.get("refused") in ("LOCKED", "LOCK_RACE", "RESUME_REFUSED")
                                            or o.get("rc") == 8
                                            for o in outs if o.get("rc") != 0)
            and status() == "SEALED" and sealed_ok() and one_marker(ch)
            and all(after.get(n) == before.get(n) for n in names), "outcomes": outs}


def t_S11_memory_watchdog():
    ch = fresh()
    r = T.child(sb(), "execute", {"alloc_mb": 400, "job_sleep": 3, "mem_cap_mb": 200})
    rec = sb().sealed_record()
    ev = rec["lifecycle"]["stage1_context"]["memory_watchdog"]["events"] if rec else []
    ev = [e for e in ev if "rss_bytes" in e]
    return {"ok": r["out"] == {"rc": 5} and rec["status"] == "TARGET_EVALUATION_FAILED" and len(ev) >= 1
            and all(e["killed"] and e["rss_bytes"] > e["cap_bytes"] for e in ev) and status() == "INDETERMINATE"
            and one_marker(ch), "events": ev[:2], "sealed_status": rec and rec["status"]}


def t_S12_eval_cap_awake_time():
    ch = fresh()
    t0 = time.time()
    r = T.child(sb(), "execute", {"eval_cap_s": 2, "job_sleep": 1.5})
    took = time.time() - t0
    rec = sb().sealed_record()
    return {"ok": r["out"] == {"rc": 5} and rec["status"] == "TARGET_EVALUATION_FAILED"
            and rec["target"]["error"].startswith("TimeoutError") and rec["lifecycle"]["eval_cap"]["hit"] is True
            and rec["lifecycle"]["eval_cap"]["clock"] == "CLOCK_UPTIME_RAW" and status() == "INDETERMINATE"
            and one_marker(ch) and took < 60, "eval_cap": rec["lifecycle"]["eval_cap"], "seconds": round(took, 1)}


# ====================================================================== R1 (iv): stale git lockfiles of the campaign
MARKER_LOCK = T.PREFIX + "target-consumed.lock"
JOURNAL_LOCK = T.PREFIX + "journal.lock"
CKPT_LOCK = T.PREFIX + "ckpt.lock"
PENDING_LOCK = T.PREFIX + "pending-result.lock"
BRANCH_LOCK = "refs/heads/" + T.BRANCH + ".lock"
PACKED_LOCK = "packed-refs.lock"


def _plant(point: str, rel: str, at: int = 1) -> dict:
    return {"fault": {point: {"at": at, "how": "plant", "path": str(sb().lock_path(rel))}}}


def _actions() -> list:
    p = sb().spool() / "recover-actions.jsonl"
    return [json.loads(x) for x in p.read_text().splitlines()] if p.exists() else []


def _journal_state() -> str | None:
    code = str(sb().p(T.NS_REL + "/code"))
    if code not in sys.path:
        sys.path.insert(0, code)
    import mbs308_state as Sm
    rec = Sm.Journal.read(Sm.Store(sb().root, "refs/heads/" + T.BRANCH))[1]
    return rec and rec["state"]


def t_L01_marker_lock():
    """A stale target-consumed.lock (a) before execute: GIT_LOCKED, nothing consumed; (b) appearing between the intent
    and the marker (the DEF-1 d wedge): MARKER_WRITE_FAILED (the marker provably absent), the intent closed
    ABORTED_INTENT, NO_TARGET_CONSUMED. recover moves the lock aside (recorded); the next execute takes over the
    intent and seals."""
    base = baseline()
    ch = fresh()
    sb().plant_lock(MARKER_LOCK)
    a1 = T.child(sb(), "execute")
    a_state = status()
    a_rec = recover()
    a2 = T.child(sb(), "execute")
    ok_a = a1["out"] == {"rc": 2, "refused": "GIT_LOCKED"} and a_state == "NO_TARGET_CONSUMED" \
        and moved_locks(a_rec) == 1 and action_of(a_rec) == "none" and a2["out"] == {"rc": 0} and sealed_ok() \
        and one_marker(ch)
    ch = fresh()
    b1 = T.child(sb(), "execute", _plant("F1", MARKER_LOCK))
    b_state, b_journal = status(), _journal_state()
    b_marker = T.PREFIX + "target-consumed" in sb().refs()
    b_again = T.child(sb(), "execute")
    b_rec = recover()
    b2 = T.child(sb(), "execute")
    rec = sb().sealed_record()
    ok_b = b1["out"] == {"rc": 2, "refused": "MARKER_WRITE_FAILED"} and b_state == "NO_TARGET_CONSUMED" \
        and b_journal == "ABORTED_INTENT" and not b_marker and b_again["out"] == {"rc": 2, "refused": "GIT_LOCKED"} \
        and moved_locks(b_rec) == 1 and b2["out"] == {"rc": 0} and sealed_ok() and one_marker(ch) \
        and T.certified_bytes(rec) == base and len(sb().locks_aside()) == 1 and _actions()[0]["lock"] == MARKER_LOCK
    return {"ok": ok_a and ok_b, "a": [a1["out"], a_state, a2["out"]],
            "b": [b1["out"], b_state, b_journal, b_again["out"], b2["out"]]}


def t_L02_journal_lock_after_crash():
    ch = fresh()
    T.child(sb(), "execute", {"fault": {"F3": {"at": 4, "how": "kill"}}})
    names, before = sb().ckpt_names(), counts()
    sb().plant_lock(JOURNAL_LOCK)
    s1 = status()
    direct = T.child(sb(), "resume")
    r = recover()
    after = counts()
    return {"ok": s1 == "CONSUMED_INTERRUPTED" and direct["out"] == {"rc": 2, "refused": "GIT_LOCKED"}
            and moved_locks(r) == 1 and action_of(r) == "resume" and r["out"] == {"rc": 0} and status() == "SEALED"
            and sealed_ok() and one_marker(ch) and all(after.get(n) == before.get(n) for n in names)
            and not sb().lock_path(JOURNAL_LOCK).exists(),
            "direct_resume": direct["out"], "recover": r["out"]}


def t_L03_journal_lock_during_seal():
    """R1 (ii): a journal lock appearing once the result is durable (F8) never stops the seal: the run seals itself
    (the journal lags); recover then moves the lock aside and catches the journal up."""
    ch = fresh()
    r = T.child(sb(), "execute", _plant("F8", JOURNAL_LOCK))
    s1, j1 = status(), _journal_state()
    r2 = recover()
    return {"ok": r["out"] == {"rc": 0} and s1 == "SEALED" and sealed_ok() and j1 == "COMPUTING"
            and moved_locks(r2) == 1 and action_of(r2) == "materialize" and _journal_state() == "SEALED"
            and one_marker(ch), "run": r["out"], "journal_after_run": j1, "journal_after_recover": _journal_state()}


def t_L04_journal_conflict_during_seal():
    """R1 (ii): a GENUINE journal conflict once the result is durable (another writer advances the journal at F8) is
    recorded and never stops the seal."""
    ch = fresh()
    r = T.child(sb(), "execute", {"fault": {"F8": {"how": "bump_journal", "repo": str(sb().root),
                                                  "branch": "refs/heads/" + T.BRANCH}}})
    return {"ok": r["out"] == {"rc": 0} and status() == "SEALED" and sealed_ok() and one_marker(ch), "run": r["out"]}


def t_L05_ckpt_lock_midrun():
    """R1 (i): a ckpt.lock appearing after the 14th checkpoint: the later checkpoint writes fail WITHOUT a conflict,
    are recorded and retried, and the evaluation completes and seals (no LostOwnership)."""
    base = baseline()
    ch = fresh()
    r = T.child(sb(), "execute", _plant("F3", CKPT_LOCK, at=14))
    rec = sb().sealed_record()
    life = (rec or {}).get("lifecycle", {})
    fails = life.get("stage1_context", {}).get("checkpoint_write_failures", [])
    refw = [f for f in life.get("ref_write_failures", []) if f["ref"].endswith("/ckpt")]
    return {"ok": r["out"] == {"rc": 0} and status() == "SEALED" and sealed_ok() and len(fails) == 4
            and all(f.endswith("RefWriteError") for f in fails) and len(refw) >= 4 and all(f["lock_present"] for f in refw)
            and T.certified_bytes(rec) == base and one_marker(ch), "run": r["out"], "ckpt_failures": fails}


def t_L06_ckpt_lock_after_crash():
    ch = fresh()
    T.child(sb(), "execute", {"fault": {"F3": {"at": 4, "how": "kill"}}})
    names, before = sb().ckpt_names(), counts()
    sb().plant_lock(CKPT_LOCK)
    r = recover()
    after = counts()
    return {"ok": moved_locks(r) == 1 and action_of(r) == "resume" and status() == "SEALED" and sealed_ok()
            and one_marker(ch) and all(after.get(n) == before.get(n) for n in names), "recover": r["out"]}


def t_L07_pending_lock():
    ch = fresh()
    r = T.child(sb(), "execute", _plant("F8", PENDING_LOCK))
    s1 = status()
    n0 = sum(counts().values())
    r2 = recover()
    return {"ok": r["out"] == {"rc": 4} and s1 == "RESULT_DURABLE_UNSEALED" and moved_locks(r2) == 1
            and action_of(r2) == "seal-only" and status() == "SEALED" and sealed_ok() and sum(counts().values()) == n0
            and one_marker(ch), "run": r["out"], "state": s1}


def t_L08_branch_lock():
    ch = fresh()
    r = T.child(sb(), "execute", _plant("F10", BRANCH_LOCK))
    s1 = status()
    n0 = sum(counts().values())
    r2 = recover()
    return {"ok": r["out"] == {"rc": 4} and s1 == "PENDING_RESULT" and moved_locks(r2) == 1
            and action_of(r2) == "seal-only" and status() == "SEALED" and sealed_ok() and sum(counts().values()) == n0
            and one_marker(ch), "run": r["out"], "state": s1}


def _intact(p: Path) -> bool:
    """The planted lockfile is still in place, byte for byte (sb().plant_lock and the fault hook write these bytes)."""
    return p.is_file() and not p.is_symlink() and p.read_bytes() == b"0" * 40 + b"\n"


def t_L09_packed_refs_lock_never_moved():
    """C-1 (REVIEW_IMPLEMENTATION_MBS308_DELTA): packed-refs.lock is never a campaign lockfile. It blocks only ref
    deletion, which the campaign never performs, and a live git holder is invisible to lsof, so the campaign never
    lists, moves or deletes it. (a) Planted after a crash: the classification lists no lockfile, recover resumes and
    seals. (b) Planted mid-run (at the 4th checkpoint) and (c) once the result is durable (F8): the run seals itself
    with no failed ref write. (d) Planted before execute: MB r1's carried check_clean refuses GIT_LOCKED with nothing
    consumed and recover does nothing; once git's lock is gone (the test removes it, as git would), execute seals. In
    every case the planted file stays in place byte for byte, git-locks-aside stays empty and no recover action names
    it."""
    base = baseline()
    lk = sb().lock_path(PACKED_LOCK)

    def untouched() -> bool:
        return _intact(lk) and sb().locks_aside() == [] and not any(a.get("lock") == PACKED_LOCK for a in _actions())
    ch = fresh()                                                                            # (a)
    T.child(sb(), "execute", {"fault": {"F3": {"at": 4, "how": "kill"}}})
    sb().plant_lock(PACKED_LOCK)
    cls = classify()
    r = recover()
    ok_a = cls.get("git_locks") == [] and r["out"] == {"rc": 0} and action_of(r) == "resume" \
        and moved_locks(r) is None and status() == "SEALED" and sealed_ok() and one_marker(ch) and untouched()
    a = {"listed": cls.get("git_locks"), "recover": r["out"], "action": action_of(r), "untouched": untouched()}
    lk.unlink(missing_ok=True)          # missing only if something moved it: the assertions above already failed
    out = {}
    for tag, point, at in (("b", "F3", 4), ("c", "F8", 1)):                                 # (b), (c)
        ch = fresh()
        r = T.child(sb(), "execute", _plant(point, PACKED_LOCK, at=at))
        rec = sb().sealed_record()
        life = (rec or {}).get("lifecycle", {})
        out[tag] = {"ok": r["out"] == {"rc": 0} and status() == "SEALED" and sealed_ok() and one_marker(ch)
                    and T.certified_bytes(rec) == base and not life.get("ref_write_failures")
                    and not life.get("stage1_context", {}).get("checkpoint_write_failures") and untouched(),
                    "run": r["out"], "planted_during_run": lk.exists()}
        if lk.exists():
            lk.unlink()
    ch = fresh()                                                                            # (d)
    sb().plant_lock(PACKED_LOCK)
    d1 = T.child(sb(), "execute")
    d_state = status()
    d_rec = recover()
    d_held = untouched()
    lk.unlink(missing_ok=True)          # git's own lock is released (by git; never by the campaign)
    d2 = T.child(sb(), "execute")
    ok_d = d1["out"] == {"rc": 2, "refused": "GIT_LOCKED"} and d_state == "NO_TARGET_CONSUMED" \
        and action_of(d_rec) == "none" and moved_locks(d_rec) is None and d_held and d2["out"] == {"rc": 0} \
        and sealed_ok() and one_marker(ch)
    return {"ok": ok_a and out["b"]["ok"] and out["c"]["ok"] and ok_d, "a": a, "b": out["b"], "c": out["c"],
            "d": [d1["out"], d_state, action_of(d_rec), d_held, d2["out"]]}


def t_L10_lock_with_live_campaign_process():
    """A lockfile is NOT stale while a live campaign process exists (here: the pidfile names a live process): recover
    does nothing; once that process is gone, recover moves the lock aside and resumes."""
    ch = fresh()
    T.child(sb(), "execute", {"fault": {"F3": {"at": 4, "how": "kill"}}})
    lk = sb().plant_lock(JOURNAL_LOCK)
    code = str(sb().p(T.NS_REL + "/code"))
    if code not in sys.path:
        sys.path.insert(0, code)
    import mbs308_host as H
    h = T.Helper(120)
    try:
        (sb().spool() / "driver.pid").write_text(json.dumps({"identity": H.identity(h.p.pid)}))
        r1 = recover()
        held = lk.exists() and sb().locks_aside() == []
    finally:
        h.kill()
    r2 = recover()
    return {"ok": r1["out"] == {"rc": 8} and held and moved_locks(r2) == 1 and status() == "SEALED" and sealed_ok()
            and one_marker(ch), "first": r1["out"], "second": r2["out"]}


def t_L11_campaign_lock_open():
    """A campaign lockfile that some process holds open (lsof) is NOT stale: recover does nothing; once it is closed,
    recover moves it aside and resumes. (C-1: this case planted packed-refs.lock, which is no longer a campaign
    lockfile; it now plants the campaign's own ckpt ref lock.)"""
    ch = fresh()
    T.child(sb(), "execute", {"fault": {"F3": {"at": 4, "how": "kill"}}})
    lk = sb().plant_lock(CKPT_LOCK)
    holder = subprocess.Popen([T.PY, "-I", "-S", "-B", "-c", f"import time; f = open({str(lk)!r}); time.sleep(120)"],
                              stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        time.sleep(0.5)
        r1 = recover()
        held = lk.exists() and sb().locks_aside() == []
    finally:
        holder.kill()
        holder.wait()
    r2 = recover()
    return {"ok": r1["out"] == {"rc": 8} and held and moved_locks(r2) == 1 and status() == "SEALED" and sealed_ok()
            and one_marker(ch) and _actions()[-1]["lock"] == CKPT_LOCK, "first": r1["out"], "second": r2["out"]}


def t_L12_lock_ps_failure_not_stale():
    """N-3 (REVIEW_IMPLEMENTATION_MBS308_DELTA): a campaign lockfile is NOT stale while a recorded campaign process
    identity cannot be read. The pidfile names a live process and `ps` fails for it (planted): its identity is UNKNOWN,
    never dead, so recover does nothing (exit 8). Once the pid is gone (positive evidence of death, whatever `ps`
    does), recover moves the lock aside and resumes."""
    ch = fresh()
    T.child(sb(), "execute", {"fault": {"F3": {"at": 4, "how": "kill"}}})
    lk = sb().plant_lock(JOURNAL_LOCK)
    code = str(sb().p(T.NS_REL + "/code"))
    if code not in sys.path:
        sys.path.insert(0, code)
    import mbs308_host as H
    h = T.Helper(120)
    try:
        ident = H.identity(h.p.pid)
        (sb().spool() / "driver.pid").write_text(json.dumps({"identity": ident}))
        r1 = recover(ps_fail_pids=[h.p.pid])
        held = lk.exists() and sb().locks_aside() == []
    finally:
        h.kill()
    r2 = recover(ps_fail_pids=[h.p.pid])
    complete = all(ident.get(k) for k in ("pid", "start_time", "boot_uuid", "command_sha256"))
    return {"ok": complete and r1["out"] == {"rc": 8} and held and moved_locks(r2) == 1 and status() == "SEALED"
            and sealed_ok() and one_marker(ch), "first": r1["out"], "second": r2["out"]}


if __name__ == "__main__":
    T.cli(globals())
