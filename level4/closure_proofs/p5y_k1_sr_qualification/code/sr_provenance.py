"""SR certifying provenance: execution-derived TCB, runtime binding, scientific
hash and the truly-final fail-closed producer gate.

Built on the Aux4 CORRECTED principles, but NOT by copying the Aux4 manifest.
The SR path imports a different module set (sr_sources, sr_operators,
sr_propagate, plus the frozen assembly/spec/universe and the P5X panel
primitives), so its TCB must be DERIVED FROM THIS EXECUTION, not declared ahead
of time. A copied Aux4 manifest would be silently wrong for SR.

The five Aux3 provenance failures Aux4 repaired, and how they are avoided here:

  PRODUCER_MANIFEST      exact absolute paths, hashed; no basename whitelist,
                         no exemptions. `tcb_from_execution` reads sys.modules
                         AFTER the certifying computation, so a module that was
                         imported lazily is still captured.
  STRICT_ENFORCEMENT     `final_gate` runs after the certificate is assembled AND
                         after the scientific hash is computed, and raises.
  RUNTIME_BINDING        CPython build, flint/Arb version, BLAS kernel and thread
                         contract are bound into the record.
  CERTIFICATE_DETERMINISM  no lazy imports on the certifying path and no bare
                         `except Exception`; `assert_no_lazy_imports` enforces it
                         by AST over this namespace.
  AUXILIARY_GOVERNANCE   `scientific_fields` is schema-driven: every field named
                         in the schema must be present, so a new scientific
                         quantity cannot silently escape the hash.
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import platform
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
ROOT = NS.parents[2]
_IMPL = ROOT / "level4/closure_proofs/p5y_k1_cover_ledger_implementation/code"
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))

import flint                                                       # noqa: E402
import spec                                                        # noqa: E402

SCHEMA = "k1.sr.certificate.v1"

# Every scientific field that MUST enter the hash. Schema-driven: a missing key
# is a hard failure, so a new quantity cannot be added without being bound.
SCIENTIFIC_FIELDS = (
    "detector", "cell_index", "m", "bits", "e_lo", "e_hi", "rho",
    "C_resolvent", "k0", "k1", "k2", "kz", "kz1", "kz2",
    "R_interval_mag", "D_interval_mag", "R2_interval_mag", "M_R2",
    "W_cover_exact", "B_cover_budget", "utilisation",
    "s0_envelope_order0", "s0_envelope_order1", "s0_envelope_order2",
    "assembly_coefficients_sha256", "dag_sha256", "excluded_routes_sha256",
)


# ------------------------------------------------------- M_R2 semantics lock
M_R2_SEMANTICS = "sup_{e in cell} |R''_{SR,m}(e)| == mag(R2_interval)"
"""The K1 cover obligation. See assembly.curvature_bound and ledger.cover_charge."""

FORBIDDEN_M2_SEMANTICS = "sup_e E_e[Rbar^2]"
"""The P5X theorem-consumer scalar M_2 (EXACT_SR_TARGET.md section 5).

