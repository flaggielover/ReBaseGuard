"""MB-S r1: the state machine (architecture section 2), the resume rules (section 4), the persistence contract (section 3)
and the MB r1 state assertion (GC-8). Every state is constructed in a SANDBOX (real crashes of the synthetic run, or
planted refs / journals), classified by the driver's read-only `status`, and driven by `recover`; the test asserts the
state, the action, the final state, one marker, no recomputation of a verified checkpoint and, where a result is sealed,
that its certified bytes equal an uninterrupted run's. Synthetic evaluator only; no cell is evaluated.

    python3.14 -I -S -B test_mbs308_state.py [t_name ...] [--out report.json]
"""
from __future__ import annotations

import datetime
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mbs308_testlib as T  # noqa: E402

TMP = T.SCRATCH / "t_state"
_SB: dict = {}


def sb() -> T.Sandbox:
    if "sb" not in _SB:
        _SB["sb"] = T.Sandbox(TMP)
    return _SB["sb"]


def S():
    """The sandbox's own mbs308_state / mbs308_host (the code under test, possibly mutated)."""
    code = str(sb().p(T.NS_REL + "/code"))
    if code not in sys.path:
        sys.path.insert(0, code)
    import mbs308_state
    return mbs308_state


def store():
    return S().Store(sb().root, "refs/heads/" + T.BRANCH)


def status(**kw) -> str:
    r = T.child(sb(), "status", kw or None)
    return r["stdout"].strip().splitlines()[-1] if r["stdout"].strip() else f"ERROR {r['stderr'][-300:]}"


def classify(**kw) -> dict:
    r = T.child(sb(), "classify", kw or None)
    return (r["out"] or {}).get("classified", {"state": "ERROR", "stderr": r["stderr"][-300:]})


def fresh() -> dict:
    if "base" not in _SB and not _SB.get("in_baseline"):    # the uninterrupted reference run comes first, always
        baseline()
    ch = sb().grant_chain()
    log = sb().tmp / "joblog.txt"
    if log.exists():
        log.unlink()
    flag = sb().tmp / "worker_died.flag"
    if flag.exists():
        flag.unlink()
    return ch


def baseline() -> bytes:
    if "base" not in _SB:
        _SB["in_baseline"] = True
        fresh()
        r = T.child(sb(), "execute")
        rec = sb().sealed_record()
        assert r["out"] == {"rc": 0} and rec["status"] == "TARGET_EVALUATED", r
        _SB["base"] = T.certified_bytes(rec)
    return _SB["base"]


def one_marker(ch) -> bool:
    refs = sb().refs()
    return [r for r in refs if r.endswith("target-consumed")] == [T.PREFIX + "target-consumed"] and \
        refs[T.PREFIX + "target-consumed"] == ch["grant"]


def platform() -> dict:
    if "platform" not in _SB:
        _SB["platform"] = T.child(sb(), "platform")["out"]["platform"]
    return _SB["platform"]


def plant_computing(ch, process: dict, **extra) -> None:
    st = store()
    assert st.cas_ref(T.PREFIX + "target-consumed", ch["grant"], None)
    now = S().utc()
    S().Journal(st, None, None).advance(**{"state": "COMPUTING", "grant_commit": ch["grant"],
                                           "driver_sha256": sb().driver_sha, "boot_uuid": process.get("boot_uuid"),
                                           "process": process, "attempt": 1, "history": [], "ckpt_tree": None,
                                           "n_ckpt": 0, "ckpt_failures": {}, "marker_utc": now,
                                           "platform": platform(),
                                           "attempt_started_utc": now, **extra})


def host():
    S()
    import mbs308_host
    return mbs308_host


def dead_identity() -> dict:
    h = T.Helper(60)
    ident = host().identity(h.p.pid)
    h.kill()
    return ident


def crash(point: str, at: int = 1, how: str = "kill", **spec) -> dict:
    return T.child(sb(), "execute", {"fault": {point: {"at": at, "how": how}}, **spec})


def recover(**spec) -> dict:
    return T.child(sb(), "recover", spec or None)


def sealed_ok() -> bool:
    rec = sb().sealed_record()
    return rec is not None and rec["status"] == "TARGET_EVALUATED" and T.certified_bytes(rec) == baseline() and \
        sb().materialized().read_bytes() == sb().sealed_raw()


def counts() -> dict:
    return T.joblog_counts(sb().tmp / "joblog.txt")


# ====================================================================== states and recover actions
def t_no_target_consumed():
    baseline()
    fresh()
    s0 = status()
    r = recover()
    return {"ok": s0 == "NO_TARGET_CONSUMED" and r["out"] == {"rc": 0} and "-> none" in r["stdout"]
            and sb().refs() == {}, "status": s0, "recover": r["out"]}


def t_computing_then_interrupted():
    """COMPUTING: a live recorded process under the same boot -> recover waits, resume / close refuse. Its death ->
    INTERRUPTED -> recover resumes -> SEALED (bytes = uninterrupted)."""
    base = baseline()
    ch = fresh()
    h = T.Helper(300)
    try:
        plant_computing(ch, host().identity(h.p.pid))
        refs0 = sb().refs()
        s1 = status()
        r_wait = recover()
        r_res = T.child(sb(), "resume")
        r_close = T.child(sb(), "close-indeterminate")
        refs_before = sb().refs()
    finally:
        h.kill()
    s2 = status()
    r = recover()
    s3 = status()
    rec = sb().sealed_record()
    return {"ok": s1 == "CONSUMED_COMPUTING" and r_wait["out"] == {"rc": 8} and "-> wait" in r_wait["stdout"]
            and r_res["out"] == {"rc": 2, "refused": "RESUME_REFUSED"}
            and r_close["out"] == {"rc": 2, "refused": "NO_DISCRETIONARY_ABANDONMENT"}
            and refs_before == refs0 and s2 == "CONSUMED_INTERRUPTED" and r["out"] == {"rc": 0}
            and s3 == "SEALED" and rec is not None and T.certified_bytes(rec) == base and one_marker(ch)
            and rec["lifecycle"]["attempt"] == 2,
            "states": [s1, s2, s3], "wait": r_wait["out"], "resume": r_res["out"], "close": r_close["out"],
            "recover": r["out"]}


def _ps_fails_for(H, pids: set):
    """In-process twin of the child harness knob `ps_fail_pids`: `ps` readings fail for these pids. Returns the undo."""
    real_start, real_cmd = H.process_start, H.process_command_sha256
    H.process_start = lambda pid, text=None: None if int(pid) in pids else real_start(pid, text)
    H.process_command_sha256 = lambda pid, text=None: None if int(pid) in pids else real_cmd(pid, text)

    def undo():
        H.process_start, H.process_command_sha256 = real_start, real_cmd
    return undo


def t_computing_ps_failure_not_interrupted():
    """Liveness delta (REVIEW_IMPLEMENTATION_MBS308_DELTA_R3 s3), the classifier's CONSUMED_COMPUTING test: the
    journal's recorded process is a LIVE helper for which `ps` fails (planted with the child knob ps_fail_pids). Its
    identity is UNKNOWN, never dead, so the state is CONSUMED_COMPUTING, recover waits (exit 8) and resume refuses,
    with no ref moved. Once the helper is gone (positive evidence of death, whatever `ps` does) the state is
    CONSUMED_INTERRUPTED and recover resumes and seals the uninterrupted bytes."""
    base = baseline()
    ch = fresh()
    h = T.Helper(300)
    try:
        ident = host().identity(h.p.pid)
        undo = _ps_fails_for(host(), {h.p.pid})              # control: the planted failure reads UNKNOWN, not DEAD
        try:
            planted = host().identity_state(ident)
        finally:
            undo()
        plant_computing(ch, ident)
        bad = {"ps_fail_pids": [h.p.pid]}
        refs0 = sb().refs()
        s1 = status(**bad)
        r_wait = recover(**bad)
        r_res = T.child(sb(), "resume", bad)
        refs_before = sb().refs()
    finally:
        h.kill()
    s2 = status(**bad)
    r = recover(**bad)
    s3 = status()
    rec = sb().sealed_record()
    complete = all(ident.get(k) for k in ("pid", "start_time", "boot_uuid", "command_sha256"))
    return {"ok": complete and planted == "UNKNOWN" and s1 == "CONSUMED_COMPUTING" and r_wait["out"] == {"rc": 8}
            and "-> wait" in r_wait["stdout"] and r_res["out"] == {"rc": 2, "refused": "RESUME_REFUSED"}
            and refs_before == refs0 and s2 == "CONSUMED_INTERRUPTED" and r["out"] == {"rc": 0} and s3 == "SEALED"
            and rec is not None and T.certified_bytes(rec) == base and one_marker(ch)
            and rec["lifecycle"]["attempt"] == 2,
            "planted_identity_state": planted, "states": [s1, s2, s3], "wait": r_wait["out"], "resume": r_res["out"],
            "recover": r["out"]}


def t_reboot():
    """A simulated reboot: the recorded process is alive, but the classifier's boot UUID differs -> INTERRUPTED."""
    ch = fresh()
    h = T.Helper(300)
    other = "00000000-0000-4000-8000-000000000000"
    try:
        plant_computing(ch, host().identity(h.p.pid))
        same = status()
        rebooted = status(boot_uuid=other)
        r = recover(boot_uuid=other)
    finally:
        h.kill()
    return {"ok": same == "CONSUMED_COMPUTING" and rebooted == "CONSUMED_INTERRUPTED" and r["out"] == {"rc": 0}
            and status() == "SEALED" and sealed_ok() and one_marker(ch),
            "same_boot": same, "other_boot": rebooted, "recover": r["out"]}


def t_platform_mismatch_at_resume():
    """DR2 (b): after an interruption, a different OS build (planted in the classifier's platform input) makes the run
    CONSUMED_UNRECORDED and recover closes it INDETERMINATE -- never a mixed-platform resume; the same build resumes."""
    ch = fresh()
    crash("F3", at=4)
    names = sb().ckpt_names()
    other = {"platform_override": {"os_build": "25Z999"}}
    c = classify(**other)
    before = counts()
    r = recover(**other)
    s = status(**other)
    rec = sb().sealed_record()
    no_compute = counts() == before and all(before.get(n) == 1 for n in names)
    marker_ok = one_marker(ch)
    ch2 = fresh()
    crash("F3", at=4)
    same = status()
    return {"ok": c["state"] == "CONSUMED_UNRECORDED" and "PLATFORM_PIN_MISMATCH" in c["why"]
            and "-> close-indeterminate" in r["stdout"] and s == "INDETERMINATE" and rec is not None
            and rec["status"] == "INDETERMINATE_CLOSED" and no_compute and marker_ok
            and same == "CONSUMED_INTERRUPTED" and bool(ch2),
            "classified": c["why"], "recover": r["out"], "final": s, "same_platform": same}


