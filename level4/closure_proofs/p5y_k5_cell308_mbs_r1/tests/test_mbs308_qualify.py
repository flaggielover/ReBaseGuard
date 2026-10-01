"""MB-S r1: the qualification framework's own tests (builder4, research brief 46). TARGET-FREE: planted records,
planted patterns and tokens (neutral numbers, never a tail figure or a cell-308 record token), throw-away git
repositories under the scratch directory, and one SPARSE sandbox cloned (--shared) from the separate --no-local base
store (never the real object store). No science computation, no decoy, no cell 305-309.

Covers the aggregator, every BUILT case (pass and a planted failure), the PENDING cases failing closed, the R-rule
functions, the manifest writer's core and the CLI refusals. The code under test is tests/../code or a mutated copy
(MBS308_TEST_CODE_DIR, the mutant runner).

    python3.14 -I -S -B test_mbs308_qualify.py [t_name ...] [--out report.json]
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mbs308_testlib as T  # noqa: E402

CODE = T.code_dir()
sys.path.insert(0, str(CODE))
import mbs308_manifest as MF  # noqa: E402
import mbs308_qualify as Q  # noqa: E402
import mbs308_rrules as RR  # noqa: E402

CFG_PATH = T.NSS / "config" / "MBS308_QUALIFICATION_CASES.json"
CFG = Q.load_config(CFG_PATH)
TMP = T.SCRATCH / "t_qualify"
NS_REL = T.NS_REL
GIT_ENV = {"PATH": "/usr/bin:/bin", "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "planted",
           "GIT_AUTHOR_EMAIL": "planted@invalid", "GIT_COMMITTER_NAME": "planted",
           "GIT_COMMITTER_EMAIL": "planted@invalid"}


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def mg(repo: Path, *args, check=True) -> str:
    p = subprocess.run(["/usr/bin/git", "-C", str(repo), "-c", "commit.gpgsign=false", *args], capture_output=True,
                       text=True, env=dict(GIT_ENV, HOME=str(repo)), stdin=subprocess.DEVNULL)
    if check and p.returncode:
        raise RuntimeError(f"git {args[:3]}: {p.stderr[:300]}")
    return p.stdout.strip()


def mini_repo(name: str) -> Path:
    """A throw-away git repository under the scratch directory (never the campaign's)."""
    d = TMP / name
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    mg(d, "init", "-q", "-b", "main")
    return d


def commit(repo: Path, files: dict, msg: str) -> str:
    for rel, data in files.items():
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data if isinstance(data, bytes) else data.encode())
    mg(repo, "add", "-f", *files)
    mg(repo, "commit", "-q", "--allow-empty", "-m", msg)
    return mg(repo, "rev-parse", "HEAD")


def all_pass_cases() -> dict:
    return {c["id"]: {"pass": True} for c in CFG["cases"]}


def guard_pin() -> str:
    return next(c["sha256"] for c in CFG["commit_pins"] if c["key"] == "mbr1_guard_base")


# ------------------------------------------------------------------ the aggregator and the declared cases
def t_aggregator_boolean_pass_and_dev():
    """Every case must carry a boolean `pass` (a missing or non-boolean one fails loudly); a configured case that did
    not run or an unknown case fails; a dev report is never a PASS."""
    ok_off = Q.aggregate(all_pass_cases(), CFG, "official")
    ok_dev = Q.aggregate(all_pass_cases(), CFG, "dev")
    c1 = all_pass_cases()
    c1["QC11-S"] = {"status": "x"}
    miss = Q.aggregate(c1, CFG, "official")
    c2 = all_pass_cases()
    c2["QC12-S"] = {"pass": 1}
    nonbool = Q.aggregate(c2, CFG, "official")
    c3 = all_pass_cases()
    del c3["Q8-S"]
    notrun = Q.aggregate(c3, CFG, "official")
    c4 = all_pass_cases()
    c4["QC99"] = {"pass": True}
    unknown = Q.aggregate(c4, CFG, "official")
    c5 = all_pass_cases()
    c5["QC13-S"] = {"pass": False}
    one_fail = Q.aggregate(c5, CFG, "review")
    cfg2 = json.loads(json.dumps(CFG))
    cfg2["cases"].append({"id": "QC98", "gates": ["Q8"], "status": "BUILT", "depends_on": []})
    inconsistent = Q.aggregate(dict(all_pass_cases(), QC98={"pass": True}), cfg2, "official")
    ok = ok_off["pass"] is True and ok_dev["pass"] is False and \
        miss["pass"] is False and miss["cases_missing_pass"] == ["QC11-S"] and \
        nonbool["pass"] is False and nonbool["cases_missing_pass"] == ["QC12-S"] and \
        notrun["pass"] is False and notrun["cases_not_run"] == ["Q8-S"] and \
        unknown["pass"] is False and unknown["cases_unknown"] == ["QC99"] and \
        one_fail["pass"] is False and one_fail["gates"]["Q10"]["pass"] is False and \
        one_fail["gates"]["Q11"]["pass"] is False and one_fail["gates"]["Q8"]["pass"] is True and \
        inconsistent["pass"] is False and inconsistent["config_consistency"]["unknown_in_config"] == ["QC98"]
    return {"ok": ok, "official_all_pass": ok_off["pass"], "dev_all_pass": ok_dev["pass"]}


def t_pending_cases_fail_closed():
    """A DECLARED (option-dependent) case returns exactly pass false / PENDING_USER_DECISION / its depends_on, and
    keeps every gate it belongs to (and the qualification) failing even when every BUILT case passes. Since brief 54
    the user's decisions are recorded and no case of the configuration is pending (asserted); the mechanism is
    exercised with PLANTED pending cases declared on both sides (the verifier's table and a copy of the
    configuration)."""
    cfg_pending = {c["id"]: c for c in CFG["cases"] if c["status"] == Q.PENDING_STATUS}
    none_pending = cfg_pending == {} and dict(Q.PENDING_CASES) == {} and Q.config_consistency(CFG)["pass"] is True
    planted = {"QC97": ("MBS-97",), "QC98": ("MBS-98", "PLANTED SEQUENCING")}
    saved = dict(Q.PENDING_CASES)
    try:
        Q.PENDING_CASES.update(planted)
        cfg = json.loads(json.dumps(CFG))
        cfg["cases"] += [{"id": "QC97", "gates": ["Q3"], "status": Q.PENDING_STATUS, "depends_on": ["MBS-97"]},
                         {"id": "QC98", "gates": ["Q12", "Q13"], "status": Q.PENDING_STATUS,
                          "depends_on": ["MBS-98", "PLANTED SEQUENCING"]}]
        cp = {c["id"]: c for c in cfg["cases"] if c["status"] == Q.PENDING_STATUS}
        rows = {}
        for cid in Q.PENDING_CASES:
            r = Q.pending(cid)
            rows[cid] = r["pass"] is False and r["status"] == "PENDING_USER_DECISION" and \
                r["depends_on"] == list(cp[cid]["depends_on"]) and bool(r["depends_on"])
        cases = {c["id"]: ({"pass": True} if c["status"] == "BUILT" else Q.pending(c["id"])) for c in cfg["cases"]}
        agg = Q.aggregate(cases, cfg, "official")
        pend_gates = {g for c in cp.values() for g in c["gates"]}
        gates_ok = all(agg["gates"][g]["pass"] is False for g in pend_gates) and \
            all(v["pass"] is True for g, v in agg["gates"].items() if g not in pend_gates)
        ok = none_pending and set(cp) == set(Q.PENDING_CASES) == set(planted) and all(rows.values()) and \
            agg["pass"] is False and gates_ok and agg["pending_user_decision"] == sorted(planted) and \
            Q.config_consistency(cfg)["pass"] is True
    finally:
        Q.PENDING_CASES.clear()
        Q.PENDING_CASES.update(saved)
    return {"ok": ok, "pending": len(rows), "gates_blocked": sorted(pend_gates), "none_pending_today": none_pending}