A DIFFERENT quantity. It feeds P5X-T4/T6/T9 and is NOT a K1 cover obligation.
Substituting it for M_R2 would leave every K1 cover obligation undischarged while
appearing to succeed, so the two must never share a field name, a schema slot or
a variable name. Enforced by assert_M_R2_semantics and by tests.
"""

FORBIDDEN_FIELD_NAMES = ("M_2", "M2", "E_Rbar2", "E_Rbar_squared", "Rbar2_mean")


class M_R2SemanticsViolation(RuntimeError):
    """The P5X scalar M_2 leaked into a K1 M_R2 slot."""


def assert_M_R2_semantics(record: dict | None = None) -> bool:
    """No record or schema field may carry the P5X M_2 under a K1 name."""
    if "M_R2" not in SCIENTIFIC_FIELDS:
        raise M_R2SemanticsViolation("M_R2 vanished from the scientific schema")
    for bad in FORBIDDEN_FIELD_NAMES:
        if bad in SCIENTIFIC_FIELDS:
            raise M_R2SemanticsViolation(
                f"{bad} (the P5X scalar M_2) is in the K1 scientific schema")
        if record is not None and bad in record:
            raise M_R2SemanticsViolation(
                f"{bad} (the P5X scalar M_2) is present in a K1 record")
    return True


class ProducerGateFailure(RuntimeError):
    """The truly-final fail-closed producer gate rejected this record."""


class LazyImportOnCertifyingPath(RuntimeError):
    """A function-level import was found in a certifying module."""


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p: Path) -> str:
    return sha256_bytes(p.read_bytes())


def canonical(obj) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True) + "\n").encode("ascii")


# --------------------------------------------------------------- TCB
def tcb_from_execution() -> dict:
    """Exact path-based TCB derived from what THIS process actually imported.

    No basename whitelist and no declared allow-list: every loaded module whose
    file lives under the repository root is hashed by its absolute path. Call
    this AFTER the certifying computation so lazily imported modules cannot
    escape.
    """
    out = {}
    for name, mod in sorted(sys.modules.items()):
        f = getattr(mod, "__file__", None)
        if not f:
            continue
        p = Path(f).resolve()
        try:
            p.relative_to(ROOT)
        except ValueError:
            continue
        if p.suffix != ".py":
            continue
        out[str(p)] = sha256_file(p)
    return out


def assert_no_lazy_imports(code_dir: Path | None = None) -> list[str]:
    """AST check: no import inside a function/method in this namespace."""
    code_dir = code_dir or (NS / "code")
    offenders = []
    for p in sorted(code_dir.glob("*.py")):
        tree = ast.parse(p.read_text())
        for fn in ast.walk(tree):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for n in ast.walk(fn):
                if isinstance(n, (ast.Import, ast.ImportFrom)):
                    offenders.append(f"{p.name}:{n.lineno}")
    if offenders:
        raise LazyImportOnCertifyingPath(str(offenders))
    return offenders


def assert_no_bare_except(code_dir: Path | None = None) -> list[str]:
    """AST check: no `except Exception` / bare except on the certifying path."""
    code_dir = code_dir or (NS / "code")
    offenders = []
    for p in sorted(code_dir.glob("*.py")):
        for n in ast.walk(ast.parse(p.read_text())):
            if isinstance(n, ast.ExceptHandler):
                t = n.type
                if t is None or (isinstance(t, ast.Name) and t.id == "Exception"):
                    offenders.append(f"{p.name}:{n.lineno}")
    if offenders:
        raise LazyImportOnCertifyingPath("bare/broad except: " + str(offenders))
    return offenders


# --------------------------------------------------------- runtime binding
def runtime_binding() -> dict:
    """CPython build, Arb/flint identity, BLAS kernel and the thread contract."""
    binding = {
        "python_version": sys.version,
        "python_build": " ".join(platform.python_build()),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "flint_version": getattr(flint, "__version__", "unknown"),
        "flint_file": str(Path(flint.__file__).resolve()),
        "threads_pinned": {v: os.environ.get(v) for v in
                           ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                            "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS")},
    }
    so = Path(flint.__file__).resolve().parent
    libs = sorted(str(p) for p in so.rglob("*.so"))[:8]
    binding["backend_libraries"] = {p: sha256_file(Path(p)) for p in libs
                                    if Path(p).exists()}
    return binding


# -------------------------------------------------------- scientific hash
def scientific_fields(record: dict) -> dict:
    """Project the record onto the schema. A missing field is a hard failure."""
    missing = [k for k in SCIENTIFIC_FIELDS if k not in record]
    if missing:
        raise ProducerGateFailure(f"scientific fields missing from record: {missing}")
    return {k: record[k] for k in SCIENTIFIC_FIELDS}


def scientific_hash(record: dict) -> str:
    return sha256_bytes(canonical(scientific_fields(record)))


# ------------------------------------------------------------ final gate
def final_gate(record: dict, *, tcb: dict, expected_tcb: dict | None = None) -> dict:
    """Truly-final fail-closed gate. Runs AFTER assembly AND after the hash.

    Raises on any of: missing scientific field, empty TCB, a certifying module
    absent from the TCB, a TCB hash mismatch against a pinned manifest, an
    unpinned thread contract, or a lazy import / broad except on the path.
    """
    assert_M_R2_semantics(record)                    # M_2 must not wear M_R2's name
    h = scientific_hash(record)                      # raises on missing fields
    if not tcb:
        raise ProducerGateFailure("empty TCB")
    required = {"sr_sources.py", "sr_operators.py", "sr_propagate.py"}
    present = {Path(p).name for p in tcb}
    if not required <= present:
        raise ProducerGateFailure(f"certifying modules absent from TCB: "
                                  f"{sorted(required - present)}")
    if expected_tcb is not None:
        drift = {p: (tcb.get(p), expected_tcb.get(p))
                 for p in set(tcb) | set(expected_tcb)
                 if tcb.get(p) != expected_tcb.get(p)}
        if drift:
            raise ProducerGateFailure(f"TCB drift against pinned manifest: "
                                      f"{sorted(drift)[:4]}")
    assert_no_lazy_imports()
    assert_no_bare_except()
    binding = runtime_binding()
    if binding["threads_pinned"]["OMP_NUM_THREADS"] != "1":
        raise ProducerGateFailure("thread contract not pinned to 1")
    return {"schema": SCHEMA, "scientific_hash": h, "tcb": tcb,
            "runtime_binding": binding, "gate": "PASS"}


def resume_identity(record: dict, tcb: dict) -> str:
    """Exact resume identity: scientific hash + TCB + frozen checkpoint hash."""
    return sha256_bytes(canonical({
        "scientific_hash": scientific_hash(record),
        "tcb": tcb,
        "checkpoint_sha256": spec.CHECKPOINT_SHA256,
        "schema": SCHEMA,
    }))