def t_result_durable_unsealed():
    ch = fresh()
    c = crash("F8", how="exit")
    s1 = status()
    n0 = sum(counts().values())
    r = recover()
    return {"ok": c["rc"] == 86 and s1 == "RESULT_DURABLE_UNSEALED" and "-> seal-only" in r["stdout"]
            and r["out"] == {"rc": 0} and status() == "SEALED" and sealed_ok() and sum(counts().values()) == n0
            and one_marker(ch), "status": s1, "recover": r["out"]}


def t_pending_result():
    ch = fresh()
    c = crash("F10", how="kill")
    s1 = status()
    n0 = sum(counts().values())
    r = recover()
    return {"ok": c["signal"] == 9 and s1 == "PENDING_RESULT" and "-> seal-only" in r["stdout"]
            and status() == "SEALED" and sealed_ok() and sum(counts().values()) == n0 and one_marker(ch),
            "status": s1, "recover": r["out"]}


def t_sealed_materialize():
    ch = fresh()
    r0 = T.child(sb(), "execute")
    raw = sb().sealed_raw()
    sb().materialized().unlink()
    s1 = status()
    r = recover()
    again = T.child(sb(), "execute")
    return {"ok": r0["out"] == {"rc": 0} and s1 == "SEALED" and "-> materialize" in r["stdout"]
            and sb().materialized().read_bytes() == raw and again["out"] == {"rc": 2, "refused": "CONSUMED"}
            and one_marker(ch), "recover": r["out"], "rerun": again["out"]}


def t_unrecorded_no_journal_then_indeterminate():
    """Marker, no journal -> CONSUMED_UNRECORDED -> recover seals the value-free INDETERMINATE record -> INDETERMINATE;
    nothing computed; execute / resume refuse afterwards."""
    ch = fresh()
    assert store().cas_ref(T.PREFIX + "target-consumed", ch["grant"], None)
    c1 = classify()
    r = recover()
    s2 = status()
    rec = sb().sealed_record()
    again = T.child(sb(), "execute")
    res = T.child(sb(), "resume")
    value_free = rec is not None and "target" not in rec and rec["status"] == "INDETERMINATE_CLOSED" and \
        rec["mechanical_outcome"] == "CELL308_EXECUTION_INDETERMINATE" and rec.get("value_free") is True
    return {"ok": c1["state"] == "CONSUMED_UNRECORDED" and "NO_JOURNAL" in c1["why"]
            and "-> close-indeterminate" in r["stdout"] and r["out"] == {"rc": 5} and s2 == "INDETERMINATE"
            and value_free and counts() == {} and again["out"] == {"rc": 2, "refused": "CONSUMED"}
            and res["out"] == {"rc": 2, "refused": "RESUME_REFUSED"} and one_marker(ch),
            "classified": c1["why"], "recover": r["out"], "after": [s2, again["out"], res["out"]]}


def t_unrecorded_journal_invalid():
    ch = fresh()
    st = store()
    assert st.cas_ref(T.PREFIX + "target-consumed", ch["grant"], None)
    assert st.cas_ref(T.PREFIX + "journal", st.put_blob(b"not a journal\n"), None)
    c = classify()
    return {"ok": c["state"] == "CONSUMED_UNRECORDED" and "JOURNAL_INVALID" in c["why"], "classified": c["why"]}


def t_budget_exhausted():
    """Three resumes at most: attempt 4 dead -> UNRECORDED; attempt 3 dead -> INTERRUPTED (planted journals)."""
    out = {}
    for att in (3, 4):
        ch = fresh()
        plant_computing(ch, dead_identity(), attempt=att)
        out[att] = classify()
    return {"ok": out[3]["state"] == "CONSUMED_INTERRUPTED" and out[4]["state"] == "CONSUMED_UNRECORDED"
            and "RESUME_BUDGET_EXHAUSTED" in out[4]["why"], "attempt3": out[3]["state"], "attempt4": out[4]["why"]}


def t_budget_real_resumes():
    """execute + three resumes, each killed after 3 new checkpoints -> CONSUMED_UNRECORDED -> INDETERMINATE; no verified
    checkpoint was ever recomputed."""
    ch = fresh()
    runs = [crash("F3", at=3)]
    states = [status()]
    served_recomputed = []
    for _ in range(3):
        names0, c0 = sb().ckpt_names(), counts()
        runs.append(T.child(sb(), "resume", {"fault": {"F3": {"at": 3, "how": "kill"}}}))
        c1 = counts()
        served_recomputed += [n for n in names0 if c1.get(n, 0) != c0.get(n, 0)]
        states.append(status())
    names = sb().ckpt_names()
    r = recover()
    rec = sb().sealed_record()
    return {"ok": all(x["signal"] == 9 for x in runs) and states == ["CONSUMED_INTERRUPTED"] * 3 +
            ["CONSUMED_UNRECORDED"] and len(names) == 12 and not served_recomputed
            and "-> close-indeterminate" in r["stdout"] and rec is not None
            and rec["status"] == "INDETERMINATE_CLOSED" and one_marker(ch),
            "states": states, "checkpoints": len(names), "recover": r["out"]}


def t_deadline():
    out = {}
    for days in (6, 8):
        ch = fresh()
        t = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days)).strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ")
        plant_computing(ch, dead_identity(), marker_utc=t)
        out[days] = classify()
    return {"ok": out[6]["state"] == "CONSUMED_INTERRUPTED" and out[8]["state"] == "CONSUMED_UNRECORDED"
            and "DEADLINE_PASSED" in out[8]["why"], "6d": out[6]["state"], "8d": out[8]["why"]}


def t_ckpt_tree_inconsistent():
    """The checkpoint tree recorded in the journal at the last attempt start must still be contained in the ckpt ref."""
    fresh()
    crash("F3", at=5)
    T.child(sb(), "resume", {"fault": {"F3": {"at": 2, "how": "kill"}}})
    st = store()
    tree = st.rev(T.PREFIX + "ckpt")
    ent = st.ls_tree(tree)
    recorded = st.ls_tree(S().Journal.read(st)[1]["ckpt_tree"])
    ent.pop(sorted(recorded)[0])                      # drop a checkpoint the journal recorded at the attempt start
    smaller = st.mktree(ent)
    assert st.cas_ref(T.PREFIX + "ckpt", smaller, tree)
    c = classify()
    return {"ok": c["state"] == "CONSUMED_UNRECORDED" and "CKPT_TREE_INCONSISTENT" in c["why"], "classified": c["why"]}


def _plant_ckpt(variant: str):
    """Replace ONE checkpoint (the first entry) by a variant of itself that breaks exactly one binding (MBS-9 iii);
    returns the replaced name. Synthetic sandbox checkpoints only."""
    Sm = S()
    st = store()
    tree = st.rev(T.PREFIX + "ckpt")
    ent = st.ls_tree(tree)
    names = sorted(ent)
    name = names[0]
    good = json.loads(st.get_blob(ent[name]))
    good.pop("self_sha256")
    bad = dict(good)
    if variant == "wrong_grant":
        bad["grant_commit"] = "f" * 40
    elif variant == "wrong_driver":
        bad["driver_sha256"] = "0" * 64
    elif variant == "future_seq":
        bad["journal_seq"] = 10 ** 6
    elif variant == "other_attempt":
        bad["attempt"] = 7
    elif variant == "wrong_platform":
        bad["platform_sha256"] = Sm.sha(b"another platform")
    elif variant == "wrong_record_hash":
        bad["record_sha256"] = "0" * 64
    elif variant == "job_swap":                  # job B's checkpoint served under job A's name
        other = json.loads(st.get_blob(ent[names[1]]))
        other.pop("self_sha256")
        bad = other
    else:
        raise ValueError(variant)
    ent[name] = st.put_blob(Sm.canon_signed(bad))
    new = st.mktree(ent)
    assert st.cas_ref(T.PREFIX + "ckpt", new, tree)
    return name


def _binding_case(variant: str) -> dict:
    """A checkpoint that breaks one binding is never served: resume recomputes exactly that job (and no verified one);
    the sealed bytes equal the uninterrupted run's."""
    base = baseline()
    ch = fresh()
    crash("F3", at=5)
    name = _plant_ckpt(variant)
    before = sb().ckpt_names()
    c0 = counts()
    r = recover()
    c = counts()
    good = [n for n in before if n != name]
    rec = sb().sealed_record()
    return {"ok": r["out"] == {"rc": 0} and status() == "SEALED" and sealed_ok() and c.get(name) == c0.get(name, 0) + 1
            and all(c.get(n) == 1 for n in good) and rec["lifecycle"]["checkpoints_rejected"] == [name]
            and sorted(rec["lifecycle"]["stage1_context"]["served"]) == sorted(good)
            and T.certified_bytes(rec) == base and one_marker(ch),
            "variant": variant, "rejected": rec["lifecycle"]["checkpoints_rejected"]}


def t_ckpt_wrong_grant():
    return _binding_case("wrong_grant")


def t_ckpt_wrong_driver():
    return _binding_case("wrong_driver")


def t_ckpt_future_seq():
    return _binding_case("future_seq")


def t_ckpt_other_attempt():
    return _binding_case("other_attempt")


def t_ckpt_wrong_platform():
    return _binding_case("wrong_platform")


def t_ckpt_wrong_record_hash():
    return _binding_case("wrong_record_hash")


def t_ckpt_job_swap():
    return _binding_case("job_swap")


def t_two_consecutive_failures():
    """The same job's checkpoint fails verification a second time in a row -> resume stops WITHOUT computing ->
    CONSUMED_UNRECORDED -> recover seals INDETERMINATE."""
    ch = fresh()
    crash("F3", at=5)
    name = _plant_ckpt("wrong_grant")
    Sm = S()
    st = store()
    jid, jrec = Sm.Journal.read(st)
    Sm.Journal(st, jid, jrec).advance(ckpt_failures={name: 1})
    c_before = counts()
    s1 = status()
    r = recover()
    s2 = classify()
    r2 = recover()
    return {"ok": s1 == "CONSUMED_INTERRUPTED" and r["out"] == {"rc": 6} and counts() == c_before
            and s2["state"] == "CONSUMED_UNRECORDED" and "CKPT_CONSECUTIVE_FAILURES" in s2["why"]
            and r2["out"] == {"rc": 5} and status() == "INDETERMINATE" and one_marker(ch),
            "resume": r["out"], "then": s2["why"], "close": r2["out"]}


