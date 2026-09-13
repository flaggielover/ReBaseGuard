"""SYNTHETIC adversarial acceptance of the CUSUM Aux5 production-provenance successor. NON-RESULT-BEARING.

Only synthetic workers run, in scratch roots outside the repository. Production objects are read or refused, never
created: the frozen certifier is not started, no production runtime root is created, no production countersignature
exists, and nothing is launched.

  python -B tests/prov_acceptance.py --scratch DIR --out RESULT.json [--only NAME ...]
"""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import time
import traceback
from pathlib import Path

os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
NS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NS / "code"))
import prov_schema as S                                                                  # noqa: E402
sys.path.insert(0, str(S.PRED_NS / "tests"))
import acceptance as PA                                                                  # noqa: E402  predecessor harness
import k4_input_attestation as K4A                                                       # noqa: E402
import prod_ledger as L                                                                  # noqa: E402
import prod_supervisor as PS                                                             # noqa: E402
import prov_entry as PENT                                                                # noqa: E402
import prov_integrity as PI                                                              # noqa: E402
import prov_ledger as PL                                                                 # noqa: E402
from prod_common import (K4_NS, ROOT, Refusal, atomic_write_bytes, atomic_write_json,    # noqa: E402
                         canonical, sha256_bytes, sha256_file)
from prod_spec import PRODUCTION_RUNTIME_ROOT as PREDECESSOR_ROOT                        # noqa: E402
from prod_sealer import hash_modules                                                     # noqa: E402
from prod_spec import QUALIFICATION_RECORDS                                              # noqa: E402
from prov_authorization import (build_authorization, load_authorization, synthetic_countersignature,  # noqa: E402
                                verify_countersignature, write_authorization)
from prov_envelope import build_envelope, envelope_rel, verify_pair                      # noqa: E402
from prov_spec import (AUTHORIZATION, AUTHORIZATION_HASH, COUNTERSIGNATURE, PRODUCTION_RUNTIME_ROOT,  # noqa: E402
                       load_checkpoint, synthetic_spec)
from prov_supervisor import synthetic_authz                                              # noqa: E402

PROV_SUPERVISOR = NS / "code/prov_supervisor.py"
check, expect_refusal, Fail, refused_with = PA.check, PA.expect_refusal, PA.Fail, PA.refused_with
attempts, count = PA.attempts, PA.count
TESTS: list = []


def test(*covers):
    def deco(fn):
        TESTS.append((fn.__name__, covers, fn))
        return fn
    return deco


def expect_any(codes, fn, *args, **kw):
    try:
        fn(*args, **kw)
    except Refusal as r:
        check(r.code in codes, f"expected one of {codes}, got {r.code}: {r.detail}")
        return r
    raise Fail(f"expected one of {codes}; nothing was refused")


class ProvCampaign(PA.Campaign):
    def __init__(self, scratch: Path, name: str, *, countersign: bool = True, **cfg):
        d = scratch / name
        base = {"authorization_path": str(d / "auth.json"), "authorization_hash_path": str(d / "auth.hash"),
                "countersignature_path": str(d / "countersignature.json"), "freeze_record_sha256": "0" * 64}
        base.update(cfg)
        super().__init__(scratch, name, **base)
        self.auth, self.auth_sha = self.authorize(countersign=countersign)

    @property
    def spec(self):
        return synthetic_spec(self.cfg)

    def authorize(self, *, countersign: bool, run_id: str | None = None):
        auth = build_authorization(self.spec, authorization_id=f"SYN-AUTH-{self.dir.name}",
                                   run_id=run_id or f"SYN-RUN-{self.dir.name}", host={})
        sha = write_authorization(auth, self.cfg["authorization_path"], self.cfg["authorization_hash_path"])
        if countersign:
            atomic_write_json(self.cfg["countersignature_path"],
                              synthetic_countersignature(auth, sha, freeze_record_sha256=self.cfg["freeze_record_sha256"]))
        return auth, sha

    def authz(self):
        origin = getattr(self, "origin", None)
        return origin.authz() if origin is not None else synthetic_authz(self.spec, self.cfg)

    def start(self, keep: bool = True):
        self.runs += 1
        log_path = self.dir / f"run{self.runs}.log"
        env = {k: v for k, v in os.environ.items() if k != PS.KEEPER_ENV}
        argv = [sys.executable, "-B", str(PROV_SUPERVISOR), "--synthetic-spec", self.cfg["config_path"]]
        with open(log_path, "wb") as log:
            p = subprocess.Popen(argv + (["--keep"] if keep else []), stdout=log, stderr=subprocess.STDOUT, env=env,
                                 start_new_session=True)
        p.log_path = log_path
        return p

    def view(self):
        return PI.ledger_view(self.spec)

    def pair(self, st, cell):
        (aid, a), = attempts(st, cell=cell, status="SEALED")
        return aid, self.root / a["record"], self.root / (a.get("provenance") or {}).get("envelope", envelope_rel(aid, cell))

    def variant(self, scratch: Path, name: str) -> "ProvCampaign":
        """A byte copy of this campaign's root, mutated by a test. It is verified with the ORIGINAL campaign's
        authorization (which binds the original runtime root); only the files are read from the copy."""
        v = object.__new__(ProvCampaign)
        v.dir = scratch / name
        v.dir.mkdir()
        v.cfg = dict(self.cfg, root=str(v.dir / "root"), config_path=str(v.dir / "cfg.json"))
        shutil.copytree(self.root, v.dir / "root")
        v.save()
        v.runs, v.origin = 0, self
        v.auth, v.auth_sha = self.auth, self.auth_sha
        return v


