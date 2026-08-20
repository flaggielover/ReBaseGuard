"""Command-line entry point."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rebaseguard_certify import audit
from rebaseguard_certify.bellman import finite_interval_bellman_crosscheck
from rebaseguard_certify.certificate import finalize_after_audit, write_certificate
from rebaseguard_certify.contraction import certify_monotone_block_contraction
from rebaseguard_certify.enclosure import propagate_residual_enclosure
from rebaseguard_certify.residual import certify_continuum_residuals, construct_candidate_payloads


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _prove(destination: Path) -> int:
    repository = destination.parent.parent
    proof_directory = repository / "proofs"
    proof_directory.mkdir(parents=True, exist_ok=True)
    contraction = certify_monotone_block_contraction()
    _write_json(proof_directory / "contraction_monotone.json", contraction)
    candidates = construct_candidate_payloads(degree=12, quadrature_order=400, scale_bits=50)
    _write_json(proof_directory / "candidates.json", candidates)
    residual = certify_continuum_residuals(
        candidates, phi_order=50, subdivision_depth=0, bits=256
    )
    _write_json(proof_directory / "residual.json", residual)
    enclosure = propagate_residual_enclosure(residual, contraction, bits=256)
    _write_json(proof_directory / "enclosure.json", enclosure)
    bellman = finite_interval_bellman_crosscheck(cells=12, z_bins=96, bits=192)
    _write_json(proof_directory / "bellman_crosscheck.json", bellman)
    write_certificate(repository, destination)
    if not enclosure["gamma_lower_gt_2"]:
        return 1
    audit_status = audit.main([str(destination)])
    if audit_status != 0:
        return audit_status
    finalize_after_audit(destination, proof_directory / "audit_report.md")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    audit_parser = subparsers.add_parser("audit")
    audit_parser.add_argument("certificate")
    prove_parser = subparsers.add_parser("prove")
    prove_parser.add_argument("--certificate", required=True)
    args = parser.parse_args(argv)
    if args.command == "audit":
        return audit.main([args.certificate])
    return _prove(Path(args.certificate))


def main_entry() -> None:
    raise SystemExit(main())


if __name__ == "__main__":
    main_entry()
