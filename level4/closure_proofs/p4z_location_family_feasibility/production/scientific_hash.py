"""Schema-driven, fail-closed scientific hashing and the producer manifest.

Two rules, both learned the hard way on the P5Y/CUSUM line.

**Exclusion based, not inclusion based.**  The hash covers every field of a
result document except an explicit, enumerated non-scientific allowlist
(timings, host counters, free text).  A field nobody thought about is therefore
*hashed*, not silently dropped.  A field that is neither known-scientific nor
explicitly excluded raises: unknown scientific fields fail closed.

**Path based TCB, resolved after import.**  The manifest lists exact repository
paths with their git blob hashes.  The final producer gate runs *after* every
scientific module is imported and compares each module's resolved ``__file__``
against the manifest, so a module that was imported lazily from somewhere else
cannot slip past a gate that ran at start-up.  There are no basename
exemptions: a path either is in the manifest or the run aborts.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

NS = Path(__file__).resolve().parent.parent
REPO = NS.parent.parent.parent
REL = "level4/closure_proofs"

#: Every file that can reach a scientific number.  Order is irrelevant; the
#: manifest is sorted before hashing.
TCB_PATHS = (
    # P4Z estimators and analytic contract
    f"{REL}/p4z_location_family_feasibility/src/rebaseguard_p4z/__init__.py",
    f"{REL}/p4z_location_family_feasibility/src/rebaseguard_p4z/analytic.py",
    f"{REL}/p4z_location_family_feasibility/src/rebaseguard_p4z/rbscore.py",
    f"{REL}/p4z_location_family_feasibility/src/rebaseguard_p4z/rbmap.py",
    # P4Z production driver and its dependencies
    f"{REL}/p4z_location_family_feasibility/production/run_p4z.py",
    f"{REL}/p4z_location_family_feasibility/production/scientific_hash.py",
    f"{REL}/p4z_location_family_feasibility/production/runtime_contract.py",
    # inherited frozen P4 implementation, read-only
    f"{REL}/p4_theory_generalization/src/rebaseguard_p4_general/__init__.py",
    f"{REL}/p4_theory_generalization/src/rebaseguard_p4_general/detectors.py",
    f"{REL}/p4_theory_generalization/src/rebaseguard_p4_general/families.py",
    f"{REL}/p4_theory_generalization/src/rebaseguard_p4_general/simulate.py",
    # frozen configuration
    f"{REL}/p4_theory_generalization/configs/P4_PROTOCOL.json",
    f"{REL}/p4z_location_family_feasibility/configs/estimand_contract.json",
    f"{REL}/p4z_location_family_feasibility/configs/checkpoint_p4z.json",
    f"{REL}/p4z_location_family_feasibility/production/stage0_freeze.json",
    f"{REL}/p4z_location_family_feasibility/production/campaign_plan.json",
    f"{REL}/p4z_location_family_feasibility/production/mac_runtime_contract.json",
)

#: Deliberately NOT in the TCB: ``adjudicate.py``, ``build_plan.py``,
#: ``independent_adjudication.py``, ``replay_check.py``, ``build_closure.py``.
#: None of them produces a block.  ``build_plan.py`` emits
#: ``campaign_plan.json``, which IS in the TCB by content, so the plan a run
#: consumed is bound exactly; binding the generator as well would mean that
#: correcting a downstream *reader* invalidates already-produced block data,
#: which is over-binding rather than safety.

#: Modules whose resolved __file__ must be inside the manifest at the final gate.
SCIENTIFIC_MODULES = (
    "rebaseguard_p4z.analytic",
    "rebaseguard_p4z.rbscore",
    "rebaseguard_p4z.rbmap",
    "rebaseguard_p4_general.detectors",
    "rebaseguard_p4_general.families",
    "rebaseguard_p4_general.simulate",
)

#: The ONLY fields excluded from the scientific hash.  Everything else is
#: hashed, including fields added later by someone who forgets this list exists.
NON_SCIENTIFIC_FIELDS = frozenset({
    "cpu_seconds", "wall_seconds", "peak_rss_mb", "started_utc", "finished_utc",
    "elapsed_seconds", "host_load", "note", "schema_note", "progress",
    "scientific_hash", "producer_hash",
})


class ProducerGateError(RuntimeError):
    """Fail-closed producer failure.  Never caught inside the driver."""


def _git(*args: str) -> str:
    out = subprocess.run(("git", "-C", str(REPO)) + args,
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise ProducerGateError(f"git {' '.join(args)} failed: {out.stderr.strip()}")
    return out.stdout.strip()


def refuse_dirty_scientific_state() -> str:
    """No result-bearing run from a modified TCB.  Returns HEAD."""
    dirty = _git("status", "--porcelain", "--", *TCB_PATHS)
    if dirty:
        raise ProducerGateError(
            "refusing to run: scientific source state is dirty:\n" + dirty)
    return _git("rev-parse", "HEAD")


def build_manifest() -> dict[str, object]:
    """Immutable producer manifest: exact paths, git blob hashes, content hashes.

    ``head`` is recorded as provenance metadata but is deliberately **excluded**
    from ``producer_hash``.  The producer's identity is the *content* of the
    trusted files, not the commit that happens to be checked out; binding HEAD
    would make an unrelated documentation commit invalidate every block already
    produced under identical scientific code.
    """
    head = _git("rev-parse", "HEAD")
    entries = {}
    for rel in sorted(TCB_PATHS):
        path = REPO / rel
        if not path.exists():
            raise ProducerGateError(f"TCB path missing: {rel}")
        blob = _git("rev-parse", f"HEAD:{rel}")
        entries[rel] = {
            "git_blob": blob,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    manifest = {
        "schema": "rebaseguard.p4z-producer-manifest.v1",
        "entries": entries,
    }
    manifest["producer_hash"] = hashlib.sha256(
        json.dumps({k: v for k, v in manifest.items() if k != "producer_hash"},
                   indent=2, sort_keys=True).encode()).hexdigest()
    manifest["head_informational"] = head
    return manifest


def verify_manifest(manifest: dict[str, object]) -> None:
    """Re-read every TCB file and compare.  No stale producer admission."""
    body = {k: v for k, v in manifest.items()
            if k not in ("producer_hash", "head_informational")}
    recomputed = hashlib.sha256(
        json.dumps(body, indent=2, sort_keys=True).encode()).hexdigest()
    if recomputed != manifest["producer_hash"]:
        raise ProducerGateError("producer manifest's own hash does not match")
    for rel, entry in manifest["entries"].items():
        path = REPO / rel
        if not path.exists():
            raise ProducerGateError(f"TCB path vanished mid-run: {rel}")
        got = hashlib.sha256(path.read_bytes()).hexdigest()
        if got != entry["sha256"]:
            raise ProducerGateError(f"TCB file changed mid-run: {rel}")


def final_producer_gate(manifest: dict[str, object]) -> None:
    """Run AFTER every scientific module is imported.

    Closes the lazy-import loophole: a module resolved from outside the manifest
    aborts the run even if it was imported long after start-up.
    """
    allowed = {str((REPO / rel).resolve()) for rel in manifest["entries"]}
    for name in SCIENTIFIC_MODULES:
        module = sys.modules.get(name)
        if module is None:
            raise ProducerGateError(
                f"final gate: scientific module {name!r} was never imported; "
                "the gate must run after all scientific modules are loaded")
        resolved = getattr(module, "__file__", None)
        if resolved is None:
            raise ProducerGateError(f"final gate: {name!r} has no __file__")
        if str(Path(resolved).resolve()) not in allowed:
            raise ProducerGateError(
                f"final gate: {name!r} resolved to {resolved}, which is not in "
                "the producer manifest (no basename exemption exists)")
    verify_manifest(manifest)


def _strip(node, path=""):
    """Recursively drop non-scientific fields; raise on anything unhashable."""
    if isinstance(node, dict):
        out = {}
        for key, value in node.items():
            if key in NON_SCIENTIFIC_FIELDS:
                continue
            out[key] = _strip(value, f"{path}.{key}")
        return out
    if isinstance(node, (list, tuple)):
        return [_strip(v, f"{path}[{i}]") for i, v in enumerate(node)]
    if isinstance(node, (str, int, float, bool)) or node is None:
        return node
    raise ProducerGateError(
        f"unknown scientific field type at {path}: {type(node).__name__}; "
        "the scientific hash fails closed on anything it cannot canonicalise")


def scientific_hash(document: dict[str, object]) -> str:
    """Exclusion-based hash over every scientific field of a result document."""
    stripped = _strip(document)
    return hashlib.sha256(
        json.dumps(stripped, indent=2, sort_keys=True,
                   ensure_ascii=True, allow_nan=False).encode()).hexdigest()
