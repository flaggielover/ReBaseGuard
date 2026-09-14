"""THE production entrypoint of the CUSUM Aux5 new-glibc successor. NON-CERTIFYING. Fails closed.

  python gs_entry.py preflight [--out F]           read-only launch preflight; READY or NOT_READY (exit 0 / 30)
  python gs_entry.py launch --confirm-checkpoint-sha256 SHA --confirm-authorization-sha256 SHA
  python gs_entry.py settle                        end-of-campaign settlement of the terminal successor ledger (gs_settle)
  python gs_entry.py status | composite-audit --out F | attest --out F | export --out DIR

After production the operator sequence is: supervisor exits terminal -> settle -> composite-audit -> attest -> export.
The frozen supervisor never settles its own final run, so the frozen successor audit (and with it the composite audit,
the K4 attestation and the export) is never ready before `settle`. `settle --synthetic-spec CFG` runs the same settlement
on a synthetic acceptance campaign and is refused inside every production runtime root.

READY requires every check to PASS; nothing skips or weakens a check (`overrides` exists for tests only and is not
reachable from this command line). The supervisor re-runs this preflight under the campaign lock before genesis. The
superseded checkpoint 51df2186 and authorization 03b9ca80 are refused by name.

  G01 checkpoint_and_freeze             checkpoint sha == hash file == freeze record; frozen, unlaunched; not superseded
  G02 bound_sources                     every bound source unchanged (inside load_checkpoint); settlement tooling bound
  G03 carryover_countersignature        verifier PASS, sha e1ee7fb1 == checkpoint binding, committed
  G04 proposal_q6_launch_readiness      proposal and Q6 verify; frozen glibc_successor.launch_readiness READY
  G05 run_authorization                 recomputes; bound by the freeze record; committed before the freeze (pre-result)
  G06 synthetic_acceptance              PASS for this checkpoint and authorization on the bound host
  G07 checkout                          running from the bound clean checkout
  G08 predecessor_binding_live          live re-collection byte-identical to PREDECESSOR_BINDING.json
  G09 predecessor_halted_immutable      HALTED; ledger/journal/reaper and all 256 record/envelope bytes unchanged
  G10 composite_predecessor_half        frozen prov_integrity.audit; exactly the tolerated issues; 128 pairs
  G11 containment                       live containment == bound POST_STATE
  G12 host_runtime_identity_and_boot    10 facts, 11 libraries, 8 packages, boot id; admission guard clean
  G13 runtime_contract_probe            env -i probe in the bound venv: manifest v3 ok, identity equal
  G14 universe_and_cap                  universe 128-325, disjoint from 0-127; ledger cap == residual; invariant
  G15 qualification_firewall            4 qualification + 4 Q6 record hashes bound and unchanged
  G16 protected_trees                   predecessor namespaces unchanged, clean, commits in history
  G17 run_state                         successor root ABSENT/PRE_GENESIS, or a ledger born under this authorization
                                        that is not halted/terminal; no live lock, no DRAIN; refused roots never used
  G18 host_idle                         no certifier, supervisor or worker of any generation (argv-element match)
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import gs_schema as GS                                                           # noqa: E402
import carryover_countersignature as CC                                          # noqa: E402
import glibc_successor as G                                                      # noqa: E402
import gs_composite as GC                                                        # noqa: E402
import gs_host as H                                                              # noqa: E402
import gs_settle as ST                                                           # noqa: E402
import prod_ledger as L                                                          # noqa: E402
import q6_result as R                                                            # noqa: E402
from gs_authorization import load_authorization, load_authz, verify_authorization  # noqa: E402
from gs_spec import check_cost_cap, load_checkpoint, production_spec, spec_from_checkpoint  # noqa: E402
from prod_common import Refusal, atomic_write_json, sha256_bytes, sha256_file    # noqa: E402

PREFLIGHT_CHECKS = ("G01_checkpoint_and_freeze", "G02_bound_sources", "G03_carryover_countersignature",
                    "G04_proposal_q6_launch_readiness", "G05_run_authorization", "G06_synthetic_acceptance",
                    "G07_checkout", "G08_predecessor_binding_live", "G09_predecessor_halted_immutable",
                    "G10_composite_predecessor_half", "G11_containment", "G12_host_runtime_identity_and_boot",
                    "G13_runtime_contract_probe", "G14_universe_and_cap", "G15_qualification_firewall",
                    "G16_protected_trees", "G17_run_state", "G18_host_idle")
READY, NOT_READY = "READY_TO_LAUNCH_SUCCESSOR", "NOT_READY"
EXIT_REFUSED = 30


def _git(*args) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(GS.ROOT), *args], capture_output=True)


def _json(p):
    return json.loads(Path(p).read_bytes())


def production_authz():
    spec, cp = production_spec()
    return load_authz(spec, cp, auth_path=GS.AUTHORIZATION, hash_path=GS.AUTHORIZATION_HASH, cs_path=GS.COUNTERSIGNATURE,
                      cs_verifier=CC.verify_countersignature)


def predecessor_objects():
    import prov_entry as PENT
    import prov_spec
    spec, _cp = prov_spec.production_spec()
    return spec, PENT.production_authz()


def live_record_envelope_digest(root: Path) -> str:
    rows = sorted([(str(p.relative_to(root)), sha256_file(p)) for p in root.glob("attempts/*/aux5_CUSUM_*_256.json")]
                  + [(str(p.relative_to(root)), sha256_file(p)) for p in root.glob("provenance/**/*") if p.is_file()],
                  key=lambda r: r[0].encode())
    return sha256_bytes("".join(f"{h}  {p}\n" for p, h in rows).encode())


def refuse_superseded(checkpoint_sha256=None, authorization_sha256=None) -> None:
    if checkpoint_sha256 == GS.SUPERSEDED_CHECKPOINT_SHA256:
        raise Refusal("SUPERSEDED_CHECKPOINT", "checkpoint 51df2186 was superseded before launch and is never launched")
    if authorization_sha256 == GS.SUPERSEDED_AUTHORIZATION_SHA256:
        raise Refusal("SUPERSEDED_AUTHORIZATION", "authorization 03b9ca80 was superseded before launch and is never used")


def settlement_tooling(cp: dict) -> dict:
    es = cp.get("END_OF_CAMPAIGN_SETTLEMENT") or {}
    mods = es.get("module_sha256") or {}
    live = {r: (sha256_file(GS.ROOT / r) if (GS.ROOT / r).is_file() else None) for r in mods}
    if (not mods or live != mods or es.get("version") != ST.SETTLE_VERSION or es.get("command") != ST.SETTLE_COMMAND
            or f"{GS.NS_REL}/code/gs_settle.py" not in mods or f"{GS.NS_REL}/code/gs_entry.py" not in mods):
        raise Refusal("SETTLEMENT_TOOLING", "the end-of-campaign settlement tooling is not the one bound by the checkpoint")
    return {"settlement_version": es["version"], "settlement_modules": len(mods)}


def preflight(*, overrides=None, in_supervisor: bool = False) -> dict:
    ov = overrides or {}
    checks, ctx = [], {"probe_cpu_usec": 0, "sha": None, "asha": None}

    def check(name, fn):
        try:
            checks.append({"check": name, "status": "PASS", "detail": fn()})
        except Refusal as r:
            checks.append({"check": name, "status": "FAIL", "code": r.code, "detail": r.detail})
        except Exception as exc:                                       # noqa: BLE001  anything unexpected FAILS
            checks.append({"check": name, "status": "FAIL", "code": "UNEXPECTED", "detail": repr(exc)[:400]})

    def cp_():
        cp, sha = load_checkpoint()
        ctx["sha"] = sha
        return cp, sha

    def freeze():
        if not GS.FREEZE_RECORD.exists():
            raise Refusal("NOT_FROZEN", "config/FREEZE_RECORD.json is absent")
        return _json(GS.FREEZE_RECORD)

    def g01():
        _cp, sha = cp_()
        refuse_superseded(checkpoint_sha256=sha)
        fr = freeze()
        if (fr.get("schema") != GS.FREEZE_SCHEMA or fr.get("status") != GS.FREEZE_STATUS
                or fr.get("checkpoint_sha256") != sha or fr.get("production_launched") is not False):
            raise Refusal("FREEZE_RECORD", "the freeze record does not bind this checkpoint as frozen and unlaunched")
        return {"checkpoint_sha256": sha}

    def g02():
        cp, _sha = cp_()
        return {"bound_sources": len(cp["bound_sources"]), **settlement_tooling(cp)}

    def g03():
        cp, _sha = cp_()
        problems = ov["countersignature_problems"] if "countersignature_problems" in ov else CC.verify_countersignature()
        sha = sha256_file(GS.COUNTERSIGNATURE) if GS.COUNTERSIGNATURE.exists() else None
        if problems or sha != GS.COUNTERSIGNATURE_SHA256 or cp["countersignature_sha256"] != sha:
            raise Refusal("COUNTERSIGNATURE_INVALID", f"{problems[:4]} sha {sha}")
        if _git("ls-files", "--error-unmatch", str(GS.COUNTERSIGNATURE.relative_to(GS.ROOT))).returncode != 0:
            raise Refusal("COUNTERSIGNATURE_INVALID", "the countersignature is not committed")
        return {"countersignature_sha256": sha}

    def g04():
        cp, _sha = cp_()
        p = G.verify_proposal() + R.verify_result()
        if p:
            raise Refusal("PROPOSAL_OR_Q6", f"{p[:4]}")
        q6_raw = (GS.NS / R.RESULT_REL).read_bytes()
        q6 = G.evaluate_q6(json.loads(q6_raw), _json(GS.NS / "config/Q6_REFERENCE.json"), result_sha256=sha256_bytes(q6_raw))
        cs_raw = GS.COUNTERSIGNATURE.read_bytes()
        rep = G.launch_readiness(proposal_problems=[], proposal_sha256=sha256_file(GS.NS / G.PROPOSAL), q6=q6,
                                 countersignature=json.loads(cs_raw), countersignature_sha256=sha256_bytes(cs_raw),
                                 checkpoint=cp)
        if rep["state"] != "READY_TO_LAUNCH_SUCCESSOR" or q6["result_sha256"] != GS.Q6_RESULT_SHA256:
            raise Refusal("LAUNCH_READINESS", f"{rep['state']} {rep['problems']}")
        return {"launch_readiness": rep["state"]}

    def g05():
        cp, sha = cp_()
        auth, asha = load_authorization(GS.AUTHORIZATION, GS.AUTHORIZATION_HASH)
        ctx["asha"] = asha
        refuse_superseded(authorization_sha256=asha)
        verify_authorization(auth, spec_from_checkpoint(cp, sha), cp)
        ra = freeze().get("run_authorization") or {}
        commit = ra.get("commit", "")
        if ra.get("sha256") != asha or _git("merge-base", "--is-ancestor", commit, "HEAD").returncode != 0:
            raise Refusal("AUTHORIZATION_NOT_FROZEN", "the freeze record does not bind this authorization at an ancestor commit")
        shown = _git("show", f"{commit}:{GS.AUTHORIZATION.relative_to(GS.ROOT)}")
        if shown.returncode != 0 or sha256_bytes(shown.stdout) != asha:
            raise Refusal("AUTHORIZATION_NOT_PRE_RESULT", "the authorization differs from the one committed at its commit")
        return {"authorization_sha256": asha, "commit": commit, "ledger_id": auth["ledger"]["ledger_id"]}

    def g06():
        cp, sha = cp_()
        acc = freeze()["synthetic_acceptance"]
        path = GS.ROOT / acc["path"]
        if sha256_file(path) != acc["sha256"]:
            raise Refusal("ACCEPTANCE", "acceptance result bytes differ from the freeze record")
        res = _json(path)
        if (res.get("schema") != GS.ACCEPTANCE_SCHEMA or res.get("GLIBC_SUCCESSOR_SYNTHETIC_ACCEPTANCE") != "PASS"
                or res.get("checkpoint_sha256") != sha or res.get("host_name") != cp["host"]["bound_facts"]["host_name"]
                or res.get("run_authorization_sha256") != sha256_file(GS.AUTHORIZATION)):
            raise Refusal("ACCEPTANCE", "acceptance is not a PASS for this checkpoint and authorization on the bound host")
        return {"tests": len(res.get("tests", {}))}

    def g07():
        cp, _sha = cp_()
        if GS.ROOT != Path(cp["checkout_path"]):
            raise Refusal("CHECKOUT", f"entrypoint runs from {GS.ROOT}, checkpoint binds {cp['checkout_path']}")
        st = _git("status", "--porcelain")
        if st.returncode != 0 or st.stdout.strip():
            raise Refusal("CHECKOUT", f"checkout is not clean: {st.stdout.decode()[:300]}")
        return {"head": _git("rev-parse", "HEAD").stdout.decode().strip()}

    def g08():
        live = ov["live_binding"] if "live_binding" in ov else G.collect(GS.ROOT)
        committed = _json(GS.BINDING)
        p = G.compare_live(committed, live) + G.verify_binding(live)
        if p or sha256_bytes(G.dump(live)) != GS.BINDING_SHA256:
            raise Refusal("PREDECESSOR_CHANGED_SINCE_BINDING", f"{p[:4]}")
        return {"binding_sha256": GS.BINDING_SHA256}

    def g09():
        cp, _sha = cp_()
        pred = cp["predecessor"]
        root = Path(pred["runtime_root"])
        files = ov.get("predecessor_files") or {n: sha256_file(root / n) for n in pred["files_sha256"]}
        digest = ov.get("predecessor_digest") or live_record_envelope_digest(root)
        st = ov.get("predecessor_state") or _json(root / "ledger.json")
        if files != pred["files_sha256"] or digest != pred["record_envelope_digest_sha256"]:
            raise Refusal("PREDECESSOR_EVIDENCE_CHANGED", "predecessor ledger/journal/reaper or record/envelope bytes changed")
        if st.get("disposition") != "HALTED" or st.get("halt") != pred["stop"]:
            raise Refusal("PREDECESSOR_NOT_HALTED", f"disposition {st.get('disposition')}")
        if L.CampaignLock(root).probe() == "LIVE":
            raise Refusal("PREDECESSOR_LOCK_LIVE", "a process holds the predecessor campaign lock")
        return {"disposition": "HALTED", "record_envelope_digest": digest}

    def g10():
        binding = _json(GS.BINDING)
        if "predecessor_audit" in ov:
            rep = ov["predecessor_audit"]
        else:
            import prov_integrity as PI
            pspec, pauthz = predecessor_objects()
            rep = PI.audit(pspec, pauthz)
        p = GC.predecessor_problems(rep, GC.tolerance_for_production(binding))
        if p:
            raise Refusal("COMPOSITE_PREDECESSOR_HALF", f"{p}")
        return {"verified_pairs": len(rep["pairs"]), "tolerated": sorted(rep["issues"])}

    def g11():
        cp, _sha = cp_()
        live = ov["containment"] if "containment" in ov else H.containment_state()
        p = H.containment_problems(cp["host"]["containment"]["post_state"], live)
        if p:
            raise Refusal("CONTAINMENT_NOT_APPLIED", f"{p}")
        return {"holds": len(live["holds"])}

    def g12():
        cp, sha = cp_()
        live = ov["host_identity"] if "host_identity" in ov else H.full_host_identity()
        p = H.identity_problems(cp["host"], live)
        if not p and "host_identity" not in ov:
            p = spec_from_checkpoint(cp, sha).host_guard()
        if p:
            raise Refusal("HOST_DRIFT", "; ".join(p[:6]))
        return {"host_name": live["host_name"], "boot_id": live["boot_id"]}

    def g13():
        cp, _sha = cp_()
        if "probe" in ov:
            result, cpu = ov["probe"], 0
        else:
            import prod_entry as PE
            result, cpu = PE.identity_probe(cp)
        ctx["probe_cpu_usec"] += cpu
        ident = cp["producer"]["record_identity"]
        if not result.get("ok") or any(result.get(k) != ident[k] for k in ("producer_manifest_hash", "runtime_contract_hash",
                                                                          "producer_identity_hash")) \
                or result.get("files") != cp["producer"]["tcb_files"]:
            raise Refusal("RUNTIME_CONTRACT", f"{result.get('problems', [])[:3]}")
        return {"producer_identity_hash": ident["producer_identity_hash"][:16], "probe_cpu_usec": cpu}

    def g14():
        cp, sha = cp_()
        spec = spec_from_checkpoint(cp, sha)
        p = G.check_partition(GS.OLD_CELLS, spec.cell_indices) + G.check_no_recomputation(spec.cell_indices)
        p += G.check_cap(_json(GS.NS / "config/CPU_CAP_CONTINUITY.json"), _json(GS.BINDING))
        check_cost_cap(cp["cost_cap"])
        if spec.cap_usec != GS.RESIDUAL_CAP_US or L.INVARIANT != GS.INVARIANT:
            p.append("spec cap or invariant")
        if p:
            raise Refusal("UNIVERSE_OR_CAP", f"{p}")
        return {"cells": len(spec.cell_indices), "cap_usec": spec.cap_usec}

    def g15():
        cp, sha = cp_()
        fw = cp["qualification_firewall"]["record_file_sha256"]
        q = cp["qualification"]
        live = {k: sha256_file(GS.ROOT / p) for k, p in q["record_paths"].items()}
        q6 = _json(GS.NS / R.RESULT_REL)["runs"]
        live.update({f"Q6_{k}": sha256_file(GS.NS / f"evidence/requalification_r1/qualification_r1/c{k[:3]}_{k[3]}/aux5_CUSUM_{k[:3]}_256.json")
                     for k in q6})
        if live != fw or len(fw) != 8 or spec_from_checkpoint(cp, sha).qualification_record_sha256 != frozenset(fw.values()):
            raise Refusal("QUALIFICATION_FIREWALL", "qualification or Q6 record hashes differ from the checkpoint")
        return {"firewalled_records": len(fw)}

    def g16():
        p = ov["protected_trees"] if "protected_trees" in ov else CC.check_git(CC.git_state, GS.ROOT)
        if p:
            raise Refusal("PROTECTED_TREES", f"{p}")
        return {"protected_trees": len(CC.PROTECTED_TREES)}

    def g17():
        import issuance as ISS
        cp, sha = cp_()
        spec = spec_from_checkpoint(cp, sha)
        root = Path(spec.root)
        if root in GS.REFUSED_ROOTS or any(r in root.parents for r in GS.REFUSED_ROOTS):
            raise Refusal("REFUSED_ROOT", str(root))
        if not in_supervisor and root.is_dir() and L.CampaignLock(root).probe() == "LIVE":
            raise Refusal("ANOTHER_SUPERVISOR_LIVE", "a supervisor holds the successor campaign lock")
        if L.Paths(root).drain.exists():
            raise Refusal("DRAIN_PRESENT", "a DRAIN marker is present")
        if not (root / "ledger.json").exists() and not (root / "journal.jsonl").exists():
            lock_state = "FREE" if in_supervisor or not root.is_dir() else ISS._lock_state(root)
            rr = ISS.classify_runtime_root(root, lock_state=lock_state, bound_host=cp["host"]["bound_facts"]["host_name"])
            if rr["state"] not in ("ABSENT", "PRE_GENESIS"):
                raise Refusal("RUNTIME_ROOT_NOT_PRE_GENESIS", f"{rr['state']} {rr['problems'][:4]}")
            return {"runtime_root": rr["state"], "production_started": False}
        view = L.Ledger.inspect(spec)
        _auth, asha = load_authorization(GS.AUTHORIZATION, GS.AUTHORIZATION_HASH)
        if (_json(root / "ledger.json").get("production_authorization") or {}).get("authorization_sha256") != asha:
            raise Refusal("NO_PRE_RESULT_AUTHORIZATION", "the existing successor ledger was not born under this authorization")
        if view["halt"] is not None or view["disposition"] in L.TERMINAL:
            raise Refusal("TERMINAL_OR_HALTED", f"{view['disposition']} {view['halt']}")
        return {"runtime_root": "LEDGER_UNDER_THIS_AUTHORIZATION", "production_started": True, **view}

    def g18():
        found = ov["processes"] if "processes" in ov else H.foreign_campaign_processes()
        if found:
            raise Refusal("HOST_NOT_IDLE", f"{found[:4]}")
        return {"foreign_processes": 0}

    for name, fn in zip(PREFLIGHT_CHECKS, (g01, g02, g03, g04, g05, g06, g07, g08, g09, g10, g11, g12, g13, g14, g15, g16,
                                           g17, g18)):
        check(name, fn)
    ready = all(c["status"] == "PASS" for c in checks)
    return {"schema": GS.PREFLIGHT_SCHEMA, "version": GS.PREFLIGHT_VERSION, "ready": ready,
            "checkpoint_sha256": ctx["sha"], "authorization_sha256": ctx["asha"], "checks": checks,
            "probe_cpu_usec": ctx["probe_cpu_usec"], "production_launched": False,
            "GLIBC_SUCCESSOR_LAUNCH": READY if ready else NOT_READY,
            "PRODUCTION_LAUNCH_AUTHORIZED": ready,
            "launch_requires": "READY here and an explicit operator command with both confirmations"}


def print_report(rep: dict) -> None:
    for c in rep["checks"]:
        print(f"  {c['status']:4s}  {c['check']}" + ("" if c["status"] == "PASS" else f"   [{c['code']}] {str(c['detail'])[:300]}"))
    print(f"GLIBC_SUCCESSOR_LAUNCH = {rep['GLIBC_SUCCESSOR_LAUNCH']}   checkpoint {rep['checkpoint_sha256']}   "
          f"authorization {rep['authorization_sha256']}")


def _supervisor_preflight():
    rep = preflight(in_supervisor=True)
    print_report(rep)
    return rep["ready"], rep, rep["probe_cpu_usec"]


def settle_command(synthetic_spec=None) -> int:
    """`gs_entry.py settle`: THE sanctioned end-of-campaign settlement (gs_settle.settle_campaign). The synthetic form
    differs only in which campaign it loads; the settlement code path is the same."""
    try:
        if synthetic_spec:
            from gs_spec import synthetic_drift_spec, synthetic_spec as load_synthetic
            from gs_supervisor import synthetic_successor_authz
            cfg = _json(synthetic_spec)
            if cfg.get("predecessor_shape"):
                raise Refusal("PREDECESSOR_RUNTIME_REFUSED", "a predecessor-shaped ledger is never settled by the successor")
            spec = synthetic_drift_spec(cfg) if cfg.get("drift_after_records") else load_synthetic(cfg)
            ST.precheck_target(spec)
            authz = synthetic_successor_authz(spec, cfg)
        else:
            spec, _cp = production_spec()
            refuse_superseded(checkpoint_sha256=spec.checkpoint_sha256)
            ST.precheck_target(spec)
            authz = production_authz()
            refuse_superseded(authorization_sha256=authz.block["authorization_sha256"])
        rep = ST.settle_campaign(spec, authz)
    except Refusal as r:
        print(f"REFUSED [{r.code}] {r.detail}")
        return EXIT_REFUSED
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"REFUSED [SETTLE_INPUT_UNREADABLE] {type(exc).__name__}: {exc}")
        return EXIT_REFUSED
    print(json.dumps(rep, indent=1, sort_keys=True))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="CUSUM Aux5 new-glibc successor production entrypoint")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("preflight").add_argument("--out")
    p = sub.add_parser("launch")
    p.add_argument("--confirm-checkpoint-sha256", required=True)
    p.add_argument("--confirm-authorization-sha256", required=True)
    sub.add_parser("_supervise", help=argparse.SUPPRESS)
    s = sub.add_parser("settle", help="end-of-campaign settlement of the terminal successor ledger; never admits")
    s.add_argument("--synthetic-spec", help="synthetic acceptance only: settle a synthetic successor campaign")
    sub.add_parser("status")
    for name in ("composite-audit", "attest", "export"):
        sub.add_parser(name).add_argument("--out", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "settle":
        return settle_command(a.synthetic_spec)
    try:
        if a.cmd == "preflight":
            rep = preflight()
            print_report(rep)
            if a.out:
                atomic_write_json(a.out, rep)
            return 0 if rep["ready"] else EXIT_REFUSED
        if a.cmd == "launch":
            cp, sha = load_checkpoint()
            _auth, asha = load_authorization(GS.AUTHORIZATION, GS.AUTHORIZATION_HASH)
            refuse_superseded(checkpoint_sha256=sha, authorization_sha256=asha)
            refuse_superseded(checkpoint_sha256=a.confirm_checkpoint_sha256, authorization_sha256=a.confirm_authorization_sha256)
            if a.confirm_checkpoint_sha256 != sha or a.confirm_authorization_sha256 != asha:
                print("REFUSED: the confirmations do not equal the frozen checkpoint and authorization sha256")
                return EXIT_REFUSED
            rep = preflight()
            print_report(rep)
            if not rep["ready"]:
                return EXIT_REFUSED
            import prod_supervisor as PS
            env = {"PATH": "/usr/bin:/bin", "HOME": os.environ.get("HOME", "/root"), "LANG": "C.UTF-8"}
            return PS.keep([sys.executable, "-B", str(Path(__file__).resolve()), "_supervise"], root=cp["runtime_root"], env=env)
        spec, cp = production_spec()
        if a.cmd == "_supervise":
            from gs_supervisor import SuccessorSupervisor
            return SuccessorSupervisor(spec, authz_loader=production_authz, preflight=_supervisor_preflight).run()
        if a.cmd == "status":
            print(json.dumps(L.Ledger.inspect(spec), indent=1, sort_keys=True, default=str))
            return 0
        pspec, pauthz = predecessor_objects()
        exists = (Path(spec.root) / "ledger.json").exists()
        rep = GC.composite_audit(pred_spec=pspec, pred_authz=pauthz, succ_spec=spec,
                                 succ_authz=production_authz() if exists else None,
                                 tolerance=GC.tolerance_for_production(_json(GS.BINDING)),
                                 qualification_shas=spec.qualification_record_sha256, successor_ledger_exists=exists)
        if a.cmd == "composite-audit":
            atomic_write_json(a.out, rep)
            print(json.dumps({k: rep[k] for k in ("state", "K4_READY", "old_cells_verified", "new_cells_verified", "problems")}))
            return 0
        if a.cmd == "attest":
            atomic_write_json(a.out, GC.build_composite_attestation(rep, successor_checkpoint_sha256=spec.checkpoint_sha256,
                                                                    predecessor_checkpoint_sha256=pspec.checkpoint_sha256))
            return 0
        print(json.dumps(GC.export_composite(rep, pred_root=pspec.root, succ_root=spec.root, out_dir=a.out)["cells"]))
        return 0
    except Refusal as r:
        print(f"REFUSED [{r.code}] {r.detail}")
        return EXIT_REFUSED


if __name__ == "__main__":
    raise SystemExit(main())
