"""QC10 (and the sandbox part of QC07): exactly-once flows of the cell-307 driver, on DECOY state only.

Every flow runs in a `git clone --shared` sandbox checked out at the freeze commit.
* The sandbox has its own refs, index and worktree. Its only link to the real repository is read-only object sharing
  through alternates, so no marker, pending ref, commit or file is ever created in the real repository.
* The driver is executed from the sandbox's frozen bytes. Only its four QUALIFIED_* identity constants are re-pointed
  at the sandbox.
* The control, the consumer loader, `prepare` and the evaluator are STUBS. No cell is evaluated, and nothing is
  certified in the band.
* Grant chains are synthetic sandbox commits.
"""
from __future__ import annotations

import concurrent.futures
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
import types
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
REPO = HERE.parents[4]
CP = "level4/closure_proofs/"
NS_REL = CP + "p5y_k5_cell307_rlr_r1"
PY = sys.executable
GENV = {"PATH": "/usr/bin:/bin", "LC_ALL": "C", "GIT_OPTIONAL_LOCKS": "0", "HOME": os.environ.get("HOME", "/var/empty")}
SIGS = (signal.SIGINT, signal.SIGTERM, signal.SIGHUP, signal.SIGQUIT, signal.SIGALRM)


def g(root: Path, *args, check=True) -> str:
    p = subprocess.run(["/usr/bin/git", "-C", str(root), *args], capture_output=True, text=True, env=GENV,
                       stdin=subprocess.DEVNULL)
    if check and p.returncode:
        raise RuntimeError(f"git {args[:3]} failed: {p.stderr[:300]}")
    return p.stdout.strip()


class Sandbox:
    def __init__(self, tmp: Path, freeze: str):
        root = tmp / "sbx"
        subprocess.run(["/usr/bin/git", "clone", "-q", "--shared", "--no-checkout", str(REPO), str(root)], check=True,
                       env=GENV, capture_output=True)
        self.root = root.resolve()
        g(self.root, "checkout", "-q", "-B", "p5y-k5-cell307-rlr-r1", freeze)
        self.freeze = freeze
        if g(self.root, "rev-parse", "--path-format=absolute", "--git-common-dir") == \
                g(REPO, "rev-parse", "--path-format=absolute", "--git-common-dir"):
            raise RuntimeError("the sandbox shares the real common dir")

    def p(self, rel: str) -> Path:
        return self.root / rel

    def write(self, rel: str, text: str) -> None:
        self.p(rel).parent.mkdir(parents=True, exist_ok=True)
        self.p(rel).write_text(text)

    def commit(self, rels: list, msg: str) -> str:
        g(self.root, "add", "-f", *rels)
        g(self.root, "commit", "-q", "-m", msg)
        return g(self.root, "rev-parse", "HEAD")

    def reset(self, commit: str) -> None:
        for ref in g(self.root, "for-each-ref", "--format=%(refname)").split():
            if ref.startswith(("refs/p5y-k5-cell307-rlr-r1/", "refs/rlr-tail/")):
                g(self.root, "update-ref", "-d", ref)
        gd = Path(g(self.root, "rev-parse", "--path-format=absolute", "--git-dir"))
        for f in gd.glob("rlr307-*"):
            f.unlink()
        ev = self.p(NS_REL + "/evidence")
        if ev.is_symlink():
            ev.unlink()
        g(self.root, "checkout", "-q", "-f", "p5y-k5-cell307-rlr-r1")
        g(self.root, "reset", "-q", "--hard", commit)
        g(self.root, "clean", "-qfdx", "--", NS_REL)


