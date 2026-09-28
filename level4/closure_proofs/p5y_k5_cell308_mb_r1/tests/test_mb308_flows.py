"""QC10 (and the sandbox part of QC09): exactly-once flows of the cell-308 driver, on DECOY state only.

Every flow runs in a `git clone --shared` sandbox (own refs, index and worktree; object sharing through alternates is
read-only, so no marker, pending ref, commit or file is ever created in the real repository):
* the sandbox checks out the real HEAD with `checkout -B p5y-k5-cell308-mb-r1`; the formal namespace (as built, or as
  frozen) is copied in, its manifest is written by the sandbox's own mb308_manifest.py, and ONE sandbox commit plays
  the freeze commit (the real repository is never committed to);
* the driver is executed from the sandbox's bytes; only its four QUALIFIED_* identity constants are re-pointed;
* the controls, the consumer / science loaders, `prepare` and the evaluator are STUBS: no cell is evaluated and
  nothing is certified in the band; grant chains are synthetic sandbox commits.
"""
from __future__ import annotations

import concurrent.futures
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import time
import types
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
REPO = HERE.parents[4]
CP = "level4/closure_proofs/"
NS_REL = CP + "p5y_k5_cell308_mb_r1"
BRANCH = "p5y-k5-cell308-mb-r1"
PY = sys.executable
GENV = {"PATH": "/usr/bin:/bin", "LC_ALL": "C", "GIT_OPTIONAL_LOCKS": "0", "HOME": os.environ.get("HOME", "/var/empty")}
SIGS = (signal.SIGINT, signal.SIGTERM, signal.SIGHUP, signal.SIGQUIT, signal.SIGALRM)
COPY_DIRS = ("code", "tests", "config", "theory", "errata")


def g(root: Path, *args, check=True) -> str:
    p = subprocess.run(["/usr/bin/git", "-C", str(root), *args], capture_output=True, text=True, env=GENV,
                       stdin=subprocess.DEVNULL)
    if check and p.returncode:
        raise RuntimeError(f"git {args[:3]} failed: {p.stderr[:300]}")
    return p.stdout.strip()


class Sandbox:
    def __init__(self, tmp: Path, base: str, freeze: str | None = None):
        root = tmp / "sbx"
        subprocess.run(["/usr/bin/git", "clone", "-q", "--shared", "--no-checkout", str(REPO), str(root)], check=True,
                       env=GENV, capture_output=True)
        self.root = root.resolve()
        if g(self.root, "rev-parse", "--path-format=absolute", "--git-common-dir") == \
                g(REPO, "rev-parse", "--path-format=absolute", "--git-common-dir"):
            raise RuntimeError("the sandbox shares the real common dir")
        g(self.root, "config", "user.name", "sandbox")
        g(self.root, "config", "user.email", "sandbox@invalid")
        if freeze:                                    # a real freeze commit exists: use it as is
            g(self.root, "checkout", "-q", "-B", BRANCH, freeze)
            self.freeze = freeze
            return
        g(self.root, "checkout", "-q", "-B", BRANCH, base)
        for d in COPY_DIRS:
            src = NS / d
            if src.is_dir():
                shutil.copytree(src, self.root / NS_REL / d, ignore=shutil.ignore_patterns("__pycache__"))
        m = subprocess.run([PY, "-I", "-S", "-B", str(self.root / NS_REL / "code/mb308_manifest.py")],
                           capture_output=True, text=True, env=GENV, stdin=subprocess.DEVNULL)
        if m.returncode:
            raise RuntimeError(f"sandbox manifest failed: {m.stdout[-300:]} {m.stderr[-300:]}")
        g(self.root, "add", "-f", NS_REL)
        g(self.root, "commit", "-q", "-m", "sandbox: synthetic freeze of the formal namespace (never in the real repo)")
        self.freeze = g(self.root, "rev-parse", "HEAD")

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
            if ref.startswith("refs/p5y-k5-cell308-mb-r1/"):
                g(self.root, "update-ref", "-d", ref)
        gd = Path(g(self.root, "rev-parse", "--path-format=absolute", "--git-dir"))
        for f in gd.glob("mb308-*"):
            f.unlink()
        ev = self.p(NS_REL + "/evidence")
        if ev.is_symlink():
            ev.unlink()
        g(self.root, "checkout", "-q", "-f", BRANCH)
        g(self.root, "reset", "-q", "--hard", commit)
        g(self.root, "clean", "-qfdx", "--", NS_REL)


