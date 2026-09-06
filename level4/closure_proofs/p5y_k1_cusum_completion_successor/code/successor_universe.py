"""PHASE 4: obligation identity and resume admission under the NEW producer.

Reuses the independently validated Repair2 semantics — exact per-obligation
identity, recursive source-certificate hashes over actual certified content,
recomputed `unit_hash` — and changes exactly one thing: the producer identity
stamped and required is THIS successor's, not Repair2's and not the
final-completion lineage-only hash.

Admission rejects, by construction:
  * the Repair2 producer identity
  * the final-completion lineage-only identity (which is Repair2's hash)
  * the reviewed parent hash
  * any stale successor producer hash
  * any single differing identity-bearing field
  * a forged or stale `unit_hash`
  * dependency hashes that do not match the certificates on hand
"""
from __future__ import annotations

import hashlib
from fractions import Fraction as F

import ancestry                                                 # noqa: F401

import spec                                                     # noqa: E402
from repair_universe import (SUPERSEDED_CHECKPOINT_HASHES,       # noqa: E402
                             SUPERSEDED_UNIVERSES, _cell_of,
                             dependencies_of)

import successor_producer as SP                                 # noqa: E402
from successor_producer import canonical                        # noqa: E402

IDENTITY_KIND = SP.IDENTITY_KIND

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
    pass


class InexactField(ResumeRejected):
    pass


class ProvenanceRejected(ResumeRejected):
    pass


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
            F(part)
        return
    if isinstance(value, str):
        F(value)
        return
    raise InexactField(f"{field}: unsupported encoding {type(value).__name__}")


def unit_id(unit: tuple) -> str:
    return "|".join(str(x) for x in unit)


def context(*, producer_hash: str | None = None, backend_hash: str | None = None,
            precision_bits: int = spec.PRODUCTION_BITS) -> dict:
    return {"producer_hash": producer_hash or SP.producer_hash(),
            "backend_hash": backend_hash or SP.backend_hash(),
            "precision_bits": precision_bits}


def canonical_identity(unit: tuple, *, producer_hash: str, backend_hash: str,
                       precision_bits: int,
                       source_certificate_hashes: dict) -> dict:
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
        "detector": detector, "cell_index": index,
        "unit_kind": kind, "function_or_m": tag,
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
    from successor_certhash import certificate_hash
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
    if not isinstance(record, dict):
        raise ResumeRejected("record must be a mapping")

    total = record.get("obligation_universe_total")
    if total in SUPERSEDED_UNIVERSES:
        raise ResumeRejected(f"superseded obligation universe {total!r}")
    if record.get("checkpoint_hash") in SUPERSEDED_CHECKPOINT_HASHES:
        raise ResumeRejected("record bound to a superseded parent checkpoint")

    if record.get("implementation_hash_kind") != IDENTITY_KIND:
        raise ProvenanceRejected(
            "record does not carry this successor's producer identity kind "
            f"({record.get('implementation_hash_kind')!r})")
    stamped = record.get("implementation_hash")
    for name, h in SP.rejected_producer_hashes().items():
        if stamped == h:
            raise ProvenanceRejected(
                f"record stamps the {name} identity, which does not cover the "
                "code that produced it")

    for field in EXACT_FIELDS:
        _check_exact(record.get(field), field)

    expected = canonical_identity(
        expected_unit, producer_hash=producer_hash, backend_hash=backend_hash,
        precision_bits=precision_bits,
        source_certificate_hashes=expected_source_hashes(
            expected_unit, dependency_certificates))

    for field in IDENTITY_FIELDS:
        if field not in record:
            raise ResumeRejected(f"resume identity missing field {field}")
        if record[field] != expected[field]:
            raise (ProvenanceRejected if field in
                   ("source_certificate_hashes", "implementation_hash")
                   else ResumeRejected)(
                f"resume identity mismatch on {field}")

    body = {k: record[k] for k in IDENTITY_FIELDS}
    recomputed = hashlib.sha256(canonical(body)).hexdigest()
    if record.get("unit_hash") != recomputed:
        raise ResumeRejected("unit_hash mismatch (forged or stale)")
    if recomputed != expected["unit_hash"]:
        raise ResumeRejected("unit_hash does not identify the expected obligation")
    return True


def admits(record: dict, expected_unit: tuple, **ctx) -> bool:
    try:
        return admit_resume_record(record, expected_unit, **ctx)
    except ResumeRejected:
        return False
