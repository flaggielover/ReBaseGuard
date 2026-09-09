"""Tightly bound adapter to the AUTHORITATIVE SR cell computation.

This module implements NO science. It resolves and calls the already-frozen
scientific modules and records their identity, so the integrated launcher cannot
drift from the adjudicated computation:

    sr_pilot.sr_cell(index)                     -> the frozen cell spec
    sr_nstep.ResolventCertificate.from_frozen_cell(cell)
    sr_propagate.cell_certificate(...)          -> THE result-bearing computation
    sr_universe.resume_identity / admit         -> frozen resume semantics
    sr_provenance.scientific_hash / tcb_from_execution

The `science` parameter exists so the launcher's result-bearing transition can be
exercised in tests with a stub, WITHOUT executing a genuine production cell. The
default is the real authoritative callable.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ADAPTER_SCHEMA = "rebaseguard.p5y.k1.sr.multihost.executor-adapter.v1"

BOUND_SCIENTIFIC_MODULES = (
    "level4/closure_proofs/p5y_k1_sr_qualification/code/sr_pilot.py",
    "level4/closure_proofs/p5y_k1_sr_qualification/code/sr_propagate.py",
    "level4/closure_proofs/p5y_k1_sr_qualification/code/sr_nstep.py",
    "level4/closure_proofs/p5y_k1_sr_qualification/code/sr_universe.py",
    "level4/closure_proofs/p5y_k1_sr_qualification/code/sr_provenance.py",
    "level4/closure_proofs/p5y_k1_sr_qualification/code/sr_operators.py",
    "level4/closure_proofs/p5y_k1_sr_qualification/code/sr_sources.py",
    "level4/closure_proofs/p5y_k1_sr_qualification/code/sr_patch.py",
    "level4/closure_proofs/p5y_k1_sr_qualification/code/sr_refine.py",
    "level4/closure_proofs/p5y_k1_sr_qualification/code/sr_width.py",
    "level4/closure_proofs/p5y_k1_sr_qualification/code/sr_cost.py",
    "level4/closure_proofs/p5y_k1_sr_qualification/code/sr_dag.py",
    "level4/closure_proofs/p5y_k1_task1r_budget_harness/code/harness.py",
    "level4/closure_proofs/p5y_k1_sr_backend_cost_audit/code/opt_backend.py",
    "level4/closure_proofs/p5y_k1_cover_ledger_implementation/code/spec.py",
    "level4/closure_proofs/p5y_k1_cover_ledger_implementation/code/universe.py",
)

_SYS_PATH_SUBDIRS = (
    "level4/closure_proofs/p5y_k1_sr_qualification/code",
    "level4/closure_proofs/p5y_k1_task1r_budget_harness/code",
    "level4/closure_proofs/p5y_k1_sr_backend_cost_audit/code",
    "level4/closure_proofs/p5y_k1_cover_ledger_implementation/code",
    "level4/closure_proofs/p5x_global_nonlinear_dynamics/compute_optimization_r3_sr_symbolic",
    "rebaseguard-proof/src",
)


class AdapterRefusal(RuntimeError):
    """The scientific adapter refused to bind."""


def adapter_identity(root) -> dict:
    """SHA-256 of every bound scientific module plus this adapter itself."""
    root = Path(root)
    mods = {}
    for rel in BOUND_SCIENTIFIC_MODULES:
        p = root / rel
        if not p.exists():
            raise AdapterRefusal(f"bound scientific module absent: {rel}")
        mods[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    mods["<adapter>"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    blob = "".join(f"{k}:{v}\n" for k, v in sorted(mods.items())).encode()
    return {"schema": ADAPTER_SCHEMA, "modules": mods,
            "SCIENTIFIC_ADAPTER_HASH": hashlib.sha256(blob).hexdigest()}


def bind(root):
    """Import the authoritative modules. No science is implemented here."""
    root = Path(root)
    for sub in _SYS_PATH_SUBDIRS:
        p = str(root / sub)
        if p not in sys.path:
            sys.path.insert(0, p)
    try:
        import sr_pilot, sr_propagate, sr_nstep, sr_universe, sr_provenance
    except Exception as exc:                                   # noqa: BLE001
        raise AdapterRefusal(f"cannot bind authoritative science: {exc!r}") from exc
    return {"sr_pilot": sr_pilot, "sr_propagate": sr_propagate, "sr_nstep": sr_nstep,
            "sr_universe": sr_universe, "sr_provenance": sr_provenance}


def real_cell_certificate(mods, cell_index: int) -> dict:
    """THE authoritative result-bearing computation. Never called while the frozen
    authorization has production_enabled=false."""
    from fractions import Fraction as F
    from flint import arb
    cell = mods["sr_pilot"].sr_cell(cell_index)
    lo, hi = F(cell["left"][0]), F(cell["right"][0])
    rho = abs(F(cell["rho"][0]))

    def _arb(f):
        f = F(f)
        return arb(f.numerator) / arb(f.denominator)

    res = mods["sr_nstep"].ResolventCertificate.from_frozen_cell(cell)
    return mods["sr_propagate"].cell_certificate(
        resolvent=res, e_lo=_arb(lo), e_hi=_arb(hi), rho=_arb(rho), cell_e=(lo, hi))


def execute_cell(root, cell_index: int, *, science=None) -> dict:
    """Execute ONE cell through the authoritative computation.

    `science` is injectable ONLY so the launcher's post-authorization path is
    independently testable; the default is the real authoritative callable.
    """
    mods = bind(root)
    fn = science if science is not None else real_cell_certificate
    cert = fn(mods, cell_index)
    return {"cell_id": cell_index, "certificate": cert,
            "scientific_content_hash": mods["sr_provenance"].sha256_bytes(
                mods["sr_provenance"].canonical(
                    {"cell": cell_index, "cert": repr(cert)}))}
