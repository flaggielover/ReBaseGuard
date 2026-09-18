"""r3 qualification suites for the independent-review defects D1-D4 (EXECUTOR_SPEC_R3.md). NON-SCIENTIFIC.

    d1_part(proto)  in-process prelaunch verification: adversarial suite + D01-D04 and A01-A03 mutants
    d2_part(proto)  slot-N marker lifecycle and ledger reconciliation: supervisor runs + marker faults + L01-L04, V01
    d3_part(proto)  reboot recovery: crash boundaries x {same boot, changed boot}, LIVE, idempotence, a live crash, R01-R02
    provenance_*    D4 RUN_PROVENANCE.json

Only manufactured fixtures, qualification backends (burn, diskfull) and SYNTHETIC verifier reports / countersignatures
are used. The real verifier is called on the host where no AUTHORIZATION_ACTIVE.json exists, so it REFUSES; nothing
real is authorized or computed. REAL_INPUT_ARITHMETIC_GUARD stays DENY (its file is never touched).
"""
from __future__ import annotations

import copy
import errno
import hashlib
import importlib.util
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
import types
from pathlib import Path

import paths

NS = paths.NS
CODE = NS / "code"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def variant(file: str, mut: dict | None = None, name: str | None = None):
    """The module compiled from code/<file>, optionally with one text mutation, imported normally from a private
    temporary directory (importlib registers it; nothing is patched). Path constants are pinned to the real namespace,
    as in the mutant-dir harness of qualify_executor."""
    import importlib
    import secrets
    src = (CODE / file).read_text()
    if mut is not None:
        if src.count(mut["old"]) != 1:
            raise ValueError(f"anchor {mut['id']}")
        src = src.replace(mut["old"], mut["new"])
    src = src.replace("NS = Path(__file__).resolve().parents[1]", f'NS = Path("{NS}")')
    src = src.replace('CLI = Path(__file__).resolve().parent / "executor_cli.py"', f'CLI = Path("{CODE / "executor_cli.py"}")')
    tag = name or f"v_{Path(file).stem}_{(mut or {}).get('id', 'control')}_{secrets.token_hex(4)}"
    d = Path(tempfile.mkdtemp(prefix="exec-variant-"))
    (d / f"{tag}.py").write_text(src)
    sys.path.insert(0, str(d))
    try:
        return importlib.import_module(tag)
    finally:
        sys.path.remove(str(d))


def _row(ok, **detail):
    return {"pass": bool(ok), **detail}


# ================================================================== D1
def _real_ctx(slot=1):
    import executor_core as EC
    import input_adapters as IA
    import qualify_executor as Q
    ctx = Q.context_for(IA.RealInputAdapter().bind(), Path(EC.prereg()["output_namespace"]) / f"slot-{slot}")
    return ctx


def _synthetic(ctx, AI):
    """A synthetic, self-consistent PERMITTED world for the pure layers (never written to the repository)."""
    head = "1" * 40
    facts = {"auth_path": "/synthetic/AUTHORIZATION_ACTIVE.json", "auth_path_is_prereg_path": True, "auth_sha": "a" * 64,
             "auth_sha_after": "a" * 64, "science_sha": ctx.protocol_sha256, "head": head}
    report = {"schema": AI.REPORT_SCHEMA, "verdict": "LAUNCH_PERMITTED", "failing_checks": [],
              "checks": {c: {"pass": True, "detail": "synthetic"} for c in AI.CHECK_IDS}, "read_only": True,
              "authorization_path": facts["auth_path"], "authorization_sha256": facts["auth_sha"],
              "science_sha256": ctx.protocol_sha256, "head": head, "freeze_commit_derived": "2" * 40,
              "authorization_commit_derived": "3" * 40}
    live = AI.executor_identity()["files"]
    amendment = {"executor_sources_sha256": {AI.REL + f: h for f, h in live.items()}}
    am_sha = sha(json.dumps(amendment, sort_keys=True).encode())
    facts.update({"amendment_sha": am_sha, "amendment": amendment,
                  "auth": {"PRODUCER_R4_IDENTITY": {"executor_binding_sha256": am_sha}}})
    return facts, report, am_sha


class _FakeVerifier(types.ModuleType):
    """A verifier module that is NOT the frozen one (its verify is foreign code); records whether it was executed."""

    def __init__(self, report):
        super().__init__("fake_prelaunch_verify")
        import prelaunch_verify as PV
        self.__file__ = PV.__file__                     # even the path and bytes of the frozen file do not suffice
        self.AUTH_ACTIVE, self.AMENDMENT = PV.AUTH_ACTIVE, PV.AMENDMENT
        self.calls = []
        self._report = report

        def verify(auth_path, **kw):
            self.calls.append(str(auth_path))
            return copy.deepcopy(self._report)
        self.verify = verify