def t_config_and_protocol_s11():
    """The protocol draft's section 11 qualification plan lists every case with its gates and status exactly as the
    configuration does; the configuration agrees with the verifier."""
    proto = (T.NSS / "protocol/MBS308_PROTOCOL_DRAFT.md").read_text()
    s11 = proto.split("\n## 11.", 1)[1].split("\n## 12.", 1)[0] if "\n## 11." in proto else ""
    rows = {}
    for ln in s11.splitlines():
        cells = [c.strip().strip("`") for c in ln.strip().strip("|").split("|")]
        if ln.startswith("| `") and len(cells) >= 3:
            rows[cells[0]] = (tuple(g.strip() for g in cells[1].split(",")), cells[2])
    want = {c["id"]: (tuple(c["gates"]), c["status"]) for c in CFG["cases"]}
    return {"ok": bool(rows) and rows == want and Q.config_consistency(CFG)["pass"] is True,
            "differ": sorted(set(rows.items()) ^ set(want.items()))}


# ------------------------------------------------------------------ R-rules
def t_rrules_planted_controls():
    """Every branch of R-MEM, R-FREE, R-EXCL-PCT and R-ALLOW on planted inputs (expectations computed independently),
    and the exact helpers."""
    rows = Q.r_rules_planted()
    M = RR.MIB
    helpers = RR.roundup(1, 5) == 5 and RR.roundup(5, 5) == 5 and RR.roundup(F(51, 2), 5) == 30 and \
        RR.roundup_256mib(256 * M + 1) == 512 * M and RR.roundup_256mib(256 * M) == 256 * M and \
        RR.basename("/a/b/c.d") == "c.d" and RR.under("/usr/libexec", "/usr/libexec/") and \
        not RR.under("/usr/libexecX/y", "/usr/libexec/") and RR.pct("25.1") == F(251, 10)
    return {"ok": len(rows) >= 30 and all(v is True for v in rows.values()) and helpers,
            "failed": sorted(k for k, v in rows.items() if v is not True), "n": len(rows)}


def t_rrules_numbers_are_the_ratifications():
    """Every number of the rule module is the ratification's: each appears in the ratification's section 'Written
    rules' (read from the committed text at 3c2a7854), and the module's constants equal those numbers."""
    raw = Q.git_show_bytes(RR.RATIFICATION_COMMIT, RR.RATIFICATION_REL, repo=T.base_store())
    text = raw.decode() if raw else ""
    sec = " ".join(text.split("## Written rules", 1)[1].split("\n## Evidence", 1)[0].split()) if raw else ""
    phrases = ("roundup_256MiB(max(k × P, 1 GiB)), k = max(3, 2s)", "provisional cap (3 GiB)", "MEM_POLL_S 2 s",
               "WORKERS 5", "provisional cap doubled", "g × MEM_POLL_S ≤ 0.1 × MEM_CAP",
               "MEM_POLL_S = max(0.5 s, 0.1 × MEM_CAP / g)", "≤ 0.5 s qualification sampler",
               "FREE_MEM_MIN = max(2 GiB, roundup_256MiB(MEM_CAP + (WORKERS − 1) × P + D))",
               "≥ 10 readings, 30 s apart", "At least 3 consecutive readings", "EXCL_CPU_PCT = 25",
               "min(50, roundup_5(1.25 × its maximum reading))", "`/System/`, `/usr/libexec/`, `/usr/sbin/`, `/sbin/` "
               "or `/Library/Apple/`", "`/Applications`, `/Users`, `/opt`, `/usr/local`, `/Library/Frameworks`, "
               "`/usr/bin` or `/bin`", "any Python interpreter, or the hosting app", "GATE_UNATTAINABLE")
    found = {p: p in sec for p in phrases}
    consts = RR.ROUND_STEP_BYTES == 256 * RR.MIB and RR.MEM_FLOOR_BYTES == RR.GIB and RR.K_MIN == 3 and \
        RR.K_SPREAD_FACTOR == 2 and RR.MEASUREMENT_CAP_BYTES == 3 * RR.GIB and RR.MEASUREMENT_POLL_S == 2 and \
        RR.MEASUREMENT_WORKERS == 5 and RR.RERUN_CAP_FACTOR == 2 and RR.POLL_FRACTION == F(1, 10) and \
        RR.POLL_MIN_S == F(1, 2) and RR.SAMPLER_MAX_INTERVAL_S == F(1, 2) and RR.FREE_FLOOR_BYTES == 2 * RR.GIB and \
        RR.READINGS_MIN == 10 and RR.READING_SPACING_S == 30 and RR.CONSECUTIVE_MIN == 3 and \
        RR.EXCL_BASE_PCT == 25 and RR.EXCL_CEILING_PCT == 50 and RR.EXCL_FACTOR == F(5, 4) and \
        RR.EXCL_ROUND_STEP == 5 and \
        RR.SIP_PREFIXES == ("/System/", "/usr/libexec/", "/usr/sbin/", "/sbin/", "/Library/Apple/") and \
        [p.rstrip("/") for p in RR.NEVER_PREFIXES] == ["/Applications", "/Users", "/opt", "/usr/local",
                                                       "/Library/Frameworks", "/usr/bin", "/bin"]
    return {"ok": all(found.values()) and consts, "missing": [p for p, v in found.items() if not v], "consts": consts}


def t_rrules_h3_reproduction():
    """The ratification's own H3 readings (transcription checked against its text) through R-ALLOW over the 39 names of
    35cabb50 give exactly the item-16 list applied at b0dd8e93."""
    r = Q.h3_reproduction(repo=T.base_store(), cfg=CFG)
    return {"ok": r.get("pass") is True and len(r.get("additions", [])) == 4, "detail": r}


# ------------------------------------------------------------------ QS-* suites and the mutant matrix
def _report(results: dict) -> dict:
    return {"n": len(results), "passed": sum(1 for v in results.values() if v.get("ok")), "results": results}


def t_qs_suite_summary():
    """A suite passes only with > 0 tests, every test ok, consistent counts and exit code 0."""
    good = _report({"t_a": {"ok": True}, "t_b": {"ok": True}})
    one = _report({"t_a": {"ok": True}, "t_b": {"ok": False, "detail": {}}})
    err = _report({"t_a": {"ok": False, "error": "RuntimeError: x"}})
    liar = dict(good, passed=1)
    ok = Q.suite_summary(good, 0)["pass"] is True and Q.suite_summary(good, None)["pass"] is True and \
        Q.suite_summary(good, 1)["pass"] is False and Q.suite_summary(one, 1)["failed"] == ["t_b"] and \
        Q.suite_summary(err, 1)["errors"] == ["t_a"] and Q.suite_summary(_report({}), 0)["pass"] is False and \
        Q.suite_summary(liar, 0)["pass"] is False and Q.suite_summary(None, 0)["pass"] is False
    return {"ok": ok}


PLANTED_SUITE = '''import sys
sys.path.insert(0, {tests!r})
import mbs308_testlib as T
{body}
if __name__ == "__main__":
    T.cli(globals())
'''


