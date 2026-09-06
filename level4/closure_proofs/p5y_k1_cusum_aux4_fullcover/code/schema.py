"""PHASE 7: field classification for the canonical scientific hash V2.

WHAT WENT WRONG IN AUX3
-----------------------
Aux3 hashed a hand-picked INCLUDE list. Anything the author did not think to
name simply fell out of the certificate, silently. Three scientifically
meaningful fields were lost that way, and mutating them left the hash unchanged:

    auxiliary_evidence.candidate_suprema   the certified sup|Xhat^(3)| values
                                           that the node bound multiplies by rho
    auxiliary_evidence.order               which derivative order the evidence is
    auxiliary_evidence.hermite_weight      which Hermite weight built the order-3
                                           collocation operator

An include list fails open: forgetting a field silently drops it. This module
inverts the rule. Classification walks the record and assigns every leaf path to
one of three classes:

    SCIENTIFIC_IDENTITY   must influence the scientific hash
    PROVENANCE_IDENTITY   must influence the producer/provenance hash
    INCIDENTAL_RUNTIME    may be excluded -- and ONLY these may be

`INCIDENTAL_PATHS` is the whitelist. A field matching nothing is SCIENTIFIC by
default, so a new field added later is bound automatically and a mistake fails
CLOSED. `classify_record()` reports every path with its class, and the test suite
asserts that the union of what the hash consumes and what is whitelisted covers
the record exactly, with nothing unaccounted for.
"""
from __future__ import annotations

import fnmatch

SCIENTIFIC = "SCIENTIFIC_IDENTITY"
PROVENANCE = "PROVENANCE_IDENTITY"
INCIDENTAL = "INCIDENTAL_RUNTIME"

# Timings, memory and counters: they differ between honest repeat runs of the
# same science. Patterns are matched against the dotted record path, with `*`
# standing for one path segment and `**` for any depth.
INCIDENTAL_PATHS = (
    "cpu_seconds*",
    "wall_seconds",
    "peak_rss_kib",
    "generated_utc",
    "pid",
    "host*",
    "**.cpu_seconds",
    "**.bernstein_calls",
    "**.kernel_calls",
    "work.bernstein_calls",
    "work.kernel_calls",
    "objects.*.cpu_seconds",
    "objects.*.bernstein_calls",
    "objects.*.kernel_calls",
    "auxiliary_evidence.objects.*.cpu_seconds",
    "auxiliary_evidence.objects.*.bernstein_calls",
    "auxiliary_evidence.objects.*.kernel_calls",
    "tightening_report.*.factor",          # float ratio of two bound rationals
    "node_refinement.decisions.*.factor",  # ditto
    "node_refinement.best_factor",
    "node_refinement.median_factor",
    "whole_cell_refinement.*.tightening_factor_H",
    "whole_cell_refinement.*.second_order.factor_H",
    "m.*.cover.utilization",               # float view of an exact rational
    "m.*.top_level_gates.*.utilization",
    "m.*.worst_top_level_utilization",
    "scipy_guard.call_sites_observed",     # a count, varies with warm-up
    "run.**",                              # bookkeeping for resumability
)

# Producer/runtime identity: bound by the producer identity hash. These are also
# hashed into the scientific record, because a certificate that does not say what
# produced it is not a certificate -- but they are reported separately so the two
# identities can be audited independently.
PROVENANCE_PATHS = (
    "producer.**",
    "producer_manifest_*",
    "runtime_contract_hash",
    "producer_identity_hash",
    "auxiliary_evidence_hash",
    "certificates.*.identity.**",
    "provenance_chain.**",
    "campaign",
    "changes*",
    "threading.**",
    "universe.**",
    "scipy_guard.**",
)


def _match(path: str, patterns) -> bool:
    for pattern in patterns:
        if "**" in pattern:
            regex = pattern.replace(".", r"\.").replace("**", ".*").replace("*", "[^.]*")
            import re
            if re.fullmatch(regex, path):
                return True
        elif fnmatch.fnmatchcase(path, pattern):
            return True
    return False


def classify(path: str) -> str:
    """Classify one dotted record path. Unknown fields are SCIENTIFIC."""
    if _match(path, INCIDENTAL_PATHS):
        return INCIDENTAL
    if _match(path, PROVENANCE_PATHS):
        return PROVENANCE
    return SCIENTIFIC


def walk(node, prefix: str = ""):
    """Yield (path, value) for every leaf of the record."""
    if isinstance(node, dict):
        for key, value in sorted(node.items()):
            yield from walk(value, f"{prefix}.{key}" if prefix else str(key))
    elif isinstance(node, list):
        for i, value in enumerate(node):
            yield from walk(value, f"{prefix}.{i}")
    else:
        yield prefix, node


def classify_record(record: dict) -> dict:
    """Every leaf path of a record with its class, and the class totals."""
    out = {}
    for path, _ in walk(record):
        out[path] = classify(path)
    counts = {SCIENTIFIC: 0, PROVENANCE: 0, INCIDENTAL: 0}
    for cls in out.values():
        counts[cls] += 1
    return {"paths": out, "counts": counts,
            "incidental_patterns": list(INCIDENTAL_PATHS),
            "provenance_patterns": list(PROVENANCE_PATHS),
            "default_class_for_unknown_fields": SCIENTIFIC}


def scientific_paths(record: dict) -> list[str]:
    return sorted(p for p, c in classify_record(record)["paths"].items()
                  if c in (SCIENTIFIC, PROVENANCE))


def incidental_paths(record: dict) -> list[str]:
    return sorted(p for p, c in classify_record(record)["paths"].items()
                  if c == INCIDENTAL)
