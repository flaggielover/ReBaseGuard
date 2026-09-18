"""r4 governed-launch qualification (EXECUTOR_SPEC_R4.md R4-4). NON-SCIENTIFIC; SYNTHETIC GOVERNANCE ONLY.

    governed_part(proto)   control + mutants N01-N05, each in its own private mount namespace
    python -B code/qualify_governed.py driver --src-repo R --out F [--mutation JSON]     (inside the namespace)

The driver builds a SYNTHETIC full clone S of the repository under test and commits, in S only (never pushed), a
SYNTHETIC review, an amendment binding S's executor bytes and the frozen adapter pins, AUTHORIZATION_ACTIVE.json,
a countersignature, the guard policy EXTERNAL_AUTHORIZATION and a ledger LAUNCH_NOTICE, in the order the preregistration
fixes. The UNMODIFIED frozen verifier (S's byte-identical copy) then runs with its defaults through S's own supervisor.

Two hermetic test doubles, nothing else:
  * the verifier's network read `git ls-remote origin` (GitHub publication anchor) is answered from a local synthetic
    bare repository by a `git` shim on PATH; the origin URL stays the allow-listed GitHub URL;
  * the preregistered output namespace /root/work/k5-first-real-probe is virtual: the scenario runs in a private mount
    namespace with a copy-on-write overlay over /root/work, so the real namespace is never created.
Manufactured input only (governed_manufactured); no real K1 arithmetic anywhere.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

import paths

NS = paths.NS
REPO = paths.REPO
REL_NS = str(NS.relative_to(REPO))
REL_PROTO = "level4/closure_proofs/p5y_k5_cusum_first_real_probe_protocol"
GITHUB = "https://github.com/flaggielover/ReBaseGuard.git"
ADAPTER_PINS = {"level4/closure_proofs/p5y_k5_order3_readiness_audit/code/k5_minimality.py",
                "level4/closure_proofs/p5y_k5b_independent_countersignature/code/k5b_check.py"}
QUAL_EVIDENCE = "level4/closure_proofs/p5y_k5_cusum_order3_r4_tightening/evidence/qualification_r4/QUALIFICATION_RESULT_R4.json"
POSITIVE_FIXTURE, CHILD_FIXTURE = "XF01_positive_L1", "XF03_negative_U1"
# disk-backed scratch OUTSIDE /root/work (the overlay target) and outside the RAM-backed /tmp; removed after every driver
SCRATCH = Path("/var/tmp/k5gov")
SHIM = """#!{py}
# SYNTHETIC QUALIFICATION TEST DOUBLE: answers the frozen verifier's network publication read `git ls-remote origin`
# from a local synthetic bare repository; every other git invocation is the real git, unchanged.
import os, sys
REAL = "/usr/bin/git"
args = sys.argv[1:]
if "ls-remote" in args:
    i = args.index("ls-remote")
    if i + 1 < len(args) and args[i + 1] == "origin":
        args[i + 1] = os.environ["K5_SYNTHETIC_ORIGIN"]