def d1_suite(AI) -> dict:
    """Every row must pass. AI is authorization_interface (or a mutant of it)."""
    import executor_core as EC
    import prelaunch_verify as PV
    rows = {}
    ctx = _real_ctx()
    facts, report, am_sha = _synthetic(ctx, AI)

    # ---- the production call path, structurally and live
    import ast
    tree = ast.parse((CODE / "authorization_interface.py").read_text())
    fns = {n.name: ast.unparse(n) for n in tree.body if isinstance(n, ast.FunctionDef)}
    vfn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "validate")
    rows["production_path_calls_frozen_verifier_in_process"] = _row(
        [a.arg for a in vfn.args.args] == ["ctx"]
        and "import prelaunch_verify as PV" in fns.get("validate", "")
        and "return validate_with(ctx, PV, COUNTERSIGNATURE_FILE)" in fns.get("validate", "")
        and "run_verifier(module.verify, module.AUTH_ACTIVE)" in fns.get("validate_with", ""))
    cli = (CODE / "executor_cli.py").read_text()
    rows["no_cli_path_for_authorization_material"] = _row("--authorization" not in cli and "prelaunch_report" not in cli
                                                          and "authorization_bundle" not in cli)
    rows["frozen_verifier_source_accepted"] = _row(AI.verifier_source_problems(PV) == [])
    ok, problems, binding = AI.validate(ctx)
    # on this host no AUTHORIZATION_ACTIVE.json exists: the frozen verifier either raises (it cannot read the file) or
    # returns REFUSED; both refuse, and nothing else is accepted
    rows["live_verifier_refuses_unauthorized_host"] = _row(
        ok is False and (any(x.startswith("verifier raised") for x in problems)
                         or (binding.get("prelaunch_verdict") == "REFUSED" and any("verifier verdict" in x for x in problems))),
        problems=[EC.mask(x) for x in problems[:3]])
    genuine = PV.verify(PV.TEMPLATE)                        # a genuine frozen-verifier REFUSED object (read-only)
    rows["genuine_refused_report_is_refused"] = _row(genuine.get("verdict") == "REFUSED"
                                                     and AI.decide_from_report(genuine, AI.live_facts(PV) | {
                                                         "auth_sha_after": AI.live_facts(PV)["auth_sha"]}, ctx) != [],
                                                     primary=EC.mask(str(genuine.get("primary_reason"))[:80]))
    rows["guard_external_policy_refuses_live"] = _row(EC.decide("EXTERNAL_AUTHORIZATION", ctx)["real_arithmetic_permitted"] is False)
    rows["guard_frozen_policy_deny"] = _row(EC.guard_decision(ctx)["policy"] == "DENY"
                                            and EC.guard_decision(ctx)["real_arithmetic_permitted"] is False)

    # ---- forged operator report / operator material: refused before any verifier code runs
    fake = _FakeVerifier(report)
    forged_ctx = copy.copy(ctx)
    forged_ctx.prelaunch_report = copy.deepcopy(report)
    ok, problems, binding = AI.validate_with(forged_ctx, fake, AI.COUNTERSIGNATURE_FILE)
    rows["forged_operator_report_refused_before_verifier"] = _row(
        ok is False and binding == {} and fake.calls == [] and problems[:1]
        and problems[0].startswith("operator-supplied"), problems=problems[:2])
    ok, _, _ = AI.validate(forged_ctx)
    rows["forged_operator_report_refused_on_frozen_path"] = _row(ok is False)

    # ---- wrong verifier source: never executed
    fake2 = _FakeVerifier(report)
    ok, problems, binding = AI.validate_with(ctx, fake2, AI.COUNTERSIGNATURE_FILE)
    rows["non_frozen_verifier_never_executed"] = _row(ok is False and fake2.calls == [] and binding == {},
                                                      problems=problems[:2])
    tmp = Path(tempfile.mkdtemp(prefix="exec-d1-"))
    for label, mutate in (("modified_copy", lambda b: b + b"\n# modified\n"), ("unmodified_copy_elsewhere", lambda b: b)):
        f = tmp / label / "level4" / "closure_proofs" / "ns" / "code" / "prelaunch_verify.py"
        f.parent.mkdir(parents=True)
        f.write_bytes(mutate(Path(PV.__file__).read_bytes()))
        spec = importlib.util.spec_from_file_location(f"pv_{label}", f)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        rows[f"wrong_verifier_source_{label}"] = _row(bool(AI.verifier_source_problems(mod)))

    # ---- verifier raises / returns FAIL / malformed
    rows["verifier_raises"] = _row(AI.run_verifier(lambda p: (_ for _ in ()).throw(RuntimeError("boom")), "x")[1]
                                   == "verifier raised RuntimeError")
    rows["positive_control_synthetic_permitted_report"] = _row(AI.decide_from_report(report, facts, ctx) == [])

    _same = object()

    def bad(label, rep=_same, fct=None, c=None):
        r = copy.deepcopy(report) if rep is _same else rep
        rows[label] = _row(AI.decide_from_report(r, fct or facts, c or ctx) != [])

    def edit(**kw):
        r = copy.deepcopy(report)
        r.update(kw)
        return r

    bad("verifier_returns_refused", edit(verdict="REFUSED", failing_checks=["P01"]))
    bad("verifier_failing_checks_nonempty", edit(failing_checks=["P11"]))
    r = copy.deepcopy(report)
    del r["checks"]["P07"]
    bad("verifier_output_missing_check", r)
    r = copy.deepcopy(report)
    r["checks"]["P04"]["pass"] = False
    bad("verifier_check_failed_but_verdict_permitted", r)
    bad("verifier_output_malformed_list", [report])
    bad("verifier_output_malformed_none", None)
    bad("verifier_output_wrong_schema", edit(schema="rebaseguard.other.v1"))
    bad("verifier_output_not_read_only", edit(read_only=False))
    bad("stale_report_other_head", edit(head="4" * 40))
    bad("report_for_another_authorization_sha", edit(authorization_sha256="b" * 64))
    bad("report_for_another_authorization_path", edit(authorization_path="/elsewhere/AUTHORIZATION_ACTIVE.json"))
    bad("authorization_changed_after_verification", fct=dict(facts, auth_sha_after="c" * 64))
    bad("authorization_path_not_prereg_path", fct=dict(facts, auth_path_is_prereg_path=False))
    bad("wrong_protocol_identity_in_report", edit(science_sha256="d" * 64))
    other = copy.copy(ctx)
    other.protocol_sha256 = "e" * 64
    bad("correct_report_wrong_protocol_identity_in_context", c=other)
    bad("report_without_derived_commits", edit(authorization_commit_derived=None))
    rows["authorization_rehash_detects_change"] = _row(AI.authorization_unchanged({"authorization_sha256": "0" * 64}) is False
                                                       and AI.authorization_unchanged({}) is False)

    # ---- executor binding (amendment <-> authorization <-> address <-> running bytes)
    bctx = copy.copy(ctx)
    bctx.executor_binding_sha256 = am_sha
    rows["binding_positive_control"] = _row(AI.binding_problems(facts, bctx) == [])
    rows["binding_authorization_names_other"] = _row(AI.binding_problems(
        dict(facts, auth={"PRODUCER_R4_IDENTITY": {"executor_binding_sha256": "f" * 64}}), bctx) != [])
    rows["binding_context_names_other"] = _row(AI.binding_problems(facts, ctx) != [])
    stale_am = copy.deepcopy(facts["amendment"])
    stale_am["executor_sources_sha256"][AI.REL + "code/executor_core.py"] = "0" * 64
    rows["binding_amendment_not_running_bytes"] = _row(AI.binding_problems(dict(facts, amendment=stale_am), bctx) != [])
    rows["binding_no_amendment"] = _row(AI.binding_problems(dict(facts, amendment=None, amendment_sha=None), bctx) != [])

    # ---- countersignature (second requirement), with synthetic git helpers and a temporary file
    git_ok = types.SimpleNamespace(committed_unmodified=lambda p: True, introduced_by=lambda p: ["5" * 40],
                                   is_ancestor=lambda a, b: True)
    tmpl = json.loads(AI.TEMPLATE_FILE.read_text())
    cs = dict(tmpl, status="COUNTERSIGNED", EXECUTION_AUTHORIZED=True, protocol_authorization_sha256=facts["auth_sha"],
              execution_binding_amendment_sha256=am_sha, attempt_slot=1, nonce="5a" * 16,
              countersigner={"identity": "SYNTHETIC-QUALIFICATION-ONLY", "independent_of_execution_host": True,
                             "verified_from": "synthetic", "utc": time.time() - 100})

    def cs_rows(label, obj, helpers=git_ok, want_ok=False, raw=None):
        f = tmp / f"cs_{label}.json"
        f.write_text(raw if raw is not None else json.dumps(obj))
        probs = AI.countersignature_problems(facts, report, ctx, helpers, f)
        rows[f"countersignature_{label}"] = _row((probs == []) is want_ok, problems=probs[:2])

    cs_rows("positive_control", cs, want_ok=True)
    cs_rows("names_other_authorization", dict(cs, protocol_authorization_sha256="b" * 64))
    cs_rows("names_other_amendment", dict(cs, execution_binding_amendment_sha256="b" * 64))
    cs_rows("other_slot", dict(cs, attempt_slot=2))
    cs_rows("countersigner_not_independent", dict(cs, countersigner=dict(cs["countersigner"], independent_of_execution_host=False)))
    cs_rows("countersigned_in_future", dict(cs, countersigner=dict(cs["countersigner"], utc=time.time() + 10 ** 6)))
    cs_rows("short_nonce", dict(cs, nonce="abc"))
    cs_rows("inactive", dict(cs, status="INACTIVE_TEMPLATE"))
    cs_rows("result_blind_changed", dict(cs, result_blind="seen"))
    cs_rows("extra_field", dict(cs, extra=1))
    cs_rows("malformed", None, raw="{not json")
    cs_rows("not_committed", cs, helpers=types.SimpleNamespace(committed_unmodified=lambda p: False,
                                                               introduced_by=lambda p: [], is_ancestor=lambda a, b: False))
    cs_rows("committed_before_authorization", cs, helpers=types.SimpleNamespace(
        committed_unmodified=lambda p: True, introduced_by=lambda p: ["5" * 40], is_ancestor=lambda a, b: False))
    rows["countersignature_absent_on_host"] = _row(bool(AI.countersignature_problems(facts, report, ctx, PV,
                                                                                      AI.COUNTERSIGNATURE_FILE)))
    shutil.rmtree(tmp, ignore_errors=True)
    return rows


