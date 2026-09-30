"""QC11: exactly-once sandbox flows for code/p309_driver.py (package rev. 2b QC11, as amended by rev. 2c).

  python3 tests/test_p309_exactly_once.py   -> evidence/fc6/EXACTLY_ONCE_FLOWS.json (qualification copies it);
                                               exit 0 iff every flow ends as specified

Every sandbox is a light repository under the scratchpad (`git init` + a read-only alternates link to this
repository's objects), sparse-checked-out to the formal namespace, with no remote; it is never pushed.  Flows use ONLY the synthetic TEST names (the guard's TestContext:
TEST_MARKER, TEST_PENDING_REF); the production marker name is never created anywhere.  Stage 1 and Stage 2 are stubs
(post-marker evaluators, controls, job runners): nothing is evaluated for any cell.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from fractions import Fraction as F
from pathlib import Path

FNS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FNS / "code"))
import p309_driver as D  # noqa: E402

G = D.G
REPO = D.REPO
SCRATCH = Path("/tmp/claude-0/-home-user-ReBaseGuard/ea54e9f6-e828-5447-be15-220ef2c329fd/scratchpad/qc11_sandboxes")
SB_BRANCH = "refs/heads/p309-test-sandbox"
NS = D.NS_REL
OWN_SHA = D.sha(Path(D.__file__).read_bytes())


def sh(repo: Path, *a, env=None, input_=None, check=True) -> str:
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update({"GIT_AUTHOR_NAME": "p309-test", "GIT_AUTHOR_EMAIL": "test@invalid", "GIT_COMMITTER_NAME": "p309-test",
              "GIT_COMMITTER_EMAIL": "test@invalid", **(env or {})})
    r = subprocess.run(["git", "-C", str(repo), *a], capture_output=True, input=input_, env=e)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {a[:3]}: {r.stderr.decode()[-300:]}")
    return r.stdout.decode()


def commit(sb: Path, parent, files: dict, msg: str, parents=None, modes=None) -> str:
    with tempfile.NamedTemporaryFile(dir=SCRATCH, delete=False) as tf:
        idx = tf.name
    try:
        env = {"GIT_INDEX_FILE": idx}
        sh(sb, "read-tree", parent, env=env)
        for path, data in files.items():
            blob = sh(sb, "hash-object", "-w", "--stdin", input_=data).strip()
            mode = (modes or {}).get(path, "100644")
            sh(sb, "update-index", "--add", "--cacheinfo", f"{mode},{blob},{path}", env=env)
        tree = sh(sb, "write-tree", env=env).strip()
        ps = []
        for p in (parents or [parent]):
            ps += ["-p", p]
        return sh(sb, "commit-tree", tree, *ps, "-m", msg).strip()
    finally:
        os.unlink(idx)


def new_sandbox(name: str) -> Path:
    """a light sandbox: `git init` + a read-only alternates link to this repository's object store (+ its shallow
    boundary).  This repository is a shallow clone, so `git clone --shared` would copy the whole pack (~445 MB) per
    sandbox.  New objects are written only into the sandbox; nothing is ever written to this repository."""
    sb = SCRATCH / name
    if sb.exists():
        shutil.rmtree(sb)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", str(sb)], check=True, capture_output=True)
    (sb / ".git" / "objects" / "info" / "alternates").write_text(str(REPO / ".git" / "objects") + "\n")
    if (REPO / ".git" / "shallow").exists():
        shutil.copy(REPO / ".git" / "shallow", sb / ".git" / "shallow")
    head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True,
                          check=True).stdout.strip()
    sh(sb, "update-ref", SB_BRANCH, head)
    sh(sb, "symbolic-ref", "HEAD", SB_BRANCH)
    sh(sb, "sparse-checkout", "set", "--no-cone", f"/{NS}/")
    sh(sb, "reset", "-q", "--hard", head)
    return sb


def build_chain(sb: Path, *, grant_over=None, grant_raw=None, drop_review=False, extra_after_freeze=None,
                qual=None, review_text=None, grant_extra_files=None, record_commits=False, grant_parents=None,
                qual_extra=None, review_extra=None, child_after_grant=False) -> dict:
    base = sh(sb, "rev-parse", "HEAD").strip()
    man = (REPO / D.MANIFEST_REL).read_bytes()
    # the sandbox freeze commit must change a frozen path even when the manifest bytes equal the base's (the driver
    # locates the freeze as the last commit touching the frozen directories); the nonce file exists only in sandboxes
    F_ = commit(sb, base, {D.MANIFEST_REL: man, f"{NS}/freeze/SANDBOX_FREEZE_NONCE.txt": sb.name.encode() + b"\n"},
                "sandbox freeze (manifest)")
    c = {"F": F_}
    tip = F_
    if extra_after_freeze:
        tip = commit(sb, tip, extra_after_freeze, "a change after the freeze")
    if record_commits:
        tip = commit(sb, tip, {D.CHECKPOINT_LEDGER_REL: b'{"r":1}\n'}, "checkpoint record")
    q = qual if qual is not None else {"pass": True, "freeze_commit": F_}
    Q = commit(sb, tip, {D.QUAL_REL: json.dumps(q).encode(), **(qual_extra or {})}, "qualification")
    c["Q"] = tip = Q
    if record_commits:
        tip = commit(sb, tip, {D.CHECKPOINT_LEDGER_REL: b'{"r":2}\n'}, "checkpoint record")
    if not drop_review:
        rv = review_text if review_text is not None else "# review\nQUALIFICATION_ACCEPTED\n"
        Rv = commit(sb, tip, {D.QREVIEW_REL: rv.encode(), **(review_extra or {})}, "qualification review")
        c["Rv"] = tip = Rv
    if record_commits:
        tip = commit(sb, tip, {D.CHECKPOINT_LEDGER_REL: b'{"r":3}\n'}, "checkpoint record")
    g = {"schema": "P309_TEST_GRANT/1", "cell": G._TEST_CELL, "driver_sha256": OWN_SHA,
         "frozen_manifest_sha256": hashlib.sha256(man).hexdigest(), "frozen_commit": F_,
         "qualification_commit": Q, "qualification_review_commit": c.get("Rv"),
         "cell_interval": ["1/3", "20/51"], "drift_hull_Ew": ["341/1024", "201/512"]}
    g.update(grant_over or {})
    raw = grant_raw if grant_raw is not None else json.dumps(g, sort_keys=True).encode()
    Gc = commit(sb, tip, {G._TEST_GRANT_PATH: raw, **(grant_extra_files or {})}, "TEST_ONLY grant",
                parents=[tip] + (grant_parents or []))
    c["G"] = tip = Gc
    if child_after_grant:
        tip = commit(sb, tip, {f"{NS}/tests/after.txt": b"x"}, "after the grant")
    sh(sb, "update-ref", SB_BRANCH, tip)
    sh(sb, "symbolic-ref", "HEAD", SB_BRANCH)
    sh(sb, "reset", "-q", "--hard", tip)
    return c


def ctx_of(sb: Path) -> D.ExecContext:
    return D.sandbox_context(sb)


OK_CONTROL = lambda: {"reproduces_C2_exactly": True, "digest": "sandbox"}  # noqa: E731
BAD_CONTROL = lambda: {"reproduces_C2_exactly": False, "digest": "sandbox"}  # noqa: E731
PREP = lambda: {}  # noqa: E731


def ev_ok(con, prep):
    return {"cell": D.TARGET_CELL, "decision": {"mechanical_outcome": "NOT_CLOSED"}}


def ev_raise(con, prep):
    raise RuntimeError("stub failure after the marker")


def ev_indep(con, prep):
    raise D.IndependentCheckFailed("stub reconstruction mismatch")


def ev_bexc(con, prep):
    raise KeyboardInterrupt("stub interrupt")


def ev_unserializable(con, prep):
    return {"cell": D.TARGET_CELL, "decision": {"mechanical_outcome": "NOT_CLOSED"}, "bad": object()}


def execute(sb, evaluator=ev_ok, control=OK_CONTROL, **kw):
    ctx = ctx_of(sb)
    try:
        return D.run_execute(OWN_SHA, ctx=ctx, prepare=PREP, evaluator=evaluator, control=control, **kw)
    except D.Refusal as exc:
        return ("REFUSED", exc.code)


def refs(sb) -> dict:
    return dict(line.split()[::-1] for line in sh(sb, "for-each-ref", "--format=%(objectname) %(refname)").splitlines())


def status_of(sb) -> str | None:
    p = sb / D.RESULT_REL
    return json.loads(p.read_text()).get("status") if p.exists() else None


# --------------------------------------------------------------------------------------------------- the flows
def pre_marker_flows() -> dict:
    R = {}

    def refused(name, code, **kw):
        sb = new_sandbox(name)
        setup = kw.pop("setup", None)
        c = build_chain(sb, **kw)
        if setup:
            setup(sb, c)
        before = (refs(sb), sh(sb, "rev-parse", "HEAD"))
        out = execute(sb)
        after = (refs(sb), sh(sb, "rev-parse", "HEAD"))
        # refs and HEAD unchanged; execute creates no marker (F20 plants one in its setup, which must survive as is)
        R[name] = {"pass": out == ("REFUSED", code) and before == after
                   and (G.TEST_MARKER in before[0] or G.TEST_MARKER not in after[0]),
                   "got": str(out)}

    refused("F01_no_grant_commit", "GRANT_MISSING", setup=lambda sb, c: (
        sh(sb, "update-ref", SB_BRANCH, c["Rv"]), sh(sb, "reset", "-q", "--hard", c["Rv"])))
    refused("F02_grant_not_at_head", "GRANT_INVALID", child_after_grant=True)
    refused("F03_grant_touches_another_file", "GRANT_INVALID", grant_extra_files={f"{NS}/tests/x.txt": b"x"})
    sb = new_sandbox("F04_grant_is_a_merge")
    base = sh(sb, "rev-parse", "HEAD").strip()
    side = commit(sb, base, {f"{NS}/tests/side.txt": b"s"}, "side")
    build_chain(sb, grant_parents=[side])
    R["F04_grant_is_a_merge"] = {"pass": execute(sb) == ("REFUSED", "GRANT_INVALID")}
    refused("F05_wrong_driver_sha", "GRANT_INVALID", grant_over={"driver_sha256": "0" * 64})
    refused("F06_wrong_manifest_sha", "GRANT_INVALID", grant_over={"frozen_manifest_sha256": "1" * 64})
    refused("F07_frozen_commit_not_in_chain", "GRANT_INVALID", grant_over={"frozen_commit": "2" * 40})
    refused("F08_missing_review", "GRANT_INVALID", drop_review=True)
    refused("F09_extra_commit_in_chain", "GRANT_INVALID", extra_after_freeze={f"{NS}/qualification/extra.txt": b"e"})
    refused("F10_review_rejected", "REVIEW_VERDICT", review_text="# review\nQUALIFICATION_REJECTED\n")
    refused("F11_review_verdict_not_on_line_2", "REVIEW_VERDICT", review_text="# review\n\nQUALIFICATION_ACCEPTED\n")
    refused("F12_qualification_not_pass", "GRANT_INVALID", qual={"pass": False})
    refused("F13_qualification_other_freeze", "GRANT_INVALID", qual={"pass": True, "freeze_commit": "3" * 40})
    refused("F14_qualification_touches_code", "GRANT_INVALID", qual_extra={f"{NS}/code/x.py": b"# x\n"})
    refused("F15_review_touches_another_file", "GRANT_INVALID", review_extra={f"{NS}/tests/y.txt": b"y"})
    refused("F16_frozen_dir_changed_after_freeze", "GRANT_INVALID",
            extra_after_freeze={f"{NS}/code/late.py": b"# late\n"})
    refused("F17_dirty_tree", "DIRTY_TREE", setup=lambda sb, c: (sb / NS / "untracked.txt").write_text("u"))
    refused("F18_result_file_present", "TARGET_ARTIFACT_EXISTS", setup=lambda sb, c: (
        (sb / D.EXEC_DIR_REL).mkdir(parents=True), (sb / D.RESULT_REL).write_text("{}")))
    refused("F19_result_dir_is_symlink", "RESULT_PATH_OCCUPIED", setup=lambda sb, c: (
        (sb / NS / "evidence").mkdir(exist_ok=True), os.symlink("/tmp", sb / D.EXEC_DIR_REL)))
    refused("F20_marker_already_exists", "CONSUMED", setup=lambda sb, c: sh(sb, "update-ref", G.TEST_MARKER, c["G"]))
    refused("F21_pending_ref_exists", "CONSUMED", setup=lambda sb, c: sh(sb, "update-ref", G.TEST_PENDING_REF, c["G"]))
    refused("F22_emergency_file_exists", "TARGET_ARTIFACT_EXISTS", setup=lambda sb, c: (
        Path(sh(sb, "rev-parse", "--path-format=absolute", "--git-dir").strip()) / D.EMERGENCY_NAME).write_text("{}"))
    refused("F23_prior_marker_namespace", "CONSUMED", setup=lambda sb, c: sh(sb, "update-ref", "refs/rlr-tail/x", c["G"]))
    refused("F24_unparseable_grant", "GRANT_INVALID", grant_raw=b"{not json")
    # F25 CONTROL_FAILED: sealed, exit 3, no marker
    sb = new_sandbox("F25_control_failed")
    build_chain(sb)
    rc = execute(sb, control=BAD_CONTROL)
    R["F25_control_failed_sealed_not_consumed"] = {"pass": rc == 3 and G.TEST_MARKER not in refs(sb)
                                                   and status_of(sb) == "CONTROL_FAILED", "got": rc}
    # F26 valid chain with interleaved checkpoint-record commits
    sb = new_sandbox("F26_record_commits_allowed")
    build_chain(sb, record_commits=True)
    rc = execute(sb)
    R["F26_record_commits_allowed"] = {"pass": rc == 0 and status_of(sb) == "TARGET_EVALUATED", "got": rc}
    return R


def post_marker_flows() -> dict:
    import p309_postexec as PX
    R = {}

    def run(name, evaluator=ev_ok, want_rc=0, want_status="TARGET_EVALUATED", **kw):
        sb = new_sandbox(name)
        c = build_chain(sb)
        rc = execute(sb, evaluator=evaluator, **kw)
        return sb, c, rc

    sb, c, rc = run("F27_success")
    px = PX.checks(ctx_of(sb), second_execute=lambda: 2 if execute(sb) == ("REFUSED", "CONSUMED") else 99)
    R["F27_success_and_postexec"] = {"pass": rc == 0 and px["ok"], "got": {"rc": rc, "postexec": px}}
    for name, ev, st in (("F28_evaluator_raises", ev_raise, "TARGET_EVALUATION_FAILED"),
                         ("F29_independent_check_fails", ev_indep, "INDEPENDENT_CHECK_FAILED"),
                         ("F30_base_exception", ev_bexc, "TARGET_EVALUATION_FAILED")):
        sb, c, rc = run(name, evaluator=ev)
        rec = json.loads((sb / D.RESULT_REL).read_text())
        R[name] = {"pass": rc == 5 and rec["status"] == st and rec["mechanical_outcome"] == "EXECUTION_INDETERMINATE"
                   and G.TEST_MARKER in refs(sb), "got": rc}

    def bad_persist(ctx, data):
        raise OSError("stub: pending ref not writable")
    sb, c, rc = run("F31_persist_fails_emergency_ok", persist=bad_persist)
    rc2 = D.run_seal_only(ctx_of(sb))
    R["F31_persist_fails_emergency_then_seal_only"] = {"pass": rc == 4 and rc2 == 0 and status_of(sb) ==
                                                       "TARGET_EVALUATED", "got": [rc, rc2]}
    orig = D.persist_emergency
    D.persist_emergency = lambda ctx, data: (_ for _ in ()).throw(OSError("stub: git dir not writable"))
    try:
        sb, c, rc = run("F32_no_evidence_channel", persist=bad_persist)
    finally:
        D.persist_emergency = orig
    again = execute(sb)
    R["F32_consumed_unrecorded_never_again"] = {"pass": rc == 6 and G.TEST_MARKER in refs(sb)
                                                and again == ("REFUSED", "CONSUMED"), "got": [rc, str(again)]}

    def bad_seal(ctx, blob, msg):
        raise OSError("stub: seal failed")
    sb, c, rc = run("F33_seal_fails", sealer=bad_seal)
    rc2 = D.run_seal_only(ctx_of(sb))
    R["F33_seal_fails_then_seal_only"] = {"pass": rc == 4 and rc2 == 0 and status_of(sb) == "TARGET_EVALUATED",
                                          "got": [rc, rc2]}

    def bad_mat(ctx, blob):
        raise OSError("stub: materialize failed")
    sb, c, rc = run("F34_materialize_fails", materializer=bad_mat)
    rc2 = D.run_seal_only(ctx_of(sb))
    R["F34_materialize_fails_then_seal_only"] = {"pass": rc == 7 and rc2 == 0 and status_of(sb) == "TARGET_EVALUATED",
                                                 "got": [rc, rc2]}
    sb = new_sandbox("F35_seal_only_nothing")
    build_chain(sb)
    try:
        D.run_seal_only(ctx_of(sb))
        R["F35_seal_only_without_evidence_refused"] = {"pass": False}
    except D.Refusal as exc:
        R["F35_seal_only_without_evidence_refused"] = {"pass": exc.code == "SEAL_ONLY", "got": exc.code}
    sb = new_sandbox("F36_seal_only_pending_without_marker")
    c = build_chain(sb)
    blob = sh(sb, "hash-object", "-w", "--stdin", input_=b'{"status": "TARGET_EVALUATED"}\n').strip()
    sh(sb, "update-ref", G.TEST_PENDING_REF, blob)
    try:
        D.run_seal_only(ctx_of(sb))
        R["F36_seal_only_post_marker_evidence_without_marker"] = {"pass": False}
    except D.Refusal as exc:
        R["F36_seal_only_post_marker_evidence_without_marker"] = {"pass": exc.code == "SEAL_ONLY"}
    sb, c, rc = run("F37_seal_only_other_result_at_head")
    other = commit(sb, sh(sb, "rev-parse", "HEAD").strip(), {D.RESULT_REL: b'{"status": "OTHER"}\n'}, "other result")
    sh(sb, "update-ref", SB_BRANCH, other)
    sh(sb, "reset", "-q", "--hard", other)
    try:
        D.run_seal_only(ctx_of(sb))
        R["F37_seal_only_head_holds_other_result"] = {"pass": False}
    except D.Refusal as exc:
        R["F37_seal_only_head_holds_other_result"] = {"pass": exc.code == "SEAL_ONLY"}
    sb, c, rc = run("F38_second_execute")
    R["F38_second_execute_refused"] = {"pass": rc == 0 and execute(sb) == ("REFUSED", "CONSUMED")}
    sb, c, rc = run("F39_recording_failure", evaluator=ev_unserializable)
    rec = json.loads((sb / D.RESULT_REL).read_text()) if (sb / D.RESULT_REL).exists() else {}
    R["F39_recording_failure_sealed"] = {"pass": rc == 5 and rec.get("status") == "POST_MARKER_RECORDING_FAILED",
                                         "got": rc}
    return R


# ---------------------------------------------------------------------- Stage-1 failure mapping and budget mechanics
def _stub_runner(payload_for):
    """a real child process that writes the given JSON (or burns CPU) and exits: os.wait4 accounting is genuine."""
    def runner(spec):
        pl = payload_for(spec)
        if pl == "BURN":
            code = "import resource,sys\nx=0\nwhile True: x+=1\n"
            lim = int(spec["_limit"])

            def lim_fn():
                import resource as r
                r.setrlimit(r.RLIMIT_CPU, (lim, lim + 5))
            return subprocess.Popen([sys.executable, "-c", code], preexec_fn=lim_fn)
        # the payload goes through a side file (certificate payloads exceed the argv limit); the child moves it into
        # place, so the output still appears only when the child runs
        src = spec["_out"] + ".stub"
        Path(src).write_text(json.dumps(pl))
        code = f"import os; os.replace({src!r}, {spec['_out']!r})"
        return subprocess.Popen([sys.executable, "-c", code])
    return runner


def gate_str(st) -> dict:
    return {str(i): (str(v) if v is not None else None) for i, v in dict(st["gate_result"].gamma).items()}


def stage_flows() -> dict:
    import srk_gate as GT
    R = {}
    cell = (F(1, 2), F(37, 72))                               # the declared decoy cell (a stub run; nothing computed)
    vid = "sha256:" + D.pin_table(D.load_manifest())[D.VARIANT_REL][0]
    base = {"kind": "JOB_RETURNED", "W_status": "W_NEGATIVE", "V_status": {}, "certificates": [], "verdicts": {},
            "verdict_source": vid, "adapter_records": [], "log_digest": ""}
    st = D.stage1a("decoy", cell, dict(D.GEOMETRY), vid, workers=2, runner=_stub_runner(lambda s: base))
    R["S01_non_certified_falls_back"] = {"pass": all(v is None for v in dict(st["gate_result"].gamma).values())}
    # real committed decoy certificates of this cell, returned by a stub job with a chosen verdict
    certs = []
    for j in range(4):
        d = json.loads((D.E.RNS / f"evidence/srk_decoys_cell/cell_h5_k1_2_C1_2_37_72_S{j}.json").read_text())
        certs += [c for c in d["certificates"].values() if c.get("status") == "CERTIFIED"]

    def with_verdict(v):
        def pl(spec):
            cs = [c for c in certs if c["block"] == spec["block"] and c["degree"] == spec["degree"]]
            return dict(base, W_status="CERTIFIED", certificates=cs, verdicts={c["sha256"]: v for c in cs})
        return pl
    st = D.stage1a("decoy", cell, dict(D.GEOMETRY), vid, workers=2, runner=_stub_runner(with_verdict("REJECT")))
    st_ok = D.stage1a("decoy", cell, dict(D.GEOMETRY), vid, workers=2, runner=_stub_runner(with_verdict("ACCEPT")))
    R["S02_non_accept_verdicts_fall_back"] = {
        "pass": all(v is None for v in dict(st["gate_result"].gamma).values())
        and any(v is not None for v in dict(st_ok["gate_result"].gamma).values()),
        "got": {"REJECT": gate_str(st), "ACCEPT": gate_str(st_ok)}}
    st = D.stage1a("decoy", cell, dict(D.GEOMETRY), vid, workers=2, runner=_stub_runner(lambda s: base), budget_s=0)
    R["S03_budget_zero_no_job_starts_no_raise"] = {"pass": len(st["run"]["not_started"]) == 12 and all(
        v is None for v in dict(st["gate_result"].gamma).values())}
    try:
        D.stage1a("decoy", cell, dict(D.GEOMETRY), vid, workers=2,
                  runner=_stub_runner(lambda s: {"kind": "JOB_EXCEPTION", "error": "stub"}))
        R["S04_job_exception_raises"] = {"pass": False}
    except RuntimeError:
        R["S04_job_exception_raises"] = {"pass": True}
    order = [(j, d) for j, d in D.stage1a_jobs()]
    R["S05_rung_major_order"] = {"pass": order == [(j, d) for d in (8, 10, 12) for j in range(4)]}
    run = D.run_jobs([{"x": 1}], budget_s=100, job_limit_s=1, workers=1, runner=_stub_runner(lambda s: "BURN"))
    R["S06_job_limit_terminates_and_discards"] = {"pass": run["results"][0]["kind"] == "TERMINATED_JOB_LIMIT",
                                                  "got": run["results"][0]}
    run = D.run_jobs([{"x": 1}] * 3, budget_s=0.5, job_limit_s=2, workers=1, runner=_stub_runner(lambda s: "BURN"))
    R["S07_start_threshold_stops_starting_without_raising"] = {
        "pass": len(run["results"]) == 1 and run["not_started"] == [1, 2], "got": run["not_started"]}
    wrong = dict(base, verdict_source="sha256:" + "9" * 64)
    try:
        D.stage1a("decoy", cell, dict(D.GEOMETRY), vid, workers=2, runner=_stub_runner(lambda s: wrong))
        R["S08_verdicts_from_another_verifier_raise"] = {"pass": False}
    except RuntimeError:
        R["S08_verdicts_from_another_verifier_raise"] = {"pass": True}
    A = {"A0": F(3), "A1": F(5), "A2": F(7)}
    R["S09_stage1b_failure_gives_S_I1"] = {"pass": D.compose_S(A, {"cell": {"status": "CERTIFICATION_FAILED"}}) == A
                                           and D.compose_S(A, None) == A}
    m = D.load_manifest()
    nc = {"kind": "JOB_RETURNED", "status": "NOT_CERTIFIED", "record": {"status": "NOT_CERTIFIED"}}
    st1b = D.stage1b("decoy", (F(1, 2), F(51, 100)), m, workers=2, runner=_stub_runner(lambda s: nc))
    R["S10_stage1b_not_certified_is_certification_failed"] = {"pass": st1b["cell"]["status"] == "CERTIFICATION_FAILED"}
    try:
        D.stage1b("decoy", (F(1, 2), F(51, 100)), m, workers=2,
                  runner=_stub_runner(lambda s: {"kind": "JOB_EXCEPTION", "error": "stub"}))
        R["S11_stage1b_job_exception_raises"] = {"pass": False}
    except RuntimeError:
        R["S11_stage1b_job_exception_raises"] = {"pass": True}
    IND = D._ind()
    rec = {"status": "CERTIFIED", "degree": 4, "A_bar": "3", "tau": "2", "D_lo": "1/2", "C_T": "5", "D1": "1/3",
           "D2": "1/5", "L1_up": "1/7", "L2_up": "1/9", "tau_a_lo": "1/2", "C_R": "4",
           "tau_a_up": "1", "S2_up": "1/3", "TN_up": "1/4", "Lambda_lo": "1/6"}    # every ladder key present
    sup = IND.block_supply(rec, F(1), F(1))
    bad = dict(rec, **{k: D.fs(v) for k, v in sup.items() if k in ("A0_SUPPLY", "G0", "G1", "G2")},
               A1_SUPPLY=D.fs(sup["A1_SUPPLY"] + 1), A2_SUPPLY=D.fs(sup["A2_SUPPLY"]))
    mism = {"kind": "JOB_RETURNED", "status": "CERTIFIED", "record": bad}
    try:
        D.stage1b("decoy", (F(1, 2), F(51, 100)), m, workers=2, runner=_stub_runner(lambda s: mism))
        R["S12_stage1b_reconstruction_mismatch_raises"] = {"pass": False}
    except D.IndependentCheckFailed:
        R["S12_stage1b_reconstruction_mismatch_raises"] = {"pass": True}
    except Exception as exc:  # noqa: BLE001
        R["S12_stage1b_reconstruction_mismatch_raises"] = {"pass": False, "got": f"{type(exc).__name__}: {exc}"[:200]}
    # S13: the execute order (historical control and Stage-1a gate import the SRK side, which imports c1b_gauss by a
    # plain import; then Stage 1b loads the pinned certifier): Stage 1b loads, and the module table is unchanged
    names = ("c1b_gauss", "c1b_kernel", "c1b_float", "c1b_pw", "c1b_prov", "c1b_certpw", "ov_quarantine")
    before = {n: sys.modules.get(n) for n in names}
    pre = before["c1b_gauss"] is not None and getattr(before["c1b_gauss"], "_rlr307_pinned", None) is None
    try:
        st1b = D.stage1b("decoy", (F(1, 2), F(51, 100)), m, workers=2, runner=_stub_runner(lambda s: nc))
        after = {n: sys.modules.get(n) for n in names}
        R["S13_stage1b_after_srk_imports_table_unchanged"] = {
            "pass": pre and st1b["cell"]["status"] == "CERTIFICATION_FAILED" and all(after[n] is before[n] for n in names),
            "got": {"srk_side_c1b_gauss_preloaded": pre, "changed": [n for n in names if after[n] is not before[n]]}}
    except Exception as exc:  # noqa: BLE001
        R["S13_stage1b_after_srk_imports_table_unchanged"] = {"pass": False, "got": f"{type(exc).__name__}: {exc}"[:200]}
    # S14 (delta review D2): the frozen budget mechanics as the runner sees them: Stage 1b per-job limit and start
    # threshold 21 600 s, RLR307 order (degree descending, then block); Stage 1a 12 CPU-h per job, 48 CPU-h threshold
    seen = {"1a": [], "1b": []}

    def capture(stage, payload):
        inner = _stub_runner(lambda s: payload)

        def runner(spec):
            seen[stage].append(spec)
            return inner(spec)
        return runner
    st1b = D.stage1b("decoy", (F(1, 2), F(51, 100)), m, workers=2, runner=capture("1b", nc))
    st1a = D.stage1a("decoy", cell, dict(D.GEOMETRY), vid, workers=2, runner=capture("1a", base))
    keys = [(s["degree"], s["block"]) for s in seen["1b"]]
    R["S14_frozen_budget_mechanics"] = {
        "pass": bool(keys) and keys == sorted(keys, key=lambda t: (-t[0], t[1]))
        and len({t[0] for t in keys}) > 1
        and all(s["_limit"] == 21600 for s in seen["1b"]) and st1b["run"]["budget_s"] == 21600
        and st1b["run"]["job_limit_s"] == 21600 and D.STAGE1B_JOB_LIMIT_S == D.STAGE1B_BUDGET_S == 21600
        and all(s["_limit"] == 12 * 3600 for s in seen["1a"]) and st1a["run"]["budget_s"] == 48 * 3600
        and st1a["run"]["job_limit_s"] == 12 * 3600 and D.WORKERS == 4,
        "got": {"stage1b_jobs": len(keys), "stage1b_order": keys[:8], "stage1a_jobs": len(seen["1a"])}}
    _ = GT
    return R


if __name__ == "__main__":
    D.E.log("tests/test_p309_exactly_once.py", "QC11 exactly-once sandbox flows (stubs; synthetic TEST names only)",
            klass="SYNTHETIC", notes="sandboxes are light repositories under the scratchpad (alternates, no remote), never pushed; "
                                     "no production ref is created; nothing is evaluated for any cell")
    res = {}
    res.update(pre_marker_flows())
    res.update(post_marker_flows())
    res.update(stage_flows())
    bad = [k for k, v in res.items() if not v.get("pass")]
    leaked = []
    for p in sorted(SCRATCH.iterdir()):
        try:
            leaked += [r for r in sh(p, "for-each-ref", "--format=%(refname)").split() if r.startswith(G._PROD_NAMESPACE)]
        except RuntimeError:
            pass
    leaked += [r for r in sh(REPO, "for-each-ref", "--format=%(refname)").split() if r.startswith(G._PROD_NAMESPACE)]
    res["Z_no_production_ref_anywhere"] = {"pass": not leaked, "got": leaked}
    ok = all(v.get("pass") for v in res.values())
    out = {"utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "flows": len(res),
           "all_pass": ok, "driver_sha256": OWN_SHA, "test_sha256": D.sha(Path(__file__).read_bytes()), "results": res}
    (D.E.evidence_dir("fc6") / "EXACTLY_ONCE_FLOWS.json").write_text(json.dumps(out, indent=1, sort_keys=True,
                                                                                 default=str) + "\n")
    for k, v in res.items():
        print(f"[{'PASS' if v.get('pass') else 'FAIL'}] {k}  {'' if v.get('pass') else v.get('got', '')}")
    sys.exit(0 if ok else 1)