def t_qs_suite_runner_planted():
    """run_suite runs a suite file in a fresh process and records its counts: planted passing, failing, erroring and
    empty suites."""
    d = TMP / "qs_planted"
    if d.exists():
        shutil.rmtree(d)
    (d / "tests").mkdir(parents=True)
    bodies = {"pass": "def t_a():\n    return {'ok': True}\ndef t_b():\n    return True\n",
              "fail": "def t_a():\n    return {'ok': True}\ndef t_b():\n    return {'ok': False}\n",
              "error": "def t_a():\n    raise RuntimeError('planted')\n", "empty": "X = 1\n"}
    res = {}
    for k, b in bodies.items():
        (d / "tests" / f"test_planted_{k}.py").write_text(PLANTED_SUITE.format(tests=str(T.NSS / "tests"), body=b))
        res[k] = Q.run_suite(f"tests/test_planted_{k}.py", d / f"{k}.json", dict(T.GENV), d, ns=d)
    ok = res["pass"]["pass"] is True and res["pass"]["n"] == 2 and res["fail"]["pass"] is False and \
        res["fail"]["failed"] == ["t_b"] and res["error"]["pass"] is False and res["error"]["errors"] == ["t_a"] and \
        res["empty"]["pass"] is False and all(r["record_sha256"] for r in res.values())
    return {"ok": ok, "summary": {k: {x: v.get(x) for x in ("pass", "n", "failed", "errors", "rc")}
                                  for k, v in res.items()}}


def t_qs_mutant_summary():
    """QS-MUTANTS passes only when the unmutated code passes, the matrix holds exactly the declared mutants and every
    one is killed BY ASSERTION (not by an error, a timeout or an invalid mutant)."""
    decl = ["A", "B"]
    kill = {"killed": True, "test_passed": False, "error": None}
    good = {"unmutated_all_pass": True, "matrix": {"A": dict(kill), "B": dict(kill)}}
    by_error = {"unmutated_all_pass": True, "matrix": {"A": dict(kill), "B": dict(kill, error="TimeoutExpired")}}
    invalid = {"unmutated_all_pass": True, "matrix": {"A": dict(kill), "B": {"killed": False,
                                                                           "error": "INVALID MUTANT"}}}
    surv = {"unmutated_all_pass": True, "matrix": {"A": dict(kill), "B": {"killed": False, "test_passed": True}}}
    unmut = dict(good, unmutated_all_pass=False)
    missing = {"unmutated_all_pass": True, "matrix": {"A": dict(kill)}}
    extra = {"unmutated_all_pass": True, "matrix": {"A": dict(kill), "B": dict(kill), "C": dict(kill)}}
    s = lambda r, d=decl, rc=0: Q.mutant_summary(r, d, rc)  # noqa: E731
    declared = Q.declared_mutants(T.NSS / "tests" / "test_mbs308_mutants.py")
    ok = s(good)["pass"] is True and s(good, rc=1)["pass"] is False and s(by_error)["pass"] is False and \
        s(by_error)["killed_otherwise"] == ["B"] and s(invalid)["pass"] is False and s(surv)["pass"] is False and \
        s(unmut)["pass"] is False and s(missing)["pass"] is False and s(extra)["pass"] is False and \
        s(good, d=[])["pass"] is False and s(None)["pass"] is False and \
        len(declared) >= 91 and set(EXPECTED_MUTANTS) <= set(declared) and len(set(declared)) == len(declared)
    return {"ok": ok, "declared": len(declared)}


def t_qs_resume_decoy_summary():
    """QS-RESUME-DECOY (builder5, brief 50): the verifier's summary of the case runner's value-free record passes only
    for an OFFICIAL-form record that says pass, with target_evaluations 0 and exit code 0 (or none known); a dev-form
    record, a failing record, a record without target_evaluations 0, a non-zero exit code, a non-boolean `pass` and no
    record never pass. The case is BUILT (no longer PENDING) and its runner exists; QS-DISK is a configured suite."""
    good = {"pass": True, "form": "official", "target_evaluations": 0, "k": 3, "served": 3, "computed": 4}
    s = Q.resume_decoy_summary
    ok = s(good, 0)["pass"] is True and s(good, None)["pass"] is True and \
        s(dict(good, form="dev"), 0)["pass"] is False and s(dict(good, **{"pass": False}), 0)["pass"] is False and \
        s(dict(good, target_evaluations=1), 0)["pass"] is False and \
        s({k: v for k, v in good.items() if k != "target_evaluations"}, 0)["pass"] is False and \
        s(good, 1)["pass"] is False and s(None, 0)["pass"] is False and s({"pass": "yes"}, 0)["pass"] is False and \
        "QS-RESUME-DECOY" in Q.BUILT_CASES and "QS-RESUME-DECOY" not in Q.PENDING_CASES and \
        (T.NSS / Q.RESUME_DECOY_RUNNER).is_file() and "QS-DISK" in Q.SUITE_CASES and \
        CFG["suites"].get("QS-DISK") == "tests/test_mbs308_disk.py"
    return {"ok": ok}


# the matrix at integration (brief 49): builder2's / builder3's M01-M57 and builder4's MQ01-MQ34 (later additions allowed)
EXPECTED_MUTANTS = [f"M{i:02d}" for i in range(1, 58)] + [f"MQ{i:02d}" for i in range(1, 35)]


# ------------------------------------------------------------------ QC09-S
def t_qc09s_guard():
    """QC09-S on the code under test: the one-line diff, the driver's binding and pin, DECOY refusals and the arming
    sequence in a throw-away repository (MB r1's marker never arms)."""
    w = TMP / "qc09"
    w.mkdir(parents=True, exist_ok=True)
    r = Q.qc09_guard(w, repo=T.base_store(), code=CODE, mbr1_guard_pin=guard_pin())
    return {"ok": r["pass"] is True and r["child"].get("admitted_pairs", 0) > 0,
            "detail": {k: v for k, v in r.items() if k != "child"}, "child": r["child"]}


def _code_copy(tag: str) -> Path:
    d = TMP / tag / "code"
    if d.parent.exists():
        shutil.rmtree(d.parent)
    shutil.copytree(CODE, d, ignore=shutil.ignore_patterns("__pycache__"))
    return d


def t_qc09s_planted_guard_failures():
    """Planted guard faults make QC09-S fail: (a) the guard's marker reverted to MB r1's ref (MB r1's marker then arms);
    (b) label 307 dropped from the quarantine."""
    a = _code_copy("qc09_plant_a")
    g = (a / "mbs308_guard.py").read_text()
    (a / "mbs308_guard.py").write_text(g.replace('"refs/p5y-k5-cell308-mbs-r1/target-consumed"',
                                                 '"refs/p5y-k5-cell308-mb-r1/target-consumed"'))
    ra = Q.qc09_guard(a.parent, repo=T.base_store(), code=a, mbr1_guard_pin=guard_pin())
    b = _code_copy("qc09_plant_b")
    g = (b / "mbs308_guard.py").read_text()
    (b / "mbs308_guard.py").write_text(g.replace("frozenset({305, 306, 307, 308, 309})",
                                                 "frozenset({305, 306, 308, 309})"))
    rb = Q.qc09_guard(b.parent, repo=T.base_store(), code=b, mbr1_guard_pin=guard_pin())
    ok = ra["pass"] is False and ra["diff_is_exactly_the_marker_line"] is False and \
        ra["child"].get("arming_refusals", {}).get("mbr1_marker_naming_the_grant_at_head") is False and \
        rb["pass"] is False and rb["child"].get("labels_305_309_refused") is False
    return {"ok": ok}


