"""Certificate identity, resume admission, and auxiliary ownership.

NO LAZY IMPORTS ON THE CERTIFYING PATH
--------------------------------------
Aux3 built its rejected-identity list by importing predecessor producer modules
at record-assembly time, inside `try/except Exception`. On the real run that
import failed -- two namespaces both provide a module called `ancestry`, so the
wrong one won -- and the failure was swallowed. The record then carried a
`rejected_identities` map that silently depended on module-cache state, and that
map is inside the scientific hash. Same declared producer identity, different
certificate.

Here the rejected identities are STATIC data: commit ids, plus the predecessor
manifest hash read from a committed artifact that is itself byte-bound in the
TCB. Nothing is imported, so nothing can be swallowed.
"""
from __future__ import annotations

import hashlib
import json

import ancestry5
import ancestry4

import spec
import universe as reviewed
from repair_universe import _cell_of, dependencies_of                # noqa: F401
from repair2_universe import SUPERSEDED_UNIVERSES                    # noqa: F401

import manifest_v3 as manifest_v2

IDENTITY_KIND = "cusum_aux5_manifest_bound_identity_v3"

IDENTITY_FIELDS = (
    "checkpoint_hash", "cells_sha256", "error_algebra_sha256",
    "producer_manifest_hash", "producer_manifest_schema",
    "producer_manifest_path", "producer_manifest_version",
    "runtime_contract_hash", "producer_identity_hash",
    "implementation_hash_kind", "obligation_universe_total",
    "detector", "cell_index", "unit_kind", "function_or_m",
    "e0", "rho", "left", "right", "C_upper", "precision_bits",
    "source_certificate_hashes", "auxiliary_evidence_hash",
)

AUXILIARY_OWNERSHIP = {
    "owner_units": "the assembly units of this cell (m = 1,2,3,5), whose "
                   "curvature bound M_R2 is what the evidence sharpens",
    "creates_top_level_work_ids": False,
    "creates_dag_nodes": False,
    "creates_dag_edges": False,
    "obligation_universe_total": 17978,
    "verifiable_only_through": "the parent cell certificate's scientific content",
    "adjudicated": "AUXILIARY_DERIVATIVE_SOUND = YES (Aux3)",
}


class ResumeRejected(RuntimeError):
    """A record was offered for a unit it does not certify."""


class ProvenanceRejected(ResumeRejected):
    """A record's producer or sources cannot be resolved and recomputed."""


class InexactField(ResumeRejected):
    """A certified field arrived in an inexact representation."""


def canonical(obj) -> bytes:
    return manifest_v2.canonical(obj)


def unit_id(unit: tuple) -> str:
    return "|".join(str(x) for x in unit)


def context(*, precision_bits: int = spec.PRODUCTION_BITS) -> dict:
    ident = manifest_v2.identity()
    return {"producer_manifest_hash": ident["producer_manifest_hash"],
            "producer_manifest_schema": ident["producer_manifest_schema"],
            "producer_manifest_path": ident["producer_manifest_path"],
            "producer_manifest_version": ident["producer_manifest_version"],
            "runtime_contract_hash": ident["runtime_contract_hash"],
            "producer_identity_hash": ident["producer_identity_hash"],
            "precision_bits": precision_bits}


def rejected_producer_identities() -> dict:
    """Static. Read from committed bytes; nothing is imported or executed."""
    out = {
        "reviewed_parent_commit": ancestry4.REVIEWED_COMMIT,
        "repair1_commit": ancestry4.REPAIR1_COMMIT,
        "repair2_commit": ancestry4.REPAIR2_COMMIT,
        "final_commit": ancestry4.FINAL_COMMIT,
        "cusum_successor_commit": ancestry4.CUSUM_COMMIT,
        "aux3_commit": ancestry4.AUX3_COMMIT,
        "aux4_commit": ancestry5.AUX4_COMMIT,
    }
    artifact = ancestry4.AUX3_NS / "manifests" / "producer_manifest_v1.json"
    if artifact.exists():                       # byte-bound in the TCB
        m = json.loads(artifact.read_text())
        out["aux3_producer_manifest_hash"] = hashlib.sha256(
            canonical(m)).hexdigest()
    aux4 = ancestry5.AUX4_NS / "manifests" / "producer_manifest_v2.json"
    if aux4.exists():                           # byte-bound in the TCB
        out["aux4_producer_manifest_hash"] = hashlib.sha256(
            canonical(json.loads(aux4.read_text()))).hexdigest()
    return out


def _check_exact(value, field: str) -> None:
    if isinstance(value, float):
        raise InexactField(f"{field} arrived as a float; certified fields are exact")
    if isinstance(value, dict):
        for k, v in value.items():
            _check_exact(v, f"{field}.{k}")
    if isinstance(value, (list, tuple)):
        for i, v in enumerate(value):
            _check_exact(v, f"{field}[{i}]")


