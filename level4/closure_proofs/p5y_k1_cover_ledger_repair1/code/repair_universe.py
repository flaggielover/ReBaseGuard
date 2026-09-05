"""REPAIR 2: exact per-obligation resume identity.

DEFECT (independently adjudicated, WORK_UNIVERSE = FAIL)
--------------------------------------------------------
`universe.admit_resume_record(record, *, backend_hash, impl_hash)` in the
reviewed implementation validates only GLOBAL context -- checkpoint hash, cells
hash, error-algebra hash, backend hash, implementation hash, precision and the
total obligation count -- and takes no `expected_unit` at all. It therefore
admits a record for one obligation as any other: mutating `detector`,
`cell_index`, `unit_kind`, `function_or_m`, `e0`, `rho` or `unit_hash` leaves
the record admissible. The frozen `work.resume_identity` list also requires
`source_certificate_hashes`, which the reviewed identity never carried.

REPAIR
------
`admit_resume_record(record, expected_unit, ...)` now rebuilds the canonical
identity for the obligation being resumed and requires the record to match it
FIELD FOR FIELD, including:

    checkpoint_hash, cells_sha256, error_algebra_sha256, backend_hash,
    implementation_hash, obligation_universe_total, detector, cell_index,
    unit_kind, function_or_m, left, right, e0, rho, C_upper, precision_bits,
    source_certificate_hashes, unit_hash

`unit_hash` is additionally RECOMPUTED from the canonical serialisation, so a
record cannot carry a stale or forged hash that happens to match a mutated body.

Exactness
---------
`e0`, `rho`, `left`, `right` and `C_upper` are compared in the repository's
canonical exact encoding -- the frozen affine `[p, s]` rational-string pair
meaning `p + s*c_SR`, and reduced rational strings. Floats are rejected
outright: a float in any exact field is a hard reject, not a tolerance
comparison.

Dependency binding
------------------
`source_certificate_hashes` is derived from the FROZEN dependency graph
(`algebra.unit_dependencies`), so an obligation cannot be replayed unless the
exact set of dependency obligations it is defined to consume is named, with
their own canonical unit hashes. `dependencies_of` reimplements the frozen
rules for a single unit; a test asserts it agrees with the frozen whole-graph
function on a sample.
"""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction as F

import prior                                                    # noqa: F401

import spec                                                     # noqa: E402
import universe as reviewed                                     # noqa: E402

M_VALUES = spec.M_VALUES
OBJECTS = reviewed.OBJECTS
SUPERSEDED_UNIVERSES = reviewed.SUPERSEDED_UNIVERSES
SUPERSEDED_CHECKPOINT_HASHES = reviewed.SUPERSEDED_CHECKPOINT_HASHES

# Every field below is identity-bearing: a difference in ANY of them means a
# different obligation, and must cause rejection.
IDENTITY_FIELDS = (
    "checkpoint_hash", "cells_sha256", "error_algebra_sha256",
    "backend_hash", "implementation_hash", "obligation_universe_total",
    "detector", "cell_index", "unit_kind", "function_or_m",
    "left", "right", "e0", "rho", "C_upper", "precision_bits",
    "source_certificate_hashes",
)
EXACT_FIELDS = ("left", "right", "e0", "rho", "C_upper")


class ResumeRejected(RuntimeError):
    """The record does not exactly identify the obligation being resumed."""


class InexactField(ResumeRejected):
    """An exact quantity was supplied as a float or a non-canonical string."""


# ------------------------------------------------------------------ helpers
def canonical(obj) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True) + "\n").encode("ascii")


def _cell_of(detector: str, index: int):
    if index < 0:
        return None
    for c in spec.CELLS:
        if c["detector"] == detector and c["index"] == index:
            return c
    raise KeyError((detector, index))


def _check_exact(value, field: str):
    """Exact quantities are affine rational-string pairs or reduced rationals."""
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