def d1_part(proto) -> dict:
    import authorization_interface as AI
    control = d1_suite(AI)
    muts = {}
    for mut in proto["d1_mutations"] + proto["authorization_mutations"]:
        try:
            rows = d1_suite(variant("authorization_interface.py", mut))
            failing = [k for k, v in rows.items() if not v["pass"]]
            muts[mut["id"]] = {"detected": bool(failing), "failing": failing[:6]}
        except Exception as exc:                                                    # a crash is NOT a detection
            muts[mut["id"]] = {"detected": False, "crashed": f"{type(exc).__name__}: {str(exc)[:200]}"}
    control_ok = all(v["pass"] for v in control.values())
    return {"rows": control, "control_pass": control_ok, "mutations": muts,
            "mutations_count": f"{sum(v['detected'] for v in muts.values())}/{len(muts)}",
            "pass": control_ok and len(muts) == 7 and all(v["detected"] for v in muts.values())}


# ================================================================== D2
def _child_pid_for(slot: Path) -> int | None:
    for d in Path("/proc").iterdir():
        if not d.name.isdigit():
            continue
        try:
            argv = [a.decode(errors="replace") for a in (d / "cmdline").read_bytes().split(b"\0") if a]
        except OSError:
            continue
        if any(Path(a).name == "executor_cli.py" for a in argv) and str(slot) in argv:
            return int(d.name)
    return None


def _wait_started(slot: Path, timeout=300) -> bool:
    for _ in range(int(timeout / 0.25)):
        log = slot / "ATTEMPT_LOG.jsonl"
        if log.exists() and "ARITHMETIC_STARTED" in log.read_text():
            return True
        time.sleep(0.25)
    return False


def supervisor_runs(proto, root: Path, SV=None, cli=None) -> dict:
    """The six supervisor scenarios of the D2 matrix (real child processes, qualification backends only)."""
    import executor_core as EC
    import lifecycle as LC
    import probe_rules as PR
    SV = SV or __import__("supervisor")
    T = proto["supervisor_tests"]
    fid = T["fixture"]
    ceil = EC.prereg()["cpu_ceiling"]
    full = {"cpu_soft": ceil["per_attempt_cpu_seconds_soft"], "cpu_hard": ceil["per_attempt_cpu_seconds_rlimit"],
            "wall": ceil["per_attempt_wall_seconds"]}
    kw = {} if cli is None else {"cli": cli}
    runs = {}

    def run(name, mode, lim, fixture=True):
        return SV.supervise(root / name / "slot-1", mode, fixture_id=fid if fixture else None, **lim, **kw)

    runs["success"] = run("success", "manufactured", full)
    # r4 (EXECUTOR_SPEC_R4.md R4-1): a real launch under DENY is PRELAUNCH_REFUSED before any slot exists
    runs["real_launch_prelaunch_refused"] = run("prelaunch", "real", full, fixture=False)
    # a refusal AFTER the slot exists but before arithmetic (the D2 lifecycle case): a second attempt of an already
    # sealed fixture in the same namespace is refused by the executor (FINALIZED_ADDRESS_EXISTS) -> RUN_FAILED
    runs["pre_arithmetic_refusal"] = SV.supervise(root / "success" / "slot-2", "manufactured", fixture_id=fid, **full, **kw)
    runs["cpu_ceiling"] = run("cpu", "burn", T["cpu_limit"])
    runs["wall_timeout"] = run("wall", "burn", T["wall_timeout"])
    holder = {}
    th = threading.Thread(target=lambda: holder.setdefault("r", run("kill", "burn", T["external_kill"])))
    th.start()
    slot = root / "kill" / "slot-1"
    if _wait_started(slot):
        time.sleep(1.0)
        pid = _child_pid_for(slot)
        if pid:
            os.kill(pid, signal.SIGKILL)
    th.join()
    runs["external_kill"] = holder.get("r")
    runs["disk_full"] = run("disk", "diskfull", full)
    return runs


