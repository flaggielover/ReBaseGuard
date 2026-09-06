"""The exact SR work universe (8,849 obligations), its sharding, and resume identity.

Generalises the Task1R architecture, which certified ONE object class (F_0) on ONE
patch at ONE drift, to the full frozen SR scope: every object class, every cell,
every m, plus derivatives, curvature and assembly.

Nothing is hard-coded that can be derived: the ordered identities come from the
frozen `universe.work_ids()` filtered to the SR detector, so this module cannot
drift from the frozen scope. It defines no new obligation and changes no
top-level count -- `ResolventCertificate` and any refinement evidence are NESTED
supporting evidence consumed inside these obligations, never new work IDs.

Sharding uses the frozen floor rule [floor(k*N/S), floor((k+1)*N/S)) with no
per-shard ceil inflation, so shards partition the universe exactly for any worker
count. Resume admission follows the corrected Aux4 principles: a record is
admissible only if its checkpoint hash, its producer TCB and its scientific hash
all match, and historically superseded universes are rejected outright.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
ROOT = NS.parents[2]
IMPL = ROOT / "level4/closure_proofs/p5y_k1_cover_ledger_implementation/code"
SPECC = ROOT / "level4/closure_proofs/p5y_k1_cover_ledger_successor/code"
for _p in (str(IMPL), str(SPECC), str(Path(__file__).resolve().parent)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import spec                                                        # noqa: E402
import universe as frozen_universe                                 # noqa: E402

import sr_provenance as PR                                         # noqa: E402

DETECTOR = "SR"
EXPECTED_SR_OBLIGATIONS = 8849


class UniverseMismatch(RuntimeError):
    """The derived SR universe does not match the frozen scope."""


class InadmissibleRecord(RuntimeError):
    """A resume record was rejected by the admission rules."""


def work_ids() -> list[tuple]:
    """Ordered SR obligation identities, filtered from the frozen universe."""
    return [w for w in frozen_universe.work_ids() if w[0] == DETECTOR]


def work_id_str(w: tuple) -> str:
    """Canonical deterministic string identity: SR:<cell>:<kind>:<name>."""
    return f"{w[0]}:{w[1]}:{w[2]}:{w[3]}"


def audit() -> dict:
    """Exact count, no duplicates, no gaps, exact cell/m/function identities."""
    ids = work_ids()
    findings, ok = [], True
    if len(ids) != EXPECTED_SR_OBLIGATIONS:
        ok = False
        findings.append(f"count {len(ids)} != {EXPECTED_SR_OBLIGATIONS}")
    strs = [work_id_str(w) for w in ids]
    if len(set(strs)) != len(strs):
        ok = False
        findings.append("duplicate work IDs")
    cells = sorted({w[1] for w in ids if w[1] >= 0})
    if cells != list(range(spec.COUNTS["SR"])):
        ok = False
        findings.append("cell indices are not exactly 0..315")
    per_cell: dict[int, set] = {}
    for w in ids:
        if w[1] >= 0:
            per_cell.setdefault(w[1], set()).add((w[2], w[3]))
    shapes = {frozenset(v) for v in per_cell.values()}
    if len(shapes) != 1:
        ok = False
        findings.append("cells do not all carry the same obligation shape")
    shape = sorted(next(iter(shapes))) if shapes else []
    expect_shape = sorted(
        [("object", n) for n in frozen_universe.OBJECTS]
        + [("dependency_bundle", "orders_0_1")]
        + [("curvature", str(m)) for m in spec.M_VALUES]
        + [("assembly", str(m)) for m in spec.M_VALUES])
    if shape != expect_shape:
        ok = False
        findings.append("per-cell obligation shape differs from the frozen one")
    far = [w for w in ids if w[1] < 0]
    if len(far) != 1 or far[0][2] != "far_field":
        ok = False
        findings.append("SR far-field unit is not exactly one")
    # the global universe must not have moved
    if len(frozen_universe.work_ids()) != spec.TOTAL_UNITS != 17978:
        ok = False
        findings.append("top-level universe changed")
    return {"ok": ok, "findings": findings, "n_sr_obligations": len(ids),
            "n_cells": len(cells), "obligations_per_cell": len(shape),
            "far_field_units": len(far),
            "total_universe": len(frozen_universe.work_ids())}


# ------------------------------------------------------------------ sharding
def shard(k: int, n_shards: int, ids: list | None = None) -> list[tuple]:
    """Frozen floor rule; shards partition the universe exactly."""
    ids = work_ids() if ids is None else ids
    N = len(ids)
    if not 0 <= k < n_shards:
        raise ValueError(f"shard {k} outside 0..{n_shards - 1}")
    lo = (k * N) // n_shards
    hi = ((k + 1) * N) // n_shards
    return ids[lo:hi]


def shard_conservation(n_shards: int) -> dict:
    ids = work_ids()
    seen: list[tuple] = []
    for k in range(n_shards):
        seen += shard(k, n_shards, ids)
    return {"n_shards": n_shards, "total": len(ids), "covered": len(seen),
            "exact_partition": seen == ids,
            "no_overlap": len({work_id_str(w) for w in seen}) == len(ids)}


# -------------------------------------------------------------- resume identity
def resume_identity(work_id: tuple, record: dict, tcb: dict) -> str:
    """Exact resume identity for ONE SR obligation.

    Binds the work ID, the scientific hash of the record, the producer TCB and the
    frozen checkpoint hash. Changing any one of them changes the identity, so a
    record cannot be replayed across cells, across m, or across producers.
    """
    return PR.sha256_bytes(PR.canonical({
        "work_id": work_id_str(work_id),
        "scientific_hash": PR.scientific_hash(record),
        "tcb": tcb,
        "checkpoint_sha256": spec.CHECKPOINT_SHA256,
        "schema": PR.SCHEMA,
    }))


def admit(work_id: tuple, record: dict, tcb: dict, *,
          claimed_identity: str, claimed_universe_size: int) -> bool:
    """Resume admission. Rejects superseded universes and identity drift."""
    if claimed_universe_size in frozen_universe.SUPERSEDED_UNIVERSES:
        raise InadmissibleRecord(
            f"record bound to the superseded {claimed_universe_size}-object universe")
    if claimed_universe_size != spec.TOTAL_UNITS:
        raise InadmissibleRecord(
            f"record universe {claimed_universe_size} != frozen {spec.TOTAL_UNITS}")
    if record.get("checkpoint_sha256") in frozen_universe.SUPERSEDED_CHECKPOINT_HASHES:
        raise InadmissibleRecord("record bound to a superseded checkpoint hash")
    actual = resume_identity(work_id, record, tcb)
    if actual != claimed_identity:
        raise InadmissibleRecord("resume identity mismatch (stale producer or record)")
    return True


def write_manifest(path: Path | None = None) -> Path:
    path = path or (NS / "config/sr_work_universe.json")
    ids = work_ids()
    a = audit()
    path.write_text(json.dumps({
        "schema": "k1.sr.work-universe.v1",
        "detector": DETECTOR,
        "n_obligations": len(ids),
        "n_cells": spec.COUNTS["SR"],
        "m_values": list(spec.M_VALUES),
        "by_kind": dict(Counter(w[2] for w in ids)),
        "first": [work_id_str(w) for w in ids[:4]],
        "last": [work_id_str(w) for w in ids[-4:]],
        "ordered_ids_sha256": PR.sha256_bytes(
            PR.canonical([work_id_str(w) for w in ids])),
        "audit": a,
    }, indent=1, sort_keys=True) + "\n")
    return path


if __name__ == "__main__":
    a = audit()
    print(json.dumps(a, indent=1))
    for s in (1, 4, 7, 64, 317):
        c = shard_conservation(s)
        print(f"  shards={s:>4}: exact_partition={c['exact_partition']} "
              f"no_overlap={c['no_overlap']} covered={c['covered']}")
    print("manifest:", write_manifest())