# ------------------------------------------------------------------ QC11-S
PLANTS_QC11 = {   # check -> (exact fragment of the driver, replacement): each planted break must flip its check
    "exactly_one_marker_write_a_cas_in_run_execute": (
        "        jr = STATE.Journal(st, jid, jrec)\n        me = HOST.identity()\n",
        "        jr = STATE.Journal(st, jid, jrec)\n        st.cas_ref(CONSUMED_REF, grant[\"grant_commit\"], None)\n"
        "        me = HOST.identity()\n"),
    "post_marker_prints_value_free": (
        "        close_host(common)\n        data = serialize(common)\n",
        "        close_host(common)\n        print(f\"MBS308 {tgt}\")\n        data = serialize(common)\n"),
    "target_control_only_in_pre_marker_common_after_check_grant": (
        "    check_clean()\n    st = store()\n",
        "    check_clean()\n    control(None, None, TARGET_CELL)\n    st = store()\n"),
    "resume_arms_before_reading_checkpoints": (
        "        GUARD.arm_target(str(REPO), grant[\"grant_commit\"], [(F(a), F(b)) for a, b in prep[\"pairs\"]])\n"
        "        ck = STATE.Checkpointer(", "        ck = STATE.Checkpointer("),
    "cli_passes_no_injection": ("            return run_execute(own_sha)\n",
                                "            return run_execute(own_sha, evaluator=None)\n"),
    "eval_cap_per_attempt_on_awake_time": ("    cap = STATE.AwakeCap(EVAL_CAP_S).start()\n",
                                           "    cap = STATE.AwakeCap(10 ** 9).start()\n"),
    "no_file_write_in_target_path": ("    \"\"\"The ONE scientific evaluation (after the marker).\"\"\"\n",
                                     "    \"\"\"The ONE scientific evaluation (after the marker).\"\"\"\n"
                                     "    Path(\"planted\").write_text(\"x\")\n"),
}


def t_qc11s_structure_and_planted_breaks():
    """QC11-S's driver structure holds on the code under test, and each planted break flips its own check."""
    src = (CODE / "mbs308_driver.py").read_text()
    host = (CODE / "mbs308_host.py").read_text()
    base = Q.qc11_driver_structure(src, host)
    flips = {}
    for check, (old, new) in PLANTS_QC11.items():
        if src.count(old) != 1:
            flips[check] = f"fragment occurs {src.count(old)} times"
            continue
        flips[check] = Q.qc11_driver_structure(src.replace(old, new), host).get(check) is False
    return {"ok": bool(base) and all(v is True for v in base.values()) and all(v is True for v in flips.values()),
            "base_failing": [k for k, v in base.items() if v is not True], "flips": flips}


def _science_tree(tag: str) -> Path:
    """MB r1's science modules and the F2 / F3 files at 21e99cf0, extracted from the base store (read only)."""
    d = TMP / tag
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    bs = T.base_store()
    pinned = Q.git_show_bytes(T.BASE, T.NSF_REL + "/code/mb308_pinned.py", repo=bs).decode()
    pc = Q.module_constants(pinned)
    paths = [T.NSF_REL + "/code", pc["INDEP_PIN"][0], pc["TUPLE_PIN"][0]]
    arc = subprocess.run(["/usr/bin/git", "-C", str(bs), "archive", T.BASE, *paths], capture_output=True,
                         env=T.GENV, check=True).stdout
    subprocess.run(["/usr/bin/tar", "-x", "-C", str(d)], input=arc, check=True, capture_output=True)
    return d


def t_qc11s_science_bytes():
    """MB r1's science-byte checks pass on the pinned bytes; a planted byte change fails the pin first."""
    d = _science_tree("qc11_sci")
    src = (CODE / "mbs308_driver.py").read_text()
    r = Q.qc11_science_bytes(d, src, T.NSS)
    word = "KNOCK" + "OUT_RECON"                                # built at run time, never written
    nsp = TMP / "qc11_ns"
    if nsp.exists():
        shutil.rmtree(nsp)
    (nsp / "tests").mkdir(parents=True)
    (nsp / "tests" / "planted.py").write_text(f"X = '{word}'\n")
    hit_other = Q.qc11_science_bytes(d, src, nsp)["no_successor_code_names_the_research_reconstructions"] is False
    (nsp / "tests" / "planted.py").unlink()
    st = (T.NSS / "tests" / "test_mbs308_static.py").read_text()
    (nsp / "tests" / "test_mbs308_static.py").write_text(st)
    exempt_ok = Q.qc11_science_bytes(d, src, nsp)["no_successor_code_names_the_research_reconstructions"] is True
    (nsp / "tests" / "test_mbs308_static.py").write_text(st + f"\n# {word}\n")
    hit_outside = Q.qc11_science_bytes(d, src, nsp)["no_successor_code_names_the_research_reconstructions"] is False
    p = d / T.NSF_REL / "code" / "mb308_consumer.py"
    p.write_bytes(p.read_bytes() + b"\n# planted\n")
    r2 = Q.qc11_science_bytes(d, src, T.NSS)
    checks = {k: v for k, v in r.items() if not k.startswith("_")}
    exc = r.get("_named_exception") or []
    return {"ok": len(checks) > 10 and all(v is True for v in checks.values()) and hit_other and exempt_ok and
            hit_outside and
            r2["science_bytes_are_the_pinned_bytes"] is False and len(r2) == 1 and
            all(e["file"] == "test_mbs308_static.py" and e["function"] == "t_mbs12_static_carryovers" for e in exc),
            "failing": [k for k, v in checks.items() if v is not True], "named_exception": exc}


# ------------------------------------------------------------------ QC12-S
PATS = [r"7\." + "0" * k + "3" for k in range(1, 26)]              # neutral planted patterns (never a tail figure)


def t_qc12s_tail_scan():
    """The tail-figure scan on planted patterns: clean files pass; a hit in any file fails (file named, counted); the
    timing-key exemption applies only to JSON under the post-freeze directories; planted controls fire."""
    pd = Q.post_freeze_dirs(CODE)
    clean = [(NS_REL + "/code/x.py", "nothing here"),
             (NS_REL + "/qualification/MBS308_X.json", json.dumps({"t": {"seconds": "7.003", "ok": True}}))]
    r0 = Q.qc12_core(clean, PATS, post_dirs=pd)
    r1 = Q.qc12_core(clean + [(NS_REL + "/protocol/P.md", "value 7.0003 here")], PATS, post_dirs=pd)
    r2 = Q.qc12_core(clean + [(NS_REL + "/config/C.json", json.dumps({"seconds": "7.003"}))], PATS, post_dirs=pd)
    r3 = Q.qc12_core(clean + [(NS_REL + "/qualification/Y.json", json.dumps({"value": "7.003"}))], PATS, post_dirs=pd)
    r4 = Q.qc12_core(clean, PATS[:20], post_dirs=pd)
    ok = r0["pass"] is True and r0["timing_field_exemptions"] and r0["planted_control_fires"] is True and \
        r1["pass"] is False and list(r1["tail_figure_hits"]) == [NS_REL + "/protocol/P.md"] and \
        r2["pass"] is False and r3["pass"] is False and r4["pass"] is False and \
        all(isinstance(v, int) for v in r1["tail_figure_hits"].values())
    return {"ok": ok}


def _tokens():
    rec = {"r": [f"{1000000 + 37 * i}/1000000" for i in range(12)]}
    toks: set = set()
    Q.tokenise(rec, toks)
    geom: set = set()
    Q.tokenise({"left": "3141593/1000000", "right": "2718282/1000000"}, geom)
    return toks | geom, geom


