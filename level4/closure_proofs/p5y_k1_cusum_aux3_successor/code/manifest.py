"""PHASE 3-5: the immutable, COMMITTED producer manifest.

WHAT WAS WRONG BEFORE
---------------------
The predecessor computed its producer hash on the fly from the working tree. A
record therefore carried a 64-hex number that a verifier could not resolve: to
recheck it you needed the exact tree that produced it, which is precisely what
the hash was supposed to establish. Adjudication called this
REPOSITORY_PROVENANCE = FAIL / PRODUCER_BINDING = FAIL, and it is why the
predecessor's own tests kept passing while its committed records went stale.

WHAT THIS DOES INSTEAD
----------------------
The manifest is a COMMITTED ARTIFACT: `manifests/producer_manifest_v1.json`,
holding canonical `path -> sha256` for every certifying input actually executed,
plus the runtime contract. A record carries

    producer_manifest_hash = sha256(canonical(manifest))
    producer_manifest_schema = "k1.cusum-aux3.producer-manifest.v1"
    producer_manifest_path   = the committed artifact's repo-relative path

so a verifier with the repository alone can: read the committed artifact,
recompute every file hash from disk, recompute the manifest hash, and compare it
against the record. Every step is reproducible without trusting this code.

FAIL-CLOSED
-----------
`verify(...)` returns the discrepancies; `require(...)` raises. The certifying
runner calls `require(...)` BEFORE it emits anything, so a certificate cannot be
produced when a certifying byte, a bound library version, or the artifact itself
has moved. That is the `strict=True` semantics the adjudication asked for, and it
runs inside the certifying process, not in a later audit.

WHAT IS IN SCOPE
----------------
Certifying = can change a certified number. That is: this namespace's certifying
modules, every inherited module that actually executes on the CUSUM path, the
frozen successor's inputs, and the certified backend sources. Reporting, audit,
diagnostics, tests and documentation are OUT of scope and are listed explicitly
so their exclusion is auditable rather than accidental.

RUNTIME BINDING, HONESTLY
-------------------------
Bound: `python-flint` (all ball arithmetic), `numpy` (the float candidate solve
and the collocation quadrature), the CPython major.minor policy, the BLAS/OpenMP
thread contract, and the frozen precision. SciPy is NOT bound: `scipy_status`
below records whether it was imported at all on the certifying path, measured by
`evidence/scipy_execution_probe.json`, and the manifest binds it only if it is
actually executed. Binding a library that never runs would be theatre; leaving
out one that does would be a hole.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

import ancestry

SCHEMA = "k1.cusum-aux3.producer-manifest.v1"
ARTIFACT = ancestry.NS / "manifests" / "producer_manifest_v1.json"

# --- this namespace's certifying modules ---------------------------------
AUX3_MODULES = (
    "ancestry.py", "aux_collocation.py", "aux_certifier.py", "aux_refine.py",
    "aux_propagate.py", "manifest.py", "aux_universe.py", "aux_certhash.py",
    "aux_qualify.py",
)
# Reporting, audit, diagnostics and detectors cannot change a certified value.
AUX3_NON_CERTIFYING = (
    "aux_audit.py", "aux_report.py", "no_monkeypatch.py", "far_field_inherited.py",
)

# --- inherited modules that actually execute ------------------------------
CUSUM_MODULES = ("order2.py", "refine2.py")
FINAL_MODULES = ("base.py", "sharp_norms.py", "sharp_certifier.py")
REPAIR2_MODULES = ("prior2.py", "producer.py", "certhash.py", "provenance.py",
                   "repair2_universe.py")
REPAIR1_MODULES = ("prior.py", "repair_layer2.py", "repair_scoped.py",
                   "repair_check.py", "repair_universe.py")
REVIEWED_MODULES = ("spec.py", "intervals.py", "opnorms.py", "depgraph.py",
                    "universe.py", "assembly.py", "ledger.py", "refine.py",
                    "propagate.py", "scoped.py", "cusum_layer1.py",
                    "cusum_layer2.py", "qualify.py")

# --- frozen successor inputs ---------------------------------------------
FROZEN_INPUTS = ("config/checkpoint.json", "config/cells.json",
                 "config/cover_witnesses.json", "config/record_schema.json",
                 "ERROR_ALGEBRA.md", "code/algebra.py")

# --- certified backend sources -------------------------------------------
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

THIRD_PARTY_DIRS = ("/.venv/", "/site-packages/")
NON_CERTIFYING_DIRS = ("/tests/", "/diagnostics/", "/manifests/", "/evidence/",
                       "/benchmarks/", "/adjudication/", "/deploy/")
NON_CERTIFYING_BASENAMES = set(AUX3_NON_CERTIFYING) | {
    "decompose.py", "successor_audit.py", "successor_report.py",
    "successor_producer.py", "successor_certhash.py", "successor_universe.py",
    "successor_qualify.py", "determinism.py", "far_field_inherited.py",
    "repair_compare.py", "repair_components.py", "repair_report.py",
    "repair_audit.py", "repair2_audit.py", "repair2_report.py",
    "final_audit.py", "final_qualify.py", "far_field.py", "sr_cost.py",
    "sr_status.py", "audit_impl.py", "bench.py", "report.py",
    "report_main.py", "build_spec.py", "seal.py", "audit.py",
    "representatives.py",
}


class ManifestFailure(RuntimeError):
    """The committed manifest does not describe this repository state."""


def canonical(obj) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True) + "\n").encode("ascii")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def certifying_paths() -> list[Path]:
    out = [ancestry.NS / "code" / n for n in AUX3_MODULES]
    out += [ancestry.CUSUM_NS / "code" / n for n in CUSUM_MODULES]
    out += [ancestry.FINAL_NS / "code" / n for n in FINAL_MODULES]
    out += [ancestry.REPAIR2_NS / "code" / n for n in REPAIR2_MODULES]
    out += [ancestry.REPAIR1_NS / "code" / n for n in REPAIR1_MODULES]
    out += [ancestry.IMPL_NS / "code" / n for n in REVIEWED_MODULES]
    out += [ancestry.SPEC_NS / n for n in FROZEN_INPUTS]
    out += list(BACKEND_INPUTS)
    return out


def _version(module_name: str) -> str | None:
    try:
        mod = __import__(module_name)
    except ImportError:
        return None
    return getattr(mod, "__version__", None)


def scipy_execution_evidence() -> dict:
    """Is SciPy on the certifying path at all? Measured, not assumed."""
    path = ancestry.NS / "evidence" / "scipy_execution_probe.json"
    if not path.exists():
        return {"measured": False,
                "note": "no probe recorded; scipy treated as UNRESOLVED"}
    return json.loads(path.read_text())


def runtime_contract() -> dict:
    """The numerical runtime this producer is bound to."""
    import flint
    import spec
    scipy = scipy_execution_evidence()
    imported = bool(scipy.get("imported_on_certifying_path"))
    executed = bool(scipy.get("called_on_certifying_path"))
    contract = {
        "python_major_minor": f"{sys.version_info.major}.{sys.version_info.minor}",
        "python_flint_version": _version("flint"),
        "numpy_version": _version("numpy"),
        "flint_threads": 1,
        "blas_threads": "1",
        "thread_environment": sorted(
            ["OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
             "NUMEXPR_NUM_THREADS"]),
        "precision_bits": spec.PRODUCTION_BITS,
        "taylor_order": 120,
        "collocation_degree": 12,
        "collocation_quadrature": 400,
        "subdivision_depth": 0,
        # Measured, not assumed: scipy is IMPORTED by a certifying backend file
        # (`spectral_candidate.py`: `from scipy.special import ndtr`) but no
        # scipy function is CALLED on the CUSUM path -- the only call sites are
        # inside `solve_spectral_candidates`, which this path never reaches,
        # because candidates come from `cusum_layer1.dyadic_candidate`. So the
        # import must succeed, and the version cannot change a certified number.
        # Availability is bound; the version deliberately is not.
        "scipy_status": ("BOUND_EXECUTED" if executed else
                         "AVAILABILITY_ONLY_IMPORTED_NOT_CALLED" if imported
                         else "EXCLUDED_NOT_IMPORTED" if scipy.get("measured")
                         else "UNRESOLVED"),
        "scipy_import_required": imported,
        "scipy_version": _version("scipy") if executed else None,
        "scipy_evidence": scipy.get("evidence_path"),
    }
    del flint
    return contract


def build() -> dict:
    """The manifest for the CURRENT working tree."""
    files = {}
    for p in certifying_paths():
        rel = str(Path(p).resolve().relative_to(ancestry.ROOT))
        if not Path(p).exists():
            raise ManifestFailure(f"certifying input missing: {rel}")
        files[rel] = sha256_file(p)
    return {"schema": SCHEMA,
            "manifest_version": 1,
            "kind": "cusum_aux3_producer_manifest_v1",
            "files": dict(sorted(files.items())),
            "runtime": runtime_contract(),
            "excluded_non_certifying": {
                "namespace_modules": sorted(AUX3_NON_CERTIFYING),
                "directories": sorted(NON_CERTIFYING_DIRS),
                "rationale": "reporting, auditing, tests, diagnostics and "
                             "committed artifacts cannot change a certified "
                             "value; they are excluded explicitly so the "
                             "exclusion is auditable",
            }}


def manifest_hash(manifest: dict | None = None) -> str:
    return hashlib.sha256(canonical(manifest if manifest is not None
                                    else load())).hexdigest()


def load() -> dict:
    if not ARTIFACT.exists():
        raise ManifestFailure(
            f"committed producer manifest is missing: "
            f"{ARTIFACT.relative_to(ancestry.ROOT)}")
    return json.loads(ARTIFACT.read_text())


def write() -> str:
    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    m = build()
    ARTIFACT.write_text(json.dumps(m, indent=2, sort_keys=True) + "\n")
    return manifest_hash(m)


def verify() -> dict:
    """Recompute every committed entry from disk. Returns the discrepancies."""
    committed = load()
    problems = []
    if committed.get("schema") != SCHEMA:
        problems.append(f"schema {committed.get('schema')!r} != {SCHEMA!r}")
    for rel, sha in committed.get("files", {}).items():
        path = ancestry.ROOT / rel
        if not path.exists():
            problems.append(f"missing certifying input: {rel}")
            continue
        actual = sha256_file(path)
        if actual != sha:
            problems.append(f"content changed: {rel} ({actual[:12]} != {sha[:12]})")
    expected = set(str(Path(p).resolve().relative_to(ancestry.ROOT))
                   for p in certifying_paths())
    listed = set(committed.get("files", {}))
    for extra in sorted(listed - expected):
        problems.append(f"manifest lists a non-certifying path: {extra}")
    for missing in sorted(expected - listed):
        problems.append(f"certifying input absent from the manifest: {missing}")
    live = runtime_contract()
    for key, value in committed.get("runtime", {}).items():
        if key in ("scipy_evidence",):
            continue
        if live.get(key) != value:
            problems.append(f"runtime {key}: {live.get(key)!r} != committed {value!r}")
    return {"ok": not problems, "problems": problems,
            "manifest_hash": manifest_hash(committed),
            "schema": committed.get("schema"),
            "files": len(committed.get("files", {}))}


def loaded_module_coverage() -> dict:
    """Every repo module currently imported must be covered or declared."""
    committed = load()
    covered = set(committed.get("files", {}))
    uncovered = []
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
        uncovered.append(rel)
    return {"ok": not uncovered, "uncovered_loaded_modules": uncovered,
            "covered": len(covered)}


def require() -> dict:
    """Fail-closed gate. Called by the runner BEFORE any certificate is emitted."""
    state = verify()
    if not state["ok"]:
        raise ManifestFailure(
            "producer manifest does not describe this repository state: "
            + "; ".join(state["problems"][:8]))
    coverage = loaded_module_coverage()
    if not coverage["ok"]:
        raise ManifestFailure(
            "executed certifying modules absent from the committed manifest: "
            + ", ".join(coverage["uncovered_loaded_modules"][:8]))
    for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                "NUMEXPR_NUM_THREADS"):
        if os.environ.get(var) != "1":
            raise ManifestFailure(
                f"threading contract violated: {var}={os.environ.get(var)!r}")
    return {"manifest_hash": state["manifest_hash"],
            "manifest_schema": SCHEMA,
            "manifest_path": str(ARTIFACT.relative_to(ancestry.ROOT)),
            "files": state["files"],
            "loaded_module_coverage": True,
            "runtime": load()["runtime"]}


def identity() -> dict:
    """What a certificate record carries as its producer identity."""
    m = load()
    return {"producer_manifest_hash": manifest_hash(m),
            "producer_manifest_schema": m["schema"],
            "producer_manifest_path": str(ARTIFACT.relative_to(ancestry.ROOT)),
            "producer_manifest_version": m["manifest_version"],
            "manifest_file_count": len(m["files"])}


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--verify", action="store_true")
    a = ap.parse_args()
    if a.write:
        print(json.dumps({"written": str(ARTIFACT.relative_to(ancestry.ROOT)),
                          "manifest_hash": write()}, indent=2))
    if a.verify or not a.write:
        print(json.dumps(verify(), indent=2))


if __name__ == "__main__":
    main()