os.execv(REAL, [REAL] + args)
"""


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _row(ok, **detail):
    return {"pass": bool(ok), **detail}


# ================================================================== driver (inside the private mount namespace)
class Synthetic:
    def __init__(self, src_repo: Path, mutation: dict | None, work: Path):
        self.base = work / "synthetic"
        self.base.mkdir()
        self.S = self.base / "repo"
        self.origin = self.base / "origin.git"
        self.shim = self.base / "shim"
        self.env = dict(os.environ, PATH=f"{self.shim}:{os.environ.get('PATH', '/usr/bin:/bin')}",
                        K5_SYNTHETIC_ORIGIN=str(self.origin), GIT_AUTHOR_NAME="synthetic-qualification",
                        GIT_AUTHOR_EMAIL="synthetic@qualification.invalid", GIT_COMMITTER_NAME="synthetic-qualification",
                        GIT_COMMITTER_EMAIL="synthetic@qualification.invalid", OMP_NUM_THREADS="1",
                        OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", NUMEXPR_NUM_THREADS="1", PYTHONHASHSEED="0")
        self.shim.mkdir()
        (self.shim / "git").write_text(SHIM.format(py=sys.executable))
        (self.shim / "git").chmod(0o755)
        head = subprocess.run(["git", "-C", str(src_repo), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        self.run("git", "clone", "-q", "--shared", "--no-checkout", str(src_repo), str(self.S), cwd=self.base)
        self.g("checkout", "-q", "--detach", head)
        # the executor tree under test (identical for a frozen checkout; the DEV working tree otherwise)
        subprocess.run(["rsync", "-a", "--delete", "--exclude", "__pycache__", "--exclude", "evidence", f"{NS}/",
                        f"{self.S / REL_NS}/"], check=True)
        if mutation:
            f = self.S / REL_NS / "code" / mutation["file"]
            src = f.read_text()
            if src.count(mutation["old"]) != 1:
                raise ValueError(f"anchor {mutation['id']}")
            f.write_text(src.replace(mutation["old"], mutation["new"]))
        self.run(sys.executable, "-B", str(self.S / REL_NS / "code/make_protocol_executor.py"), "--dev",
                 str(self.base / "dev_protocol.json"), cwd=self.S)                       # pins of the tree under test
        guard = self.S / REL_NS / "config/REAL_INPUT_GUARD.json"
        g = json.loads(guard.read_text())
        g["policy"] = "EXTERNAL_AUTHORIZATION"
        guard.write_text(json.dumps(g, indent=1, sort_keys=True) + "\n")
        self.commit("SYNTHETIC QUALIFICATION: executor tree under test and guard policy EXTERNAL_AUTHORIZATION")

    def run(self, *cmd, cwd=None, check=True):
        r = subprocess.run(list(cmd), cwd=str(cwd or self.S), env=self.env, capture_output=True, text=True)
        if check and r.returncode != 0:
            raise RuntimeError(f"{cmd[:3]} rc={r.returncode}: {r.stderr[-400:]}")
        return r

    def g(self, *args):
        return self.run("git", "-C", str(self.S), *args).stdout.strip()

    def commit(self, message: str) -> str:
        self.g("add", "-A")
        self.g("commit", "-q", "--allow-empty", "-m", message)
        return self.g("rev-parse", "HEAD")

    def publish(self):
        if not self.origin.exists():
            self.run("git", "init", "-q", "--bare", str(self.origin), cwd=self.base)
        self.g("push", "-q", "--force", str(self.origin), "HEAD:refs/heads/p5y-postk1-frontier")
        self.g("remote", "set-url", "origin", GITHUB)
        self.g("update-ref", "refs/remotes/origin/p5y-postk1-frontier", "HEAD")

    def file_sha(self, rel: str) -> str:
        return sha((self.S / rel).read_bytes())

    def governance_until_amendment(self):
        sys.path.insert(0, str(self.S / REL_NS / "code"))
        import authorization_interface as AI
        import probe_rules as PR
        srcs = {f"{REL_NS}/{f}": h for f, h in AI.executor_identity()["files"].items()}
        for rel in ADAPTER_PINS:
            srcs[rel] = self.file_sha(rel)
        review = f"{REL_NS}/review/SYNTHETIC_QUALIFICATION_REVIEW.md"
        (self.S / review).write_text(
            "# SYNTHETIC QUALIFICATION FIXTURE - NOT A REVIEW\n\nThis file exists only inside a throwaway synthetic clone "
            "built by code/qualify_governed.py and is never published.\n\n"
            f"REVIEW_VERDICT: PASS_WITH_SCOPE_LIMITATION\nREVIEWED_AMENDMENT_SOURCES_SHA256: {sha(PR.canonical(srcs))}\n")
        self.commit("SYNTHETIC QUALIFICATION: review fixture")
        time.sleep(1.1)
        amendment = {"schema": "rebaseguard.p5y.k5.cusum-first-real-probe.execution-binding-amendment.v1",
                     "status": "BOUND_QUALIFIED",
                     "science_preregistration_sha256": self.file_sha(f"{REL_PROTO}/protocol/SCIENCE_PREREGISTRATION_R4.json"),
                     "executor_entry": f"{REL_NS}/code/executor_cli.py",
                     "consumption_adapter_entry": "level4/closure_proofs/p5y_k5b_independent_countersignature/code/k5b_check.py",
                     "executor_sources_sha256": srcs, "qualification_evidence_sha256": {QUAL_EVIDENCE: self.file_sha(QUAL_EVIDENCE)},
                     "independent_review": review, "independent_review_sha256": self.file_sha(review),
                     "independent_review_verdict": "PASS_WITH_SCOPE_LIMITATION",
                     "amendment_rule_ack": "SYNTHETIC QUALIFICATION FIXTURE (never published)"}
        (self.S / REL_PROTO / "protocol/EXECUTION_BINDING_AMENDMENT.json").write_text(json.dumps(amendment, indent=1) + "\n")
        self.commit("SYNTHETIC QUALIFICATION: execution binding amendment")
        self.publish()

    def authorization(self):
        time.sleep(1.1)
        tmpl = json.loads((self.S / REL_PROTO / "protocol/AUTHORIZATION_TEMPLATE_R4.json").read_text())
        freeze = self.g("log", "--diff-filter=A", "--format=%H", "--", f"{REL_PROTO}/protocol/SCIENCE_PREREGISTRATION_R4.json")
        auth = json.loads(json.dumps(tmpl))
        auth.update({"EXECUTION_AUTHORIZED": True, "PROTOCOL_FREEZE_COMMIT": freeze,
                     "AUTHORIZED_BY": "SYNTHETIC QUALIFICATION FIXTURE (never published)",
                     "AUTHORIZATION_UTC": datetime.now(timezone.utc).isoformat()})
        auth["PRODUCER_R4_IDENTITY"]["executor_binding_sha256"] = self.file_sha(f"{REL_PROTO}/protocol/EXECUTION_BINDING_AMENDMENT.json")
        (self.S / REL_PROTO / "protocol/AUTHORIZATION_ACTIVE.json").write_text(json.dumps(auth, indent=1) + "\n")
        self.commit("SYNTHETIC QUALIFICATION: authorization fixture")
        time.sleep(1.1)
        tmplc = json.loads((self.S / REL_NS / "config/EXTERNAL_AUTHORIZATION_TEMPLATE.json").read_text())
        cs = dict(tmplc, status="COUNTERSIGNED", EXECUTION_AUTHORIZED=True,
                  protocol_authorization_sha256=self.file_sha(f"{REL_PROTO}/protocol/AUTHORIZATION_ACTIVE.json"),
                  execution_binding_amendment_sha256=self.file_sha(f"{REL_PROTO}/protocol/EXECUTION_BINDING_AMENDMENT.json"),
                  attempt_slot=1, nonce="5a" * 16,
                  countersigner={"identity": "SYNTHETIC QUALIFICATION FIXTURE", "independent_of_execution_host": True,
                                 "verified_from": "synthetic", "utc": time.time() - 1})
        (self.S / REL_NS / "authorization").mkdir(exist_ok=True)
        (self.S / REL_NS / "authorization/COUNTERSIGNATURE_ACTIVE.json").write_text(json.dumps(cs, indent=1) + "\n")
        self.commit("SYNTHETIC QUALIFICATION: countersignature fixture")
        self.publish()

    def launch_notice(self):
        led = self.S / REL_PROTO / "ledger/ATTEMPT_LEDGER.jsonl"
        led.parent.mkdir(exist_ok=True)
        entry = {"event": "LAUNCH_NOTICE", "slot": "slot-1",
                 "authorization_sha256": self.file_sha(f"{REL_PROTO}/protocol/AUTHORIZATION_ACTIVE.json"),
                 "utc": datetime.now(timezone.utc).isoformat()}
        with open(led, "a") as fh:
            fh.write(json.dumps(entry, sort_keys=True) + "\n")
        self.commit("SYNTHETIC QUALIFICATION: ledger LAUNCH_NOTICE slot-1")
        self.publish()

    def supervisor(self, slot: int, fixture=POSITIVE_FIXTURE):
        ns_root = "/root/work/k5-first-real-probe"
        r = self.run(sys.executable, "-B", str(self.S / REL_NS / "code/supervisor.py"), "launch", "--namespace", ns_root,
                     "--slot", str(slot), "--mode", "governed_manufactured", "--fixture-id", fixture, check=False,
                     cwd=self.S / REL_NS)
        try:
            out = json.loads(r.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            out = {"unparsed": r.stdout[-300:], "stderr": r.stderr[-600:]}
        return r.returncode, out

    def child(self, mode, slot_dir: Path, uid, digest, fixture=CHILD_FIXTURE):
        cmd = [sys.executable, "-B", str(self.S / REL_NS / "code/executor_cli.py"), mode, "--output-dir", str(slot_dir),
               "--attempt-uid", uid]
        if digest:
            cmd += ["--decision-sha256", digest]
        if mode != "real":
            cmd += ["--fixture-id", fixture]
        r = subprocess.run(cmd, cwd=str(self.S / REL_NS), env=self.env, capture_output=True, text=True)
        line = next((l for l in r.stderr.splitlines() if l.startswith("EXECUTOR_REFUSAL:")), r.stderr[-300:])
        return r.returncode, line


def _own_cmdline():
    return [a.decode(errors="replace") for a in Path("/proc/self/cmdline").read_bytes().split(b"\0") if a]


def scenario(syn: Synthetic) -> dict:
    rows = {}
    ns_root = Path("/root/work/k5-first-real-probe")
    slot1 = ns_root / "slot-1"
    syn.governance_until_amendment()
    # 1. verifier exception (no AUTHORIZATION_ACTIVE.json yet) -> PRELAUNCH_REFUSED, nothing created
    rc, out = syn.supervisor(1)
    rows["verifier_exception_creates_no_slot"] = _row(
        rc == 3 and out.get("prelaunch") == "PRELAUNCH_REFUSED" and any("verifier raised" in p for p in out.get("problems", []))
        and not slot1.exists() and not ns_root.exists(), got=out)
    # 2. verifier REFUSED (authorized, but no LAUNCH_NOTICE: P11) -> PRELAUNCH_REFUSED, nothing created
    syn.authorization()
    rc, out = syn.supervisor(1)
    rows["verifier_refused_creates_no_slot"] = _row(
        rc == 3 and out.get("prelaunch") == "PRELAUNCH_REFUSED" and any("verifier verdict" in p for p in out.get("problems", []))
        and not slot1.exists() and not ns_root.exists(), got=out)
    # 3. the permitted governed launch, end to end
    syn.launch_notice()
    rc, out = syn.supervisor(1)
    files = sorted(p.name for p in slot1.iterdir()) if slot1.exists() else []
    state = json.loads((slot1 / "RUN_STATE.json").read_text()) if (slot1 / "RUN_STATE.json").exists() else {}
    dec = state.get("prelaunch_decision") or {}
    rep = dec.get("prelaunch_report") or {}
    events = [json.loads(l)["event"] for l in (slot1 / "ATTEMPT_LOG.jsonl").read_text().splitlines()] \
        if (slot1 / "ATTEMPT_LOG.jsonl").exists() else []
    rows["permitted_synthetic_end_to_end"] = _row(
        rc == 0 and out.get("terminal") == "RUN_COMPLETE.json"
        and files == ["ATTEMPT_LOG.jsonl", "MANUFACTURED_RECORD_SEALED.json", "RUN_COMPLETE.json", "RUN_STATE.json"]
        and events == ["VALIDATED", "ARITHMETIC_STARTED", "SEALED"]
        and rep.get("verdict") == "LAUNCH_PERMITTED" and rep.get("failing_checks") == []
        and all(c.get("pass") is True for c in (rep.get("checks") or {}).values()) and len(rep.get("checks") or {}) == 12
        and state.get("prelaunch_decision_sha256") == sha(json.dumps(dec, sort_keys=True, separators=(",", ":"),
                                                                     ensure_ascii=True).encode()),
        got=out, files=files, events=events, primary=rep.get("primary_reason"))
    # the executor child's own gate evidence shows the bound decision was re-checked (governed harness analogue)
    try:
        rec = json.loads((slot1 / "MANUFACTURED_RECORD_SEALED.json").read_text())
        guard = rec["scientific"]["guard"]
        rows["child_rechecked_bound_decision"] = _row(
            guard["policy"] == "EXTERNAL_AUTHORIZATION" and guard["real_arithmetic_permitted"] is True
            and guard["binding"]["prelaunch_decision_sha256"] == state["prelaunch_decision_sha256"]
            and rec["scientific"]["producer_qualification"]["gates"]["Q01_PRELAUNCH_VERIFIED"] is True)
    except Exception as exc:
        rows["child_rechecked_bound_decision"] = _row(False, error=f"{type(exc).__name__}")
    # ledger reconciliation of the permitted attempt
    sys.path.insert(0, str(syn.S / REL_NS / "code"))
    import lifecycle as LC
    try:
        notice = [json.loads(l) for l in (syn.S / REL_PROTO / "ledger/ATTEMPT_LEDGER.jsonl").read_text().splitlines()]
        led = notice + [LC.outcome_entry(slot1), {"event": "SCIENTIFIC_RECORD_SEALED", "slot": "slot-1",
                                                  "sha256": sha((slot1 / "MANUFACTURED_RECORD_SEALED.json").read_bytes())}]
        rows["ledger_reconciles_permitted_attempt"] = _row(LC.reconcile(slot1, led) == [])
    except Exception as exc:
        rows["ledger_reconciles_permitted_attempt"] = _row(False, error=f"{type(exc).__name__}: {str(exc)[:120]}")

    # 4. the child's pure re-check: a coherent crafted binding runs; each single inconsistency refuses before arithmetic
    import executor_core as EC
    import input_adapters as IA
    import supervisor as SV
    spec = SV.fixture_spec(CHILD_FIXTURE)
    binding = IA.ManufacturedInputAdapter().bind(spec)

    def crafted(n: int, **over):
        slot = ns_root / f"slot-{n}"
        d = json.loads(json.dumps(dec))
        d["slot"] = slot.name
        ctx = EC.standard_context(binding, slot)
        d["attempt"] = {"k1_record_sha256": binding["record_sha256"], "binding_kind": "manufactured", "right": binding["right"],
                        "m_set": list(ctx.m_set), "point_e": ctx.point_e, "theorem_cell": ctx.theorem_cell,
                        "precision_bits": ctx.precision_bits}
        uid = f"crafted-{n}"
        st = LC.build_run_state(pid=os.getpid(), argv=_own_cmdline(), boot=LC.boot_id(), start_epoch=time.time(),
                                authorization_sha256=d["authorization_sha256"], slot=slot.name, attempt_uid=uid,
                                protocol_sha256=state.get("protocol_sha256"), executor_identity_sha256=dec.get("executor_identity_sha256"),
                                mode="manufactured", prelaunch_decision=d)
        st.update(over.get("state", {}))
        slot.mkdir(parents=True)
        if not over.get("no_run_state"):
            LC.write_new(slot, LC.RUN_STATE, st)
        return slot, uid, st["prelaunch_decision_sha256"]

    def no_arith(slot: Path) -> bool:
        log = slot / "ATTEMPT_LOG.jsonl"
        return not (log.exists() and "ARITHMETIC_STARTED" in log.read_text()) and \
            not any((slot / n).exists() for n in LC.ALL_SEALS)

    def refused_by_guard(rc, err, needle, slot: Path | None) -> bool:
        """Refused BEFORE arithmetic, and by the guard's pure re-check for the stated reason (not by any later check)."""
        return rc == 3 and "UNAUTHORIZED_REAL_ARITHMETIC" in err and needle in err and (slot is None or no_arith(slot))

    child_rows = ("child_changed_decision_digest_refused", "child_changed_attempt_uid_refused",
                  "child_missing_run_state_refused", "child_stale_run_state_refused", "child_wrong_supervisor_pid_refused",
                  "child_wrong_supervisor_argv_refused", "unsupervised_real_mode_refused",
                  "unsupervised_governed_mode_refused", "child_coherent_binding_runs")
    if not dec:
        rows.update({k: _row(False, error="no permitted decision to derive crafted bindings from") for k in child_rows})
    else:
        # negatives FIRST (before any crafted attempt seals this fixture's addresses), each refused by the guard itself
        s, u, dg = crafted(3)
        rc, err = syn.child("governed_manufactured", s, u, "0" * 64)
        rows["child_changed_decision_digest_refused"] = _row(refused_by_guard(rc, err, "digest differs", s), err=err)
        s, u, dg = crafted(4)
        rc, err = syn.child("governed_manufactured", s, "another-attempt", dg)
        rows["child_changed_attempt_uid_refused"] = _row(refused_by_guard(rc, err, "another attempt", s), err=err)
        s, u, dg = crafted(5, no_run_state=True)
        rc, err = syn.child("governed_manufactured", s, u, dg)
        rows["child_missing_run_state_refused"] = _row(refused_by_guard(rc, err, "RUN_STATE missing", s), err=err)
        s = ns_root / "slot-6"
        s.mkdir()
        shutil.copy(slot1 / "RUN_STATE.json", s / "RUN_STATE.json")
        rc, err = syn.child("governed_manufactured", s, state.get("attempt_uid"), state.get("prelaunch_decision_sha256"))
        rows["child_stale_run_state_refused"] = _row(refused_by_guard(rc, err, "supervisor identity", s), err=err)
        s, u, dg = crafted(7, state={"pid": 1})
        rc, err = syn.child("governed_manufactured", s, u, dg)
        rows["child_wrong_supervisor_pid_refused"] = _row(refused_by_guard(rc, err, "supervisor identity", s), err=err)
        s, u, dg = crafted(8, state={"argv": ["/not/the/supervisor"]})
        rc, err = syn.child("governed_manufactured", s, u, dg)
        rows["child_wrong_supervisor_argv_refused"] = _row(refused_by_guard(rc, err, "supervisor identity", s), err=err)
        missing = ns_root / "slot-9"
        rc, err = syn.child("real", missing, "unsupervised", "0" * 64)
        rows["unsupervised_real_mode_refused"] = _row(refused_by_guard(rc, err, "no supervised slot", None)
                                                      and not missing.exists(), err=err)
        rc, err = syn.child("governed_manufactured", missing, "unsupervised", "0" * 64)
        rows["unsupervised_governed_mode_refused"] = _row(refused_by_guard(rc, err, "no supervised slot", None)
                                                          and not missing.exists(), err=err)
        # the coherent crafted binding LAST: accepted by the same pure re-check and runs to a seal
        s, u, dg = crafted(2)
        rc, err = syn.child("governed_manufactured", s, u, dg)
        rows["child_coherent_binding_runs"] = _row(rc == 0 and (s / "MANUFACTURED_RECORD_SEALED.json").exists(), err=err)

    # 5. unit layers (each defence checked on its own)
    rows["slot_admission_requires_supervisor"] = _row(
        bool(EC.slot_admission(ns_root / "slot-missing", "u", require_supervisor=True))
        and EC.slot_admission(ns_root / "slot-missing", None, require_supervisor=False) == [])
    import ast
    code = syn.S / REL_NS / "code"
    refs = {}
    for f in ("executor_core.py", "backends.py", "executor_cli.py", "input_adapters.py"):
        t = ast.unparse(ast.parse((code / f).read_text()))
        refs[f] = [x for x in ("prelaunch_decision(", "AI.validate(", "validate_with(", "run_verifier(", "PV.verify(",
                  "prelaunch_verify.verify(")
                   if x in t]
    sup = ast.unparse(ast.parse((code / "supervisor.py").read_text()))
    rows["static_single_verifier_call_site"] = _row(all(v == [] for v in refs.values())
                                                    and sup.count("AI.prelaunch_decision(ctx)") == 1, refs=refs)
    # 6. post-start fence (LAST: it latches this process)
    import authorization_interface as AI
    ctx = EC.standard_context(binding, ns_root / "slot-10")
    EC._mark_arithmetic_started()
    try:
        AI.validate(ctx)
        fenced = False
    except AI.PostStartVerifierCall:
        fenced = True
    try:
        d = EC.decide("EXTERNAL_AUTHORIZATION", ctx)
        pure_after_start = d["real_arithmetic_permitted"] is False
    except BaseException:
        pure_after_start = False
    rows["post_start_full_verifier_unreachable"] = _row(fenced and pure_after_start
                                                        and EC.void_class(AI.PostStartVerifierCall("x")) is None)
    return rows


