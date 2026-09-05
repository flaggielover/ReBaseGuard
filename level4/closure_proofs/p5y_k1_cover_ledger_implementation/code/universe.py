"""The frozen 17,978-obligation work universe: identity, ordering, hashing,
exact-conservation sharding and resume admission.

Counts are DERIVED from the frozen cover table, never hard-coded here:

    objects            19 per cell   h_1..h_4, S_0..S_4, F_0..F_4, dF_0..dF_4
    dependency_bundle   1 per cell   certified h/S derivatives and finite kernel
                                     powers, orders 0 and 1, union over all m
    curvature           4 per cell   one per m in {1,2,3,5}
    assembly            4 per cell   one per m in {1,2,3,5}
    far_field           2 total      one per detector

    (19+1+4+4) * 642 + 2 = 17978,  base objects 19 * 642 = 12198

Sharding uses the frozen floor rule [floor(k*N/S), floor((k+1)*N/S)) with no
ceil-per-shard inflation, so the shards partition the universe exactly for any
worker count. Resume admission rejects the superseded 12,255-object universe,
any checkpoint hash other than the frozen one, and any implementation hash other
than the one that produced the record.
"""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction as F
from pathlib import Path

import spec

OBJECTS = ([f"h_{j}" for j in range(1, 5)]
           + [f"S_{r}" for r in range(5)]
           + [f"F_{r}" for r in range(5)]
           + [f"dF_{r}" for r in range(5)])
assert len(OBJECTS) == spec.OBJECTS_PER_CELL == 19

UNIT_KINDS = ("object", "dependency_bundle", "curvature", "assembly", "far_field")

SUPERSEDED_UNIVERSES = {12255, 12198 + 57, 323 * 19, 322 * 19}
SUPERSEDED_CHECKPOINT_HASHES = {
    # parent optimized successor and parent binding campaign, per the frozen
    # CHECKPOINT.md authority chain; a record bound to these is not admissible.
    "a5d09f83078bf02ae5d015bfb08eb35429190f646cc51260f6ca72fce6e325ec",
    "ababbef4d42ad5a7a61e87279eb895c1b2d0ecfe67454f18c85acf6d57cd5c1d",
    "20e664dec414b427e2b714531f3121224774f20f46cfe43e5c84300ec9de3aea",
}


# --------------------------------------------------------------------- ids
def work_ids(cells=None) -> list[tuple]:
    """Deterministic ordered obligation identities.

    Independently written; a focused test asserts byte-equality with the frozen
    reference algebra.work_ids so that this namespace cannot drift from it.
    """
    cells = spec.CELLS if cells is None else cells
    ids: list[tuple] = []
    for c in cells:
        prefix = (c["detector"], c["index"])
        ids += [(*prefix, "object", name) for name in OBJECTS]
        ids.append((*prefix, "dependency_bundle", "orders_0_1"))
        ids += [(*prefix, "curvature", str(m)) for m in spec.M_VALUES]
        ids += [(*prefix, "assembly", str(m)) for m in spec.M_VALUES]
    ids += [(det, -1, "far_field", "all_m") for det in spec.DETECTORS]
    return ids


def unit_kind_counts(cells=None) -> dict:
    out = {k: 0 for k in UNIT_KINDS}
    for u in work_ids(cells):
        out[u[2]] += 1
    return out


# ------------------------------------------------------------------ hashing
def canonical(obj) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True) + "\n").encode("ascii")


# The modules that can change a certificate. Reporting, benchmarking and
# self-audit tooling is deliberately EXCLUDED: editing a table renderer must not
# invalidate the identity of records that were already certified, and including
# it would make the stored identity unstable for no scientific reason.
CERTIFYING_MODULES = (
    "spec.py", "intervals.py", "opnorms.py", "depgraph.py", "universe.py",
    "assembly.py", "ledger.py", "refine.py", "propagate.py", "scoped.py",
    "cusum_layer1.py", "cusum_layer2.py", "qualify.py",
)


def implementation_hash() -> str:
    """Deterministic hash of the certificate-producing implementation."""
    code = Path(__file__).resolve().parent
    items = []
    for name in sorted(CERTIFYING_MODULES):
        path = code / name
        if not path.exists():
            raise FileNotFoundError(f"certifying module missing: {name}")
        items.append((name, hashlib.sha256(path.read_bytes()).hexdigest()))
    blob = b"".join(n.encode() + b"\0" + h.encode() + b"\n" for n, h in items)
    return hashlib.sha256(blob).hexdigest()


def _cell_of(detector: str, index: int) -> dict | None:
    if index < 0:
        return None
    for c in spec.CELLS:
        if c["detector"] == detector and c["index"] == index:
            return c
    raise KeyError((detector, index))