def expected_runs(runs: dict, root: Path) -> dict:
    import lifecycle as LC
    import probe_rules as PR
    rows = {}

    def files(name):
        return sorted(p.name for p in (root / name / "slot-1").iterdir())

    s = runs["success"]
    rows["success_complete_only"] = _row(
        s["terminal"] == "RUN_COMPLETE.json" and files("success") == ["ATTEMPT_LOG.jsonl", "MANUFACTURED_RECORD_SEALED.json",
                                                                     "RUN_COMPLETE.json", "RUN_STATE.json"]
        and s["marker"]["sealed_record_sha256"] == sha((root / "success/slot-1/MANUFACTURED_RECORD_SEALED.json").read_bytes())
        and len(s["marker"]["qualification_gates"]) == 16 and s["events"] == ["VALIDATED", "ARITHMETIC_STARTED", "SEALED"])
    r = runs["real_launch_prelaunch_refused"]
    rows["real_launch_prelaunch_refused_no_slot"] = _row(
        r.get("prelaunch") == "PRELAUNCH_REFUSED" and r.get("terminal") is None and r.get("slot_created") is False
        and not (root / "prelaunch").exists(), got={k: r.get(k) for k in ("prelaunch", "problems", "slot_created")})
    r = runs["pre_arithmetic_refusal"]
    refused_slot = root / "success" / "slot-2"
    rows["pre_arithmetic_refusal"] = _row(
        r["terminal"] == "RUN_FAILED.json" and r["failure_class"] == "INTEGRITY_REFUSAL"
        and r["marker"]["arithmetic_started"] is False and r["events"] == []
        and sorted(p.name for p in refused_slot.iterdir()) == ["RUN_FAILED.json", "RUN_STATE.json"]
        and "FINALIZED_ADDRESS_EXISTS" in (r["marker"]["supervisor_evidence"]["integrity_refusal"] or ""),
        got=r.get("failure_class"))
    for key, name, cls in (("cpu_ceiling", "cpu", "CPU_RLIMIT"), ("wall_timeout", "wall", "WALL_TIMEOUT")):
        r = runs[key]
        rows[key] = _row(r["terminal"] == "RUN_FAILED.json" and r["failure_class"] == cls and r["marker"]["arithmetic_started"]
                         and "MANUFACTURED_VOID_RECORD_SEALED.json" in files(name)
                         and r["marker"]["void_record_sha256"] == sha((root / name / "slot-1/MANUFACTURED_VOID_RECORD_SEALED.json").read_bytes())
                         and r["events"] == ["VALIDATED", "ARITHMETIC_STARTED", "VOID"], failure_class=r["failure_class"])
    r = runs["external_kill"] or {}
    rows["external_kill"] = _row(r.get("failure_class") == "PROCESS_KILLED_BY_EXTERNAL_SIGNAL"
                                 and r["marker"]["arithmetic_started"] is True
                                 and not any(n in LC.ALL_SEALS for n in files("kill"))
                                 and PR.retry_decision({"arithmetic_started": True, "sealed_record_exists": False,
                                                        "failure_class": r["failure_class"], "attempts_started": 1})["decision"]
                                 == "RETRY_PERMITTED", failure_class=r.get("failure_class"))
    r = runs["disk_full"]
    rows["disk_full_transient_no_seal"] = _row(r["failure_class"] == "DISK_FULL_BEFORE_SEAL" and r["marker"]["arithmetic_started"]
                                               and not any(n in LC.ALL_SEALS for n in files("disk")),
                                               failure_class=r["failure_class"])
    for name, slot_path in (("success", "success/slot-1"), ("refusal", "success/slot-2"), ("cpu", "cpu/slot-1"),
                            ("wall", "wall/slot-1"), ("kill", "kill/slot-1"), ("disk", "disk/slot-1")):
        c = LC.classify(root / slot_path, current_boot=LC.boot_id(), pid_alive_with_argv=lambda *a: False)
        rows[f"classify_terminal_{name}"] = _row(c["class"] != "E" and c["terminal"] is not None, problems=c["problems"][:2])
        # no numbers outside the sealed record: masked traceback / refusal, events without values
        text = "".join((root / slot_path / f).read_text() for f in ("RUN_FAILED.json",) if (root / slot_path / f).exists())
        if text:
            fail = json.loads(text)
            rows[f"no_digits_in_failure_text_{name}"] = _row(not any(ch.isdigit() for ch in fail["traceback"]
                                                                   + str(fail["supervisor_evidence"].get("integrity_refusal") or "")))
    return rows


def _ledger_for(slot: Path) -> list:
    import lifecycle as LC
    state = json.loads((slot / LC.RUN_STATE).read_text())
    led = [{"event": "LAUNCH_NOTICE", "slot": slot.name, "authorization_sha256": state["authorization_sha256"], "utc": "x"},
           LC.outcome_entry(slot)]
    seal = next((n for n in LC.ALL_SEALS if (slot / n).exists()), None)
    if seal:
        led.append({"event": "VOID_RECORD_SEALED" if "VOID" in seal else "SCIENTIFIC_RECORD_SEALED", "slot": slot.name,
                    "sha256": sha((slot / seal).read_bytes())})
    return led


def _copy_slot(src: Path, dst: Path) -> Path:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst)
    return dst


class _RU:
    ru_utime, ru_stime = 1.0, 0.0


