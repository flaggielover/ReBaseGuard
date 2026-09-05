"""K1 successor production: work-unit identity, sharding and record schemas.

Everything here is derived from the FROZEN successor checkpoint. No scientific
parameter is defined in this file; it only enumerates and addresses work.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
ROOT = NS.parents[2]
SUC = ROOT / "level4/closure_proofs/p5y_k1_successor_optimized"
AUD = ROOT / "level4/closure_proofs/p5y_k1_sr_backend_cost_audit"

RECORD_SCHEMA = "rebaseguard.p5y.k1.cell_record.v1"
INDEX_SCHEMA = "rebaseguard.p5y.k1.aggregate_index.v1"

STATUS = ("COMPLETE", "FAILED", "NOT_RUN", "NOT_IMPLEMENTED")


def load_checkpoint() -> dict:
    return json.loads((SUC / "config/checkpoint_s.json").read_text())


def checkpoint_hash() -> str:
    """Recomputed, never read from a field."""
    man = json.loads((SUC / "manifests/successor_manifest.json").read_text())
    agg = hashlib.sha256()
    for f, h in man["file_sha256"].items():
        cur = hashlib.sha256((SUC / f).read_bytes()).hexdigest()
        if cur != h:
            raise RuntimeError(f"successor checkpoint file altered: {f}")
        agg.update(f.encode()); agg.update(b"\0")
        agg.update(h.encode()); agg.update(b"\n")
    return agg.hexdigest()


def backend_hash() -> str:
    """Hash of the qualified optimized backend plus the Task1R reference harness."""
    T1R = ROOT / "level4/closure_proofs/p5y_k1_task1r_budget_harness"
    agg = hashlib.sha256()
    for p in (AUD / "code/opt_backend.py", T1R / "code/harness.py"):
        agg.update(p.name.encode()); agg.update(b"\0")
        agg.update(hashlib.sha256(p.read_bytes()).hexdigest().encode()); agg.update(b"\n")
    return agg.hexdigest()


# ------------------------------------------------------------ work enumeration
def function_ids(ck: dict) -> list[str]:
    """The frozen 19-function DAG order -- deterministic, never sorted or filtered."""
    return [f["id"] for f in ck["production_dag"]["functions"]]


def enumerate_units(ck: dict) -> list[tuple[str, int, str]]:
    """Deterministic global unit list: detector-major, then sub-cell, then function.

    CUSUM first: the frozen execution order runs the cheap detector first so a
    governance or scientific failure surfaces for ~126 CPU-h instead of ~387.
    """
    fns = function_ids(ck)
    units: list[tuple[str, int, str]] = []
    for det in ("CUSUM", "SR"):
        n = ck["cover"][det]["subcell_count"]
        for cell in range(n):
            for fn in fns:
                units.append((det, cell, fn))
    return units


def unit_id(det: str, cell: int, fn: str) -> str:
    return f"{det}:{cell:04d}:{fn}"


def shard_bounds(n: int, shards: int) -> list[tuple[int, int]]:
    """FLOOR boundaries. Never ceil-per-shard: that is the P4X defect, which
    overexecutes because shards*ceil(n/shards) > n."""
    if shards < 1:
        raise ValueError("shards must be >= 1")
    b = [(n * k) // shards for k in range(shards + 1)]
    return [(b[k], b[k + 1]) for k in range(shards)]


def verify_conservation(n: int, shards: int) -> dict:
    sb = shard_bounds(n, shards)
    covered: list[int] = []
    for lo, hi in sb:
        covered.extend(range(lo, hi))
    return {"shards": shards, "total": n, "sum_sizes": sum(hi - lo for lo, hi in sb),
            "exact": sum(hi - lo for lo, hi in sb) == n,
            "no_duplicates": len(covered) == len(set(covered)),
            "no_missing": set(covered) == set(range(n)),
            "first": sb[0][0] == 0, "last": sb[-1][1] == n}


# ------------------------------------------------------------- record helpers
def new_record(det: str, cell: int, fn: str, *, ck_hash: str, be_hash: str) -> dict:
    return {
        "schema": RECORD_SCHEMA,
        "work_id": unit_id(det, cell, fn),
        "checkpoint_hash": ck_hash,
        "backend_hash": be_hash,
        "detector": det,
        "subcell_index": cell,
        "e_interval": None,
        "patch": None,
        "function_id": fn,
        "m_relevance": None,
        # --- the certified outputs, persisted BY DESIGN (see driver docstring)
        "R_enclosure": None,
        "R_prime_enclosure": None,
        "contributing_object_ids": [],
        # --- ledger provenance
        "candidate_id": None, "candidate_degree": None, "candidate_residual": None,
        "kernel_residual": None, "resolvent_amplification_bound": None,
        "rounding_error": None, "interval_radius": None,
        "propagated_absolute_half_width": None, "allowed_absolute_half_width": None,
        "budget_usage_by_component": None,
        "endpoint_sliver_contribution": None,
        "P1_E_d": None, "P1_headroom_rel": None,
        "complexity_score": None, "working_precision_bits": None,
        # --- accounting
        "cpu_seconds": None, "peak_rss_mib": None,
        "status": "NOT_RUN", "failure_class": None,
        "certificate_status": None,
    }


def atomic_append(path: Path, obj: dict) -> None:
    """Atomic per-record write: a crash can never leave a torn line."""
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(obj, sort_keys=True) + "\n"
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".part")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(line)
            f.flush()
            os.fsync(f.fileno())
        with open(path, "a") as out, open(tmp) as src:
            out.write(src.read())
            out.flush()
            os.fsync(out.fileno())
    finally:
        os.unlink(tmp)


def read_records(path: Path) -> tuple[list[dict], int]:
    """Return (valid records, count of rejected corrupt/partial lines)."""
    if not path.exists():
        return [], 0
    good, bad = [], 0
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            bad += 1
            continue
        if r.get("schema") != RECORD_SCHEMA or "work_id" not in r:
            bad += 1
            continue
        good.append(r)
    return good, bad
