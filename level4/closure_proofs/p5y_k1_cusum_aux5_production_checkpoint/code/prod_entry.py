"""THE production entrypoint of the CUSUM Aux5 campaign. NON-CERTIFYING. Fails closed; no permissive fallback.

  python prod_entry.py preflight                    read-only; prints READY or NOT_READY (exit 0 / 30)
  python prod_entry.py launch --confirm-checkpoint-sha256 SHA
                                                    keeper + supervisor; the supervisor re-runs this whole preflight
                                                    under the campaign lock before its first admission
  python prod_entry.py status | drain | undrain | settle | export --out DIR | attest --out FILE

READY requires every check to PASS. No flag skips, weakens or overrides a check; `overrides` exists only for the
acceptance tests, only replaces live facts with test values, and is unreachable from this command line.

  C01 checkpoint_and_freeze      sha256(PRODUCTION_CHECKPOINT.json) == PRODUCTION_CHECKPOINT_HASH == FREEZE_RECORD
  C02 bound_sources              every bound source still has its frozen bytes
  C03 producer_identity          Aux5 manifest v3 bytes, recomputed identity hashes, certifier bytes
  C04 host_identity              live host facts == the bound rebaseguard-vultr-02 facts
  C05 checkout                   the bound checkout path, clean
  C06 runtime_contract           fresh env -i probe in the bound venv: manifest_v3.verify() ok, identity equal
  C07 universe_geometry          frozen cells table, geometry digest, cover facts
  C08 qualification_pass         qualification PASS record, protocol, the four record hashes, c_max
  C09 cost_cap                   formula bytes; CAP recomputed == 300 CPU-h; reservation; invariant
  C10 ledger_schema              ledger/journal/reaper/export schemas equal the checkpoint's
  C11 k4_structural_attestation  bound attestation file, recomputed byte-identically, K4 ... ATTESTED = YES
  C12 synthetic_acceptance       acceptance result bound by the freeze record, PASS, same checkpoint and host
  C13 run_state                  no live supervisor; runtime root FRESH or a compatible ledger; no halt, no DRAIN,
                                 no terminal disposition
  C14 host_idle                  no certifier, supervisor or synthetic worker process on the host
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import resource
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import k4_input_attestation as K4A                                                   # noqa: E402
import prod_cells                                                                    # noqa: E402
import prod_ledger as L                                                              # noqa: E402
from prod_common import (AUX5_NS, BOUND_HOST_FACTS, CHECKPOINT, CHECKPOINT_HASH,     # noqa: E402
                         FREEZE_RECORD, NS, ROOT, Refusal, atomic_write_bytes, atomic_write_json, canonical,
                         host_facts, host_problems, processes_matching, rusage_usec, sha256_bytes, sha256_file)
from prod_spec import (CHECKPOINT_SCHEMA, CampaignSpec, load_frozen_checkpoint,      # noqa: E402
                       manifest_identity)
from prod_supervisor import EXIT_REFUSED, Supervisor, keep                           # noqa: E402

REPORT_SCHEMA = "rebaseguard.p5y.k1.cusum-aux5.production-preflight.v1"
FREEZE_SCHEMA = "rebaseguard.p5y.k1.cusum-aux5.production-freeze-record.v1"
ACCEPTANCE_SCHEMA = "rebaseguard.p5y.k1.cusum-aux5.synthetic-acceptance.v1"
PROCESS_MARKERS = ("qualify5.py", "prod_entry.py launch", "prod_entry.py _supervise", "prod_supervisor.py",
                   "synthetic_worker.py")
PROBE = ("import json, sys\n"
         "sys.path.insert(0, sys.argv[1])\n"
         "import manifest_v3\n"
         "s = manifest_v3.verify()\n"
         "print(json.dumps({'ok': s['ok'], 'problems': s['problems'][:8], 'files': s['files'],\n"
         "                  'producer_manifest_hash': s['manifest_hash'],\n"
         "                  'runtime_contract_hash': s['runtime_contract_hash'],\n"
         "                  'producer_identity_hash': s['producer_identity_hash']}))\n")


def load_cap_formula(cp: dict):
    path = AUX5_NS / "code/cap_formula.py"
    if sha256_file(path) != cp["cost_cap"]["cap_formula_py_sha256"]:
        raise Refusal("COST_CAP", "cap_formula.py differs from its frozen bytes")
    spec = importlib.util.spec_from_file_location("aux5_cap_formula", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def identity_probe(cp: dict, *, root=None, env_extra=None) -> tuple[dict, int]:
    """manifest_v3.verify() in a fresh env -i interpreter of the bound venv. Returns (result, probe CPU usec)."""
    root = Path(root or cp["checkout_path"])
    env = dict(cp["runtime_contract"]["worker_environment"])
    env.update(env_extra or {})
    before = rusage_usec(resource.getrusage(resource.RUSAGE_CHILDREN))
    try:
        r = subprocess.run([cp["runtime_contract"]["venv_python"], "-c", PROBE,
                            str(root / cp["producer"]["namespace"] / "code")],
                           cwd=str(root), env=env, capture_output=True, text=True, timeout=900)
    except (OSError, subprocess.SubprocessError) as exc:
        return {"ok": False, "problems": [f"probe could not run: {exc!r}"]}, 0
    cpu = rusage_usec(resource.getrusage(resource.RUSAGE_CHILDREN)) - before
    if r.returncode != 0:
        return {"ok": False, "problems": [f"probe exit {r.returncode}: {r.stderr[-400:]}"]}, cpu
    return json.loads(r.stdout.strip().splitlines()[-1]), cpu


# ------------------------------------------------------------------ preflight
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
        except Exception as exc:                                    # noqa: BLE001  anything unexpected FAILS
            checks.append({"check": name, "status": "FAIL", "code": "UNEXPECTED", "detail": repr(exc)[:400]})

    def c01():
        if not raw:
            raise Refusal("CHECKPOINT_MISSING", str(CHECKPOINT))
        if cp.get("schema") != CHECKPOINT_SCHEMA or cp.get("status") != "FROZEN_PRE_PRODUCTION":
            raise Refusal("CHECKPOINT_SCHEMA", f"{cp.get('schema')!r} / {cp.get('status')!r}")
        if not CHECKPOINT_HASH.exists() or CHECKPOINT_HASH.read_text().strip() != sha:
            raise Refusal("CHECKPOINT_HASH", "PRODUCTION_CHECKPOINT_HASH != sha256(PRODUCTION_CHECKPOINT.json)")
        if not FREEZE_RECORD.exists():
            raise Refusal("NOT_FROZEN", "config/FREEZE_RECORD.json is absent")
        fr = json.loads(FREEZE_RECORD.read_text())
        if (fr.get("schema") != FREEZE_SCHEMA or fr.get("status") != "FROZEN"
                or fr.get("production_checkpoint_sha256") != sha or fr.get("production_launched") is not False):
            raise Refusal("FREEZE_RECORD", "the freeze record does not bind this checkpoint as frozen and unlaunched")
        return {"checkpoint_sha256": sha}

    def c02():
        drift = sorted(r for r, h in cp["bound_sources"].items()
                       if not (ROOT / r).exists() or sha256_file(ROOT / r) != h)
        if drift:
            raise Refusal("BOUND_SOURCE_DRIFT", f"{len(drift)} bound sources changed: {drift[:6]}")
        return {"bound_sources": len(cp["bound_sources"])}

    def c03():
        p = cp["producer"]
        mpath = ROOT / p["manifest_path"]
        if sha256_file(mpath) != p["manifest_file_sha256"]:
            raise Refusal("PRODUCER_IDENTITY", "producer manifest v3 bytes differ")
        m = json.loads(mpath.read_text())
        ident = manifest_identity(m)
        for k, v in ident.items():
            if p["record_identity"][k] != v:
                raise Refusal("PRODUCER_IDENTITY", f"{k} recomputes to {v[:16]}, checkpoint binds "
                                                   f"{p['record_identity'][k][:16]}")
        certifier = sha256_file(ROOT / p["certifier_path"])
        if certifier != p["certifier_sha256"] or m["files"].get(p["certifier_path"]) != certifier:
            raise Refusal("PRODUCER_IDENTITY", "the certifier bytes differ from the manifest / checkpoint")
        if cp["runtime_contract"]["runtime_contract_hash"] != ident["runtime_contract_hash"]:
            raise Refusal("RUNTIME_CONTRACT", "checkpoint runtime contract hash differs from the manifest")
        return ident

    def c04():
        live = ov.get("host_facts") or host_facts()
        problems = host_problems(cp["host"]["bound_facts"], live, BOUND_HOST_FACTS)
        if problems:
            raise Refusal("WRONG_HOST", "; ".join(problems[:6]))
        return {"host_name": live["host_name"]}

    def c05():
        if ROOT != Path(cp["checkout_path"]):
            raise Refusal("CHECKOUT", f"entrypoint runs from {ROOT}, checkpoint binds {cp['checkout_path']}")
        status = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain"], capture_output=True, text=True)
        if status.returncode != 0 or status.stdout.strip():
            raise Refusal("CHECKOUT", f"checkout is not clean: {status.stdout.strip()[:300] or status.stderr[:300]}")
        head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True)
        return {"head": head.stdout.strip()}

    def c06():
        if "probe" in ov:
            result, cpu = ov["probe"], 0
        else:
            result, cpu = identity_probe(cp, root=ov.get("probe_root"), env_extra=ov.get("probe_env_extra"))
        ctx["probe_cpu_usec"] += cpu
        if not result.get("ok"):
            raise Refusal("RUNTIME_CONTRACT", "; ".join(result.get("problems", [])[:4]) or "probe failed")
        for k in ("producer_manifest_hash", "runtime_contract_hash", "producer_identity_hash"):
            if result.get(k) != cp["producer"]["record_identity"][k]:
                raise Refusal("PRODUCER_IDENTITY" if k != "runtime_contract_hash" else "RUNTIME_CONTRACT",
                              f"live {k} {str(result.get(k))[:16]} != frozen {cp['producer']['record_identity'][k][:16]}")
        if result.get("files") != cp["producer"]["tcb_files"]:
            raise Refusal("PRODUCER_IDENTITY", f"TCB file count {result.get('files')}")
        return {k: result[k][:16] for k in ("producer_identity_hash", "runtime_contract_hash")} | {"probe_cpu_usec": cpu}

    def c07():
        cells = prod_cells.cusum_cells()
        g = cp["geometry"]
        if prod_cells.geometry_digest(cells) != g["geometry_digest"] or prod_cells.cover_facts(cells) != g["cover"]:
            raise Refusal("FROZEN_GEOMETRY_MUTATED", "geometry digest or cover facts differ")
        return {"cells": len(cells), "geometry_digest": g["geometry_digest"][:16]}

    def c08():
        q = cp["qualification"]
        path = ROOT / q["result_path"]
        if sha256_file(path) != q["result_sha256"]:
            raise Refusal("QUALIFICATION", "QUALIFICATION_RESULT.json bytes differ")
        res = json.loads(path.read_text())
        if (res["QUALIFICATION"] != "PASS" or res["CUSUM_DETERMINISM"] != "PASS" or not all(res["criteria"].values())
                or res["production"] is not False or res["transition_to_production_authorized"] is not False):
            raise Refusal("QUALIFICATION", "qualification record is not a non-production PASS")
        if sha256_file(ROOT / q["protocol_path"]) != q["protocol_sha256"] or res["protocol_sha256"] != q["protocol_sha256"]:
            raise Refusal("QUALIFICATION", "protocol bytes differ")
        cmax = []
        for key, relpath in q["record_paths"].items():
            if sha256_file(ROOT / relpath) != q["record_file_sha256"][key]:
                raise Refusal("QUALIFICATION", f"qualification record {key} bytes differ")
            cmax.append(json.loads((ROOT / relpath).read_text())["cpu_seconds_including_dependencies"])
        if repr(max(cmax)) != cp["cost_cap"]["c_max_cpu_seconds"]:
            raise Refusal("QUALIFICATION", f"c_max recomputes to {max(cmax)!r}")
        return {"verdict": "PASS", "c_max_cpu_seconds": repr(max(cmax))}

    def c09():
        c = cp["cost_cap"]
        if sha256_file(ROOT / c["formula_path"]) != c["formula_file_sha256"]:
            raise Refusal("COST_CAP", "COST_CAP_FORMULA.json bytes differ")
        derived = load_cap_formula(cp).cap(c_max_cpu_seconds=c["c_max_cpu_seconds"], n_cells=c["N"], workers=c["W"])
        if derived["exact"]["CAP"] != "300" or derived["CAP_cpu_h"] != c["cap_cpu_h"] or c["cap_cpu_h"] != 300:
            raise Refusal("COST_CAP", f"CAP recomputes to {derived['exact']['CAP']}, checkpoint binds {c['cap_cpu_h']}")
        from fractions import Fraction
        if Fraction(derived["exact"]["R"]) * 3_600_000_000 != c["reservation_usec"] or c["invariant"] != L.INVARIANT:
            raise Refusal("COST_CAP", "reservation or invariant differs")
        return {"CAP_cpu_h": derived["CAP_cpu_h"], "R_cpu_h": derived["exact"]["R"]}

    def c10():
        want = cp["ledger"]["schemas"]
        have = {"ledger": L.LEDGER_SCHEMA, "journal": L.JOURNAL_SCHEMA, "reaper": L.REAPER_SCHEMA,
                "export": L.EXPORT_SCHEMA}
        if want != have:
            raise Refusal("LEDGER_SCHEMA", f"{have} != {want}")
        return have

    def c11():
        k = cp["k4"]
        path = ROOT / k["input_schema_attestation_path"]
        if sha256_file(path) != k["input_schema_attestation_sha256"]:
            raise Refusal("K4_ATTESTATION", "attestation file bytes differ")
        live = K4A.attest_schema()
        if canonical(live) != canonical(json.loads(path.read_text())):
            raise Refusal("K4_ATTESTATION", "the attestation does not recompute identically")
        if live["K4_CUSUM_INPUT_SCHEMA_ATTESTED"] != "YES" or live["k4_checkpoint"]["checkpoint_sha256"] != k["checkpoint_sha256"]:
            raise Refusal("K4_ATTESTATION", f"attested {live['K4_CUSUM_INPUT_SCHEMA_ATTESTED']}; {live['problems'][:3]}")
        return {"K4_CUSUM_INPUT_SCHEMA_ATTESTED": "YES"}

    def c12():
        fr = json.loads(FREEZE_RECORD.read_text())
        acc = fr["synthetic_acceptance"]
        path = ROOT / acc["path"]
        if sha256_file(path) != acc["sha256"]:
            raise Refusal("ACCEPTANCE", "acceptance result bytes differ from the freeze record")
        res = json.loads(path.read_text())
        if (res.get("schema") != ACCEPTANCE_SCHEMA or res.get("CUSUM_SYNTHETIC_ACCEPTANCE") != "PASS"
                or res.get("checkpoint_sha256") != sha or res.get("host_name") != cp["host"]["bound_facts"]["host_name"]):
            raise Refusal("ACCEPTANCE", "acceptance result is not a PASS for this checkpoint on the bound host")
        return {"scenarios": len(res.get("scenarios", {})), "verdict": "PASS"}

    def c13():
        spec = CampaignSpec.production()
        if not in_supervisor and L.CampaignLock(spec.root).probe() == "LIVE":
            raise Refusal("ANOTHER_SUPERVISOR_LIVE", "a supervisor holds the campaign lock")
        if L.Paths(spec.root).drain.exists():
            raise Refusal("DRAIN_PRESENT", "a DRAIN marker is present")
        view = L.Ledger.inspect(spec)
        if view["relation"] != "FRESH":
            if view["halt"] is not None:
                raise Refusal("HALTED", f"ledger halted: {view['halt']}")
            if view["disposition"] in L.TERMINAL:
                raise Refusal("TERMINAL_DISPOSITION", view["disposition"])
        return view

    def c14():
        skip = {os.getpid()} | ({os.getppid()} if in_supervisor else set())
        found = [p for p in processes_matching(PROCESS_MARKERS) if p["pid"] not in skip]
        if found:
            raise Refusal("HOST_NOT_IDLE", f"{found[:4]}")
        return {"foreign_processes": 0}

    for name, fn in (("C01_checkpoint_and_freeze", c01), ("C02_bound_sources", c02), ("C03_producer_identity", c03),
                     ("C04_host_identity", c04), ("C05_checkout", c05), ("C06_runtime_contract", c06),
                     ("C07_universe_geometry", c07), ("C08_qualification_pass", c08), ("C09_cost_cap", c09),
                     ("C10_ledger_schema", c10), ("C11_k4_structural_attestation", c11),
                     ("C12_synthetic_acceptance", c12), ("C13_run_state", c13), ("C14_host_idle", c14)):
        check(name, fn)
    ready = all(c["status"] == "PASS" for c in checks)
    return {"schema": REPORT_SCHEMA, "ready": ready, "checkpoint_sha256": sha if raw else None,
            "checks": checks, "probe_cpu_usec": ctx["probe_cpu_usec"],
            "CUSUM_AUX5_PRODUCTION_ENTRYPOINT": "READY" if ready else "NOT_READY", "production_launched": False}


def print_report(rep: dict) -> None:
    for c in rep["checks"]:
        tail = "" if c["status"] == "PASS" else f"   [{c['code']}] {str(c['detail'])[:300]}"
        print(f"  {c['status']:4s}  {c['check']}{tail}")
    if rep["ready"]:
        print(f"CUSUM_AUX5_PRODUCTION_ENTRYPOINT = READY   checkpoint {rep['checkpoint_sha256']}")
        print("READY_TO_LAUNCH_PRODUCTION: nothing has been launched. Launching requires the explicit operator command")
        print(f"  prod_entry.py launch --confirm-checkpoint-sha256 {rep['checkpoint_sha256']}")
    else:
        print("CUSUM_AUX5_PRODUCTION_ENTRYPOINT = NOT_READY   (fail closed: nothing may be launched)")


def _supervisor_preflight():
    rep = preflight(in_supervisor=True)
    print_report(rep)
    return rep["ready"], rep, rep["probe_cpu_usec"]


# ------------------------------------------------------------------ commands
def _locked_ledger(spec):
    lock = L.CampaignLock(spec.root)
    lock.acquire({"tool": "prod_entry", "pid": os.getpid()})
    led = L.Ledger(spec, lock)
    led.open(allow_genesis=False)
    return lock, led


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="CUSUM Aux5 production entrypoint")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("preflight")
    p_launch = sub.add_parser("launch")
    p_launch.add_argument("--confirm-checkpoint-sha256", required=True)
    sub.add_parser("_supervise", help=argparse.SUPPRESS)
    for name in ("status", "drain", "undrain", "settle"):
        sub.add_parser(name)
    p_export = sub.add_parser("export")
    p_export.add_argument("--out", required=True)
    p_attest = sub.add_parser("attest")
    p_attest.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    try:
        if a.cmd == "preflight":
            rep = preflight()
            print_report(rep)
            return 0 if rep["ready"] else EXIT_REFUSED
        if a.cmd == "launch":
            cp, sha = load_frozen_checkpoint()
            if a.confirm_checkpoint_sha256 != sha:
                print("REFUSED: --confirm-checkpoint-sha256 does not equal the frozen production checkpoint sha256")
                return EXIT_REFUSED
            env = {"PATH": "/usr/bin:/bin", "HOME": os.environ.get("HOME", "/root"), "LANG": "C.UTF-8"}
            return keep([sys.executable, str(Path(__file__).resolve()), "_supervise"], root=cp["runtime_root"], env=env)
        spec = CampaignSpec.production()
        if a.cmd == "_supervise":
            return Supervisor(spec, preflight=_supervisor_preflight).run()
        if a.cmd == "status":
            print(json.dumps(L.Ledger.inspect(spec), indent=1, sort_keys=True, default=str))
            return 0
        if a.cmd == "drain":
            if not Path(spec.root).exists():
                raise Refusal("NO_CAMPAIGN", str(spec.root))
            atomic_write_bytes(L.Paths(spec.root).drain, b"DRAIN\n")
            print("DRAIN marker written; the supervisor stops admitting and lets admitted work finish")
            return 0
        lock, led = _locked_ledger(spec)
        try:
            if a.cmd == "undrain":
                if led.p.drain.exists():
                    os.unlink(led.p.drain)
                print("DRAIN marker removed")
            elif a.cmd == "settle":
                reaped, unreadable = L.read_reaper(led.p)
                report = L.reconcile(led, reaped, unreadable)
                overhead = L.unmatched_overhead(reaped, led.state)
                if overhead:
                    led.txn("OVERHEAD_CHARGED", lambda s: L.op_charge_overhead(s, overhead), {"records": len(overhead)})
                print(json.dumps({"reconciled": report, "overhead_records_charged": len(overhead)}, indent=1))
            elif a.cmd == "export":
                print(json.dumps({k: v for k, v in L.export_bundle(led, a.out).items() if k != "files"}, indent=1))
            elif a.cmd == "attest":
                att = K4A.build_integrity_attestation(spec, led.state, checkpoint_sha256=spec.checkpoint_sha256)
                atomic_write_json(a.out, att)
                print(json.dumps({k: att[k] for k in ("schema", "cells_verified", "all_scientific_hashes_verified")}))
        finally:
            lock.release()
        return 0
    except Refusal as r:
        print(f"REFUSED [{r.code}] {r.detail}")
        return EXIT_REFUSED


if __name__ == "__main__":
    raise SystemExit(main())