def marker_faults(root: Path, EC, LC, SV) -> dict:
    """Marker-fault matrix on copies of real slots. EC / LC / SV may be mutants (L-group)."""
    import probe_rules as PR
    rows = {}
    ok_slot = root / "success" / "slot-1"
    faults = root / "faults"
    boot = LC.boot_id()
    dead = lambda *a: False                                                                      # noqa: E731

    s = _copy_slot(ok_slot, faults / "malformed" / "slot-1")
    (s / "RUN_COMPLETE.json").write_text("{not json")
    rows["malformed_marker_is_torn"] = _row(LC.classify(s, current_boot=boot, pid_alive_with_argv=dead)["class"] == "E")
    s = _copy_slot(ok_slot, faults / "dup" / "slot-1")
    try:
        LC.write_terminal(s, "RUN_FAILED.json", {"attempt_uid": "x"})
        rows["duplicate_terminal_refused"] = _row(False)
    except LC.MarkerError:
        rows["duplicate_terminal_refused"] = _row(not (s / "RUN_FAILED.json").exists())
    s2 = _copy_slot(ok_slot, faults / "dup2" / "slot-1")
    state = json.loads((s2 / "RUN_STATE.json").read_text())
    (s2 / "RUN_FAILED.json").write_text(json.dumps({"attempt_uid": state["attempt_uid"]}))
    rows["duplicate_terminal_present_is_torn"] = _row(LC.classify(s2, current_boot=boot, pid_alive_with_argv=dead)["class"] == "E")
    s = _copy_slot(ok_slot, faults / "conflict" / "slot-1")
    rec = json.loads((s / "MANUFACTURED_RECORD_SEALED.json").read_text())
    try:
        EC.seal(dict(rec, void=True), s, "MANUFACTURED_VOID_RECORD_SEALED.json")
        rows["scientific_void_conflict_refused_at_seal"] = _row(False)
    except Exception as exc:
        rows["scientific_void_conflict_refused_at_seal"] = _row("SEAL_CONFLICT" in str(exc)
                                                                and not (s / "MANUFACTURED_VOID_RECORD_SEALED.json").exists())
    s3 = _copy_slot(ok_slot, faults / "conflict2" / "slot-1")
    shutil.copy(s3 / "MANUFACTURED_RECORD_SEALED.json", s3 / "MANUFACTURED_VOID_RECORD_SEALED.json")
    rows["scientific_void_conflict_present_is_torn"] = _row(LC.classify(s3, current_boot=boot, pid_alive_with_argv=dead)["class"] == "E")
    s = _copy_slot(ok_slot, faults / "stale" / "slot-1")
    comp = json.loads((s / "RUN_COMPLETE.json").read_text())
    (s / "RUN_COMPLETE.json").write_text(json.dumps(dict(comp, attempt_uid="another-attempt")))
    rows["stale_terminal_marker_is_torn"] = _row(LC.classify(s, current_boot=boot, pid_alive_with_argv=dead)["class"] == "E")
    stale_slot = faults / "stale_state" / "slot-1"
    stale_slot.mkdir(parents=True)
    LC.write_new(stale_slot, LC.RUN_STATE, dict(state, attempt_uid="another-attempt", pid=os.getppid()))
    rows["executor_refuses_stale_run_state"] = _row(bool(EC.slot_admission(stale_slot, state["attempt_uid"])))
    rows["executor_admits_own_run_state"] = _row(EC.slot_admission(stale_slot, "another-attempt") == [])
    # ledger reconciliation
    led = _ledger_for(ok_slot)
    rows["ledger_reconciles_success"] = _row(LC.reconcile(ok_slot, led) == [])
    for key, rel in (("cpu", "cpu/slot-1"), ("refusal", "success/slot-2"), ("kill", "kill/slot-1")):
        sl = root / rel
        rows[f"ledger_reconciles_{key}"] = _row(LC.reconcile(sl, _ledger_for(sl)) == [])
    cpu_slot = root / "cpu" / "slot-1"
    bad = _ledger_for(cpu_slot)
    bad[1] = dict(bad[1], failure_class="HOST_REBOOT_OR_BOOT_ID_CHANGE")
    rows["ledger_disagreement_failure_class"] = _row(LC.reconcile(cpu_slot, bad) != [])
    bad = _ledger_for(cpu_slot)
    bad[1] = dict(bad[1], run_failed_sha256="0" * 64)
    rows["ledger_disagreement_run_failed_sha"] = _row(LC.reconcile(cpu_slot, bad) != [])
    bad = _ledger_for(ok_slot)
    bad[1] = dict(bad[1], sealed_record_sha256=None)
    rows["ledger_disagreement_seal_missing_in_ledger"] = _row(LC.reconcile(ok_slot, bad) != [])
    kill_slot = root / "kill" / "slot-1"
    bad = _ledger_for(kill_slot) + [{"event": "SCIENTIFIC_RECORD_SEALED", "slot": "slot-1", "sha256": "0" * 64}]
    rows["ledger_seal_host_does_not_hold"] = _row(LC.reconcile(kill_slot, bad) != [])
    # no RUN_COMPLETE without a valid sealed record (supervisor finish on a tampered seal, exit 0)
    s = _copy_slot(ok_slot, faults / "tampered" / "slot-1")
    (s / "RUN_COMPLETE.json").unlink()
    rec = json.loads((s / "MANUFACTURED_RECORD_SEALED.json").read_text())
    rec["scientific"]["per_m"]["1"]["L0"] = "0/1"
    (s / "MANUFACTURED_RECORD_SEALED.json").write_text(json.dumps(rec))
    st = json.loads((s / "RUN_STATE.json").read_text())
    r = SV.finish(s, st, status=0, ru=_RU(), wall_seconds=1.0, wall_timeout=False, cpu_soft=9000, stderr_text="")
    rows["no_complete_without_valid_seal"] = _row(r["terminal"] == "RUN_FAILED.json" and not (s / "RUN_COMPLETE.json").exists()
                                                  and r["failure_class"] == "INTEGRITY_REFUSAL")
    # VOID only for integrity / cost classes; a transient disk-full error seals nothing
    rows["void_class_disk_full_is_transient"] = _row(EC.void_class(OSError(errno.ENOSPC, "No space left on device")) is None
                                                     and EC.void_class(EC.ExecutorRefusal("CPU_RLIMIT: x")) == "CPU_RLIMIT"
                                                     and EC.void_class(EC.ExecutorRefusal("WALL_TIMEOUT: x")) == "WALL_TIMEOUT"
                                                     and EC.void_class(EC.ExecutorRefusal("K1_IDENTITY_MISMATCH")) == "INTEGRITY_REFUSAL")
    return rows