def forge(env_path: Path, out: Path, mutate) -> Path:
    env = json.loads(env_path.read_text())
    mutate(env)
    env.pop("binding_sha256", None)
    env["binding_sha256"] = sha256_bytes(canonical(env))          # an adversary who also recomputes the binding
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(env, indent=1, sort_keys=True) + "\n")
    return out


def completed(scratch, name, **cfg) -> ProvCampaign:
    c = ProvCampaign(scratch, name, **cfg)
    code, out = c.run(keep=True)
    check(code == PS.EXIT_COMPLETE, f"{name}: exit {code}: {out[-500:]}")
    c.settle()
    return c


def vp(c, st, entries, record, envelope, **kw):
    return verify_pair(spec=kw.pop("spec", c.spec), authz=kw.pop("authz", c.authz()), st=st, entries=entries,
                       record_path=record, envelope_path=envelope, **kw)


# ====================================================================== tests
@test("valid record + valid envelope -> accepted", "integrity audit", "K4 attestation recomputation")
def t01_valid_pair_accepted(scratch):
    c = completed(scratch, "t01", cells=list(range(6)))
    st, entries = c.view()
    for cell in range(6):
        aid, rec, env = c.pair(st, cell)
        got = vp(c, st, entries, rec, env)
        check(got["attempt"] == aid and env.stat().st_mode & 0o222 == 0, f"cell {cell} pair verified, envelope read-only")
    bound = [e for e in entries if e["event"] == S.PROVENANCE_EVENT]
    check(len(bound) == 6, "one PROVENANCE_BOUND entry per sealed cell")
    rep = PI.audit(c.spec, c.authz())
    check(rep["INTEGRITY_READY_FOR_ADJUDICATION"] and rep["A_completeness"]["verified_pairs"] == 6, f"audit {rep['issues']}")
    att = PI.build_k4_attestation(c.spec, c.authz(), rep)
    PI.verify_k4_attestation(att, c.spec, c.authz())
    env0 = json.loads(c.pair(st, 0)[2].read_text())
    check(env0["scientific_record"]["certifier_constant_flags_observed"] == S.CERTIFIER_CONSTANT_FLAGS,
          "the internal false flags are recorded verbatim as certifier constants")
    return {"pairs": 6, "audit_ready": True}


@test("record only -> refused", "envelope only -> refused")
def t02_record_only_and_envelope_only_refused(scratch):
    c = completed(scratch, "t02", cells=list(range(3)))
    st, entries = c.view()
    aid, rec, env = c.pair(st, 0)
    expect_refusal("PAIR_INCOMPLETE", vp, c, st, entries, rec, scratch / "t02" / "no-such-envelope.json")
    expect_refusal("PAIR_INCOMPLETE", vp, c, st, entries, scratch / "t02" / "no-such-record.json", env)
    for name, victim in (("t02_record_only", lambda v, s: v.pair(s, 1)[2]), ("t02_envelope_only", lambda v, s: v.pair(s, 1)[1])):
        v = c.variant(scratch, name)
        vst, _ = v.view()
        os.unlink(victim(v, vst))
        rep = PI.audit(v.spec, v.authz())
        check(not rep["INTEGRITY_READY_FOR_ADJUDICATION"] and rep["A_completeness"]["verified_pairs"] == 2,
              f"{name}: audit must refuse the half pair: {rep['issues']}")
        expect_refusal("ATTESTATION_REFUSED", PI.build_k4_attestation, v.spec, v.authz(), rep)
        lock, led = v.open_ledger()
        try:
            expect_refusal("EXPORT_REFUSED", PI.export_pairs, led, v.authz(), v.dir / "export")
        finally:
            lock.release()
    return {"record_only": "PAIR_INCOMPLETE", "envelope_only": "PAIR_INCOMPLETE"}


@test("qualification record + forged envelope -> refused")
def t03_qualification_record_with_forged_envelope(scratch):
    c = completed(scratch, "t03", cells=[0, 1])
    st, entries = c.view()
    _aid, _rec, env = c.pair(st, 0)
    qual = QUALIFICATION_RECORDS["318A"]
    qcopy = scratch / "t03" / "forged" / "aux5_CUSUM_318_256.json"
    qcopy.parent.mkdir(parents=True)
    shutil.copyfile(qual, qcopy)
    forged = forge(env, scratch / "t03" / "forged" / "envelope.json",
                   lambda e: e["scientific_record"].update(sha256=sha256_file(qual), path="attempts/x/aux5_CUSUM_318_256.json"))
    expect_refusal("QUALIFICATION_RECORD_REUSE", vp, c, st, entries, qcopy, forged)
    return {"refused": "QUALIFICATION_RECORD_REUSE"}


