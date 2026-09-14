"""Build the new-glibc successor carry-over manifest, checkpoint and pre-result run authorization. NON-CERTIFYING.

  python make_gs_checkpoint.py manifest    -> config/CARRYOVER_MANIFEST.json   (derived only from PREDECESSOR_BINDING.json)
  python make_gs_checkpoint.py build       -> config/GLIBC_SUCCESSOR_CHECKPOINT.json + _HASH
  python make_gs_checkpoint.py authorize   -> config/RUN_AUTHORIZATION.json + _HASH (refused once production started)

Producer, runtime contract, scientific universe, geometry, precision, scientific hash, result schema, K4, the
predecessor qualification and the workers are inherited VERBATIM from the provenance checkpoint dd4c89d7. What is new:
the host (new glibc), the containment state, the universe 128-325, the residual cap, the runtime root and checkout, the
carry-over and composite layer, the conditions of the carry-over countersignature, and (repair r2) the sanctioned
END_OF_CAMPAIGN_SETTLEMENT path plus the supersession of checkpoint 51df2186 / authorization 03b9ca80.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import gs_schema as GS                                                           # noqa: E402
import carryover_countersignature as CC                                          # noqa: E402
import glibc_successor as G                                                      # noqa: E402
import gs_settle as ST                                                           # noqa: E402
import prod_ledger as L                                                          # noqa: E402
import prov_schema as S                                                          # noqa: E402
from gs_authorization import build_authorization, write_authorization           # noqa: E402
from gs_spec import load_checkpoint, spec_from_checkpoint                        # noqa: E402
from prod_common import Refusal, atomic_write_bytes, canonical, sha256_bytes, sha256_file  # noqa: E402

INHERITED = ("producer", "runtime_contract", "scientific_universe", "geometry", "precision", "scientific_hash",
             "result_schema", "k4", "qualification", "workers", "lifecycle", "ledger")
NS = GS.NS


def rel(p) -> str:
    return str(Path(p).resolve().relative_to(GS.ROOT))


def _json(p):
    return json.loads(Path(p).read_bytes())


def _run_evidence(p: Path) -> bool:
    """Acceptance and preflight generations are written after the checkpoint they test; they are never bound into it."""
    return any(part.startswith(("acceptance_r", "preflight_r")) for part in p.relative_to(NS / "evidence").parts)


def build_manifest() -> dict:
    b = _json(GS.BINDING)
    if sha256_file(GS.BINDING) != GS.BINDING_SHA256 or G.verify_binding(b):
        raise Refusal("MANIFEST_REFUSED", "the committed predecessor binding does not verify")
    return {"schema": GS.MANIFEST_SCHEMA, "binding_sha256": GS.BINDING_SHA256, "carryover_cells": [0, 127],
            "cells": b["cells"], "cells_digest_sha256": b["cells_digest_sha256"],
            "pairs_sha256": b["integrity"]["frozen_audit"]["pairs_sha256"],
            "record_envelope_digest_sha256": CC.record_envelope_digest(b), "host_clock": b["host_clock"],
            "rule": "derived only from config/PREDECESSOR_BINDING.json; its cells equal the binding's cells section; old "
                    "cells are consumed only through the composite audit, never imported as ledger rows"}


def settlement_binding() -> dict:
    mods = [NS / "code/gs_settle.py", NS / "code/gs_entry.py"]
    return {
        "command": ST.SETTLE_COMMAND, "version": ST.SETTLE_VERSION, "report_schema": ST.SETTLE_SCHEMA,
        "module_sha256": {rel(p): sha256_file(p) for p in mods},
        "document": {"path": rel(NS / "SETTLEMENT_REPAIR.md"), "sha256": sha256_file(NS / "SETTLEMENT_REPAIR.md")},
        "frozen_model": "prov_entry.py / prod_entry.py settle: campaign flock, authorization-bound ledger open, frozen "
                        "prod_ledger.reconcile (RUN_SETTLED), frozen unmatched_overhead + op_charge_overhead (OVERHEAD_CHARGED)",
        "frozen_transitions_only": list(ST.SETTLEMENT_EVENTS),
        "required": "after the successor supervisor exits with a terminal disposition and before gs_entry.py composite-audit, "
                    "attest and export: the frozen successor audit is INTEGRITY_READY_FOR_ADJUDICATION only on a COMPLETE ledger "
                    "whose supervisor runs are all settled, and the frozen supervisor never settles its own final run",
        "operator_sequence": ["gs_entry.py settle", "gs_entry.py composite-audit --out F", "gs_entry.py attest --out F",
                              "gs_entry.py export --out DIR"],
        "preconditions": [
            "target is a successor universe (128-325) outside every predecessor, blocked, qualification and repository root",
            "a ledger exists (ABSENT and PRE_GENESIS refused)",
            "no campaign process of any generation on the host; the campaign flock is free",
            "ledger continuous or journal-behind-one, validates, born under the presented run authorization",
            "terminal disposition (COMPLETE, HALTED or INCOMPLETE_BUDGET_EXHAUSTED); no open attempt; no sealed-but-unbound "
            "attempt; sealed record and bound envelope bytes unchanged",
            "every precondition is checked read-only before the first ledger write; a refusal writes nothing"],
        "evidence_rule": "every reaper line verifies; the one unsettled run is the latest run and ended EXITED; exactly one "
                         "keeper reap record matches it, with the disposition's exit code, taken after the run ended, whose "
                         "rusage is not smaller than the CPU already charged to the run; an uncharged keeper exit follows it; "
                         "otherwise REAPER_UNREADABLE / SETTLEMENT_EVIDENCE_MISSING / _AMBIGUOUS / _CONTRADICTORY",
        "charge_rule": "frozen: final run REAPER_RUSAGE extra = reap - children - self; each uncharged keeper exit once; only "
                       "the supervisor bucket moves; the cap is the residual cap and never changes",
        "never": ["a scientific record", "a provenance envelope", "a cell or attempt", "the disposition or halt", "the cap",
                  "a predecessor file", "an admission"],
        "idempotence": "a settled ledger returns ALREADY_SETTLED and writes nothing; a crash between or inside the two frozen "
                       "transitions is repaired by the frozen ledger open and completed by the next call, charging each run "
                       "and each reaper record at most once",
        "halted_or_budget_exhausted": "settled for accounting only; disposition and halt unchanged; never adjudication-ready",
        "synthetic_acceptance_rule": "every synthetic settlement runs `gs_entry.py settle --synthetic-spec CFG` in a fresh "
                                     "interpreter (refused inside every production root); no scenario settles through a helper",
    }


def build_checkpoint() -> dict:
    import gs_entry
    pcp = _json(GS.PROV_NS / "config/PROVENANCE_CHECKPOINT.json")
    if sha256_file(GS.PROV_NS / "config/PROVENANCE_CHECKPOINT.json") != G.EXPECTED["checkpoint_sha256"]:
        raise Refusal("CHECKPOINT_BUILD_REFUSED", "predecessor provenance checkpoint bytes differ")
    b, rq, q6 = _json(GS.BINDING), _json(NS / "config/REQUALIFICATION_PROTOCOL.json"), _json(NS / "evidence/requalification_r1/Q6_RESULT.json")
    post, capc = _json(NS / "evidence/containment/POST_STATE.json"), _json(NS / "config/CPU_CAP_CONTINUITY.json")
    for path, want in ((NS / "config/GLIBC_SUCCESSOR_PROPOSAL.json", GS.PROPOSAL_SHA256), (GS.COUNTERSIGNATURE, GS.COUNTERSIGNATURE_SHA256),
                       (NS / "evidence/requalification_r1/Q6_RESULT.json", GS.Q6_RESULT_SHA256), (GS.BINDING, GS.BINDING_SHA256)):
        if sha256_file(path) != want:
            raise Refusal("CHECKPOINT_BUILD_REFUSED", f"{path.name} differs from its governed sha256")
    if q6["Q6_FINAL"] != "PASS" or not GS.CARRYOVER_MANIFEST.exists():
        raise Refusal("CHECKPOINT_BUILD_REFUSED", "Q6 is not PASS or the carry-over manifest is absent")
    if not GS.SUPERSESSION_RECORD.exists() or GS.FREEZE_RECORD.exists():
        raise Refusal("CHECKPOINT_BUILD_REFUSED", "the supersession record must exist and no freeze record may be present")
    sup = _json(GS.SUPERSESSION_RECORD)
    if (sup["superseded"]["checkpoint_sha256"] != GS.SUPERSEDED_CHECKPOINT_SHA256
            or sup["superseded"]["run_authorization_sha256"] != GS.SUPERSEDED_AUTHORIZATION_SHA256
            or sup["statements"]["used_for_production_genesis"] is not False):
        raise Refusal("CHECKPOINT_BUILD_REFUSED", "the supersession record does not name the superseded objects")
    cp = {k: pcp[k] for k in INHERITED}
    bound = set(G.SYSTEM_LIBRARIES)
    host_facts = {k: rq["host"][k] for k in ("host_name", "machine_id_sha256", "cpu_model", "logical_cpus", "physical_cores",
                                             "smt_groups", "kernel_release", "libc_path", "libc_sha256", "glibc_package_version")}
    q6_quals = {f"Q6_{k}": v["record_sha256"] for k, v in q6["runs"].items()}
    cp.update({
        "schema": GS.CHECKPOINT_SCHEMA, "status": "FROZEN_PRE_PRODUCTION", "frozen_utc": "2026-09-14",
        "campaign_id": GS.CAMPAIGN_ID, "result_bearing": False, "production_launched": False,
        "SCIENTIFIC_PRODUCER": "UNCHANGED_AUX5", "NEW_SCIENTIFIC_COMPUTE": "NONE_IN_THIS_CHECKPOINT",
        "proposal_sha256": GS.PROPOSAL_SHA256, "carryover_rule_sha256": sha256_file(NS / "CARRYOVER_PROTOCOL.md"),
        "countersignature_sha256": GS.COUNTERSIGNATURE_SHA256, "q6_result_sha256": GS.Q6_RESULT_SHA256,
        "carryover_cells": list(GS.OLD_CELLS), "production_universe": list(GS.NEW_CELLS),
        "successor_residual_cap_usec": GS.RESIDUAL_CAP_US,
        "predecessor": {
            "checkpoint_sha256": G.EXPECTED["checkpoint_sha256"],
            "freeze_record_sha256": sha256_file(GS.PROV_NS / "config/FREEZE_RECORD.json"),
            "authorization": b["predecessor"]["production_authorization"],
            "active_countersignature_sha256": G.EXPECTED["countersignature_sha256"],
            "revoked_countersignature_sha256": CC.REVOKED_COUNTERSIGNATURE,
            "runtime_root": str(GS.PREDECESSOR_RUNTIME_ROOT), "checkout_path": str(GS.PREDECESSOR_CHECKOUT_PATH),
            "files_sha256": b["files"], "ledger_state_sha256": b["ledger_state_sha256"],
            "genesis_entry_sha256": b["journal"]["genesis_entry_sha256"], "last_entry_sha256": b["journal"]["last_entry_sha256"],
            "cells_digest_sha256": b["cells_digest_sha256"], "pairs_sha256": b["integrity"]["frozen_audit"]["pairs_sha256"],
            "record_envelope_digest_sha256": GS.RECORD_ENVELOPE_DIGEST, "binding_sha256": GS.BINDING_SHA256,
            "disposition": b["predecessor"]["disposition"], "stop": b["predecessor"]["stop"],
            "unsettled_supervisor_runs": [GS.UNSETTLED_RUN], "immutable": True,
            "rule": "never opened with a lock, settled, written, moved or deleted; its terminal disposition stays authoritative"},
        "carryover_manifest": {"path": rel(GS.CARRYOVER_MANIFEST), "sha256": sha256_file(GS.CARRYOVER_MANIFEST),
                               "carryover_cells": [0, 127], "rule": GS.CARRYOVER_RULE},
        "requalification": {"protocol_sha256": sha256_file(NS / "config/REQUALIFICATION_PROTOCOL.json"),
                            "reference_sha256": sha256_file(NS / "config/Q6_REFERENCE.json"),
                            "result_sha256": GS.Q6_RESULT_SHA256, "verdict": q6["Q6_FINAL"],
                            "c_max_cpu_seconds": q6["qualification_cpu_accounting"]["c_max_cpu_seconds"]},
        "host": {"bound_facts": host_facts, "system_libraries_sha256": rq["host"]["system_libraries_sha256"],
                 "packages": rq["host"]["packages"], "boot_id": b["host_clock"]["boot_id"],
                 "guard_before_every_admission": list(pcp["host"]["guard_before_every_admission"])
                 + sorted(bound) + ["boot_id"],
                 "containment": {**{f"{n}_sha256": sha256_file(NS / f"evidence/containment/{n}.json")
                                    for n in ("PRE_STATE", "POST_STATE", "POST_RUN_STATE")},
                                 "post_state": {k: post[k] for k in GS.CONTAINMENT_KEYS}},
                 "drift_rule": "any difference in a bound fact, system library, package, the boot id or the containment "
                               "state refuses the launch; a difference before an admission halts admissions (HOST_DRIFT)"},
        "qualification_firewall": {"record_file_sha256": {**pcp["qualification"]["record_file_sha256"], **q6_quals},
                                   "rule": "no production record of either half may be byte-identical to a qualification "
                                           "or Q6 record (QUALIFICATION_RECORD_REUSE)"},
        "checkout_path": str(GS.CHECKOUT_PATH), "runtime_root": str(GS.SUCCESSOR_RUNTIME_ROOT),
        "refused_runtime_roots": [str(r) for r in GS.REFUSED_ROOTS],
        "cost_cap": {**{k: pcp["cost_cap"][k] for k in ("c_max_cpu_seconds", "cap_formula_py_sha256", "formula_file_sha256",
                                                          "formula_path", "admission_rule", "accounting_unit")},
                     "absolute_campaign_cap_usec": GS.ABSOLUTE_CAP_US, "predecessor_settled_usec": GS.PREDECESSOR_SETTLED_US,
                     "successor_residual_cap_usec": GS.RESIDUAL_CAP_US, "cap_usec": GS.RESIDUAL_CAP_US,
                     "reservation_usec": GS.RESERVATION_US, "invariant": list(GS.INVARIANT),
                     "cpu_cap_continuity_sha256": sha256_file(NS / "config/CPU_CAP_CONTINUITY.json"),
                     "predecessor_settlement_components_usec": capc["predecessor_settlement_components_usec"],
                     "excluded_from_accounting": {
                         "qualification_cpu_seconds": pcp["cost_cap"]["excluded_from_accounting"]["qualification_cpu_seconds"],
                         "q6_requalification_cpu_seconds": q6["qualification_cpu_accounting"]["total_cpu_seconds"],
                         "rule": "qualification and Q6 CPU are not production cells: excluded and disclosed",
                         "synthetic_acceptance": "separate synthetic ledgers; never counted"},
                     "rules": ["the successor ledger genesis cap is the residual cap and never changes (CAP_CHANGE_FORBIDDEN)",
                               "predecessor consumption is charged once, as absolute - residual; it is never reset or re-imported",
                               "the absolute 300 CPU-h cap is never raised",
                               "end-of-campaign settlement charges only the frozen reaper rules into the successor ledger"]},
        "run_state": {"pre_genesis_files": list(L.PRE_GENESIS_FILES),
                      "production_start_predicate": "PRODUCTION_STARTED iff ledger.json or journal.jsonl exists in the "
                                                    "successor runtime root; a root holding only PRE_GENESIS_FILES is not started",
                      "acceptable_before_launch": ["ABSENT", "PRE_GENESIS"],
                      "relaunch": "a ledger born under this authorization that is OPEN or DRAINED, with no halt and no "
                                  "terminal disposition, may be relaunched; anything else is refused",
                      "end_of_campaign": "a terminal ledger is never relaunched; it is settled by gs_entry.py settle, then "
                                         "consumed only through the composite audit"},
        "id_schemes": {"authorization_id": GS.AUTHORIZATION_ID, "production_run_id": GS.RUN_ID,
                       "supervisor_run_id": "R<UTC %Y%m%dT%H%M%SZ>-<pid> (frozen prod_supervisor)",
                       "ledger_id": "sha256(canonical({schema: prov LEDGER_ID_SCHEMA, ledger_schema, campaign_id, "
                                    "production_run_id, runtime_root, production_checkpoint_sha256})) (frozen prov_authorization)"},
        "composite_audit": {"module": f"{GS.NS_REL}/code/gs_composite.py",
                            "requirements": ["frozen prov_integrity.audit unchanged on the predecessor ledger",
                                             f"tolerate exactly {GS.STOP_ISSUE} (the bound HOST_DRIFT stop) and "
                                             f"D_unsettled_supervisor_runs ({GS.UNSETTLED_RUN}); any other issue refuses",
                                             "all 128 predecessor pairs verified; digest equal to the binding",
                                             "frozen prov_integrity.audit unchanged on the successor ledger",
                                             "the successor ledger is settled by gs_entry.py settle first; no successor audit "
                                             "issue is ever tolerated",
                                             "old/new disjoint; union exactly 0-325; one producer identity",
                                             "qualification and Q6 records never reused", "both provenance halves disclosed",
                                             "INCOMPLETE until the successor ledger is COMPLETE and settled; never K4-ready before"]},
        "k4_composite_attestation": {"schema": "rebaseguard.p5y.k1.cusum-production.integrity-attestation.v1",
                                     "cells_verified": 326, "all_scientific_hashes_verified": True,
                                     "producer_identity_hash": pcp["producer"]["record_identity"]["producer_identity_hash"],
                                     "producer_checkpoint_sha256": "this successor checkpoint",
                                     "binds_predecessor_checkpoint": G.EXPECTED["checkpoint_sha256"],
                                     "disclosure": {"cells_0_127": "predecessor authorized campaign",
                                                    "cells_128_325": "successor campaign"},
                                     "k4_assembly_run": False},
        "END_OF_CAMPAIGN_SETTLEMENT": settlement_binding(),
        "supersedes": {"checkpoint_sha256": GS.SUPERSEDED_CHECKPOINT_SHA256,
                       "run_authorization_sha256": GS.SUPERSEDED_AUTHORIZATION_SHA256,
                       "record_path": rel(GS.SUPERSESSION_RECORD), "record_sha256": sha256_file(GS.SUPERSESSION_RECORD),
                       "reason": "END_OF_CAMPAIGN_SETTLEMENT_PATH_MISSING found by the independent pre-launch review; the "
                                 "superseded objects were never used for a production genesis and are refused by name"},
        "conditions": {k: {"text": v, "enforced_by": e} for (k, v), e in zip(CC.CONDITIONS.items(), (
            "gs_entry preflight G01-G18 and gs_spec.load_checkpoint", "gs_composite.composite_audit",
            "gs_entry.py settle + gs_composite.build_composite_attestation", "gs_entry launch requires READY preflight + "
            "frozen checkpoint + run authorization + explicit confirmations", "gs_spec.SuccessorSpec.host_guard + preflight G11/G12"))},
        "authority": {"carryover_rule": GS.CARRYOVER_RULE, "composite_rule": S.COMPOSITE_RULE,
                      "countersignature_path": rel(GS.COUNTERSIGNATURE),
                      "run_authorization": {"path": rel(GS.AUTHORIZATION), "schema": GS.AUTH_SCHEMA,
                                            "authorization_id": GS.AUTHORIZATION_ID, "production_run_id": GS.RUN_ID},
                      "sanctioned_consumer_path": "gs_entry.py settle -> gs_composite.composite_audit -> "
                                                  "build_composite_attestation / export_composite"},
        "entrypoint": {"path": f"{GS.NS_REL}/code/gs_entry.py", "checks": list(gs_entry.PREFLIGHT_CHECKS),
                       "version": GS.PREFLIGHT_VERSION, "commands": ["preflight", "launch", "settle", "status",
                                                                     "composite-audit", "attest", "export"]},
    })
    cp["ledger"] = {**pcp["ledger"], "successor_universe": "cells exactly 128-325; cells 0-127 are never rows"}
    cp["lifecycle"] = {**pcp["lifecycle"], "successor_guard": "frozen host facts + 11 system libraries + boot id before every admission",
                       "end_of_campaign_settlement": "the frozen supervisor leaves its final run unsettled; gs_entry.py settle "
                                                     "settles it with the frozen reaper rules before any composite audit"}
    srcs = dict(pcp["bound_sources"])
    extra = ([GS.PROV_NS / f"config/{n}" for n in ("PROVENANCE_CHECKPOINT.json", "PROVENANCE_CHECKPOINT_HASH", "FREEZE_RECORD.json",
                                                    "RUN_AUTHORIZATION.json", "RUN_AUTHORIZATION_HASH", "COUNTERSIGNATURE.json",
                                                    "ENVELOPE_SCHEMA.json")]
             + [GS.PROV_NS / "evidence/acceptance_r1/ACCEPTANCE_RESULT.json"]
             + sorted((NS / "code").glob("*.py")) + sorted((NS / "tests").glob("*.py"))
             + sorted((NS / "countersignature").rglob("*.py")) + [NS / "countersignature/README.md", NS / "countersignature/COUNTERSIGNATURE_HASH"]
             + [NS / n for n in ("CARRYOVER_PROTOCOL.md", "SUCCESSOR_CHECKPOINT_SPEC.md", "HOST_CONTAINMENT_PLAN.md",
                                 "HOST_DRIFT_FORENSIC_AUDIT.md", "README.md", "SETTLEMENT_REPAIR.md")]
             + [NS / "config" / n for n in ("GLIBC_SUCCESSOR_PROPOSAL.json", "GLIBC_SUCCESSOR_PROPOSAL_HASH", "PREDECESSOR_BINDING.json",
                                            "CPU_CAP_CONTINUITY.json", "REQUALIFICATION_PROTOCOL.json", "Q6_REFERENCE.json",
                                            "COUNTERSIGNATURE.json", "CARRYOVER_MANIFEST.json")]
             + sorted(p for p in (NS / "evidence").rglob("*") if p.is_file() and not _run_evidence(p)))
    tracked = set(subprocess.run(["git", "-C", str(GS.ROOT), "ls-files", "-z", "--", GS.NS_REL, str(GS.PROV_NS.relative_to(GS.ROOT))],
                                 capture_output=True, check=True).stdout.decode().split("\0")) - {""}
    extra = [p for p in extra if rel(p) in tracked]          # only committed files: an ignored local file is never bound
    srcs.update({rel(p): sha256_file(p) for p in extra})
    untracked = sorted(r for r in srcs if subprocess.run(["git", "-C", str(GS.ROOT), "ls-files", "--error-unmatch", r],
                                                         capture_output=True).returncode != 0)
    if untracked:
        raise Refusal("CHECKPOINT_BUILD_REFUSED", f"bound sources not tracked by git: {untracked[:6]}")
    missing = [r for r in (f"{GS.NS_REL}/code/gs_settle.py", f"{GS.NS_REL}/code/gs_entry.py", f"{GS.NS_REL}/SETTLEMENT_REPAIR.md",
                           rel(GS.SUPERSESSION_RECORD), f"{GS.NS_REL}/tests/gs_scenarios_c.py") if r not in srcs]
    if missing:
        raise Refusal("CHECKPOINT_BUILD_REFUSED", f"settlement repair sources not bound: {missing}")
    cp["bound_sources"] = dict(sorted(srcs.items()))
    return cp


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["manifest", "build", "authorize"])
    a = ap.parse_args(argv)
    try:
        if a.action == "manifest":
            data = (json.dumps(build_manifest(), indent=1, sort_keys=True) + "\n").encode()
            atomic_write_bytes(GS.CARRYOVER_MANIFEST, data)
            print(json.dumps({"carryover_manifest_sha256": sha256_bytes(data)}))
        elif a.action == "build":
            data = (json.dumps(build_checkpoint(), indent=1, sort_keys=True) + "\n").encode()
            if sha256_bytes(data) == GS.SUPERSEDED_CHECKPOINT_SHA256:
                raise Refusal("CHECKPOINT_BUILD_REFUSED", "the build reproduced the superseded checkpoint")
            atomic_write_bytes(GS.CHECKPOINT, data)
            atomic_write_bytes(GS.CHECKPOINT_HASH, (sha256_bytes(data) + "\n").encode())
            print(json.dumps({"checkpoint_sha256": sha256_bytes(data)}))
        else:
            cp, sha = load_checkpoint()
            root = GS.SUCCESSOR_RUNTIME_ROOT
            if sha == GS.SUPERSEDED_CHECKPOINT_SHA256:
                raise Refusal("AUTHORIZATION_REFUSED", "the superseded checkpoint is never authorized")
            if root.exists() or (root / "ledger.json").exists() or (root / "journal.jsonl").exists():
                raise Refusal("AUTHORIZATION_NOT_PRE_RESULT", f"{root} exists; a pre-result authorization precedes any runtime root")
            spec = spec_from_checkpoint(cp, sha)
            auth = build_authorization(spec, cp, authorization_id=GS.AUTHORIZATION_ID, run_id=GS.RUN_ID)
            data_sha = write_authorization(auth, GS.AUTHORIZATION, GS.AUTHORIZATION_HASH)
            if data_sha == GS.SUPERSEDED_AUTHORIZATION_SHA256:
                raise Refusal("AUTHORIZATION_REFUSED", "the build reproduced the superseded authorization")
            print(json.dumps({"run_authorization_sha256": data_sha, "ledger_id": auth["ledger"]["ledger_id"]}))
    except Refusal as r:
        print(f"REFUSED [{r.code}] {r.detail}")
        return 30
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