def unit_identity(unit: tuple, *, backend_hash: str, impl_hash: str | None = None,
                  precision_bits: int | None = None) -> dict:
    """The frozen resume identity for one obligation.

    Includes the exact symbolic e0/rho encodings, so an SR terminal cell can
    never be confused with a decimal approximation of itself.
    """
    detector, index, kind, tag = unit
    cell = _cell_of(detector, index)
    ident = {
        "checkpoint_hash": spec.CHECKPOINT_SHA256,
        "cells_sha256": spec.CELLS_SHA256,
        "error_algebra_sha256": spec.ERROR_ALGEBRA_SHA256,
        "backend_hash": backend_hash,
        "implementation_hash": impl_hash or implementation_hash(),
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
        "precision_bits": spec.PRODUCTION_BITS if precision_bits is None
                          else precision_bits,
    }
    ident["unit_hash"] = hashlib.sha256(canonical(ident)).hexdigest()
    return ident


def universe_hash(*, backend_hash: str, impl_hash: str | None = None) -> str:
    impl = impl_hash or implementation_hash()
    h = hashlib.sha256()
    for u in work_ids():
        h.update(unit_identity(u, backend_hash=backend_hash,
                               impl_hash=impl)["unit_hash"].encode())
        h.update(b"\n")
    return h.hexdigest()


# ----------------------------------------------------------------- sharding
def shard_bounds(n: int, k: int, workers: int) -> tuple[int, int]:
    """Frozen floor rule. No ceil-per-shard inflation, no rounding slack."""
    if not (n >= 0 and workers > 0 and 0 <= k < workers):
        raise ValueError("invalid shard request")
    return n * k // workers, n * (k + 1) // workers


def shard(units: list, k: int, workers: int) -> list:
    lo, hi = shard_bounds(len(units), k, workers)
    return units[lo:hi]


def verify_shard_conservation(workers: int, units=None) -> dict:
    units = work_ids() if units is None else units
    parts = [shard(units, k, workers) for k in range(workers)]
    flat = [u for p in parts for u in p]
    seen = set()
    overlaps = 0
    for u in flat:
        if u in seen:
            overlaps += 1
        seen.add(u)
    return {
        "workers": workers,
        "total": len(units),
        "union_equals_universe": flat == units,
        "no_overlap": overlaps == 0,
        "no_dropped_work": len(flat) == len(units),
        "shard_sizes": [len(p) for p in parts],
        "max_minus_min": (max(len(p) for p in parts) - min(len(p) for p in parts)),
    }


# ---------------------------------------------------------------- resume
class ResumeRejected(RuntimeError):
    pass


def admit_resume_record(record: dict, *, backend_hash: str,
                        impl_hash: str | None = None) -> bool:
    """Admit a prior record only under an exactly matching new identity."""
    impl = impl_hash or implementation_hash()
    total = record.get("obligation_universe_total")
    if total in SUPERSEDED_UNIVERSES or (total is not None and total != spec.TOTAL_UNITS):
        raise ResumeRejected(
            f"superseded or mismatched obligation universe {total!r}; "
            f"this campaign has exactly {spec.TOTAL_UNITS} obligations")
    if record.get("checkpoint_hash") in SUPERSEDED_CHECKPOINT_HASHES:
        raise ResumeRejected("record bound to a superseded parent checkpoint hash")
    for field, expect in (("checkpoint_hash", spec.CHECKPOINT_SHA256),
                          ("cells_sha256", spec.CELLS_SHA256),
                          ("error_algebra_sha256", spec.ERROR_ALGEBRA_SHA256),
                          ("backend_hash", backend_hash),
                          ("implementation_hash", impl),
                          ("precision_bits", spec.PRODUCTION_BITS)):
        if record.get(field) != expect:
            raise ResumeRejected(f"resume identity mismatch on {field}: "
                                 f"{record.get(field)!r} != {expect!r}")
    return True


# ---------------------------------------------------------------- manifest
def manifest(*, backend_hash: str) -> dict:
    units = work_ids()
    impl = implementation_hash()
    counts = unit_kind_counts()
    return {
        "schema": "k1.cover-ledger.work-universe.v1",
        "checkpoint_hash": spec.CHECKPOINT_SHA256,
        "cells_sha256": spec.CELLS_SHA256,
        "backend_hash": backend_hash,
        "implementation_hash": impl,
        "detector_cell_counts": spec.COUNTS,
        "unit_kind_counts": counts,
        "base_object_units": counts["object"],
        "total_units": len(units),
        "universe_hash": universe_hash(backend_hash=backend_hash, impl_hash=impl),
        "shard_conservation": {str(w): verify_shard_conservation(w, units)
                               for w in (1, 8, 16, 32, 64)},
        "old_universes_rejected": sorted(SUPERSEDED_UNIVERSES),
        "production_enabled": spec.PRODUCTION_ENABLED,
    }
