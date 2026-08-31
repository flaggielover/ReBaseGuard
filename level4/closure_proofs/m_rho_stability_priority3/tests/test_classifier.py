"""Focused tests for the generic stability classifier."""

from __future__ import annotations

import math

import pytest

from rebaseguard_p3_map import classifier as C


def test_multiplier_is_the_imported_identity():
    assert C.multiplier(0.25, 9.0) == pytest.approx(0.25 * (1.0 - 9.0))
    assert C.multiplier(0.0, 1e6) == 0.0


@pytest.mark.parametrize("gamma", [2.5, 7.5, 15.916540429525044])
def test_attraction_below_and_repulsion_above_the_boundary(gamma):
    rho_c = 1.0 / (gamma - 1.0)
    assert C.classify(rho_c * 0.5, gamma) == C.CLASS_STABLE
    assert C.classify(rho_c * 1.5, gamma) == C.CLASS_UNSTABLE


def test_exact_boundary_is_boundary_not_stable_or_unstable():
    gamma = 7.5
    assert C.classify(1.0 / (gamma - 1.0), gamma) == C.CLASS_BOUNDARY
    assert C.DYNAMICS[C.CLASS_BOUNDARY] == "FIRST_ORDER_BOUNDARY_INCONCLUSIVE"


def test_rho_zero_is_attracting_for_every_gain():
    for gamma in (-5.0, 0.0, 1.0, 2.0, 1e9):
        assert C.classify(0.0, gamma) == C.CLASS_STABLE


@pytest.mark.parametrize(
    "gamma,regime",
    [(7.5, "GAMMA_GT_2"), (2.0, "GAMMA_EQ_2"), (1.5, "ONE_LT_GAMMA_LT_2"),
     (1.0, "GAMMA_EQ_1"), (0.4, "ZERO_LE_GAMMA_LT_1"), (-0.5, "GAMMA_LT_0")],
)
def test_every_gain_regime_is_labelled(gamma, regime):
    assert C.gamma_regime(gamma) == regime


def test_gain_equal_one_has_no_boundary_and_is_attracting_everywhere():
    b = C.boundary(1.0)
    assert b.rho_crit is None
    assert not b.rho_crit_formula_applicable
    assert not b.accessible_in_admissible_domain
    assert C.classify(1.0, 1.0) == C.CLASS_STABLE


def test_gain_between_one_and_two_pushes_the_boundary_out_of_the_domain():
    b = C.boundary(1.5)
    assert b.rho_crit == pytest.approx(2.0)
    assert not b.accessible_in_admissible_domain
    assert "outside" in b.admissible_interpretation


def test_gain_exactly_two_puts_the_boundary_at_full_reuse():
    b = C.boundary(2.0)
    assert b.rho_crit == pytest.approx(1.0)
    assert b.accessible_in_admissible_domain
    assert C.classify(1.0, 2.0) == C.CLASS_BOUNDARY


def test_gain_below_one_uses_the_absolute_value_form_not_the_gamma_gt_one_form():
    b = C.boundary(0.5)
    assert not b.rho_crit_formula_applicable
    assert "does not apply" in b.rho_crit_formula
    assert b.rho_crit == pytest.approx(2.0)


def test_gain_strictly_between_zero_and_one_attracts_at_full_reuse():
    assert C.classify(1.0, 0.5) == C.CLASS_STABLE


def test_gain_zero_puts_the_boundary_at_full_reuse():
    b = C.boundary(0.0)
    assert b.rho_crit == pytest.approx(1.0)
    assert b.accessible_in_admissible_domain
    assert C.classify(1.0, 0.0) == C.CLASS_BOUNDARY


def test_negative_gain_admits_an_accessible_boundary():
    b = C.boundary(-1.0)
    assert b.gamma_regime == "GAMMA_LT_0"
    assert b.rho_crit == pytest.approx(0.5)
    assert b.accessible_in_admissible_domain


def test_domain_boundaries_of_rho_are_recorded():
    inside = C.classify_cell(1.0, 7.5, cell_evidence_class="X",
                             gamma_evidence_class="EXACT_SYMBOLIC")
    outside = C.classify_cell(1.5, 7.5, cell_evidence_class="X",
                              gamma_evidence_class="EXACT_SYMBOLIC")
    assert inside["rho_in_admissible_domain"]
    assert not outside["rho_in_admissible_domain"]


def test_magnitude_interval_is_zero_when_the_gain_interval_straddles_one():
    lo, hi = C.magnitude_interval(0.5, 0.5, 1.5)
    assert lo == 0.0
    assert hi == pytest.approx(0.25)


def test_magnitude_interval_rejects_negative_rho():
    with pytest.raises(ValueError):
        C.magnitude_interval(-0.1, 2.0, 3.0)


def test_uncertainty_crossing_forces_an_inconclusive_evidence_label():
    gamma, se = 11.0, 0.5
    rho = 1.0 / (gamma - 1.0)
    cell = C.classify_cell(rho, gamma,
                           cell_evidence_class="THEOREM_PLUS_EMPIRICAL_ESTIMATE",
                           gamma_evidence_class="EMPIRICAL_ONLY",
                           gamma_se=se,
                           gamma_interval=C.normal_interval(gamma, se))
    assert cell["uncertainty_status"] == C.UNCERTAINTY_SENSITIVE
    assert not cell["classification_reportable_as_robust"]
    assert cell["evidence_class"] == "INCONCLUSIVE"


def test_uncertainty_far_from_the_boundary_stays_robust():
    gamma, se = 11.0, 0.05
    cell = C.classify_cell(0.5, gamma,
                           cell_evidence_class="THEOREM_PLUS_EMPIRICAL_ESTIMATE",
                           gamma_evidence_class="EMPIRICAL_ONLY",
                           gamma_se=se,
                           gamma_interval=C.normal_interval(gamma, se))
    assert cell["uncertainty_status"] == C.UNCERTAINTY_ROBUST
    assert cell["evidence_class"] == "THEOREM_PLUS_EMPIRICAL_ESTIMATE"


def test_exact_input_never_receives_an_uncertainty_interval():
    cell = C.classify_cell(0.5, 7.5, cell_evidence_class="THEOREM_PLUS_CERTIFIED_INPUT",
                           gamma_evidence_class="EXACT_SYMBOLIC",
                           gamma_exact="15/2")
    assert cell["uncertainty_status"] == C.UNCERTAINTY_EXACT
    assert cell["gamma_tilde_ci95"] is None
    assert cell["evidence_class"] == "THEOREM_PLUS_CERTIFIED_INPUT"


def test_delta_method_standard_error_matches_the_documented_formula():
    gamma, se = 15.916540429525044, 0.05990518871399268
    b = C.boundary(gamma, se, C.normal_interval(gamma, se))
    assert b.rho_crit_se_delta == pytest.approx(se / (gamma - 1.0) ** 2)
    lo, hi = C.normal_interval(gamma, se)
    assert b.rho_crit_interval == pytest.approx([1.0 / (hi - 1.0), 1.0 / (lo - 1.0)])


def test_boundary_interval_is_unbounded_when_the_gain_interval_reaches_one():
    b = C.boundary(1.2, 0.5, (0.7, 1.7))
    assert b.rho_crit_interval == [None, None] or b.rho_crit_interval[1] is None
    assert not math.isnan(b.rho_crit)
