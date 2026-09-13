"""Pre-result run authorization and independent countersignature. NON-CERTIFYING.

PS1 precedent (p5y_k1_ps1_production): config/LAUNCH_AUTHORIZATION.json + _HASH is committed before any result;
`result_bearing: false` is a property of that authorization OBJECT (the launcher refuses one that is not false); every
sealed production cell record carries production_provenance.production_authorization_hash equal to its sha256.

This successor keeps that shape and adds one gate: the authorization is NOT self-activating. A ledger GENESIS, and
therefore any result, requires an independent COUNTERSIGNATURE that binds the authorization sha256 and the freeze
record. This module verifies countersignatures. It can create one only for a SYNTHETIC authorization; there is no
code path that creates a production countersignature.
"""
from __future__ import annotations

import json
from pathlib import Path

import prov_schema as S
import prod_cells
import prod_ledger as L
from prod_common import ROOT, Refusal, atomic_write_bytes, canonical, sha256_bytes, sha256_file

ENVELOPE_SCHEMA_FILE = S.NS / "config/ENVELOPE_SCHEMA.json"


class Authz:
    """A verified (authorization, countersignature) pair and the block every genesis and envelope must carry."""

    def __init__(self, auth: dict, auth_sha: str, cs: dict, cs_sha: str, *, auth_bytes: bytes = b"", cs_bytes: bytes = b""):
        self.auth, self.auth_sha, self.cs, self.cs_sha = auth, auth_sha, cs, cs_sha
        self.auth_bytes, self.cs_bytes = auth_bytes, cs_bytes
        self.block = {"authorization_sha256": auth_sha, "authorization_id": auth["authorization_id"],
                      "production_run_id": auth["production_run_id"], "ledger_id": auth["ledger"]["ledger_id"],
                      "countersignature_sha256": cs_sha}


def ledger_id(spec, run_id: str) -> str:
    return sha256_bytes(canonical({"schema": S.LEDGER_ID_SCHEMA, "ledger_schema": L.LEDGER_SCHEMA,
                                   "campaign_id": spec.campaign_id, "production_run_id": run_id,
                                   "runtime_root": str(spec.root), "production_checkpoint_sha256": spec.checkpoint_sha256}))


def executor_sources_sha256() -> dict:
    """sha256 of every module on the production execution surface (PS1 scientific_adapter_hash analogue)."""
    files = sorted((S.NS / "code").glob("*.py")) + sorted((S.PRED_NS / "code").glob("*.py")) + [
        ROOT / "level4/closure_proofs/p5y_k1_cusum_aux5_successor/code/qualify5.py",
        ROOT / "level4/closure_proofs/p5y_k1_cusum_aux5_successor/manifests/producer_manifest_v3.json"]
    got = {str(p.resolve().relative_to(ROOT)): sha256_file(p) for p in files}
    return {"files": got, "EXECUTOR_HASH": sha256_bytes(canonical(got))}