def d2_part(proto) -> dict:
    import executor_core as EC
    import lifecycle as LC
    import supervisor as SV
    import qualify_executor as Q
    root = Path(tempfile.mkdtemp(prefix="exec-d2-"))
    runs = supervisor_runs(proto, root)
    rows = expected_runs(runs, root)
    rows.update(marker_faults(root, EC, LC, SV))
    muts = {}
    targets = {"supervisor.py": "SV", "executor_core.py": "EC", "lifecycle.py": "LC"}
    for mut in proto["lifecycle_mutations"]:
        try:
            mods = {"EC": EC, "LC": LC, "SV": SV}
            mods[targets[mut["file"]]] = variant(mut["file"], mut)
            sub = root / f"mut_{mut['id']}"
            for rel in ("success/slot-1", "success/slot-2", "cpu/slot-1", "kill/slot-1"):
                _copy_slot(root / rel, sub / rel)
            mr = marker_faults(sub, mods["EC"], mods["LC"], mods["SV"])
            failing = [k for k, v in mr.items() if not v["pass"]]
            muts[mut["id"]] = {"detected": bool(failing), "failing": failing[:6]}
        except Exception as exc:
            muts[mut["id"]] = {"detected": False, "crashed": f"{type(exc).__name__}: {str(exc)[:200]}"}
    # V01: VOID sealing dropped, through a mutant-shadowing executor wrapper under the real supervisor
    for mut in proto["void_mutations"]:
        md = Path(tempfile.mkdtemp(prefix=f"exec-v-{mut['id']}-"))
        src = (CODE / mut["file"]).read_text()
        (md / mut["file"]).write_text(src.replace(mut["old"], mut["new"]).replace(
            "NS = Path(__file__).resolve().parents[1]", f'NS = Path("{NS}")'))
        wrapper = md / "cli_wrapper.py"
        wrapper.write_text(Q.WRAPPER.format(code=str(CODE), mut=str(md), cli=str(SV.CLI)))
        T = proto["supervisor_tests"]
        r = SV.supervise(root / f"v_{mut['id']}" / "slot-1", "burn", fixture_id=T["fixture"], cli=wrapper, **T["cpu_limit"])
        sealed = (root / f"v_{mut['id']}" / "slot-1" / "MANUFACTURED_VOID_RECORD_SEALED.json").exists()
        muts[mut["id"]] = {"detected": not (sealed and r["failure_class"] == "CPU_RLIMIT")}
    control_ok = all(v["pass"] for v in rows.values())
    want = len(proto["lifecycle_mutations"]) + len(proto["void_mutations"])
    return {"rows": rows, "control_pass": control_ok, "mutations": muts,
            "mutations_count": f"{sum(v['detected'] for v in muts.values())}/{len(muts)}",
            "runs": {k: {x: (v or {}).get(x) for x in ("terminal", "failure_class", "events")} for k, v in runs.items()},
            "pass": control_ok and len(muts) == want and all(v["detected"] for v in muts.values())}


# ================================================================== D3
BOUNDARIES = ("before_run_state", "after_run_state", "during_attempt_log", "before_scientific_seal",
              "immediately_after_scientific_seal", "before_run_complete", "after_void_seal",
              "during_terminal_write_tmp", "during_terminal_write_truncated")