@test("swapped envelopes between cells -> refused")
def t04_swapped_envelopes(scratch):
    c = completed(scratch, "t04", cells=[0, 1, 2])
    st, entries = c.view()
    _a0, rec0, env0 = c.pair(st, 0)
    _a1, rec1, env1 = c.pair(st, 1)
    expect_refusal("RECORD_MISMATCH", vp, c, st, entries, rec0, env1)
    expect_refusal("RECORD_MISMATCH", vp, c, st, entries, rec1, env0)
    retarget = forge(env1, scratch / "t04" / "retarget.json",
                     lambda e: e["ledger"].update(attempt_id=_a0))              # claim cell 0's attempt
    expect_any({"CELL_MISMATCH", "PRODUCER_MISMATCH", "AUTHORIZATION_MISMATCH", "RECORD_MISMATCH"}, vp, c, st, entries,
               rec0, retarget)
    v = c.variant(scratch, "t04_disk_swap")
    vst, _ = v.view()
    p0, p1 = v.pair(vst, 0)[2], v.pair(vst, 1)[2]
    b0, b1 = p0.read_bytes(), p1.read_bytes()
    for p in (p0, p1):
        os.chmod(p, 0o644)
    p0.write_bytes(b1)
    p1.write_bytes(b0)
    rep = PI.audit(v.spec, v.authz())
    check(not rep["INTEGRITY_READY_FOR_ADJUDICATION"] and rep["issues"].get("B_pair_refused"), "on-disk swap refused")
    return {"swap": "RECORD_MISMATCH", "disk_swap_audit": sorted(rep["issues"])}


@test("changed scientific bytes -> refused")
def t05_changed_scientific_bytes(scratch):
    c = completed(scratch, "t05", cells=[0, 1])
    st, entries = c.view()
    _aid, rec, env = c.pair(st, 0)
    r = json.loads(rec.read_text())
    incidental = scratch / "t05" / "incidental.json"
    r2 = dict(r, wall_seconds=r["wall_seconds"] + 1.0)
    incidental.write_text(json.dumps(r2, indent=1, sort_keys=True) + "\n")
    expect_refusal("RECORD_MISMATCH", vp, c, st, entries, incidental, env)
    H, _ = hash_modules()
    r3 = copy.deepcopy(r)
    r3["m"]["1"]["M_R2"] = "999/7"
    r3["scientific_content_hash"] = H.record_scientific_hash(r3)
    scientific = scratch / "t05" / "scientific.json"
    scientific.write_text(json.dumps(r3, indent=1, sort_keys=True) + "\n")
    expect_refusal("RECORD_MISMATCH", vp, c, st, entries, scientific, env)
    v = c.variant(scratch, "t05_in_place")
    vst, _ = v.view()
    vrec = v.pair(vst, 0)[1]
    os.chmod(vrec, 0o644)
    vrec.write_bytes(scientific.read_bytes())
    rep = PI.audit(v.spec, v.authz())
    check(not rep["INTEGRITY_READY_FOR_ADJUDICATION"], "in-place scientific change refused by the audit")
    return {"incidental_edit": "RECORD_MISMATCH", "scientific_edit": "RECORD_MISMATCH", "audit_issues": sorted(rep["issues"])}


@test("wrong producer -> refused")
def t06_wrong_producer(scratch):
    c = completed(scratch, "t06", cells=[0, 1])
    st, entries = c.view()
    _aid, rec, env = c.pair(st, 0)
    forged = forge(env, scratch / "t06" / "forged.json",
                   lambda e: e["producer"].update(producer_identity_hash="1" * 64))
    expect_refusal("PRODUCER_MISMATCH", vp, c, st, entries, rec, forged)
    other = c.spec
    other.identity = dict(other.identity, producer_identity_hash="2" * 64)
    expect_refusal("PRODUCER_IDENTITY", vp, c, st, entries, rec, env, spec=other)
    return {"forged_envelope": "PRODUCER_MISMATCH", "foreign_producer_spec": "PRODUCER_IDENTITY"}


@test("wrong checkpoint -> refused")
def t07_wrong_checkpoint(scratch):
    c = completed(scratch, "t07", cells=[0, 1])
    st, entries = c.view()
    _aid, rec, env = c.pair(st, 0)
    forged = forge(env, scratch / "t07" / "forged.json",
                   lambda e: e["checkpoint"].update(production_checkpoint_sha256=S.PREDECESSOR["checkpoint_sha256"]))
    expect_refusal("CHECKPOINT_MISMATCH", vp, c, st, entries, rec, forged)
    other = synthetic_spec({**c.cfg, "checkpoint_sha256": "SYNTHETIC-another-checkpoint"})
    expect_refusal("INCOMPATIBLE_RUN_STATE", vp, c, st, entries, rec, env, spec=other)
    return {"forged_envelope": "CHECKPOINT_MISMATCH", "foreign_checkpoint": "INCOMPATIBLE_RUN_STATE"}


