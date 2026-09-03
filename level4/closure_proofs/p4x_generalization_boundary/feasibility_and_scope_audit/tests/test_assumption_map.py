"""The A1-A7 map must agree with the frozen theorem and assumption audit."""

from __future__ import annotations

import pytest

IDS = ("A1", "A2", "A3", "A4", "A5", "A6", "A7")


def test_all_seven_assumptions_are_mapped(results):
    mapped = results["assumption_boundary_audit"]
    for aid in IDS:
        assert aid in mapped, aid


@pytest.mark.parametrize("aid", IDS)
def test_every_assumption_is_stated_in_the_frozen_theorem(p4, aid):
    text = (p4 / "THEOREM.md").read_text()
    assert f"**({aid})" in text, aid


@pytest.mark.parametrize("aid", IDS)
def test_every_assumption_appears_in_the_frozen_closure_report_table(p4, aid):
    text = (p4 / "CLOSURE_REPORT.md").read_text()
    assert f"| {aid} |" in text, aid


def test_only_a3_carries_a_load_bearing_negative_test(results):
    mapped = results["assumption_boundary_audit"]
    load_bearing = [aid for aid in IDS
                    if mapped[aid]["load_bearing_negative_test"] is True]
    assert load_bearing == ["A3"]


def test_the_a3_negative_test_already_passes(results):
    assert results["assumption_boundary_audit"]["A3"]["status"] == "SATISFIED"
    assert results["outside_assumption_audit"]["uniform"]["confirmed"] == 16


def test_the_first_moment_boundary_is_a_non_existence_claim(results, p4):
    cauchy = results["outside_assumption_audit"]["cauchy"]
    assert cauchy["claimed_failure_mode"].startswith("NON_EXISTENCE")
    assert cauchy["signature_reachable"] is False
    assert cauchy["load_bearing"] is False
    # and the frozen theorem says exactly that
    text = (p4 / "THEOREM.md").read_text()
    assert "E|A_1| >= E[|Z_1| 1{|Z_1| >= h + k}] = infinity" in text


def test_the_moving_support_failure_is_a_false_identity_claim(p4):
    text = (p4 / "THEOREM.md").read_text()
    assert "moving support breaks (A3), and the identity is false" in text
    assert "the identity fails by exactly `2`" in text


def test_finite_variance_is_not_required(p4):
    """t1p5 is inside the theorem: L3 needs only a 1+eta moment."""
    assert "**No finite variance is required.**" in (p4 / "CLOSURE_REPORT.md").read_text()
    audit = (p4 / "ASSUMPTION_AUDIT.md").read_text()
    assert "finite second moment of `eps` | **not needed**" in audit


def test_symmetry_is_used_only_for_the_fixed_point(p4):
    text = (p4 / "THEOREM.md").read_text()
    assert "**Symmetry is used only here.**" in text
    assert "It is not used by G1, G1', G2 or G3" in text


def test_no_assumption_beyond_a3_requires_a_failure_demonstration(results):
    mapped = results["assumption_boundary_audit"]
    required = [aid for aid in IDS
                if mapped[aid]["failure_outside_required"] is True]
    assert required == ["A3"]
