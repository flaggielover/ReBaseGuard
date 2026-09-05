"""REPAIR2 defect 1: a canonical PRODUCER implementation identity.

DEFECT (independently adjudicated, WORK_UNIVERSE = FAIL on Repair1)
-------------------------------------------------------------------
Repair1 stamps `universe.implementation_hash()` -- the REVIEWED implementation's
hash -- into every certificate it emits, for both `implementation_hash` and
`backend_hash`. That function hashes exactly thirteen files:

    p5y_k1_cover_ledger_implementation/code/{spec,intervals,opnorms,depgraph,
      universe,assembly,ledger,refine,propagate,scoped,cusum_layer1,
      cusum_layer2,qualify}.py

None of Repair1's own certificate-producing modules is among them. Repair1's
`repair_layer2.correct_residuals` is what actually decides the certified
`delta_mid`/`delta_cell` that end up in the record, yet changing it leaves the
stamped hash bit-identical. A certificate must bind to the code that produced
it; Repair1's does not.

REPAIR
------
`producer_manifest()` is a deterministic `repo-relative path -> sha256` map over
EVERY input that can change an emitted certified value:

  * Repair2 certifying modules
  * the Repair1 modules Repair2 actually executes
  * the reviewed-implementation modules actually executed
  * the frozen successor's algebra and config inputs
    (checkpoint.json, cells.json, cover_witnesses.json, record_schema.json,
     ERROR_ALGEBRA.md, code/algebra.py)
  * the certified backend contract actually imported
    (rebaseguard_certify arb/polynomial/residual/spectral_candidate,
     ra_certifier, raw_certifier, fast_range)
  * the fixed certificate-generation parameters, as a separate canonical block

`producer_hash()` is the sha256 of the canonical serialisation of that manifest.
It is NOT the Git commit hash: the frozen contract nowhere accepts a commit id
as complete implementation identity, and a commit covers unrelated files while
saying nothing about which bytes were actually executed.

Properties enforced by tests:
  * deterministic, canonically ordered, no timestamps, no worktree noise
  * changing ANY certifying file changes the producer hash
  * changing documentation/diagnostics does NOT change it (deliberately out of
    scope -- they cannot affect a certified value)
  * the reviewed parent hash alone is rejected as insufficient
  * `verify_loaded_modules_covered()` catches a certifying module that was
    executed but left out of the manifest
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import prior2

SCHEMA = "k1.repair2.producer-manifest.v1"

# --- Repair2's own certificate-producing modules -------------------------
REPAIR2_MODULES = (
    "prior2.py", "producer.py", "certhash.py", "provenance.py",
    "repair2_universe.py", "repair2_qualify.py",
)
# Reporting and self-audit are deliberately EXCLUDED: they cannot change a
# certified value, and including them would make the producer identity churn
# for reasons that are not scientific.
REPAIR2_NON_CERTIFYING = (
    "repair2_audit.py", "repair2_report.py",
)

# --- Repair1 modules Repair2 actually executes ---------------------------
REPAIR1_MODULES = (
    "prior.py", "repair_layer2.py", "repair_scoped.py", "repair_check.py",
    "repair_universe.py",
)

# --- reviewed-implementation modules actually executed -------------------
REVIEWED_MODULES = (
    "spec.py", "intervals.py", "opnorms.py", "depgraph.py", "universe.py",
    "assembly.py", "ledger.py", "refine.py", "propagate.py", "scoped.py",
    "cusum_layer1.py", "cusum_layer2.py", "qualify.py",
)

# --- frozen successor inputs --------------------------------------------
FROZEN_INPUTS = (
    "config/checkpoint.json", "config/cells.json", "config/cover_witnesses.json",
    "config/record_schema.json", "ERROR_ALGEBRA.md", "code/algebra.py",
)

# --- certified backend contract actually imported ------------------------
BACKEND_INPUTS = (
    prior2.PROOF_SRC / "rebaseguard_certify/__init__.py",
    prior2.PROOF_SRC / "rebaseguard_certify/arb_backend.py",
    prior2.PROOF_SRC / "rebaseguard_certify/polynomial.py",
    prior2.PROOF_SRC / "rebaseguard_certify/residual.py",
    prior2.PROOF_SRC / "rebaseguard_certify/spectral_candidate.py",
    prior2.P5X / "certified_method_repair_ra/ra_certifier.py",
    prior2.P5X / "compute_optimization_r2/fast_range.py",
    prior2.GATE1 / "raw_certifier.py",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(obj) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True) + "\n").encode("ascii")


def certifying_paths() -> list[Path]:
    """Every file whose bytes can change an emitted certified value."""
    out = [prior2.NS / "code" / n for n in REPAIR2_MODULES]
    out += [prior2.REPAIR1_NS / "code" / n for n in REPAIR1_MODULES]
    out += [prior2.IMPL_NS / "code" / n for n in REVIEWED_MODULES]
    out += [prior2.SPEC_NS / n for n in FROZEN_INPUTS]
    out += list(BACKEND_INPUTS)
    return out


def generation_parameters() -> dict:
    """Fixed certificate-generation parameters, read from the live modules.

    These already live inside hashed files; recording them explicitly makes the
    manifest self-describing, so a reader can answer "under what parameters?"
    without re-deriving them from source.
    """
    import flint
    import numpy
    import cusum_layer1 as L1
    import cusum_layer2 as L2
    import spec
    return {
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
        "precision_escalation_allowed": spec.PRECISION_ESCALATION_ALLOWED,
        "degree_adaptation_allowed": spec.DEGREE_ADAPTATION_ALLOWED,
    }


def producer_manifest() -> dict:
    """Deterministic `path -> sha256` over every certifying input."""
    files = {}
    for p in certifying_paths():
        if not p.exists():
            raise FileNotFoundError(f"certifying input missing: {p}")
        files[str(p.relative_to(prior2.ROOT))] = _sha256(p)
    return {
        "schema": SCHEMA,
        "files": dict(sorted(files.items())),
        "generation_parameters": generation_parameters(),
    }


def producer_hash(manifest: dict | None = None) -> str:
    return hashlib.sha256(canonical(manifest or producer_manifest())).hexdigest()


# ------------------------------------------------------------------ audits
def backend_hash() -> str:
    """Identity of the certified numeric backend contract actually imported.

    A separate line from the producer hash: the checkpoint and cell table are
    already stamped individually as `checkpoint_hash` and `cells_sha256`, so
    this covers the Arb/Bernstein/kernel machinery those certificates run on.
    Repair1 stamped the reviewed parent hash here too, which said nothing about
    the backend at all.
    """
    files = {str(p.relative_to(prior2.ROOT)): _sha256(p) for p in BACKEND_INPUTS}
    return hashlib.sha256(canonical(
        {"schema": "k1.repair2.backend-contract.v1",
         "files": dict(sorted(files.items()))})).hexdigest()


def parent_hash() -> str:
    """The hash Repair1 stamped: the reviewed parent's, which is insufficient."""
    import universe as reviewed
    return reviewed.implementation_hash()