def build_chain(sb: Sandbox, drv_sha: str, *, review_line="QUALIFICATION_ACCEPTED", qual_pass=True, drv_override=None,
                extra_commit=False, manifest_sha=None) -> dict:
    sb.reset(sb.freeze)
    q = {"schema": "sandbox-decoy", "pass": qual_pass, "review_mode": False, "freeze_commit": sb.freeze}
    sb.write(NS_REL + "/qualification/MB308_QUALIFICATION.json", json.dumps(q))
    qc = sb.commit([NS_REL + "/qualification/MB308_QUALIFICATION.json"], "sandbox: qualification (decoy)")
    sb.write(NS_REL + "/review/MB308_QUALIFICATION_REVIEW.md", f"# sandbox review (decoy)\n{review_line}\n")
    rc = sb.commit([NS_REL + "/review/MB308_QUALIFICATION_REVIEW.md"], "sandbox: review (decoy)")
    if extra_commit:
        sb.write(NS_REL + "/review/EXTRA.md", "extra\n")
        sb.commit([NS_REL + "/review/EXTRA.md"], "sandbox: an extra commit breaking the chain")
    man = manifest_sha or hashlib.sha256(sb.p(NS_REL + "/protocol/MB308_FREEZE.json").read_bytes()).hexdigest()
    grant = {"schema": "rebaseguard.p5y.k5.cell308-mb-r1.grant.v1", "exactly_once": True, "cell": 308, "route": "MB",
             "closure_only": True, "driver_sha256": drv_override or drv_sha, "freeze_commit": sb.freeze,
             "qualification_commit": qc, "qualification_review_commit": rc, "input_manifest_sha256": man}
    sb.write(NS_REL + "/authorization/MB308_GRANT.json", json.dumps(grant))
    gc = sb.commit([NS_REL + "/authorization/MB308_GRANT.json"], "sandbox: grant (decoy)")
    return {"qual": qc, "review": rc, "grant": gc}


def load_driver(sb: Sandbox, tag: str) -> types.ModuleType:
    path = sb.p(NS_REL + "/code/mb308_driver.py")
    saved = list(sys.path)
    mod = types.ModuleType(f"mb308_driver_{tag}")
    mod.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), "exec"), mod.__dict__)
    sys.path[:] = saved
    mod.QUALIFIED_WORKTREE = str(sb.root)
    mod.QUALIFIED_GIT_DIR = str(sb.root / ".git")
    mod.QUALIFIED_COMMON_DIR = str(sb.root / ".git")
    calls = {"evaluator": 0}

    def stub_control(con, sci, k):
        return {"pass": True, "C_A": {"stub": True}, "C_B": {"stub": True},
                "_ca": {"_A": {"A0": F(1), "A1": F(1), "A2": F(1)}}, "_bundle": None}

    def stub_prepare(con, ctl, own_sha, grant, sci):
        return {"blocks": [], "pairs": [], "kappa_check": {"stub": True}}

    def stub_eval(con, prep):
        calls["evaluator"] += 1
        return {"cell": 308, "decision": {"mechanical_outcome": "STUB_DECOY"}}

    mod.load_consumer = lambda: {"stub": True}
    mod.load_science = lambda allow_uncommitted=False, with_decoy_gen=False: {"stub": True}
    mod.control = stub_control
    mod._stub = {"calls": calls, "prepare": stub_prepare, "evaluator": stub_eval}
    return mod


