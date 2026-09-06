"""PHASE 6/9: canonical certificate content hashing, auxiliary evidence included.

THE INVARIANT (inherited, adjudicated PASS, preserved unchanged)

    same producer manifest + same exact scientific inputs + same precision
      => same canonical scientific certificate hash

EXCLUDED, because they are incidental to the science and differ between honest
repeat runs: CPU seconds, wall seconds, peak RSS, call counters, host, pid,
timestamps, and the threading readback.

NOT EXCLUDED, on purpose: interval endpoints, error bounds, refined bounds,
status, source certificate hashes, exact cell and m parameters, producer
identity, and -- new here -- the auxiliary third-derivative evidence. Changing
one auxiliary bound changes the parent certificate's hash, which is what makes
the nested evidence part of the certificate rather than a comment on it.
"""
from __future__ import annotations

import hashlib
import json

import ancestry                                                 # noqa: F401

import certhash as repair2_certhash                             # noqa: E402

EXCLUDED_RUNTIME_FIELDS = (
    "cpu_seconds", "cpu_seconds_prepare", "cpu_seconds_including_dependencies",
    "cpu_seconds_auxiliary", "wall_seconds", "peak_rss_kib", "bernstein_calls",
    "kernel_calls", "threading", "host", "norm_improvement", "tightening_report",
    "generated_utc", "pid",
)

OBJECTS = repair2_certhash.OBJECTS


def canonical(obj) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True) + "\n").encode("ascii")


def _strip(node):
    if isinstance(node, dict):
        return {k: _strip(v) for k, v in sorted(node.items())
                if k not in EXCLUDED_RUNTIME_FIELDS}
    if isinstance(node, list):
        return [_strip(v) for v in node]
    return node


def auxiliary_evidence(record: dict) -> dict:
    """The nested third-derivative evidence, exactly as it is hashed."""
    return _strip({
        "kind": record.get("auxiliary_evidence", {}).get("kind"),
        "objects": record.get("auxiliary_evidence", {}).get("objects", {}),
        "midpoint_eps": record.get("auxiliary_evidence", {}).get("midpoint_eps", {}),
        "ownership": record.get("auxiliary_evidence", {}).get("ownership", {}),
        "node_refinement": record.get("node_refinement"),
    })


def auxiliary_evidence_hash(record: dict) -> str:
    return hashlib.sha256(canonical(auxiliary_evidence(record))).hexdigest()


def certified_content(unit: tuple, record: dict) -> dict:
    """Reuse the validated Repair2 extraction, then strip runtime noise."""
    return _strip(repair2_certhash.certified_content(unit, record))


def obligation_status(unit: tuple, record: dict) -> str:
    return repair2_certhash.obligation_status(unit, record)


def build_certificate(unit: tuple, identity: dict, record: dict) -> dict:
    return {"identity": identity,
            "certified": certified_content(unit, record),
            "status": obligation_status(unit, record)}


def certificate_hash(certificate: dict) -> str:
    for field in EXCLUDED_RUNTIME_FIELDS:
        if field in certificate:
            raise ValueError(f"{field} is runtime noise; not hashable content")
    return hashlib.sha256(canonical(_strip(certificate))).hexdigest()


def record_scientific_hash(record: dict) -> str:
    """One hash over a whole cell record's scientific content.

    Used by the repeated-run determinism test: it must be identical across fresh
    processes with identical inputs, and must move when any certified number,
    any auxiliary bound, or the producer identity moves.
    """
    payload = {
        "schema": "k1.cusum-aux3.cell-record.v1",
        "detector": record["detector"],
        "cell_index": record["cell_index"],
        "precision_bits": record["precision_bits"],
        "e0": record["e0"], "rho": record["rho"], "C_upper": record["C_upper"],
        "producer": _strip(record["producer"]),
        "objects": _strip(record["objects"]),
        "eps_mid": record["eps_mid"],
        "eps_cell": record["eps_cell"],
        "eps_cell_refined": record["eps_cell_refined"],
        "m": _strip(record["m"]),
        "auxiliary_evidence": auxiliary_evidence(record),
        "certificates": _strip(record["certificates"]),
        "provenance_chain": _strip(record["provenance_chain"]),
        "s0_charge_audit": record["s0_charge_audit"],
    }
    return hashlib.sha256(canonical(payload)).hexdigest()
