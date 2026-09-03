"""F3 provenance audit invariants.  Governance only; nothing frozen or changed."""
from __future__ import annotations
import json
import subprocess
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
ROOT = NS.parents[2]
R = json.loads((NS / "f3_provenance_audit" / "audit_results.json").read_text())


def test_nothing_historical_was_changed():
    assert R["historical_r8_mutated"] is False
    assert R["f3_changed"] is False
    assert R["next_binding_checkpoint"] == "NOT_CREATED"
    assert R["verdicts"]["r8_remains_FAIL"] is True


def test_f3_provenance_is_checkpoint_a_and_pre_result():
    p = R["provenance"]
    assert p["first_commit"] == "db0781ed79851ca55af788731a47a0f4dda1d9c6"
    assert p["pre_result"] is True


def test_the_quoted_rationale_really_is_in_checkpoint_a():
    """Provenance must come from the commit, not from a later summary."""
    out = subprocess.run(
        ["git", "show", "db0781ed79851ca55af788731a47a0f4dda1d9c6:"
         "level4/closure_proofs/p5x_global_nonlinear_dynamics/CERTIFICATE_PLAN.md"],
        cwd=ROOT, capture_output=True, text=True, check=True).stdout
    assert "central engineering bet" in out
    assert "the required half-width for `P5X-T4` is `< 0.2`" in out


def test_g3_pass_condition_is_r_max_lt_2():
    out = subprocess.run(
        ["git", "show", "db0781ed79851ca55af788731a47a0f4dda1d9c6:"
         "level4/closure_proofs/p5x_global_nonlinear_dynamics/FROZEN_GATES.md"],
        cwd=ROOT, capture_output=True, text=True, check=True).stdout
    assert "R_max < 2" in out.replace("\\", "")


def test_strongest_consumer_is_looser_than_f3():
    m = R["max_half_widths"]
    assert abs(m["G3_R_max_lt_2"] - (2 - 1.5903422831)) < 1e-12
    assert m["G3_R_max_lt_2"] > m["F3_as_frozen"]
    assert m["F3_strictness_vs_strongest_consumer"] > 2.0


def test_r8_certifies_sign_but_not_the_load_bearing_claim():
    r = R["r8_enclosure"]
    assert r["certifies_sign"] is True
    assert r["certifies_G3"] is False and r["abs_R_max"] > 2


def test_successor_gate_still_has_teeth():
    """A re-specification that everything passes would be gate weakening."""
    h = {x["label"]: x for x in R["hypotheticals_diagnostic"]}
    assert any(x["G3"] is False for x in h.values())
    assert R["r8_enclosure"]["certifies_G3"] is False


def test_campaign_wide_qualification_is_recorded():
    q = R["campaign_wide_qualification"]
    assert any(row["G3"] is False for row in q["rows"])
    assert "OUT OF SCOPE" in q["conclusion"]


def test_case_and_governance_classification():
    v = R["verdicts"]
    assert v["audit_case"] == "B" and v["governance_class"] == "G2"
    assert v["f3_mathematically_necessary"] is False
    assert v["successor_respec_allowed"] is True