def t_qc12s_token_scan():
    """The record-token scan on PLANTED tokens: geometry tokens exempt only in the guard source and inside the
    manifest's guard field; any other occurrence of any token fails; the manifest-copy controls fire."""
    pd = Q.post_freeze_dirs(CODE)
    toks, geom = _tokens()
    g = sorted(geom)
    man = json.dumps({"guard": {"cell308_cover": g}, "schema": "x"}, indent=1)
    files = [(Q.GUARD_REL, f"# {g[0]} {g[1]}"), (Q.MANIFEST_REL, man), (NS_REL + "/code/x.py", "clean")]
    r0 = Q.qc12_core(files, PATS, post_dirs=pd, toks=toks, geom=geom, manifest_text=man)
    non_geo = sorted(toks - geom)[3]
    r1 = Q.qc12_core(files + [(NS_REL + "/tests/t.py", non_geo)], PATS, post_dirs=pd, toks=toks, geom=geom,
                     manifest_text=man)
    man2 = man + "\n" + g[0]
    r2 = Q.qc12_core([(Q.MANIFEST_REL, man2)], PATS, post_dirs=pd, toks=toks, geom=geom, manifest_text=man)
    r3 = Q.qc12_core([(NS_REL + "/code/mbs308_host.py", g[0])], PATS, post_dirs=pd, toks=toks, geom=geom,
                     manifest_text=man)
    r4 = Q.qc12_core(files, PATS, post_dirs=pd, toks=toks, geom=geom, manifest_text=None)
    ok = r0["pass"] is True and r0["geometry_exemptions"] and r0["planted_non_geometry_token_in_manifest_copy_fires"] \
        and r0["planted_geometry_token_outside_guard_field_fires"] and \
        r0["planted_geometry_token_inside_guard_field_exempt"] and \
        r1["pass"] is False and r1["record_token_hit_files"] == [NS_REL + "/tests/t.py"] and \
        r2["pass"] is False and r3["pass"] is False and r4["pass"] is False
    return {"ok": ok}


def t_qc12s_pattern_pin():
    """The pattern file is read at run time only through its pin (sha256 and blob at HEAD): a planted pin in a
    throw-away repository reads; a tampered file or a wrong pin refuses."""
    repo = mini_repo("qc12_pin")
    rel = Q.PATTERNS_PIN[0]
    raw = json.dumps({"patterns": PATS}).encode()
    commit(repo, {rel: raw}, "planted patterns")
    b = mg(repo, "rev-parse", f"HEAD:{rel}")
    saved = Q.PATTERNS_PIN
    res = {}
    try:
        Q.PATTERNS_PIN = (rel, sha(raw), b[:12])
        res["reads"] = Q.tail_patterns(repo) == PATS
        (repo / rel).write_bytes(raw + b" ")
        try:
            Q.tail_patterns(repo)
            res["tampered_refused"] = False
        except ValueError:
            res["tampered_refused"] = True
        (repo / rel).write_bytes(raw)
        Q.PATTERNS_PIN = (rel, "0" * 64, b[:12])
        try:
            Q.tail_patterns(repo)
            res["wrong_pin_refused"] = False
        except ValueError:
            res["wrong_pin_refused"] = True
    finally:
        Q.PATTERNS_PIN = saved
    return {"ok": all(res.values()) and len(res) == 3, "res": res}


# ------------------------------------------------------------------ QC13-S
def t_qc13s_records():
    """Governance records by commit and path in a throw-away repository: a verdict on line 2 exactly once, a pinned
    sha256, a named ledger line, presence, the branch; every failure mode is reported (never the text)."""
    repo = mini_repo("qc13")
    lines = [json.dumps({"agent": "coord", "purpose": "PLANTED RULING: option X (planted)"})]
    c1 = commit(repo, {"r/A.md": "# t\nPLANTED_ACCEPTED\nbody\n", "r/B.md": "# t\n\nPLANTED_ACCEPTED\n",
                       "r/C.md": "# t\nPLANTED_ACCEPTED\nPLANTED_ACCEPTED\n", "r/L.jsonl": "\n".join(lines) + "\n",
                       "r/D.md": "planted presence\n"}, "planted records")
    mg(repo, "update-ref", "refs/heads/research", c1)
    mg(repo, "checkout", "-q", "--orphan", "other")
    c2 = commit(repo, {"r/E.md": "# t\nPLANTED_ACCEPTED\n"}, "off-branch record")
    show = lambda c, p: Q.git_show_bytes(c, p, repo=repo)  # noqa: E731
    anc = lambda c, ref: Q.git_rc("merge-base", "--is-ancestor", c, ref, repo=repo) == 0  # noqa: E731
    ref = "refs/heads/research"
    rec = lambda **k: Q.check_record(dict({"id": "x", "ref": ref, "kind": "verdict",  # noqa: E731
                                           "verdict": "PLANTED_ACCEPTED"}, **k), show=show, is_ancestor=anc)
    a_sha = sha((repo / "r/A.md").read_bytes()) if (repo / "r/A.md").exists() else \
        sha(Q.git_show_bytes(c1, "r/A.md", repo=repo))
    exp = {
        "ok_verdict": (rec(commit=c1, path="r/A.md"), "OK"),
        "ok_verdict_and_sha": (rec(commit=c1, path="r/A.md", sha256=a_sha), "OK"),
        "verdict_not_on_line_2": (rec(commit=c1, path="r/B.md"), "VERDICT_MISMATCH"),
        "verdict_twice": (rec(commit=c1, path="r/C.md"), "VERDICT_MISMATCH"),
        "wrong_verdict": (rec(commit=c1, path="r/A.md", verdict="PLANTED_REJECTED"), "VERDICT_MISMATCH"),
        "sha_mismatch": (rec(commit=c1, path="r/A.md", sha256="0" * 64), "SHA_MISMATCH"),
        "missing_path": (rec(commit=c1, path="r/Z.md"), "MISSING"),
        "pending": (rec(commit=None, path=None), "PENDING_RECORD"),
        "not_on_ref": (rec(commit=c2, path="r/E.md"), "NOT_ON_REF"),
        "presence": (rec(commit=c1, path="r/D.md", kind="presence"), "OK"),
        "jsonl_line": (rec(commit=c1, path="r/L.jsonl", kind="jsonl_line",
                           match={"agent": "coord", "purpose_prefix": "PLANTED RULING: option X"}), "OK"),
        "jsonl_line_missing": (rec(commit=c1, path="r/L.jsonl", kind="jsonl_line",
                                   match={"agent": "coord", "purpose_prefix": "PLANTED RULING: option Y"}),
                               "LINE_MISSING"),
        "unknown_kind": (rec(commit=c1, path="r/D.md", kind="other"), "UNKNOWN_KIND")}
    got = {k: (r["status"], r["pass"]) for k, (r, _) in exp.items()}
    ok = all(got[k] == (want, want == "OK") for k, (_, want) in exp.items()) and \
        not any("PLANTED_ACCEPTED" in json.dumps(r) for r, _ in exp.values())
    return {"ok": ok, "got": got}


def t_qc13s_ledger_and_core():
    """The successor agents' ledger lines (pre-grant classes, 0 target, no LEAK_FLAG) and the QC13-S decision: a record
    not yet named (the user's freeze decision) keeps QC13-S failing."""
    good = {"agent": "builder4", "class": "SYNTHETIC_VALIDATION", "new_target_evaluations": 0,
            "target_equivalent_proxies": 0, "target_informed_optimisation": 0}
    other = {"agent": "someone", "class": "TARGET_EVALUATION", "new_target_evaluations": 1}
    L = lambda *rows: "\n".join(json.dumps(r) for r in rows) + "\n"  # noqa: E731
    agents = {"builder4"}
    lc = {"good": Q.ledger_check(L(good, other), agents)["pass"] is True,
          "target": Q.ledger_check(L(good, dict(good, new_target_evaluations=1)), agents)["pass"] is False,
          "class": Q.ledger_check(L(dict(good, **{"class": "TARGET_EVALUATION"})), agents)["pass"] is False,
          "leak": Q.ledger_check(L(dict(good, LEAK_FLAG=True)), agents)["pass"] is False,
          "proxy": Q.ledger_check(L(dict(good, target_equivalent_proxies=1)), agents)["pass"] is False,
          "none": Q.ledger_check(L(other), agents)["pass"] is False,
          "unreadable": Q.ledger_check(None, agents)["pass"] is False}
    okr, pend = {"id": "A", "status": "OK", "pass": True}, {"id": "U", "status": "PENDING_RECORD", "pass": False}
    P, G, LD = {"pass": True}, {"pass": True}, {"pass": True}
    core = {"all": Q.qc13_core(P, G, LD, [okr])["pass"] is True,
            "pending": Q.qc13_core(P, G, LD, [okr, pend])["pass"] is False and
            Q.qc13_core(P, G, LD, [okr, pend])["pending_records"] == ["U"],
            "pre": Q.qc13_core({"pass": False}, G, LD, [okr])["pass"] is False,
            "gov": Q.qc13_core(P, {"pass": False}, LD, [okr])["pass"] is False,
            "ledger": Q.qc13_core(P, G, {"pass": False}, [okr])["pass"] is False,
            "empty": Q.qc13_core(P, G, LD, [])["pass"] is False}
    cfg_pend = [r["id"] for r in CFG["governance_records"] if not r.get("commit")]
    named = {r["id"]: r for r in CFG["governance_records"] if r.get("commit")}
    owner_named = all(named.get(i, {}).get("sha256") for i in ("USER_FREEZE_DECISION", "USER_OWNER_SUPPLEMENT_1",
                                                               "USER_OWNER_SUPPLEMENT_2"))
    return {"ok": all(lc.values()) and all(core.values()) and cfg_pend == ["IMPLEMENTATION_REVIEW_ACCEPTED"] and
            owner_named, "ledger": lc, "core": core, "un_named": cfg_pend}


