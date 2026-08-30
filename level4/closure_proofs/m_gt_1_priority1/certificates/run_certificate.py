#!/usr/bin/env python3
"""Generate the rigorous Arb certificate for the frozen finite-support witness."""

from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

from flint import arb, ctx
import flint

CAMPAIGN = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[4]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def q(value: Fraction | tuple[int, int] | int) -> arb:
    if isinstance(value, tuple):
        value = Fraction(*value)
    if isinstance(value, int):
        value = Fraction(value, 1)
    return arb(value.numerator) / arb(value.denominator)


def ball(value: arb) -> dict[str, str]:
    return {"ball": str(value), "lower": str(value.lower()), "upper": str(value.upper())}


def parse() -> tuple[dict, list[dict]]:
    witness_path = CAMPAIGN / "certificates" / "WITNESS.json"
    manifest = json.loads((CAMPAIGN / "manifest.json").read_text())
    expected = manifest["frozen_new_inputs"]["finite_support_witness_sha256"]
    if sha256(witness_path) != expected:
        raise SystemExit("finite-support witness hash mismatch")
    witness = json.loads(witness_path.read_text())
    paths = []
    for item in witness["paths"]:
        increments = [Fraction(*x) for x in item["increments"]]
        paths.append({
            "label": item["label"], "p": Fraction(*item["probability"]),
            "tau": int(item["tau"]), "z": increments, "T": sum(increments),
        })
    return witness, paths


def a_value(path: dict, m: int) -> Fraction:
    w = min(m, path["tau"])
    return sum(path["z"][-w:]) / w


def expectation_at(paths: list[dict], m: int, e: arb) -> tuple[arb, arb, arb]:
    weights = [q(path["p"]) * (-e * q(path["T"])).exp() for path in paths]
    normalizer = sum(weights, arb(0))
    normalized_sum = sum((weight / normalizer for weight in weights), arb(0))
    mean_a = sum((weight * q(a_value(path, m)) for weight, path in zip(weights, paths)), arb(0)) / normalizer
    return mean_a, normalizer, normalized_sum


def main() -> None:
    witness, paths = parse()
    ctx.prec = int(witness["arb_precision_bits"])
    m_grid = [int(x) for x in witness["m_grid"]]
    rho_attract = Fraction(*witness["rho"]["attraction"])
    rho_repel = Fraction(*witness["rho"]["repulsion"])
    steps = [Fraction(*x) for x in witness["finite_difference_steps"]]

    baseline_total = sum(path["p"] for path in paths)
    baseline_ET = sum(path["p"] * path["T"] for path in paths)
    score_exact = all((-path["T"] + baseline_ET) == -path["T"] for path in paths)
    records = []
    all_checks = baseline_total == 1 and baseline_ET == 0 and score_exact

    for m in m_grid:
        gamma = sum(path["p"] * a_value(path, m) * path["T"] for path in paths)
        fixed = sum(
            path["p"] * (sum(path["z"][-min(m, path["tau"]):]) / m) * path["T"]
            for path in paths
        )
        correction = sum(
            path["p"] * (Fraction(1, path["tau"]) - Fraction(1, m)) * path["T"] ** 2
            for path in paths if path["tau"] < m
        )
        decomposition = gamma == fixed + correction
        correction_nonnegative = correction >= 0
        exact_attract = rho_attract * (1 - gamma)
        exact_repel = rho_repel * (1 - gamma)

        fd_records = []
        previous_error: arb | None = None
        convergence = True
        normalization = True
        for step in steps:
            h = q(step)
            values = {}
            for label, rho in (("attraction", rho_attract), ("repulsion", rho_repel)):
                mean_plus, m_plus, n_plus = expectation_at(paths, m, h)
                mean_minus, m_minus, n_minus = expectation_at(paths, m, -h)
                f_plus = q(rho) * (h + mean_plus)
                f_minus = q(rho) * (-h + mean_minus)
                fd = (f_plus - f_minus) / (arb(2) * h)
                exact = q(rho * (1 - gamma))
                error = abs(fd - exact)
                values[label] = {"derivative": ball(fd), "exact_error": ball(error)}
                if label == "attraction":
                    if previous_error is not None:
                        convergence &= bool(error < previous_error)
                    previous_error = error
                normalization &= bool(m_plus > arb(0) and m_minus > arb(0))
                normalization &= n_plus.contains(1) and n_minus.contains(1)
            fd_records.append({"step": f"{step.numerator}/{step.denominator}", **values})

        attraction = bool(abs(q(exact_attract)) < arb(1))
        repulsion = bool(abs(q(exact_repel)) > arb(1))
        checks = {
            "probability_family_normalization": normalization,
            "score_at_zero": score_exact,
            "random_denominator_decomposition": decomposition,
            "short_correction_nonnegative": correction_nonnegative,
            "derivative_identity": gamma == Fraction(15, 2),
            "finite_difference_convergence": convergence,
            "attraction": attraction,
            "repulsion": repulsion,
        }
        passed = all(checks.values())
        all_checks &= passed
        records.append({
            "m": m,
            "exact": {
                "gamma": f"{gamma.numerator}/{gamma.denominator}",
                "fixed_contribution": f"{fixed.numerator}/{fixed.denominator}",
                "short_correction": f"{correction.numerator}/{correction.denominator}",
                "attraction_derivative": f"{exact_attract.numerator}/{exact_attract.denominator}",
                "repulsion_derivative": f"{exact_repel.numerator}/{exact_repel.denominator}",
            },
            "arb": {
                "gamma": ball(q(gamma)),
                "fixed_plus_correction": ball(q(fixed) + q(correction)),
                "attraction_derivative": ball(q(exact_attract)),
                "repulsion_derivative": ball(q(exact_repel)),
            },
            "finite_differences": fd_records,
            "checks": checks,
            "pass": passed,
        })

    payload = {
        "campaign": witness["campaign"],
        "evidence_class": "RIGOROUS_INTERVAL_FINITE_SUPPORT_ONLY",
        "backend": f"python-flint {flint.__version__} / Arb",
        "precision_bits": ctx.prec,
        "witness_sha256": sha256(CAMPAIGN / "certificates" / "WITNESS.json"),
        "analytic_probability_family": {
            "baseline_probability_sum": str(baseline_total),
            "baseline_E_T": str(baseline_ET),
            "argument": "Finite positive exponential weights have a finite strictly positive normalizer for every real e; division gives probabilities summing algebraically to one.",
            "score_argument": "M'(0)/M(0)=-E0[T]=0 by sign symmetry, hence d log P_e(omega)/de at zero is exactly -T(omega).",
            "score_at_zero_exact": score_exact,
        },
        "records": records,
        "all_checks_pass": bool(all_checks),
        "evidence_boundary": witness["evidence_boundary"],
    }
    out = CAMPAIGN / "certificates" / "certificate.json"
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({"output": str(out.relative_to(ROOT)),
                      "all_checks_pass": payload["all_checks_pass"]}, indent=2))


if __name__ == "__main__":
    main()