@test("wrong run authorization -> refused")
def t08_wrong_run_authorization(scratch):
    c = completed(scratch, "t08", cells=[0, 1])
    st, entries = c.view()
    _aid, rec, env = c.pair(st, 0)
    d = scratch / "t08" / "other_auth"
    d.mkdir()
    other = dict(c.cfg, authorization_path=str(d / "auth.json"), authorization_hash_path=str(d / "auth.hash"),
                 countersignature_path=str(d / "cs.json"))
    auth2 = build_authorization(c.spec, authorization_id="SYN-AUTH-OTHER", run_id="SYN-RUN-OTHER", host={})
    sha2 = write_authorization(auth2, other["authorization_path"], other["authorization_hash_path"])
    atomic_write_json(other["countersignature_path"], synthetic_countersignature(auth2, sha2, freeze_record_sha256=other["freeze_record_sha256"]))
    authz2 = synthetic_authz(c.spec, other)
    expect_refusal("NO_PRE_RESULT_AUTHORIZATION", vp, c, st, entries, rec, env, authz=authz2)
    forged = forge(env, scratch / "t08" / "forged.json", lambda e: e["authorization"].update(production_run_id="SYN-RUN-OTHER"))
    expect_refusal("AUTHORIZATION_MISMATCH", vp, c, st, entries, rec, forged)
    bad_cap = dict(auth2, cap=dict(auth2["cap"], cap_usec=auth2["cap"]["cap_usec"] * 2))
    write_authorization(bad_cap, other["authorization_path"], other["authorization_hash_path"])
    expect_refusal("AUTHORIZATION_MISMATCH", synthetic_authz, c.spec, other)
    Path(other["authorization_path"]).write_text(Path(other["authorization_path"]).read_text().replace("SYN-RUN-OTHER", "SYN-RUN-EDIT"))
    expect_refusal("AUTHORIZATION_INVALID", synthetic_authz, c.spec, other)
    cs_foreign = dict(synthetic_countersignature(auth2, sha2, freeze_record_sha256=other["freeze_record_sha256"]))
    atomic_write_json(c.dir / "foreign_cs.json", cs_foreign)
    expect_refusal("COUNTERSIGNATURE_INVALID", verify_countersignature, c.dir / "foreign_cs.json", auth=c.auth,
                   auth_sha=c.auth_sha, freeze_record_sha256=c.cfg["freeze_record_sha256"])
    return {"foreign_authorization": "NO_PRE_RESULT_AUTHORIZATION", "forged_section": "AUTHORIZATION_MISMATCH",
            "tampered_authorization": ["AUTHORIZATION_MISMATCH", "AUTHORIZATION_INVALID"],
            "countersignature_for_another_authorization": "COUNTERSIGNATURE_INVALID"}


@test("envelope created without pre-result authorization -> refused", "no retroactive authorization",
      "no self-authorization")
def t09_no_pre_result_authorization(scratch):
    c = ProvCampaign(scratch, "t09_uncountersigned", cells=[0, 1], countersign=False)
    code, out = c.run(keep=False)
    check(code == PS.EXIT_REFUSED and refused_with(out, "COUNTERSIGNATURE_MISSING") and not (c.root / "ledger.json").exists(),
          f"no ledger and no result without a countersignature (exit {code})")
    pre = ProvCampaign(scratch, "t09_unauthorized_ledger", cells=[0, 1])
    script = (f"import json, sys\nsys.path.insert(0, {str(NS / 'code')!r})\nimport prov_schema\nimport prod_supervisor as PS\n"
              f"from prov_spec import synthetic_spec\nspec = synthetic_spec(json.load(open({pre.cfg['config_path']!r})))\n"
              "raise SystemExit(PS.Supervisor(spec).run())\n")
    r = subprocess.run([sys.executable, "-B", "-c", script], capture_output=True, text=True, timeout=300)
    check(r.returncode == PS.EXIT_COMPLETE, f"unauthorized (predecessor-style) ledger produced: {r.stdout[-300:]}")
    st, entries, _t, _rel = L.Ledger.read_and_relate(L.Paths(pre.root))
    (aid, a), = attempts(st, cell=0, status="SEALED")
    rec = pre.root / a["record"]
    env = build_envelope(spec=pre.spec, authz=pre.authz(), st=st, entries=entries, aid=aid, record_bytes=rec.read_bytes())
    envp = pre.dir / "after_the_fact_envelope.json"
    envp.write_text(json.dumps(env, indent=1, sort_keys=True) + "\n")
    expect_refusal("NO_PRE_RESULT_AUTHORIZATION", vp, pre, st, entries, rec, envp, require_bound=False)
    code2, out2 = pre.run(keep=False)
    check(code2 == PS.EXIT_REFUSED and refused_with(out2, "NO_PRE_RESULT_AUTHORIZATION"),
          "the successor supervisor refuses to adopt a ledger born without the authorization")
    PA.forge_next_state(pre.root, lambda s: s.__setitem__("production_authorization", pre.authz().block))
    st2, entries2, _t2, _r2 = L.Ledger.read_and_relate(L.Paths(pre.root))
    expect_refusal("NO_PRE_RESULT_AUTHORIZATION", vp, pre, st2, entries2, rec, envp, require_bound=False)
    prod_auth, prod_sha = load_authorization(AUTHORIZATION, AUTHORIZATION_HASH)
    expect_refusal("SELF_AUTHORIZATION_REFUSED", synthetic_countersignature, prod_auth, prod_sha, freeze_record_sha256="0" * 64)
    return {"uncountersigned": "COUNTERSIGNATURE_MISSING, no ledger", "after_the_fact": "NO_PRE_RESULT_AUTHORIZATION",
            "retroactive_block_insertion": "NO_PRE_RESULT_AUTHORIZATION", "production_self_countersign": "SELF_AUTHORIZATION_REFUSED"}