# ------------------------------------------------------------------ the manifest writer and Q8-S
def _q8_repo():
    repo = mini_repo("q8")
    ns = repo / NS_REL
    old = commit(repo, {"pinned/old.txt": "commit-pinned bytes\n"}, "older")
    files = {NS_REL + "/code/a.py": "A = 1\n", NS_REL + "/config/c.json": "{}\n",
             NS_REL + "/protocol/MBS308_PROTOCOL_DRAFT.md": "# p\n", NS_REL + "/BUILD_REPORT.md": "# r\n",
             NS_REL + "/qualification/q.json": "{}\n", NS_REL + "/code/__pycache__/z.pyc": b"\0",
             "ext/e1.txt": "external one\n", "ext/e2.txt": "external two\n"}
    commit(repo, files, "planted namespace")
    mp = ns / "protocol" / "MBS308_FREEZE.json"
    pd = Q.post_freeze_dirs(CODE)
    ext_pins = {"x:e1": ("ext/e1.txt", sha(b"external one\n"), None), "x:e2": ("ext/e2.txt", None, None)}
    cpins = {"c:old": (old, "pinned/old.txt", sha(b"commit-pinned bytes\n"))}
    man = {"schema": MF.SCHEMA, "frozen_files": MF.frozen_files(repo, ns, mp, pd),
           "external_files": MF.external_files(repo, ext_pins), "commit_pinned_files": MF.commit_files(repo, cpins),
           "driver": {"sha256": "d" * 64}}
    mp.write_text(json.dumps(man, indent=1, sort_keys=True) + "\n")
    commit(repo, {NS_REL + "/protocol/MBS308_FREEZE.json": mp.read_text()}, "planted freeze")
    return repo, ns, mp, pd, ext_pins, cpins, man


def t_manifest_core_and_q8_core():
    """The writer's core lists every namespace file except the manifest, __pycache__ and the post-freeze directories,
    refuses on a pin mismatch; Q8-S's decision passes on the planted freeze and fails on each planted fault."""
    repo, ns, mp, pd, ext_pins, cpins, man = _q8_repo()
    listed = {str(p.relative_to(repo)) for p in MF.namespace_files(ns, mp, pd)}
    want = {NS_REL + "/code/a.py", NS_REL + "/config/c.json", NS_REL + "/protocol/MBS308_PROTOCOL_DRAFT.md",
            NS_REL + "/BUILD_REPORT.md"}
    req = [NS_REL + "/code/a.py"]

    def q8(m=None, **kw):
        a = dict(repo=repo, on_disk={str(p.relative_to(repo)) for p in MF.namespace_files(ns, mp, pd)},
                 expect_ext=ext_pins, expect_commit=cpins, expect_recorded={"driver.sha256": "d" * 64},
                 bindings_ok=True, required=req, schema=MF.SCHEMA)
        a.update(kw)
        return Q.q8_core(man if m is None else m, **a)
    res = {"writer_lists_exactly": listed == want, "clean": q8()["pass"] is True}
    for key, fn in (("refuse_ext_pin", lambda: MF.external_files(repo, {"k": ("ext/e1.txt", "0" * 64, None)})),
                    ("refuse_ext_blob", lambda: MF.external_files(repo, {"k": ("ext/e1.txt", None, "ffff")})),
                    ("refuse_commit_pin", lambda: MF.commit_files(repo, {"k": ("0" * 40, "pinned/old.txt", None)}))):
        try:
            fn()
            res[key] = False
        except MF.ManifestRefusal:
            res[key] = True
    res["recorded_mismatch"] = q8(expect_recorded={"driver.sha256": "e" * 64})["recorded_mismatches"] == \
        ["driver.sha256"]
    res["bindings"] = q8(bindings_ok=False)["pass"] is False
    res["required"] = q8(required=[NS_REL + "/code/missing.py"])["pass"] is False
    res["schema"] = q8(dict(man, schema="other"))["pass"] is False
    res["unexpected_external"] = q8(dict(man, external_files=dict(man["external_files"], extra={})))["pass"] is False
    res["unexpected_commit_pin"] = q8(dict(man, commit_pinned_files=dict(man["commit_pinned_files"], x={})))[
        "pass"] is False
    res["missing_external"] = q8(expect_ext=dict(ext_pins, **{"x:e3": ("ext/e3.txt", None, None)}))["pass"] is False
    (ns / "code" / "a.py").write_text("A = 2\n")
    r = q8()
    res["tampered_file"] = r["mismatches"] == [NS_REL + "/code/a.py"] and r["pass"] is False
    (ns / "code" / "a.py").write_text("A = 1\n")
    (ns / "code" / "new.py").write_text("B = 1\n")
    r = q8()
    res["unlisted_file"] = r["unlisted_files"] == [NS_REL + "/code/new.py"] and r["pass"] is False
    (ns / "code" / "new.py").unlink()
    (repo / "ext/e2.txt").write_text("external two, tampered\n")
    r = q8()
    res["tampered_external"] = r["external_mismatches"] == ["x:e2"] and r["pass"] is False
    return {"ok": all(v is True for v in res.values()), "res": res}


# ------------------------------------------------------------------ preconditions and the CLI
def t_preconditions_core():
    """official: HEAD = freeze, no review / grant / result / post-freeze record, no campaign ref, MB r1's state exact,
    no spool result, tracked and namespace clean, the host ready; review: the qualification commit on the freeze;
    dev: any HEAD. Each planted fault refuses."""
    host = {"host_on_ac": True, "platform_pins": True, "section8_preflight_gates": True,
            "sleep_channels_available": True}
    base = {"freeze_commit": "f" * 40, "head": "f" * 40, "head_parent": "e" * 40, "head_changed": [],
            "forbidden_present": [], "campaign_refs": [], "mbr1_state_ok": True, "spool_result_entries": [],
            "tracked_clean": True, "namespace_clean_including_ignored": True, "host": host}
    P = lambda mode, **k: Q.preconditions_core(mode, dict(base, **k))["pass"]  # noqa: E731
    qual = dict(head="a" * 40, head_parent="f" * 40, head_changed=[NS_REL + "/qualification/MBS308_QUALIFICATION.json"])
    res = {"official_ok": P("official") is True, "head": P("official", head="a" * 40) is False,
           "review_file": P("official", forbidden_present=[NS_REL + "/review"]) is False,
           "ref": P("official", campaign_refs=["refs/p5y-k5-cell308-mbs-r1/journal"]) is False,
           "mbr1": P("official", mbr1_state_ok=False) is False,
           "spool": P("official", spool_result_entries=["result.json"]) is False,
           "dirty": P("official", tracked_clean=False) is False,
           "ignored": P("official", namespace_clean_including_ignored=False) is False,
           "host_missing": P("official", host={}) is False,
           "host_gate": P("official", host=dict(host, section8_preflight_gates=False)) is False,
           "review_on_qual_commit": P("review", **qual) is True,
           "review_other_file": P("review", **dict(qual, head_changed=qual["head_changed"] + ["x"])) is False,
           "review_ignores_host": P("review", host={}) is True,
           "dev_any_head": P("dev", head="a" * 40, tracked_clean=False) is True,
           "dev_forbidden": P("dev", forbidden_present=["x"]) is False}
    return {"ok": all(res.values()), "res": res}


