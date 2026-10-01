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
import platform
import shutil
import subprocess
import sys
import tempfile
import types
from fractions import Fraction as F
from pathlib import Path

FNS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FNS / "code"))
import p309_env as E  # noqa: E402  (r2 P7: scratch_dir)
import p309_driver as D  # noqa: E402

G = D.G
REPO = D.REPO
SCRATCH = E.scratch_dir("qc11_sandboxes")   # r2 P7: under P309_SCRATCH_ROOT (validated; no fallback)
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
    sh(sb, "sparse-checkout", "set", "--no-cone", f"/{NS}/", "/TEST_ONLY/")
    sh(sb, "reset", "-q", "--hard", head)
    return sb


def utc_in(seconds: float) -> str:
    t = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=seconds)
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def test_grant(sb: Path, man: bytes, F_: str, Q: str, Rv: str | None) -> dict:
    """a complete TEST-context grant (spec 2.2 / 3 fields; driver B3 fields), valid for this host and sandbox."""
    pins = D.pin_table(json.loads(man))
    return {"schema": "P309_TEST_GRANT/1", "campaign": G._TEST_CELL, "cell": G._TEST_CELL,
            "geometry": dict(D.GRANT_GEOMETRY["SANDBOX"]), "cell_interval": list(D.TEST_CELL_INTERVAL),
            "drift_hull_Ew": ["341/1024", "201/512"], "closure_only": True, "executions_authorized": 1,
            "driver_sha256": OWN_SHA, "frozen_manifest_sha256": hashlib.sha256(man).hexdigest(), "frozen_commit": F_,
            "qualification_commit": Q, "qualification_review_commit": Rv,
            "verifier_id": "sha256:" + pins[D.VARIANT_REL][0], "guard_id": "sha256:" + pins[D.GUARD_REL][0],
            "execution_host": {"host_id_sha256": G.host_id(), "worktree": str(sb)},
            "runtime": {"python": platform.python_version()}, "marker_ref": G.TEST_MARKER,
            "not_after_utc": utc_in(30 * 86400), "issued_utc": utc_in(-60),
            "authority": "TEST_ONLY sandbox authority (QC11); not an owner grant"}


def build_chain(sb: Path, *, grant_over=None, grant_raw=None, drop_review=False, extra_after_freeze=None,
                qual=None, review_text=None, grant_extra_files=None, record_commits=False, grant_parents=None,
                qual_extra=None, review_extra=None, child_after_grant=False, window=None, pre_review_window=None,
                freeze_record="ok") -> dict:
    """F (manifest; TEST_ONLY manifest = the same bytes) <- FR (freeze record) <- [extra] <- Q <- Rv <- [window] <- G"""
    base = sh(sb, "rev-parse", "HEAD").strip()
    man = (REPO / D.MANIFEST_REL).read_bytes()
    # the sandbox freeze commit must change a frozen path even when the manifest bytes equal the base's (the driver
    # locates the freeze as the last commit touching the frozen directories); the nonce file exists only in sandboxes
    F_ = commit(sb, base, {D.MANIFEST_REL: man, G._TEST_MANIFEST_PATH: man,
                           f"{NS}/freeze/SANDBOX_FREEZE_NONCE.txt": sb.name.encode() + b"\n"}, "sandbox freeze (manifest)")
    c = {"F": F_}
    tip = F_
    if freeze_record in ("ok", "late_change"):
        tip = commit(sb, tip, {D.FREEZE_RECORD_REL: json.dumps({"freeze_commit": F_}).encode()}, "freeze record")
    elif freeze_record == "wrong":
        tip = commit(sb, tip, {D.FREEZE_RECORD_REL: json.dumps({"freeze_commit": base}).encode()}, "freeze record")
    if freeze_record == "late_change":
        tip = commit(sb, tip, {D.FREEZE_RECORD_REL: json.dumps({"freeze_commit": F_, "x": 1}).encode()}, "record edit")
    if extra_after_freeze:
        tip = commit(sb, tip, extra_after_freeze, "a change after the freeze")
    if record_commits:
        tip = commit(sb, tip, {D.CHECKPOINT_LEDGER_REL: b'{"r":1}\n'}, "checkpoint record")
    q = qual if qual is not None else {"pass": True, "freeze_commit": F_}
    Q = commit(sb, tip, {D.QUAL_REL: json.dumps(q).encode(), **(qual_extra or {})}, "qualification")
    c["Q"] = tip = Q
    if record_commits:
        tip = commit(sb, tip, {D.CHECKPOINT_LEDGER_REL: b'{"r":2}\n'}, "checkpoint record")
    for k, files in enumerate(pre_review_window or []):
        tip = commit(sb, tip, files, f"window-type commit before the review {k}")
    if not drop_review:
        rv = review_text if review_text is not None else "# review\nQUALIFICATION_ACCEPTED\n"
        Rv = commit(sb, tip, {D.QREVIEW_REL: rv.encode(), **(review_extra or {})}, "qualification review")
        c["Rv"] = tip = Rv
    if record_commits:
        tip = commit(sb, tip, {D.CHECKPOINT_LEDGER_REL: b'{"r":3}\n'}, "checkpoint record")
    for k, files in enumerate(window or []):
        tip = commit(sb, tip, files, f"window commit {k}")
    g = test_grant(sb, man, F_, Q, c.get("Rv"))
    g.update(grant_over or {})
    for k in [k for k, v in g.items() if v is DROP]:
        del g[k]
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


DROP = object()


def ctx_of(sb: Path) -> D.ExecContext:
    return D.sandbox_context(sb)


