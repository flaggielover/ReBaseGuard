"""Tight two-sided resolvent audit invariants.  Pre-freeze; nothing frozen."""
from __future__ import annotations
import json
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
R = json.loads((NS / "tight_two_sided_resolvent_audit" / "audit_results.json").read_text())


def test_nothing_binding_created_or_run():
    assert R["next_binding_checkpoint"] == "NOT_CREATED"
    assert R["binding_gate_run"] is False and R["sr_prototype_rerun"] is False


def test_one_sided_fallback_preserved():
    f = R["one_sided_fallback"]
    assert f["C_cell"] == 216.963 and f["preserved"] and f["weakened"] is False


def test_b2_and_f3_untouched():
    i = R["invariants"]
    assert i["b2_unchanged"] and i["f3_unchanged"] and i["candidate_unchanged"]
    assert i["one_sided_bound_unchanged"] and i["recurrence_unchanged"]


def test_true_two_sided_constant_is_much_smaller():
    s = R["numerical_reference_diagnostic"]["sup_h"]
    assert s["0.24"] < 140 and s["0.25"] < 130 and s["0.26"] < 120
    assert R["numerical_reference_diagnostic"]["slack_of_one_sided_at_worst_e"] > 1.5


def test_supersolution_identity_gives_a_uniform_margin():
    r = R["route"]
    assert "alpha-1" in r["identity"].replace(" ", "")
    assert "UNIFORM" in r["key"]


def test_degree_16_is_the_best_fit_and_20_is_worse():
    f = {d["degree"]: d for d in R["candidate_fits"]}
    assert f[16]["C_pointwise"] < f[12]["C_pointwise"]
    assert f[20]["C_pointwise"] > f[16]["C_pointwise"]     # monomial blow-up
    assert f[16]["C_pointwise"] < 150


def test_arb_conversion_was_required():
    assert "Arb" in R["conversion_note"] and "-1.45e6" in R["conversion_note"]


def test_sign_certificate_fails_the_cost_budget_everywhere():
    for row in R["sign_certificate_cost"]:
        assert row["T2"] is False
        assert row["six_core_hours"] > R["T2_budget_six_core_hours"]


def test_tightening_C_alone_does_not_close_F3():
    best = [r for r in R["f3_impact"] if r["C"] == 134.854][0]
    assert best["direct_1024_ratio"] > 1.0        # still short even with a perfect C
    assert R["verdicts"]["C_side_worth_at_most"] < 2.0


def test_not_frozen_with_the_right_failure_class():
    v = R["verdicts"]
    assert v["ready_to_freeze"] is False and v["failure_class"] == "TC-C"
    assert v["rigorous_C_obtained"] is False
    assert v["class_rigorous"] == "NO_IMPROVEMENT"
