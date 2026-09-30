"""MB-S r1: planted mutants (architecture section 7; MBS-4, MBS-9 iii; DR2 b). Every gate has a mutant that must make
its TARGET test FAIL, and the unmutated code must make every target test PASS.

For each mutant: the namespace's code/ is copied, ONE exact fragment is replaced (it must occur exactly once), the
driver's HELPER_SHA256 table is re-pinned to the mutated helper bytes (so the mutant is killed by the gate's own test,
never by a pin check), and the target test runs in a fresh process against the mutated copy (MBS308_TEST_CODE_DIR;
its sandbox is a --shared clone of the separate base store, never of the real object store).

    python3.14 -I -S -B test_mbs308_mutants.py [--only M01,M02] [--out report.json]
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mbs308_testlib as T  # noqa: E402

TMP = T.SCRATCH / "t_mutants"
TESTS = T.NSS / "tests"
HELPERS = ("mbs308_guard.py", "mbs308_host.py", "mbs308_state.py", "mbs308_launch.py")

# id: (file, exact old fragment, new fragment, target "module::test", what the mutant breaks)
MUTANTS = {
    "M01": ("mbs308_state.py", '                fsync_file(fd)\n                steps.append("fsync")',
            '                steps.append("fsync")', "state::t_persistence_contract", "skip the fsync of the tmp file"),
    "M02": ("mbs308_state.py", '    if got != sha(json.dumps(rest, sort_keys=True).encode()):\n        return None',
            '    if False:\n        return None', "state::t_verify_result_units", "skip the self-hash check"),
    "M03": ("mbs308_state.py", '    try:\n        spool_data = st.spool_read(RESULT_FILE)\n',
            '    try:\n        spool_data = st.spool_read(RESULT_FILE)\n'
            '        if spool_data is None and os.path.lexists(st.spool() / TMP_FILE):\n'
            '            spool_data = open(st.spool() / TMP_FILE, "rb").read()\n',
            "crash::t_F7_exit", "accept a .tmp file as the result"),
    "M04": ("mbs308_state.py", '            ok = ok and rec.get("grant_commit") == self.grant                             # the grant\n',
            '', "state::t_ckpt_wrong_grant", "accept a checkpoint bound to a wrong grant"),
    "M05": ("mbs308_state.py", '            ok = ok and rec.get("driver_sha256") == self.driver_sha                       # the driver\n',
            '', "state::t_ckpt_wrong_driver", "accept a checkpoint bound to a wrong driver sha"),
    "M06": ("mbs308_state.py", '            ok = ok and rec.get("platform_sha256") == self.platform_sha                   # the platform pin\n',
            '', "state::t_ckpt_wrong_platform", "accept a checkpoint written under another platform pin"),
    "M07": ("mbs308_state.py", 'ok = rec.get("attempt") in attempts and rec.get("journal_seq") == attempts[rec.get("attempt")]',
            'ok = rec.get("attempt") in attempts', "state::t_ckpt_future_seq",
            "accept a checkpoint with a wrong / future journal seq"),
    "M08": ("mbs308_state.py", 'ok = rec.get("attempt") in attempts and rec.get("journal_seq") == attempts[rec.get("attempt")]',
            'ok = rec.get("journal_seq") in attempts.values()', "state::t_ckpt_other_attempt",
            "accept a checkpoint from another attempt"),
    "M09": ("mbs308_state.py", '    if key is None or rec.get("name") != name or rec.get("job") != [key[0], key[1], key[2]]:\n'
            '        return False\n    if isinstance(record, dict)', '    return True\n    if isinstance(record, dict)',
            "state::t_ckpt_job_swap", "serve the checkpoint of job A as job B"),
    "M10": ("mbs308_state.py", '            ok = ok and isinstance(rec.get("record"), (dict, list)) and \\\n'
            '                rec.get("record_sha256") == sha(canon(rec["record"]))',
            '            ok = ok and isinstance(rec.get("record"), (dict, list))', "state::t_ckpt_wrong_record_hash",
            "skip the checkpoint record hash"),
    "M11": ("mbs308_state.py", '    if _not_dead(jrec.get("process"), cur_boot, None):',
            '    if False:', "state::t_computing_then_interrupted", "resume on a live process"),
    "M12": ("mbs308_driver.py", '        if cls["state"] != "CONSUMED_UNRECORDED":\n            raise Refusal("NO_DISCRETIONARY_ABANDONMENT"',
            '        if cls["state"] not in ("CONSUMED_UNRECORDED", "CONSUMED_INTERRUPTED"):\n'
            '            raise Refusal("NO_DISCRETIONARY_ABANDONMENT"', "state::t_no_abandonment", "allow abandonment"),
    "M13": ("mbs308_launch.py", '            "detached": bool(not_descendant and other_session and named)}',
            '            "detached": HOST.process_ppid(job_pid) == 1}', "launch::t_ppid1_is_not_detachment",
            "treat PPID = 1 as detachment"),
    "M14": ("mbs308_host.py", '            if not self._stop.is_set():\n                self._spawn()',
            '            if False:\n                self._spawn()', "launch::t_supervisor_respawns_in_process",
            "no caffeinate re-spawn"),
    "M15": ("mbs308_host.py", '    if ident.get("boot_uuid") and ident["boot_uuid"] != cur_boot:\n        return "DEAD"',
            '    if False:\n        return "DEAD"', "state::t_reboot",
            "ignore the boot UUID (a reboot is not an interruption)"),
    "M16": ("mbs308_state.py", '        if not self.store.cas_ref(JOURNAL_REF, oid, self.jid or None):',
            '        if self.store.git("update-ref", JOURNAL_REF, oid, write=True).returncode != 0:',
            "state::t_journal_cas", "journal update without compare-and-swap"),
    "M17": ("mbs308_driver.py", '            marker_ok = st.cas_ref(CONSUMED_REF, grant["grant_commit"], None)',
            '            marker_ok = st.git("update-ref", CONSUMED_REF, grant["grant_commit"], write=True).returncode == 0',
            "state::t_marker_cas", "marker without compare-and-swap"),
    "M18": ("mbs308_state.py", 'MAX_RESUMES = 3 ', 'MAX_RESUMES = 4 ', "state::t_budget_exhausted",
            "a fourth resume"),
    "M19": ("mbs308_state.py", '    if (time.time() if now is None else now) - t_marker > DEADLINE_S:', '    if False:',
            "state::t_deadline", "no 7-day deadline"),
    "M20": ("mbs308_driver.py", '    if hooks:                                   # section 7',
            '    if False:                                   # section 7',
            "static::t_fault_hook_test_only", "production accepts the test hook"),
    "M21": ("mbs308_driver.py", '        if any(int(v) >= STATE.CKPT_FAIL_LIMIT for v in fails.values()):',
            '        if False:', "state::t_two_consecutive_failures", "no two-consecutive-failures rule"),
    "M22": ("mbs308_host.py", '    if st is None or st != ident.get("start_time"):', '    if st is None:',
            "state::t_stale_pidfile", "trust a pidfile whose start time differs"),
    "M23": ("mbs308_state.py", '        if back != data or verify_serialized(back) is None:', '        if False:',
            "state::t_persistence_contract", "skip the read-back verification"),
    "M24": ("mbs308_state.py", '    if not isinstance(g, dict) or g.get("grant_commit") != grant:\n        return None, "GRANT_BINDING"',
            '    if not isinstance(g, dict):\n        return None, "GRANT_BINDING"', "state::t_verify_result_units",
            "accept a result bound to another grant"),
    "M25": ("mbs308_driver.py", '    if refs != [[MBR1_MARKER, MBR1_MARKER_TARGET]]:',
            '    if [MBR1_MARKER, MBR1_MARKER_TARGET] not in refs:', "state::t_gc8_mbr1_state",
            "MB r1 state checked as a prefix wildcard (GC-8)"),
    "M26": ("mbs308_state.py", '    if jrec.get("platform_mismatch") or jrec.get("platform") != platform:',
            '    if jrec.get("platform_mismatch"):', "state::t_platform_mismatch_at_resume",
            "skip the resume-time platform pin check (DR2)"),
    "M27": ("mbs308_state.py", '                        os.kill(pid, signal.SIGKILL)\n                        killed = True',
            '                        killed = True', "crash::t_S11_memory_watchdog", "the memory watchdog never kills"),
    "M28": ("mbs308_state.py", '        self.refuse_if_terminal()\n', '', "state::t_ckpt_never_read_after_terminal",
            "read checkpoints after a terminal state (MBS-4)"),
    "M29": ("mbs308_state.py", '        self.written += 1\n        fault("F3")',
            '        self.written += 1\n        if self.journal is not None:\n'
            '            self.journal.advance(n_ckpt=len(entries))\n        fault("F3")',
            "state::t_no_in_run_observation", "per-job progress in the journal (MBS-3)"),
    "M30": ("mbs308_driver.py", '            if st.spool_exists(name):\n                st.quarantine(name, "resume")',
            '            pass', "crash::t_S06_truncated_result", "resume does not set a rejected spool result aside"),
    "M31": ("mbs308_driver.py", '    pre["host_gates"] = host_preflight(check_launched())',
            '    pre["host_gates"] = host_preflight({"pass": True})', "state::t_execute_refuses_outside_launchd",
            "execute without the launchd launcher"),
    "M32": ("mbs308_driver.py", '                jr.advance(state="ABORTED_INTENT", aborted_utc=utc())',
            '                pass',
            "state::t_marker_cas", "a refused intent makes an unrecorded run look resumable"),
    "M33": ("mbs308_state.py", '        while not self._stop.wait(self.poll_s):\n            self._release_broken()\n',
            '        while not self._stop.wait(self.poll_s):\n', "crash::t_S01_worker_death",
            "a broken pool is not released (the driver hangs until EVAL_CAP)"),
    # ---- repairs R1 / R2 / R4 (implementation review REVIEW_IMPLEMENTATION_MBS308, 6d3a44cd)
    "M34": ("mbs308_state.py", '            if readable and cur != expect:\n                return False', '            return False',
            "crash::t_L05_ckpt_lock_midrun", "R1 (i) undone: every ref-write failure read as a CAS conflict"),
    "M35": ("mbs308_driver.py", '        if not durable:\n            raise STATE.LostOwnership()',
            '        raise STATE.LostOwnership()', "crash::t_L04_journal_conflict_during_seal",
            "R1 (ii) undone: a journal conflict after the durable result stops the seal"),
    "M36": ("mbs308_driver.py", '            moved = STATE.move_stale_git_locks(store(), boot_uuid)', '            moved = []',
            "crash::t_L02_journal_lock_after_crash", "R1 (iii) undone: recover never moves stale git lockfiles aside"),
    "M37": ("mbs308_state.py", '    if isinstance(prec, dict) and _not_dead(prec.get("identity"), boot_uuid, exclude_pid):\n'
            '        live.append("pidfile")\n', '', "crash::t_L10_lock_with_live_campaign_process",
            "R1 (iii) guard undone: a lock is 'stale' although a live campaign process holds the pidfile"),
    "M38": ("mbs308_state.py", '"git_locks_stale": not live and all(v is False for v in opened.values())}',
            '"git_locks_stale": not live}', "crash::t_L11_campaign_lock_open",
            "R1 (iii) guard undone: a lockfile held open by a live process is moved aside"),
    "M39": ("mbs308_driver.py", '        if jrec is None or jrec["state"] not in ("ARMING", "ABORTED_INTENT") or \\',
            '        if jrec is None or jrec["state"] not in ("ARMING",) or \\', "crash::t_L01_marker_lock",
            "R1 (d wedge) undone: an aborted intent (marker write failed) blocks every later execute"),
    "M40": ("mbs308_launch.py", '    while HOST.identity_state(identity) != "DEAD":',
            '    while HOST.launchd_job_pid(label) is not None:', "launch::t_wait_cleanup_ignores_failing_print",
            "R2 undone: the launcher boots out on one negative `launchctl print`"),
    "M41": ("mbs308_launch.py", '        raise                    # never boot out after the bootstrap (R2)',
            '        bootout(label)\n        raise                    # never boot out after the bootstrap (R2)',
            "launch::t_launch_never_boots_out_after_bootstrap", "R2 undone: launch() boots out after the bootstrap"),
    "M42": ("mbs308_driver.py", '    g["gates"]["free_memory_ge_min"] = isinstance(fm, int) and fm >= FREE_MEM_MIN_BYTES',
            '    g["gates"]["free_memory_ge_min"] = True', "state::t_gc10_start_gates",
            "GC-10 free-memory start gate ignored (R4)"),
    "M43": ("mbs308_driver.py", '    g["gates"]["host_exclusive"] = not busy', '    g["gates"]["host_exclusive"] = True',
            "state::t_gc10_start_gates", "GC-10 exclusivity start gate ignored (R4)"),
    "M44": ("mbs308_driver.py", '    bad = [k for k, v in PLATFORM_PINS.items() if got.get(k) != v]', '    bad = []',
            "state::t_pins_resume_platform", "platform pin never compared (execute / resume) (R4)"),
    "M45": ("mbs308_driver.py", '    shas = check_bindings()\n    state = check_governance_state()\n    pre = ',
            '    shas = {}\n    state = check_governance_state()\n    pre = ', "state::t_pins_resume_research",
            "research pins not re-verified at execute / resume (R4)"),
    "M46": ("mbs308_driver.py", '            raise Refusal("SCIENCE_PIN_MISMATCH", rel)', '            pass',
            "state::t_pins_resume_science", "science pins not re-verified at execute / resume (R4)"),
    "M47": ("mbs308_driver.py", '        if git("ls-tree", tip, "--", ev).stdout.strip():', '        if False:',
            "state::t_gc8_evidence_at_head_and_mbr1_branch", "GC-8 evidence path at HEAD / on MB r1's branch ignored (R4)"),
    # ---- R3 + C-1 + N-2 / N-3 (implementation delta review REVIEW_IMPLEMENTATION_MBS308_DELTA, 99185dcb)
    "M48": ("mbs308_state.py", '    rel = st.branch_ref + ".lock"\n    if os.path.lexists(cd / rel):\n        out.append(rel)\n',
            '    for rel in (st.branch_ref + ".lock", "packed-refs.lock"):\n        if os.path.lexists(cd / rel):\n'
            '            out.append(rel)\n', "crash::t_L09_packed_refs_lock_never_moved",
            "C-1 undone: packed-refs.lock is a campaign lockfile again (listed, refused on, moved aside)"),
    "M49": ("mbs308_host.py", '    if ident.get("start_time") and st != ident["start_time"]:',
            '    if st != ident.get("start_time"):', "launch::t_identity_state_positive_evidence",
            "N-2 undone: an identity recorded without its start time reads DEAD for a live process"),
    "M50": ("mbs308_state.py", '    return HOST.identity_state(ident, boot_uuid) != "DEAD"',
            '    return HOST.identity_alive(ident, boot_uuid)', "crash::t_L12_lock_ps_failure_not_stale",
            "N-3 undone: a failed `ps` makes a live campaign process read dead, so its lockfile is moved aside"),
    "M51": ("mbs308_driver.py", ',\n                        "spotlightknowledged.updater", "cloudd", "BackgroundShortcutRunner", '
            '"modelcatalogd"})', '})', "state::t_gc10_ratified_allow_list",
            "R3 undone: the four ratified OS daemons are not on the exclusivity allow-list"),
    "M52": ("mbs308_launch.py", 'timeout=PRE_CAP_S + 100)', 'timeout=1900)', "launch::t_preflight_timeout_rule",
            "R3 undone: the launcher's preflight timeout is the literal 1900 s, not the rule PRE_CAP_S + 100 s"),
    # ---- liveness delta (REVIEW_IMPLEMENTATION_MBS308_DELTA_R3 s3 recommendation and coverage note X4; builder3)
    "M53": ("mbs308_state.py", '    if _not_dead(jrec.get("process"), cur_boot, None):',
            '    if HOST.identity_alive(jrec.get("process"), cur_boot):',
            "state::t_computing_ps_failure_not_interrupted",
            "liveness delta undone at the classifier: a failed `ps` makes the live recorded process read dead "
            "(CONSUMED_INTERRUPTED), so a resume could race it"),
    "M54": ("mbs308_state.py", '                if _not_dead(holder, None, None):',
            '                if HOST.identity_alive(holder):', "crash::t_S13_lock_ps_failure_not_broken",
            "liveness delta undone at Lock.acquire: a failed `ps` makes the live holder read dead, so its recover "
            "lock is broken"),
    "M55": ("mbs308_state.py", '    if jrec is not None and _not_dead(jrec.get("process"), boot_uuid, exclude_pid):',
            '    if jrec is not None and HOST.identity_alive(jrec.get("process"), boot_uuid):',
            "crash::t_L13_lock_sources_ps_failure_each",
            "N-3 undone for the journal source only (reviewR3C1's X4): a failed `ps` makes the journal's live recorded "
            "process read dead, so the lockfiles read stale"),
    "M56": ("mbs308_state.py", '    if _not_dead(holder, boot_uuid, exclude_pid):',
            '    if HOST.identity_alive(holder, boot_uuid):', "crash::t_L13_lock_sources_ps_failure_each",
            "N-3 undone for the recover-lock source only: a failed `ps` makes the live lock holder read dead, so the "
            "lockfiles read stale"),
    # M15's former fragment (identity_alive's boot check; since the liveness delta the classifier no longer reads it)
    "M57": ("mbs308_host.py", '    if not ident.get("boot_uuid") or ident.get("boot_uuid") != cur_boot:\n        return False',
            '    if not ident.get("boot_uuid"):\n        return False', "state::t_stale_pidfile",
            "trust a pidfile recorded under another boot (identity_alive ignores the boot UUID)"),
}


def repin(code: Path) -> None:
    drv = code / "mbs308_driver.py"
    s = drv.read_text()
    for name in HELPERS:
        h = hashlib.sha256((code / name).read_bytes()).hexdigest()
        s, n = re.subn(r'("%s": )"[0-9a-f]{64}"' % re.escape(name), r'\1"%s"' % h, s)
        assert n == 1, name
    drv.write_text(s)


def make_code(tag: str, mutant: tuple | None) -> Path:
    d = TMP / tag / "code"
    if d.parent.exists():
        shutil.rmtree(d.parent)
    shutil.copytree(T.NSS / "code", d, ignore=shutil.ignore_patterns("__pycache__"))
    if mutant is not None:
        f, old, new = mutant[:3]
        p = d / f
        s = p.read_text()
        if s.count(old) != 1:
            raise RuntimeError(f"{tag}: the fragment occurs {s.count(old)} times in {f}")
        p.write_text(s.replace(old, new))
        import ast
        ast.parse(p.read_text())            # a mutant must be valid Python: a syntax error is never a "kill"
    repin(d)
    return d


def run_target(target: str, code: Path, tag: str) -> dict:
    mod, test = target.split("::")
    out = TMP / tag / "result.json"
    env = dict(T.GENV, MBS308_TEST_CODE_DIR=str(code), MBS308_SCRATCH=str(TMP / tag / "scratch"),
               MBS308_BASE_STORE=str(T.BASE_STORE))            # the runner's own base store, never another default
    (TMP / tag / "scratch").mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    p = subprocess.run([T.PY, "-I", "-S", "-B", str(TESTS / f"test_mbs308_{mod}.py"), test, "--out", str(out)],
                       capture_output=True, text=True, env=env, stdin=subprocess.DEVNULL, timeout=900)
    try:
        r = json.loads(out.read_text())["results"][test]
    except (OSError, ValueError, KeyError):
        r = {"ok": False, "error": "no result", "stdout": p.stdout[-400:], "stderr": p.stderr[-400:]}
    return {"test_passed": bool(r.get("ok")), "rc": p.returncode, "seconds": round(time.time() - t0, 1),
            "error": r.get("error")}


def main() -> int:
    args = sys.argv[1:]
    only = None
    out_path = None
    if "--only" in args:
        only = set(args[args.index("--only") + 1].split(","))
    if "--out" in args:
        out_path = args[args.index("--out") + 1]
    sel = {k: v for k, v in MUTANTS.items() if only is None or k in only}
    TMP.mkdir(parents=True, exist_ok=True)
    # 1. the unmutated code (re-pinned identically) must PASS every target test
    base_code = make_code("UNMUTATED", None)
    unmutated = {}
    for target in sorted({v[3] for v in sel.values()}):
        unmutated[target] = run_target(target, base_code, "UNMUTATED")
        print(f"{'PASS' if unmutated[target]['test_passed'] else 'FAIL'} unmutated {target} "
              f"({unmutated[target]['seconds']} s)", flush=True)
    # 2. every mutant must make its target test FAIL
    matrix = {}
    for mid, m in sel.items():
        try:
            code = make_code(mid, m)
            r = run_target(m[3], code, mid)
            killed = not r["test_passed"]
        except Exception as exc:                                        # noqa: BLE001 (an invalid mutant survives)
            r, killed = {"error": f"INVALID MUTANT {type(exc).__name__}: {exc}"}, False
        matrix[mid] = {"file": m[0], "breaks": m[4], "target": m[3], "killed": killed, **r}
        print(f"{'KILLED' if killed else 'SURVIVED'} {mid} {m[4]} -> {m[3]} ({r.get('seconds')} s)", flush=True)
    rep = {"unmutated_all_pass": all(v["test_passed"] for v in unmutated.values()), "unmutated": unmutated,
           "matrix": matrix, "killed": sum(1 for v in matrix.values() if v["killed"]), "total": len(matrix),
           "survivors": [k for k, v in matrix.items() if not v["killed"]]}
    if out_path:
        Path(out_path).write_text(json.dumps(rep, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: rep[k] for k in ("unmutated_all_pass", "killed", "total", "survivors")}))
    return 0 if rep["unmutated_all_pass"] and not rep["survivors"] else 1


if __name__ == "__main__":
    sys.exit(main())
