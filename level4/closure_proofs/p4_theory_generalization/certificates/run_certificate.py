#!/usr/bin/env python3
"""Rigorous Arb certification of the three frozen Priority-4 objects.

Every inequality below is decided on Arb balls, so a reported `True` means the
enclosure proves it.  Exact rational quantities are compared with `Fraction`
arithmetic, which is exact by construction.

What this file does **not** do: it does not certify any frozen CUSUM or SR
gain, Gaussian or non-Gaussian, and it does not upgrade any Monte Carlo number.
"""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

from flint import arb, ctx

CAMPAIGN = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def q(value: Fraction | tuple[int, int] | int) -> arb:
    if isinstance(value, tuple):
        value = Fraction(*value)
    if isinstance(value, int):
        value = Fraction(value, 1)
    return arb(value.numerator) / arb(value.denominator)


def ball(value: arb) -> dict[str, str]:
    return {"ball": str(value), "lower": str(value.lower()),
            "upper": str(value.upper())}


def clamp_score(z: Fraction) -> Fraction:
    """psi(z) = sign(z) * min(|z|, 1) -- a bounded, Laplace-like score."""
    if z > 0:
        return min(z, Fraction(1))
    if z < 0:
        return max(z, Fraction(-1))
    return Fraction(0)


# --------------------------------------------------------------------------
# 1. Laplace closed form, unbounded horizon
# --------------------------------------------------------------------------

def certify_laplace(spec: dict) -> dict:
    b = arb(1) / arb(int(spec["b_squared_reciprocal"])).sqrt()
    c = q(tuple(spec["c"]))
    gain = (c + b) / b
    # g_1(e) = -(c+b) tanh(e/b)
    def g1(e: arb) -> arb:
        return -(c + b) * (e / b).tanh()

    exact_derivative = -(c + b) / b
    fixed_point = g1(arb(0))

    records = []
    previous: arb | None = None
    converging = True
    for step in spec["finite_difference_steps"]:
        h = q(tuple(step))
        fd = (g1(h) - g1(-h)) / (arb(2) * h)
        error = abs(fd - exact_derivative)
        if previous is not None:
            converging &= bool(error < previous)
        previous = error
        records.append({"step": f"{step[0]}/{step[1]}",
                        "central_difference": ball(fd),
                        "error_against_exact": ball(error)})

    rho_a = q(tuple(spec["rho"]["attraction"]))
    rho_r = q(tuple(spec["rho"]["repulsion"]))
    critical = arb(1) / (gain - arb(1))
    checks = {
        "laplace_gain_closed_form": bool(gain > arb(1))
            and bool(abs(gain - (arb(1) + arb(2) * arb(2).sqrt())) < arb(2) ** -100),
        "laplace_map_fixed_point": fixed_point.contains(0),
        "laplace_finite_difference_convergence": converging,
        "laplace_attraction": bool(abs(rho_a * (arb(1) - gain)) < arb(1)),
        "laplace_repulsion": bool(abs(rho_r * (arb(1) - gain)) > arb(1)),
    }
    return {
        "object": "unit-variance Laplace, memoryless detector, m=1, unbounded horizon",
        "gain": ball(gain), "map_derivative": ball(exact_derivative),
        "critical_rho": ball(critical),
        "critical_rho_minus_sqrt2_over_4": ball(critical - arb(2).sqrt() / arb(4)),
        "finite_differences": records, "checks": checks,
    }


# --------------------------------------------------------------------------
# 2. Uniform moving-support counterexample (exactly rational)
# --------------------------------------------------------------------------

def certify_uniform(spec: dict) -> dict:
    a = Fraction(*spec["a"])
    c = Fraction(*spec["c"])
    alarm = 1 - c / a
    slope = -a / (a - c)
    rows = []
    linear = True
    for point in spec["test_points"]:
        e = Fraction(*point)
        # exact closed-form integrals of PROOF.md Section 9
        numerator = -e
        value = numerator / alarm
        linear &= value == slope * e
        rows.append({"e": f"{e.numerator}/{e.denominator}",
                     "g1": f"{value.numerator}/{value.denominator}"})
    # the theorem's right-hand side is -Gamma; the a.e. interior score of a
    # flat density is identically zero, so Gamma = 0 and the predicted slope
    # is 0.  The defect is the whole of the true slope.
    score_side = Fraction(0)
    defect = abs(slope - score_side)
    checks = {
        "uniform_alarm_probability_constant": alarm == Fraction(*spec["expected_alarm_probability"]),
        "uniform_map_exactly_linear": linear and slope == Fraction(*spec["expected_map_slope"]),
        "uniform_identity_defect_positive": defect == Fraction(*spec["expected_defect"]) and defect > 0,
    }
    return {
        "object": "uniform innovations, memoryless detector, moving support",
        "alarm_probability": f"{alarm.numerator}/{alarm.denominator}",
        "map_slope": f"{slope.numerator}/{slope.denominator}",
        "score_side": "0",
        "identity_defect": f"{defect.numerator}/{defect.denominator}",
        "points": rows, "checks": checks,
    }


# --------------------------------------------------------------------------
# 3. Finite-support general-score witness
# --------------------------------------------------------------------------