def t_ckpt_never_read_after_terminal():
    """MBS-4: after the seal, the checkpoint tree is never read again (Checkpointer.verified_records refuses); the
    checkpoints stay (never deleted), recorded by count and tree hash only."""
    fresh()
    r = T.child(sb(), "execute")
    Sm = S()
    st = store()
    camp = Sm.Campaign(st, T.NS_REL + "/evidence/execution/MBS308_CELL308_RESULT.json",
                       T.NS_REL + "/authorization/MBS308_GRANT.json")
    jid, jrec = Sm.Journal.read(st)
    ck = Sm.Checkpointer(st, Sm.Journal(st, jid, jrec), "x" * 40, "y" * 64, campaign=camp)
    try:
        ck.verified_records(attempts={1: 2})
        refused = False
    except Sm.StateError as e:
        refused = e.code == "CKPT_TERMINAL"
    return {"ok": r["out"] == {"rc": 0} and refused and len(sb().ckpt_names()) == 18, "refused": refused}


def t_no_in_run_observation():
    """MBS-3: execute / resume print nothing per job before the seal; the durable host log carries host events only;
    the journal carries state transitions only (its length does not grow with the number of jobs)."""
    import re
    fresh()
    runs = [T.child(sb(), "execute", {"fault": {"F3": {"at": 6, "how": "kill"}}}), recover()]
    allowed = re.compile(r"^(MBS308 (SEALED|RECOVER state|UNSEALED|NOTHING DURABLE|RESUME STOPPED|LOST OWNERSHIP)\b"
                         r"|\{\"rc\": -?\d+.*\}$)")
    jobre = re.compile(r"\b(RLR|C1B|C2B|VER)[.:]\d")
    lines = [ln for r in runs for ln in r["stdout"].splitlines() if ln.strip()]
    errs = [ln for r in runs for ln in r["stderr"].splitlines() if ln.strip()]
    bad_out = [ln for ln in lines if not allowed.match(ln)]
    bad_err = [ln for ln in errs if jobre.search(ln) or ("warn" not in ln.lower() and "semaphore" not in ln.lower())]
    Sm = S()
    st = store()
    chain, jid = 0, st.rev(T.PREFIX + "journal")
    while jid:
        chain += 1
        rec = json.loads(st.get_blob(jid))
        jid = rec.get("prev")
    host_log = st.host_log_read()
    return {"ok": not bad_out and not bad_err and status() == "SEALED" and chain <= 8
            and all(e.get("source") == "caffeinate_supervisor" for e in host_log) and len(host_log) >= 2,
            "bad_stdout": bad_out[:5], "bad_stderr": bad_err[:5], "journal_entries": chain, "host_log": len(host_log)}


def t_no_abandonment():
    ch = fresh()
    crash("F3", at=4)
    s = status()
    outs = {a: T.child(sb(), a)["out"] for a in ("close-indeterminate", "seal-only", "execute")}
    return {"ok": s == "CONSUMED_INTERRUPTED" and outs == {"close-indeterminate": {"rc": 2, "refused":
                                                                                   "NO_DISCRETIONARY_ABANDONMENT"},
                                                           "seal-only": {"rc": 2, "refused": "SEAL_ONLY"},
                                                           "execute": {"rc": 2, "refused": "CONSUMED"}}
            and status() == "CONSUMED_INTERRUPTED" and one_marker(ch), "refusals": outs}


def t_indeterminate_after_worker_death():
    """A worker death is an execution failure (MB r1 rule): sealed TARGET_EVALUATION_FAILED -> INDETERMINATE."""
    ch = fresh()
    r = T.child(sb(), "execute", {"worker_die": "RLR.1.4"})
    rec = sb().sealed_record()
    s = status()
    r2 = recover()
    return {"ok": r["out"] == {"rc": 5} and rec["status"] == "TARGET_EVALUATION_FAILED" and s == "INDETERMINATE"
            and "-> materialize" in r2["stdout"] and one_marker(ch) and "BrokenProcessPool" in rec["target"]["error"],
            "status": s, "sealed_status": rec["status"]}


def t_control_failed():
    ch = fresh()
    r = T.child(sb(), "execute", {"control_pass": False})
    rec = sb().sealed_record()
    s = status()
    again = T.child(sb(), "execute")
    return {"ok": r["out"] == {"rc": 3} and rec["status"] == "CONTROL_FAILED" and rec["target_evaluations"] == 0
            and T.PREFIX + "target-consumed" not in sb().refs() and s == "NO_TARGET_CONSUMED"
            and again["out"] == {"rc": 2, "refused": "CONSUMED"} and counts() == {},
            "run": r["out"], "rerun": again["out"], "chain": ch["grant"][:8]}