def driver(args):
    out, work = Path(args.out), Path(args.work)
    syn = None
    try:
        (work / "u").mkdir()
        (work / "w").mkdir()
        subprocess.run(["mount", "-t", "overlay", "overlay", "-o",
                        f"lowerdir=/root/work,upperdir={work / 'u'},workdir={work / 'w'}", "/root/work"], check=True)
        if Path("/root/work/k5-first-real-probe").exists():
            raise RuntimeError("the preregistered namespace exists on the host; refusing to qualify")
        mutation = json.loads(args.mutation) if args.mutation else None
        syn = Synthetic(Path(args.src_repo), mutation, work)
        rows = scenario(syn)
        out.write_text(json.dumps({"rows": rows}, indent=1, sort_keys=True, default=str))
    except BaseException:
        out.write_text(json.dumps({"error": traceback.format_exc()[-3000:]}, indent=1))
    finally:
        if syn is not None:
            shutil.rmtree(syn.base, ignore_errors=True)


# ================================================================== part (outside the namespace)
def run_driver(mutation: dict | None) -> dict:
    """One scenario in its own private mount namespace; its overlay upper and synthetic clone are removed afterwards
    (the namespace, and with it the overlay mount, ends when the driver exits)."""
    SCRATCH.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="run-", dir=SCRATCH))
    out = work / "result.json"
    cmd = ["unshare", "--mount", "--propagation", "private", "--", sys.executable, "-B", str(Path(__file__).resolve()),
           "driver", "--src-repo", str(REPO), "--out", str(out), "--work", str(work)]
    if mutation:
        cmd += ["--mutation", json.dumps(mutation)]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=5400, cwd=str(NS))
        if not out.exists() or not out.read_text().strip():
            return {"error": f"driver produced no result rc={p.returncode}: {p.stderr[-600:]}"}
        return json.loads(out.read_text())
    finally:
        shutil.rmtree(work, ignore_errors=True)


def governed_part(proto) -> dict:
    control = run_driver(None)
    rows = control.get("rows", {})
    control_ok = "error" not in control and bool(rows) and all(v["pass"] for v in rows.values())
    muts = {}
    for mut in proto["governed_mutations"]:
        r = run_driver(mut)
        if "error" in r:
            muts[mut["id"]] = {"detected": False, "crashed": r["error"][-400:]}
        else:
            failing = [k for k, v in r["rows"].items() if not v["pass"]]
            muts[mut["id"]] = {"detected": bool(failing), "failing": failing[:6]}
    real_ns_untouched = not Path("/root/work/k5-first-real-probe").exists()
    return {"control": control, "rows": rows, "control_pass": control_ok, "mutations": muts,
            "mutations_count": f"{sum(v['detected'] for v in muts.values())}/{len(muts)}",
            "real_namespace_untouched": real_ns_untouched,
            "pass": control_ok and real_ns_untouched and len(muts) == len(proto["governed_mutations"])
            and all(v["detected"] for v in muts.values())}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("driver")
    d.add_argument("--src-repo", required=True)
    d.add_argument("--out", required=True)
    d.add_argument("--mutation")
    d.add_argument("--work", required=True)
    a = ap.parse_args()
    driver(a)