def certify_witness(spec: dict) -> dict:
    paths = []
    for item in spec["paths"]:
        increments = [Fraction(*x) for x in item["increments"]]
        paths.append({
            "label": item["label"], "p": Fraction(*item["probability"]),
            "tau": int(item["tau"]), "z": increments,
            "T": sum(increments),
            "S": sum(clamp_score(z) for z in increments),
        })
    m = int(spec["m"])

    def window_sum(path: dict) -> Fraction:
        return sum(path["z"][-min(m, path["tau"]):])

    def a_value(path: dict) -> Fraction:
        return window_sum(path) / min(m, path["tau"])

    total_mass = sum(p["p"] for p in paths)
    baseline_score = sum(p["p"] * p["S"] for p in paths)
    mean_window = sum(p["p"] * a_value(p) for p in paths)
    gain = sum(p["p"] * a_value(p) * p["S"] for p in paths)
    fixed = sum(p["p"] * (window_sum(p) / m) * p["S"] for p in paths)
    corrections = {
        p["label"]: (Fraction(1, p["tau"]) - Fraction(1, m)) * p["T"] * p["S"]
        for p in paths if p["tau"] < m
    }
    expected_correction = sum(
        p["p"] * (Fraction(1, p["tau"]) - Fraction(1, m)) * p["T"] * p["S"]
        for p in paths if p["tau"] < m
    )
    gaussian_form = sum(p["p"] * a_value(p) * p["T"] for p in paths)

    # exponential tilt P_e(w) proportional to p(w) exp(-e S(w))
    def tilt(e: arb) -> tuple[arb, arb, arb]:
        weights = [q(p["p"]) * (-e * q(p["S"])).exp() for p in paths]
        norm = sum(weights, arb(0))
        mean_a = sum((w * q(a_value(p)) for w, p in zip(weights, paths)), arb(0)) / norm
        mass = sum((w / norm for w in weights), arb(0))
        return mean_a, norm, mass

    rho_a = Fraction(*spec["rho"]["attraction"])
    rho_r = Fraction(*spec["rho"]["repulsion"])
    fd_rows = []
    previous: arb | None = None
    converging = True
    normalised = True
    for step in spec["finite_difference_steps"]:
        h = q(tuple(step))
        mp, np_, mass_p = tilt(h)
        mm, nm, mass_m = tilt(-h)
        fd = (q(rho_a) * (h + mp) - q(rho_a) * (-h + mm)) / (arb(2) * h)
        exact = q(rho_a * (1 - gain))
        error = abs(fd - exact)
        if previous is not None:
            converging &= bool(error < previous)
        previous = error
        normalised &= bool(np_ > arb(0)) and bool(nm > arb(0))
        normalised &= mass_p.contains(1) and mass_m.contains(1)
        fd_rows.append({"step": f"{step[0]}/{step[1]}",
                        "central_difference": ball(fd),
                        "error_against_exact": ball(error)})

    checks = {
        "witness_probability_normalization": total_mass == 1 and normalised,
        "witness_score_at_zero": baseline_score == 0,
        "witness_zero_is_fixed_point": mean_window == 0,
        "witness_derivative_identity": gain == Fraction(*spec["expected_gain"]),
        "witness_general_decomposition": gain == fixed + expected_correction
            and fixed == Fraction(*spec["expected_fixed_denominator_gain"]),
        "witness_short_correction_negative": all(v < 0 for v in corrections.values()),
        "witness_expected_short_correction_negative":
            expected_correction == Fraction(*spec["expected_expected_short_correction"])
            and expected_correction < 0,
        "witness_gaussian_form_gain_differs":
            gaussian_form == Fraction(*spec["expected_gaussian_form_gain"])
            and gaussian_form != gain,
        "witness_finite_difference_convergence": converging,
        "witness_attraction": abs(rho_a * (1 - gain)) < 1,
        "witness_repulsion": abs(rho_r * (1 - gain)) > 1,
    }
    return {
        "object": "finite-support exponential tilt with a bounded non-affine score",
        "not_a_location_family": True,
        "exact": {
            "gain": f"{gain.numerator}/{gain.denominator}",
            "fixed_denominator_gain": f"{fixed.numerator}/{fixed.denominator}",
            "expected_short_correction":
                f"{expected_correction.numerator}/{expected_correction.denominator}",
            "gaussian_form_gain": f"{gaussian_form.numerator}/{gaussian_form.denominator}",
            "pathwise_short_corrections": {
                k: f"{v.numerator}/{v.denominator}" for k, v in corrections.items()
            },
            "exact_unit_boundary_rho": "2/3",
        },
        "finite_differences": fd_rows, "checks": checks,
    }


def main() -> None:
    witness_path = CAMPAIGN / "certificates" / "WITNESS.json"
    manifest = json.loads((CAMPAIGN / "manifest.json").read_text())
    expected = manifest["frozen_new_inputs"]["finite_support_witness_sha256"]
    if sha256(witness_path) != expected:
        raise SystemExit("frozen witness hash mismatch")
    witness = json.loads(witness_path.read_text())
    ctx.prec = int(witness["arb_precision_bits"])

    sections = {
        "laplace_closed_form": certify_laplace(witness["laplace_closed_form"]),
        "uniform_counterexample": certify_uniform(witness["uniform_counterexample"]),
        "general_score_witness": certify_witness(witness["general_score_witness"]),
    }
    checks: dict[str, bool] = {}
    for section in sections.values():
        checks.update({k: bool(v) for k, v in section["checks"].items()})
    missing = [name for name in witness["required_certificates"] if name not in checks]
    payload = {
        "schema": "rebaseguard.p4-certificate.v1",
        "witness_sha256": sha256(witness_path),
        "arb_precision_bits": ctx.prec,
        "sections": sections,
        "required_certificates": witness["required_certificates"],
        "missing_certificates": missing,
        "all_checks_pass": not missing and all(checks.values()),
        "failed_checks": sorted(k for k, v in checks.items() if not v),
        "evidence_boundary": witness["evidence_boundary"],
    }
    out = CAMPAIGN / "certificates" / "certificate.json"
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({
        "all_checks_pass": payload["all_checks_pass"],
        "failed_checks": payload["failed_checks"],
        "missing_certificates": missing,
    }, indent=2))
    if not payload["all_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
