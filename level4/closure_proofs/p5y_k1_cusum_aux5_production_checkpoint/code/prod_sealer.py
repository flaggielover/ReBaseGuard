"""Seal-time verification of one CUSUM Aux5 cell record. NON-CERTIFYING.

A record enters the production ledger only if every check below holds; each failure is a Refusal with its
own code. Obligation statuses (PASS/...) are scientific outcomes and are NEVER read here.

  QUALIFICATION_RECORD_REUSE  the file is byte-identical to a qualification record (318/323, A/B)
  SYNTHETIC_PRODUCTION_MIX    a synthetic fixture offered to production, or a genuine record to a synthetic run
  RESULT_SCHEMA               required top-level fields, the exact m scope {1,2,3,5}, the exact per-m key set
  CELL_IDENTITY, FROZEN_GEOMETRY, PRECISION
  PRODUCER_IDENTITY, RUNTIME_CONTRACT, FINAL_GATE, PROVENANCE_CHAIN, SCIPY_GUARD, UNIVERSE
  K4_INPUT_STRUCTURE          the fields the frozen K4 assembly reads, present as exact rationals (never compared)
  SCIENTIFIC_HASH, AUXILIARY_HASH, K4_HASH_COVERAGE    recomputed with the frozen Aux4 hash semantics
  CPU_EVIDENCE_INCONSISTENT   the record claims more CPU or wall time than its attempt could have used
  RECORD_PREDATES_ATTEMPT     the file is older than its reservation

The last two make a copied-in record (qualification or otherwise) unsealable: an attempt that did not
compute the cell cannot have used the CPU the record claims.
"""
from __future__ import annotations

import copy
import json
import os
import sys
from pathlib import Path

from prod_cells import M_VALUES
from prod_common import (AUX4_NS, HEX64, Refusal, canonical, fsync_dir, is_rational_str, sha256_bytes,
                         sha256_file)

HASH_MODULE_SHA256 = {
    "ancestry4.py": "91d517955345e38592b11cabfe76edcf7594872c195950ff18c66aee2e50048a",
    "schema.py": "25c70663affa90122db60fcb859c4576d3c9d73469c6ac7522f8c9091dc54211",
    "hash_v2.py": "c00912e39d3e71a2c6c3f8684c24d7a8d9ceb6b6750331d2dbd9140bf679518a",
}
RECORD_SCHEMA = "k1.cusum-aux4.cell-record.v2"
REQUIRED_TOP_LEVEL = (
    "C_upper", "auxiliary_evidence", "auxiliary_evidence_hash", "campaign", "cell_index", "certificates",
    "cpu_seconds_including_dependencies", "detector", "e0", "implementation_hash_kind", "m",
    "obligation_universe_total", "precision_bits", "producer", "producer_identity_hash", "producer_manifest_hash",
    "producer_manifest_path", "producer_manifest_schema", "producer_manifest_version", "provenance_chain", "rho",
    "runtime_contract_hash", "scientific_content_hash", "scipy_guard", "universe", "wall_seconds",
)
PER_M_KEYS = (
    "C_upper", "D_interval", "D_interval_mag", "M_R2", "R2_interval", "R_interval", "R_interval_mag",
    "cell_index", "channel_provenance", "cover", "detector", "e0", "local_gates", "m",
    "nested_candidate_gates", "rho", "status", "target_gate", "top_level_gates", "worst_top_level_utilization",
)
INTERVALS = ("R_interval", "D_interval", "R2_interval")
SYNTHETIC_STAMP = "SYNTHETIC_FIXTURE_NOT_SCIENCE"
OBLIGATIONS_PER_CELL = 28
UNIVERSE_TOTAL = 17978
CPU_SLACK_S = 2.0
WALL_SLACK_S = 2.0
MTIME_SLACK_S = 2.0

_MODULES: dict = {}


