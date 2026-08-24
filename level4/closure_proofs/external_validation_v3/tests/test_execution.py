from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[2]
sys.path.insert(0, str(BASE / "src"))

from config import EXECUTION, PROTOCOL


def load(name: str) -> dict:
    return json.loads((BASE / name).read_text())


def test_execution_configuration_hash_is_frozen():
    expected = load("results/execution_hash.json")["execution_config_sha256"]
    actual = hashlib.sha256((BASE / "results/execution_config.json").read_bytes()).hexdigest()
    assert actual == expected
    assert load("results/execution_hash.json")["confirmatory_outcomes_existed_when_frozen"] is False


def test_both_p0_only_gates_pass():
    gates = load("results/gates.json")
    assert gates["all_primary_pass"] is True
    assert gates["confirmatory_outcomes_generated"] is False
    assert {task: row["status"] for task, row in gates["tasks"].items()} == {
        "metropt": "PASS", "retail": "PASS"
    }


def test_dataset_eligibility_is_mechanical():
    gates = load("results/gates.json")
    assert all(row["gates"]["dataset"] for row in gates["tasks"].values())
    assert gates["tasks"]["metropt"]["dataset_audit"]["raw_rows"] == 1516948
    assert gates["tasks"]["retail"]["dataset_audit"]["raw_rows"] == 1067371
    assert all(row["dataset_audit"]["malformed_selected_rows"] == 0
               for row in gates["tasks"].values())


def test_splits_are_chronological_and_exact():
    gates = load("results/gates.json")["tasks"]
    assert gates["metropt"]["split"] == {
        "train": [0, 3312], "calibration": [3312, 8280], "evaluation": [8280, 16561]
    }
    assert gates["retail"]["split"] == {
        "train": [0, 3510], "calibration": [3510, 8775], "evaluation": [8775, 17550]
    }


def test_leakage_guards_all_pass():
    gates = load("results/gates.json")["tasks"]
    for row in gates.values():
        assert row["gates"]["leakage"] is True
        assert row["leakage"]["model_fit_source"] == "train only"
        assert row["leakage"]["scale_source"] == "train only"
        assert row["leakage"]["threshold_source"] == "calibration only"
        assert row["leakage"]["rho_source"] == "frozen protocol"
        assert row["leakage"]["no_future_features"] is True


def test_calibration_uses_fresh_policy_only():
    for row in load("results/gates.json")["tasks"].values():
        assert row["calibration"]["policy"] == "P0_fresh"
        assert row["calibration"]["status"] == "PASS"


def test_calibration_point_and_interval_gates_pass():
    for row in load("results/gates.json")["tasks"].values():
        value = row["calibration"]
        assert value["point_tolerance_pass"] is True
        assert value["target_inside_ci"] is True
        assert value["effective_block_gate_pass"] is True


def test_actual_power_floor_is_enforced_everywhere():
    floor = PROTOCOL["power"]["minimum_effective_blocks"]
    assert floor == 40
    for row in load("results/gates.json")["tasks"].values():
        power = row["actual_power"]
        assert min(power["calibration_cycle_blocks"], power["natural_blocks"],
                   power["event_blocks"]) >= floor


def test_actual_calibration_values_are_finite_and_near_target():
    for row in load("results/gates.json")["tasks"].values():
        value = row["calibration"]
        assert value["threshold"] > 0
        assert abs(value["achieved"]["mean"] / value["target_arl"] - 1) <= 0.1


def test_model_and_scale_are_train_owned():
    for row in load("results/gates.json")["tasks"].values():
        assert row["model"]["kind"] == "ridge"
        assert row["model"]["lambda"] == 1.0
        assert row["model"]["fit_source"] == "train only"
        assert row["train_residual_scale"] > 0


def test_rho_and_interventions_remain_frozen():
    assert PROTOCOL["policies"]["P2_rebaseguard"] == 0.029796
    assert [row["id"] for row in PROTOCOL["interventions"]] == [
        "STEP_0.5", "STEP_1.0", "STEP_2.0", "GRADUAL_1.0", "RECURRING_1.0"
    ]


def test_event_grid_inputs_are_outcome_blind():
    assert PROTOCOL["events"]["count"] == 240
    assert EXECUTION["events"]["task_seeds"] == {"metropt": 20270111, "retail": 20270112}


def test_no_confirmatory_result_exists_at_gate_checkpoint():
    tree = subprocess.check_output([
        "git", "ls-tree", "-r", "--name-only", "07e2fb7",
        "level4/closure_proofs/external_validation_v3/results",
    ], cwd=ROOT, text=True)
    assert "_confirmatory.json" not in tree


def test_raw_archives_are_gitignored():
    result = subprocess.run(["git", "check-ignore", str(BASE / "data_cache/metropt.zip")],
                            cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0


def test_execution_preserves_v2_tree():
    expected = load("results/historical_hashes.json")["trees"][
        "level4/closure_proofs/external_validation_v2"
    ]
    actual = subprocess.check_output([
        "git", "rev-parse", "HEAD:level4/closure_proofs/external_validation_v2"
    ], cwd=ROOT, text=True).strip()
    assert actual == expected