OK_CONTROL = lambda: {"reproduces_C2_exactly": True, "digest": "sandbox"}  # noqa: E731
BAD_CONTROL = lambda: {"reproduces_C2_exactly": False, "digest": "sandbox"}  # noqa: E731
PREP = lambda: {}  # noqa: E731


def RAISING_CONTROL():
    raise ValueError("stub: the control raised")


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
        return D.run_execute(OWN_SHA, ctx=ctx, prepare=kw.pop("prepare", PREP), evaluator=evaluator, control=control,
                             **kw)
    except D.Refusal as exc:
        return ("REFUSED", exc.code)


def refs(sb) -> dict:
    return dict(line.split()[::-1] for line in sh(sb, "for-each-ref", "--format=%(objectname) %(refname)").splitlines())


def result_path(sb) -> Path:
    return sb / D.SANDBOX_RESULT_REL


def status_of(sb) -> str | None:
    p = result_path(sb)
    return json.loads(p.read_text()).get("status") if p.exists() else None


def git_dir_of(sb) -> Path:
    return Path(sh(sb, "rev-parse", "--path-format=absolute", "--git-dir").strip())


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
        nonce_ok = name == "F22b_run_nonce_exists" or not (git_dir_of(sb) / D.RUN_NONCE_NAME).exists()
        R[name] = {"pass": (out == ("REFUSED", code) and before == after and nonce_ok
                            and (G.TEST_MARKER in before[0] or G.TEST_MARKER not in after[0])),
                   "got": str(out)}
        return sb

    refused("F01_no_grant_commit", "GRANT_MISSING", setup=lambda sb, c: (
        sh(sb, "update-ref", SB_BRANCH, c["Rv"]), sh(sb, "reset", "-q", "--hard", c["Rv"])))
    refused("F02_grant_not_at_head", "GRANT_INVALID", child_after_grant=True)
    refused("F03_grant_touches_another_file", "GRANT_INVALID", grant_extra_files={f"{NS}/evidence/x.txt": b"x"})
    sb = new_sandbox("F04_grant_is_a_merge")
    base = sh(sb, "rev-parse", "HEAD").strip()
    side = commit(sb, base, {f"{NS}/evidence/side.txt": b"s"}, "side")
    build_chain(sb, grant_parents=[side])
    R["F04_grant_is_a_merge"] = {"pass": execute(sb) == ("REFUSED", "GRANT_INVALID")}
    refused("F05_wrong_driver_sha", "GRANT_INVALID", grant_over={"driver_sha256": "0" * 64})
    refused("F06_wrong_manifest_sha", "GRANT_INVALID", grant_over={"frozen_manifest_sha256": "1" * 64})
    refused("F07_frozen_commit_not_recorded", "GRANT_INVALID", grant_over={"frozen_commit": "2" * 40})
    refused("F08_missing_review", "GRANT_INVALID", drop_review=True)
    refused("F09_extra_commit_in_chain", "GRANT_INVALID", extra_after_freeze={f"{NS}/qualification/extra.txt": b"e"})
    refused("F10_review_rejected", "REVIEW_VERDICT", review_text="# review\nQUALIFICATION_REJECTED\n")
    refused("F11_review_verdict_not_on_line_2", "REVIEW_VERDICT", review_text="# review\n\nQUALIFICATION_ACCEPTED\n")
    refused("F12_qualification_not_pass", "GRANT_INVALID", qual={"pass": False})
    refused("F13_qualification_other_freeze", "GRANT_INVALID", qual={"pass": True, "freeze_commit": "3" * 40})
    refused("F14_qualification_touches_code", "FREEZE_RECORD", qual_extra={f"{NS}/code/x.py": b"# x\n"})
    refused("F15_review_touches_another_file", "GRANT_INVALID", review_extra={f"{NS}/evidence/y.txt": b"y"})
    refused("F16_frozen_dir_changed_after_freeze", "FREEZE_RECORD",
            extra_after_freeze={f"{NS}/code/late.py": b"# late\n"})
    refused("F17_dirty_tree", "DIRTY_TREE", setup=lambda sb, c: (sb / NS / "untracked.txt").write_text("u"))
    refused("F18_result_file_present", "TARGET_ARTIFACT_EXISTS", setup=lambda sb, c: result_path(sb).write_text("{}"))
    refused("F19_result_tmp_is_symlink", "RESULT_PATH_OCCUPIED", setup=lambda sb, c: os.symlink(
        "/tmp", str(result_path(sb)) + ".tmp"))
    refused("F20_marker_already_exists", "CONSUMED", setup=lambda sb, c: sh(sb, "update-ref", G.TEST_MARKER, c["G"]))
    refused("F21_pending_ref_exists", "CONSUMED", setup=lambda sb, c: sh(sb, "update-ref", G.TEST_PENDING_REF, c["G"]))
    refused("F22_emergency_file_exists", "TARGET_ARTIFACT_EXISTS", setup=lambda sb, c: (
        git_dir_of(sb) / D.EMERGENCY_NAME).write_text("{}"))
    refused("F22b_run_nonce_exists", "TARGET_ARTIFACT_EXISTS", setup=lambda sb, c: (
        git_dir_of(sb) / D.RUN_NONCE_NAME).write_text("{}"))
    refused("F23_prior_marker_namespace", "CONSUMED", setup=lambda sb, c: sh(sb, "update-ref", "refs/rlr-tail/x", c["G"]))
    refused("F24_unparseable_grant", "GRANT_INVALID", grant_raw=b"{not json")
    refused("F24b_executions_authorized_true", "GRANT_INVALID", grant_over={"executions_authorized": True})
    # F25 CONTROL_FAILED: sealed, exit 3, no marker; F25b: an exception in the control is a control failure (NB5)
    for name, ctl in (("F25_control_failed", BAD_CONTROL), ("F25b_control_raises", RAISING_CONTROL)):
        sb = new_sandbox(name)
        build_chain(sb)
        rc = execute(sb, control=ctl)
        rec = json.loads(result_path(sb).read_text()) if result_path(sb).exists() else {}
        R[name + "_sealed_not_consumed"] = {"pass": rc == 3 and G.TEST_MARKER not in refs(sb)
                                            and rec.get("status") == "CONTROL_FAILED"
                                            and (name == "F25_control_failed" or "error" in rec.get("historical_control", {})),
                                            "got": rc}
    # F26 valid chain with interleaved checkpoint-record commits
    sb = new_sandbox("F26_record_commits_allowed")
    build_chain(sb, record_commits=True)
    rc = execute(sb)
    R["F26_record_commits_allowed"] = {"pass": rc == 0 and status_of(sb) == "TARGET_EVALUATED", "got": rc}
    return R