def build_chain(sb: Sandbox, drv_sha: str, *, review_line="QUALIFICATION_ACCEPTED", qual_pass=True, drv_override=None,
                extra_commit=False, manifest_sha=None) -> dict:
    sb.reset(sb.freeze)
    q = {"schema": "sandbox-decoy", "pass": qual_pass, "review_mode": False, "freeze_commit": sb.freeze}
    sb.write(NS_REL + "/qualification/RLR307_QUALIFICATION.json", json.dumps(q))
    qc = sb.commit([NS_REL + "/qualification/RLR307_QUALIFICATION.json"], "sandbox: qualification (decoy)")
    sb.write(NS_REL + "/review/RLR307_QUALIFICATION_REVIEW.md", f"# sandbox review (decoy)\n{review_line}\n")
    rc = sb.commit([NS_REL + "/review/RLR307_QUALIFICATION_REVIEW.md"], "sandbox: review (decoy)")
    if extra_commit:
        sb.write(NS_REL + "/review/EXTRA.md", "extra\n")
        sb.commit([NS_REL + "/review/EXTRA.md"], "sandbox: an extra commit breaking the chain")
    man = manifest_sha or __import__("hashlib").sha256(sb.p(NS_REL + "/protocol/RLR307_FREEZE.json").read_bytes()).hexdigest()
    grant = {"schema": "rebaseguard.p5y.k5.cell307-rlr-r1.grant.v1", "exactly_once": True, "cell": 307, "route": "RLR",
             "closure_only": True, "driver_sha256": drv_override or drv_sha, "freeze_commit": sb.freeze,
             "qualification_commit": qc, "qualification_review_commit": rc, "input_manifest_sha256": man}
    sb.write(NS_REL + "/authorization/RLR307_GRANT.json", json.dumps(grant))
    gc = sb.commit([NS_REL + "/authorization/RLR307_GRANT.json"], "sandbox: grant (decoy)")
    return {"qual": qc, "review": rc, "grant": gc}


def load_driver(sb: Sandbox, tag: str) -> types.ModuleType:
    path = sb.p(NS_REL + "/code/rlr307_driver.py")
    saved = list(sys.path)
    mod = types.ModuleType(f"rlr307_driver_{tag}")
    mod.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), "exec"), mod.__dict__)
    sys.path[:] = saved
    mod.QUALIFIED_WORKTREE = str(sb.root)
    mod.QUALIFIED_GIT_DIR = str(sb.root / ".git")
    mod.QUALIFIED_COMMON_DIR = str(sb.root / ".git")
    calls = {"evaluator": 0}

    def stub_control(con, k):
        return {"cell": k, "supply": "STUB", "reproduces_C2_exactly": True, "field_matches": {}, "provenance": {},
                "evaluated": {}, "_A": {"A0": F(1), "A1": F(1), "A2": F(1)}, "_ci": None}

    def stub_prepare(con, ctl, own_sha, grant, mods):
        return {"blocks": [], "kappa_check": {"stub": True}}

    def stub_eval(con, prep):
        calls["evaluator"] += 1
        return {"cell": 307, "decision": {"mechanical_outcome": "STUB_DECOY"}}

    mod.load_consumer = lambda: {"stub": True}
    mod.control = stub_control
    mod._stub = {"calls": calls, "prepare": stub_prepare, "evaluator": stub_eval}
    return mod


def restore_signals(saved: dict) -> None:
    signal.alarm(0)
    for s, h in saved.items():
        signal.signal(s, h)


