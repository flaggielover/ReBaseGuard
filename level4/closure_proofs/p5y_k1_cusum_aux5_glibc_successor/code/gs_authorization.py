"""Pre-result run authorization of the new-glibc successor. NON-CERTIFYING.

The authorization is committed before any successor ledger exists and binds the successor checkpoint, the active
carry-over countersignature, Q6, the proposal, the predecessor binding, the exact host/runtime, the runtime root, the
universe 128-325, the residual and absolute caps, the containment state, the composite rule, the K4 downstream
obligation, the launch-preflight version and the ledger genesis rules. Every field recomputes from the checkpoint and
the campaign specification.

It yields the frozen prov_authorization.Authz object, so the frozen ProvenanceLedger genesis, envelope derivation,
verify_pair and prov_integrity.audit run unchanged. The countersignature it carries is the carry-over countersignature
(config/COUNTERSIGNATURE.json, verified by countersignature/code/carryover_countersignature.py). That countersignature
is necessary but not sufficient: launching also requires this authorization, the frozen checkpoint and a READY launch
preflight. This module never creates a production countersignature.
"""
from __future__ import annotations

import json
from pathlib import Path

import gs_schema as GS
import prod_cells
import prod_ledger as L
import prov_schema as S
from prod_common import Refusal, atomic_write_bytes, canonical, sha256_bytes, sha256_file
from prov_authorization import Authz, ledger_id

ENVELOPE_SCHEMA_FILE = GS.PROV_NS / "config/ENVELOPE_SCHEMA.json"


def executor_sources() -> dict:
    files = (sorted((GS.NS / "code").glob("*.py")) + sorted(GS.CS_CODE.glob("*.py"))
             + sorted((GS.PROV_NS / "code").glob("*.py")) + sorted((GS.PROD_NS / "code").glob("*.py"))
             + [GS.AUX5_NS / "code/qualify5.py", GS.AUX5_NS / "manifests/producer_manifest_v3.json"])
    got = {str(p.resolve().relative_to(GS.ROOT)): sha256_file(p) for p in files}
    return {"files": got, "EXECUTOR_HASH": sha256_bytes(canonical(got))}


def build_authorization(spec, cp: dict, *, authorization_id: str, run_id: str) -> dict:
    rows = [spec.cells[i] for i in sorted(spec.cell_indices)]
    host = cp["host"]
    return {
        "schema": GS.AUTH_SCHEMA, "status": GS.AUTH_STATUS, "mode": spec.mode, "result_bearing": False,
        "result_bearing_semantics": "a property of THIS authorization object (it carries no result); records become "
                                    "result-bearing only as verified pairs of a ledger born under it",
        "authorization_id": authorization_id, "production_run_id": run_id, "campaign_id": spec.campaign_id,
        "production_checkpoint_sha256": spec.checkpoint_sha256,
        "proposal_sha256": cp["proposal_sha256"], "q6_result_sha256": cp["q6_result_sha256"],
        "predecessor_binding_sha256": cp["predecessor"]["binding_sha256"],
        "carryover_manifest_sha256": cp["carryover_manifest"]["sha256"],
        "countersignature": {"sha256": cp["countersignature_sha256"], "path": cp["authority"]["countersignature_path"],
                             "semantics": "NECESSARY_BUT_NOT_SUFFICIENT: carry-over authorized by the independent "
                                          "countersignature; production launch additionally requires this "
                                          "authorization, the frozen checkpoint and a READY launch preflight"},
        "predecessor_checkpoint": {"checkpoint_sha256": cp["predecessor"]["checkpoint_sha256"],
                                   "status": GS.PREDECESSOR_STATUS,
                                   "authorization_sha256": cp["predecessor"]["authorization"]["authorization_sha256"],
                                   "countersignature_sha256": cp["predecessor"]["active_countersignature_sha256"],
                                   "ledger_id": cp["predecessor"]["authorization"]["ledger_id"],
                                   "runtime_root": cp["predecessor"]["runtime_root"]},
        "producer": {k: spec.identity[k] for k in S.IDENTITY_KEYS},
        "runtime": {"runtime_contract_hash": spec.identity["runtime_contract_hash"],
                    "worker_argv_template": list(spec.worker_template), "workers": len(spec.cores),
                    "cores": list(spec.cores), "checkout_path": str(spec.worker_cwd), "precision_bits": spec.precision_bits},
        "host": {**host["bound_facts"], "system_libraries_sha256": host["system_libraries_sha256"],
                 "packages": host["packages"], "boot_id": host["boot_id"]},
        "containment": host["containment"],
        "universe": {"detector": "CUSUM", "cells": len(rows), "first_index": min(spec.cell_indices),
                     "last_index": max(spec.cell_indices),
                     "cell_indices_sha256": sha256_bytes(canonical(sorted(spec.cell_indices))),
                     "geometry_digest": sha256_bytes(canonical(rows)), "cells_table_sha256": prod_cells.CELLS_SHA256,
                     "m_values": list(prod_cells.M_VALUES), "precision_bits": spec.precision_bits,
                     "carryover_cells": [cp["carryover_cells"][0], cp["carryover_cells"][-1]],
                     "rule": GS.CARRYOVER_RULE},
        "cap": {"cap_usec": spec.cap_usec, "reservation_usec": spec.reservation_usec, "invariant": L.INVARIANT,
                "absolute_campaign_cap_usec": cp["cost_cap"]["absolute_campaign_cap_usec"],
                "predecessor_settled_usec": cp["cost_cap"]["predecessor_settled_usec"]},
        "ledger": {"ledger_id": ledger_id(spec, run_id), "ledger_schema": L.LEDGER_SCHEMA,
                   "journal_schema": L.JOURNAL_SCHEMA, "runtime_root": str(spec.root),
                   "genesis_rule": "the GENESIS state and journal entry 0 carry this authorization block; the cells are "
                                   "exactly the production universe, the cap is the residual cap; no import transition",
                   "pre_genesis_files": list(L.PRE_GENESIS_FILES),
                   "production_start_predicate": cp["run_state"]["production_start_predicate"],
                   "supervisor_run_id_scheme": cp["id_schemes"]["supervisor_run_id"]},
        "provenance": {"envelope_schema": S.ENVELOPE_SCHEMA, "envelope_schema_file_sha256": sha256_file(ENVELOPE_SCHEMA_FILE),
                       "composite_rule": S.COMPOSITE_RULE},
        "composite": {"carryover_rule": GS.CARRYOVER_RULE, "audit_requirements": cp["composite_audit"],
                      "k4_downstream_obligation": cp["k4_composite_attestation"]},
        "executor_sources": executor_sources(),
        "launch_preflight": {"path": cp["entrypoint"]["path"], "version": GS.PREFLIGHT_VERSION,
                             "schema": GS.PREFLIGHT_SCHEMA, "checks": cp["entrypoint"]["checks"]},
        "conditions": cp["conditions"],
        "temporal_rule": "committed before the successor runtime root holds any genesis artifact; every envelope binds a "
                         "genesis entry naming this authorization and a RESERVED entry preceding its result",
    }