@test("duplicate envelope -> refused")
def t10_duplicate_envelope(scratch):
    c = completed(scratch, "t10", cells=[0, 1])
    st, entries = c.view()
    aid, rec, env = c.pair(st, 0)
    s = copy.deepcopy(st)
    expect_refusal("DUPLICATE_ENVELOPE", PL.op_bind_provenance, s, aid, envelope_rel(aid, 0), "3" * 64)
    other = forge(env, scratch / "t10" / "second.json", lambda e: e.update(record_flag_semantics="second envelope"))
    expect_refusal("ENVELOPE_MISMATCH", vp, c, st, entries, rec, other)
    regen = forge(env, scratch / "t10" / "regen.json", lambda e: e["host_runtime"].update(pid=1))
    expect_refusal("HOST_RUNTIME_MISMATCH", vp, c, st, entries, rec, regen)
    v = c.variant(scratch, "t10_stray")
    vst, _ = v.view()
    va, _vr, venv = v.pair(vst, 0)
    stray = v.root / "provenance" / "A99999-C0000" / "CUSUM_0000.envelope.json"
    stray.parent.mkdir(parents=True)
    shutil.copyfile(venv, stray)
    rep = PI.audit(v.spec, v.authz())
    check(not rep["INTEGRITY_READY_FOR_ADJUDICATION"] and rep["issues"].get("C_unbound_envelope_files"), "stray duplicate refused")
    return {"rebind": "DUPLICATE_ENVELOPE", "second_envelope": "ENVELOPE_MISMATCH", "stray_file": "C_unbound_envelope_files"}


@test("stale/replayed envelope -> refused")
def t11_stale_and_replayed_envelope(scratch):
    c = ProvCampaign(scratch, "t11", cells=[0, 1], cores=[0], plan={"0": ["hang", "ok"]})
    p = c.start(keep=True)
    st0 = c.wait_for(lambda s: attempts(s, cell=0, status="RUNNING"), what="cell 0 running")
    os.kill(attempts(st0, cell=0, status="RUNNING")[0][1]["pid"], signal.SIGKILL)
    code, _ = c.finish(p)
    check(code == PS.EXIT_COMPLETE, f"exit {code}")
    c.settle()
    st, entries = c.view()
    (torn_aid, _t), (sealed_aid, _s) = attempts(st, cell=0)
    _aid, rec, env = c.pair(st, 0)
    stale = forge(env, scratch / "t11" / "stale.json", lambda e: e["ledger"].update(attempt_id=torn_aid))
    expect_refusal("LEDGER_LINKAGE", vp, c, st, entries, rec, stale)
    twin = completed(scratch, "t11_twin", cells=[0, 1], cores=[0])
    tst, _ = twin.view()
    _ta, _trec, tenv = twin.pair(tst, 0)
    expect_any({"AUTHORIZATION_MISMATCH", "LEDGER_LINKAGE", "RECORD_MISMATCH"}, vp, c, st, entries, rec, tenv)
    return {"stale_torn_attempt": "LEDGER_LINKAGE", "replay_from_another_run": "refused"}


