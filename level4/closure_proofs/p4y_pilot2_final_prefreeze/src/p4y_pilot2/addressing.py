"""Collision-free logical addressing for Pilot-2 (brief sections 19-20).

Randomness is keyed by LOGICAL SCIENTIFIC IDENTITY:

    campaign  ->  base offset
    cell      ->  configuration + route + block size
    stratum   ->  the production-representative (B_ref, B1) regime
    namespace ->  calibration / design / validation / probe
    replicate ->  independent repetition
    block     ->  the Philox ``batch``; step is the internal counter

and never by worker id, process id, scheduling order, or shard index.  The
seed function takes none of those as arguments and cannot without a signature
change, which a test pins.

No modulo compression.  The map is an injective positional code over the whole
frozen domain, and ``enumerate_domain`` materialises that domain so injectivity
is CHECKED, not asserted -- brief section 20.
"""

from __future__ import annotations

from dataclasses import dataclass

#: Pilot-2 campaign base.  Pilot-1's address space has a THEORETICAL ceiling of
#: 4.31e9 + MAX_CELLS(1000) * 1e6 = 5.31e9, so Pilot-2 starts a clean 1e9 above
#: that ceiling rather than above Pilot-1's merely observed maximum.  The
#: frozen P4 campaign, the P4X R0 pilot and P4X production all live below 5e6.
#: No Pilot-2 stream can coincide with any of them, by construction.
CAMPAIGN_BASE = 6_310_000_000
PILOT1_CEILING = 4_310_000_000 + 1_000 * 1_000_000

CELL_STRIDE = 100_000_000
STRATUM_STRIDE = 10_000_000
NAMESPACE_STRIDE = 1_000_000
MAX_REPLICATES = NAMESPACE_STRIDE

MAX_CELLS = 20
MAX_STRATA = 10
MAX_NAMESPACES = 10

NAMESPACE_INDEX = {
    "calibration": 0,   # fixes r*_pilot; never reused
    "reference": 1,     # the historical-style reference measurement
    "design": 2,        # selects kappa and cap; never an endpoint
    "validation": 3,    # the ONLY source of the primary endpoint
    "probe": 9,         # pre-freeze feasibility only, never result-bearing
}

CELL_INDEX: dict[str, int] = {}
STRATUM_INDEX: dict[str, int] = {}


class AddressError(ValueError):
    """A logical address is outside the frozen domain, or would collide."""


def register(cells: dict[str, int], strata: dict[str, int]) -> None:
    """Freeze the address table.  Indices are declared, never order-assigned."""
    for table, mapping, limit, what in (
        (CELL_INDEX, cells, MAX_CELLS, "cell"),
        (STRATUM_INDEX, strata, MAX_STRATA, "stratum"),
    ):
        for key, idx in mapping.items():
            if not 0 <= idx < limit:
                raise AddressError(f"{what} index {idx} outside the domain")
            if table.get(key, idx) != idx:
                raise AddressError(
                    f"{what} {key!r} already frozen at {table[key]}, not {idx}")
            clash = [k for k, v in table.items() if v == idx and k != key]
            if clash:
                raise AddressError(
                    f"{what} index {idx} already used by {clash[0]!r}")
            table[key] = idx


def seed(cell: str, stratum: str, namespace: str, replicate: int) -> int:
    """The logical stream key.  No worker, pid, shard or schedule argument."""
    if cell not in CELL_INDEX:
        raise AddressError(f"cell {cell!r} has no frozen address")
    if stratum not in STRATUM_INDEX:
        raise AddressError(f"stratum {stratum!r} has no frozen address")
    if namespace not in NAMESPACE_INDEX:
        raise AddressError(f"namespace {namespace!r} has no frozen address")
    if not 0 <= replicate < MAX_REPLICATES:
        raise AddressError(f"replicate {replicate} outside the domain")
    return (CAMPAIGN_BASE
            + CELL_INDEX[cell] * CELL_STRIDE
            + STRATUM_INDEX[stratum] * STRATUM_STRIDE
            + NAMESPACE_INDEX[namespace] * NAMESPACE_STRIDE
            + replicate)


@dataclass(frozen=True, slots=True)
class Address:
    cell: str
    stratum: str
    namespace: str
    replicate: int

    @property
    def seed(self) -> int:
        return seed(self.cell, self.stratum, self.namespace, self.replicate)


def enumerate_domain(max_replicate: int) -> list[Address]:
    """Every logical address the frozen Pilot-2 design can reach."""
    return [Address(c, s, n, r)
            for c in CELL_INDEX
            for s in STRATUM_INDEX
            for n in NAMESPACE_INDEX
            for r in range(max_replicate)]


def audit_injectivity(max_replicate: int) -> dict:
    """Assert ``#addresses == #unique seeds`` over the whole frozen domain."""
    domain = enumerate_domain(max_replicate)
    seeds = [a.seed for a in domain]
    unique = set(seeds)
    collisions: list[tuple[Address, Address]] = []
    if len(unique) != len(seeds):
        seen: dict[int, Address] = {}
        for a in domain:
            prev = seen.setdefault(a.seed, a)
            if prev is not a:
                collisions.append((prev, a))
    return {
        "addresses": len(domain),
        "unique_seeds": len(unique),
        "collision_free": len(unique) == len(seeds),
        "collisions": collisions[:8],
        "min_seed": min(seeds) if seeds else None,
        "max_seed": max(seeds) if seeds else None,
        "cells": dict(CELL_INDEX),
        "strata": dict(STRATUM_INDEX),
        "namespaces": dict(NAMESPACE_INDEX),
        "max_replicate": max_replicate,
    }


def audit_reachable_domain(reachable: list[Address]) -> dict:
    """Audit the EXACT set of addresses the frozen design will touch.

    Brief section 20 asks for the complete frozen Pilot-2 logical address
    domain, enumerated and checked -- not a sample of it.  ``reachable`` is
    built by ``strata.reachable_addresses()`` from the frozen cells, strata,
    namespaces and replicate counts, so this is the whole domain and nothing
    else.
    """
    seeds = [x.seed for x in reachable]
    unique = set(seeds)
    dupes: list[tuple[Address, Address]] = []
    if len(unique) != len(seeds):
        seen: dict[int, Address] = {}
        for x in reachable:
            prev = seen.setdefault(x.seed, x)
            if prev is not x:
                dupes.append((prev, x))
    return {
        "addresses": len(reachable),
        "unique_seeds": len(unique),
        "collision_free": len(unique) == len(seeds),
        "collisions": [(str(p), str(q)) for p, q in dupes[:8]],
        "min_seed": min(seeds) if seeds else None,
        "max_seed": max(seeds) if seeds else None,
    }


def bounds_are_injective_by_construction() -> bool:
    """The positional code is injective iff each field fits its stride."""
    return (MAX_REPLICATES <= NAMESPACE_STRIDE
            and MAX_NAMESPACES * NAMESPACE_STRIDE <= STRATUM_STRIDE
            and MAX_STRATA * STRATUM_STRIDE <= CELL_STRIDE
            and max(NAMESPACE_INDEX.values(), default=0) < MAX_NAMESPACES)
