"""PHASE 2: a NEW canonical producer identity for this successor.

THE DEFECT BEING REPAIRED (independently adjudicated: PROVENANCE = FAIL)
------------------------------------------------------------------------
`p5y_k1_final_completion/code/final_qualify.py` built its certificates with
`RU2.context()` -- the REPAIR2 producer hash -- and stamped that into every
certificate identity, while its own record admitted:

    "this record is produced by the final-completion certifier, whose modules
     are NOT in the Repair2 producer manifest; the stamped hash is Repair2's
     and is recorded for lineage only, not as this record's producer identity"

So certificates whose certified values were decided by `sharp_norms.py` (which
changed M_R2 by up to 37x) carry an identity that is blind to `sharp_norms.py`,
`sharp_certifier.py`, `base.py` and `final_qualify.py`. A record that names a
producer which did not produce it is not provenance; writing the disclaimer into
the artifact does not repair it.

THE REPAIR
----------
`producer_manifest()` here is a deterministic `repo-relative path -> sha256` map
over EVERY module actually executed on the certifying path, at every ancestry
level, plus the frozen inputs, the backend contract, pinned third-party numerical
versions and the fixed generation parameters. `producer_hash()` is the canonical
hash of that manifest. It is NOT Repair2's hash, NOT the final-completion
lineage-only hash, and NOT a commit id.

Coverage is enforced, not asserted: `verify_loaded_modules_covered()` walks
`sys.modules` and fails on any repository module that was imported on the
certifying path but is absent from the manifest. Phase 10 runs it in an isolated
process so cross-suite `sys.modules` contamination cannot mask or fake it.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import ancestry

SCHEMA = "k1.cusum-successor.producer-manifest.v1"
IDENTITY_KIND = "cusum_successor_producer_manifest_v1"

# --- this successor's certificate-producing modules -----------------------
SUCCESSOR_MODULES = (
    "ancestry.py", "order2.py", "refine2.py", "successor_producer.py",
    "successor_certhash.py", "successor_universe.py", "successor_qualify.py",
)
# Reporting, decomposition and self-audit cannot change a certified value.
SUCCESSOR_NON_CERTIFYING = (
    "decompose.py", "successor_audit.py", "successor_report.py",
    "far_field_inherited.py",
)

# --- final-completion modules actually executed --------------------------
FINAL_MODULES = ("base.py", "sharp_norms.py", "sharp_certifier.py")

# --- Repair2 modules actually executed -----------------------------------
REPAIR2_MODULES = ("prior2.py", "producer.py", "certhash.py", "provenance.py",
                   "repair2_universe.py")

# --- Repair1 modules actually executed -----------------------------------
REPAIR1_MODULES = ("prior.py", "repair_layer2.py", "repair_scoped.py",
                   "repair_check.py", "repair_universe.py")

# --- reviewed-implementation modules actually executed -------------------
REVIEWED_MODULES = ("spec.py", "intervals.py", "opnorms.py", "depgraph.py",
                    "universe.py", "assembly.py", "ledger.py", "refine.py",
                    "propagate.py", "scoped.py", "cusum_layer1.py",
                    "cusum_layer2.py", "qualify.py")

# --- frozen successor inputs ---------------------------------------------
FROZEN_INPUTS = ("config/checkpoint.json", "config/cells.json",
                 "config/cover_witnesses.json", "config/record_schema.json",
                 "ERROR_ALGEBRA.md", "code/algebra.py")

# --- certified backend contract actually imported ------------------------
BACKEND_INPUTS = (
    ancestry.PROOF_SRC / "rebaseguard_certify/__init__.py",
    ancestry.PROOF_SRC / "rebaseguard_certify/arb_backend.py",
    ancestry.PROOF_SRC / "rebaseguard_certify/polynomial.py",
    ancestry.PROOF_SRC / "rebaseguard_certify/residual.py",
    ancestry.PROOF_SRC / "rebaseguard_certify/spectral_candidate.py",
    ancestry.P5X / "certified_method_repair_ra/ra_certifier.py",
    ancestry.P5X / "compute_optimization_r2/fast_range.py",
    ancestry.GATE1 / "raw_certifier.py",
)


def canonical(obj) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True) + "\n").encode("ascii")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def certifying_paths() -> list[Path]:
    out = [ancestry.NS / "code" / n for n in SUCCESSOR_MODULES]
    out += [ancestry.FINAL_NS / "code" / n for n in FINAL_MODULES]
    out += [ancestry.REPAIR2_NS / "code" / n for n in REPAIR2_MODULES]
    out += [ancestry.REPAIR1_NS / "code" / n for n in REPAIR1_MODULES]
    out += [ancestry.IMPL_NS / "code" / n for n in REVIEWED_MODULES]
    out += [ancestry.SPEC_NS / n for n in FROZEN_INPUTS]
    out += list(BACKEND_INPUTS)
    return out


def generation_parameters() -> dict:
    """Fixed parameters and pinned numerical versions that bind the arithmetic."""
    import flint
    import numpy
    import cusum_layer1 as L1
    import cusum_layer2 as L2
    import spec
    params = {
        "python_flint_version": flint.__version__,
        "numpy_version": numpy.__version__,
        "taylor_order": L2.TAYLOR_N,
        "subdivision_depth": L2.SUBDIVISION_DEPTH,
        "chebyshev_degree": L1.DEGREE,
        "quadrature_order": L1.QUADRATURE,
        "scale_bits": L1.SCALE_BITS,
        "state_half_width_h": L1.H_FROZEN,
        "threshold_k": L1.K_FROZEN,
        "w_indices": [list(x) for x in L1.W_INDICES],
        "production_bits": spec.PRODUCTION_BITS,
        "m_values": list(spec.M_VALUES),
        "obligation_universe_total": spec.TOTAL_UNITS,
        "cells_sha256": spec.CELLS_SHA256,
        "precision_escalation_allowed": spec.PRECISION_ESCALATION_ALLOWED,
        "degree_adaptation_allowed": spec.DEGREE_ADAPTATION_ALLOWED,
        # Determinism contract: the float candidate solve must be single
        # threaded, or BLAS reduction order can change the candidate and hence
        # the certified residual. Bound into the producer identity so a record
        # produced under a different threading contract is a different producer.
        "blas_threads": 1,
        "flint_threads": 1,
    }
    try:
        import scipy
        params["scipy_version"] = scipy.__version__
    except ModuleNotFoundError:                     # pragma: no cover
        params["scipy_version"] = None
    return params


def producer_manifest() -> dict:
    files = {}
    for p in certifying_paths():
        if not p.exists():
            raise FileNotFoundError(f"certifying input missing: {p}")
        files[str(p.relative_to(ancestry.ROOT))] = _sha256(p)
    return {"schema": SCHEMA, "identity_kind": IDENTITY_KIND,
            "files": dict(sorted(files.items())),
            "generation_parameters": generation_parameters()}


def producer_hash(manifest: dict | None = None) -> str:
    return hashlib.sha256(canonical(manifest or producer_manifest())).hexdigest()


# --------------------------------------------------------- rejected lineages
def repair2_hash() -> str:
    import producer as repair2_producer
    return repair2_producer.producer_hash()


def reviewed_parent_hash() -> str:
    import universe as reviewed
    return reviewed.implementation_hash()


def rejected_producer_hashes() -> dict:
    """Identities a successor record must never carry."""
    return {"repair2_producer": repair2_hash(),
            "final_completion_lineage_only": repair2_hash(),
            "reviewed_parent": reviewed_parent_hash()}


def backend_hash() -> str:
    files = {str(p.relative_to(ancestry.ROOT)): _sha256(p) for p in BACKEND_INPUTS}
    return hashlib.sha256(canonical(
        {"schema": "k1.cusum-successor.backend-contract.v1",
         "files": dict(sorted(files.items()))})).hexdigest()


# --------------------------------------------------------- coverage audit
THIRD_PARTY_DIRS = ("/.venv/", "/site-packages/")
NON_CERTIFYING_DIRS = ("/tests/", "/diagnostics/", "/manifests/",
                       "/benchmarks/", "/adjudication/", "/deploy/")
NON_CERTIFYING_BASENAMES = set(SUCCESSOR_NON_CERTIFYING) | {
    "repair_compare.py", "repair_components.py", "repair_report.py",
    "repair_audit.py", "repair2_audit.py", "repair2_report.py",
    "final_audit.py", "final_qualify.py", "far_field.py", "sr_cost.py",
    "sr_status.py", "audit_impl.py", "bench.py", "report.py",
    "report_main.py", "build_spec.py", "seal.py", "audit.py",
    "representatives.py",
}


def verify_loaded_modules_covered(*, strict: bool = True) -> dict:
    covered = set(producer_manifest()["files"])
    missing = []
    for name, mod in sorted(sys.modules.items()):
        f = getattr(mod, "__file__", None)
        if not f:
            continue
        try:
            rel = str(Path(f).resolve().relative_to(ancestry.ROOT))
        except ValueError:
            continue
        marked = "/" + rel
        if any(d in marked for d in THIRD_PARTY_DIRS):
            continue
        if rel in covered:
            continue
        if any(d in marked for d in NON_CERTIFYING_DIRS):
            continue
        base = Path(rel).name
        if base.startswith("test_") or base in NON_CERTIFYING_BASENAMES:
            continue
        missing.append(rel)
    result = {"covered": len(covered), "uncovered_loaded_modules": missing,
              "ok": not missing}
    if strict and missing:
        raise RuntimeError(
            f"loaded certifying modules absent from the manifest: {missing}")
    return result


def describe() -> dict:
    m = producer_manifest()
    h = producer_hash(m)
    rejected = rejected_producer_hashes()
    return {"schema": SCHEMA, "identity_kind": IDENTITY_KIND,
            "producer_hash": h, "backend_hash": backend_hash(),
            "file_count": len(m["files"]),
            "rejected_lineages": rejected,
            "distinct_from_all_rejected": all(h != v for v in rejected.values()),
            "covers_final_completion_certifiers": all(
                str((ancestry.FINAL_NS / "code" / n).relative_to(ancestry.ROOT))
                in m["files"] for n in FINAL_MODULES),
            "manifest": m}
