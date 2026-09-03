"""R8 binding certification invariants.  Preserves the prototype FAIL."""
from __future__ import annotations
import json
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
B1 = json.loads((NS / "results" / "r8_b1_resolvent.json").read_text())
B2 = json.loads((NS / "results" / "r8_b2_sweep.json").read_text())
PR = json.loads((NS / "results" / "r8_sr_prototype.json").read_text())
SPEC = (NS / "compute_optimization_r8_sr_certification" / "R8_BINDING_SPEC.md").read_text()


def test_b1_resolvent_bounds_are_inside_frozen_budgets():
    assert B1["e=1/4"]["C"] <= 1000 and B1["e=1/4"]["converged"]
    assert B1["e=0"]["C"] <= 3000 and B1["e=0"]["converged"]


def test_b1_cell_construction_nonconvergence_is_recorded():
    """Negative result preserved: the frozen cell-mass route does not converge."""
    assert B1["cell[0.24,0.26]"]["converged"] is False
    assert B1["cell[0.24,0.26]"]["q"] == 1.0


def test_b2_worst_meets_the_unweakened_threshold():
    assert B2["worst"] <= 1e-2
    assert B2["grid"] == 1024 and B2["cells"] == 1024 * 1024


def test_b2_improvement_over_the_historical_enclosure():
    assert 6.736713e4 / B2["worst"] >= 1e6


def test_grid_deviation_is_disclosed_not_silent():
    assert "DISCLOSED DEVIATION" in SPEC and "1024x1024, not `256x256`" in SPEC
    import re
    assert re.search(r"threshold `<= 1e-2` is\s+\*\*not\*\* weakened", SPEC)


def test_f3_failure_was_predicted_before_the_run():
    assert "PREDICTED FAIL on F3" in SPEC
    assert "202.6x" in SPEC


def test_prototype_fail_is_preserved():
    assert PR["verdict"] == "FAIL"
    assert set(PR["failed"]) == {"F3_half_width", "F7_cpu"}
    assert PR["criteria"]["F3_half_width"]["value"] > 0.2


def test_prototype_is_mc_consistent_despite_failing():
    assert PR["criteria"]["F2_mc_consistent"]["pass"] is True


def test_panel_and_softplus_freedom_preserved():
    assert PR["criteria"]["F4_z_panels"]["count"] == 0
    assert PR["criteria"]["F5_softplus"]["count"] == 0


def test_every_prototype_input_traces_to_a_binding_output():
    i = PR["inputs"]
    assert abs(i["C_SR_cell"] - 216.963) < 1e-6
    assert abs(i["delta"] - B2["worst"]) < 1e-15
    assert PR["checkpoint_j"] == "55c5f1de9eb07a855948f92215b38a24b8321c5d"
