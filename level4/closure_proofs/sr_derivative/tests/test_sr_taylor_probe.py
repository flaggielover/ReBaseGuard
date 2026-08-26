"""Guards for the rigorous-but-local SR Taylor blocker probe."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from flint import arb, ctx


CAMPAIGN = Path(__file__).resolve().parents[1]
CERTIFICATE = CAMPAIGN / "certificate"
RESULT = CAMPAIGN / "results" / "sr_taylor_residual_blocker.json"
sys.path.insert(0, str(CERTIFICATE))

import validated_taylor as vt  # noqa: E402


def test_univariate_jet_exponential_coefficients():
    with ctx.workprec(128):
        coefficients = vt.exponential(vt.variable(arb(0), 4))
        assert coefficients[0].contains(1)
        assert coefficients[1].contains(1)
        assert coefficients[2].contains(arb(1) / arb(2))
        assert coefficients[3].contains(arb(1) / arb(6))
        assert coefficients[4].contains(arb(1) / arb(24))


def test_validated_taylor_integrates_quadratic():
    with ctx.workprec(128):
        value = vt.integrate_with_taylor_remainder(
            lambda z: vt.multiply(z, z),
            -arb(1),
            arb(1),
            partitions=2,
            order=4,
        )
        assert value.contains(arb(2) / arb(3))


def test_open_probe_records_exact_propagation_blocker():
    result = json.loads(RESULT.read_text())
    assert result["status"] == "OPEN"
    assert result["sampled_grid_used"] is False
    assert result["exact_global_patch_cover"] is False
    patch = arb(result["first_continuum_patch"]["certified_residual_a_upper"]["ball"])
    feasible = arb(
        result["propagation_budget"]["maximum_epsilon_a_if_epsilon_b_zero"]["ball"]
    )
    assert patch > feasible


def test_probe_never_promotes_point_evidence_to_global_evidence():
    result = json.loads(RESULT.read_text())
    assert result["proof_role"] == "RIGOROUS LOCAL PROBE; NOT A GLOBAL CERTIFICATE"
    assert result["claim"] == "NO GLOBAL SR RESIDUAL SUPREMUM CERTIFIED"
    assert "Bernstein" in result["most_plausible_fix"]