def t_grant_binds_every_owner_record():
    """Brief 54, part C1 (owner supplement 1, section 6; owner supplement 2, section 12): the grant's `user_ruling_s1`
    must be the index of ALL the user's complete owner records in fixed order (original, supplement 1, supplement 2),
    each with its research path, commit, byte length, sha256 and complete verbatim text, plus the index digest and
    reaffirms_c4. The real `check_grant` (through `execute`, in the sandbox) accepts exactly that, and refuses, with
    nothing consumed: one byte changed in any of the three texts (the entry's digest left as it was, and again with the
    entry made self-consistent, as a forger would), any one record missing, any one record alone, the two-record index
    that was complete before supplement 2, the records in another order (reversed, rotated, the supplements swapped), a
    record twice in place of another, a fourth record, a section-only excerpt of the original (sections 5 and 5-6 by
    their byte ranges) and an excerpt of supplement 2, the old single-text field, an added paraphrase key (in the field
    and in a record), reaffirms_c4 not true, a wrong index digest, and no ruling. The texts are read from the base
    store at their research commits."""
    import copy
    good = T.s1_ruling()
    want = T.s1_owner_records()
    rows_ok = [(r["record"], r["path"], r["commit"], r["bytes"], r["sha256"]) for r in good["records"]] == \
        [tuple(w) for w in want] and len(want) == 3 and \
        [w[0] for w in want] == ["original", "supplement_1", "supplement_2"]
    if not rows_ok:                                 # the planted controls below index the three records
        return {"ok": False, "rows_ok": False, "records": [w[0] for w in want]}

    def flip(ur, i, reindex):
        u = copy.deepcopy(ur)
        t = u["records"][i]["verbatim"]
        k = len(t) // 2
        u["records"][i]["verbatim"] = t[:k] + ("x" if t[k] != "x" else "y") + t[k + 1:]
        return T.s1_reindex(u) if reindex else u

    def excerpt(lo, hi, i=0):
        u = copy.deepcopy(good)
        raw = u["records"][i]["verbatim"].encode()
        u["records"][i]["verbatim"] = raw[lo:hi].decode()
        return T.s1_reindex(u)

    def pick(*idx):                                 # the records idx, in that order, as a self-consistent index
        return T.s1_reindex(dict(copy.deepcopy(good), records=[copy.deepcopy(good["records"][i]) for i in idx]))
    old_style = {"verbatim": good["records"][0]["verbatim"], "sha256": good["records"][0]["sha256"],
                 "reaffirms_c4": True}
    extra_rec = copy.deepcopy(good)
    extra_rec["records"][1]["summary"] = "planted paraphrase"
    fourth = copy.deepcopy(good)
    fourth["records"].append(dict(copy.deepcopy(good["records"][2]), record="supplement_3"))
    n2 = good["records"][2]["bytes"]
    planted = {
        "byte_changed_in_original": flip(good, 0, False),
        "byte_changed_in_supplement_1": flip(good, 1, False),
        "byte_changed_in_supplement_2": flip(good, 2, False),
        "byte_changed_in_original_self_consistent": flip(good, 0, True),
        "byte_changed_in_supplement_1_self_consistent": flip(good, 1, True),
        "byte_changed_in_supplement_2_self_consistent": flip(good, 2, True),
        "original_missing": pick(1, 2),
        "supplement_1_missing": pick(0, 2),
        "supplement_2_missing_the_index_before_it": pick(0, 1),
        "original_alone": pick(0),
        "supplement_1_alone": pick(1),
        "supplement_2_alone": pick(2),
        "records_reversed": pick(2, 1, 0),
        "records_rotated": pick(1, 2, 0),
        "supplements_swapped": pick(0, 2, 1),
        "supplement_1_twice_in_place_of_supplement_2": pick(0, 1, 1),
        "a_fourth_record": T.s1_reindex(fourth),
        "section_5_excerpt_only": excerpt(3624, 5006),
        "sections_5_6_excerpt_only": excerpt(3624, 5736),
        "supplement_2_excerpt_only": excerpt(0, n2 // 2, 2),
        "old_single_text_field": old_style,
        "paraphrase_key_in_field": dict(copy.deepcopy(good), summary="planted paraphrase"),
        "paraphrase_key_in_record": extra_rec,
        "reaffirms_c4_false": dict(copy.deepcopy(good), reaffirms_c4=False),
        "wrong_index_digest": dict(copy.deepcopy(good), index_sha256="0" * 64),
        "no_ruling": None,
    }
    rows = {}
    for name, ur in planted.items():
        sb().grant_chain(ruling=ur if ur is not None else False)
        r = T.child(sb(), "execute")
        rows[name] = r["out"] == {"rc": 2, "refused": "GRANT_INVALID"} and \
            "every complete owner record" in (r["detail"] or "") and sb().refs() == {} and \
            sb().sealed_record() is None
    # the two excerpts are exactly the ranges R2 (section 5) and R3 (sections 5-6) of the conformance review
    # (REVIEW_OWNER_DECISION_CONFORMANCE_MBS308 section 1.3: lengths 1382 and 2112 and their sha256)
    ex5, ex56 = excerpt(3624, 5006)["records"][0], excerpt(3624, 5736)["records"][0]
    excerpt_is_real = (ex5["bytes"], ex5["sha256"]) == (
        1382, "a04a0255fe19d5368eb4483a9d560c6ba25ac98c8139fd618c86efd700866e9d") and \
        (ex56["bytes"], ex56["sha256"]) == (2112, "ff2878dae97ba1df8b6673244d8ae2d4f0bb4626c2059def54b0e6904ecdb56c")
    ch = sb().grant_chain()                                 # the three complete records: accepted, the run seals
    r = T.child(sb(), "execute")
    rec = sb().sealed_record() or {}
    s1 = (rec.get("grant") or {}).get("user_ruling_s1") or {}
    accepted = r["out"] == {"rc": 0} and rec.get("status") == "TARGET_EVALUATED" and one_marker(ch) and \
        s1.get("index_sha256") == good["index_sha256"] and \
        [x["sha256"] for x in s1.get("records", [])] == [w[4] for w in want]
    return {"ok": rows_ok and all(rows.values()) and len(rows) == 26 and excerpt_is_real and accepted,
            "refused": rows, "accepted": accepted, "rows_ok": rows_ok, "excerpt_is_real": excerpt_is_real,
            "run": r["out"]}


def t_execute_refuses_outside_launchd():
    """execute outside the launchd job (the real check, not stubbed) refuses before the marker; nothing consumed."""
    fresh()
    r = T.child(sb(), "execute", {"real_launch_check": True})
    return {"ok": r["out"] == {"rc": 2, "refused": "NOT_LAUNCHED_BY_LAUNCHER"} and sb().refs().get(
        T.PREFIX + "target-consumed") is None and counts() == {}, "run": r["out"]}


def t_marker_cas():
    """Both executes passed check_not_evaluated (a race): the marker CAS from zero must refuse the second."""
    ch = fresh()
    assert store().cas_ref(T.PREFIX + "target-consumed", ch["grant"], None)
    s0 = classify()
    r = T.child(sb(), "execute", {"skip_not_evaluated": True})
    s1 = classify()
    return {"ok": r["out"] == {"rc": 2, "refused": "CONSUMED"} and counts() == {} and one_marker(ch)
            and s0["state"] == s1["state"] == "CONSUMED_UNRECORDED" and "ABORTED_INTENT" in s1["why"],
            "run": r["out"], "before": s0["why"], "after": s1["why"]}


def t_journal_cas():
    fresh()
    Sm = S()
    st = store()
    j1 = Sm.Journal(st, None, None)
    j1.advance(state="ARMING", attempt=1)
    jid, jrec = Sm.Journal.read(st)
    a, b = Sm.Journal(st, jid, jrec), Sm.Journal(st, jid, jrec)
    a.advance(state="COMPUTING")
    try:
        b.advance(state="COMPUTING")
        conflict = False
    except Sm.JournalConflict:
        conflict = True
    jid2, jrec2 = Sm.Journal.read(st)
    return {"ok": conflict and jrec2["seq"] == 2 and jrec2["prev"] == jid, "conflict_raised": conflict}


def t_stale_pidfile():
    Sm = S()
    st = store()
    fresh()
    st.spool(create=True)
    h = T.Helper(120)
    try:
        live = host().identity(h.p.pid)
        out = {}
        for tag, ident in (("dead", dead_identity()), ("wrong_start", dict(live, start_time="Thu Jan  1 00:00:00 1970")),
                           ("wrong_cmd", dict(live, command_sha256="0" * 64)), ("wrong_boot", dict(live, boot_uuid="X")),
                           ("exact", live)):
            (st.spool() / Sm.PIDFILE).write_text(json.dumps({"identity": ident}))
            out[tag] = Sm.read_pidfile(st)[1]
        (st.spool() / Sm.PIDFILE).unlink()
        out["absent"] = Sm.read_pidfile(st)[1]
    finally:
        h.kill()
    return {"ok": out == {"dead": "STALE", "wrong_start": "STALE", "wrong_cmd": "STALE", "wrong_boot": "STALE",
                          "exact": "LIVE", "absent": "ABSENT"}, "states": out}


def t_gc8_mbr1_state():
    """GC-8: MB r1's recorded state exactly; an extra MB r1 ref, an MB r1 pending ref, an emergency file or an
    NSF/evidence path each refuse (before anything is consumed)."""
    out = {}
    plants = {
        "extra_ref": lambda: T.g(sb().root, "update-ref", "refs/p5y-k5-cell308-mb-r1/extra", T.MBR1_TARGET),
        "pending_ref": lambda: T.g(sb().root, "update-ref", "refs/p5y-k5-cell308-mb-r1/pending-result",
                                   T.MBR1_TARGET),
        "marker_moved": lambda: T.g(sb().root, "update-ref", T.MBR1_MARKER, sb().freeze),
        "emergency_file": lambda: (sb().mbr1_git_dir / "mb308-cell308-emergency-result.json").write_text("{}"),
        "evidence_path": lambda: sb().p(T.NSF_REL + "/evidence").mkdir(parents=True),
    }
    for tag, plant in plants.items():
        fresh()
        plant()
        r = T.child(sb(), "execute")
        out[tag] = r["out"]
        if sb().p(T.NSF_REL + "/evidence").exists():
            sb().p(T.NSF_REL + "/evidence").rmdir()
    fresh()
    ok_run = T.child(sb(), "execute")["out"]
    return {"ok": all(v == {"rc": 2, "refused": "MBR1_STATE"} for v in out.values()) and ok_run == {"rc": 0}
            and counts() != {}, "refusals": out, "unplanted": ok_run}


# ====================================================================== R4: start gates, pins, GC-8 (behavioural)
GOOD_HOST = {"batt": "Now drawing from 'AC Power'\n", "pmset": " lowpowermode         0\n",
             "thermal": "com.apple.system.thermalpressurelevel 0\n", "free": 10 * 2 ** 30, "memory": "1\n",
             "boot": "A7417159-025C-461F-8BF8-3F9C7F3C58CB\n"}
SU_OFF = {"AutomaticallyInstallMacOSUpdates": "0", "AutomaticDownload": "1", "CriticalUpdateInstall": "0",
          "ConfigDataInstall": "1"}


def _vm(free_bytes: int) -> str:
    pages = free_bytes // 16384
    return ("Mach Virtual Memory Statistics: (page size of 16384 bytes)\n"
            f"Pages free:                               {pages}.\nPages active:                  1000.\n"
            "Pages inactive:                                0.\nPages speculative:                0.\n"
            "Pages throttled:                                0.\nPages wired down:            1000.\n"
            "Pages purgeable:                                0.\n")


PS_QUIET = "    1     0   0.4 /sbin/launchd\n  300     1   1.2 /usr/libexec/somed\n"


def _gates(vm: str, ps: str) -> dict:
    return T.child(sb(), "host_gates", {"planted": {"host": GOOD_HOST, "su": SU_OFF, "vm_stat": vm, "ps": ps}})["out"]


def rule_constants() -> dict:
    """The five rule constants the driver UNDER TEST carries, read exactly from its text (brief 54): the provisional
    values before the apply step, the rule outputs after it. The start-gate tests plant their readings relative to
    these, so they hold for whatever the driver carries."""
    S()
    import mbs308_derive as DV
    return DV.driver_constants(sb().driver.read_text())


def big_memory() -> int:
    return max(8 * 2 ** 30, 2 * rule_constants()["FREE_MEM_MIN_BYTES"])


def t_gc10_start_gates():
    """The DRIVER's GC-10 start gates on planted readings: free memory (vm_stat) and host exclusivity (ps); each failing
    reading fails exactly its gate and refuses start; an allow-listed or own-child busy process does not."""
    fresh()
    big, small = big_memory(), 2 ** 29                      # far from the driver's threshold on either side (the
    #                                                         rule's floor is 2 GiB, so 0.5 GiB is always below it)
    busy_other = PS_QUIET + " 4242     1  90.0 /Applications/Busy.app/Contents/MacOS/Busy\n"
    busy_ui = PS_QUIET + " 4243     1  90.0 /System/Library/PrivateFrameworks/SkyLight.framework/Resources/WindowServer\n"
    busy_child = PS_QUIET + " 4244 {SELF}  90.0 /usr/bin/python3\n"
    out = {"good": _gates(_vm(big), PS_QUIET), "low_memory": _gates(_vm(small), PS_QUIET),
           "vm_unreadable": _gates("garbage\n", PS_QUIET), "busy_other": _gates(_vm(big), busy_other),
           "busy_allow_listed": _gates(_vm(big), busy_ui), "busy_own_child": _gates(_vm(big), busy_child)}
    ok = out["good"]["rc"] == 0 and all(out["good"]["gates"].values()) \
        and out["low_memory"] == {"rc": 2, "refused": "HOST_PREFLIGHT", "detail": "HOST_PREFLIGHT: free_memory_ge_min"} \
        and out["vm_unreadable"]["detail"] == "HOST_PREFLIGHT: free_memory_ge_min" \
        and out["busy_other"] == {"rc": 2, "refused": "HOST_PREFLIGHT", "detail": "HOST_PREFLIGHT: host_exclusive"} \
        and out["busy_allow_listed"]["rc"] == 0 and out["busy_own_child"]["rc"] == 0
    return {"ok": ok, "cases": {k: v.get("refused", "PASS") for k, v in out.items()}}


# R3: the four Apple OS daemons of CONSTANTS_RATIFICATION_MBS308 item 16 (H3 readings; paths as the ratifier's H3/H4)
RATIFIED_DAEMONS = {
    "spotlightknowledged.updater": "/usr/libexec/spotlightknowledged.updater",
    "cloudd": "/System/Library/PrivateFrameworks/CloudKitDaemon.framework/Support/cloudd",
    "BackgroundShortcutRunner": "/System/Library/PrivateFrameworks/WorkflowKit.framework/XPCServices/"
                                "BackgroundShortcutRunner.xpc/Contents/MacOS/BackgroundShortcutRunner",
    "modelcatalogd": "/System/Library/PrivateFrameworks/ModelCatalogRuntime.framework/Support/modelcatalogd",
}


def t_gc10_ratified_allow_list():
    """R3 (ratification item 16) and R-ALLOW: the DRIVER's exclusivity gate on planted ps readings passes each OS
    daemon the allow-list holds beyond the 39 names of the rejected build, above the threshold, one at a time and all
    together; the allow-list stays a list of names, so an OS daemon that is not on it still refuses start
    (host_exclusive). Before the apply step those additions are exactly the four ratified daemons (item 16, provisional);
    after it they are R-ALLOW's output, which by the rule always holds the two ratified daemons whose H3 readings exceed
    every value EXCL_CPU_PCT can take (spotlightknowledged.updater 70.3, BackgroundShortcutRunner 52.2)."""
    fresh()
    big = big_memory()
    allow = set(rule_constants()["EXCL_ALLOW"])
    added = sorted(allow & set(RATIFIED_DAEMONS))
    out = {}
    for i, name in enumerate(added):
        out[name] = _gates(_vm(big), PS_QUIET + f" {4300 + i}     1  70.0 {RATIFIED_DAEMONS[name]}\n")
    out["all_added"] = _gates(_vm(big), PS_QUIET + "".join(f" {4310 + i}     1  52.0 {RATIFIED_DAEMONS[n]}\n"
                                                           for i, n in enumerate(added)))
    out["unlisted_os_daemon"] = _gates(_vm(big), PS_QUIET + " 4320     1  70.0 /usr/libexec/notratifiedd\n")
    ok = {"spotlightknowledged.updater", "BackgroundShortcutRunner"} <= set(added) and \
        all(out[k]["rc"] == 0 and all(out[k]["gates"].values()) for k in (*added, "all_added")) \
        and out["unlisted_os_daemon"] == {"rc": 2, "refused": "HOST_PREFLIGHT", "detail": "HOST_PREFLIGHT: host_exclusive"}
    return {"ok": ok, "ratified_daemons_on_the_list": added,
            "cases": {k: v.get("refused", "PASS") for k, v in out.items()}}


PIN_OVERRIDE = {"pin_override": {"os_build": "25Z999"}}
RESEARCH_REL = "level4/closure_proofs/p5y_k5_tail_c2_closure/evidence/registry_c2/REGISTRY_C2.json"
SCIENCE_REL = T.NSF_REL + "/code/mb308_supply.py"


def _journal_attempt():
    rec = S().Journal.read(store())[1]
    return rec and rec.get("attempt")


def _restoring(rel: str):
    p = sb().p(rel)
    return p, p.read_bytes()


def _nothing_consumed() -> bool:
    return T.PREFIX + "target-consumed" not in sb().refs() and counts() == {}


def t_pins_execute_platform():
    fresh()
    r = T.child(sb(), "execute", PIN_OVERRIDE)
    return {"ok": r["out"] == {"rc": 2, "refused": "PLATFORM_PIN_MISMATCH"} and _nothing_consumed()
            and T.PREFIX + "journal" not in sb().refs(), "run": r["out"]}


def _resume_refusal(spec: dict, want: str, rel: str | None = None) -> dict:
    """After an interruption, a pin refusal at resume stops BEFORE the attempt counter moves: nothing is computed,
    the state stays CONSUMED_INTERRUPTED; with the pin restored, recover resumes and seals."""
    ch = fresh()
    crash("F3", at=4)
    before, att = counts(), _journal_attempt()
    keep = _restoring(rel) if rel else None
    try:
        r = recover(**spec)
    finally:
        if keep:
            keep[0].write_bytes(keep[1])
    s1, att1, c1 = status(), _journal_attempt(), counts()
    r2 = recover()
    return {"ok": r["out"] == {"rc": 2, "refused": want} and s1 == "CONSUMED_INTERRUPTED" and att1 == att == 1
            and c1 == before and r2["out"] == {"rc": 0} and status() == "SEALED" and sealed_ok() and one_marker(ch),
            "refusal": r["out"], "state_after": s1, "attempt_after": att1}


def t_pins_resume_platform():
    return _resume_refusal(PIN_OVERRIDE, "PLATFORM_PIN_MISMATCH")


def t_pins_execute_research():
    fresh()
    p, orig = _restoring(RESEARCH_REL)
    try:
        r = T.child(sb(), "execute", {"skip_clean": True, "tamper_after_import": RESEARCH_REL})
    finally:
        p.write_bytes(orig)
    return {"ok": r["out"] == {"rc": 2, "refused": "PIN_MISMATCH"} and _nothing_consumed(), "run": r["out"]}


def t_pins_resume_research():
    return _resume_refusal({"tamper_after_import": RESEARCH_REL}, "PIN_MISMATCH", RESEARCH_REL)


def t_pins_execute_science():
    fresh()
    p, orig = _restoring(SCIENCE_REL)
    try:
        r = T.child(sb(), "execute", {"skip_clean": True, "tamper_after_import": SCIENCE_REL})
    finally:
        p.write_bytes(orig)
    return {"ok": r["out"] == {"rc": 2, "refused": "SCIENCE_PIN_MISMATCH"} and _nothing_consumed(), "run": r["out"]}


def t_pins_resume_science():
    return _resume_refusal({"tamper_after_import": SCIENCE_REL}, "SCIENCE_PIN_MISMATCH", SCIENCE_REL)


def t_pins_science_fresh_process():
    """A science module changed BEFORE the driver starts: the driver refuses at import (SciencePinError), for execute
    and for recover after an interruption; nothing is consumed or computed; the state is unchanged."""
    fresh()
    p, orig = _restoring(SCIENCE_REL)
    try:
        p.write_bytes(orig + b"\n# planted\n")
        r1 = T.child(sb(), "execute")
    finally:
        p.write_bytes(orig)
    ok1 = r1["out"] is None and r1["rc"] not in (0, None) and "SciencePinError" in r1["stderr"] and _nothing_consumed()
    ch = fresh()
    crash("F3", at=4)
    before = counts()
    try:
        p.write_bytes(orig + b"\n# planted\n")
        r2 = recover()
    finally:
        p.write_bytes(orig)
    ok2 = r2["out"] is None and "SciencePinError" in r2["stderr"] and status() == "CONSUMED_INTERRUPTED" \
        and _journal_attempt() == 1 and counts() == before
    r3 = recover()
    return {"ok": ok1 and ok2 and r3["out"] == {"rc": 0} and sealed_ok() and one_marker(ch),
            "execute_rc": r1["rc"], "recover_rc": r2["rc"]}


def t_gc8_evidence_at_head_and_mbr1_branch():
    """GC-8: an NSF/evidence path committed at HEAD (absent from the worktree), or on MB r1's branch, refuses."""
    ev = T.NSF_REL + "/evidence/planted.txt"
    fresh()
    sb().write(ev, "planted\n")
    T.g(sb().root, "add", "-f", ev)
    T.g(sb().root, "commit", "-q", "-m", "sandbox: planted NSF/evidence at HEAD")
    sb().p(ev).unlink()
    sb().p(T.NSF_REL + "/evidence").rmdir()
    r1 = T.child(sb(), "execute")
    ok1 = r1["out"] == {"rc": 2, "refused": "MBR1_STATE"} and "HEAD holds an NSF/evidence path" in (r1["detail"] or "")
    fresh()
    env = dict(T.GENV, GIT_INDEX_FILE=str(sb().tmp / "planted.index"))
    run = lambda *a: subprocess.run(["/usr/bin/git", "-C", str(sb().root), *a], capture_output=True, text=True,  # noqa
                                    env=env, check=True).stdout.strip()
    try:
        blob = subprocess.run(["/usr/bin/git", "-C", str(sb().root), "hash-object", "-w", "--stdin"],
                              input="planted\n", capture_output=True, text=True, env=T.GENV, check=True).stdout.strip()
        run("read-tree", T.BASE)
        run("update-index", "--add", "--cacheinfo", f"100644,{blob},{ev}")
        c = run("commit-tree", run("write-tree"), "-p", T.BASE, "-m", "sandbox: MB r1 branch with NSF/evidence")
        T.g(sb().root, "branch", "-f", "p5y-k5-cell308-mb-r1", c)
        r2 = T.child(sb(), "execute")
    finally:
        T.g(sb().root, "branch", "-f", "p5y-k5-cell308-mb-r1", T.BASE)
    ok2 = r2["out"] == {"rc": 2, "refused": "MBR1_STATE"} and \
        "refs/heads/p5y-k5-cell308-mb-r1 holds an NSF/evidence path" in (r2["detail"] or "")
    return {"ok": ok1 and ok2 and _nothing_consumed(), "head": r1["detail"], "mbr1_branch": r2["detail"]}


def t_cas_ref_conflict_vs_infrastructure():
    """R1 (i), unit: a genuine CAS conflict returns False at once; a lockfile (the ref still holds the expected old
    value) is recorded and raises RefWriteError once the retries are spent; a lock that clears during the retry
    schedule is overcome."""
    import threading
    Sm = S()
    fresh()
    ref = T.PREFIX + "unit-test"
    st = Sm.Store(sb().root, "refs/heads/" + T.BRANCH)
    b1, b2 = st.put_blob(b"cas unit 1\n"), st.put_blob(b"cas unit 2\n")
    created = st.cas_ref(ref, b1, None) is True
    conflict = st.cas_ref(ref, b2, None) is False and st.cas_ref(ref, b2, b2) is False
    lk = sb().plant_lock(ref + ".lock")
    n0 = len(Sm.REF_WRITE_FAILURES)
    try:
        st.cas_ref(ref, b2, b1)
        infra = "NO_RAISE"
    except Sm.RefWriteError:
        infra = "RefWriteError"
    recorded = len(Sm.REF_WRITE_FAILURES) == n0 + 1 and Sm.REF_WRITE_FAILURES[-1]["lock_present"] is True
    st2 = Sm.Store(sb().root, "refs/heads/" + T.BRANCH, retry_delays=(0.8,))    # test-local schedule
    threading.Timer(0.2, lk.unlink).start()
    retried = st2.cas_ref(ref, b2, b1) is True and st.rev(ref) == b2
    return {"ok": created and conflict and infra == "RefWriteError" and recorded and retried,
            "created": created, "conflict": conflict, "infra": infra, "recorded": recorded, "retried": retried}


# ====================================================================== persistence contract and units
def t_persistence_contract():
    """Section 3: O_CREAT|O_EXCL|O_NOFOLLOW tmp, full write, fsync(fd) + F_FULLFSYNC, rename, dir fsync + F_FULLFSYNC,
    read-back verify (a corrupted read-back raises), a second write refuses, a stale tmp is renamed aside."""
    import fcntl
    Sm = S()
    fresh()
    st = store()
    data = Sm.serialize({"schema": Sm.RESULT_SCHEMA, "complete": True, "status": "TARGET_EVALUATED", "cell": 308,
                         "grant": {"grant_commit": "a" * 40}, "driver_sha256": "b" * 64, "n": {10: 1, 8: 2}})
    calls = []
    real = {"open": os.open, "fsync": os.fsync, "rename": os.rename, "fcntl": fcntl.fcntl}

    def w_open(path, flags, *a, **k):
        fd = real["open"](path, flags, *a, **k)
        calls.append(("open", str(path).rsplit("/", 1)[-1], flags, fd))
        return fd

    def w_fsync(fd):
        calls.append(("fsync", fd))
        return real["fsync"](fd)

    def w_rename(a, b, *x, **k):
        calls.append(("rename", str(a), str(b)))
        return real["rename"](a, b, *x, **k)

    def w_fcntl(fd, op, *a):
        calls.append(("fcntl", fd, op))
        return real["fcntl"](fd, op, *a)
    os.open, os.fsync, os.rename, fcntl.fcntl = w_open, w_fsync, w_rename, w_fcntl
    try:
        st.spool(create=True)
        (st.spool() / Sm.TMP_FILE).write_bytes(b"stale partial")
        info = st.spool_write_result(data)
    finally:
        os.open, os.fsync, os.rename, fcntl.fcntl = real["open"], real["fsync"], real["rename"], real["fcntl"]
    tmp_open = [c for c in calls if c[0] == "open" and c[1] == Sm.TMP_FILE]
    fd = tmp_open[0][3] if tmp_open else None
    want = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
    seq = [c[0] for c in calls if c[0] in ("fsync", "rename", "fcntl")]
    i_fs = next((i for i, c in enumerate(calls) if c == ("fsync", fd)), None)
    i_rn = next((i for i, c in enumerate(calls) if c[0] == "rename" and c[2] == Sm.RESULT_FILE), None)
    full_file = any(c[0] == "fcntl" and c[1] == fd and c[2] == fcntl.F_FULLFSYNC for c in calls[:i_rn or 0])
    dir_sync = i_rn is not None and any(c[0] == "fsync" for c in calls[i_rn + 1:])
    back_ok = (st.spool() / Sm.RESULT_FILE).read_bytes() == data
    stale_aside = any(n.startswith(Sm.TMP_FILE + ".rejected-") for n in os.listdir(st.spool()))
    try:
        st.spool_write_result(data)
        second = "NOT_REFUSED"
    except Sm.StateError as e:
        second = e.code
    (st.spool() / Sm.RESULT_FILE).unlink()
    orig = Sm.Store.spool_read
    Sm.Store.spool_read = lambda self, name: (orig(self, name) or b"")[:-3] + b"}\n"
    try:
        st.spool_write_result(data)
        corrupt = "NOT_DETECTED"
    except OSError:
        corrupt = "DETECTED"
    finally:
        Sm.Store.spool_read = orig
    try:
        st.spool_read(Sm.TMP_FILE)
        tmp_read = "READ"
    except Sm.StateError:
        tmp_read = "NEVER_READ"
    return {"ok": bool(tmp_open) and (tmp_open[0][2] & want) == want and i_fs is not None and i_rn is not None
            and i_fs < i_rn and full_file and dir_sync and back_ok and stale_aside and second == "SPOOL_RESULT_EXISTS"
            and corrupt == "DETECTED" and tmp_read == "NEVER_READ" and info["steps"][-1] == "read_back_verified",
            "sequence": seq, "second_write": second, "corrupt_read_back": corrupt, "tmp": tmp_read}


def t_verify_result_units():
    Sm = S()
    g, d = "a" * 40, "b" * 64
    rec = {"schema": Sm.RESULT_SCHEMA, "complete": True, "status": "TARGET_EVALUATED", "cell": 308,
           "grant": {"grant_commit": g}, "driver_sha256": d, "x": {10: "1/3", 8: "2/3"}}
    data = Sm.serialize(rec)
    body = json.loads(data)
    wrong_hash = data.replace(b'"1/3"', b'"1/4"')
    relayout = (json.dumps(body, sort_keys=True) + "\n").encode()
    out = {"good": Sm.verify_result(data, grant=g, driver_sha=d)[1],
           "wrong_hash": Sm.verify_result(wrong_hash, grant=g, driver_sha=d)[1],
           "relayout": Sm.verify_result(relayout, grant=g, driver_sha=d)[1],
           "grant": Sm.verify_result(data, grant="c" * 40, driver_sha=d)[1],
           "driver": Sm.verify_result(data, grant=g, driver_sha="e" * 64)[1],
           "incomplete": Sm.verify_result(Sm.serialize(dict(rec, complete=False)), grant=g, driver_sha=d)[1],
           "truncated": Sm.verify_result(data[:-20], grant=g, driver_sha=d)[1],
           "absent": Sm.verify_result(None, grant=g, driver_sha=d)[1]}
    return {"ok": out == {"good": "", "wrong_hash": "SELF_HASH_OR_LAYOUT", "relayout": "SELF_HASH_OR_LAYOUT",
                          "grant": "GRANT_BINDING", "driver": "DRIVER_BINDING", "incomplete": "NOT_COMPLETE",
                          "truncated": "SELF_HASH_OR_LAYOUT", "absent": "ABSENT"}, "reasons": out}


def t_enc_dec_lossless():
    from fractions import Fraction as F
    Sm = S()
    objs = [{"a": F(1, 3), "t": (1, F(2, 5), "x"), "d": {8: [1.5, -0.0, 1e-300], 10: None}, "$k": True},
            [(), {}, [], F(-7, 3)], {"nested": {(1, 2): {"deep": (F(1),)}}}]
    ok = True
    for o in objs:
        back = Sm.dec(json.loads(Sm.canon(Sm.enc(o))))
        ok = ok and back == o and repr(back) == repr(o)
    try:
        Sm.enc({"s": {1, 2}})
        refuses = False
    except TypeError:
        refuses = True
    return {"ok": ok and refuses, "roundtrip": ok, "refuses_unknown": refuses}


# ====================================================================== O-2 / O-3 (REVIEW_OPTIONB_LIVENESS_MBS308)
def _lock_files() -> dict:
    sp = sb().spool()
    names = sorted(os.listdir(sp)) if sp.is_dir() else []
    return {"asides": [n for n in names if n.startswith("recover.lock.rejected-stale-lock")],
            "staged": [n for n in names if n.startswith("recover.lock.staged-")],
            "lock": (sp / "recover.lock").read_bytes() if (sp / "recover.lock").exists() else None}


def _lock_state(Sm, st) -> str:
    raw = Sm.lock_read(st, "recover.lock")
    if raw is None:
        return "absent"
    try:
        return "complete" if isinstance(json.loads(raw).get("identity"), dict) else "incomplete"
    except (ValueError, AttributeError):
        return "incomplete"


def t_lock_record_complete_before_name():
    """O-2: a concurrent acquirer can never see the recover lock's name without its complete identity record. Every
    write of acquirer A is intercepted (the module's own _write_all); at each one the lock NAME is observed, and the
    first time it exists while A is still writing, a second acquirer B runs right there. Required: the name is never
    seen empty or partial, exactly one of A and B holds the lock, no lock was broken as stale (no set-aside file), no
    staged record is left, and the lock holds the holder's record. (Before the repair: A's O_EXCL name is empty during
    its write, B breaks it as "no recorded identity" and BOTH hold the lock.)"""
    fresh()
    Sm = S()
    st = store()
    st.spool(create=True)
    a, b = Sm.Lock(st), Sm.Lock(st)
    seen, res, flag = [], {}, {"in_b": False, "b_ran": False}
    real = Sm._write_all

    def intercepted(fd, data):
        if not flag["in_b"]:
            state = _lock_state(Sm, st)
            seen.append(state)
            if state != "absent" and not flag["b_ran"]:
                flag["in_b"] = flag["b_ran"] = True
                try:
                    b.acquire()
                    res["B"] = "TAKEN"
                except Sm.Locked as e:
                    res["B"] = e.code
                finally:
                    flag["in_b"] = False
        real(fd, data)
    Sm._write_all = intercepted
    try:
        try:
            a.acquire()
            res["A"] = "TAKEN"
        except Sm.Locked as e:
            res["A"] = e.code
    finally:
        Sm._write_all = real
    if not flag["b_ran"]:                     # the name never existed during A's writes: B comes after A
        try:
            b.acquire()
            res["B"] = "TAKEN"
        except Sm.Locked as e:
            res["B"] = e.code
    files = _lock_files()
    holders = [lk for lk in (a, b) if lk.held]
    holder_ok = len(holders) == 1 and files["lock"] is not None and \
        json.loads(files["lock"])["identity"]["pid"] == os.getpid()
    for lk in (a, b):
        lk.release()
    return {"ok": "incomplete" not in seen and sorted(res.values()) == ["LOCKED", "TAKEN"] and
            files["asides"] == [] and files["staged"] == [] and holder_ok and _lock_files()["lock"] is None,
            "observed_during_writes": seen, "results": res, "holders": len(holders),
            "asides": len(files["asides"]), "staged_left": len(files["staged"])}


def t_lock_race_put_back_one_name():
    """O-3: the LOCK_RACE put-back leaves the lock with ONE name. A stale lock (a dead holder) is being broken by A;
    between A's read and A's rename, B breaks the same stale lock and takes the lock (planted by intercepting A's
    rename). A moves B's fresh lock aside, sees it changed, puts it back and refuses LOCK_RACE. Required: the lock holds
    B's bytes with link count 1, A's set-aside name is gone (only B's set-aside copy of the stale lock remains, byte for
    byte), B's release removes the lock, and a later acquire takes it. (Before the repair: two links, B cannot release,
    every later acquire refuses LOCK_RACE.)"""
    fresh()
    Sm = S()
    st = store()
    sp = st.spool(create=True)
    stale = Sm.canon({"identity": dead_identity(), "utc": Sm.utc()})
    (sp / "recover.lock").write_bytes(stale)
    a, b = Sm.Lock(st), Sm.Lock(st)
    real_rename, flag, res = os.rename, {"done": False}, {}

    def intercepted(src, dst, *args, **kw):
        if not flag["done"] and str(src) == "recover.lock" and str(dst).startswith("recover.lock.rejected-stale"):
            flag["done"] = True
            b.acquire()                            # B breaks the same stale lock and takes it first
            res["B"] = "TAKEN"
        return real_rename(src, dst, *args, **kw)
    os.rename = intercepted
    try:
        try:
            a.acquire()
            res["A"] = "TAKEN"
        except Sm.Locked as e:
            res["A"] = e.code
    finally:
        os.rename = real_rename
    files = _lock_files()
    lock = sp / "recover.lock"
    b_bytes = files["lock"]
    nlink = os.stat(lock).st_nlink if lock.exists() else None
    aside_bytes = [(sp / n).read_bytes() for n in files["asides"]]
    b_record = b_bytes is not None and json.loads(b_bytes)["identity"]["pid"] == os.getpid()
    b.release()
    released = not lock.exists()
    c = Sm.Lock(st)
    try:
        c.acquire()
        later = "TAKEN"
    except Sm.Locked as e:
        later = e.code
    c.release()
    return {"ok": res == {"B": "TAKEN", "A": "LOCK_RACE"} and b_record and nlink == 1 and aside_bytes == [stale]
            and released and later == "TAKEN" and files["staged"] == [],
            "results": res, "link_count_after_put_back": nlink, "asides": len(aside_bytes),
            "released_by_b": released, "later_acquire": later}


def t_lock_second_name_not_wedged():
    """O-3 (crash windows): a lock that carries a second name (a crash between Lock.acquire's link and the unlink of
    its staged record, or inside a put-back) is still READ: a dead holder's two-name lock is broken (moved aside once)
    and the lock taken; a live holder's two-name lock is refused LOCKED (never broken, never LOCK_RACE)."""
    fresh()
    Sm = S()
    st = store()
    sp = st.spool(create=True)
    out = {}
    for case in ("dead_holder", "live_holder"):
        for n in os.listdir(sp):
            if n.startswith("recover.lock"):
                os.unlink(sp / n)
        h = T.Helper(60) if case == "live_holder" else None
        try:
            ident = host().identity(h.p.pid) if h is not None else dead_identity()
            raw = Sm.canon({"identity": ident, "utc": Sm.utc()})
            (sp / "recover.lock.staged-424242-abcdef").write_bytes(raw)
            os.link(sp / "recover.lock.staged-424242-abcdef", sp / "recover.lock")      # two names, as a crash leaves
            lk = Sm.Lock(st)
            try:
                lk.acquire()
                out[case] = "TAKEN"
            except Sm.Locked as e:
                out[case] = e.code
            out[case + "_asides"] = len(_lock_files()["asides"])
            out[case + "_lock_intact"] = (sp / "recover.lock").exists() and \
                (sp / "recover.lock").read_bytes() == raw
            lk.release()
        finally:
            if h is not None:
                h.kill()
    return {"ok": out["dead_holder"] == "TAKEN" and out["dead_holder_asides"] == 1 and
            out["live_holder"] == "LOCKED" and out["live_holder_asides"] == 0 and out["live_holder_lock_intact"],
            "cases": out}


# ====================================================================== R-MEM inputs of the decoy record (brief 50, task 3)
def t_decoy_records_rmem_inputs():
    """main()'s REAL decoy branch (a sandbox child; the synthetic evaluator stands in for decoy(): MB r1's unchanged
    stage1 over fake job keys, each job holding 64 MB for 1 s) records R-MEM's inputs: D = the driver's own peak RSS
    (ru_maxrss of RUSAGE_SELF), the fixed-rate 0.5 s sampler (samples, no failed read, the driver's and the workers'
    peak RSS, the highest growth rate, the largest spacing) and the run's configuration (R-MEM step 1). The record is
    complete for R-MEM step 1's field checks: the only reasons named are this synthetic run's own, WORKERS 2 and no
    launchd launcher."""
    sb()
    out = sb().tmp / "decoy_main_synth.json"
    out.unlink(missing_ok=True)
    r = T.child(sb(), "decoy-main-synth", {"out": str(out), "alloc_mb": 64, "job_sleep": 1.0}, timeout=600)
    try:
        rec = json.loads(out.read_text())
    except (OSError, ValueError):
        return {"ok": False, "child": r["out"], "tail": (r["stdout"] + r["stderr"])[-600:]}
    lc = rec.get("lifecycle", {})
    rs, ctx, run_cfg = lc.get("rss_sampler") or {}, lc.get("stage1_context") or {}, lc.get("rmem_run") or {}
    S()
    from fractions import Fraction as F
    import mbs308_rrules as RR
    const = rule_constants()                        # the cap and poll the driver under test carries (brief 54)
    cap, poll = const["MEM_CAP_BYTES"], F(repr(float(F(const["MEM_POLL_S"]))))
    run = {"id": "synthetic", "cell": 297, "launcher": run_cfg.get("launched_by_launchd"),
           "ladder": run_cfg.get("ladder"), "workers": run_cfg.get("workers"),
           "mem_cap_bytes": run_cfg.get("mem_cap_bytes"), "mem_poll_s": run_cfg.get("mem_poll_s"), "rerun_of": None,
           "watchdog_events": (ctx.get("memory_watchdog") or {}).get("events"),
           "driver_maxrss_bytes": lc.get("driver_maxrss_bytes"),
           "worker_peak_rss_bytes": (ctx.get("memory_watchdog") or {}).get("worker_peak_rss_bytes"),
           "jobs": [{"name": n, "kind": n.split(".")[0], "rung": int(n.split(".")[2]), "job_maxrss_bytes": v}
                    for n, v in (ctx.get("job_maxrss_bytes") or {}).items()]}
    reasons = RR._run_reasons(run, cap, poll)
    mib = 1024 * 1024
    ok = r["out"] == {"rc": 0} and rec.get("synthetic") is True and isinstance(lc.get("driver_maxrss_bytes"), int) \
        and lc["driver_maxrss_bytes"] > 10 * mib and rs.get("interval_s") == "0.25" and rs.get("samples", 0) >= 4 \
        and rs.get("failed_reads") == 0 and (rs.get("driver_peak_rss_bytes") or 0) > 10 * mib \
        and (rs.get("worker_peak_rss_bytes") or 0) >= 64 * mib and rs.get("max_growth_bytes_per_s", 0) > 0 \
        and 0 < rs.get("max_spacing_s", 0) < 2.0 and reasons == ["NOT_UNDER_LAUNCHD_LAUNCHER", "WORKERS_NOT_5"] \
        and isinstance(rs.get("max_spacing_ns"), int) and rs["max_spacing_ns"] > 0 \
        and abs(rs["max_spacing_ns"] / 1e9 - rs["max_spacing_s"]) <= 0.001 \
        and run_cfg.get("mem_cap_bytes") == cap and len(run["jobs"]) > 0
    return {"ok": ok, "rss_sampler": rs, "driver_maxrss_bytes": lc.get("driver_maxrss_bytes"),
            "rmem_run": run_cfg, "r_mem_step1_reasons": reasons, "jobs": len(run["jobs"])}


def t_decoy_failure_record_on_watchdog_event():
    """Owner supplement 2, sections 1 and 6: a memory-watchdog event in a decoy must be mechanically detectable.
    main()'s REAL decoy branch (a sandbox child; the synthetic evaluator; each job holds 400 MB under a planted 200 MB
    cap, as S11 does for `execute`): the watchdog kills the worker, the decoy FAILS -- and the driver still writes the
    run's record to --out: `decoy_failed`, no stage 1, the watchdog's kill event (rss above the cap, killed), the
    sampler record with its largest observed spacing, the driver's peak RSS and the run configuration. The failure
    itself is not swallowed (the child does not report rc 0). Through the rule functions the record is an EVENT run:
    MEMORY_WATCHDOG_EVENT, never dropped, RERUN_REQUIRED in a designated series and
    QUALIFICATION_MEMORY_WATCHDOG_UNDER_FROZEN_CAP in an official one. A decoy that does not fail writes no
    `decoy_failed` (t_decoy_records_rmem_inputs)."""
    sb()
    out = sb().tmp / "decoy_main_synth_failed.json"
    out.unlink(missing_ok=True)
    r = T.child(sb(), "decoy-main-synth", {"out": str(out), "alloc_mb": 400, "job_sleep": 3, "mem_cap_mb": 200},
                timeout=600)
    try:
        rec = json.loads(out.read_text())
    except (OSError, ValueError):
        return {"ok": False, "child": r["out"], "rc": r["rc"], "tail": (r["stdout"] + r["stderr"])[-600:]}
    S()
    import mbs308_derive as DV
    import mbs308_rrules as RR
    lc = rec.get("lifecycle", {})
    wd = (lc.get("stage1_context") or {}).get("memory_watchdog") or {}
    kills = [e for e in RR.cap_events(wd.get("events"))]
    run = DV.compact_run(rec, "decoy297", exit_code=r["rc"])
    cap = 200 * 1024 * 1024
    ri = DV.run_input(run)
    mem_d = RR.r_mem([ri], required_cells=[297], workers=2, mem_poll_s="2", host=None, sampler=None,
                     measurement_cap_bytes=cap, measurement_poll_s="0.3")
    mem_o = RR.r_mem([ri], required_cells=[297], workers=2, mem_poll_s="2", host=None, sampler=None,
                     measurement_cap_bytes=cap, measurement_poll_s="0.3", official=True)
    rows = {"failure_not_swallowed": r["out"] != {"rc": 0} and r["rc"] != 0,
            "record_written_as_failed": isinstance(rec.get("decoy_failed"), str) and bool(rec["decoy_failed"]) and
            "stage1" not in rec and rec.get("mode") == "decoy" and rec.get("decoy_cell") == 297,
            "kill_event_recorded": len(kills) >= 1 and all(
                e.get("killed") is True and e.get("rss_bytes", 0) > e.get("cap_bytes", 0) == cap for e in kills) and
            wd.get("cap_bytes") == cap,
            "rmem_fields_kept": isinstance(lc.get("driver_maxrss_bytes"), int) and
            isinstance((lc.get("rss_sampler") or {}).get("max_spacing_ns"), int) and
            (lc.get("rmem_run") or {}).get("mem_cap_bytes") == cap and isinstance(rec.get("host"), dict),
            "compact_run_carries_it": run["decoy_failed"] == rec["decoy_failed"] and
            "DECOY_FAILED" in DV.plan_reasons(run, {297: None}),
            "designated_series_rerun_required": mem_d["status"] == "RERUN_REQUIRED" and
            mem_d["uncured_event_runs"] == ["decoy297"] and
            mem_d["rerun_required"] == [{"id": "decoy297", "cell": 297, "rerun_cap_bytes": 2 * cap}],
            "official_series_fails_closed": mem_o["status"] == RR.STATUS_OFFICIAL_WATCHDOG and
            mem_o["rerun_required"] == [] and mem_o["event_runs"] == ["decoy297"]}
    return {"ok": all(rows.values()), "rows": rows, "decoy_failed": rec.get("decoy_failed"), "child_rc": r["rc"],
            "events": kills[:2]}


# ====================================================================== reviewQ6's repairs (builder7, research brief 56)
def _pid_gates(ident, **spec) -> dict:
    """The driver's start gates in a child, every planted reading good, with `ident` recorded in the campaign pidfile
    (None: no pidfile)."""
    st = store()
    st.spool(create=True)
    pf = st.spool() / S().PIDFILE
    if pf.exists():
        pf.unlink()
    if ident is not None:
        pf.write_text(json.dumps({"identity": ident}))
    planted = {"host": GOOD_HOST, "su": SU_OFF, "vm_stat": _vm(big_memory())}
    if "ps" in spec:
        planted["ps"] = spec.pop("ps")
    return T.child(sb(), "host_gates", dict(spec, planted=planted))["out"]


def t_start_gates_fail_closed_on_no_reading():
    """R6 (reviewQ6 ruling (a)): the two start gates that failed OPEN on a failed `ps` fail CLOSED. Through the
    DRIVER's host_preflight in a sandbox child, every other reading planted good:
    host_exclusive: a failed `ps -A` (the reading itself fails), an empty output and an output without a process row
    refuse (HOST_PREFLIGHT: host_exclusive); a quiet listing passes; a busy process refuses (as before).
    no_other_campaign_job: a pidfile recording a LIVE process whose `ps` readings fail is not STALE (UNKNOWN is never
    DEAD): the gate refuses; a live recorded process refuses (as before); a pidfile of a positively dead process (pid
    gone, or the pid reused: another start time) and no pidfile pass."""
    fresh()
    busy = PS_QUIET + " 4242     1  90.0 /Applications/Busy.app/Contents/MacOS/Busy\n"
    excl = {"HOST_PREFLIGHT: host_exclusive"}
    job = {"HOST_PREFLIGHT: no_other_campaign_job"}
    out = {"quiet": _pid_gates(None, ps=PS_QUIET), "busy": _pid_gates(None, ps=busy),
           "ps_fails": _pid_gates(None, ps_list_fails=True), "ps_empty": _pid_gates(None, ps=""),
           "ps_no_row": _pid_gates(None, ps="garbage line\n\n")}
    h = T.Helper(180)
    try:
        live = host().identity(h.p.pid)
        out["pid_live"] = _pid_gates(live, ps=PS_QUIET)
        out["pid_live_ps_failing"] = _pid_gates(live, ps=PS_QUIET, ps_fail_pids=[h.p.pid])
        out["pid_reused"] = _pid_gates(dict(live, start_time="Thu Jan  1 00:00:00 1970"), ps=PS_QUIET)
    finally:
        h.kill()
    out["pid_dead"] = _pid_gates(dead_identity(), ps=PS_QUIET)
    out["pid_absent"] = _pid_gates(None, ps=PS_QUIET)
    (store().spool() / S().PIDFILE).unlink(missing_ok=True)
    det = {k: (v or {}).get("detail") for k, v in out.items()}
    passes = {k: (v or {}).get("rc") == 0 and all(v["gates"].values()) for k, v in out.items()}
    ok = all(passes[k] for k in ("quiet", "pid_dead", "pid_reused", "pid_absent")) and \
        all({det[k]} == excl and out[k]["rc"] == 2 for k in ("busy", "ps_fails", "ps_empty", "ps_no_row")) and \
        all({det[k]} == job and out[k]["rc"] == 2 for k in ("pid_live", "pid_live_ps_failing"))
    return {"ok": ok, "cases": {k: det[k] or ("PASS" if passes[k] else "?") for k in out}}


def t_lock_read_never_follows_symlink():
    """G-7 (reviewQ6, YS3): lock_read, the one reader of the recover lock, never follows a symlink. A lock NAME that is
    a symlink to a file holding a complete lock record of a DEAD process (inside the spool, or outside it) reads None,
    exactly as no lock does, while the same bytes under a regular name are read; so Lock.acquire never takes a
    symlink's target for a stale holder: it breaks nothing, moves nothing aside, takes nothing (LOCK_RACE) and leaves
    the symlink and its target untouched."""
    fresh()
    Sm = S()
    st = store()
    sp = st.spool(create=True)
    for n in os.listdir(sp):
        if n.startswith("recover.lock") or n.startswith("planted"):
            os.unlink(sp / n)
    data = Sm.canon({"identity": dead_identity(), "utc": Sm.utc()})
    inside, outside = sp / "planted-holder", sb().tmp / "planted-holder-outside"
    out = {}
    for tag, target in (("inside_the_spool", inside), ("outside_the_spool", outside)):
        target.write_bytes(data)
        lock = sp / "recover.lock"
        os.symlink(target, lock)
        out[f"{tag}:symlink_reads_none"] = Sm.lock_read(st, "recover.lock") is None
        lk = Sm.Lock(st)
        try:
            lk.acquire()
            res = "TAKEN"
        except Sm.Locked as e:
            res = e.code
        out[f"{tag}:acquire_takes_nothing"] = res == "LOCK_RACE" and lk.held is False and lock.is_symlink() and \
            target.read_bytes() == data and _lock_files()["asides"] == []
        lk.release()
        for n in os.listdir(sp):                                    # whatever the attempt left (nothing, as asserted)
            if n.startswith("recover.lock"):
                os.unlink(sp / n)
        target.unlink(missing_ok=True)
    (sp / "recover.lock").write_bytes(data)
    out["regular_file_is_read"] = Sm.lock_read(st, "recover.lock") == data
    os.unlink(sp / "recover.lock")
    out["absent_reads_none"] = Sm.lock_read(st, "recover.lock") is None
    return {"ok": all(out.values()), "cases": out}


def t_decoy_record_ladder_and_driver_peak():
    """G-2 (reviewQ6: YM2, YM6): two recorded fields of main()'s decoy branch. (1) The ladder: a decoy run with
    --dev-ladder is recorded as "dev", never "frozen", so it can never satisfy R-MEM step 1 (NOT_THE_FROZEN_LADDER;
    t_decoy_records_rmem_inputs covers the frozen side). (2) D is the DRIVER's own peak RSS (ru_maxrss of RUSAGE_SELF),
    not its children's: the synthetic jobs hold 256 MB each, so the workers' peak (RUSAGE_CHILDREN, read in the same
    child after the run) is far above the driver's; the recorded D is at most the driver's own peak read after the
    run and well below the children's."""
    sb()
    out = sb().tmp / "decoy_main_synth_dev.json"
    out.unlink(missing_ok=True)
    r = T.child(sb(), "decoy-main-synth", {"out": str(out), "alloc_mb": 256, "job_sleep": 1.0, "dev_ladder": True,
                                           "report_rusage": True}, timeout=600)
    try:
        rec = json.loads(out.read_text())
    except (OSError, ValueError):
        return {"ok": False, "child": r["out"], "tail": (r["stdout"] + r["stderr"])[-600:]}
    S()
    import mbs308_rrules as RR
    lc = rec.get("lifecycle", {})
    cfg, ctx = lc.get("rmem_run") or {}, lc.get("stage1_context") or {}
    ch = r["out"] or {}
    d, own, kids = lc.get("driver_maxrss_bytes"), ch.get("self_maxrss_bytes"), ch.get("children_maxrss_bytes")
    run = {"id": "synthetic-dev", "cell": 297, "launcher": True, "ladder": cfg.get("ladder"), "workers": 5,
           "mem_cap_bytes": cfg.get("mem_cap_bytes"), "mem_poll_s": cfg.get("mem_poll_s"), "rerun_of": None,
           "watchdog_events": (ctx.get("memory_watchdog") or {}).get("events"), "driver_maxrss_bytes": d,
           "worker_peak_rss_bytes": None,
           "jobs": [{"name": n, "kind": n.split(".")[0], "rung": int(n.split(".")[2]), "job_maxrss_bytes": v}
                    for n, v in (ctx.get("job_maxrss_bytes") or {}).items()]}
    const = rule_constants()
    from fractions import Fraction as F
    reasons = RR._run_reasons(run, const["MEM_CAP_BYTES"], F(repr(float(F(const["MEM_POLL_S"])))))
    mib = 1024 * 1024
    rows = {"child_ran": ch.get("rc") == 0 and rec.get("synthetic") is True and len(run["jobs"]) > 0,
            "dev_ladder_recorded_as_dev": cfg.get("ladder") == "dev",
            "a_dev_ladder_run_is_never_a_step1_input": reasons == ["NOT_THE_FROZEN_LADDER"],
            "control_children_far_above_the_driver": all(isinstance(x, int) for x in (d, own, kids)) and
            kids >= 256 * mib and kids > own + 64 * mib,
            "D_is_the_drivers_own_peak": isinstance(d, int) and isinstance(own, int) and isinstance(kids, int) and
            10 * mib < d <= own < kids}
    return {"ok": all(rows.values()), "rows": rows, "driver_maxrss_bytes": d, "self_after": own,
            "children_after": kids, "ladder": cfg.get("ladder"), "r_mem_step1_reasons": reasons}


def t_decoy_record_driver_peak_read_last():
    """Brief 56 follow-up, item 3: R-MEM's D ("the driver's own peak RSS in those runs", ru_maxrss of RUSAGE_SELF) is
    read LAST in main()'s decoy branch: after the run's host-provenance collection, immediately before the record is
    serialised. The provenance collection is planted to hold 300 MB of resident memory while it runs (a stand-in for
    its power-log read) and the process's peak RSS is read INSIDE it; the recorded D must be at least that reading
    (ru_maxrss never decreases, so a D read before the provenance collection would be far below it) and at most the
    process's peak read after main() returned. The same holds for a decoy that FAILS (its record is written too)."""
    sb()
    mib = 1024 * 1024
    rows, seen = {}, {}
    for tag, extra in (("completed", {"alloc_mb": 64, "job_sleep": 1.0}),
                       ("failed", {"alloc_mb": 400, "job_sleep": 3, "mem_cap_mb": 200})):
        out = sb().tmp / f"decoy_main_synth_last_{tag}.json"
        out.unlink(missing_ok=True)
        r = T.child(sb(), "decoy-main-synth", dict(extra, out=str(out), provenance_alloc_mb=300, report_rusage=True),
                    timeout=600)
        try:
            rec = json.loads(out.read_text())
        except (OSError, ValueError):
            return {"ok": False, "case": tag, "child": r["out"], "tail": (r["stdout"] + r["stderr"])[-600:]}
        d = (rec.get("lifecycle") or {}).get("driver_maxrss_bytes")
        ch = r["out"] or {}
        inside, after = ch.get("maxrss_inside_provenance_bytes"), ch.get("self_maxrss_bytes")
        seen[tag] = {"D": d, "inside_provenance": inside, "after_main": after, "rc": r["rc"]}
        if tag == "completed":
            rows["completed_run_recorded"] = ch.get("rc") == 0 and rec.get("synthetic") is True and \
                "decoy_failed" not in rec and isinstance(rec.get("host"), dict)
            rows["control_the_plant_took_effect"] = isinstance(inside, int) and inside >= 300 * mib
            rows["D_read_after_the_provenance_collection"] = isinstance(d, int) and isinstance(inside, int) and \
                isinstance(after, int) and inside <= d <= after
        else:                       # the failure is re-raised (no JSON line with rc 0); the record is still written
            rows["failed_run_recorded"] = isinstance(rec.get("decoy_failed"), str) and r["out"] != {"rc": 0} and \
                isinstance(rec.get("host"), dict)
            rows["failed_run_D_read_after_the_provenance_collection"] = isinstance(d, int) and d >= 300 * mib
    return {"ok": all(rows.values()), "rows": rows, "readings": seen}


if __name__ == "__main__":
    T.cli(globals())