def hash_modules():
    """The frozen Aux4 scientific-hash semantics, imported only after their bytes are verified."""
    if not _MODULES:
        code = AUX4_NS / "code"
        for name, digest in HASH_MODULE_SHA256.items():
            if sha256_file(code / name) != digest:
                raise Refusal("HASH_SEMANTICS_MUTATED", f"{name} differs from the frozen Aux4 bytes")
        if str(code) not in sys.path:
            sys.path.append(str(code))
        import hash_v2
        import schema
        for mod, name in ((hash_v2, "hash_v2.py"), (schema, "schema.py")):
            if Path(mod.__file__).resolve() != (code / name).resolve():
                raise Refusal("HASH_SEMANTICS_SHADOWED", f"{name} was imported from {mod.__file__}")
        if hash_v2.SCHEMA != RECORD_SCHEMA:
            raise Refusal("HASH_SEMANTICS_MUTATED", f"record schema {hash_v2.SCHEMA!r}")
        _MODULES.update(H=hash_v2, S=schema)
    return _MODULES["H"], _MODULES["S"]


# ------------------------------------------------------------------ K4 structure (never compares values)
def k4_consumed_paths() -> list[str]:
    paths = ["cell_index", "detector", "e0.0", "e0.1", "rho.0", "rho.1", "C_upper", "precision_bits",
             "producer_identity_hash", "producer.producer_identity_hash", "runtime_contract_hash",
             "producer.runtime.precision_bits"]
    for m in M_VALUES:
        for iv in INTERVALS:
            paths += [f"m.{m}.{iv}.lo", f"m.{m}.{iv}.hi"]
        paths += [f"m.{m}.M_R2", f"m.{m}.detector"]
    return paths


def k4_structure_problems(rec: dict) -> list[str]:
    out = []

    def rational(value, where):
        if not is_rational_str(value):
            out.append(f"{where}: not an exact rational string")

    idx = rec.get("cell_index")
    if not isinstance(idx, int) or isinstance(idx, bool):
        out.append("cell_index: not an int")
    if rec.get("detector") != "CUSUM":
        out.append("detector: not CUSUM")
    for g in ("e0", "rho"):
        v = rec.get(g)
        if isinstance(v, list) and len(v) == 2:
            rational(v[0], f"{g}.0")
            rational(v[1], f"{g}.1")
        else:
            out.append(f"{g}: not an exact [p, s] pair")
    rational(rec.get("C_upper"), "C_upper")
    if rec.get("precision_bits") != 256:
        out.append("precision_bits: not 256")
    ident = rec.get("producer_identity_hash")
    if not (isinstance(ident, str) and HEX64.fullmatch(ident)):
        out.append("producer_identity_hash: not a sha256")
    prod = rec.get("producer") if isinstance(rec.get("producer"), dict) else {}
    if prod.get("producer_identity_hash") != ident:
        out.append("producer.producer_identity_hash differs from producer_identity_hash")
    if (prod.get("runtime") or {}).get("precision_bits") != 256:
        out.append("producer.runtime.precision_bits: not 256")
    m = rec.get("m")
    if not isinstance(m, dict) or set(m) != set(M_VALUES):
        out.append(f"m scope is not {list(M_VALUES)}")
        return out
    for k in M_VALUES:
        entry = m[k]
        if not isinstance(entry, dict):
            out.append(f"m.{k}: not a mapping")
            continue
        if entry.get("detector") != "CUSUM":
            out.append(f"m.{k}.detector: not CUSUM")
        for iv in INTERVALS:
            d = entry.get(iv)
            if not isinstance(d, dict):
                out.append(f"m.{k}.{iv}: missing")
                continue
            rational(d.get("lo"), f"m.{k}.{iv}.lo")
            rational(d.get("hi"), f"m.{k}.{iv}.hi")
        rational(entry.get("M_R2"), f"m.{k}.M_R2")
        for g in ("cell_index", "e0", "rho", "C_upper"):
            if entry.get(g) != rec.get(g):
                out.append(f"m.{k}.{g}: inconsistent with the cell")
    return out


def _walk(obj, path: str):
    parts = path.split(".")
    for p in parts[:-1]:
        obj = obj[int(p)] if isinstance(obj, list) else obj[p]
    return obj, (int(parts[-1]) if isinstance(obj, list) else parts[-1])


