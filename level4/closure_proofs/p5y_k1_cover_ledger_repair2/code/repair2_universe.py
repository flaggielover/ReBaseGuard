"""Repair2 obligation identity: exact identity AND exact evidence provenance.

Repair1 bound (A) exact obligation identity. Repair2 additionally binds
(B) exact evidence provenance:

    implementation_hash        the REPAIR2 PRODUCER hash (producer.py), which
                               covers the code that actually produced the
                               record -- not the reviewed parent's hash
    implementation_hash_kind   "repair2_producer_manifest_v1", so a Repair1
                               record (which stamps the parent hash and carries
                               no kind) is structurally inadmissible here
    backend_hash               the certified backend contract subset
    source_certificate_hashes  hashes of the ACTUAL consumed dependency
                               certificates, not identity metadata

`unit_hash` is recomputed from the identity body on every admission, so a
forged or stale hash cannot survive.
"""
from __future__ import annotations

import hashlib
from fractions import Fraction as F

import prior2                                                   # noqa: F401

import spec                                                     # noqa: E402
import universe as reviewed                                     # noqa: E402
from repair_universe import (SUPERSEDED_CHECKPOINT_HASHES,       # noqa: E402
                             SUPERSEDED_UNIVERSES, _cell_of,
                             dependencies_of)

import producer                                                 # noqa: E402
from certhash import canonical                                  # noqa: E402

IDENTITY_KIND = "repair2_producer_manifest_v1"

IDENTITY_FIELDS = (
    "checkpoint_hash", "cells_sha256", "error_algebra_sha256",
    "backend_hash", "implementation_hash", "implementation_hash_kind",
    "obligation_universe_total",
    "detector", "cell_index", "unit_kind", "function_or_m",
    "left", "right", "e0", "rho", "C_upper", "precision_bits",
    "source_certificate_hashes",
)
EXACT_FIELDS = ("left", "right", "e0", "rho", "C_upper")


class ResumeRejected(RuntimeError):
    """The record does not exactly identify the obligation or its evidence."""


class InexactField(ResumeRejected):
    """An exact quantity was supplied as a float or a non-canonical string."""


class ProvenanceRejected(ResumeRejected):
    """The declared evidence provenance does not match the actual certificates."""


def _check_exact(value, field: str):
    if value is None:
        return
    if isinstance(value, float):
        raise InexactField(f"{field}: float {value!r} in an exact field")
    if isinstance(value, list):
        if len(value) != 2:
            raise InexactField(f"{field}: affine encoding must be [p, s]")
        for part in value:
            if isinstance(part, float) or not isinstance(part, str):
                raise InexactField(f"{field}: affine part {part!r} is not exact")
            try:
                F(part)
            except (ValueError, ZeroDivisionError) as exc:
                raise InexactField(f"{field}: {part!r} is not a rational") from exc
        return
    if isinstance(value, str):
        try:
            F(value)
        except (ValueError, ZeroDivisionError) as exc:
            raise InexactField(f"{field}: {value!r} is not a rational") from exc
        return
    raise InexactField(f"{field}: unsupported exact encoding {type(value).__name__}")


def unit_id(unit: tuple) -> str:
    return "|".join(str(x) for x in unit)


def parse_unit_id(uid: str) -> tuple:
    d, i, k, t = uid.split("|")
    return (d, int(i), k, t)


def context(*, producer_hash: str | None = None,
            backend_hash: str | None = None,
            precision_bits: int = spec.PRODUCTION_BITS) -> dict:
    return {"producer_hash": producer_hash or producer.producer_hash(),
            "backend_hash": backend_hash or producer.backend_hash(),
            "precision_bits": precision_bits}