@test("corrupted ledger linkage -> refused")
def t12_corrupted_ledger_linkage(scratch):
    c = completed(scratch, "t12", cells=[0, 1])
    v = c.variant(scratch, "t12_forged_binding")
    vst, _ = v.view()
    aid = v.pair(vst, 0)[0]
    PA.forge_next_state(v.root, lambda s: s["attempts"][aid]["provenance"].update(envelope_sha256="4" * 64))
    st, entries = v.view()
    _a, rec, env = v.pair(st, 0)
    expect_refusal("ENVELOPE_NOT_BOUND_TO_LEDGER", vp, v, st, entries, rec, env)
    v2 = c.variant(scratch, "t12_forged_seal")
    PA.forge_next_state(v2.root, lambda s: s["attempts"][aid]["seal"].update(record_sha256="5" * 64))
    st2, entries2 = v2.view()
    _a2, rec2, env2 = v2.pair(st2, 0)
    expect_refusal("RECORD_MISMATCH", vp, v2, st2, entries2, rec2, env2)
    v3 = c.variant(scratch, "t12_broken_chain")
    j = v3.root / "journal.jsonl"
    j.write_text(j.read_text().replace('"event": "SEALED"', '"event": "SEALED_X"', 1))
    expect_refusal("JOURNAL_CORRUPT", v3.view)
    v4 = c.variant(scratch, "t12_naive_edit")
    led = json.loads((v4.root / "ledger.json").read_text())
    led["attempts"][aid]["seal"]["record_sha256"] = "6" * 64
    atomic_write_json(v4.root / "ledger.json", led)
    expect_refusal("LEDGER_ROLLBACK_OR_MUTATION", v4.view)
    return {"forged_binding": "ENVELOPE_NOT_BOUND_TO_LEDGER", "forged_seal": "RECORD_MISMATCH",
            "broken_chain": "JOURNAL_CORRUPT", "naive_edit": "LEDGER_ROLLBACK_OR_MUTATION"}


@test("atomic binding: crash between SEALED and PROVENANCE_BOUND", "crash recovery")
def t13_crash_between_seal_and_binding(scratch):
    c = ProvCampaign(scratch, "t13", cells=[0, 1], cores=[0])
    script = (f"import json, os, sys\nsys.path.insert(0, {str(NS / 'code')!r})\nimport prov_schema\nimport prod_supervisor as PS\n"
              "import prov_supervisor as PV\n"
              f"cfg = json.load(open({c.cfg['config_path']!r}))\nspec = PV.synthetic_spec(cfg)\n"
              "class Crash(PV.ProvenanceSupervisor):\n"
              "    def _finalize(self, led, aid, status, ru):\n"
              "        PS.Supervisor._finalize(self, led, aid, status, ru)\n"
              "        if led.state['attempts'][aid]['status'] == 'SEALED':\n            os._exit(99)\n"
              "raise SystemExit(Crash(spec, authz_loader=lambda: PV.synthetic_authz(spec, cfg)).run())\n")
    r = subprocess.run([sys.executable, "-B", "-c", script], capture_output=True, text=True, timeout=300)
    check(r.returncode == 99, f"crash harness exit {r.returncode}: {r.stderr[-300:]}")
    st = c.state()
    unbound = PL.unbound_sealed(st)
    check(len(unbound) == 1, f"one sealed attempt left unbound: {unbound}")
    code, out = c.run(keep=True)
    check(code == PS.EXIT_COMPLETE, f"exit {code}: {out[-400:]}")
    c.settle()
    rep = PI.audit(c.spec, c.authz())
    check(rep["INTEGRITY_READY_FOR_ADJUDICATION"], f"recovered binding verifies: {rep['issues']}")
    return {"unbound_after_crash": unbound, "bound_on_restart": True}


@test("SIGKILL", "crash recovery", "worker death after durable seal is recoverable")
def t14_supervisor_sigkill_recovered_envelope(scratch):
    c = ProvCampaign(scratch, "t14", cells=[0, 1, 2], cores=[0, 2], plan={"0": ["write_then_hang"]})
    p = c.start(keep=True)
    st = c.wait_for(lambda s: attempts(s, cell=0, status="RUNNING"), what="cell 0 running")
    record = c.root / attempts(st, cell=0)[0][1]["record"]
    deadline = time.monotonic() + 30
    while not record.exists() and time.monotonic() < deadline:
        time.sleep(0.05)
    os.kill(json.loads((c.root / "campaign.owner.json").read_text())["pid"], signal.SIGKILL)
    c.finish(p)
    code, _ = c.run(keep=True)
    check(code == PS.EXIT_COMPLETE, f"exit {code}")
    c.settle()
    st2, entries2 = c.view()
    aid, rec, env = c.pair(st2, 0)
    got = vp(c, st2, entries2, rec, env)
    e = json.loads(env.read_text())
    check(st2["attempts"][aid]["seal"]["recovered"] is True and e["cpu_accounting"]["charge_evidence"] == "REAPER_RUSAGE"
          and e["ledger"]["seal"]["event"] == "RECONCILED_SEALED", "recovered seal carries a valid envelope")
    return {"recovered_pair": got["attempt"]}


@test("record flags must be the certifier constants")
def t15_record_flags(scratch):
    out = {}
    for behaviour in ("flags_true", "no_flags"):
        c = ProvCampaign(scratch, f"t15_{behaviour}", cells=[0, 1], cores=[0], plan={"0": [behaviour]})
        code, log = c.run(keep=False)
        check(code == PS.EXIT_REFUSED and refused_with(log, "RECORD_FLAGS"), f"{behaviour}: exit {code}")
        check(PL.unbound_sealed(c.state()), f"{behaviour}: the record is never bound as production")
        rep = PI.audit(c.spec, c.authz())
        check(not rep["INTEGRITY_READY_FOR_ADJUDICATION"], f"{behaviour}: audit refuses")
        out[behaviour] = "RECORD_FLAGS"
    return out


