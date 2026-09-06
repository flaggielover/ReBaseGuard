"""PHASE 7: canonical scientific certificate hash V2.

    same producer identity + same runtime contract + same exact scientific input
      + same precision   =>   byte-identical canonical scientific hash

Built by EXCLUSION, not inclusion. The record is walked in full; every leaf whose
path classifies as INCIDENTAL_RUNTIME is dropped; everything else is hashed. A
field nobody thought about is therefore bound automatically -- which is precisely
what Aux3's include list got wrong with `candidate_suprema`, `order` and
`hermite_weight`.

Two hashes are published:

    scientific_content_hash   the whole record minus incidental runtime noise
    auxiliary_evidence_hash   the nested third-derivative evidence alone, so the
                              parent certificate can be checked down to it

Both are canonical JSON: sorted keys, compact separators, ASCII, trailing
newline. Rational values travel as exact strings; no float ever enters either
hash, which is why the float `utilization` and `factor` views are classified
incidental -- their exact rational sources are hashed instead.
"""
from __future__ import annotations

import hashlib
import json

import ancestry4                                            # noqa: F401

import schema

SCHEMA = "k1.cusum-aux4.cell-record.v2"
AUX_SCHEMA = "k1.cusum-aux4.auxiliary-evidence.v2"


def canonical(obj) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True) + "\n").encode("ascii")


def _prune(node, prefix: str = ""):
    """Drop exactly the leaves classified INCIDENTAL_RUNTIME."""
    if isinstance(node, dict):
        out = {}
        for key, value in sorted(node.items()):
            path = f"{prefix}.{key}" if prefix else str(key)
            pruned = _prune(value, path)
            if pruned is not _DROP:
                out[key] = pruned
        return out
    if isinstance(node, list):
        out = []
        for i, value in enumerate(node):
            pruned = _prune(value, f"{prefix}.{i}")
            if pruned is not _DROP:
                out.append(pruned)
        return out
    return _DROP if schema.classify(prefix) == schema.INCIDENTAL else node


class _Drop:
    def __repr__(self):
        return "<incidental>"


_DROP = _Drop()


def scientific_content(record: dict) -> dict:
    """The record with incidental runtime noise removed, ready to hash."""
    body = _prune({k: v for k, v in record.items()
                   if k not in ("scientific_content_hash",)})
    return {"schema": SCHEMA, "record": body}


def record_scientific_hash(record: dict) -> str:
    return hashlib.sha256(canonical(scientific_content(record))).hexdigest()


def auxiliary_evidence_content(record: dict) -> dict:
    aux = record.get("auxiliary_evidence", {})
    return {"schema": AUX_SCHEMA,
            "evidence": _prune(aux, "auxiliary_evidence"),
            "node_refinement": _prune(record.get("node_refinement"),
                                      "node_refinement")}


def auxiliary_evidence_hash(record: dict) -> str:
    return hashlib.sha256(canonical(auxiliary_evidence_content(record))).hexdigest()


def certificate_hash(certificate: dict) -> str:
    """One unit certificate, pruned by the same rule."""
    return hashlib.sha256(canonical(_prune(certificate))).hexdigest()


def audit_record(record: dict) -> dict:
    """Which fields the hash actually consumed, and which it dropped."""
    consumed = set()
    for path, _ in schema.walk(scientific_content(record)["record"]):
        consumed.add(path)
    classified = schema.classify_record(record)
    dropped = sorted(p for p, c in classified["paths"].items()
                     if c == schema.INCIDENTAL)
    all_paths = set(classified["paths"])
    unaccounted = sorted(p for p in all_paths
                         if p not in consumed and p not in dropped
                         and p != "scientific_content_hash")
    return {"leaf_paths": len(all_paths),
            "hashed": len(consumed),
            "dropped_incidental": len(dropped),
            "dropped_paths": dropped,
            "unaccounted": unaccounted,
            "counts": classified["counts"],
            "ok": not unaccounted}