def admission_flows() -> dict:
    """R4 B1, B3, B5, B7(b)/(c), NB4: every grant precondition is refused BEFORE the marker (exit 2, no ref)."""
    R = {}

    def refused(name, code, **kw):
        sb = new_sandbox(name)
        setup = kw.pop("setup", None)
        c = build_chain(sb, **kw)
        if setup:
            setup(sb, c)
        before = refs(sb)
        out = execute(sb)
        R[name] = {"pass": out == ("REFUSED", code) and refs(sb) == before and G.TEST_MARKER not in refs(sb),
                   "got": str(out)}

    w = F(20, 51) - F(1, 3)                                   # B1: a same-width neighbour of the declared cell
    lo, hi = F(1, 3) + w, F(20, 51) + w
    ew = G.outward_hull(lo, hi)
    refused("A01_shifted_cell_same_width", "ADMISSION", grant_over={
        "cell_interval": [D.fs(lo), D.fs(hi)], "drift_hull_Ew": [D.fs(ew[0]), D.fs(ew[1])]})
    refused("A02_geometry_not_exact_strings", "ADMISSION", grant_over={"geometry": {"h": "3/1", "k": "1/2"}})
    refused("A03_wrong_verifier_id", "ADMISSION", grant_over={"verifier_id": "sha256:" + "4" * 64})
    refused("A04_wrong_guard_id", "ADMISSION", grant_over={"guard_id": "sha256:" + "5" * 64})
    refused("A05_wrong_marker_ref", "ADMISSION", grant_over={"marker_ref": "refs/p309-test/OTHER"})
    refused("A06_wrong_host", "ADMISSION", grant_over={"execution_host": {"host_id_sha256": "6" * 64,
                                                                          "worktree": "/nonexistent"}})
    refused("A07_wrong_worktree", "ADMISSION", grant_over={"execution_host": {"host_id_sha256": G.host_id(),
                                                                              "worktree": "/nonexistent"}})
    refused("A08_wrong_runtime", "ADMISSION", grant_over={"runtime": {"python": "2.7.18"}})
    refused("A09_short_horizon", "ADMISSION", grant_over={"not_after_utc": utc_in(86400)})
    refused("A10_expired", "ADMISSION", grant_over={"not_after_utc": utc_in(-60)})
    refused("A11_placeholder_expiry", "ADMISSION",
            grant_over={"not_after_utc": "<SET BY THE OWNER, ISO-8601 UTC, e.g. 2026-10-31T23:59:59Z>"})
    refused("A12_placeholder_issued", "ADMISSION", grant_over={"issued_utc": "<SET BY THE OWNER>"})
    refused("A13_placeholder_authority", "ADMISSION",
            grant_over={"authority": "<THE OWNER'S GRANT INSTRUCTION, verbatim reference>"})
    refused("A14_missing_authority", "ADMISSION", grant_over={"authority": DROP})
    # R4F F2: only the proposal's own placeholders are refused; an authority quoting the owner's text is admitted
    sb = new_sandbox("A27_authority_quoting_owner_text_admitted")
    build_chain(sb, grant_over={"authority": 'owner message 2026-10-01: "EXECUTION GRANT -> run once <P309>"'})
    R["A27_authority_quoting_owner_text_admitted"] = {"pass": execute(sb) == 0}
    # R4F NF1: the worktree field is required
    refused("A28_missing_worktree", "ADMISSION", grant_over={"execution_host": {"host_id_sha256": G.host_id()}})
    refused("A15_issued_in_the_future", "ADMISSION", grant_over={"issued_utc": utc_in(3600)})
    refused("A16_detached_head", "BRANCH", setup=lambda sb, c: sh(sb, "checkout", "-q", "--detach", c["G"]))
    refused("A17_strict_descendant_ref", "ADMISSION", setup=lambda sb, c: sh(
        sb, "update-ref", "refs/heads/side", commit(sb, c["G"], {f"{NS}/evidence/s.txt": b"s"}, "child of G")))
    # E1-1 positive (B7(d)): a non-current ref exactly AT the grant commit does not block
    sb = new_sandbox("A18_ref_at_grant_commit_allowed")
    c = build_chain(sb)
    sh(sb, "update-ref", "refs/remotes/origin/p309-test-sandbox", c["G"])
    rc = execute(sb)
    R["A18_ref_at_grant_commit_allowed"] = {"pass": rc == 0 and status_of(sb) == "TARGET_EVALUATED", "got": rc}
    # B5 grant window
    sb = new_sandbox("A19_window_commits_allowed")
    build_chain(sb, window=[{f"{NS}/ledger/ZERO_TARGET_LEDGER.jsonl": b'{"w":1}\n'},
                            {f"{NS}/handoff/PROPOSED_EXECUTION_AUTHORIZATION_P309.json": b"{}\n",
                             f"{NS}/ledger/EXPOSURE_LEDGER.jsonl": b'{"w":2}\n'},
                            {f"{NS}/qualification/host_rerun/QC10_HOST.json": b"{}\n"}])
    rc = execute(sb)
    R["A19_window_commits_allowed"] = {"pass": rc == 0 and status_of(sb) == "TARGET_EVALUATED", "got": rc}
    refused("A20_window_commit_outside_window_paths", "GRANT_INVALID", window=[{f"{NS}/evidence/w.txt": b"w"}])
    refused("A21_window_type_commit_before_review", "GRANT_INVALID",
            pre_review_window=[{f"{NS}/ledger/ZERO_TARGET_LEDGER.jsonl": b'{"w":1}\n'}])
    refused("A22_window_commit_touching_review_files", "GRANT_INVALID",
            window=[{D.QREVIEW_PREFIX + "_EXEC_LEDGER.jsonl": b"{}\n"}])
    # B7(c) freeze record
    refused("A23_freeze_record_missing", "FREEZE_RECORD", freeze_record="missing")
    refused("A24_freeze_record_names_another_commit", "FREEZE_RECORD", freeze_record="wrong")
    refused("A25_freeze_record_changed_later", "FREEZE_RECORD", freeze_record="late_change")
    # NB4: hooks are refused outside a sandbox context, before anything is read (a dummy non-sandbox context object)
    dummy = types.SimpleNamespace(kind="PRODUCTION")
    try:
        D.run_execute(OWN_SHA, ctx=dummy, evaluator=ev_ok)
        R["A26_hooks_refused_outside_sandbox"] = {"pass": False}
    except D.Refusal as exc:
        R["A26_hooks_refused_outside_sandbox"] = {"pass": exc.code == "HOOKS", "got": exc.code}
    return R


