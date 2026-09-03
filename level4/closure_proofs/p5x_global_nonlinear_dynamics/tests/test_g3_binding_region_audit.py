"""G3 consumer-binding-region audit invariants.  Pre-freeze; nothing frozen."""
from __future__ import annotations
import json, subprocess
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
ROOT = NS.parents[2]
R = json.loads((NS / "g3_binding_region_audit" / "audit_results.json").read_text())


def test_nothing_binding_or_historical_changed():
    assert R["next_binding_checkpoint"] == "NOT_CREATED"
    assert R["historical_r8_mutated"] is False
    assert R["criterion_weakened"] is False and R["production_run"] is False


def test_cover_matches_the_frozen_scope_document():
    out = subprocess.run(
        ["git", "show", "db0781ed79851ca55af788731a47a0f4dda1d9c6:"
         "level4/closure_proofs/p5x_global_nonlinear_dynamics/FROZEN_SCOPE.md"],
        cwd=ROOT, capture_output=True, text=True, check=True).stdout
    assert "`e_far = 12`" in out
    assert R["cover"]["e_far"] == 12


def test_R_at_zero_is_exact_from_P5_T3():
    out = subprocess.run(
        ["git", "show", "HEAD:level4/closure_proofs/p5x_global_nonlinear_dynamics/FROZEN_THEOREM.md"],
        cwd=ROOT, capture_output=True, text=True, check=True).stdout
    assert "`R` odd, `S` even, `R(0) = 0`" in out
    assert R["exact_facts"]["R_at_zero"] == 0.0


def test_binding_locations_do_not_coincide():
    b = R["binding_locations"]
    assert b["they_coincide"] is False
    assert b["absR_max"]["e"] != b["C_SR_max"]["e"]
    assert b["peak_grid_requirement"]["e"] not in (b["absR_max"]["e"], b["C_SR_max"]["e"])


def test_allowed_half_width_grows_as_R_shrinks():
    """The consumer margin, not a uniform half-width, is what matters."""
    a = {x["e"]: x for x in R["adaptive_requirement"]}
    assert a[0.0]["allowed_hw"] > 1.9        # |R(0)| = 0
    assert a[0.25]["allowed_hw"] < 0.45      # |R| near its maximum


def test_grid_requirement_collapses_in_the_far_field():
    a = {x["e"]: x for x in R["adaptive_requirement"]}
    assert a[2.0]["grid"] < 20 and a[1.0]["grid"] < 50
    assert a[0.10]["grid"] == max(x["grid"] for x in R["adaptive_requirement"])


def test_near_zero_theorem_is_optional_not_a_dependency():
    n = R["near_zero"]
    assert n["is_dependency"] is False
    assert R["cost"]["total_without_near_zero_theorem"] < 500


def test_cost_is_strong_and_much_cheaper_than_uniform():
    c = R["cost"]
    assert c["cost_class"] == "STRONG"
    assert 30 < c["total_cpu_hours"] <= 100
    assert c["speedup_vs_uniform_1024"] > 20


def test_all_pre_freeze_conditions_pass_and_spec_is_only_drafted():
    p = R["pre_freeze"]
    assert all(p[k] == "PASS" for k in
               ("B1_consumer_confirmed", "B2_full_cover_route", "B3_cost_le_500",
                "B4_no_historical_change", "B5_no_new_candidate"))
    assert p["ready_to_freeze"] is True
    assert p["successor_spec"] == "DRAFTED_NOT_CREATED"


def test_caveats_are_recorded():
    assert len(R["caveats"]) >= 3
    assert any("ADAPTIVE" in c for c in R["caveats"])