def covers_repair1_producer_code() -> bool:
    """Does the manifest actually include Repair1's certificate-producing code?"""
    files = set(producer_manifest()["files"])
    return all(str((prior2.REPAIR1_NS / "code" / n).relative_to(prior2.ROOT))
               in files for n in REPAIR1_MODULES)


# Directory markers and module names that cannot affect a certified value.
NON_CERTIFYING_DIRS = ("/tests/", "/diagnostics/", "/manifests/",
                       "/benchmarks/", "/adjudication/", "/deploy/")
# The virtualenv happens to live inside the tree but is NOT repository source.
# Third-party libraries are bound by pinned VERSION in generation_parameters
# (the frozen checkpoint pins python-flint 0.9.0), not by hashing the venv.
THIRD_PARTY_DIRS = ("/.venv/", "/site-packages/")
NON_CERTIFYING_BASENAMES = (
    "repair_compare.py", "repair_components.py", "repair_report.py",
    "repair_audit.py", "repair2_audit.py", "repair2_report.py",
    "audit_impl.py", "bench.py", "report.py", "report_main.py",
    "build_spec.py", "seal.py", "audit.py", "representatives.py",
)


def verify_loaded_modules_covered(*, strict: bool = True) -> dict:
    """Every repo-local module actually imported must be in the manifest.

    Catches the Repair1 failure mode in general form: a module that really did
    participate in producing the certificate but was never hashed.
    """
    covered = set(producer_manifest()["files"])
    allow = {str((prior2.NS / "code" / n).relative_to(prior2.ROOT))
             for n in REPAIR2_NON_CERTIFYING}
    missing = []
    for name, mod in sorted(sys.modules.items()):
        f = getattr(mod, "__file__", None)
        if not f:
            continue
        try:
            rel = str(Path(f).resolve().relative_to(prior2.ROOT))
        except ValueError:
            continue                      # outside the repository
        if rel in covered or rel in allow:
            continue
        marked = "/" + rel
        if any(d in marked for d in THIRD_PARTY_DIRS):
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
            "loaded certifying modules absent from the producer manifest: "
            f"{missing}")
    return result


def describe() -> dict:
    m = producer_manifest()
    return {"schema": SCHEMA, "producer_hash": producer_hash(m),
            "reviewed_parent_hash": parent_hash(),
            "distinct_from_parent": producer_hash(m) != parent_hash(),
            "file_count": len(m["files"]),
            "covers_repair1_producer_code": covers_repair1_producer_code(),
            "manifest": m}