def post_marker_flows() -> dict:
    import p309_postexec as PX
    R = {}

    def run(name, evaluator=ev_ok, **kw):
        sb = new_sandbox(name)
        c = build_chain(sb)
        rc = execute(sb, evaluator=evaluator, **kw)
        return sb, c, rc

    sb, c, rc = run("F27_success")
    px = PX.checks(ctx_of(sb), second_execute=lambda: 2 if execute(sb) == ("REFUSED", "CONSUMED") else 99)
    R["F27_success_and_postexec"] = {"pass": rc == 0 and px["ok"] and not (git_dir_of(sb) / D.RUN_NONCE_NAME).exists(),
                                     "got": {"rc": rc, "postexec": px}}
    for name, ev, st in (("F28_evaluator_raises", ev_raise, "TARGET_EVALUATION_FAILED"),
                         ("F29_independent_check_fails", ev_indep, "INDEPENDENT_CHECK_FAILED"),
                         ("F30_base_exception", ev_bexc, "TARGET_EVALUATION_FAILED")):
        sb, c, rc = run(name, evaluator=ev)
        rec = json.loads(result_path(sb).read_text())
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

    def seal_only_refused(name, prepare_fn):
        sb = new_sandbox(name)
        c = build_chain(sb)
        prepare_fn(sb, c)
        before = refs(sb)
        try:
            D.run_seal_only(ctx_of(sb))
            R[name] = {"pass": False, "got": "not refused"}
        except D.Refusal as exc:
            R[name] = {"pass": exc.code == "SEAL_ONLY" and refs(sb) == before and G.TEST_PENDING_REF not in refs(sb),
                       "got": str(exc)[:160]}

    seal_only_refused("F35_seal_only_without_evidence_refused", lambda sb, c: None)

    def pending_without_marker(sb, c):
        blob = sh(sb, "hash-object", "-w", "--stdin", input_=b'{"status": "TARGET_EVALUATED"}\n').strip()
        sh(sb, "update-ref", G.TEST_PENDING_REF, blob)
    sb = new_sandbox("F36_seal_only_pending_without_marker")
    c = build_chain(sb)
    pending_without_marker(sb, c)
    try:
        D.run_seal_only(ctx_of(sb))
        R["F36_seal_only_post_marker_evidence_without_marker"] = {"pass": False}
    except D.Refusal as exc:
        R["F36_seal_only_post_marker_evidence_without_marker"] = {"pass": exc.code == "SEAL_ONLY"}
    # owner D5: seal-only creates the pending ref only for evidence bound to a marker that names a grant commit
    emer = lambda sb, gc: (git_dir_of(sb) / D.EMERGENCY_NAME).write_text(  # noqa: E731
        json.dumps({"status": "TARGET_EVALUATED", "grant": {"grant_commit": gc}}))
    seal_only_refused("F40_seal_only_emergency_without_marker", lambda sb, c: emer(sb, c["G"]))
    seal_only_refused("F41_seal_only_emergency_bound_elsewhere", lambda sb, c: (
        sh(sb, "update-ref", G.TEST_MARKER, c["G"]), emer(sb, c["Rv"])))
    seal_only_refused("F42_seal_only_marker_without_grant", lambda sb, c: (
        sh(sb, "update-ref", G.TEST_MARKER, c["Rv"]), emer(sb, c["Rv"])))
    sb, c, rc = run("F37_seal_only_other_result_at_head")
    other = commit(sb, sh(sb, "rev-parse", "HEAD").strip(), {D.SANDBOX_RESULT_REL: b'{"status": "OTHER"}\n'},
                   "other result")
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
    rec = json.loads(result_path(sb).read_text()) if result_path(sb).exists() else {}
    R["F39_recording_failure_sealed"] = {"pass": rc == 5 and rec.get("status") == "POST_MARKER_RECORDING_FAILED",
                                         "got": rc}
    return R


