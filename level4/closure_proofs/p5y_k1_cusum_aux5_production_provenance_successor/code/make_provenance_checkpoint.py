"""Build the additive CUSUM Aux5 provenance successor checkpoint and its pre-result run authorization. NON-CERTIFYING.

  python make_provenance_checkpoint.py schema      -> config/ENVELOPE_SCHEMA.json
  python make_provenance_checkpoint.py build       -> config/PROVENANCE_CHECKPOINT.json (+ _HASH)
  python make_provenance_checkpoint.py authorize   -> config/RUN_AUTHORIZATION.json (+ _HASH); awaits a countersignature

The predecessor checkpoint (4026f296) is not rewritten. Every scientific, producer, runtime, host, geometry, precision,
hash, cap, qualification and K4 section is inherited VERBATIM (checked by preflight P04). What is new is the
production-authority layer.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import prov_schema as S                                                                  # noqa: E402
import prod_ledger as L                                                                  # noqa: E402
from prod_common import ROOT, Refusal, atomic_write_bytes, rel, sha256_bytes, sha256_file  # noqa: E402
from prov_authorization import build_authorization, write_authorization                 # noqa: E402
from prov_spec import (AUTHORIZATION, AUTHORIZATION_HASH, CHECKPOINT, CHECKPOINT_HASH,    # noqa: E402
                       PRODUCTION_RUNTIME_ROOT, production_spec)

INHERITED = ("producer", "runtime_contract", "host", "workers", "scientific_universe", "geometry", "precision",
             "scientific_hash", "cost_cap", "qualification", "k4", "checkout_path")
AUTHORIZATION_ID = "CUSUM-AUX5-PROD-AUTH-001"
RUN_ID = "CUSUM-AUX5-PROD-R1"
ENVELOPE_SCHEMA_FILE = S.NS / "config/ENVELOPE_SCHEMA.json"

AUTHORITATIVE_RULE = (
    "Derived from the frozen K1 checkpoint ('an explicit separate production authorization is then necessary; it must "
    "not flip the guard inside this frozen checkpoint') and the PS1 production precedent (LAUNCH_AUTHORIZATION + "
    "production_provenance + sealed production cell record + PRODUCTION_LEDGER.completed_cells + Lane C integrity "
    "audit): a scientific artifact is PRODUCTION-AUTHORIZED iff it was produced under a hash-bound run authorization "
    "that existed before its result; RESULT-BEARING iff, in addition, it is sealed into that authorization's production "
    "ledger with a provenance object that binds the artifact bytes to the authorization, checkpoint, producer, cell and "
    "run; DISPOSITION-BEARING iff, in addition, the integrity audit admits it for adjudication. No inline boolean in the "
    "scientific artifact is part of this rule.")


def build() -> dict:
    pred_ns = S.PRED_NS
    pred_raw = (pred_ns / "config/PRODUCTION_CHECKPOINT.json").read_bytes()
    psha = sha256_bytes(pred_raw)
    if psha != S.PREDECESSOR["checkpoint_sha256"] or (pred_ns / "config/PRODUCTION_CHECKPOINT_HASH").read_text().strip() != psha:
        raise Refusal("CHECKPOINT_BUILD_REFUSED", "predecessor checkpoint bytes differ from the recorded blocked checkpoint")
    pred_freeze = json.loads((pred_ns / "config/FREEZE_RECORD.json").read_text())
    if pred_freeze.get("production_checkpoint_sha256") != psha or pred_freeze.get("production_launched") is not False:
        raise Refusal("CHECKPOINT_BUILD_REFUSED", "predecessor freeze record")
    if not ENVELOPE_SCHEMA_FILE.exists() or json.loads(ENVELOPE_SCHEMA_FILE.read_text()) != S.envelope_schema_document():
        raise Refusal("CHECKPOINT_BUILD_REFUSED", "run `schema` first: ENVELOPE_SCHEMA.json is absent or stale")
    pred = json.loads(pred_raw)
    cp = {k: pred[k] for k in INHERITED}
    cp["result_schema"] = {**pred["result_schema"], "record_flags_semantics": S.FLAG_SEMANTICS,
                           "certifier_constant_flags": S.CERTIFIER_CONSTANT_FLAGS,
                           "superseded_predecessor_semantics": "the predecessor's reading (production status conferred by "
                                                               "the ledger seal alone) is not relied on here"}
    cp["ledger"] = {**pred["ledger"], "provenance_extension": {
        "genesis": "state.production_authorization and journal entry 0 detail.production_authorization carry the "
                   "authorization block {authorization_sha256, authorization_id, production_run_id, ledger_id, "
                   "countersignature_sha256}",
        "attempt_provenance": "attempts[aid].provenance = {schema, envelope, envelope_sha256}, set once by "
                              f"{S.PROVENANCE_EVENT}", "envelope_root": "provenance/"}}
    cp["lifecycle"] = {**pred["lifecycle"], "provenance_binding": (
        "immediately after a SEALED transition the envelope is derived, written read-only, verified as a pair and bound "
        "by one PROVENANCE_BOUND transition; a sealed-but-unbound attempt is not a production result and is bound by the "
        "next supervisor before any admission or disposition")}
    cp.update({
        "schema": S.CHECKPOINT_SCHEMA, "status": "FROZEN_PRE_PRODUCTION",
        "campaign_id": "p5y_k1_cusum_aux5_production_provenance_r1",
        "frozen_utc": time.strftime("%Y-%m-%d", time.gmtime()), "result_bearing": False, "production_launched": False,
        "PREDECESSOR_CHECKPOINT": S.PREDECESSOR["status"], "SCIENTIFIC_PRODUCER": "UNCHANGED_AUX5",
        "NEW_SCIENTIFIC_COMPUTE": "NONE",
        "PRODUCTION_AUTHORITY_LAYER": ("COMPOSITE_PROVENANCE: pre-result run authorization + independent countersignature "
                                       "-> authorization-bound ledger genesis -> sealed attempt -> hash-bound production "
                                       "provenance envelope (PROVENANCE_BOUND) -> pair-verifying integrity audit"),
        "runtime_root": str(PRODUCTION_RUNTIME_ROOT),
        "predecessor": {**S.PREDECESSOR, "freeze_record_sha256": sha256_file(pred_ns / "config/FREEZE_RECORD.json"),
                        "blocked_by": "independent countersignature (relayed by the user, 2026-09-13): record-level "
                                      "production-authority semantics", "preserved": "unmodified; fenced on host"},
        "authority": {
            "authoritative_rule": AUTHORITATIVE_RULE, "composite_rule": S.COMPOSITE_RULE,
            "run_authorization": {"schema": S.AUTH_SCHEMA, "path": rel(AUTHORIZATION), "status": S.AUTH_STATUS,
                                  "authorization_id": AUTHORIZATION_ID, "production_run_id": RUN_ID,
                                  "countersignature": {"schema": S.COUNTERSIGN_SCHEMA, "required_verdict": S.APPROVED,
                                                       "path": "level4/closure_proofs/p5y_k1_cusum_aux5_production_provenance_successor/config/COUNTERSIGNATURE.json",
                                                       "created_by": "the independent reviewer only"}},
            "envelope": {"schema": S.ENVELOPE_SCHEMA, "schema_file": rel(ENVELOPE_SCHEMA_FILE),
                         "schema_file_sha256": sha256_file(ENVELOPE_SCHEMA_FILE), "binding_event": S.PROVENANCE_EVENT},
            "sanctioned_consumer_path": "prov_integrity.audit -> export_pairs / build_k4_attestation; the predecessor "
                                        "export and attest commands are non-authoritative (their ledgers carry no "
                                        "authorization block and are refused by check_genesis)"},
        "entrypoint": {"path": rel(S.NS / "code/prov_entry.py"),
                       "checks": ["P01_checkpoint_and_freeze", "P02_bound_sources", "P03_predecessor_frozen_and_fenced",
                                  "P04_inherited_sections_unchanged", "P05_provenance_schemas", "P06_run_authorization",
                                  "P07_independent_countersignature", "P08_synthetic_acceptance", "P09_run_state",
                                  "P10_host_idle"],
                       "no_self_authorization": "no code path creates a production countersignature"},
    })
    bound = dict(pred["bound_sources"])
    extra = sorted((S.NS / "code").glob("*.py")) + sorted((S.NS / "tests").glob("*.py")) + [ENVELOPE_SCHEMA_FILE] + [
        pred_ns / "config/PRODUCTION_CHECKPOINT.json", pred_ns / "config/PRODUCTION_CHECKPOINT_HASH",
        pred_ns / "config/FREEZE_RECORD.json", pred_ns / "evidence/acceptance_r1/ACCEPTANCE_RESULT.json"]
    bound.update({rel(p): sha256_file(p) for p in extra})
    cp["bound_sources"] = dict(sorted(bound.items()))
    return cp


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["schema", "build", "authorize"])
    a = ap.parse_args(argv)
    try:
        if a.action == "schema":
            atomic_write_bytes(ENVELOPE_SCHEMA_FILE, (json.dumps(S.envelope_schema_document(), indent=1, sort_keys=True) + "\n").encode())
            print("ENVELOPE_SCHEMA.json", sha256_file(ENVELOPE_SCHEMA_FILE))
        elif a.action == "build":
            cp = build()
            data = (json.dumps(cp, indent=1, sort_keys=True) + "\n").encode()
            atomic_write_bytes(CHECKPOINT, data)
            atomic_write_bytes(CHECKPOINT_HASH, (sha256_bytes(data) + "\n").encode())
            print(json.dumps({"provenance_checkpoint_sha256": sha256_bytes(data), "bound_sources": len(cp["bound_sources"])}))
        else:
            spec, cp = production_spec()
            if Path(cp["runtime_root"]).exists():
                raise Refusal("AUTHORIZATION_NOT_PRE_RESULT", f"{cp['runtime_root']} already exists")
            auth = build_authorization(spec, authorization_id=AUTHORIZATION_ID, run_id=RUN_ID,
                                       host=cp["host"]["bound_facts"])
            print(json.dumps({"run_authorization_sha256": write_authorization(auth, AUTHORIZATION, AUTHORIZATION_HASH),
                              "status": auth["status"], "ledger_id": auth["ledger"]["ledger_id"]}))
    except Refusal as r:
        print(f"REFUSED [{r.code}] {r.detail}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