def run_flows(freeze: str, tmp: Path) -> dict:
    saved = {s: signal.getsignal(s) for s in SIGS}
    tmp.mkdir(parents=True, exist_ok=True)
    sb = Sandbox(tmp, freeze)
    real_sha = __import__("hashlib").sha256(sb.p(NS_REL + "/code/rlr307_driver.py").read_bytes()).hexdigest()
    res, n = {}, [0]

    def fresh(**kw):
        n[0] += 1
        ch = build_chain(sb, real_sha, **kw)
        D = load_driver(sb, f"s{n[0]}")
        return D, ch

    def execute(D, evaluator=None, **inj):
        try:
            rc = D.run_execute(real_sha, prepare=D._stub["prepare"], evaluator=evaluator or D._stub["evaluator"], **inj)
            return {"exit": rc}
        except D.Refusal as e:
            return {"refused": e.code}
        finally:
            restore_signals(saved)

    def marker(D):
        return g(sb.root, "rev-parse", "-q", "--verify", D.CONSUMED_REF, check=False)

    def head_result(D):
        raw = subprocess.run(["/usr/bin/git", "-C", str(sb.root), "show", f"HEAD:{D.RESULT_REL}"], capture_output=True,
                             env=GENV).stdout
        return json.loads(raw) if raw else None

    # ---- X: the successful flow, the rerun and seal-only
    D, ch = fresh()
    r = execute(D)
    rec = head_result(D)
    parent = g(sb.root, "rev-parse", "HEAD^")
    mat = sb.p(D.RESULT_REL)
    res["X01_success"] = {"ok": r == {"exit": 0} and marker(D) == ch["grant"] and parent == ch["grant"]
                          and rec and rec["status"] == "TARGET_EVALUATED" and rec["target_evaluations"] == 1
                          and mat.is_file() and not mat.is_symlink()
                          and mat.read_bytes() == subprocess.run(["/usr/bin/git", "-C", str(sb.root), "show",
                                                                  f"HEAD:{D.RESULT_REL}"], capture_output=True,
                                                                 env=GENV).stdout
                          and D._stub["calls"]["evaluator"] == 1, "run": r}
    r2 = execute(D)
    res["X02_rerun_refused"] = {"ok": r2.get("refused") == "CONSUMED" and D._stub["calls"]["evaluator"] == 1, "run": r2}
    try:
        rc = D.run_seal_only()
    except D.Refusal as e:
        rc = f"refused {e.code}"
    finally:
        restore_signals(saved)
    res["X03_seal_only_no_recompute"] = {"ok": rc == 0 and D._stub["calls"]["evaluator"] == 1, "run": rc}

    # ---- C: control failure (target not consumed)
    D, ch = fresh()
    D.control = lambda con, k: {"cell": k, "reproduces_C2_exactly": False, "field_matches": {"Gamma_exact": False},
                                "provenance": {}, "evaluated": {}, "supply": "STUB", "_A": {}, "_ci": None}
    r = execute(D)
    rec = head_result(D)
    res["C01_control_failed"] = {"ok": r == {"exit": 3} and not marker(D) and rec and rec["status"] == "CONTROL_FAILED"
                                 and D._stub["calls"]["evaluator"] == 0, "run": r}
    r = execute(D)                                   # the sealed CONTROL_FAILED record now blocks any rerun
    res["C02_rerun_after_control_failed_refused"] = {"ok": "refused" in r and D._stub["calls"]["evaluator"] == 0,
                                                     "run": r}

    # ---- T: refusals before the marker (each from a fresh grant state; the evaluator must never run)
    def T(name, plant, want, **chain_kw):
        D, ch = fresh(**chain_kw)
        undo = plant(D) if plant else None
        before = marker(D)                          # a planted marker is part of the plant; the driver must not touch it
        r = execute(D)
        ok = r.get("refused") == want and marker(D) == before and D._stub["calls"]["evaluator"] == 0
        if callable(undo):
            undo()
        res[name] = {"ok": ok, "run": r, "want": want}

    exec_dir = NS_REL + "/evidence/execution"

    def mk_file(rel):
        def f(D):
            sb.p(rel).parent.mkdir(parents=True, exist_ok=True)
            sb.p(rel).write_text("planted\n")
        return f

    def mk_dir(rel):
        return lambda D: sb.p(rel).mkdir(parents=True, exist_ok=True)

    def mk_link(rel, target):
        def f(D):
            sb.p(rel).parent.mkdir(parents=True, exist_ok=True)
            os.symlink(target, sb.p(rel))
        return f

    def mk_fifo(rel):
        def f(D):
            sb.p(rel).parent.mkdir(parents=True, exist_ok=True)
            os.mkfifo(sb.p(rel))
        return f

    outside = tmp / "outside_target.json"
    T("T01_file_at_result", mk_file(exec_dir + "/RLR307_CELL307_RESULT.json"), "TARGET_ARTIFACT_EXISTS")
    T("T02_directory_at_execution_dir", mk_dir(exec_dir), "RESULT_PATH_OCCUPIED")
    T("T03_symlink_out_at_tmp", mk_link(exec_dir + "/RLR307_CELL307_RESULT.tmp", str(outside)), "RESULT_PATH_OCCUPIED")
    T("T04_broken_symlink_at_result", mk_link(exec_dir + "/RLR307_CELL307_RESULT.json", str(tmp / "nowhere")),
      "TARGET_ARTIFACT_EXISTS")
    T("T05_fifo_at_partial", mk_fifo(exec_dir + "/RLR307_CELL307_RESULT.partial"), "RESULT_PATH_OCCUPIED")
    T("T06_ignored_tmp_file", mk_file(exec_dir + "/RLR307_CELL307_RESULT.json.tmp"), "RESULT_PATH_OCCUPIED")

    def evidence_link(D):
        ev = sb.p(NS_REL + "/evidence")
        real = sb.p(NS_REL + "/evidence_real")
        ev.rename(real)
        os.symlink(str(real), str(ev))

        def undo():
            ev.unlink()
            real.rename(ev)
        return undo
    T("T07_symlinked_evidence_dir", evidence_link, "RESULT_PATH_OCCUPIED")

    def dirty(D):
        p = sb.p(NS_REL + "/protocol/RLR307_PROTOCOL.md")
        p.write_text(p.read_text() + "\nplanted\n")
    T("T08_dirty_tree", dirty, "DIRTY_TREE")
    T("T09_ignored_object_in_namespace", mk_file(NS_REL + "/code/planted.log"), "IGNORED_OBJECT")
    T("T10_prior_marker_ref", lambda D: g(sb.root, "update-ref", D.CONSUMED_REF, g(sb.root, "rev-parse", "HEAD")),
      "CONSUMED")
    T("T11_pending_ref", lambda D: g(sb.root, "update-ref", D.PENDING_REF, g(sb.root, "rev-parse", "HEAD")), "CONSUMED")
    T("T12_overnight_draft_ref_name", lambda D: g(sb.root, "update-ref", "refs/rlr-tail/cell307-target-consumed",
                                                  g(sb.root, "rev-parse", "HEAD")), "CONSUMED")

    def emergency(D):
        gd = Path(g(sb.root, "rev-parse", "--path-format=absolute", "--git-dir"))
        (gd / D.EMERGENCY_NAME).write_text("{}\n")
    T("T13_emergency_file", emergency, "TARGET_ARTIFACT_EXISTS")
    T("T14_wrong_branch", lambda D: g(sb.root, "checkout", "-q", "-b", "other-branch"), "WRONG_BRANCH")

    def no_grant(D):
        g(sb.root, "reset", "-q", "--hard", "HEAD^")
    T("T16_no_grant", no_grant, "GRANT_MISSING")
    T("T17_grant_wrong_driver_sha", None, "GRANT_INVALID", drv_override="0" * 64)
    T("T18_broken_chain", None, "GRANT_INVALID", extra_commit=True)
    T("T19_review_rejected", None, "REVIEW_VERDICT", review_line="QUALIFICATION_REJECTED")
    T("T20_qualification_not_pass", None, "GRANT_INVALID", qual_pass=False)
    T("T21_grant_wrong_manifest", None, "GRANT_INVALID", manifest_sha="1" * 64)

    # function-level tamper tests (the file is restored afterwards)
    D, ch = fresh()
    tampers = {}
    for key, how in (("registry_c2", "PIN_MISMATCH"),):
        p = sb.p(D.PINS[key][0])
        orig = p.read_bytes()
        p.write_bytes(orig + b" ")
        try:
            D.check_bindings()
            tampers[key] = "NOT_REFUSED"
        except D.Refusal as e:
            tampers[key] = e.code
        finally:
            p.write_bytes(orig)
    hp = sb.p(NS_REL + "/code/rlr307_stage1.py")
    orig = hp.read_bytes()
    hp.write_bytes(orig + b"# planted\n")
    try:
        D.check_helpers()
        tampers["helper"] = "NOT_REFUSED"
    except D.Refusal as e:
        tampers["helper"] = e.code
    finally:
        hp.write_bytes(orig)
    cpf = sb.p(D.PIN.CUSUM_REL + "c1b_pw.py")
    orig = cpf.read_bytes()
    cpf.write_bytes(orig + b"# planted\n")
    try:
        D.PIN.pinned_bytes(sb.root, "c1b_pw")
        tampers["certifier"] = "NOT_REFUSED"
    except D.PIN.PinError:
        tampers["certifier"] = "PinError"
    finally:
        cpf.write_bytes(orig)
    res["T22_tampered_inputs"] = {"ok": tampers == {"registry_c2": "PIN_MISMATCH", "helper": "HELPER_PIN_MISMATCH",
                                                    "certifier": "PinError"}, "run": tampers}

    # CLI: interpreter flags and identity (the real CLI never runs in a non-qualified worktree)
    drv = str(sb.p(NS_REL + "/code/rlr307_driver.py"))
    a = subprocess.run([PY, drv, "execute"], capture_output=True, text=True, env=GENV, stdin=subprocess.DEVNULL)
    b = subprocess.run([PY, "-I", "-S", "-B", drv, "execute"], capture_output=True, text=True, env=GENV,
                       stdin=subprocess.DEVNULL)
    res["T15_cli_flags_and_identity"] = {"ok": a.returncode == 2 and "INTERPRETER_FLAGS" in a.stdout
                                         and b.returncode == 2 and "REPO_NOT_QUALIFIED" in b.stdout,
                                         "run": [a.stdout.strip()[-80:], b.stdout.strip()[-80:]]}

    # ---- P: failures after the marker (the target is consumed; nothing may escape; no recomputation)
    def P(name, evaluator=None, want_exit=5, want_status=None, inj=None, then_seal_only=None, patch=None):
        D, ch = fresh()
        if patch:
            patch(D)
        ev_obj = evaluator or D._stub["evaluator"]
        r = execute(D, evaluator=ev_obj, **(inj or {}))
        out = {"run": r, "marker": bool(marker(D))}
        ok = r.get("exit") == want_exit and out["marker"]
        rec = head_result(D)
        if want_status:
            ok = ok and rec is not None and rec.get("status") == want_status
        if then_seal_only is not None:
            try:
                so = D.run_seal_only()
            except D.Refusal as e:
                so = f"refused {e.code}"
            finally:
                restore_signals(saved)
            out["seal_only"] = so
            rec = head_result(D)
            ok = ok and so == then_seal_only and rec is not None
        again = execute(D, evaluator=ev_obj)
        out["rerun"] = again
        ok = ok and again.get("refused") in ("CONSUMED", "TARGET_ARTIFACT_EXISTS")
        out["evaluator_calls"] = getattr(ev_obj, "calls", D._stub["calls"]["evaluator"])
        ok = ok and out["evaluator_calls"] <= 1
        res[name] = {"ok": ok, **out}

    def counting(fn):
        def ev(con, prep):
            ev.calls += 1
            return fn()
        ev.calls = 0
        return ev

    def boom(exc):
        def f():
            raise exc
        return f

    P("P01_exception", counting(boom(RuntimeError("planted"))), 5, "TARGET_EVALUATION_FAILED")
    P("P02_independent_check_failed", None, 5, "INDEPENDENT_CHECK_FAILED",
      patch=lambda D: D._stub.__setitem__("evaluator", counting(boom(D.IndependentCheckFailed("planted")))))
    P("P03_system_exit", counting(boom(SystemExit(9))), 5, "TARGET_EVALUATION_FAILED")
    P("P04_keyboard_interrupt", counting(boom(KeyboardInterrupt())), 5, "TARGET_EVALUATION_FAILED")

    def slow():
        time.sleep(3)
        return {"decision": {}}
    P("P05_evaluation_cap", counting(slow), 5, "TARGET_EVALUATION_FAILED", patch=lambda D: setattr(D, "EVAL_CAP_S", 1))

    def unserializable():
        return {"x": {1, 2}}
    P("P06_serialization_failure", counting(unserializable), 5, "POST_MARKER_RECORDING_FAILED")

    def fail_persist(data):
        raise OSError("planted primary persistence failure")
    P("P07_primary_persistence_fails_emergency_then_seal_only", None, 4, None, inj={"persist": fail_persist},
      then_seal_only=0)

    def both_fail(D):
        D.persist_emergency = boom(OSError("planted second channel failure"))
    P("P08_both_channels_fail", None, 6, None, inj={"persist": fail_persist}, patch=both_fail)

    def fail_seal(blob, msg):
        raise OSError("planted seal failure")
    P("P09_seal_fails_then_seal_only", None, 4, None, inj={"sealer": fail_seal}, then_seal_only=0)

    def fail_mat(blob):
        raise OSError("planted materialization failure")
    P("P10_materialize_fails_then_seal_only", None, 7, None, inj={"materializer": fail_mat}, then_seal_only=0)

    # a worker that cannot bootstrap: the pool failure propagates (decoy mode; nothing is certified). The importable
    # driver module is used, because spawned workers resolve the pool functions by module name.
    import rlr307_driver as DR
    try:
        DR.stage1("decoy", [{"sub_lo": F(1, 2), "sub_hi": F(17, 32), "hull_lo": F(1, 2), "hull_hi": F(17, 32)}], "",
                 "0" * 64, None, (F(1), F(1)), workers=1)
        res["P11_worker_bootstrap_failure"] = {"ok": False, "run": "no exception"}
    except concurrent.futures.process.BrokenProcessPool:
        res["P11_worker_bootstrap_failure"] = {"ok": True, "run": "BrokenProcessPool"}
    except Exception as exc:                                              # noqa: BLE001
        res["P11_worker_bootstrap_failure"] = {"ok": False, "run": f"{type(exc).__name__}"}

    # ---- QC07 sandbox part: arming needs the marker at HEAD = grant; nothing is certified
    D, ch = fresh()
    code = str(sb.p(NS_REL + "/code"))
    probe = ("import sys, json; sys.path.insert(0, %r); import rlr307_driver as D, rlr307_guard as G, rlr307_stage1 as S1\n"
             "hulls=[(S1.fs(b['hull_lo']), S1.fs(b['hull_hi'])) for b in S1.blocks_for(*G.CELL307)]\n"
             "extra=json.loads(sys.argv[2])\n"
             "try:\n    D._worker_init('target', sys.argv[1], sys.argv[3], hulls + extra, D.sha(D.HERE.read_bytes()))\n"
             "    print('ARMED', len(G.armed()['blocks']))\n"
             "except Exception as e:\n    print('REFUSED', type(e).__name__)\n") % code

    def arm(extra, grant):
        p = subprocess.run([PY, "-I", "-S", "-B", "-c", probe, str(sb.root), json.dumps(extra), grant],
                           capture_output=True, text=True, env=GENV, stdin=subprocess.DEVNULL)
        return p.stdout.strip() or p.stderr.strip()[-200:]

    no_marker = arm([], ch["grant"])
    g(sb.root, "update-ref", "refs/p5y-k5-cell307-rlr-r1/target-consumed", ch["grant"])
    with_marker = arm([], ch["grant"])
    outside_hull = arm([["5/2", "641/256"]], ch["grant"])
    wrong_grant = arm([], g(sb.root, "rev-parse", "HEAD^"))
    res["QC07_arming"] = {"ok": no_marker.startswith("REFUSED") and with_marker == "ARMED 10"
                          and outside_hull.startswith("REFUSED") and wrong_grant.startswith("REFUSED"),
                          "run": {"no_marker": no_marker, "with_marker": with_marker, "outside_hull": outside_hull,
                                  "marker_not_naming_grant": wrong_grant}}
    sb.reset(sb.freeze)
    restore_signals(saved)
    return {"flows": res, "n": len(res), "all_ok": all(v["ok"] for v in res.values()),
            "failed": [k for k, v in res.items() if not v["ok"]]}