# ------------------------------------------- R4 follow-up 3: the host-git check (rev. 2c A43, A44; R4F3-C1, NF7, NF8)
def host_git_flows() -> dict:
    """a repository hook (planted as a plain, NON-executable file: git never runs it) or a disallowed repository config
    key is refused with HOST_GIT before any ref write: by execute before the marker (NF8), by execute's re-check after
    the control (NF7), by the post-marker re-check before the persist (NF7: the evidence goes to the emergency file and
    nothing is persisted as a ref), and by seal-only (R4F3-C1), which seals once the hook or key is gone."""
    R = {}
    HOOK = "reference-transaction"
    hook = lambda sb: (git_dir_of(sb) / "hooks" / HOOK).write_text("# TEST_ONLY planted hook; not executable\n")  # noqa: E731
    unhook = lambda sb: (git_dir_of(sb) / "hooks" / HOOK).unlink()  # noqa: E731

    def badkey(sb):
        cfg = git_dir_of(sb) / "config"
        saved = cfg.read_bytes()
        cfg.write_bytes(saved + b"[core]\n\thooksPath = /nonexistent-p309-test\n")
        return lambda: cfg.write_bytes(saved)

    def state(sb):
        return (refs(sb), sh(sb, "rev-parse", "HEAD"), (git_dir_of(sb) / D.EMERGENCY_NAME).exists(),
                (git_dir_of(sb) / D.RUN_NONCE_NAME).exists(), result_path(sb).exists())

    def bad_seal(ctx, blob, msg):
        raise OSError("stub: seal failed")
    # H01 / H02: execute, before the marker
    for name, plant in (("H01_execute_hook_refused_before_marker", hook),
                        ("H02_execute_config_key_refused_before_marker", badkey)):
        sb = new_sandbox(name)
        build_chain(sb)
        plant(sb)
        before = state(sb)
        out = execute(sb)
        R[name] = {"pass": out == ("REFUSED", "HOST_GIT") and state(sb) == before and G.TEST_MARKER not in refs(sb),
                   "got": str(out)}
    # H03 / H04: a hook that appears during the historical control is refused by the re-check, before the
    # CONTROL_FAILED seal or the marker (nothing sealed, nothing consumed)
    for name, base in (("H03_hook_during_control_refused_before_marker", OK_CONTROL),
                       ("H04_hook_during_failed_control_refused_before_seal", BAD_CONTROL)):
        sb = new_sandbox(name)
        build_chain(sb)
        before = state(sb)
        out = execute(sb, control=lambda: (hook(sb), base())[1])
        R[name] = {"pass": out == ("REFUSED", "HOST_GIT") and state(sb) == before and G.TEST_MARKER not in refs(sb),
                   "got": str(out)}
    # H05: a hook that appears during the evaluation: no pending ref, the evidence goes to the emergency file (exit 4);
    # seal-only refuses while the hook exists and seals once it is removed
    sb = new_sandbox("H05_hook_during_evaluation")
    build_chain(sb)
    rc = execute(sb, evaluator=lambda con, prep: (hook(sb), ev_ok(con, prep))[1])
    mid = state(sb)
    try:
        D.run_seal_only(ctx_of(sb))
        so = "not refused"
    except D.Refusal as exc:
        so = exc.code
    after = state(sb)
    unhook(sb)
    rc2 = D.run_seal_only(ctx_of(sb))
    R["H05_hook_during_evaluation_emergency_then_seal_only"] = {
        "pass": rc == 4 and G.TEST_MARKER in mid[0] and G.TEST_PENDING_REF not in mid[0] and mid[2] and not mid[4]
        and so == "HOST_GIT" and after == mid and rc2 == 0 and status_of(sb) == "TARGET_EVALUATED"
        and G.TEST_PENDING_REF in refs(sb), "got": [rc, so, rc2]}
    # H06 / H07: seal-only on persisted, unsealed evidence (the seal failed): refused while a hook or a disallowed key
    # is present, nothing written; sealed once it is removed
    for name, plant in (("H06_seal_only_hook_refused", lambda sb: (hook(sb), lambda: unhook(sb))[1]),
                        ("H07_seal_only_config_key_refused", badkey)):
        sb = new_sandbox(name)
        build_chain(sb)
        rc = execute(sb, sealer=bad_seal)
        undo = plant(sb)
        before = state(sb)
        try:
            D.run_seal_only(ctx_of(sb))
            so = "not refused"
        except D.Refusal as exc:
            so = exc.code
        after = state(sb)
        undo()
        rc2 = D.run_seal_only(ctx_of(sb))
        R[name] = {"pass": rc == 4 and so == "HOST_GIT" and after == before and rc2 == 0
                   and status_of(sb) == "TARGET_EVALUATED", "got": [rc, so, rc2]}
    return R


