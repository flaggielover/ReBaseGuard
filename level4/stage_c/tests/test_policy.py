"""The ReBaseGuard policy: definition, guarantees, and independence from outcomes."""

from __future__ import annotations

import inspect

import numpy as np
import pytest

import policy
from policy import (
    CONSERVATIVE,
    GAMMA_CERT_HIGH,
    GAMMA_CERT_LOW,
    GAMMA_POINT,
    POINT,
    critical_rho,
    policy_table,
    rho_safe,
)


def test_critical_rho_matches_frozen_theory():
    assert critical_rho(GAMMA_POINT) == pytest.approx(1.0 / (GAMMA_POINT - 1.0))
    assert critical_rho(GAMMA_CERT_HIGH) == pytest.approx(0.037245, abs=1e-6)
    assert critical_rho(GAMMA_CERT_LOW) == pytest.approx(0.341957, abs=1e-6)


def test_critical_rho_rejects_gamma_below_one():
    with pytest.raises(ValueError, match="must exceed 1"):
        critical_rho(0.8)


@pytest.mark.parametrize("delta", [0.05, 0.1, 0.2, 0.5, 0.9])
def test_policy_meets_its_own_slope_target(delta):
    for variant in (POINT, CONSERVATIVE):
        r = rho_safe(delta, variant=variant)
        assert abs(r.slope_at_zero) == pytest.approx(1.0 - delta, rel=1e-12)


def test_conservative_is_never_less_conservative_than_point():
    """The certified variant must never allow MORE reuse than the heuristic."""
    for delta in (0.01, 0.05, 0.2, 0.5, 0.99):
        assert rho_safe(delta, variant=CONSERVATIVE).rho <= \
            rho_safe(delta, variant=POINT).rho


def test_conservative_guarantee_holds_across_the_whole_certified_interval():
    """|F'_rho(0)| = rho(Gamma-1) <= 1-delta for EVERY Gamma the certificate allows."""
    delta = 0.2
    rho = rho_safe(delta, variant=CONSERVATIVE).rho
    for gamma in np.linspace(GAMMA_CERT_LOW, GAMMA_CERT_HIGH, 500):
        assert rho * (gamma - 1.0) <= 1.0 - delta + 1e-12


def test_point_guarantee_can_fail_inside_the_certified_interval():
    """The heuristic variant is NOT certified, and this shows why."""
    delta = 0.2
    rho = rho_safe(delta, variant=POINT).rho
    worst = rho * (GAMMA_CERT_HIGH - 1.0)
    assert worst > 1.0, (
        "if this ever drops below 1 the POINT variant would be safe by accident; "
        "the distinction in the report would then need restating"
    )


def test_rho_is_decreasing_in_delta():
    for variant in (POINT, CONSERVATIVE):
        rhos = [rho_safe(d, variant=variant).rho for d in (0.05, 0.2, 0.5, 0.9)]
        assert all(rhos[i] > rhos[i + 1] for i in range(len(rhos) - 1))


def test_clipping_to_unit_interval():
    r = rho_safe(0.2, variant=POINT, gamma_point=1.05)
    assert r.rho == 1.0 and r.clipped is True


@pytest.mark.parametrize("bad", [0.0, 1.0, -0.1, 1.5])
def test_delta_must_be_strictly_inside_zero_one(bad):
    with pytest.raises(ValueError, match="delta"):
        rho_safe(bad)


def test_unknown_variant_rejected():
    with pytest.raises(ValueError, match="variant"):
        rho_safe(0.2, variant="optimistic")


def test_headline_policy_values_match_the_frozen_protocol():
    """These exact numbers are written into STAGE_C_PROTOCOL.md."""
    assert rho_safe(0.2, variant=CONSERVATIVE).rho == pytest.approx(0.029796,
                                                                    abs=1e-6)
    assert rho_safe(0.2, variant=POINT).rho == pytest.approx(0.053743, abs=1e-6)


def test_policy_does_not_depend_on_stage_b_root():
    """The policy must be definable without any Stage B or Stage C outcome.

    Two separate checks, because they guard different failure modes:

    * outcome VALUES (the Stage B root interval, the certified multiplier) must
      not appear anywhere in the file, prose included -- that would mean a
      number from the evaluation had been copied into the rule;
    * outcome IDENTIFIERS must not appear in executable code -- that would mean
      the rule imports or reads a result. Docstrings are excluded from this
      second check, since naming a test or explaining scope is not a dependency.
    """
    import io
    import tokenize

    src = inspect.getsource(policy)

    forbidden_values = ["1.0287", "1.0447", "0.10814", "0.83253", "0.029796",
                        "0.053743"]
    for value in forbidden_values:
        assert value not in src, f"outcome value {value} appears in policy.py"

    code_tokens = []
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type in (tokenize.STRING, tokenize.COMMENT):
            continue
        code_tokens.append(tok.string)
    code = " ".join(code_tokens)
    for name in ("e_star", "period2", "stage_b", "incontrol", "detection",
                 "oracle", "lambda2", "campaign", "analyze"):
        assert name not in code, f"policy code references {name!r}"

    for line in src.splitlines():
        if line.startswith(("import ", "from ")):
            assert "rebaseguard" not in line and "campaign" not in line, line


def test_policy_is_a_pure_function_of_gamma_and_delta():
    a = rho_safe(0.2, variant=CONSERVATIVE)
    b = rho_safe(0.2, variant=CONSERVATIVE)
    assert a == b
    assert rho_safe(0.2, variant=CONSERVATIVE,
                    gamma_cert_high=20.0).rho != a.rho


def test_policy_table_covers_both_variants():
    rows = policy_table()
    assert len(rows) == 8
    assert {r["variant"] for r in rows} == {POINT, CONSERVATIVE}
    for r in rows:
        if r["variant"] == CONSERVATIVE:
            assert "certified" in r["guarantee"]
            assert "LOCAL LINEAR STABILITY" in r["evidence_class"]
        else:
            assert "heuristic" in r["guarantee"]
            assert "NOT certified" in r["evidence_class"]
