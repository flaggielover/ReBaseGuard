"""PHASE 3: a canonical, deterministic scientific certificate hash.

THE INDEPENDENT FINDING
-----------------------
"repeated fresh runs can produce different exact certificate hashes under the
same producer identity."

FIELD-BY-FIELD CLASSIFICATION (see `determinism.classify_fields`)

    cpu_seconds, cpu_seconds_prepare, wall_seconds, peak_rss_kib
        NONDETERMINISTIC_RUNTIME_NOISE  -- excluded
    bernstein_calls, kernel_calls
        NONDETERMINISTIC_RUNTIME_NOISE (cache-order dependent) -- excluded
    threading, host metadata, logs
        NONDETERMINISTIC_RUNTIME_NOISE  -- excluded
    JSON key order
        SERIALIZATION_NOISE -- neutralised by sorted canonical serialisation
    norm_improvement (float ratios, diagnostic)
        SERIALIZATION_NOISE / diagnostic -- excluded
    residual deltas, eps nodes, R/D/R2 intervals, M_R2, cover, gates, status
        SCIENTIFIC_CONTENT -- INCLUDED

    float candidate coefficients
        IMPLEMENTATION_DEFECT if BLAS runs multi-threaded: `np.linalg.solve`
        reduction order then varies run to run, the degree-12 dyadic candidate
        changes, and every certified residual changes with it. That is
        scientifically meaningful drift, so it is NOT normalised away. It is
        removed at the source: `successor_qualify` pins the threading contract
        BEFORE numpy is imported (re-exec'ing if necessary), and the contract
        (`blas_threads = 1`, `flint_threads = 1`) is bound into the producer
        identity, so a record made under different threading is a different
        producer rather than a silently different certificate.

REQUIRED INVARIANT
------------------
    same certifying bytes + same exact inputs + same precision
      => same canonical scientific certificate hash

`determinism.py` tests it by repeated fresh runs in separate processes.
"""
from __future__ import annotations

import hashlib
import json

import ancestry                                                 # noqa: F401

import certhash as repair2_certhash                             # noqa: E402
import spec                                                     # noqa: E402

SCHEMA = "k1.cusum-successor.certificate.v1"

# Fields that must never enter a scientific certificate hash.
EXCLUDED_RUNTIME_FIELDS = (
    "cpu_seconds", "cpu_seconds_prepare", "cpu_seconds_including_dependencies",
    "wall_seconds", "peak_rss_kib", "bernstein_calls", "kernel_calls",
    "threading", "host", "norm_improvement", "tightening_report",
    "generated_utc", "pid",
)

OBJECTS = repair2_certhash.OBJECTS


def canonical(obj) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True) + "\n").encode("ascii")


def _strip(node):
    """Recursively drop runtime-noise fields wherever they appear."""
    if isinstance(node, dict):
        return {k: _strip(v) for k, v in node.items()
                if k not in EXCLUDED_RUNTIME_FIELDS}
    if isinstance(node, list):
        return [_strip(v) for v in node]
    return node


def certified_content(unit: tuple, record: dict) -> dict:
    """Reuse the validated Repair2 extraction, then strip runtime noise."""
    return _strip(repair2_certhash.certified_content(unit, record))


def obligation_status(unit: tuple, record: dict) -> str:
    return repair2_certhash.obligation_status(unit, record)


def build_certificate(unit: tuple, identity: dict, record: dict) -> dict:
    return {"schema": SCHEMA, "identity": identity,
            "certified": certified_content(unit, record),
            "status": obligation_status(unit, record)}


def certificate_hash(certificate: dict) -> str:
    for field in EXCLUDED_RUNTIME_FIELDS:
        if field in certificate:
            raise ValueError(f"{field} is runtime noise; not hashable content")
    return hashlib.sha256(canonical(_strip(certificate))).hexdigest()


def record_scientific_hash(record: dict) -> str:
    """One hash over a whole cell record's scientific content.

    Used by the repeated-run determinism test: it must be identical across
    fresh processes with identical inputs.
    """
    payload = {
        "detector": record["detector"],
        "cell_index": record["cell_index"],
        "precision_bits": record["precision_bits"],
        "e0": record["e0"], "rho": record["rho"], "C_upper": record["C_upper"],
        "objects": {k: {f: v[f] for f in ("delta_mid", "delta_cell", "envelope")
                        if f in v}
                    for k, v in record["objects"].items()},
        "eps_mid": record.get("eps_mid", {}),
        "eps_cell": record.get("eps_cell", {}),
        "eps_cell_refined": record.get("eps_cell_refined", {}),
        "m": _strip(record["m"]),
    }
    return hashlib.sha256(canonical(payload)).hexdigest()