# --------------------------------------------------------------------------- R4F F2: the pre-commit grant validator
def validate_flows() -> dict:
    """validate-grant on an UNCOMMITTED candidate (a file outside the sandbox) with HEAD at the would-be parent of the
    grant commit: a PASS for the valid candidate, a named failing check for each defect, nothing written or moved; and
    a PASS candidate, committed alone, is admitted by execute (the validator and execute agree)."""
    R = {}
    man = (REPO / D.MANIFEST_REL).read_bytes()

    def setup(name):
        sb = new_sandbox(name)
        c = build_chain(sb)
        parent = sh(sb, "rev-parse", f"{c['G']}~1").strip()          # drop the grant commit: HEAD = its parent
        sh(sb, "update-ref", SB_BRANCH, parent)
        sh(sb, "reset", "-q", "--hard", parent)
        return sb, c

    def validate(name, over=None, dirty=False, edit=None):
        sb, c = setup(name)
        g = test_grant(sb, man, c["F"], c["Q"], c["Rv"])
        g.update(over or {})
        for k in [k for k, v in g.items() if v is DROP]:
            del g[k]
        cand = SCRATCH / f"{name}.candidate.json"
        cand.write_text(json.dumps(g, sort_keys=True))
        if dirty:
            (sb / NS / "evidence").mkdir(parents=True, exist_ok=True)
            (sb / NS / "evidence" / "dirty.txt").write_text("x")
        if edit:
            edit(sb)
        before = (refs(sb), sh(sb, "rev-parse", "HEAD"), sh(sb, "status", "--porcelain", "--untracked-files=all"))
        out = D.validate_grant(cand, OWN_SHA, ctx=ctx_of(sb))
        after = (refs(sb), sh(sb, "rev-parse", "HEAD"), sh(sb, "status", "--porcelain", "--untracked-files=all"))
        return sb, c, cand, out, before == after

    sb, c, cand, out, same = validate("V01_valid_candidate_passes")
    R["V01_valid_candidate_passes"] = {"pass": out["pass"] and same, "got": out.get("checks")}
    # V09: the same candidate committed ALONE on top of the validated HEAD is admitted by execute
    head = sh(sb, "rev-parse", "HEAD").strip()
    gc = commit(sb, head, {G._TEST_GRANT_PATH: cand.read_bytes()}, "TEST_ONLY grant (validated candidate)")
    sh(sb, "update-ref", SB_BRANCH, gc)
    sh(sb, "reset", "-q", "--hard", gc)
    R["V09_validated_candidate_admitted_by_execute"] = {"pass": execute(sb) == 0}
    for name, over, key in (
            ("V02_placeholder_authority", {"authority": "<THE OWNER'S GRANT INSTRUCTION, verbatim reference>"},
             "authority"),
            ("V03_missing_worktree", {"execution_host": {"host_id_sha256": G.host_id()}}, "worktree"),
            ("V04_short_horizon", {"not_after_utc": utc_in(86400)}, "not_after_horizon"),
            ("V05_wrong_verifier", {"verifier_id": "sha256:" + "7" * 64}, "verifier_id"),
            ("V06_wrong_host", {"execution_host": {"host_id_sha256": "6" * 64, "worktree": "/x"}},
             "guard_candidate_check")):
        sb, c, cand, out, same = validate(name, over)
        R[name] = {"pass": out["pass"] is False and out["checks"].get(key) is False and same,
                   "got": {k: v for k, v in out["checks"].items() if not v}}
    # V10 (R4 follow-up 2 NF3): the production sequence -- validate, ONE ledger-only window commit (the ledger lines
    # validate-grant writes in production), then the candidate committed alone -- is admitted by execute
    sb, c, cand, out, same = validate("V10_window_commit_between_validation_and_grant")
    head = sh(sb, "rev-parse", "HEAD").strip()
    ztl, exl = f"{NS}/ledger/ZERO_TARGET_LEDGER.jsonl", f"{NS}/ledger/EXPOSURE_LEDGER.jsonl"
    w = commit(sb, head, {ztl: sh(sb, "show", f"{head}:{ztl}").encode() + b'{"validate": 1}\n',
                          exl: sh(sb, "show", f"{head}:{exl}").encode() + b'{"validate": 1}\n'}, "ledger-only window")
    gc = commit(sb, w, {G._TEST_GRANT_PATH: cand.read_bytes()}, "TEST_ONLY grant after the window commit")
    sh(sb, "update-ref", SB_BRANCH, gc)
    sh(sb, "reset", "-q", "--hard", gc)
    R["V10_window_commit_between_validation_and_grant"] = {"pass": out["pass"] and same and execute(sb) == 0}
    sb, c, cand, out, same = validate("V07_wrong_chain_commit", {"qualification_commit": "8" * 40})
    R["V07_wrong_chain_commit"] = {"pass": out["pass"] is False and out["chain"] is False and same}
    sb, c, cand, out, same = validate("V08_dirty_tree", dirty=True)
    R["V08_dirty_tree"] = {"pass": out["pass"] is False and out["clean_tree_before"] is False and same}
    # V11 (R4 follow-up 3 NF8): a planted repository hook fails the host_git check
    sb, c, cand, out, same = validate("V11_hook_present", edit=lambda sb: (
        git_dir_of(sb) / "hooks" / "reference-transaction").write_text("# TEST_ONLY planted hook; not executable\n"))
    pre = out.get("execute_prechecks", {})
    R["V11_hook_present"] = {"pass": out["pass"] is False and {k for k, v in pre.items() if not k.endswith("_refusal")
                                                                and not v} == {"host_git"}
                             and "HOST_GIT" in pre.get("host_git_refusal", "") and all(out["checks"].values())
                             and out["chain"] and same, "got": pre}
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
            "verdict_details": {}, "verdict_source": vid, "adapter_records": [], "log_digest": ""}
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
            return dict(base, W_status="CERTIFIED", certificates=cs, verdicts={c["sha256"]: v for c in cs},
                        verdict_details={c["sha256"]: {"verdict": v, "reason": "stub"} for c in cs})
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
    # S15 (R4 B4): a worker killed below its CPU limit is a runtime failure, never a budget fallback
    def killer(spec):
        return subprocess.Popen([sys.executable, "-c", "import os, signal; os.kill(os.getpid(), signal.SIGKILL)"])
    run = D.run_jobs([{"x": 1}], budget_s=100, job_limit_s=60, workers=1, runner=killer)
    try:
        D.stage1a("decoy", cell, dict(D.GEOMETRY), vid, workers=2, runner=killer)
        raised = False
    except RuntimeError:
        raised = True
    R["S15_sigkill_below_limit_is_job_exception"] = {"pass": run["results"][0]["kind"] == "JOB_EXCEPTION" and raised,
                                                     "got": run["results"][0]}
    # S17 (delta-2 E2): a SIGXCPU below the CPU limit (a deliberate kill -XCPU) is a runtime failure, not a budget stop
    def xcpu(spec):
        import resource as _r

        def nocore():
            _r.setrlimit(_r.RLIMIT_CORE, (0, 0))
        return subprocess.Popen([sys.executable, "-c", "import os, signal; os.kill(os.getpid(), signal.SIGXCPU)"],
                                preexec_fn=nocore)
    run = D.run_jobs([{"x": 1}], budget_s=100, job_limit_s=60, workers=1, runner=xcpu)
    try:
        D.stage1a("decoy", cell, dict(D.GEOMETRY), vid, workers=2, runner=xcpu)
        raised = False
    except RuntimeError:
        raised = True
    R["S17_sigxcpu_below_limit_is_job_exception"] = {"pass": run["results"][0]["kind"] == "JOB_EXCEPTION" and raised,
                                                     "got": run["results"][0]}
    # S16 (R4 NB6): a target-mode job refuses unless it is a child of the live execute process holding the nonce
    outs = {}
    for name, spec in (("no_nonce", {}), ("wrong_token", {"_git_dir": str(SCRATCH), "_run_token": "x"})):
        try:
            D.check_run_nonce(spec)
            outs[name] = "ran"
        except RuntimeError:
            outs[name] = "refused"
    R["S16_target_job_needs_the_run_nonce"] = {"pass": set(outs.values()) == {"refused"}, "got": outs}
    _ = GT
    return R


