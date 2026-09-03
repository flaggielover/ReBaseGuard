"""Final scope and disposition audit invariants.  Governance only."""
from __future__ import annotations
import json, subprocess
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
ROOT = NS.parents[2]
R = json.loads((NS / "final_scope_disposition_audit" / "audit_results.json").read_text())


def test_no_new_science_and_nothing_historical_changed():
    assert R["new_science_run"] is False and R["binding_campaign"] is False
    assert R["original_p5_mutated"] is False and R["historical_r8_mutated"] is False


def test_p5_failed_gates_quoted_from_the_adjudication():
    out = subprocess.run(
        ["git", "show", "HEAD:level4/closure_proofs/p5_nonlinear_dynamics/"
         "INDEPENDENT_ADJUDICATION.md"], cwd=ROOT,
        capture_output=True, text=True, check=True).stdout
    assert "FINAL_P5_VERDICT               = PARTIAL" in out
    assert "G3, G7, and G9 use universal language" in out
    for g in ("G3", "G4", "G7", "G9", "G20"):
        assert g in R["p5_original"]["failed_gates"]


def test_p5x_closed_requires_G3_all_cells_and_G4_two_sided():
    out = subprocess.run(
        ["git", "show", "db0781ed79851ca55af788731a47a0f4dda1d9c6:"
         "level4/closure_proofs/p5x_global_nonlinear_dynamics/FROZEN_GATES.md"],
        cwd=ROOT, capture_output=True, text=True, check=True).stdout
    assert "G3 = PROVED_ALL_CELLS" in out and "G4 = TWO_SIDED" in out
    req = R["p5x_frozen_verdict_semantics"]["closed_candidate_requires"]
    assert any("PROVED_ALL_CELLS" in x for x in req)
    assert any("TWO_SIDED" in x for x in req)


def test_closed_is_prohibited_by_the_post_hoc_test():
    p = R["post_hoc_narrowing_test"]
    assert p["would_closed_require_weakening"] is True
    assert p["closed_prohibited"] and p["closed_in_preexisting_scope_prohibited"]


def test_sr_g3_is_load_bearing_on_two_edges():
    s = R["sr_g3"]
    assert s["load_bearing"] is True
    assert "PROVED_ALL_CELLS" in s["edge_1"] and "8/8" in s["edge_2"]


def test_sr_g3_is_a_cost_limitation_not_a_mathematical_failure():
    c = R["sr_g3"]["classification"]
    assert c["MATHEMATICAL_FAILURE"] is False and c["CERTIFIER_FAILURE"] is False
    assert c["CERTIFICATION_COST_LIMITATION"] and c["RESOURCE_ENVELOPE_LIMITATION"]


def test_detector_separability_does_not_rescue_closure():
    d = R["detector_separability"]
    assert d["class"] == "PARTIAL"
    assert d["detector_limited_closure_allowed"] is False


def test_second_moment_independently_blocks_closure():
    s = R["second_moment"]
    assert s["load_bearing"] is True and s["status"] == "NOT_RUN"
    assert s["independently_blocks_closed"] is True


def test_only_one_of_four_core_obligations_is_closed():
    assert len(R["core_required"]) == 4
    assert len(R["core_closed"]) == 1 and len(R["core_open"]) == 3


def test_verdict_is_partial_case_D_with_a_stated_reason():
    v = R["verdict"]
    assert v["case"] == "D" and v["p5x"] == "PARTIAL"
    assert v["p5_scientific_line"] == "PARTIALLY_REPAIRED_BY_SUCCESSOR"
    assert "production phase never ran" in v["smallest_sufficient_reason"]


def test_no_new_load_bearing_mathematics_was_found():
    assert R["more_work"]["new_load_bearing_math_found"] is False
    assert R["level4"]["global_closure"] is False and R["level4"]["coexist"] is True