def build_authorization(spec, *, authorization_id: str, run_id: str, host: dict) -> dict:
    rows = [spec.cells[i] for i in sorted(spec.cell_indices)]
    return {
        "schema": S.AUTH_SCHEMA, "status": S.AUTH_STATUS, "mode": spec.mode, "result_bearing": False,
        "result_bearing_semantics": "a property of THIS authorization object (it carries no result), as in the PS1 "
                                    "launch authorization; it is not a statement about the records it governs",
        "authorization_id": authorization_id, "production_run_id": run_id, "campaign_id": spec.campaign_id,
        "production_checkpoint_sha256": spec.checkpoint_sha256, "predecessor_checkpoint": dict(S.PREDECESSOR),
        "producer": {k: spec.identity[k] for k in S.IDENTITY_KEYS},
        "runtime": {"runtime_contract_hash": spec.identity["runtime_contract_hash"],
                    "worker_argv_template": list(spec.worker_template), "workers": len(spec.cores),
                    "cores": list(spec.cores)},
        "host": dict(host),
        "universe": {"detector": "CUSUM", "cells": len(rows), "cell_indices_sha256": sha256_bytes(canonical(sorted(spec.cell_indices))),
                     "geometry_digest": sha256_bytes(canonical(rows)), "cells_table_sha256": prod_cells.CELLS_SHA256,
                     "m_values": list(prod_cells.M_VALUES), "precision_bits": spec.precision_bits,
                     "far_field_obligation": {"work_id": "CUSUM:-1:far_field:all_m",
                                              "status": "INHERITED (binding K1/P5X-T3 far-field certificate, "
                                                        "adjudicated PASS; unchanged, not produced by this run)"}},
        "cap": {"cap_usec": spec.cap_usec, "reservation_usec": spec.reservation_usec, "invariant": L.INVARIANT},
        "ledger": {"ledger_id": ledger_id(spec, run_id), "ledger_schema": L.LEDGER_SCHEMA,
                   "journal_schema": L.JOURNAL_SCHEMA, "runtime_root": str(spec.root),
                   "genesis_rule": "the ledger GENESIS state and journal entry 0 carry this authorization block; a "
                                   "genesis is refused without a verified countersignature"},
        "provenance": {"envelope_schema": S.ENVELOPE_SCHEMA, "envelope_schema_file_sha256": sha256_file(ENVELOPE_SCHEMA_FILE),
                       "composite_rule": S.COMPOSITE_RULE},
        "executor_sources": executor_sources_sha256(),
        "countersignature": {"schema": S.COUNTERSIGN_SCHEMA, "required_verdict": S.APPROVED,
                             "rule": "an independent reviewer commits config/COUNTERSIGNATURE.json binding this file's "
                                     "sha256 and the freeze record; this tooling never creates it"},
        "temporal_rule": "committed before any production ledger exists; every envelope binds a genesis entry that "
                         "names this authorization and a RESERVED entry that precedes its result; no retroactive "
                         "authorization is possible because an existing ledger without this block is refused",
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
    if auth.get("schema") != S.AUTH_SCHEMA or auth.get("result_bearing") is not False or auth.get("status") != S.AUTH_STATUS:
        raise Refusal("AUTHORIZATION_INVALID", "not a result-free pre-result run authorization")
    return auth, sha


def verify_authorization(auth: dict, spec) -> None:
    """Every field must equal the value recomputed from the live campaign specification."""
    expected = build_authorization(spec, authorization_id=auth.get("authorization_id"),
                                   run_id=auth.get("production_run_id"), host=auth.get("host") or {})
    if set(auth) != set(expected):
        raise Refusal("AUTHORIZATION_MISMATCH", f"field set differs: {sorted(set(auth) ^ set(expected))}")
    for key in sorted(expected):
        if auth[key] != expected[key]:
            raise Refusal("AUTHORIZATION_MISMATCH", f"authorization field {key!r} does not match this campaign")
    if spec.host_expected and any(auth["host"].get(k) != v for k, v in spec.host_expected.items()):
        raise Refusal("AUTHORIZATION_MISMATCH", "authorization host differs from the bound host")
    if not isinstance(auth["authorization_id"], str) or not isinstance(auth["production_run_id"], str):
        raise Refusal("AUTHORIZATION_MISMATCH", "authorization id / run id")


def verify_countersignature(path, *, auth: dict, auth_sha: str, freeze_record_sha256: str) -> tuple[dict, str]:
    path = Path(path)
    if not path.exists():
        raise Refusal("COUNTERSIGNATURE_MISSING", f"no independent countersignature binds authorization {auth_sha[:16]}; "
                                                  "production is not authorized")
    sha = sha256_file(path)
    try:
        cs = json.loads(path.read_text())
    except ValueError as exc:
        raise Refusal("COUNTERSIGNATURE_INVALID", str(exc)) from exc
    synthetic = auth["mode"] == "SYNTHETIC"
    problems = []
    if cs.get("schema") != S.COUNTERSIGN_SCHEMA:
        problems.append("schema")
    if cs.get("verdict") != S.APPROVED:
        problems.append(f"verdict {cs.get('verdict')!r}")
    for key, want in (("authorization_sha256", auth_sha), ("production_checkpoint_sha256", auth["production_checkpoint_sha256"]),
                      ("production_run_id", auth["production_run_id"]), ("mode", auth["mode"]),
                      ("freeze_record_sha256", freeze_record_sha256)):
        if cs.get(key) != want:
            problems.append(f"{key} does not bind this authorization")
    if cs.get("synthetic") is not synthetic:
        problems.append("a synthetic countersignature can never authorize production (or vice versa)")
    if not (isinstance(cs.get("reviewer"), str) and cs["reviewer"].strip()) or cs.get("reviewer_independent_of_authoring_session") is not True:
        problems.append("reviewer identity / independence not declared")
    if problems:
        raise Refusal("COUNTERSIGNATURE_INVALID", "; ".join(problems))
    return cs, sha


def synthetic_countersignature(auth: dict, auth_sha: str, *, freeze_record_sha256: str) -> dict:
    if auth.get("mode") != "SYNTHETIC":
        raise Refusal("SELF_AUTHORIZATION_REFUSED", "this tooling creates countersignatures for SYNTHETIC authorizations only")
    return {"schema": S.COUNTERSIGN_SCHEMA, "verdict": S.APPROVED, "synthetic": True, "mode": "SYNTHETIC",
            "authorization_sha256": auth_sha, "production_checkpoint_sha256": auth["production_checkpoint_sha256"],
            "production_run_id": auth["production_run_id"], "freeze_record_sha256": freeze_record_sha256,
            "reviewer": "SYNTHETIC_ACCEPTANCE_FIXTURE", "reviewer_independent_of_authoring_session": True}


def load_authz(spec, *, auth_path, hash_path, cs_path, freeze_record_sha256: str) -> Authz:
    auth, auth_sha = load_authorization(auth_path, hash_path)
    if auth["mode"] != spec.mode:
        raise Refusal("AUTHORIZATION_MISMATCH", f"authorization mode {auth['mode']} for a {spec.mode} campaign")
    verify_authorization(auth, spec)
    cs, cs_sha = verify_countersignature(cs_path, auth=auth, auth_sha=auth_sha, freeze_record_sha256=freeze_record_sha256)
    return Authz(auth, auth_sha, cs, cs_sha, auth_bytes=Path(auth_path).read_bytes(), cs_bytes=Path(cs_path).read_bytes())