# ------------------------------------------------------------------ integration: the whole path in one process
def _certs(pattern: str) -> list:
    out = []
    for j in range(4):
        d = json.loads((D.E.RNS / f"evidence/srk_decoys_cell/{pattern}_S{j}.json").read_text())
        out += [c for c in d["certificates"].values() if c.get("status") == "CERTIFIED"]
    return out


def integration_flows() -> dict:
    """R4 B2 and B7(a).  I01/I02: P10 runs the real band-scoped variant in REVIEW mode (TEST context) on the 16
    committed TEST-band h3 decoy-cell certificates sealed at the record's top level, and P5 runs seal-only on the
    interpreter-flag path.  I03: execute's whole evaluation (Stage 1a, Stage 1b, S, Stage 2, decision, recording) in
    one process, in execute's import order, on the declared decoys: stub job runners return the committed a2_h5
    certificates and manufactured, internally consistent Stage-1b rung records on a synthetic out-of-band interval
    (delta-2 E4); Stage 2 runs on the QC14' manufactured inputs; then the sandbox seal and P1-P10.  Nothing is
    evaluated for any tail cell."""
    import p309_postexec as PX
    import p309_rehearse as RH
    R = {}
    h3 = _certs("cell_h3_k1_2_C1_3_20_51")

    def ev_h3(verdict_of):
        def ev(con, prep):
            v = {c["sha256"]: verdict_of(c) for c in h3}
            return {"stage1a": {"certificates": h3, "verdicts": v,
                                "verdict_details": {k: {"verdict": x, "reason": "stub"} for k, x in v.items()}},
                    "decision": {"mechanical_outcome": "NOT_CLOSED"}}
        return ev
    for name, vf, want in (("I01_review_mode_P10_TEST_band", lambda c: "ACCEPT", True),
                           ("I02_review_mode_detects_a_wrong_sealed_verdict",
                            lambda c: "REJECT" if c["sha256"] == h3[0]["sha256"] else "ACCEPT", False)):
        sb = new_sandbox(name)
        build_chain(sb)
        rc = execute(sb, evaluator=ev_h3(vf))
        rec = json.loads(result_path(sb).read_text())
        p10 = PX.reverify(rec, sandbox=sb)
        px = PX.checks(ctx_of(sb))
        R[name] = {"pass": rc == 0 and len(h3) == 16 and p10 is want and px["ok"] and "stage1a" in rec
                   and "stage1a" not in rec.get("target", {}), "got": {"rc": rc, "P10": p10, "postexec": px}}
    # I03 the whole evaluation in one process, on decoys
    m = D.load_manifest()
    con = D.load_consumer(m)                              # execute's order: consumer, RLR307 helpers, then SRK side
    D.load_rlr307(m)
    import srk_gate  # noqa: F401  (as the historical control does)
    vid = "sha256:" + D.pin_table(m)[D.VARIANT_REL][0]
    a2 = _certs("cell_h5_k1_2_C1_2_37_72")
    # delta-2 E4: MANUFACTURED Stage-1b rung records (the S12 fixture pattern), internally consistent with the pinned
    # certifier's kappa and the RLR307 independent reconstruction, on a synthetic out-of-band interval; no campaign
    # results file and no cover-cell entry is read
    cell_1b = (F(1, 2), F(51, 100))
    sb = new_sandbox("I03_whole_evaluation_on_decoys")
    build_chain(sb)
    # the isolated certifier is loaded only for its kappa constants; its drift adapter is a TEST-context one (R4F T7)
    mods = D._load_certifier_isolated(D.load_rlr307(m)["rlr307_pinned"], G.producer_adapter(G.TestContext(sb)))
    kappa = (mods["c1b_certpw"].KAPPA1, mods["c1b_certpw"].KAPPA2)
    IND = D._ind()

    def mrec(block, degree):
        f = F(100 + 7 * block + degree, 100)
        rec = {"status": "CERTIFIED", "degree": degree, "A_bar": D.fs(3 * f), "tau": "2", "D_lo": "1/2",
               "C_T": D.fs(5 / f), "D1": "1/3", "D2": "1/5", "L1_up": D.fs(F(1, 7) / f), "L2_up": "1/9",
               "tau_a_lo": "1/2", "C_R": D.fs(4 * f), "tau_a_up": "1", "S2_up": "1/3", "TN_up": "1/4",
               "Lambda_lo": "1/6"}
        sup = IND.block_supply(rec, *kappa)
        rec.update({k: D.fs(sup[k]) for k in ("A0_SUPPLY", "A1_SUPPLY", "A2_SUPPLY", "G0", "G1", "G2")})
        return rec

    def run1a(spec):
        cs = [c for c in a2 if c["block"] == spec["block"] and c["degree"] == spec["degree"]]
        return {"kind": "JOB_RETURNED", "W_status": "CERTIFIED", "V_status": {}, "certificates": cs,
                "verdicts": {c["sha256"]: "ACCEPT" for c in cs},
                "verdict_details": {c["sha256"]: {"verdict": "ACCEPT", "reason": "stub (P10 re-verifies)"} for c in cs},
                "verdict_source": vid, "adapter_records": [], "log_digest": ""}

    def run1b(spec):
        return {"kind": "JOB_RETURNED", "block": spec["block"], "degree": spec["degree"], "status": "CERTIFIED",
                "record": mrec(spec["block"], spec["degree"]), "adapter_records": []}
    mf = RH.manufactured()
    prep = {"cell": RH.DECOY_CELL, "cell_1b": cell_1b, "verifier_id": vid, "manifest": m,
            "A_I1": mf["A"], "ci": {k: mf[k] for k in ("meas", "aux", "ad", "cov")}, "cell_label": "DECOY_INTEGRATION"}
    seen = {}

    def ev_decoys(con_, prep_):
        out = D.evaluate(con, prep, mode="decoy", runner1a=_stub_runner(run1a), runner1b=_stub_runner(run1b))
        seen["out"] = out
        return out
    rc = execute(sb, evaluator=ev_decoys)
    rec = json.loads(result_path(sb).read_text()) if result_path(sb).exists() else {}
    px = PX.checks(ctx_of(sb), reverify=lambda r: PX.reverify(r, sandbox=sb))
    s1a = rec.get("stage1a") or {}
    tgt = rec.get("target") or {}
    ok = (rc == 0 and rec.get("status") == "TARGET_EVALUATED"
          and set(s1a.get("verdict_details", {})) == set(s1a.get("verdicts", {})) and s1a.get("certificates")
          and tgt.get("stage1b", {}).get("cell", {}).get("status") == "CERTIFIED"
          and tgt.get("S") == {j: D.fs(x) for j, x in D._ind().consumed(mf["A"], {
              "A1_SUPPLY": tgt["stage1b"]["cell"]["A1_SUPPLY_max"],
              "A2_SUPPLY": tgt["stage1b"]["cell"]["A2_SUPPLY_max"]}).items()}
          and all(v for k, v in px.items() if k.startswith("P") and not k.startswith("P8"))
          and px.get("P8_single_target_cell") is False)          # the evaluated cell is the decoy label, not a target
    R["I03_whole_evaluation_on_decoys"] = {"pass": bool(ok), "got": {"rc": rc, "status": rec.get("status"),
                                                                     "postexec": px, "gate": s1a.get("gate", {}).get("source")}}
    return R


