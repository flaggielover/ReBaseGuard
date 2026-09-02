"""Gate semantics: what each gate class may and may not do.

The frozen split is the point of the repair.  Integrity gates must pass.
Scientific questions must be *resolved*, never forced true.  A falsified
hypothesis is a negative scientific result and does not, by itself, fail the
campaign.
"""
import json

import pytest

from rebaseguard_p8r import config as CFG
from conftest import payload_or_skip

ADMISSIBLE = {"SUPPORTED", "REJECTED", "INCONCLUSIVE", "OUT_OF_SCOPE"}
INTEGRITY_GATES = tuple(f"I{i}" for i in range(1, 14))
MANDATORY_QUESTIONS = tuple(
    ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S7D", "S7F", "S7X", "S8", "S9",
     "S10", "S11", "S12", "S13", "S14", "S15", "S16", "S17"])


def test_every_mandatory_question_is_resolved_admissibly():
    res = payload_or_skip("results/scientific_resolution.json")
    for q in MANDATORY_QUESTIONS:
        assert q in res["summary"], f"{q} was not evaluated"
        assert res["summary"][q] in ADMISSIBLE, (q, res["summary"][q])


def test_every_question_records_the_frozen_rule_it_applied():
    res = payload_or_skip("results/scientific_resolution.json")
    for q in res["questions"]:
        assert q["frozen_rule"], q["question"]
        assert q["statistic"] is not None, q["question"]


def test_integrity_audit_reports_all_thirteen_gates():
    p = "results/integrity/integrity_audit.json"
    audit = payload_or_skip(p)
    for g in INTEGRITY_GATES:
        assert g in audit["summary"], g
    assert set(audit["summary"]) == set(INTEGRITY_GATES)


def test_no_integrity_gate_may_be_reported_as_unverifiable_and_counted_as_pass():
    audit = payload_or_skip("results/integrity/integrity_audit.json")
    n_pass = sum(1 for v in audit["summary"].values() if v == "PASS")
    assert audit["n_pass"] == n_pass
    assert audit["all_pass"] == (n_pass == len(audit["summary"]))


def test_closure_rule_is_conjunctive_over_integrity_and_resolution():
    """The frozen closure rule: CLOSED_CANDIDATE requires every integrity gate
    to PASS *and* every mandatory question to be resolved.  It never requires a
    hypothesis to be true."""
    audit = payload_or_skip("results/integrity/integrity_audit.json")
    res = payload_or_skip("results/scientific_resolution.json")
    integrity_ok = all(v == "PASS" for v in audit["summary"].values())
    resolved_ok = all(res["summary"].get(q) in ADMISSIBLE
                      for q in MANDATORY_QUESTIONS)
    verdict = payload_or_skip("results/verdict.json")
    expect = ("CLOSED_CANDIDATE" if integrity_ok and resolved_ok
              else "FAIL_CANDIDATE" if not integrity_ok
              else "PARTIAL_CANDIDATE")
    assert verdict["verdict"] == expect, (verdict["verdict"], expect)


def test_a_rejected_hypothesis_does_not_by_itself_fail_the_campaign():
    verdict = payload_or_skip("results/verdict.json")
    res = payload_or_skip("results/scientific_resolution.json")
    rejected = [q for q, s in res["summary"].items() if s == "REJECTED"]
    if rejected and verdict["verdict"] == "FAIL_CANDIDATE":
        audit = payload_or_skip("results/integrity/integrity_audit.json")
        assert not all(v == "PASS" for v in audit["summary"].values()), (
            "FAIL_CANDIDATE was reached with every integrity gate passing; "
            "a falsified hypothesis is a negative result, not a failure")


def test_frozen_thresholds_are_the_ones_the_analysis_used():
    """A threshold in the resolution record must equal the one in config."""
    res = payload_or_skip("results/scientific_resolution.json")
    by_q = {q["question"]: q for q in res["questions"]}
    assert by_q["S7"]["statistic"]["threshold"] == CFG.S7_SPREAD_MAX
    assert by_q["S7D"]["statistic"]["threshold"] == CFG.S7D_RESIDUAL_MAX
    assert by_q["S10"]["statistic"]["required"] == CFG.S10_FAMILIES_REQUIRED
    assert by_q["S5"]["frozen_rule"].find(
        f"{CFG.CAL_TOLERANCE:.1%}") >= 0


def test_extrapolation_windows_are_out_of_scope_by_construction():
    res = payload_or_skip("results/scientific_resolution.json")
    assert res["summary"]["S7X"] == "OUT_OF_SCOPE"
    by_q = {q["question"]: q for q in res["questions"]}
    for row in by_q["S7X"]["statistic"]["rows"]:
        assert row["m"] in CFG.EXTRAPOLATION_M
