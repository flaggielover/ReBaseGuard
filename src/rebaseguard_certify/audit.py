"""Independent replay auditor for a ReBaseGuard continuum certificate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from flint import arb

from rebaseguard_certify.certificate import sha256_file
from rebaseguard_certify.contraction import certify_monotone_block_contraction
from rebaseguard_certify.enclosure import propagate_residual_enclosure
from rebaseguard_certify.residual import certify_continuum_residuals


class AuditError(RuntimeError):
    pass


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text())


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def audit_certificate(path: Path, *, full: bool = True) -> dict[str, object]:
    if not path.is_file():
        raise AuditError(f"certificate not found: {path}")
    certificate = _load(path)
    _require(certificate.get("schema") == "rebaseguard.continuum-certificate.v1", "wrong schema")
    _require(
        certificate.get("model")
        == {"k": {"numerator": 1, "denominator": 2}, "h": {"numerator": 5, "denominator": 1}},
        "wrong model",
    )
    _require(certificate.get("target") == "E[Z_tau*T_tau]", "wrong target")
    repository = path.parent.parent
    artifact_data: dict[str, dict[str, object]] = {}
    for name, record in certificate["artifacts"].items():
        artifact_path = repository / record["path"]
        _require(artifact_path.is_file(), f"missing artifact {name}")
        _require(sha256_file(artifact_path) == record["sha256"], f"hash mismatch for {name}")
        artifact_data[name] = _load(artifact_path)

    stored_contraction = artifact_data["contraction_monotone.json"]
    safe = stored_contraction["q_safe"]
    replayed_contraction = certify_monotone_block_contraction(
        n=int(stored_contraction["n"]),
        cells=int(stored_contraction["cells"]),
        q_safe_num=int(safe["numerator"]),
        q_safe_den=int(safe["denominator"]),
        bits=int(stored_contraction["precision_bits"]),
    )
    q_safe = arb(int(safe["numerator"])) / arb(int(safe["denominator"]))
    _require(
        arb(replayed_contraction["computed_one_sided_hit_lower_enclosure"]["ball"]) > q_safe,
        "block contraction was not replayed",
    )
    _require(arb(replayed_contraction["beta_n"]["ball"]) < 1, "beta is not below one")

    if full:
        stored_residual = artifact_data["residual.json"]
        candidates = artifact_data["candidates.json"]
        replayed_residual = certify_continuum_residuals(
            candidates,
            phi_order=int(stored_residual["phi_taylor_order"]),
            subdivision_depth=int(stored_residual["coverage"]["subdivision_depth"]),
            bits=int(stored_residual["precision_bits"]),
        )
        _require(replayed_residual["coverage"]["reachable_continuum_complete"], "continuum coverage failed")
        _require(
            arb(stored_residual["delta_a"]["ball"]).contains(arb(replayed_residual["delta_a"]["ball"])),
            "delta_a replay mismatch",
        )
        _require(
            arb(stored_residual["delta_b"]["ball"]).contains(arb(replayed_residual["delta_b"]["ball"])),
            "delta_b replay mismatch",
        )
    else:
        replayed_residual = artifact_data["residual.json"]

    replayed_enclosure = propagate_residual_enclosure(
        replayed_residual, replayed_contraction, bits=256
    )
    gamma_lower = arb(replayed_enclosure["gamma"]["lower_enclosure"])
    gamma_upper = arb(replayed_enclosure["gamma"]["upper_enclosure"])
    _require(gamma_lower > 2, "Gamma lower endpoint is not greater than two")
    _require(gamma_upper > gamma_lower, "invalid Gamma interval")

    bellman = artifact_data["bellman_crosscheck.json"]
    finite_gamma = arb(bellman["gamma_finite"]["ball"])
    _require(finite_gamma > gamma_lower and finite_gamma < gamma_upper, "Bellman cross-check disagrees")
    return {
        "schema": "rebaseguard.audit-report.v1",
        "mode": "full replay" if full else "quick integrity",
        "status": "PASS",
        "model_verified": True,
        "artifact_hashes_verified": True,
        "block_contraction_replayed": True,
        "continuum_residual_replayed": full,
        "resolvent_propagation_replayed": True,
        "bellman_crosscheck_consistent": True,
        "Gamma_lower": replayed_enclosure["gamma"]["lower_enclosure"],
        "Gamma_upper": replayed_enclosure["gamma"]["upper_enclosure"],
        "Gamma_lower_gt_2": True,
    }


def _write_markdown(report: dict[str, object], destination: Path) -> None:
    destination.write_text(
        "# ReBaseGuard Certificate Audit Report\n\n"
        f"**Status:** {report['status']}  \n"
        f"**Mode:** {report['mode']}  \n"
        f"**Certified interval:** `[{report['Gamma_lower']}, {report['Gamma_upper']}]`  \n"
        "**Final inequality:** `Gamma_lower > 2`\n\n"
        "All artifact hashes, the continuum block contraction, the residual enclosure, "
        "the resolvent propagation, and the independent Bellman consistency check passed.\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("certificate")
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args(argv)
    try:
        path = Path(args.certificate)
        report = audit_certificate(path, full=not args.quick)
        if not args.quick:
            _write_markdown(report, path.parent / "audit_report.md")
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    except (AuditError, FileNotFoundError, json.JSONDecodeError, ArithmeticError) as error:
        print(f"AUDIT FAIL: {error}")
        return 2


def main_entry() -> None:
    raise SystemExit(main())


if __name__ == "__main__":
    main_entry()