if __name__ == "__main__":
    D.E.log("tests/test_p309_exactly_once.py", "QC11 exactly-once sandbox flows (synthetic TEST names only) and the "
            "integration flows on declared decoys", klass="NONTARGET_DECOY",
            drifts=[["1/2", "37/72"], ["1/2", "51/100"], ["341/1024", "201/512"]],
            notes="sandboxes are light repositories under the scratchpad (alternates, no remote), never pushed; no "
                  "production ref is created; stub job runners; I01/I02 verify the 16 committed TEST-band h3 decoy "
                  "certificates in review mode; I03 composes the committed a2_h5 decoy certificates and MANUFACTURED "
                  "Stage-1b records on a synthetic interval and runs Stage 2 on the QC14' manufactured inputs; no "
                  "cover-cell entry and no campaign results file is read; nothing is evaluated for any tail cell")
    res = {}
    res.update(pre_marker_flows())
    res.update(admission_flows())
    res.update(validate_flows())
    res.update(post_marker_flows())
    res.update(host_git_flows())
    res.update(stage_flows())
    res.update(integration_flows())
    bad = [k for k, v in res.items() if not v.get("pass")]
    leaked = []
    for p in sorted(SCRATCH.iterdir()):
        try:
            leaked += [r for r in sh(p, "for-each-ref", "--format=%(refname)").split() if r.startswith(G._FORBIDDEN_NAMESPACES)]
        except RuntimeError:
            pass
    leaked += [r for r in sh(REPO, "for-each-ref", "--format=%(refname)").split() if r.startswith(G._FORBIDDEN_NAMESPACES)]
    res["Z_no_production_ref_anywhere"] = {"pass": not leaked, "got": leaked}
    ok = all(v.get("pass") for v in res.values())
    out = {"utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "flows": len(res),
           "all_pass": ok, "driver_sha256": OWN_SHA, "test_sha256": D.sha(Path(__file__).read_bytes()), "results": res}
    (D.E.evidence_dir("fc6") / "EXACTLY_ONCE_FLOWS.json").write_text(json.dumps(out, indent=1, sort_keys=True,
                                                                                 default=str) + "\n")
    for k, v in res.items():
        print(f"[{'PASS' if v.get('pass') else 'FAIL'}] {k}  {'' if v.get('pass') else v.get('got', '')}")
    sys.exit(0 if ok else 1)
