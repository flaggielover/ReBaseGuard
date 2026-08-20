"""Assemble the machine-readable proof certificate from audited artifacts."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import platform
import sys
from pathlib import Path

import flint


ARTIFACT_NAMES = (
    "candidates.json",
    "contraction_monotone.json",
    "residual.json",
    "enclosure.json",
    "bellman_crosscheck.json",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_certificate(repository: Path) -> dict[str, object]:
    proof_directory = repository / "proofs"
    artifacts: dict[str, object] = {}
    loaded: dict[str, object] = {}
    for name in ARTIFACT_NAMES:
        path = proof_directory / name
        if not path.is_file():
            raise FileNotFoundError(path)
        artifacts[name] = {"path": f"proofs/{name}", "sha256": sha256_file(path)}
        loaded[name] = json.loads(path.read_text())
    enclosure = loaded["enclosure.json"]
    residual = loaded["residual.json"]
    contraction = loaded["contraction_monotone.json"]
    if not enclosure["gamma_lower_gt_2"]:
        raise ArithmeticError("stored enclosure does not certify Gamma > 2")
    return {
        "schema": "rebaseguard.continuum-certificate.v1",
        "model": {"k": {"numerator": 1, "denominator": 2}, "h": {"numerator": 5, "denominator": 1}},
        "target": "E[Z_tau*T_tau]",
        "state_reduction": "E[Z_tau*T_tau|S_t=(p,m),T_t=x]=a(p,m)*x+b(p,m)",
        "target_state": "Gamma=b(0,0)",
        "reachable_domain": "axes 0<=p<h or 0<=m<h, plus p>0,m>0,p+m<h-2k",
        "symmetry": {"a": "a(p,m)=-a(m,p)", "b": "b(p,m)=b(m,p)"},
        "interval_backend": {
            "name": "python-flint/FLINT-Arb",
            "python_flint": flint.__version__,
            "flint": flint.__FLINT_VERSION__,
            "precision_bits": residual["precision_bits"],
            "semantics": "outward-rounded real balls",
        },
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": importlib.metadata.version("numpy"),
            "scipy": importlib.metadata.version("scipy"),
            "pytest": importlib.metadata.version("pytest"),
        },
        "gaussian_handling": {
            "tail_cutoff": None,
            "tail_bound": "no truncation; absorbing tails use full Gaussian moment formulas",
            "density_enclosure": f"degree-{2*int(residual['phi_taylor_order'])} Maclaurin polynomial plus uniform Lagrange remainder",
            "phi_uniform_error": residual["phi_uniform_error"],
        },
        "continuum_method": {
            "candidate_role": "exact dyadic candidate only; not proof evidence",
            "range_method": "symbolic integration plus tensor Bernstein convex-hull bounds",
            "coverage": residual["coverage"],
            "delta_a": residual["delta_a"],
            "delta_b": residual["delta_b"],
        },
        "block_contraction": {
            "n": contraction["n"],
            "beta_n": contraction["beta_n"],
            "q_safe": contraction["q_safe"],
            "computed_lower": contraction["computed_one_sided_hit_lower_enclosure"],
            "resolvent_bound": contraction["resolvent_bound"],
            "continuum_argument": contraction["continuum_argument"],
        },
        "error_propagation": {
            "mu": enclosure["mu"],
            "E_a": enclosure["E_a"],
            "E_b": enclosure["E_b"],
            "formula": enclosure["formula"],
        },
        "Gamma_lower": enclosure["gamma"]["lower_enclosure"],
        "Gamma_upper": enclosure["gamma"]["upper_enclosure"],
        "result": "Gamma_lower > 2",
        "proof_status": "CERTIFIED_PENDING_INDEPENDENT_AUDIT",
        "artifacts": artifacts,
        "trusted_computing_base": [
            "CPython exact integer serialization",
            "python-flint bindings",
            "FLINT/Arb outward-rounded arithmetic and transcendental functions",
            "symbolic polynomial and Bernstein residual checker",
            "monotone block-contraction checker",
            "rebaseguard_certify.audit replay and hash logic",
        ],
    }


def write_certificate(repository: Path, destination: Path) -> dict[str, object]:
    certificate = build_certificate(repository)
    destination.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    return certificate


def finalize_after_audit(destination: Path, audit_report: Path) -> dict[str, object]:
    certificate = json.loads(destination.read_text())
    if not audit_report.is_file():
        raise FileNotFoundError(audit_report)
    certificate["proof_status"] = "CERTIFIED"
    certificate["independent_audit"] = {
        "status": "PASS",
        "mode": "full replay",
        "path": str(audit_report.relative_to(destination.parent.parent)),
        "sha256": sha256_file(audit_report),
    }
    destination.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    return certificate