def build_boundaries(root: Path, ok_slot: Path, void_slot: Path, out: Path) -> dict:
    """Crash states cut from real manufactured runs at each boundary."""
    import lifecycle as LC
    slots = {}
    state = json.loads((ok_slot / LC.RUN_STATE).read_text())
    events = (ok_slot / LC.ATTEMPT_LOG).read_text().splitlines(keepends=True)

    def fresh(name):
        d = out / name / "slot-1"
        d.mkdir(parents=True)
        slots[name] = d
        return d

    fresh("before_run_state")
    d = fresh("after_run_state")
    shutil.copy(ok_slot / LC.RUN_STATE, d / LC.RUN_STATE)
    d = fresh("during_attempt_log")
    shutil.copy(ok_slot / LC.RUN_STATE, d / LC.RUN_STATE)
    (d / LC.ATTEMPT_LOG).write_text(events[0] + events[1][: len(events[1]) // 2])
    d = fresh("before_scientific_seal")
    shutil.copy(ok_slot / LC.RUN_STATE, d / LC.RUN_STATE)
    (d / LC.ATTEMPT_LOG).write_text("".join(events[:2]))
    (d / ".MANUFACTURED_RECORD_SEALED.json.4242.tmp").write_text("{partial")
    d = fresh("immediately_after_scientific_seal")
    for n in (LC.RUN_STATE, "MANUFACTURED_RECORD_SEALED.json"):
        shutil.copy(ok_slot / n, d / n)
    (d / LC.ATTEMPT_LOG).write_text("".join(events[:2]))
    d = fresh("before_run_complete")
    for n in (LC.RUN_STATE, LC.ATTEMPT_LOG, "MANUFACTURED_RECORD_SEALED.json"):
        shutil.copy(ok_slot / n, d / n)
    d = fresh("after_void_seal")
    for n in (LC.RUN_STATE, LC.ATTEMPT_LOG, "MANUFACTURED_VOID_RECORD_SEALED.json"):
        shutil.copy(void_slot / n, d / n)
    d = fresh("during_terminal_write_tmp")
    for n in (LC.RUN_STATE, LC.ATTEMPT_LOG, "MANUFACTURED_RECORD_SEALED.json"):
        shutil.copy(ok_slot / n, d / n)
    (d / ".RUN_COMPLETE.json.4242.tmp").write_bytes((ok_slot / "RUN_COMPLETE.json").read_bytes()[:40])
    d = fresh("during_terminal_write_truncated")
    for n in (LC.RUN_STATE, LC.ATTEMPT_LOG, "MANUFACTURED_RECORD_SEALED.json"):
        shutil.copy(ok_slot / n, d / n)
    (d / "RUN_COMPLETE.json").write_bytes((ok_slot / "RUN_COMPLETE.json").read_bytes()[:40])
    return slots


EXPECTED = {"before_run_state": ("A", "WRITE_RUN_FAILED_NOT_STARTED"),
            "after_run_state": ("A", "WRITE_RUN_FAILED_NOT_STARTED"),
            "during_attempt_log": ("A", "WRITE_RUN_FAILED_NOT_STARTED"),
            "before_scientific_seal": ("B", "WRITE_RUN_FAILED_INTERRUPTED"),
            "immediately_after_scientific_seal": ("C", "CONSUME_SEALED_RECORD_WRITE_RUN_COMPLETE_RECOVERED"),
            "before_run_complete": ("C", "CONSUME_SEALED_RECORD_WRITE_RUN_COMPLETE_RECOVERED"),
            "after_void_seal": ("D", "WRITE_RUN_FAILED_VOID"),
            "during_terminal_write_tmp": ("C", "CONSUME_SEALED_RECORD_WRITE_RUN_COMPLETE_RECOVERED"),
            "during_terminal_write_truncated": ("E", "ADJUDICATION_REQUIRED")}


def classification_rows(LC, slots: dict, boot: str) -> dict:
    """Pure classification (used for R-group mutants)."""
    rows = {}
    for name, slot in slots.items():
        c = LC.classify(slot, current_boot=boot, pid_alive_with_argv=lambda *a: False)
        act = LC.recovery_action(c)
        rows[f"classify_{name}"] = _row((c["class"], act) == EXPECTED[name], got=[c["class"], act])
    return rows


def _tree_hash(d: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(d.rglob("*")):
        if p.is_file():
            h.update(str(p.relative_to(d)).encode() + b"\0" + p.read_bytes())
    return h.hexdigest()


def d3_part(proto) -> dict:
    import executor_core as EC
    import lifecycle as LC
    import probe_rules as PR
    import supervisor as SV
    import qualify_executor as Q
    import input_adapters as IA
    import backends as B
    root = Path(tempfile.mkdtemp(prefix="exec-d3-"))
    T = proto["supervisor_tests"]
    ok = SV.supervise(root / "base_ok" / "slot-1", "manufactured", fixture_id=T["fixture"], cpu_soft=9000, cpu_hard=10800, wall=14400)
    vd = SV.supervise(root / "base_void" / "slot-1", "burn", fixture_id=T["fixture"], **T["cpu_limit"])
    ok_slot, void_slot = root / "base_ok" / "slot-1", root / "base_void" / "slot-1"
    rows = {"base_runs": _row(ok["terminal"] == "RUN_COMPLETE.json" and vd["failure_class"] == "CPU_RLIMIT")}
    boot = LC.boot_id()
    for label, current in (("same_boot", boot), ("changed_boot", "00000000-changed-boot-id")):
        out = root / label
        slots = build_boundaries(root, ok_slot, void_slot, out)
        for name, slot in slots.items():
            sealed_before = {n: sha((slot / n).read_bytes()) for n in LC.ALL_SEALS if (slot / n).exists()}
            report = SV.recover(slot.parent, current_boot=current, alive=lambda *a: False)[slot.name]
            want_cls, want_act = EXPECTED[name]
            after = {n: sha((slot / n).read_bytes()) for n in LC.ALL_SEALS if (slot / n).exists()}
            good = report["class"] == want_cls and report["action"] == want_act and sealed_before == after
            if want_cls == "E":
                good = good and not any((slot / t).exists() and t not in ("RUN_COMPLETE.json",) for t in LC.TERMINALS) \
                       and not (slot / "RUN_FAILED.json").exists()
            elif want_cls == "C":
                comp = json.loads((slot / "RUN_COMPLETE.json").read_text())
                good = good and comp["recovered"] is True and comp["sealed_record_sha256"] == after["MANUFACTURED_RECORD_SEALED.json"] \
                       and not (slot / "RUN_FAILED.json").exists()
            else:
                fail = json.loads((slot / "RUN_FAILED.json").read_text())
                derived = PR.failure_class(fail["supervisor_evidence"])
                want_class = "HOST_REBOOT_OR_BOOT_ID_CHANGE" if (label == "changed_boot" and name != "before_run_state") \
                    else "UNKNOWN_FAILURE"
                good = good and fail["recovered"] is True and derived == want_class \
                       and fail["arithmetic_started"] is (want_cls in ("B", "D"))
                if want_cls == "B":
                    decision = PR.retry_decision({"arithmetic_started": True, "sealed_record_exists": False,
                                                  "failure_class": derived, "attempts_started": 1})["decision"]
                    good = good and decision == ("RETRY_PERMITTED" if label == "changed_boot" else "NO_RETRY")
                if want_cls == "D":
                    good = good and fail["void_record_sha256"] == after["MANUFACTURED_VOID_RECORD_SEALED.json"]
            rows[f"{label}_{name}"] = _row(good, got=[report["class"], report["action"]])
        before = _tree_hash(out)
        again = {s: v for d in out.iterdir() for s, v in SV.recover(d, current_boot=current, alive=lambda *a: False).items()}
        rows[f"{label}_idempotent"] = _row(_tree_hash(out) == before and all(
            v["action"] in ("TERMINAL_NO_ACTION", "ADJUDICATION_REQUIRED") for v in again.values()))
    # LIVE: a slot without a terminal marker whose supervisor is alive (same boot, exact argv) is left alone
    live = build_boundaries(root, ok_slot, void_slot, root / "live")["before_scientific_seal"]
    rep = SV.recover(live.parent, current_boot=boot, alive=lambda pid, argv: True)[live.name]
    rows["live_slot_left_alone"] = _row(rep["action"] == "LIVE_NO_ACTION" and not (live / "RUN_FAILED.json").exists())
    # a sealed address is never recomputed: the namespace refuses a new attempt for the same addresses
    spec = next(f for f in proto["fixtures"] if f["id"] == T["fixture"])
    try:
        EC.execute(B.ManufacturedPointBackend(spec), Q.context_for(IA.ManufacturedInputAdapter().bind(spec),
                                                                   root / "base_ok" / "slot-2"))
        rows["sealed_address_never_rerun"] = _row(False)
    except EC.ExecutorRefusal as exc:
        rows["sealed_address_never_rerun"] = _row("FINALIZED_ADDRESS_EXISTS" in str(exc))
    # a live crash: SIGKILL the supervisor and its child mid-arithmetic, then recover
    crash_root = root / "live_crash"
    cmd = [sys.executable, "-B", str(CODE / "supervisor.py"), "launch", "--namespace", str(crash_root), "--slot", "1",
           "--mode", "burn", "--fixture-id", T["fixture"], "--cpu-soft", "600", "--cpu-hard", "900", "--wall", "600"]
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", NUMEXPR_NUM_THREADS="1")
    sup = subprocess.Popen(cmd, env=env, cwd=str(NS), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    slot = crash_root / "slot-1"
    started = _wait_started(slot)
    child = _child_pid_for(slot)
    os.kill(sup.pid, signal.SIGKILL)
    sup.wait()
    if child:
        try:
            os.kill(child, signal.SIGKILL)
        except ProcessLookupError:
            pass
    time.sleep(1.0)
    rep = SV.recover(crash_root)["slot-1"]
    fail = json.loads((slot / "RUN_FAILED.json").read_text()) if (slot / "RUN_FAILED.json").exists() else {}
    rows["live_crash_recovered"] = _row(started and rep["class"] == "B" and rep["action"] == "WRITE_RUN_FAILED_INTERRUPTED"
                                        and PR.failure_class(fail.get("supervisor_evidence") or {}) == "UNKNOWN_FAILURE"
                                        and not any((slot / n).exists() for n in LC.ALL_SEALS), got=[rep["class"], rep["action"]])
    # R-group mutants on the pure classification layer
    pure = build_boundaries(root, ok_slot, void_slot, root / "pure")
    control = classification_rows(LC, pure, boot)
    rows.update({f"pure_{k}": v for k, v in control.items()})
    muts = {}
    for mut in proto["recovery_mutations"]:
        try:
            mr = classification_rows(variant("lifecycle.py", mut), pure, boot)
            failing = [k for k, v in mr.items() if not v["pass"]]
            muts[mut["id"]] = {"detected": bool(failing), "failing": failing[:6]}
        except Exception as exc:
            muts[mut["id"]] = {"detected": False, "crashed": f"{type(exc).__name__}: {str(exc)[:200]}"}
    control_ok = all(v["pass"] for v in rows.values())
    return {"rows": rows, "control_pass": control_ok, "mutations": muts,
            "mutations_count": f"{sum(v['detected'] for v in muts.values())}/{len(muts)}",
            "pass": control_ok and len(muts) == len(proto["recovery_mutations"]) and all(v["detected"] for v in muts.values())}


# ================================================================== D4
def provenance_start(proto, outdir: Path, argv) -> dict:
    import authorization_interface as AI
    import executor_core as EC
    import flint
    import platform
    import prelaunch_verify as PV
    git = lambda *a: subprocess.run(["git", "-C", str(paths.REPO), *a], capture_output=True, text=True).stdout  # noqa: E731
    rel_out = os.path.relpath(outdir.resolve(), paths.REPO.resolve())
    porcelain = [ln for ln in git("status", "--porcelain").splitlines() if rel_out not in ln]
    facts = PV.live_host_facts()
    pins = NS / "config/EXECUTOR_PINS.json"
    return {"schema": "rebaseguard.p5y.k5.cusum-real-point-executor.run-provenance.v1",
            "git_commit": git("rev-parse", "HEAD").strip(), "porcelain_before_run": porcelain,
            "qualification_mode": "FROZEN_QUALIFICATION" if proto["status"] == "FROZEN_PRE_QUALIFICATION" else "DEV",
            "executor_identity_sha256": AI.executor_identity()["executor_identity_sha256"],
            "protocol_sha256": sha((NS / "config/EXECUTOR_QUALIFICATION_PROTOCOL.json").read_bytes()),
            "science_preregistration_sha256": sha(EC.SCIENCE_FILE.read_bytes()),
            "runtime_identity_sha256": EC.prereg()["host_runtime_identity_sha256"],
            "host_runtime_contract_differences": EC.runtime_differences(EC.prereg()["host_runtime_contract"], facts),
            "host_facts": facts, "python": platform.python_version(), "python_flint": flint.__version__,
            "flint_version": getattr(flint, "__FLINT_VERSION__", None),
            "arb": "part of FLINT >= 3 (the FLINT version above)", "glibc": facts.get("glibc_package_version"),
            "executor_pins_sha256": sha(pins.read_bytes()),
            "qualification_sources_sha256": proto["executor_sources_sha256"],
            "guard_policy": json.loads(EC.GUARD_FILE.read_text()).get("policy"),
            "authorization_state": {"protocol_authorization_active_exists": Path(PV.AUTH_ACTIVE).exists(),
                                    "countersignature_active_exists": AI.COUNTERSIGNATURE_FILE.exists(),
                                    "execution_binding_amendment_exists": Path(PV.AMENDMENT).exists(),
                                    "template_EXECUTION_AUTHORIZED": json.loads(AI.TEMPLATE_FILE.read_text())["EXECUTION_AUTHORIZED"]},
            "supervisor_identity": {"supervisor_sha256": sha((CODE / "supervisor.py").read_bytes()),
                                    "lifecycle_sha256": sha((CODE / "lifecycle.py").read_bytes()),
                                    "runner_pid": os.getpid(), "runner_argv": list(argv)},
            "started_unix": time.time(), "finished_unix": None, "qualification_result_sha256": None}


def provenance_problems(prov: dict, proto, *, final: bool, result_sha=None) -> list:
    import authorization_interface as AI
    import executor_core as EC
    p = []
    if prov.get("executor_identity_sha256") != proto["executor_identity_sha256"]:
        p.append("executor identity differs from the protocol")
    if prov.get("science_preregistration_sha256") != proto["science_preregistration_sha256"]:
        p.append("science preregistration differs")
    if prov.get("host_runtime_contract_differences"):
        p.append("host runtime differs from the frozen contract")
    if prov.get("guard_policy") != "DENY":
        p.append("guard policy is not DENY")
    a = prov.get("authorization_state") or {}
    if a.get("protocol_authorization_active_exists") or a.get("countersignature_active_exists") or \
            a.get("template_EXECUTION_AUTHORIZED") is not False:
        p.append("an authorization exists")
    if prov.get("qualification_mode") == "FROZEN_QUALIFICATION" and prov.get("porcelain_before_run"):
        p.append("frozen qualification ran on a dirty worktree")
    if not isinstance(prov.get("git_commit"), str) or len(prov["git_commit"]) != 40:
        p.append("git commit")
    if final:
        if prov.get("qualification_result_sha256") != result_sha or not prov.get("finished_unix"):
            p.append("provenance does not name the qualification result")
    return p
