"""THE production entrypoint of the CUSUM Aux5 provenance successor. NON-CERTIFYING. Fails closed.

  python prov_entry.py preflight                      read-only; READY or NOT_READY (exit 0 / 30)
  python prov_entry.py launch --confirm-checkpoint-sha256 SHA --confirm-authorization-sha256 SHA
  python prov_entry.py status | settle | audit --out F | export --out DIR | attest --out F

READY requires every check to PASS. Nothing here can create the independent countersignature, so this tooling
cannot authorize production by itself.

  P01 checkpoint_and_freeze           PROVENANCE_CHECKPOINT sha == hash file == FREEZE_RECORD
  P02 bound_sources                   every bound source (successor, predecessor, frozen inputs) unchanged
  P03 predecessor_frozen_and_fenced   predecessor preflight: C01-C12, C14 PASS; C13 refused by the on-host fence;
                                      the predecessor runtime root holds the fence and no ledger (never launched)
  P04 inherited_sections_unchanged    producer/runtime/host/workers/universe/geometry/precision/hash/cap/qualification/K4
                                      sections equal the predecessor checkpoint's
  P05 provenance_schemas              ENVELOPE_SCHEMA.json == the code's schema document; checkpoint schema ids
  P06 run_authorization               file == hash; recomputes from the production spec; committed at the freeze
                                      record's authorization commit (an ancestor of HEAD) and unchanged since
  P07 independent_countersignature    present, APPROVED, binds authorization + freeze record, committed in git
  P08 synthetic_acceptance            bound by the freeze record, PASS, same checkpoint, bound host
  P09 run_state                       no live supervisor; root FRESH or a ledger born under this authorization;
                                      no DRAIN, halt or terminal disposition
  P10 host_idle                       no certifier, supervisor or synthetic worker of either generation
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import prov_schema as S                                                                # noqa: E402
import prod_entry as PE                                                                # noqa: E402
import prod_ledger as L                                                                # noqa: E402
import prov_integrity as PI                                                            # noqa: E402
from prod_common import (ROOT, Refusal, atomic_write_json, canonical, processes_matching,  # noqa: E402
                         sha256_bytes, sha256_file)
from prod_spec import load_frozen_checkpoint as load_predecessor_checkpoint           # noqa: E402
from prod_supervisor import EXIT_REFUSED, keep                                         # noqa: E402
from prov_authorization import load_authorization, load_authz, verify_authorization, verify_countersignature  # noqa: E402
from prov_spec import (AUTHORIZATION, AUTHORIZATION_HASH, CHECKPOINT, CHECKPOINT_HASH,  # noqa: E402
                       COUNTERSIGNATURE, FREEZE_RECORD, load_checkpoint, production_spec)
from prov_supervisor import ProvenanceSupervisor                                       # noqa: E402

INHERITED_SECTIONS = ("producer", "runtime_contract", "host", "workers", "scientific_universe", "geometry", "precision",
                      "scientific_hash", "cost_cap", "qualification", "k4", "checkout_path")
FREEZE_STATUS = "FROZEN_PENDING_INDEPENDENT_COUNTERSIGNATURE"
MARKERS = PE.PROCESS_MARKERS + ("prov_entry.py launch", "prov_entry.py _supervise", "prov_supervisor.py",
                                "prov_synthetic_worker.py")
ENVELOPE_SCHEMA_FILE = S.NS / "config/ENVELOPE_SCHEMA.json"


def _git(*args) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True)


def freeze_record_sha256() -> str:
    return sha256_file(FREEZE_RECORD) if FREEZE_RECORD.exists() else "FREEZE_RECORD_ABSENT"


def production_authz():
    spec, _cp = production_spec()
    return load_authz(spec, auth_path=AUTHORIZATION, hash_path=AUTHORIZATION_HASH, cs_path=COUNTERSIGNATURE,
                      freeze_record_sha256=freeze_record_sha256())


def preflight(*, overrides=None, in_supervisor: bool = False) -> dict:
    ov = overrides or {}
    checks, ctx = [], {"probe_cpu_usec": 0}
    raw = CHECKPOINT.read_bytes() if CHECKPOINT.exists() else b""
    sha = sha256_bytes(raw)
    cp = json.loads(raw) if raw else {}

    def check(name, fn):
        try:
            checks.append({"check": name, "status": "PASS", "detail": fn()})
        except Refusal as r:
            checks.append({"check": name, "status": "FAIL", "code": r.code, "detail": r.detail})
        except Exception as exc:                                        # noqa: BLE001  anything unexpected FAILS
            checks.append({"check": name, "status": "FAIL", "code": "UNEXPECTED", "detail": repr(exc)[:400]})

    def freeze():
        if not FREEZE_RECORD.exists():
            raise Refusal("NOT_FROZEN", "config/FREEZE_RECORD.json is absent")
        return json.loads(FREEZE_RECORD.read_text())

    def p01():
        if not raw:
            raise Refusal("CHECKPOINT_MISSING", str(CHECKPOINT))
        load_checkpoint()
        fr = freeze()
        if (fr.get("schema") != S.FREEZE_SCHEMA or fr.get("status") != FREEZE_STATUS
                or fr.get("provenance_checkpoint_sha256") != sha or fr.get("production_launched") is not False):
            raise Refusal("FREEZE_RECORD", "the freeze record does not bind this checkpoint as frozen and unlaunched")
        return {"checkpoint_sha256": sha}

    def p02():
        drift = sorted(r for r, h in cp["bound_sources"].items() if not (ROOT / r).exists() or sha256_file(ROOT / r) != h)
        if drift:
            raise Refusal("BOUND_SOURCE_DRIFT", f"{len(drift)} bound sources changed: {drift[:6]}")
        return {"bound_sources": len(cp["bound_sources"])}

    def p03():
        rep = ov.get("predecessor_preflight") or PE.preflight(in_supervisor=in_supervisor)
        ctx["probe_cpu_usec"] += rep.get("probe_cpu_usec", 0)
        status = {c["check"]: c for c in rep["checks"]}
        bad = [k for k, c in status.items() if k != "C13_run_state" and c["status"] != "PASS"]
        if bad:
            raise Refusal("PREDECESSOR_FROZEN_INPUTS", f"predecessor checks failed: {[(k, status[k].get('code')) for k in bad]}")
        c13 = status.get("C13_run_state", {})
        if c13.get("status") != "FAIL" or c13.get("code") not in ("DRAIN_PRESENT", "STALE_INCOMPATIBLE_RUN_STATE"):
            raise Refusal("PREDECESSOR_NOT_FENCED", "the blocked predecessor checkpoint is still launchable on this host")
        proot = Path(S.PREDECESSOR["runtime_root"])
        if not (proot / S.FENCE_MARKER).exists() or (proot / "ledger.json").exists() or (proot / "journal.jsonl").exists():
            raise Refusal("PREDECESSOR_NOT_FENCED", f"{proot} must hold the fence marker and no ledger")
        return {"predecessor_checks_pass": len(status) - 1, "C13": c13.get("code"), "predecessor_ledger": "absent"}

    def p04():
        pred, psha = load_predecessor_checkpoint()
        if psha != S.PREDECESSOR["checkpoint_sha256"] or cp["predecessor"]["checkpoint_sha256"] != psha:
            raise Refusal("PREDECESSOR_IDENTITY", "predecessor checkpoint sha256 differs")
        diff = [k for k in INHERITED_SECTIONS if cp.get(k) != pred.get(k)]
        if diff:
            raise Refusal("INHERITED_SECTION_CHANGED", f"sections differ from the predecessor: {diff}")
        for k, want in (("PREDECESSOR_CHECKPOINT", S.PREDECESSOR["status"]), ("SCIENTIFIC_PRODUCER", "UNCHANGED_AUX5"),
                        ("NEW_SCIENTIFIC_COMPUTE", "NONE")):
            if cp.get(k) != want:
                raise Refusal("CHECKPOINT_STATEMENT", f"{k} is {cp.get(k)!r}")
        return {"inherited_sections": list(INHERITED_SECTIONS)}

    def p05():
        doc = json.loads(ENVELOPE_SCHEMA_FILE.read_text())
        if canonical(doc) != canonical(S.envelope_schema_document()):
            raise Refusal("PROVENANCE_SCHEMA", "ENVELOPE_SCHEMA.json differs from the code's schema document")
        a = cp["authority"]
        if (a["envelope"]["schema"] != S.ENVELOPE_SCHEMA or a["envelope"]["schema_file_sha256"] != sha256_file(ENVELOPE_SCHEMA_FILE)
                or a["run_authorization"]["schema"] != S.AUTH_SCHEMA or a["composite_rule"] != S.COMPOSITE_RULE):
            raise Refusal("PROVENANCE_SCHEMA", "checkpoint authority section differs from the code")
        return {"envelope_schema": S.ENVELOPE_SCHEMA}

    def p06():
        auth, asha = load_authorization(AUTHORIZATION, AUTHORIZATION_HASH)
        spec, _cp = production_spec()
        verify_authorization(auth, spec)
        fr = freeze()
        ra = fr.get("run_authorization") or {}
        if ra.get("sha256") != asha:
            raise Refusal("AUTHORIZATION_NOT_FROZEN", "the freeze record does not bind this authorization")
        commit = ra.get("commit", "")
        if _git("merge-base", "--is-ancestor", commit, "HEAD").returncode != 0:
            raise Refusal("AUTHORIZATION_NOT_PRE_RESULT", f"authorization commit {commit[:12]} is not an ancestor of HEAD")
        rel = str(AUTHORIZATION.relative_to(ROOT))
        shown = _git("show", f"{commit}:{rel}")
        if shown.returncode != 0 or sha256_bytes(shown.stdout) != asha:
            raise Refusal("AUTHORIZATION_NOT_PRE_RESULT", "the authorization differs from the one committed at its commit")
        return {"authorization_sha256": asha, "authorization_id": auth["authorization_id"],
                "production_run_id": auth["production_run_id"], "commit": commit}

    def p07():
        auth, asha = load_authorization(AUTHORIZATION, AUTHORIZATION_HASH)
        cs, cs_sha = verify_countersignature(COUNTERSIGNATURE, auth=auth, auth_sha=asha,
                                             freeze_record_sha256=freeze_record_sha256())
        if _git("ls-files", "--error-unmatch", str(COUNTERSIGNATURE.relative_to(ROOT))).returncode != 0:
            raise Refusal("COUNTERSIGNATURE_INVALID", "the countersignature is not committed")
        return {"countersignature_sha256": cs_sha, "reviewer": cs["reviewer"]}

    def p08():
        acc = freeze()["synthetic_acceptance"]
        path = ROOT / acc["path"]
        if sha256_file(path) != acc["sha256"]:
            raise Refusal("ACCEPTANCE", "acceptance result bytes differ from the freeze record")
        res = json.loads(path.read_text())
        if (res.get("schema") != S.ACCEPTANCE_SCHEMA or res.get("PROVENANCE_SYNTHETIC_ACCEPTANCE") != "PASS"
                or res.get("provenance_checkpoint_sha256") != sha or res.get("host_name") != cp["host"]["bound_facts"]["host_name"]):
            raise Refusal("ACCEPTANCE", "acceptance result is not a PASS for this checkpoint on the bound host")
        return {"tests": len(res.get("tests", {})), "verdict": "PASS"}

    def p09():
        spec, _cp = production_spec()
        if not in_supervisor and L.CampaignLock(spec.root).probe() == "LIVE":
            raise Refusal("ANOTHER_SUPERVISOR_LIVE", "a supervisor holds the campaign lock")
        if L.Paths(spec.root).drain.exists():
            raise Refusal("DRAIN_PRESENT", "a DRAIN marker is present")
        view = L.Ledger.inspect(spec)
        if view["relation"] != "FRESH":
            _auth, asha = load_authorization(AUTHORIZATION, AUTHORIZATION_HASH)
            st = json.loads(L.Paths(spec.root).ledger.read_text())
            if (st.get("production_authorization") or {}).get("authorization_sha256") != asha:
                raise Refusal("NO_PRE_RESULT_AUTHORIZATION", "the existing ledger was not born under this authorization")
            if view["halt"] is not None:
                raise Refusal("HALTED", f"ledger halted: {view['halt']}")
            if view["disposition"] in L.TERMINAL:
                raise Refusal("TERMINAL_DISPOSITION", view["disposition"])
        return view

    def p10():
        skip = {os.getpid()} | ({os.getppid()} if in_supervisor else set())
        found = [p for p in processes_matching(MARKERS) if p["pid"] not in skip]
        if found:
            raise Refusal("HOST_NOT_IDLE", f"{found[:4]}")
        return {"foreign_processes": 0}

    for name, fn in (("P01_checkpoint_and_freeze", p01), ("P02_bound_sources", p02),
                     ("P03_predecessor_frozen_and_fenced", p03), ("P04_inherited_sections_unchanged", p04),
                     ("P05_provenance_schemas", p05), ("P06_run_authorization", p06),
                     ("P07_independent_countersignature", p07), ("P08_synthetic_acceptance", p08),
                     ("P09_run_state", p09), ("P10_host_idle", p10)):
        check(name, fn)
    ready = all(c["status"] == "PASS" for c in checks)
    return {"schema": S.PREFLIGHT_SCHEMA, "ready": ready, "provenance_checkpoint_sha256": sha if raw else None,
            "checks": checks, "probe_cpu_usec": ctx["probe_cpu_usec"], "production_launched": False,
            "CUSUM_AUX5_PROVENANCE_ENTRYPOINT": "READY" if ready else "NOT_READY"}


def print_report(rep: dict) -> None:
    for c in rep["checks"]:
        tail = "" if c["status"] == "PASS" else f"   [{c['code']}] {str(c['detail'])[:300]}"
        print(f"  {c['status']:4s}  {c['check']}{tail}")
    print(f"CUSUM_AUX5_PROVENANCE_ENTRYPOINT = {rep['CUSUM_AUX5_PROVENANCE_ENTRYPOINT']}   "
          f"checkpoint {rep['provenance_checkpoint_sha256']}")
    if not rep["ready"]:
        print("fail closed: nothing may be launched")


def _supervisor_preflight():
    rep = preflight(in_supervisor=True)
    print_report(rep)
    return rep["ready"], rep, rep["probe_cpu_usec"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="CUSUM Aux5 provenance-successor production entrypoint")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("preflight")
    p = sub.add_parser("launch")
    p.add_argument("--confirm-checkpoint-sha256", required=True)
    p.add_argument("--confirm-authorization-sha256", required=True)
    sub.add_parser("_supervise", help=argparse.SUPPRESS)
    sub.add_parser("status")
    sub.add_parser("settle")
    for name in ("audit", "export", "attest"):
        sub.add_parser(name).add_argument("--out", required=True)
    a = ap.parse_args(argv)
    try:
        if a.cmd == "preflight":
            rep = preflight()
            print_report(rep)
            return 0 if rep["ready"] else EXIT_REFUSED
        if a.cmd == "launch":
            cp, sha = load_checkpoint()
            _auth, asha = load_authorization(AUTHORIZATION, AUTHORIZATION_HASH)
            if a.confirm_checkpoint_sha256 != sha or a.confirm_authorization_sha256 != asha:
                print("REFUSED: the confirmations do not equal the frozen checkpoint and authorization sha256")
                return EXIT_REFUSED
            env = {"PATH": "/usr/bin:/bin", "HOME": os.environ.get("HOME", "/root"), "LANG": "C.UTF-8"}
            return keep([sys.executable, "-B", str(Path(__file__).resolve()), "_supervise"], root=cp["runtime_root"], env=env)
        spec, _cp = production_spec()
        if a.cmd == "_supervise":
            return ProvenanceSupervisor(spec, authz_loader=production_authz, preflight=_supervisor_preflight).run()
        if a.cmd == "status":
            print(json.dumps(L.Ledger.inspect(spec), indent=1, sort_keys=True, default=str))
            return 0
        authz = production_authz()
        if a.cmd == "audit":
            rep = PI.audit(spec, authz)
            atomic_write_json(a.out, rep)
            print(json.dumps({"INTEGRITY_READY_FOR_ADJUDICATION": rep["INTEGRITY_READY_FOR_ADJUDICATION"],
                              "A": rep["A_completeness"], "issues": sorted(rep["issues"])}, indent=1))
            return 0
        lock = L.CampaignLock(spec.root)
        lock.acquire({"tool": "prov_entry", "pid": os.getpid()})
        try:
            import prov_ledger as PL
            led = PL.ProvenanceLedger(spec, lock, authz=authz)
            led.open(allow_genesis=False)
            if a.cmd == "settle":
                reaped, unreadable = L.read_reaper(led.p)
                L.reconcile(led, reaped, unreadable)
                for aid in PL.unbound_sealed(led.state):
                    PL.bind_envelope(led, authz, aid)
                overhead = L.unmatched_overhead(reaped, led.state)
                if overhead:
                    led.txn("OVERHEAD_CHARGED", lambda s: L.op_charge_overhead(s, overhead), {"records": len(overhead)})
            elif a.cmd == "export":
                print(json.dumps({k: v for k, v in PI.export_pairs(led, authz, a.out).items() if k not in ("files", "pairs")}, indent=1))
            elif a.cmd == "attest":
                atomic_write_json(a.out, PI.build_k4_attestation(spec, authz, PI.audit(spec, authz)))
        finally:
            lock.release()
        return 0
    except Refusal as r:
        print(f"REFUSED [{r.code}] {r.detail}")
        return EXIT_REFUSED


if __name__ == "__main__":
    raise SystemExit(main())
