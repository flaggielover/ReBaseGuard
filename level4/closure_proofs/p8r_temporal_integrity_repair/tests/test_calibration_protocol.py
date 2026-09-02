"""The calibration protocol says one thing and the executed run did it.

P8 failed ``G14`` partly because ``EXPERIMENT_PROTOCOL.md`` declared 250,000
search cycles and 2,048,000 verification cycles while the executable and the
artifacts used 163,840 and 1,024,000.  There was no single authoritative budget
and nothing checked the two against each other.  These tests are that check.
"""
import pytest

from rebaseguard_p8r import calibrate as CAL
from rebaseguard_p8r.config import (CAL_RETRY_BATCH0, CAL_S1_BATCH0,
                                    CAL_S1_ITERATIONS, CAL_S1_ROW_BLOCKS,
                                    CAL_S2_BATCH0, CAL_S2_ITERATIONS,
                                    CAL_S2_ROW_BLOCKS, CAL_TOLERANCE,
                                    CAL_VERIFY_1_BATCH, CAL_VERIFY_2_BATCH,
                                    CAL_VERIFY_ROW_BLOCKS, ROWS_PER_BLOCK)
from conftest import payload_or_skip


def test_there_is_exactly_one_declared_budget():
    d = CAL.declared_budget()
    assert d["s1_cycles_per_evaluation"] == CAL_S1_ROW_BLOCKS * ROWS_PER_BLOCK
    assert d["s2_cycles_per_evaluation"] == CAL_S2_ROW_BLOCKS * ROWS_PER_BLOCK
    assert d["verification_cycles"] == CAL_VERIFY_ROW_BLOCKS * ROWS_PER_BLOCK
    assert d["tolerance"] == CAL_TOLERANCE


def test_search_batch_regions_are_disjoint():
    s1 = set(range(CAL_S1_BATCH0, CAL_S1_BATCH0 + CAL_S1_ITERATIONS))
    s2 = set(range(CAL_S2_BATCH0, CAL_S2_BATCH0 + CAL_S2_ITERATIONS))
    rt = set(range(CAL_RETRY_BATCH0, CAL_RETRY_BATCH0 + CAL_S2_ITERATIONS))
    assert not (s1 & s2) and not (s1 & rt) and not (s2 & rt)
    assert CAL_VERIFY_1_BATCH not in s1 | s2 | rt
    assert CAL_VERIFY_2_BATCH not in s1 | s2 | rt
    assert CAL_VERIFY_1_BATCH != CAL_VERIFY_2_BATCH


def test_the_search_is_fixed_length_and_selects_no_best_iterate():
    """No early stop and no argmin: the returned threshold is the iterate the
    last update produces.  A data-dependent stopping rule would let search
    noise choose the answer."""
    src = (CAL.__file__)
    text = open(src).read()
    body = text[text.index("def _search_stage"):text.index("def _verify")]
    assert "break" not in body
    assert "min(" not in body and "argmin" not in body
    assert "for it in range(int(n_iter))" in body


def test_verify_call_site_refuses_a_search_class():
    from rebaseguard_p8r.addressing import CAL_SEARCH_ARL0
    with pytest.raises(PermissionError):
        CAL._verify(experiment=CAL_SEARCH_ARL0, family="gaussian",
                    threshold=520.0, batch=7, target=465.5)


def test_executed_budget_equals_declared_budget():
    cal = payload_or_skip("results/sr_calibration.json")
    assert cal["all_budgets_match_declaration"] is True
    for r in cal["rows"]:
        if r["family"] == "gaussian":
            continue
        e, d = r["executed_budget"], r["declared_budget"]
        assert e["s1_evaluations"] == d["s1_evaluations"]
        assert e["s2_evaluations"] == d["s2_evaluations"]
        assert e["s1_cycles_per_evaluation"] == d["s1_cycles_per_evaluation"]
        assert e["s2_cycles_per_evaluation"] == d["s2_cycles_per_evaluation"]
        assert e["verification_cycles"] == d["verification_cycles"]


def test_outcomes_are_from_the_frozen_set():
    cal = payload_or_skip("results/sr_calibration.json")
    allowed = {"ACCEPTED_VERIFY_1", "ACCEPTED_VERIFY_2", "CALIBRATION_FAILED",
               "FROZEN_NOT_RECALIBRATED"}
    for r in cal["rows"]:
        assert r["outcome"] in allowed


def test_no_family_was_retried_more_than_once():
    cal = payload_or_skip("results/sr_calibration.json")
    for r in cal["rows"]:
        assert len(r["retry_trace"]) in (0, CAL_S2_ITERATIONS)
        # exactly one or two acceptance evaluations, never three
        assert r["executed_budget"]["verification_evaluations"] in (1, 2)


def test_a_failed_calibration_yields_no_threshold():
    cal = payload_or_skip("results/sr_calibration.json")
    for r in cal["rows"]:
        if r["outcome"] == "CALIBRATION_FAILED":
            assert r["threshold"] is None
            assert r["accepted_by"] is None


def test_accepted_thresholds_meet_the_frozen_tolerance_on_their_holdout():
    cal = payload_or_skip("results/sr_calibration.json")
    for r in cal["rows"]:
        if r["outcome"] not in ("ACCEPTED_VERIFY_1", "ACCEPTED_VERIFY_2"):
            continue
        v = r["verify_2"] if r["outcome"] == "ACCEPTED_VERIFY_2" \
            else r["verify_1"]
        assert v["accepted"] is True
        assert v["relative_error"] <= CAL_TOLERANCE
        assert v["threshold"] == r["threshold"]
