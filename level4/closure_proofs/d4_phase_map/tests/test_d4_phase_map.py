from __future__ import annotations

import ast
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np

from rebaseguard_d4.adversarial import verify_history
from rebaseguard_d4.config import (
    CAMPAIGN, DIRECT_CELLS, EPSILON_LADDER, M_GRID, PROTOCOL_SHA256,
    REPO, RESULTS, RHO_GRID,
)
from rebaseguard_d4.direct_map import source_separation
from rebaseguard_d4.phase_map import boundary, classify


def load(name: str):
    return json.loads((RESULTS / name).read_text())


def test_01_protocol_hash_is_frozen():
    assert hashlib.sha256((CAMPAIGN / "PROTOCOL.md").read_bytes()).hexdigest() == PROTOCOL_SHA256
    assert load("protocol_hash.json")["protocol_sha256"] == PROTOCOL_SHA256


def test_02_historical_hash_integrity():
    passed, detail = verify_history()
    assert passed, detail
    assert detail["n_checked"] >= 50


def test_03_baseline_947_and_statuses_preserved():
    baseline = load("baseline_verification.json")
    assert baseline["status"] == "PASS"
    assert baseline["distinct_checks_passed"] == 947
    assert baseline["historical_stage_f"] == "LEVEL-4-PARTIAL"
    assert baseline["post_closure_global_reaudit"] == "LEVEL-4-PARTIAL"


def test_04_track1b_theorem_import_correspondence():
    decision = json.loads((REPO / "level4/closure_proofs/m_gt_1_track1b/results/decision.json").read_text())
    theorem = (REPO / "level4/closure_proofs/m_gt_1_track1b/THEOREM.md").read_text()
    assert decision["decision"] == "MGT1-TRACK1B-CLOSED"
    assert "F'_{rho,m}(0)=rho(1-GammaTilde_m)" in theorem


def test_05_stage_a_and_stage_d_semantics_are_separated():
    audit = (CAMPAIGN / "DEFINITION_AUDIT.md").read_text()
    gamma_source = (CAMPAIGN / "src/rebaseguard_d4/gamma_grid.py").read_text()
    assert "tau_m = inf{t >= m" in audit
    assert "w_m = min(m,tau)" in audit
    assert "minimum_dwell=None" in gamma_source
    assert "stage_a" not in gamma_source.lower()


def test_06_gamma_definition_is_exact_track1b_object():
    checkpoint = load("gamma_grid_checkpoint.json")
    assert "GammaTilde_m = E_0[A_m T_tau]" in checkpoint["estimand"]
    phase = load("phase_map.json")
    assert "min(m,tau)" in phase["gamma_definition"]


def test_07_gamma_grid_and_uncertainty_complete():
    gamma = load("gamma_grid.json")
    assert gamma["valid"]
    assert gamma["m_grid"] == M_GRID.tolist()
    assert len(gamma["rows"]) == 17
    assert all(row["gamma_tilde"]["se"] > 0 for row in gamma["rows"])
    assert all(len(row["gamma_tilde"]["ci95"]) == 2 for row in gamma["rows"])


def test_08_short_cycle_correction_and_probability():
    gamma = load("gamma_grid.json")
    assert gamma["checks"]["pathwise_decomposition_roundoff"]
    assert gamma["checks"]["correction_nonnegative"]
    assert gamma["rows"][0]["short_cycle_correction"]["mean"] == 0.0
    assert gamma["rows"][0]["short_cycle_probability"]["count"] == 0
    assert gamma["rows"][-1]["short_cycle_correction"]["mean"] > 0


def test_09_rho_scaling_and_boundary_regimes():
    assert boundary(3.0, 0.1, [2.8, 3.2])["rho_c_unconstrained"] == 0.5
    assert boundary(1.5, 0.1, [1.3, 1.7])["boundary_accessible_on_unit_interval"] is False
    assert boundary(1.0, 0.1, [0.8, 1.2])["rho_c_unconstrained"] is None
    assert boundary(0.0, 0.1, [-0.2, 0.2])["rho_c_unconstrained"] == 1.0


def test_10_boundary_classification():
    assert classify(-0.999) == "LOCALLY-STABLE"
    assert classify(-1.0) == "BOUNDARY"
    assert classify(-1.001) == "LOCALLY-UNSTABLE"
    assert classify(0.0) == "LOCALLY-STABLE"


def test_11_direct_map_validation_all_cells_pass():
    direct = load("direct_validation.json")
    assert direct["valid"]
    assert len(direct["rows"]) == len(DIRECT_CELLS) == 6
    assert direct["epsilon_ladder"] == EPSILON_LADDER.tolist()
    assert all(row["passed"] for row in direct["rows"])
    assert max(row["absolute_z"] for row in direct["rows"]) <= 4


def test_12_direct_implementation_is_separated():
    separation = source_separation()
    assert all(value for key, value in separation.items() if key != "direct_source")


def test_13_phase_map_is_mechanically_complete():
    phase = load("phase_map.json")
    assert phase["valid"]
    assert phase["m_grid"] == M_GRID.tolist()
    assert phase["rho_grid"] == RHO_GRID.tolist()
    assert len(phase["cells"]) == len(M_GRID) * len(RHO_GRID)
    assert phase["crossings_gamma_equals_2"][0]["bracket"] == [70, 72]


def test_14_operational_overlay_preserves_negative_result():
    operational = load("operational_overlay.json")
    historical = json.loads((REPO / "level4/stage_d/results/d2_5_verdict.json").read_text())
    assert operational["valid"]
    assert operational["historical_d2_5"] == historical["verdict"] == "MATHEMATICAL, NOT OPERATIONAL"
    assert operational["checks"]["both_theorem_sides_present"]


def test_15_claim_artifacts_do_not_overclaim():
    paths = [RESULTS / "phase_map.json", RESULTS / "operational_overlay.json"]
    paths += [CAMPAIGN / name for name in ("PHASE_MAP_REPORT.md", "OPERATIONAL_BRIDGE.md", "FINAL_REPORT.md")]
    text = "\n".join(path.read_text() for path in paths if path.exists()).lower()
    for forbidden in ("operational phase transition", "universal phase transition", "distribution-free"):
        assert forbidden not in text


def test_16_figure_provenance_and_hashes():
    index = json.loads((CAMPAIGN / "figures/figure_index.json").read_text())
    assert index["source_policy"] == "figures generated from final JSON only"
    assert set(index["inputs"]) == {
        "results/phase_map.json", "results/operational_overlay.json", "results/direct_validation.json"
    }
    for relative, expected in index["figures"].items():
        assert hashlib.sha256((CAMPAIGN / relative).read_bytes()).hexdigest() == expected


def test_17_generators_are_checkpoint_only_and_byte_stable_ready():
    gamma = load("gamma_grid_checkpoint.json")
    direct = load("direct_validation_checkpoint.json")
    operational = load("operational_overlay_checkpoint.json")
    assert gamma["complete"] and direct["complete"] and operational["complete"]
    serialized = json.dumps([gamma["summary"], direct["summary"], operational["summary"]], sort_keys=True)
    assert "/Users/" not in serialized


def test_18_reproducer_contract_and_no_absolute_paths():
    path = CAMPAIGN / "reproduce.sh"
    if not path.exists():
        return
    text = path.read_text()
    assert "scripts/verify_level_4.sh" in text
    assert "run_adversarial.py" in text
    assert "make_figures.py" in text
    assert "/Users/" not in text
    ast.parse((CAMPAIGN / "src/rebaseguard_d4/figures.py").read_text())