@test("lifecycle under the provenance layer: drain, failure halt, cap exhaustion")
def t16_lifecycle_regression(scratch):
    c = ProvCampaign(scratch, "t16_drain", cells=list(range(6)), cores=[0, 2], plan={str(i): ["slow"] for i in range(6)},
                     slow_s=1.5)
    p = c.start(keep=True)
    c.wait_for(lambda s: len(attempts(s, status="RUNNING")) == 2, what="two running")
    os.kill(p.pid, signal.SIGTERM)
    check(c.finish(p)[0] == PS.EXIT_DRAINED, "drain")
    st = c.state()
    check(all(a.get("provenance") for _, a in attempts(st, status="SEALED")) and count(st, "SEALED") == 2,
          "drained work sealed and bound")
    check(c.run(keep=True)[0] == PS.EXIT_COMPLETE, "resume")
    f = ProvCampaign(scratch, "t16_fail", cells=list(range(4)), cores=[0], plan={"2": ["fail"]})
    check(f.run(keep=True)[0] == PS.EXIT_HALTED, "failure halts")
    fst = f.state()
    check(all(a.get("provenance") for _, a in attempts(fst, status="SEALED")) and count(fst, "SEALED") == 2, "bound before halt")
    b = ProvCampaign(scratch, "t16_budget", cells=list(range(10)), cores=[0], cap_usec=4_000_000,
                     reservation_usec=1_000_000, burn_s=0.3)
    check(b.run(keep=True)[0] == PS.EXIT_BUDGET, "budget exhaustion")
    bst = b.state()
    check(bst["disposition"] == "INCOMPLETE_BUDGET_EXHAUSTED" and not PL.unbound_sealed(bst), "exhausted, all sealed bound")
    return {"drain": "PASS", "halt": "PASS", "budget": count(bst, "SEALED")}


@test("full 326-cell synthetic ledger of verified pairs", "K4 consumer requires the pair-verified attestation",
      "predecessor-style attestation refused")
def t17_full_campaign_pairs_and_k4(scratch):
    c = ProvCampaign(scratch, "t17", cells=list(range(326)), cores=[0, 2, 4, 6], burn_s=0.02, heartbeat_s=1.0)
    code, out = c.run(keep=True, timeout=2400)
    check(code == PS.EXIT_COMPLETE, f"exit {code}: {out[-400:]}")
    c.settle()
    authz = c.authz()
    rep = PI.audit(c.spec, authz)
    check(rep["INTEGRITY_READY_FOR_ADJUDICATION"] and rep["A_completeness"]["verified_pairs"] == 326, f"{rep['issues']}")
    att = PI.build_k4_attestation(c.spec, authz, rep)
    att_path = c.dir / "attestation.json"
    atomic_write_json(att_path, att)
    PI.verify_k4_attestation(att, c.spec, authz)
    lock, led = c.open_ledger()
    try:
        manifest = PI.export_pairs(led, authz, c.dir / "export")
    finally:
        lock.release()
    records = [json.loads(p.read_text()) for p in sorted((c.dir / "export/k4_records").glob("*.json"))]
    check(len(records) == 326 and len(manifest["pairs"]) == 326, "exported only verified pairs")
    cp, _sha = load_checkpoint()
    path = K4_NS / "code/k4_assembly.py"
    check(sha256_file(path) == cp["k4"]["k4_assembly_sha256"], "frozen k4_assembly.py")
    ms = importlib.util.spec_from_file_location("k4_assembly_frozen", path)
    k4 = importlib.util.module_from_spec(ms)
    ms.loader.exec_module(k4)
    k4.check_cusum_attestation(att_path, records)                    # integrity gate only; assemble() is never called
    tampered = copy.deepcopy(att)
    tampered["production_provenance"]["pairs"].pop("0")
    expect_refusal("ATTESTATION_REFUSED", PI.verify_k4_attestation, tampered, c.spec, authz)
    legacy = K4A.build_integrity_attestation(c.spec, c.state(), checkpoint_sha256=c.spec.checkpoint_sha256)
    expect_refusal("ATTESTATION_REFUSED", PI.verify_k4_attestation, legacy, c.spec, authz)
    return {"pairs": 326, "k4_gate": "accepted (pair-verified attestation)", "legacy_attestation": "refused by recomputation",
            "k4_assembly_run": False}