def restore_signals(saved: dict) -> None:
    signal.alarm(0)
    for s, h in saved.items():
        signal.signal(s, h)


def run_flows(tmp: Path, base: str | None = None, freeze: str | None = None) -> dict:  # noqa: C901
    saved = {s: signal.getsignal(s) for s in SIGS}
    tmp.mkdir(parents=True, exist_ok=True)
    sb = Sandbox(tmp, base or g(REPO, "rev-parse", "HEAD"), freeze)
    real_sha = hashlib.sha256(sb.p(NS_REL + "/code/mb308_driver.py").read_bytes()).hexdigest()
    res, n = {}, [0]

    def fresh(**kw):
        n[0] += 1
        ch = build_chain(sb, real_sha, **kw)
        return load_driver(sb, f"s{n[0]}"), ch

    def execute(D, evaluator=None, **inj):
        try:
            return {"exit": D.run_execute(real_sha, prepare=D._stub["prepare"],
                                          evaluator=evaluator or D._stub["evaluator"], **inj)}
        except D.Refusal as e:
            return {"refused": e.code}
        finally:
            restore_signals(saved)

    def marker(D):
        return g(sb.root, "rev-parse", "-q", "--verify", D.CONSUMED_REF, check=False)

    def head_raw(D) -> bytes:
        return subprocess.run(["/usr/bin/git", "-C", str(sb.root), "show", f"HEAD:{D.RESULT_REL}"], capture_output=True,
                              env=GENV).stdout

    def head_result(D):
        raw = head_raw(D)
        return json.loads(raw) if raw else None

    # ---- X: the successful flow, the rerun and seal-only
    D, ch = fresh()
    r = execute(D)
    rec = head_result(D)
    mat = sb.p(D.RESULT_REL)
    res["X01_success"] = {"ok": r == {"exit": 0} and marker(D) == ch["grant"]
                          and g(sb.root, "rev-parse", "HEAD^") == ch["grant"] and rec is not None
                          and rec["status"] == "TARGET_EVALUATED" and rec["target_evaluations"] == 1
                          and rec["mechanical_outcome"] == "STUB_DECOY" and mat.is_file() and not mat.is_symlink()
                          and mat.read_bytes() == head_raw(D) and D._stub["calls"]["evaluator"] == 1, "run": r}
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
    D.control = lambda con, sci, k: {"pass": False, "C_A": {"reproduces_C2_exactly": False},
                                     "C_B": {"reproduces_exactly": True}, "_ca": {}, "_bundle": None}
    r = execute(D)
    rec = head_result(D)
    res["C01_control_failed"] = {"ok": r == {"exit": 3} and not marker(D) and rec is not None
                                 and rec["status"] == "CONTROL_FAILED" and D._stub["calls"]["evaluator"] == 0, "run": r}
    r = execute(D)
    res["C02_rerun_after_control_failed_refused"] = {"ok": "refused" in r and D._stub["calls"]["evaluator"] == 0,
                                                     "run": r}

    # ---- T: refusals before the marker (fresh grant state each; the evaluator must never run)
    def T(name, plant, want, **chain_kw):
        D, ch = fresh(**chain_kw)
        undo = plant(D) if plant else None
        before = marker(D)
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
    T("T01_file_at_result", mk_file(exec_dir + "/MB308_CELL308_RESULT.json"), "TARGET_ARTIFACT_EXISTS")
    T("T02_directory_at_execution_dir", mk_dir(exec_dir), "RESULT_PATH_OCCUPIED")
    T("T03_symlink_out_at_tmp", mk_link(exec_dir + "/MB308_CELL308_RESULT.tmp", str(outside)), "RESULT_PATH_OCCUPIED")
    T("T04_broken_symlink_at_result", mk_link(exec_dir + "/MB308_CELL308_RESULT.json", str(tmp / "nowhere")),
      "TARGET_ARTIFACT_EXISTS")
    T("T05_fifo_at_partial", mk_fifo(exec_dir + "/MB308_CELL308_RESULT.partial"), "RESULT_PATH_OCCUPIED")
    T("T06_ignored_tmp_file", mk_file(exec_dir + "/MB308_CELL308_RESULT.json.tmp"), "RESULT_PATH_OCCUPIED")

    def evidence_link(D):
        ev = sb.p(NS_REL + "/evidence")
        real = sb.p(NS_REL + "/evidence_real")
        real.mkdir(parents=True, exist_ok=True)
        os.symlink(str(real), str(ev))

        def undo():
            ev.unlink()
            shutil.rmtree(real)
        return undo
    T("T07_symlinked_evidence_dir", evidence_link, "RESULT_PATH_OCCUPIED")

    def dirty(D):
        p = sb.p(NS_REL + "/code/mb308_manifest.py")
        p.write_text(p.read_text() + "\n# planted\n")
    T("T08_dirty_tree", dirty, "DIRTY_TREE")
    T("T09_ignored_object_in_namespace", mk_file(NS_REL + "/code/planted.log"), "IGNORED_OBJECT")
    T("T09b_pycache_in_namespace", mk_file(NS_REL + "/code/__pycache__/x.cpython-314.pyc"), "IGNORED_OBJECT")
    T("T10_prior_marker_ref", lambda D: g(sb.root, "update-ref", D.CONSUMED_REF, g(sb.root, "rev-parse", "HEAD")),
      "CONSUMED")
    T("T11_pending_ref", lambda D: g(sb.root, "update-ref", D.PENDING_REF, g(sb.root, "rev-parse", "HEAD")), "CONSUMED")

    def emergency(D):
        gd = Path(g(sb.root, "rev-parse", "--path-format=absolute", "--git-dir"))
        (gd / D.EMERGENCY_NAME).write_text("{}\n")
    T("T13_emergency_file", emergency, "TARGET_ARTIFACT_EXISTS")
    T("T14_wrong_branch", lambda D: g(sb.root, "checkout", "-q", "-b", "other-branch"), "WRONG_BRANCH")
    T("T16_no_grant", lambda D: g(sb.root, "reset", "-q", "--hard", "HEAD^"), "GRANT_MISSING")
    T("T17_grant_wrong_driver_sha", None, "GRANT_INVALID", drv_override="0" * 64)
    T("T18_broken_chain", None, "GRANT_INVALID", extra_commit=True)
    T("T19_review_rejected", None, "REVIEW_VERDICT", review_line="QUALIFICATION_REJECTED")
    T("T20_qualification_not_pass", None, "GRANT_INVALID", qual_pass=False)
    T("T21_grant_wrong_manifest", None, "GRANT_INVALID", manifest_sha="1" * 64)

    # function-level tamper tests (each file restored afterwards)
    D, ch = fresh()
    tampers = {}

    def tamper(label, rel, fn):
        p = sb.p(rel)
        orig = p.read_bytes()
        p.write_bytes(orig + b"# planted\n")
        try:
            fn()
            tampers[label] = "NOT_REFUSED"
        except D.Refusal as e:
            tampers[label] = e.code
        except D.PIN.PinError:
            tampers[label] = "PinError"
        finally:
            p.write_bytes(orig)
    tamper("registry_c2", D.CON.PINS["registry_c2"][0], D.check_bindings)
    tamper("helper", NS_REL + "/code/mb308_stage1.py", D.check_helpers)
    tamper("certifier", D.PIN.PINS["c1b_pw"][0], lambda: D.PIN.verified_bytes(sb.root, D.PIN.PINS["c1b_pw"]))
    tamper("verifier", D.PIN.PINS["vd_verify"][0], D.check_bindings)
    tamper("f2", D.PIN.INDEP_PIN[0], D.check_bindings)
    ip = sb.p(D.PIN.INDEP_PIN[0])
    ib = ip.read_bytes()
    ip.unlink()
    try:
        D.check_bindings()
        tampers["f2_removed"] = "NOT_REFUSED"
    except D.Refusal as e:
        tampers["f2_removed"] = e.code
    finally:
        ip.write_bytes(ib)
    res["T22_tampered_inputs"] = {"ok": tampers == {"registry_c2": "PIN_MISMATCH", "helper": "HELPER_PIN_MISMATCH",
                                                    "certifier": "PinError", "verifier": "PIN_MISMATCH",
                                                    "f2": "PIN_MISMATCH", "f2_removed": "F2_MISSING"}, "run": tampers}

    # CLI: interpreter flags, identity, dev flags (the real CLI never runs in a non-qualified worktree)
    drv = str(sb.p(NS_REL + "/code/mb308_driver.py"))

    def cli(*args):
        p = subprocess.run([PY, *args], capture_output=True, text=True, env=GENV, stdin=subprocess.DEVNULL)
        return p.returncode, p.stdout.strip()[-120:]
    a, b, c = cli(drv, "execute"), cli("-I", "-S", "-B", drv, "execute"), cli("-I", "-S", "-B", drv, "execute",
                                                                              "--dev-ladder")
    res["T15_cli_flags_identity_devflags"] = {"ok": a[0] == 2 and "INTERPRETER_FLAGS" in a[1] and b[0] == 2
                                              and "REPO_NOT_QUALIFIED" in b[1] and c[0] == 2
                                              and "DEV_FLAG_REFUSED" in c[1], "run": [a, b, c]}

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
            ok = ok and rec is not None and rec.get("status") == want_status and \
                rec.get("mechanical_outcome") == "CELL308_EXECUTION_INDETERMINATE"
        if then_seal_only is not None:
            try:
                so = D.run_seal_only()
            except D.Refusal as e:
                so = f"refused {e.code}"
            finally:
                restore_signals(saved)
            out["seal_only"] = so
            ok = ok and so == then_seal_only and head_result(D) is not None
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
    P("P02b_inconsistent", None, 5, "INCONSISTENT",
      patch=lambda D: D._stub.__setitem__("evaluator", counting(boom(D.Inconsistent("planted")))))
    P("P02c_c6_refusal", None, 5, "C6_REFUSED",
      patch=lambda D: D._stub.__setitem__("evaluator", counting(boom(D.CON.Stop("C6_EMPTY_BAND", "planted")))))
    P("P03_system_exit", counting(boom(SystemExit(9))), 5, "TARGET_EVALUATION_FAILED")
    P("P04_keyboard_interrupt", counting(boom(KeyboardInterrupt())), 5, "TARGET_EVALUATION_FAILED")

    def slow():
        time.sleep(3)
        return {"decision": {}}
    P("P05_evaluation_cap", counting(slow), 5, "TARGET_EVALUATION_FAILED", patch=lambda D: setattr(D, "EVAL_CAP_S", 1))
    P("P06_serialization_failure", counting(lambda: {"x": {1, 2}}), 5, "POST_MARKER_RECORDING_FAILED")

    def fail_persist(data):
        raise OSError("planted primary persistence failure")
    P("P07_primary_persistence_fails_emergency_then_seal_only", None, 4, None, inj={"persist": fail_persist},
      then_seal_only=0)
    P("P08_both_channels_fail", None, 6, None, inj={"persist": fail_persist},
      patch=lambda D: setattr(D, "persist_emergency", boom(OSError("planted second channel failure"))))

    def fail_seal(blob, msg):
        raise OSError("planted seal failure")
    P("P09_seal_fails_then_seal_only", None, 4, None, inj={"sealer": fail_seal}, then_seal_only=0)

    def fail_mat(blob):
        raise OSError("planted materialization failure")
    P("P10_materialize_fails_then_seal_only", None, 7, None, inj={"materializer": fail_mat}, then_seal_only=0)

    # a worker that cannot bootstrap (wrong driver sha): the pool failure propagates (decoy mode; nothing certified)
    import mb308_driver as DR
    blk = {"index": 0, "tile": (F(1, 2), F(17, 32)), "hull": (F(1, 2), F(17, 32)), "b": F(1, 2)}
    try:
        DR.stage1("decoy", [blk], "", "0" * 64, None, {"RLR": (4,), "C2B": (), "C1B": ()}, [], workers=1)
        res["P11_worker_bootstrap_failure"] = {"ok": False, "run": "no exception"}
    except concurrent.futures.process.BrokenProcessPool:
        res["P11_worker_bootstrap_failure"] = {"ok": True, "run": "BrokenProcessPool"}
    except Exception as exc:                                              # noqa: BLE001
        res["P11_worker_bootstrap_failure"] = {"ok": False, "run": f"{type(exc).__name__}: {exc}"[:200]}

    # ---- QC09 sandbox part: arming needs the marker at HEAD = grant and EXACTLY the frozen set; nothing certified
    D, ch = fresh()
    code = str(sb.p(NS_REL + "/code"))
    probe = ("import sys, json; sys.path.insert(0, %r); import mb308_driver as D, mb308_guard as G\n"
             "from fractions import Fraction as F\n"
             "pairs=[(str(a), str(b)) for a, b in sorted(G.target_admitted_set())]\n"
             "mut=json.loads(sys.argv[2])\n"
             "if mut == 'drop': pairs = pairs[1:]\n"
             "if mut == 'extra': pairs = pairs + [('5/2', '641/256')]\n"
             "try:\n    D._worker_init('target', sys.argv[1], sys.argv[3], pairs, D.sha(D.HERE.read_bytes()), 'x', False)\n"
             "except Exception as e:\n    print('REFUSED', type(e).__name__); sys.exit(0)\n"
             "t = G.geometry(*G.CELL308)[0]['tile']\n"
             "def ok(f, *a):\n    try:\n        f(*a); return True\n    except G.QuarantineRefusal:\n        return False\n"
             "chk = [ok(G.guard_drift, *t), ok(G.guard_cell, 'CUSUM', 5, 308), not ok(G.guard_cell, 'CUSUM', 5, 305),\n"
             "       not ok(G.guard_drift, F(5, 2), F(641, 256)), not ok(G.guard_drift, t[0], t[1] + F(1, 10**9))]\n"
             "print('ARMED', len(G.armed()['pairs']), all(chk))\n") % code

    def arm(mut, grant):
        p = subprocess.run([PY, "-I", "-S", "-B", "-c", probe, str(sb.root), json.dumps(mut), grant],
                           capture_output=True, text=True, env=GENV, stdin=subprocess.DEVNULL)
        return p.stdout.strip() or p.stderr.strip()[-200:]

    no_marker = arm("none", ch["grant"])
    g(sb.root, "update-ref", "refs/p5y-k5-cell308-mb-r1/target-consumed", ch["grant"])
    with_marker = arm("none", ch["grant"])
    dropped = arm("drop", ch["grant"])
    extra = arm("extra", ch["grant"])
    wrong_grant = arm("none", g(sb.root, "rev-parse", "HEAD^"))
    res["QC09_arming"] = {"ok": no_marker.startswith("REFUSED") and with_marker == "ARMED 37 True"
                          and dropped.startswith("REFUSED") and extra.startswith("REFUSED")
                          and wrong_grant.startswith("REFUSED"),
                          "run": {"no_marker": no_marker, "with_marker": with_marker, "drop_one_pair": dropped,
                                  "extra_band_pair": extra, "marker_not_naming_grant": wrong_grant}}
    sb.reset(sb.freeze)
    restore_signals(saved)
    return {"flows": res, "n": len(res), "all_ok": all(v["ok"] for v in res.values()),
            "failed": [k for k, v in res.items() if not v["ok"]], "sandbox": str(sb.root), "freeze": sb.freeze}