def canonical_identity(unit: tuple, *, producer_manifest_hash: str,
                       producer_manifest_schema: str, producer_manifest_path: str,
                       producer_manifest_version: int, runtime_contract_hash: str,
                       producer_identity_hash: str, precision_bits: int,
                       source_certificate_hashes: dict,
                       auxiliary_evidence_hash: str | None = None) -> dict:
    detector, index, kind, tag = unit
    cell = _cell_of(detector, index)
    ident = {
        "checkpoint_hash": spec.CHECKPOINT_SHA256,
        "cells_sha256": spec.CELLS_SHA256,
        "error_algebra_sha256": spec.ERROR_ALGEBRA_SHA256,
        "producer_manifest_hash": producer_manifest_hash,
        "producer_manifest_schema": producer_manifest_schema,
        "producer_manifest_path": producer_manifest_path,
        "producer_manifest_version": producer_manifest_version,
        "runtime_contract_hash": runtime_contract_hash,
        "producer_identity_hash": producer_identity_hash,
        "implementation_hash_kind": IDENTITY_KIND,
        "obligation_universe_total": spec.TOTAL_UNITS,
        "detector": detector, "cell_index": index,
        "unit_kind": kind, "function_or_m": tag,
        "e0": cell["e0"] if cell else None,
        "rho": cell["rho"] if cell else None,
        "left": cell["left"] if cell else None,
        "right": cell["right"] if cell else None,
        "C_upper": cell["C_upper"] if cell else None,
        "precision_bits": precision_bits,
        "source_certificate_hashes": dict(sorted(source_certificate_hashes.items())),
        "auxiliary_evidence_hash": auxiliary_evidence_hash,
    }
    for field in ("e0", "rho", "left", "right", "C_upper"):
        _check_exact(ident[field], field)
    ident["unit_hash"] = hashlib.sha256(canonical(ident)).hexdigest()
    return ident


def expected_source_hashes(unit: tuple, certificates: dict) -> dict:
    from hash_v2 import certificate_hash
    out = {}
    for dep in dependencies_of(unit):
        uid = unit_id(dep)
        if uid not in certificates:
            raise ProvenanceRejected(
                f"{unit_id(unit)}: dependency certificate {uid} is absent")
        out[uid] = certificate_hash(certificates[uid])
    return dict(sorted(out.items()))


def admit_resume_record(record: dict, expected_unit: tuple, *,
                        producer_manifest_hash: str, producer_manifest_schema: str,
                        producer_manifest_path: str, producer_manifest_version: int,
                        runtime_contract_hash: str, producer_identity_hash: str,
                        precision_bits: int, dependency_certificates: dict,
                        auxiliary_evidence_hash: str | None = None) -> bool:
    if not isinstance(record, dict):
        raise ResumeRejected("record must be a mapping")

    total = record.get("obligation_universe_total")
    if total in SUPERSEDED_UNIVERSES:
        raise ResumeRejected(f"superseded obligation universe {total}")
    if total != spec.TOTAL_UNITS:
        raise ResumeRejected(f"obligation universe {total} != {spec.TOTAL_UNITS}")

    if record.get("implementation_hash_kind") != IDENTITY_KIND:
        raise ProvenanceRejected(
            f"producer identity kind {record.get('implementation_hash_kind')!r} "
            f"is not {IDENTITY_KIND!r}")
    for field, expected in (("producer_manifest_schema", producer_manifest_schema),
                            ("producer_manifest_path", producer_manifest_path),
                            ("producer_manifest_version", producer_manifest_version)):
        if record.get(field) != expected:
            raise ProvenanceRejected(f"{field} mismatch")

    stamped = record.get("producer_manifest_hash")
    for name, value in rejected_producer_identities().items():
        if stamped == value:
            raise ProvenanceRejected(
                f"producer identity is {name}, not an Aux4 manifest identity")
    if stamped != producer_manifest_hash:
        raise ResumeRejected("stale producer: the committed manifest has moved")
    if record.get("runtime_contract_hash") != runtime_contract_hash:
        raise ResumeRejected("stale runtime: the runtime contract has moved")
    if record.get("producer_identity_hash") != producer_identity_hash:
        raise ResumeRejected("producer identity hash does not match")
    if record.get("auxiliary_evidence_hash") != auxiliary_evidence_hash:
        raise ProvenanceRejected("auxiliary evidence hash mismatch")

    expected = canonical_identity(
        expected_unit, producer_manifest_hash=producer_manifest_hash,
        producer_manifest_schema=producer_manifest_schema,
        producer_manifest_path=producer_manifest_path,
        producer_manifest_version=producer_manifest_version,
        runtime_contract_hash=runtime_contract_hash,
        producer_identity_hash=producer_identity_hash,
        precision_bits=precision_bits,
        source_certificate_hashes=expected_source_hashes(
            expected_unit, dependency_certificates),
        auxiliary_evidence_hash=auxiliary_evidence_hash)

    for field in IDENTITY_FIELDS:
        if record.get(field) != expected[field]:
            cls = (ProvenanceRejected if field == "source_certificate_hashes"
                   else ResumeRejected)
            raise cls(f"identity field {field} does not match this unit")
    if record.get("unit_hash") != expected["unit_hash"]:
        raise ResumeRejected("unit hash does not recompute")
    return True


def admits(record: dict, expected_unit: tuple, **ctx) -> bool:
    try:
        return admit_resume_record(record, expected_unit, **ctx)
    except ResumeRejected:
        return False


def universe_unchanged() -> dict:
    ids = reviewed.work_ids()
    cusum = sum(1 for c in spec.CELLS if c["detector"] == "CUSUM")
    return {"total": len(ids), "expected": 17978,
            "cusum_cells": cusum, "expected_cusum_cells": 326,
            "ok": len(ids) == 17978 == spec.TOTAL_UNITS and cusum == 326,
            "new_top_level_ids_added_here": 0}