def write_authorization(auth: dict, path, hash_path) -> str:
    data = (json.dumps(auth, indent=1, sort_keys=True) + "\n").encode()
    atomic_write_bytes(path, data)
    atomic_write_bytes(hash_path, (sha256_bytes(data) + "\n").encode())
    return sha256_bytes(data)


def load_authorization(path, hash_path) -> tuple[dict, str]:
    path, hash_path = Path(path), Path(hash_path)
    if not path.exists() or not hash_path.exists():
        raise Refusal("AUTHORIZATION_MISSING", f"{path.name} or its hash file is absent")
    sha = sha256_file(path)
    if hash_path.read_text().strip() != sha:
        raise Refusal("AUTHORIZATION_INVALID", "authorization sha256 differs from its hash file")
    auth = json.loads(path.read_text())
    if auth.get("schema") != GS.AUTH_SCHEMA or auth.get("status") != GS.AUTH_STATUS or auth.get("result_bearing") is not False:
        raise Refusal("AUTHORIZATION_INVALID", "not a result-free pre-result successor run authorization")
    return auth, sha


def verify_authorization(auth: dict, spec, cp: dict) -> None:
    expected = build_authorization(spec, cp, authorization_id=auth.get("authorization_id"),
                                   run_id=auth.get("production_run_id"))
    if set(auth) != set(expected):
        raise Refusal("AUTHORIZATION_MISMATCH", f"field set differs: {sorted(set(auth) ^ set(expected))}")
    bad = sorted(k for k in expected if auth[k] != expected[k])
    if bad:
        raise Refusal("AUTHORIZATION_MISMATCH", f"authorization fields do not match this campaign: {bad}")
    if not isinstance(auth["authorization_id"], str) or not isinstance(auth["production_run_id"], str):
        raise Refusal("AUTHORIZATION_MISMATCH", "authorization id / run id")


def synthetic_countersignature(checkpoint_label: str) -> dict:
    return {"schema": GS.SYNTHETIC_CS_SCHEMA, "synthetic": True, "mode": "SYNTHETIC",
            "checkpoint_label": checkpoint_label, "reviewer": "SYNTHETIC_ACCEPTANCE_FIXTURE",
            "note": "a fixture; it can never satisfy a PRODUCTION campaign"}


def load_authz(spec, cp: dict, *, auth_path, hash_path, cs_path, cs_verifier=None) -> Authz:
    auth, sha = load_authorization(auth_path, hash_path)
    if auth["mode"] != spec.mode:
        raise Refusal("AUTHORIZATION_MISMATCH", f"authorization mode {auth['mode']} for a {spec.mode} campaign")
    verify_authorization(auth, spec, cp)
    cs_path = Path(cs_path)
    if not cs_path.exists():
        raise Refusal("COUNTERSIGNATURE_MISSING", "no carry-over countersignature; production is not authorized")
    raw = cs_path.read_bytes()
    cs_sha = sha256_bytes(raw)
    try:
        cs = json.loads(raw)
    except ValueError as exc:
        raise Refusal("COUNTERSIGNATURE_INVALID", str(exc)[:200]) from exc
    if cs_sha != cp["countersignature_sha256"] or cs_sha != auth["countersignature"]["sha256"]:
        raise Refusal("COUNTERSIGNATURE_INVALID", "the countersignature is not the one bound by the checkpoint and authorization")
    if spec.mode == "PRODUCTION":
        if cs.get("synthetic") is not False or cs_sha != GS.COUNTERSIGNATURE_SHA256:
            raise Refusal("COUNTERSIGNATURE_INVALID", "not the active carry-over countersignature")
        problems = cs_verifier() if cs_verifier is not None else ["no countersignature verifier supplied"]
        if problems:
            raise Refusal("COUNTERSIGNATURE_INVALID", f"carry-over countersignature does not verify: {problems[:4]}")
    elif cs.get("schema") != GS.SYNTHETIC_CS_SCHEMA or cs.get("synthetic") is not True:
        raise Refusal("COUNTERSIGNATURE_INVALID", "a synthetic campaign takes only a synthetic fixture")
    return Authz(auth, sha, cs, cs_sha, auth_bytes=Path(auth_path).read_bytes(), cs_bytes=raw)
