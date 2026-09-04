"""Pilot-3 logical addressing.  Same architecture as Pilot-2, new campaign.

Brief section 21: the RNG/shard architecture is NOT redesigned.  This module
is Pilot-2's positional code with a fresh campaign base so that no Pilot-3
stream can coincide with Pilot-2, Pilot-1, the P4X R0 pilot, P4X production or
the frozen P4 campaign.  Keyed by logical scientific identity only; worker id,
process id, shard index and scheduling order are not arguments.  No modulo
compression.
"""

from __future__ import annotations

from dataclasses import dataclass

#: Pilot-2 occupies [6.31e9, 6.31e9 + MAX_CELLS(20) * 1e8) = up to 8.31e9.
#: Pilot-3 starts a clean 1e9 above that theoretical ceiling.
CAMPAIGN_BASE = 9_310_000_000
PILOT2_CEILING = 6_310_000_000 + 20 * 100_000_000

CELL_STRIDE = 100_000_000
STRATUM_STRIDE = 10_000_000
NAMESPACE_STRIDE = 1_000_000
MAX_REPLICATES = NAMESPACE_STRIDE
MAX_CELLS = 20
MAX_STRATA = 10
MAX_NAMESPACES = 10

NAMESPACE_INDEX = {
    "benchmark": 0,     # the high-quality "truth" reference; never reused
    "reference": 1,     # the Bmin-block production-style reference draw
    "design": 2,        # selects (Bmin, UCB, kappa, cap); never an endpoint
    "validation": 3,    # the ONLY source of the primary endpoint
    "probe": 9,         # pre-freeze feasibility only
}

CELL_INDEX: dict[str, int] = {}
STRATUM_INDEX: dict[str, int] = {}


class AddressError(ValueError):
    pass


def register(cells: dict[str, int], strata: dict[str, int]) -> None:
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
                raise AddressError(f"{what} index {idx} used by {clash[0]!r}")
            table[key] = idx


def seed(cell: str, stratum: str, namespace: str, replicate: int) -> int:
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


def audit_reachable_domain(reachable: list[Address]) -> dict:
    seeds = [a.seed for a in reachable]
    unique = set(seeds)
    dupes = []
    if len(unique) != len(seeds):
        seen: dict[int, Address] = {}
        for a in reachable:
            prev = seen.setdefault(a.seed, a)
            if prev is not a:
                dupes.append((str(prev), str(a)))
    return {"addresses": len(reachable), "unique_seeds": len(unique),
            "collision_free": len(unique) == len(seeds),
            "collisions": dupes[:8],
            "min_seed": min(seeds) if seeds else None,
            "max_seed": max(seeds) if seeds else None}


def bounds_are_injective_by_construction() -> bool:
    return (MAX_REPLICATES <= NAMESPACE_STRIDE
            and MAX_NAMESPACES * NAMESPACE_STRIDE <= STRATUM_STRIDE
            and MAX_STRATA * STRATUM_STRIDE <= CELL_STRIDE
            and max(NAMESPACE_INDEX.values(), default=0) < MAX_NAMESPACES)
