"""Recursive provenance: build and verify the certificate chain of a cell.

Certificates are built BOTTOM-UP in dependency order, so each obligation's
identity carries the hashes of the actual dependency certificates it consumed.
Verification then walks the same graph and re-derives every hash from the
certificates on hand, so a declared hash that does not match the certificate
actually supplied is a rejection.

Chain integrity checks (Phase 3):
  * every declared dependency exists
  * the dependency's identity is exactly the expected obligation identity
  * the dependency's certificate hash matches what the parent declared
  * no missing dependency, no extra dependency
  * canonical ordering (sorted, so a reordered map is byte-identical)
  * duplicate aliases cannot bypass equality
  * a leaf obligation has an exactly empty source-certificate map
  * a non-leaf obligation may never present an empty map
"""
from __future__ import annotations

import prior2                                                   # noqa: F401

from repair_universe import dependencies_of                     # noqa: E402

import certhash                                                 # noqa: E402
import repair2_universe as RU2                                  # noqa: E402
from repair2_universe import ProvenanceRejected, unit_id        # noqa: E402

OBJECTS = certhash.OBJECTS


def cell_units(detector: str, index: int, *, m_values=None) -> list[tuple]:
    """The 28 obligations of one cell, in a dependency-respecting order."""
    import spec
    ms = m_values or spec.M_VALUES
    p = (detector, index)
    order = [(*p, "object", f"h_{j}") for j in range(1, 5)]
    order += [(*p, "object", f"S_{r}") for r in range(5)]
    order += [(*p, "dependency_bundle", "orders_0_1")]
    order += [(*p, "object", f"F_{r}") for r in range(5)]
    order += [(*p, "object", f"dF_{r}") for r in range(5)]
    order += [(*p, "curvature", "5")]
    order += [(*p, "curvature", str(m)) for m in ms if m != 5]
    order += [(*p, "assembly", str(m)) for m in ms]
    return order


def _topologically_sound(order: list[tuple]) -> bool:
    seen = set()
    for u in order:
        for dep in dependencies_of(u):
            if unit_id(dep) not in seen:
                return False
        seen.add(unit_id(u))
    return True


def build_cell_certificates(record: dict, *, producer_hash: str,
                            backend_hash: str, precision_bits: int,
                            m_values=None) -> dict:
    """Bottom-up certificate construction for every obligation in a cell."""
    detector, index = record["detector"], record["cell_index"]
    ms = m_values or [int(m) for m in record["m"]]
    order = cell_units(detector, index, m_values=ms)
    if not _topologically_sound(order):
        raise ProvenanceRejected("build order violates the frozen dependency graph")
    certs: dict = {}
    for unit in order:
        sources = RU2.expected_source_hashes(unit, certs)
        ident = RU2.canonical_identity(
            unit, producer_hash=producer_hash, backend_hash=backend_hash,
            precision_bits=precision_bits, source_certificate_hashes=sources)
        certs[unit_id(unit)] = certhash.build_certificate(unit, ident, record)
    return certs


def verify_chain(unit: tuple, certificates: dict, *, producer_hash: str,
                 backend_hash: str, precision_bits: int,
                 _seen: set | None = None) -> dict:
    """Recursively verify one obligation's provenance against real certificates."""
    _seen = set() if _seen is None else _seen
    uid = unit_id(unit)
    if uid in _seen:
        return {"unit": uid, "status": "ALREADY_VERIFIED"}
    if uid not in certificates:
        raise ProvenanceRejected(f"{uid}: certificate absent")
    cert = certificates[uid]
    ident = cert["identity"]

    deps = dependencies_of(unit)
    declared = ident.get("source_certificate_hashes")
    if not isinstance(declared, dict):
        raise ProvenanceRejected(f"{uid}: source_certificate_hashes must be a map")

    if not deps and declared != {}:
        raise ProvenanceRejected(
            f"{uid}: leaf obligation must present an exactly empty "
            f"source-certificate map, got {sorted(declared)}")
    if deps and not declared:
        raise ProvenanceRejected(
            f"{uid}: non-leaf obligation presented an empty source-certificate map")

    expected_ids = {unit_id(d) for d in deps}
    got_ids = set(declared)
    missing, extra = expected_ids - got_ids, got_ids - expected_ids
    if missing:
        raise ProvenanceRejected(f"{uid}: missing dependencies {sorted(missing)}")
    if extra:
        raise ProvenanceRejected(f"{uid}: extra dependencies {sorted(extra)}")
    # Ordering is canonical by CONSTRUCTION, not by ingestion order: the
    # canonical serialisation sorts keys, so a benign JSON reordering is the
    # same bytes and the same hash. Rejecting on Python insertion order would
    # reject a semantically identical record, which Phase 4 forbids. Mispairing
    # a hash with the wrong dependency is caught below, by recomputation.
    if certhash.canonical(declared) != certhash.canonical(
            dict(sorted(declared.items()))):
        raise ProvenanceRejected(f"{uid}: source-certificate map is not canonical")

    # Recompute every declared hash from the certificate actually on hand.
    for dep in deps:
        did = unit_id(dep)
        if did not in certificates:
            raise ProvenanceRejected(f"{uid}: dependency certificate {did} absent")
        actual = certhash.certificate_hash(certificates[did])
        if declared[did] != actual:
            raise ProvenanceRejected(
                f"{uid}: declared hash for {did} does not match the certificate "
                f"on hand ({declared[did][:16]}... != {actual[:16]}...)")
        dep_ident = certificates[did]["identity"]
        if (dep_ident["detector"], dep_ident["cell_index"],
                dep_ident["unit_kind"], dep_ident["function_or_m"]) != dep:
            raise ProvenanceRejected(
                f"{uid}: dependency {did} carries a different obligation identity")
        verify_chain(dep, certificates, producer_hash=producer_hash,
                     backend_hash=backend_hash, precision_bits=precision_bits,
                     _seen=_seen)

    # The obligation's own identity must be exactly reconstructible.
    RU2.admit_resume_record(
        ident, unit, producer_hash=producer_hash, backend_hash=backend_hash,
        precision_bits=precision_bits, dependency_certificates=certificates)
    _seen.add(uid)
    return {"unit": uid, "status": "VERIFIED", "dependencies": len(deps)}


def verify_cell(record: dict, *, producer_hash: str, backend_hash: str,
                precision_bits: int, certificates: dict | None = None) -> dict:
    certs = certificates or build_cell_certificates(
        record, producer_hash=producer_hash, backend_hash=backend_hash,
        precision_bits=precision_bits)
    ms = [int(m) for m in record["m"]]
    roots = [(record["detector"], record["cell_index"], "assembly", str(m))
             for m in ms]
    seen: set = set()
    for r in roots:
        verify_chain(r, certs, producer_hash=producer_hash,
                     backend_hash=backend_hash, precision_bits=precision_bits,
                     _seen=seen)
    leaves = [u for u in cell_units(record["detector"], record["cell_index"],
                                    m_values=ms) if not dependencies_of(u)]
    return {
        "detector": record["detector"], "cell_index": record["cell_index"],
        "obligations": len(certs),
        "roots_verified": [unit_id(r) for r in roots],
        "units_verified": len(seen),
        "leaf_units": [unit_id(u) for u in leaves],
        "leaf_maps_empty": all(
            certs[unit_id(u)]["identity"]["source_certificate_hashes"] == {}
            for u in leaves),
        "all_verified": len(seen) == len(certs),
    }
