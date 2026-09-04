"""Pilot-4 logical addressing.  Architecture inherited, fresh campaign base."""

from __future__ import annotations

from dataclasses import dataclass

#: Pilot-3 occupies [9.31e9, 9.31e9 + 20*1e8) = up to 1.131e10.  Pilot-4 starts
#: a clean 1e9 above that theoretical ceiling.
CAMPAIGN_BASE = 12_310_000_000
PILOT3_CEILING = 9_310_000_000 + 20 * 100_000_000

CELL_STRIDE = 100_000_000
NAMESPACE_STRIDE = 1_000_000
MAX_REPLICATES = NAMESPACE_STRIDE
MAX_CELLS = 20
MAX_NAMESPACES = 10

NAMESPACE_INDEX = {
    "master0": 0,      # independent benchmark master pool 0
    "master1": 1,      # independent benchmark master pool 1
    "reference": 2,    # R disjoint fresh reference draws
    "probe": 9,        # pre-freeze feasibility only
}

CELL_INDEX: dict[str, int] = {}


class AddressError(ValueError):
    pass


def register(cells: dict[str, int]) -> None:
    for key, idx in cells.items():
        if not 0 <= idx < MAX_CELLS:
            raise AddressError(f"cell index {idx} outside the domain")
        if CELL_INDEX.get(key, idx) != idx:
            raise AddressError(f"cell {key!r} already frozen at {CELL_INDEX[key]}")
        clash = [k for k, v in CELL_INDEX.items() if v == idx and k != key]
        if clash:
            raise AddressError(f"cell index {idx} used by {clash[0]!r}")
        CELL_INDEX[key] = idx


def seed(cell: str, namespace: str, replicate: int) -> int:
    if cell not in CELL_INDEX:
        raise AddressError(f"cell {cell!r} has no frozen address")
    if namespace not in NAMESPACE_INDEX:
        raise AddressError(f"namespace {namespace!r} has no frozen address")
    if not 0 <= replicate < MAX_REPLICATES:
        raise AddressError(f"replicate {replicate} outside the domain")
    return (CAMPAIGN_BASE + CELL_INDEX[cell] * CELL_STRIDE
            + NAMESPACE_INDEX[namespace] * NAMESPACE_STRIDE + replicate)


@dataclass(frozen=True, slots=True)
class Address:
    cell: str
    namespace: str
    replicate: int

    @property
    def seed(self) -> int:
        return seed(self.cell, self.namespace, self.replicate)


def audit_reachable_domain(reachable: list[Address]) -> dict:
    seeds = [a.seed for a in reachable]
    unique = set(seeds)
    dupes = []
    if len(unique) != len(seeds):
        seen = {}
        for a in reachable:
            prev = seen.setdefault(a.seed, a)
            if prev is not a:
                dupes.append((str(prev), str(a)))
    return {"addresses": len(reachable), "unique_seeds": len(unique),
            "collision_free": len(unique) == len(seeds), "collisions": dupes[:8],
            "min_seed": min(seeds) if seeds else None,
            "max_seed": max(seeds) if seeds else None}


def bounds_are_injective_by_construction() -> bool:
    return (MAX_REPLICATES <= NAMESPACE_STRIDE
            and MAX_NAMESPACES * NAMESPACE_STRIDE <= CELL_STRIDE
            and max(NAMESPACE_INDEX.values(), default=0) < MAX_NAMESPACES)
