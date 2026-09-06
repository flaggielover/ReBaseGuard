"""PHASE 3/9: certificate identity, resume admission and auxiliary ownership.

IDENTITY
--------
A unit's identity binds the frozen contract (checkpoint, cells, error algebra,
obligation-universe total), the exact cell/m parameters, the precision, the
recursive source-certificate hashes, and -- the thing the predecessor got wrong
-- a producer identity that a verifier can RESOLVE:

    producer_manifest_hash     sha256 of the canonical committed manifest
    producer_manifest_schema   which manifest contract that hash speaks
    producer_manifest_path     where the committed artifact lives

Rejected as this successor's producer identity, each by a negative control: the
predecessor's on-the-fly hash, Repair2's hash, the reviewed parent's hash, and
every git commit id. A commit id is not a producer identity: it names a tree, not
the executed subset, and it cannot be recomputed from the inputs.

AUXILIARY OWNERSHIP
-------------------
The auxiliary third-derivative evidence introduces NO work id. It is owned by the
parent cell's curvature units, declared here in `AUXILIARY_OWNERSHIP`, hashed
into the parent certificate's scientific content, and verifiable only through it.
The top-level obligation universe stays at exactly 17,978 and the frozen DAG
gains no node.
"""
from __future__ import annotations

import hashlib

import ancestry

import spec
import universe as reviewed
from repair_universe import _cell_of, dependencies_of                # noqa: F401
from repair2_universe import SUPERSEDED_UNIVERSES                    # noqa: F401

import manifest

IDENTITY_KIND = "cusum_aux3_manifest_bound_identity_v1"

IDENTITY_FIELDS = (
    "checkpoint_hash", "cells_sha256", "error_algebra_sha256",
    "producer_manifest_hash", "producer_manifest_schema",
    "producer_manifest_path", "implementation_hash_kind",
    "obligation_universe_total", "detector", "cell_index", "unit_kind",
    "function_or_m", "e0", "rho", "left", "right", "C_upper", "precision_bits",
    "source_certificate_hashes", "auxiliary_evidence_hash",
)

# The auxiliary evidence is nested under the curvature obligations of the SAME
# cell. Nothing else may claim it, and it claims no id of its own.
AUXILIARY_OWNERSHIP = {
    "owner_units": "the assembly units of this cell (m = 1,2,3,5), whose "
                   "curvature bound M_R2 is what the evidence sharpens",
    "creates_top_level_work_ids": False,
    "creates_dag_nodes": False,
    "obligation_universe_total": 17978,
    "verifiable_only_through": "the parent cell certificate's scientific content",
}


class ResumeRejected(RuntimeError):
    """A record was offered for a unit it does not certify."""


class ProvenanceRejected(ResumeRejected):
    """A record's producer or sources cannot be resolved and recomputed."""


class InexactField(ResumeRejected):
    """A certified field arrived in an inexact representation."""


def canonical(obj) -> bytes:
    return manifest.canonical(obj)


def unit_id(unit: tuple) -> str:
    return "|".join(str(x) for x in unit)


def context(*, precision_bits: int = spec.PRODUCTION_BITS) -> dict:
    """The producer context every identity in this run is stamped with."""
    ident = manifest.identity()
    return {"producer_manifest_hash": ident["producer_manifest_hash"],
            "producer_manifest_schema": ident["producer_manifest_schema"],
            "producer_manifest_path": ident["producer_manifest_path"],
            "precision_bits": precision_bits}


def rejected_producer_identities() -> dict:
    """Identities that must never be accepted as this successor's producer."""
    out = {}
    try:
        import successor_producer as predecessor
        out["cusum_completion_successor_on_the_fly_hash"] = \
            predecessor.producer_hash()
    except Exception:                                   # pragma: no cover
        pass
    try:
        import producer as repair2
        out["repair2_producer"] = repair2.producer_hash()
    except Exception:                                   # pragma: no cover
        pass
    out["reviewed_parent_commit"] = ancestry.REVIEWED_COMMIT
    out["repair1_commit"] = ancestry.REPAIR1_COMMIT
    out["repair2_commit"] = ancestry.REPAIR2_COMMIT
    out["final_commit"] = ancestry.FINAL_COMMIT
    out["cusum_successor_commit"] = ancestry.CUSUM_COMMIT
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
                       precision_bits: int, source_certificate_hashes: dict,
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
    from aux_certhash import certificate_hash
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
                        producer_manifest_path: str, precision_bits: int,
                        dependency_certificates: dict,
                        auxiliary_evidence_hash: str | None = None) -> bool:
    """Admit a stored identity for `expected_unit`, or raise saying why not."""
    if not isinstance(record, dict):
        raise ResumeRejected("record must be a mapping")

    total = record.get("obligation_universe_total")
    if total in SUPERSEDED_UNIVERSES:
        raise ResumeRejected(f"superseded obligation universe {total}")
    if total != spec.TOTAL_UNITS:
        raise ResumeRejected(f"obligation universe {total} != {spec.TOTAL_UNITS}")

    kind = record.get("implementation_hash_kind")
    if kind != IDENTITY_KIND:
        raise ProvenanceRejected(
            f"producer identity kind {kind!r} is not {IDENTITY_KIND!r}")
    if record.get("producer_manifest_schema") != producer_manifest_schema:
        raise ProvenanceRejected("producer manifest schema mismatch")
    if record.get("producer_manifest_path") != producer_manifest_path:
        raise ProvenanceRejected("producer manifest path mismatch")

    stamped = record.get("producer_manifest_hash")
    for name, value in rejected_producer_identities().items():
        if stamped == value:
            raise ProvenanceRejected(
                f"producer identity is {name}, not a resolvable aux3 manifest")
    if stamped != producer_manifest_hash:
        raise ResumeRejected("stale producer: the committed manifest has moved")

    if record.get("auxiliary_evidence_hash") != auxiliary_evidence_hash:
        raise ProvenanceRejected("auxiliary evidence hash mismatch")

    expected = canonical_identity(
        expected_unit, producer_manifest_hash=producer_manifest_hash,
        producer_manifest_schema=producer_manifest_schema,
        producer_manifest_path=producer_manifest_path,
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
    return {"total": len(ids), "expected": 17978,
            "ok": len(ids) == 17978 == spec.TOTAL_UNITS,
            "new_top_level_ids_added_here": 0}