def t_cli_refusals():
    """The verifier and the manifest writer refuse bad invocations before touching anything."""
    q, m = str(CODE / "mbs308_qualify.py"), str(CODE / "mbs308_manifest.py")
    w = str(TMP / "cli_work")
    runs = {"no_work": ([q, "--dev", "--out", str(TMP / "o.json")], "--work"),
            "dev_without_out": ([q, "--dev", "--work", w], "--out"),
            "official_with_only": ([q, "--work", w, "--only", "QC11-S"], "review / dev options"),
            "record_scan_in_review": ([q, "--review", "--record-scan", "--work", w, "--out", str(TMP / "o.json")],
                                      "--record-scan"),
            "dev_and_review": ([q, "--dev", "--review", "--work", w, "--out", str(TMP / "o.json")], "exclude"),
            "out_inside_repository": ([q, "--dev", "--work", w, "--out", str(Q.REPO / "x.json")], "outside"),
            "manifest_without_mode": ([m], "exactly one"),
            "manifest_out_inside_repository": ([m, "--out", str(MF.REPO / "x.json")], "outside")}
    res = {}
    for k, (args, word) in runs.items():
        p = subprocess.run([T.PY, "-I", "-S", "-B", *args], capture_output=True, text=True, env=dict(T.GENV),
                           stdin=subprocess.DEVNULL, timeout=120)
        res[k] = p.returncode == 2 and "REFUSED" in p.stdout and word in p.stdout
    return {"ok": all(res.values()), "res": res}


# ------------------------------------------------------------------ one sparse sandbox: the production paths
PLANTED_OWNER = ("# planted user decision (a test stand-in; never a ruling)\n",
                 "# planted owner supplement (a test stand-in; never a ruling)\n",
                 "# planted owner supplement 2 (a test stand-in; never a ruling)\n")
OWNER_IDS = ("USER_FREEZE_DECISION", "USER_OWNER_SUPPLEMENT_1", "USER_OWNER_SUPPLEMENT_2")
SPARSE_BASE = ("/" + T.NSF_REL + "/code/", "/" + NS_REL + "/", "/" + Q.PATTERNS_PIN[0])


def _plumb_commit(root: Path, files: dict, msg: str) -> str:
    """A commit on a PLANTED branch of the sandbox, made with plumbing (the worktree is not touched)."""
    ents = []
    for name, data in sorted(files.items()):
        b = subprocess.run(["/usr/bin/git", "-C", str(root), "hash-object", "-w", "--stdin"], input=data.encode(),
                           capture_output=True, check=True, env=T.GENV).stdout.decode().strip()
        ents.append(f"100644 blob {b}\t{name}")
    tree = subprocess.run(["/usr/bin/git", "-C", str(root), "mktree"], input="\n".join(ents) + "\n", text=True,
                          capture_output=True, check=True, env=T.GENV).stdout.strip()
    return mg(root, "commit-tree", tree, "-m", msg)


def sparse_sandbox(tag: str) -> dict:
    """A `--shared` clone of the separate base store (never the real store), sparse: MB r1's code, this namespace
    (copied from the code under test and tests / protocol / config), the pattern file and every external pin the
    manifest writer lists. MB r1's recorded state is planted as the test library does. The governance records and the
    ledger of the configuration are replaced by PLANTED ones on a planted branch (no real review is ever read); the
    implementation-review record stays un-named (PENDING); the three owner records are PLANTED ones bound by their
    sha256 (brief 54; owner supplement 2). Planted designated-measurement files stand in for the section-11.2 evidence the freeze
    requires (Q8-S lists them; their content is never read here)."""
    tmp = TMP / tag
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)
    bs = T.base_store()
    root = tmp / "sbx"
    subprocess.run(["/usr/bin/git", "clone", "-q", "--shared", "--no-checkout", str(bs), str(root)], check=True,
                   env=T.GENV, capture_output=True)
    alt = (root / ".git/objects/info/alternates").read_text().split()
    if [str(Path(a).resolve()) for a in alt] != [str((bs / "objects").resolve())]:
        raise RuntimeError("the sandbox must borrow objects from the base store only")
    mg(root, "config", "user.name", "sandbox")
    mg(root, "config", "user.email", "sandbox@invalid")
    mg(root, "sparse-checkout", "set", "--no-cone", *SPARSE_BASE)
    mg(root, "checkout", "-q", "-B", T.BRANCH, T.BASE)
    mg(root, "update-ref", T.MBR1_MARKER, T.MBR1_TARGET)
    mg(root, "branch", "-f", "p5y-k5-cell308-mb-r1", T.BASE)
    dst = root / NS_REL
    for d in ("tests", "protocol", "config"):
        shutil.copytree(T.NSS / d, dst / d, ignore=shutil.ignore_patterns("__pycache__"), dirs_exist_ok=True)
    shutil.copytree(CODE, dst / "code", ignore=shutil.ignore_patterns("__pycache__"), dirs_exist_ok=True)
    for f in T.NSS.glob("*.md"):
        shutil.copy2(f, dst / f.name)
    (dst / "protocol/MBS308_FREEZE.json").unlink(missing_ok=True)
    (dst / "evidence_prefreeze").mkdir(exist_ok=True)
    for name in ("MBS308_RRULES_DESIGNATED.json", "MBS308_RRULES_DERIVATION.json"):
        (dst / "evidence_prefreeze" / name).write_text(json.dumps({"planted_by_a_test": True}) + "\n")
    # planted governance records and ledger (a planted branch; plumbing only)
    led = "\n".join(json.dumps({"agent": "builder4", "class": "SYNTHETIC_VALIDATION", "new_target_evaluations": 0,
                                "target_equivalent_proxies": 0, "target_informed_optimisation": 0,
                                "purpose": p}) for p in ("planted line", "PLANTED RULING: option B")) + "\n"
    pc = _plumb_commit(root, {"A.md": "# planted\nPLANTED_ACCEPTED\n", "L.jsonl": led, "P.md": "planted\n",
                              "U.md": PLANTED_OWNER[0], "V.md": PLANTED_OWNER[1], "W.md": PLANTED_OWNER[2]},
                       "planted governance records")
    mg(root, "update-ref", "refs/heads/planted-research", pc)
    cfg = json.loads((dst / "config/MBS308_QUALIFICATION_CASES.json").read_text())
    for r in cfg["governance_records"]:
        r["ref"] = "refs/heads/planted-research"
        r.pop("sha256", None)
        if r["id"] == "IMPLEMENTATION_REVIEW_ACCEPTED":
            continue
        if r["id"] in OWNER_IDS:                                # planted owner records, bound by sha256
            i = OWNER_IDS.index(r["id"])
            r.update({"commit": pc, "path": ("U.md", "V.md", "W.md")[i], "sha256": sha(PLANTED_OWNER[i].encode())})
            continue
        if r["kind"] == "verdict":
            r.update({"commit": pc, "path": "A.md", "verdict": "PLANTED_ACCEPTED"})
        elif r["kind"] == "jsonl_line":
            r.update({"commit": pc, "path": "L.jsonl", "match": {"agent": "builder4",
                                                                 "purpose_prefix": "PLANTED RULING: option B"}})
        else:
            r.update({"commit": pc, "path": "P.md"})
    cfg["ledger"] = {"ref": "refs/heads/planted-research", "path": "L.jsonl", "agents": ["builder4"]}
    (dst / "config/MBS308_QUALIFICATION_CASES.json").write_text(json.dumps(cfg, indent=1) + "\n")
    # every external pin the manifest writer lists, added to the sparse set (enumerated in a child process)
    enum = ("import json, sys; sys.path.insert(0, sys.argv[1]); sys.path.insert(1, sys.argv[2]); "
            "import mbs308_driver as D, mbs308_qualify as QF, mbs308_manifest as MF; "
            "print(json.dumps(sorted({v[0] for v in MF.external_pins(D, QF).values()})))")
    p = subprocess.run([T.PY, "-I", "-S", "-B", "-c", enum, str(dst / "code"), str(dst / "tests")],
                       capture_output=True, text=True, env=T.GENV, cwd=str(root), stdin=subprocess.DEVNULL)
    paths = json.loads(p.stdout.strip().splitlines()[-1])
    mg(root, "sparse-checkout", "add", *("/" + x for x in paths))
    w = subprocess.run([T.PY, "-I", "-S", "-B", str(dst / "code/mbs308_manifest.py"), "--freeze"], capture_output=True,
                       text=True, env=T.GENV, cwd=str(root), stdin=subprocess.DEVNULL)
    mg(root, "add", "-f", NS_REL)
    mg(root, "commit", "-q", "-m", "sandbox: synthetic freeze of the MB-S namespace (never in the real repo)")
    return {"root": root, "tmp": tmp, "dst": dst, "pc": pc, "externals": len(paths), "manifest_rc": w.returncode,
            "manifest_out": w.stdout[-300:] + w.stderr[-300:]}