# --------------------------------------------------- frozen dependency rules
def dependencies_of(unit: tuple) -> list[tuple]:
    """The frozen dependency set of ONE obligation.

    Reimplements `algebra.unit_dependencies` for a single unit so the whole
    17,978-node graph need not be built to admit one record. A focused test
    asserts agreement with the frozen function.
    """
    detector, index, kind, tag = unit
    if kind == "far_field":
        return []
    prefix = (detector, index)
    obj = lambda name: (*prefix, "object", name)                # noqa: E731
    bundle = (*prefix, "dependency_bundle", "orders_0_1")
    if kind == "object":
        if tag.startswith("h_"):
            j = int(tag.split("_")[1])
            return [obj(f"h_{j - 1}")] if j >= 2 else []
        if tag.startswith("S_"):
            r = int(tag.split("_")[1])
            return [obj(f"h_{r}")] if r >= 1 else []
        if tag.startswith("dF_"):
            r = int(tag.split("_")[1])
            return sorted([obj(f"F_{r}"), bundle])
        if tag.startswith("F_"):
            r = int(tag.split("_")[1])
            return [obj(f"S_{r}")]
        raise ValueError(f"unknown object {tag}")
    if kind == "dependency_bundle":
        return sorted([obj(f"h_{j}") for j in range(1, 5)]
                      + [obj(f"S_{r}") for r in range(5)])
    owner = (*prefix, "curvature", "5")
    if kind == "curvature":
        if tag == "5":
            return sorted([obj(n) for n in OBJECTS] + [bundle])
        return [owner]
    if kind == "assembly":
        if tag not in {str(v) for v in M_VALUES}:
            raise ValueError(
                f"assembly tag {tag!r} is not a frozen m in {M_VALUES}")
        m = int(tag)
        deps = {bundle, (*prefix, "curvature", tag)}
        for r in range(m):
            deps.add(obj(f"F_{r}"))
            deps.add(obj(f"dF_{r}"))
        return sorted(deps)
    raise ValueError(f"unknown unit kind {kind}")


# ------------------------------------------------------------- identity
def _base_identity(unit: tuple, *, backend_hash: str, impl_hash: str,
                   precision_bits: int) -> dict:
    detector, index, kind, tag = unit
    cell = _cell_of(detector, index)
    return {
        "checkpoint_hash": spec.CHECKPOINT_SHA256,
        "cells_sha256": spec.CELLS_SHA256,
        "error_algebra_sha256": spec.ERROR_ALGEBRA_SHA256,
        "backend_hash": backend_hash,
        "implementation_hash": impl_hash,
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
    }


def _dependency_hashes(unit: tuple, *, backend_hash: str, impl_hash: str,
                       precision_bits: int) -> dict:
    """{canonical dependency unit id -> its canonical unit hash}."""
    out = {}
    for dep in dependencies_of(unit):
        base = _base_identity(dep, backend_hash=backend_hash,
                              impl_hash=impl_hash, precision_bits=precision_bits)
        out["|".join(str(x) for x in dep)] = hashlib.sha256(
            canonical(base)).hexdigest()
    return out


def canonical_identity(unit: tuple, *, backend_hash: str, impl_hash: str,
                       precision_bits: int = spec.PRODUCTION_BITS) -> dict:
    """The complete, exact, replay-bearing identity of one obligation."""
    ident = _base_identity(unit, backend_hash=backend_hash, impl_hash=impl_hash,
                           precision_bits=precision_bits)
    ident["source_certificate_hashes"] = _dependency_hashes(
        unit, backend_hash=backend_hash, impl_hash=impl_hash,
        precision_bits=precision_bits)
    ident["unit_hash"] = hashlib.sha256(canonical(ident)).hexdigest()
    return ident


def context(*, backend_hash: str, impl_hash: str | None = None,
            precision_bits: int = spec.PRODUCTION_BITS) -> dict:
    return {"backend_hash": backend_hash,
            "impl_hash": impl_hash or reviewed.implementation_hash(),
            "precision_bits": precision_bits}


# ------------------------------------------------------------- admission
def admit_resume_record(record: dict, expected_unit: tuple, *,
                        backend_hash: str, impl_hash: str | None = None,
                        precision_bits: int = spec.PRODUCTION_BITS) -> bool:
    """Admit a prior record ONLY as the exact obligation it identifies.

    Rejects on any single differing identity-bearing field, on a stale or
    forged unit_hash, on a superseded universe or parent checkpoint, and on any
    float supplied where the repository uses an exact encoding.
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

    for field in EXACT_FIELDS:
        _check_exact(record.get(field), field)

    expected = canonical_identity(
        expected_unit, backend_hash=backend_hash,
        impl_hash=impl_hash or reviewed.implementation_hash(),
        precision_bits=precision_bits)

    for field in IDENTITY_FIELDS:
        if field not in record:
            raise ResumeRejected(f"resume identity missing required field {field}")
        if record[field] != expected[field]:
            raise ResumeRejected(
                f"resume identity mismatch on {field}: "
                f"{record[field]!r} != {expected[field]!r}")

    # Recompute rather than trust: a forged unit_hash must not survive.
    body = {k: record[k] for k in IDENTITY_FIELDS}
    recomputed = hashlib.sha256(canonical(body)).hexdigest()
    if record.get("unit_hash") != recomputed:
        raise ResumeRejected(
            f"unit_hash mismatch: {record.get('unit_hash')!r} != {recomputed!r}")
    if recomputed != expected["unit_hash"]:
        raise ResumeRejected("unit_hash does not identify the expected obligation")
    return True


def admits(record: dict, expected_unit: tuple, **ctx) -> bool:
    """Non-raising form, for negative-control sweeps."""
    try:
        return admit_resume_record(record, expected_unit, **ctx)
    except ResumeRejected:
        return False
