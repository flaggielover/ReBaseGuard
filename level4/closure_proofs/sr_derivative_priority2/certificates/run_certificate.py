#!/usr/bin/env python3
"""Rigorous Arb certificate for the frozen SR-compatible finite witness."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

import flint
from flint import arb, ctx

CAMPAIGN = Path(__file__).resolve().parents[1]
ROOT = CAMPAIGN.parents[2]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def q(value: Fraction | tuple[int, int] | int) -> arb:
    if isinstance(value, tuple):
        value = Fraction(*value)
    if isinstance(value, int):
        value = Fraction(value)
    return arb(value.numerator) / arb(value.denominator)


def ball(value: arb) -> dict[str, str]:
    return {"ball": str(value), "lower": str(value.lower()), "upper": str(value.upper())}


def load() -> tuple[dict, list[dict]]:
    manifest = json.loads((CAMPAIGN / "manifest.json").read_text())
    witness_path = CAMPAIGN / manifest["frozen_new_inputs"]["finite_support_witness"]
    assert sha(witness_path) == manifest["frozen_new_inputs"]["finite_support_witness_sha256"]
    witness = json.loads(witness_path.read_text())
    paths = []
    for row in witness["paths"]:
        z = [Fraction(*item) for item in row["increments"]]
        paths.append({"label": row["label"], "p": Fraction(*row["probability"]),
                      "tau": int(row["tau"]), "z": z, "T": sum(z)})
    return witness, paths


def certify_stopping(path: dict, threshold: Fraction) -> dict:
    rp = rm = arb(0)
    states = []
    first = None
    for step, zf in enumerate(path["z"], start=1):
        z = q(zf)
        rp = (arb(1) + rp) * (z - q(Fraction(1, 2))).exp()
        rm = (arb(1) + rm) * (-z - q(Fraction(1, 2))).exp()
        crossed = bool(rp >= q(threshold) or rm >= q(threshold))
        states.append({"t": step, "plus": ball(rp), "minus": ball(rm),
                       "crossed": crossed})
        if crossed and first is None:
            first = step
    return {"label": path["label"], "expected_tau": path["tau"],
            "certified_tau": first, "states": states,
            "pass": first == path["tau"]}


def a_value(path: dict, m: int) -> Fraction:
    w = min(m, path["tau"])
    return sum(path["z"][-w:]) / w


def expectation(paths: list[dict], m: int, e: arb) -> tuple[arb, arb, arb]:
    weights = [q(path["p"]) * (-e * q(path["T"])).exp() for path in paths]
    normalizer = sum(weights, arb(0))
    norm_sum = sum((weight / normalizer for weight in weights), arb(0))
    mean_a = sum((weight * q(a_value(path, m))
                  for weight, path in zip(weights, paths)), arb(0)) / normalizer
    return mean_a, normalizer, norm_sum


def main() -> None:
    witness, paths = load()
    ctx.prec = int(witness["arb_precision_bits"])
    threshold = Fraction(*witness["sr"]["threshold"])
    stopping = [certify_stopping(path, threshold) for path in paths]
    stopping_pass = all(row["pass"] for row in stopping)
    baseline_sum = sum(path["p"] for path in paths)
    baseline_et = sum(path["p"] * path["T"] for path in paths)
    score_pass = baseline_et == 0 and all(-path["T"] + baseline_et == -path["T"] for path in paths)
    rho_a = Fraction(*witness["rho"]["attraction"])
    rho_r = Fraction(*witness["rho"]["repulsion"])
    steps = [Fraction(*row) for row in witness["finite_difference_steps"]]
    records = []
    all_pass = stopping_pass and baseline_sum == 1 and score_pass
    for m in witness["m_grid"]:
        gamma = sum(path["p"] * a_value(path, m) * path["T"] for path in paths)
        expected_gamma = Fraction(2) + Fraction(2, m)
        fixed = sum(path["p"] * (sum(path["z"][-min(m, path["tau"]):]) / m)
                    * path["T"] for path in paths)
        correction = sum(
            path["p"] * (Fraction(1, path["tau"]) - Fraction(1, m)) * path["T"] ** 2
            for path in paths if path["tau"] < m
        )
        exact_a = rho_a * (1 - gamma)
        exact_r = rho_r * (1 - gamma)
        previous = None
        convergence = normalization = True
        fd_rows = []
        for step in steps:
            h = q(step)
            values = {}
            for label, rho, exact in (("attraction", rho_a, exact_a),
                                      ("repulsion", rho_r, exact_r)):
                ap, mp, np_ = expectation(paths, m, h)
                am, mm, nm = expectation(paths, m, -h)
                fd = (q(rho) * (h + ap) - q(rho) * (-h + am)) / (arb(2) * h)
                error = abs(fd - q(exact))
                values[label] = {"derivative": ball(fd), "exact_error": ball(error)}
                normalization &= bool(mp > arb(0) and mm > arb(0))
                normalization &= np_.contains(1) and nm.contains(1)
                if label == "attraction":
                    if previous is not None:
                        convergence &= bool(error < previous)
                    previous = error
            fd_rows.append({"step": f"{step.numerator}/{step.denominator}", **values})
        checks = {
            "sr_stopping_times": stopping_pass,
            "probability_family_normalization": normalization and baseline_sum == 1,
            "score_at_zero": score_pass,
            "random_denominator_decomposition": gamma == fixed + correction,
            "short_correction_nonnegative": correction >= 0,
            "derivative_identity": gamma == expected_gamma,
            "finite_difference_convergence": convergence,
            "attraction": bool(abs(q(exact_a)) < arb(1)),
            "repulsion": bool(abs(q(exact_r)) > arb(1)),
        }
        passed = all(checks.values())
        all_pass &= passed
        records.append({
            "m": m,
            "exact": {
                "gamma": str(gamma), "expected_gamma": str(expected_gamma),
                "fixed_contribution": str(fixed), "short_correction": str(correction),
                "attraction_derivative": str(exact_a),
                "repulsion_derivative": str(exact_r),
            },
            "arb": {"gamma": ball(q(gamma)),
                    "fixed_plus_correction": ball(q(fixed) + q(correction)),
                    "attraction_derivative": ball(q(exact_a)),
                    "repulsion_derivative": ball(q(exact_r))},
            "finite_differences": fd_rows, "checks": checks, "pass": passed,
        })
    payload = {
        "campaign": witness["campaign"],
        "evidence_class": "RIGOROUS_INTERVAL_FINITE_SUPPORT_SR_ONLY",
        "backend": f"python-flint {flint.__version__} / Arb",
        "precision_bits": ctx.prec,
        "witness_sha256": sha(CAMPAIGN / "certificates" / "WITNESS.json"),
        "sr_stopping_certificates": stopping,
        "analytic_probability_family": {
            "baseline_probability_sum": str(baseline_sum),
            "baseline_E_T": str(baseline_et),
            "normalization_argument": "Finite positive exponential weights give a finite strictly positive M(e); division gives probabilities summing exactly to one.",
            "score_argument": "d log P_e/de|0=-T-M'(0)/M(0)=-T+E0[T]=-T by sign symmetry.",
            "score_at_zero_exact": score_pass,
        },
        "records": records, "all_checks_pass": bool(all_pass),
        "evidence_boundary": witness["evidence_boundary"],
    }
    output = CAMPAIGN / "certificates" / "certificate.json"
    output.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({"output": str(output.relative_to(ROOT)),
                      "all_checks_pass": payload["all_checks_pass"]}, indent=2))
    if not payload["all_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