def _dev(sb: dict, only: str, tag: str) -> tuple:
    out = sb["tmp"] / f"{tag}.json"
    p = subprocess.run([T.PY, "-I", "-S", "-B", str(sb["dst"] / "code/mbs308_qualify.py"), "--dev", "--work",
                        str(sb["tmp"] / "work"), "--only", only, "--out", str(out)], capture_output=True, text=True,
                       env=T.GENV, cwd=str(sb["root"]), stdin=subprocess.DEVNULL, timeout=900)
    try:
        return p.returncode, json.loads(out.read_text()), p.stdout[-400:]
    except (OSError, ValueError):
        return p.returncode, None, (p.stdout + p.stderr)[-800:]


def t_integration_sparse_sandbox():
    """The production paths in one sparse sandbox of the base store: the manifest writer --freeze (with the owner
    records and every pin of the carried science cases); the verifier in dev mode runs Q8-S, QC11-S (with MB r1's
    pinned science bytes), QC09-S, QC12-S (the real pinned pattern file; counts only; no record-token scan),
    R_RULES_CONTROLS, QC13-S (planted records), Q1_theory (hashes) and the dev forms of QC01 (never run) and QC05 (a
    loader check: nothing executed): every BUILT case passes except QC13-S, which fails closed on exactly the one
    un-named record and passes once it is named, and fails again on an ALTERED owner record; the dev report never
    passes; a tampered namespace file fails Q8-S; an official run refuses on its preconditions. No science is
    computed (no decoy case is selected)."""
    sb = sparse_sandbox("integration")
    only = "Q8-S,QC11-S,QC09-S,QC12-S,R_RULES_CONTROLS,QC13-S,QC01,Q1_theory,QC05"
    rc, rep, tail = _dev(sb, only, "dev1")
    c = (rep or {}).get("cases", {})
    first = rep is not None and rc == 0 and rep["dev_mode"] is True and rep["pass"] is False and \
        all(c.get(k, {}).get("pass") is True for k in ("Q8-S", "QC11-S", "QC09-S", "QC12-S", "R_RULES_CONTROLS",
                                                       "Q1_theory")) and \
        c.get("QC13-S", {}).get("pass") is False and \
        sorted(c["QC13-S"]["pending_records"]) == ["IMPLEMENTATION_REVIEW_ACCEPTED"] and \
        c.get("QC01", {}).get("status") == "DEV_FORM" and c.get("QC01", {}).get("pass") is False and \
        c.get("QC05", {}).get("status") == "DEV_FORM" and c.get("QC05", {}).get("pass") is False and \
        c.get("QC05", {}).get("dev_checks_ok") is True and rep.get("pending_user_decision") == []
    # name the record (the worktree config only; dev mode reads it): QC13-S then passes
    cp = sb["dst"] / "config/MBS308_QUALIFICATION_CASES.json"
    cfg = json.loads(cp.read_text())
    for r in cfg["governance_records"]:
        if r["id"] == "IMPLEMENTATION_REVIEW_ACCEPTED":
            r.update({"commit": sb["pc"], "path": "A.md", "verdict": "PLANTED_ACCEPTED"})
    cp.write_text(json.dumps(cfg, indent=1) + "\n")
    rc2, rep2, _ = _dev(sb, "QC13-S", "dev2")
    second = rep2 is not None and rep2["cases"]["QC13-S"]["pass"] is True and rep2["pass"] is False
    for r in cfg["governance_records"]:                 # an ALTERED owner record (another sha256): fails closed
        if r["id"] == "USER_OWNER_SUPPLEMENT_1":
            r["sha256"] = "0" * 64
    cp.write_text(json.dumps(cfg, indent=1) + "\n")
    rc2b, rep2b, _ = _dev(sb, "QC13-S", "dev2b")
    recs = {x["id"]: x for x in (rep2b or {}).get("cases", {}).get("QC13-S", {}).get("records", [])}
    second = second and rep2b is not None and rep2b["cases"]["QC13-S"]["pass"] is False and \
        recs.get("USER_OWNER_SUPPLEMENT_1", {}).get("status") == "SHA_MISMATCH" and \
        recs.get("USER_FREEZE_DECISION", {}).get("status") == "OK" and \
        recs.get("USER_OWNER_SUPPLEMENT_2", {}).get("status") == "OK"
    # an official run refuses on its preconditions (the tracked tree is dirty now): nothing runs, nothing is written
    p = subprocess.run([T.PY, "-I", "-S", "-B", str(sb["dst"] / "code/mbs308_qualify.py"), "--work",
                        str(sb["tmp"] / "work_official")], capture_output=True, text=True, env=T.GENV,
                       cwd=str(sb["root"]), stdin=subprocess.DEVNULL, timeout=600)
    official_refused = p.returncode == 2 and "QUALIFY REFUSED: preconditions" in p.stdout and \
        not (sb["dst"] / "qualification").exists()
    mg(sb["root"], "checkout", "-q", "--", NS_REL + "/config/MBS308_QUALIFICATION_CASES.json")
    pr = sb["dst"] / "protocol/MBS308_PROTOCOL_DRAFT.md"
    pr.write_text(pr.read_text() + "\nplanted edit\n")
    rc3, rep3, _ = _dev(sb, "Q8-S", "dev3")
    tampered = rep3 is not None and rep3["cases"]["Q8-S"]["pass"] is False and \
        rep3["cases"]["Q8-S"]["mismatches"] == [NS_REL + "/protocol/MBS308_PROTOCOL_DRAFT.md"]
    return {"ok": sb["manifest_rc"] == 0 and first and second and official_refused and tampered,
            "manifest": sb["manifest_out"], "externals": sb["externals"], "first": first, "second": second,
            "official_refused": official_refused, "tampered": tampered,
            "cases": {k: v.get("pass") for k, v in c.items()}, "tail": tail if not first else ""}


if __name__ == "__main__":
    T.cli(globals())