def hash_coverage_problems(rec: dict, *, mutate: bool) -> list[str]:
    """Every K4-consumed leaf must be hashed: never classified incidental, and (if `mutate`) moving it must
    move the scientific hash."""
    H, S = hash_modules()
    out = []
    base = H.record_scientific_hash(rec)
    if base != rec.get("scientific_content_hash"):
        out.append("scientific_content_hash does not recompute")
    for path in k4_consumed_paths():
        if S.classify(path) == S.INCIDENTAL:
            out.append(f"{path}: classified INCIDENTAL (outside the scientific hash)")
        if mutate:
            twin = copy.deepcopy(rec)
            parent, key = _walk(twin, path)
            value = parent[key]
            parent[key] = value + 1 if isinstance(value, int) and not isinstance(value, bool) else f"{value}~"
            if H.record_scientific_hash(twin) == base:
                out.append(f"{path}: mutation does not move the scientific hash")
    return out


# ------------------------------------------------------------------ the seal check
def verify_record(path, *, cell: int, spec, measured_cpu_usec=None, wall_bound_s=None,
                  not_before_wall=None) -> dict:
    path = Path(path)
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise Refusal("RECORD_MISSING", str(exc)) from exc
    digest = sha256_bytes(raw)
    if digest in spec.qualification_record_sha256:
        raise Refusal("QUALIFICATION_RECORD_REUSE",
                      f"{path.name} is byte-identical to a qualification record; qualification is never production")
    try:
        rec = json.loads(raw)
    except ValueError as exc:
        raise Refusal("RECORD_UNPARSEABLE", str(exc)[:200]) from exc
    if not isinstance(rec, dict):
        raise Refusal("RECORD_UNPARSEABLE", "not a JSON object")
    if (rec.get(SYNTHETIC_STAMP) is True) != spec.synthetic:
        raise Refusal("SYNTHETIC_PRODUCTION_MIX", f"record synthetic={rec.get(SYNTHETIC_STAMP) is True}, "
                                                  f"campaign mode {spec.mode}")
    missing = [k for k in REQUIRED_TOP_LEVEL if k not in rec]
    if missing:
        raise Refusal("RESULT_SCHEMA", f"missing top-level fields {missing[:6]}")
    if rec["cell_index"] != cell or rec["detector"] != "CUSUM":
        raise Refusal("CELL_IDENTITY", f"record is {rec['detector']} cell {rec['cell_index']}, attempt is CUSUM {cell}")
    geo = spec.cells[cell]
    for g in ("e0", "rho", "C_upper"):
        if rec[g] != geo[g]:
            raise Refusal("FROZEN_GEOMETRY", f"{g} differs from the frozen cell table")
    if rec["precision_bits"] != spec.precision_bits:
        raise Refusal("PRECISION", f"precision_bits {rec['precision_bits']!r}")
    for key, value in spec.identity.items():
        if rec.get(key) != value:
            raise Refusal("RUNTIME_CONTRACT" if key == "runtime_contract_hash" else "PRODUCER_IDENTITY",
                          f"{key} {rec.get(key)!r} != frozen {value!r}")
    prod = rec["producer"] if isinstance(rec["producer"], dict) else {}
    for key in ("producer_manifest_hash", "runtime_contract_hash", "producer_identity_hash"):
        if prod.get(key) != spec.identity[key]:
            raise Refusal("PRODUCER_IDENTITY", f"producer.{key} differs from the frozen identity")
    if prod.get("runtime") != spec.runtime:
        raise Refusal("RUNTIME_CONTRACT", "producer.runtime differs from the frozen runtime contract")
    if sha256_bytes(canonical(prod["runtime"])) != spec.identity["runtime_contract_hash"]:
        raise Refusal("RUNTIME_CONTRACT", "the runtime contract does not hash to runtime_contract_hash")
    gate = prod.get("final_gate") or {}
    if gate.get("stage") != "final" or gate.get("ran_after_scientific_hash") is not True:
        raise Refusal("FINAL_GATE", "the final fail-closed gate did not authorise this record")
    chain = rec["provenance_chain"] if isinstance(rec["provenance_chain"], dict) else {}
    if not (chain.get("all_verified") is True and chain.get("obligations") == OBLIGATIONS_PER_CELL
            and chain.get("units_verified") == OBLIGATIONS_PER_CELL and chain.get("auxiliary_evidence_bound") is True
            and isinstance(rec["certificates"], dict) and len(rec["certificates"]) == OBLIGATIONS_PER_CELL):
        raise Refusal("PROVENANCE_CHAIN", "provenance chain incomplete")
    if (rec["scipy_guard"] or {}).get("scipy_free") is not True:
        raise Refusal("SCIPY_GUARD", "the run was not certified SciPy-free")
    if rec["obligation_universe_total"] != UNIVERSE_TOTAL or (rec["universe"] or {}).get("ok") is not True:
        raise Refusal("UNIVERSE", "obligation universe is not the frozen 17978")
    m = rec["m"]
    if not isinstance(m, dict) or set(m) != set(M_VALUES):
        raise Refusal("RESULT_SCHEMA", f"m scope is not {list(M_VALUES)}")
    for k in M_VALUES:
        if not isinstance(m[k], dict) or set(m[k]) != set(PER_M_KEYS):
            raise Refusal("RESULT_SCHEMA", f"m.{k} key set differs from the frozen per-m schema")
    problems = k4_structure_problems(rec)
    if problems:
        raise Refusal("K4_INPUT_STRUCTURE", "; ".join(problems[:5]))
    H, S = hash_modules()
    if H.record_scientific_hash(rec) != rec["scientific_content_hash"]:
        raise Refusal("SCIENTIFIC_HASH", "scientific_content_hash does not recompute")
    if H.auxiliary_evidence_hash(rec) != rec["auxiliary_evidence_hash"]:
        raise Refusal("AUXILIARY_HASH", "auxiliary_evidence_hash does not recompute")
    if not H.audit_record(rec)["ok"]:
        raise Refusal("SCIENTIFIC_HASH", "record has fields unaccounted for by the hash")
    for p in k4_consumed_paths():
        if S.classify(p) == S.INCIDENTAL:
            raise Refusal("K4_HASH_COVERAGE", f"{p} is outside the scientific hash")
    cpu, wall = rec["cpu_seconds_including_dependencies"], rec["wall_seconds"]
    for name, v in (("cpu_seconds_including_dependencies", cpu), ("wall_seconds", wall)):
        if isinstance(v, bool) or not isinstance(v, (int, float)) or v < 0:
            raise Refusal("CPU_EVIDENCE_INCONSISTENT", f"{name} is not a non-negative number")
    if measured_cpu_usec is not None and measured_cpu_usec / 1e6 + CPU_SLACK_S < cpu:
        raise Refusal("CPU_EVIDENCE_INCONSISTENT",
                      f"record claims {cpu:.1f} CPU-s; its attempt used at most {measured_cpu_usec / 1e6:.1f}")
    if wall_bound_s is not None and wall_bound_s + WALL_SLACK_S < wall:
        raise Refusal("CPU_EVIDENCE_INCONSISTENT",
                      f"record claims {wall:.1f} wall-s; its attempt lasted at most {wall_bound_s:.1f}")
    if not_before_wall is not None and path.stat().st_mtime + MTIME_SLACK_S < not_before_wall:
        raise Refusal("RECORD_PREDATES_ATTEMPT", f"{path.name} was written before its reservation")
    return {"record_sha256": digest, "scientific_content_hash": rec["scientific_content_hash"],
            "auxiliary_evidence_hash": rec["auxiliary_evidence_hash"], "claimed_cpu_seconds": cpu,
            "size_bytes": len(raw)}


def seal_file(path) -> None:
    """Make a verified record read-only and its directory entry durable, before the SEALED ledger write."""
    path = Path(path)
    os.chmod(path, 0o444)
    fsync_dir(path.parent)