def canonical_identity(unit: tuple, *, producer_hash: str, backend_hash: str,
                       precision_bits: int,
                       source_certificate_hashes: dict) -> dict:
    """Identity of one obligation, bound to its producer and its evidence."""
    detector, index, kind, tag = unit
    cell = _cell_of(detector, index)
    ident = {
        "checkpoint_hash": spec.CHECKPOINT_SHA256,
        "cells_sha256": spec.CELLS_SHA256,
        "error_algebra_sha256": spec.ERROR_ALGEBRA_SHA256,
        "backend_hash": backend_hash,
        "implementation_hash": producer_hash,
        "implementation_hash_kind": IDENTITY_KIND,
        "obligation_universe_total": spec.TOTAL_UNITS,
        "detector": detector,
        "cell_index": index,
        "unit_kind": kind,
        "function_or_m": tag,
        "e0": cell["e0"] if cell else None,
        "rho": cell["rho"] if cell else None,
        "left": cell["left"] if cell else None,
        "right": cell["right"] if cell else None,
        "C_upper": cell["C_upper"] if cell else None,
        "precision_bits": precision_bits,
        "source_certificate_hashes": dict(sorted(source_certificate_hashes.items())),
    }
    ident["unit_hash"] = hashlib.sha256(canonical(ident)).hexdigest()
    return ident


def expected_source_hashes(unit: tuple, certificates: dict) -> dict:
    """Hashes of the ACTUAL dependency certificates this obligation consumes.

    `certificates` maps unit-id -> already-hashed dependency certificate. A
    missing dependency is an error, never an empty entry.
    """
    from certhash import certificate_hash
    out = {}
    for dep in dependencies_of(unit):
        uid = unit_id(dep)
        if uid not in certificates:
            raise ProvenanceRejected(
                f"{unit_id(unit)}: dependency certificate {uid} is absent")
        out[uid] = certificate_hash(certificates[uid])
    return dict(sorted(out.items()))


def admit_resume_record(record: dict, expected_unit: tuple, *,
                        producer_hash: str, backend_hash: str,
                        precision_bits: int,
                        dependency_certificates: dict) -> bool:
    """Admit a record ONLY as the exact obligation AND exact evidence it names.

    `dependency_certificates` are the certificates actually being consumed;
    their hashes are recomputed here, so declaring a dependency hash that does
    not match the certificate on hand is a rejection.
    """
    if not isinstance(record, dict):
        raise ResumeRejected("record must be a mapping")

    total = record.get("obligation_universe_total")
    if total in SUPERSEDED_UNIVERSES:
        raise ResumeRejected(
            f"superseded obligation universe {total!r}; this campaign has "
            f"exactly {spec.TOTAL_UNITS} obligations")
    if record.get("checkpoint_hash") in SUPERSEDED_CHECKPOINT_HASHES:
        raise ResumeRejected("record bound to a superseded parent checkpoint hash")

    if record.get("implementation_hash_kind") != IDENTITY_KIND:
        raise ProvenanceRejected(
            "record does not carry a Repair2 producer identity "
            f"({record.get('implementation_hash_kind')!r}); a Repair1 record, "
            "which stamps the reviewed parent hash, is not admissible here")
    if record.get("implementation_hash") == producer.parent_hash():
        raise ProvenanceRejected(
            "record stamps the reviewed parent implementation hash, which does "
            "not cover the code that produced it")

    for field in EXACT_FIELDS:
        _check_exact(record.get(field), field)

    expected = canonical_identity(
        expected_unit, producer_hash=producer_hash, backend_hash=backend_hash,
        precision_bits=precision_bits,
        source_certificate_hashes=expected_source_hashes(
            expected_unit, dependency_certificates))

    for field in IDENTITY_FIELDS:
        if field not in record:
            raise ResumeRejected(f"resume identity missing required field {field}")
        if record[field] != expected[field]:
            raise (ProvenanceRejected if field == "source_certificate_hashes"
                   else ResumeRejected)(
                f"resume identity mismatch on {field}: "
                f"{record[field]!r} != {expected[field]!r}")

    body = {k: record[k] for k in IDENTITY_FIELDS}
    recomputed = hashlib.sha256(canonical(body)).hexdigest()
    if record.get("unit_hash") != recomputed:
        raise ResumeRejected(
            f"unit_hash mismatch: {record.get('unit_hash')!r} != {recomputed!r}")
    if recomputed != expected["unit_hash"]:
        raise ResumeRejected("unit_hash does not identify the expected obligation")
    return True


def admits(record: dict, expected_unit: tuple, **ctx) -> bool:
    try:
        return admit_resume_record(record, expected_unit, **ctx)
    except ResumeRejected:
        return False