@test("production isolation and no self-authorization", "entrypoint fails closed before the countersignature")
def t18_production_isolation(scratch):
    check(not PRODUCTION_RUNTIME_ROOT.exists(), "successor production runtime root absent")
    proot = Path(S.PREDECESSOR["runtime_root"])
    check((proot / S.FENCE_MARKER).exists() and not (proot / "ledger.json").exists(), "predecessor fenced, never launched")
    c = ProvCampaign(scratch, "t18", cells=[0], cores=[0])
    for root in (PRODUCTION_RUNTIME_ROOT / "x", PREDECESSOR_ROOT / "x"):
        expect_refusal("SYNTHETIC_PRODUCTION_MIX", synthetic_spec, {**c.cfg, "root": str(root)})
    check(not COUNTERSIGNATURE.exists(), "no production countersignature exists")
    expect_refusal("COUNTERSIGNATURE_MISSING", PENT.production_authz)
    check(PENT.main(["launch", "--confirm-checkpoint-sha256", "0" * 64, "--confirm-authorization-sha256", "0" * 64])
          == PS.EXIT_REFUSED, "launch refuses wrong confirmations")
    check(not PRODUCTION_RUNTIME_ROOT.exists(), "still absent")
    return {"production_root_absent": True, "countersignature": "absent (reviewer-only)"}


@test("entrypoint preflight before freeze")
def t19_preflight_before_freeze(scratch):
    rep = PENT.preflight()
    status = {c["check"]: c["status"] for c in rep["checks"]}
    expected = {"P01_checkpoint_and_freeze", "P06_run_authorization", "P07_independent_countersignature",
                "P08_synthetic_acceptance"}
    failed = {k for k, v in status.items() if v == "FAIL"}
    check(not rep["ready"] and failed == expected,
          f"only freeze/countersignature-dependent checks may fail: {[c for c in rep['checks'] if c['status'] == 'FAIL']}")
    p07 = next(c for c in rep["checks"] if c["check"] == "P07_independent_countersignature")
    check(p07["code"] == "COUNTERSIGNATURE_MISSING", f"P07 {p07}")
    return {"status": status}


# ====================================================================== driver
def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args(argv)
    scratch = Path(a.scratch).resolve()
    scratch.mkdir(parents=True, exist_ok=False)
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    try:
        _cp, sha = load_checkpoint()
        bound_ok = True
    except Refusal as r:
        sha, bound_ok = f"UNAVAILABLE: {r}", False
    auth_sha = sha256_file(AUTHORIZATION) if AUTHORIZATION.exists() else None
    roots_before = (not PRODUCTION_RUNTIME_ROOT.exists(), not (Path(S.PREDECESSOR["runtime_root"]) / "ledger.json").exists())
    results, coverage = {}, {}
    for name, covers, fn in TESTS:
        if a.only and name not in a.only:
            continue
        t0 = time.monotonic()
        try:
            results[name] = {"status": "PASS", "seconds": round(time.monotonic() - t0, 1), "details": fn(scratch)}
            results[name]["seconds"] = round(time.monotonic() - t0, 1)
        except Exception as exc:                                        # noqa: BLE001
            results[name] = {"status": "FAIL", "seconds": round(time.monotonic() - t0, 1),
                             "error": f"{type(exc).__name__}: {exc}", "trace": traceback.format_exc()[-1500:]}
        for cv in covers:
            coverage.setdefault(cv, []).append(name)
        print(f"{results[name]['status']:4s} {results[name]['seconds']:7.1f}s  {name}"
              + ("" if results[name]["status"] == "PASS" else f"  -- {results[name]['error'][:300]}"), flush=True)
    try:
        _cp2, sha_after = load_checkpoint()
    except Refusal as r:
        sha_after = f"UNAVAILABLE: {r}"
    roots_after = (not PRODUCTION_RUNTIME_ROOT.exists(), not (Path(S.PREDECESSOR["runtime_root"]) / "ledger.json").exists())
    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    ok = (bound_ok and sha == sha_after and all(roots_before) and all(roots_after) and not a.only
          and not COUNTERSIGNATURE.exists() and all(r["status"] == "PASS" for r in results.values()))
    doc = {"schema": S.ACCEPTANCE_SCHEMA, "PROVENANCE_SYNTHETIC_ACCEPTANCE": "PASS" if ok else "FAIL",
           "provenance_checkpoint_sha256": sha, "checkpoint_unchanged_during_run": sha == sha_after,
           "run_authorization_sha256": auth_sha, "bound_sources_verified": bound_ok, "host_name": socket.gethostname(),
           "git_head": head, "python": sys.version.split()[0], "started_utc": started,
           "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "non_result_bearing": True,
           "frozen_certifier_started": False, "production_launched": False,
           "production_countersignature_present": COUNTERSIGNATURE.exists(),
           "production_roots_untouched": all(roots_before) and all(roots_after),
           "scratch": str(scratch), "tests": results, "coverage": coverage}
    atomic_write_json(a.out, doc)
    print(json.dumps({"PROVENANCE_SYNTHETIC_ACCEPTANCE": doc["PROVENANCE_SYNTHETIC_ACCEPTANCE"],
                      "passed": sum(r["status"] == "PASS" for r in results.values()), "total": len(results)}))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
