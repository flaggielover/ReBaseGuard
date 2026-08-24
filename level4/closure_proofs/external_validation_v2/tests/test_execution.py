from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[2]
sys.path.insert(0, str(BASE / "src"))

from config import EXECUTION, POLICIES, PROTOCOL  # noqa: E402
from confirmatory import centered_mean, event_grid, inject  # noqa: E402
from inference import mean_summary, paired_ratio  # noqa: E402
from model import build, split  # noqa: E402
from monitor import run_monitor  # noqa: E402


def test_execution_configuration_hash_is_frozen():
    record = json.loads((BASE / "results/execution_hash.json").read_text())
    actual = hashlib.sha256((BASE / record["file"]).read_bytes()).hexdigest()
    assert actual == record["sha256"]


def test_chronological_split_is_exact_30_20_50():
    train, calibration, evaluation = split(100)
    assert (train.start, train.stop) == (0, 30)
    assert (calibration.start, calibration.stop) == (30, 50)
    assert (evaluation.start, evaluation.stop) == (50, 100)


def test_ridge_fit_is_independent_of_evaluation_targets():
    @dataclass
    class Data:
        task: str
        timestamps: np.ndarray
        X: np.ndarray
        y: np.ndarray
        audit: dict
    x = np.arange(200.0)[:, None]
    y = 2 * x[:, 0] + 1
    first = build(Data("synthetic", np.arange(200), x, y, {}))
    y2 = y.copy()
    y2[100:] += 1e6
    second = build(Data("synthetic", np.arange(200), x, y2, {}))
    assert first.model == second.model
    assert first.scale == second.scale


def test_only_policy_parameter_is_rho():
    assert POLICIES == {"P0_fresh": 0.0, "P1_full_reuse": 1.0,
                        "P2_rebaseguard": 0.029796}
    assert PROTOCOL["detector"] == {"kind": "two-sided-inclusive-CUSUM", "k": 0.5, "m": 20}


def test_monitor_consumes_same_fresh_block_for_every_policy():
    stream = np.r_[np.zeros(10), np.full(5, 4.0), np.zeros(100)]
    runs = [run_monitor(stream, scale=1, threshold=2, rho=rho, r0=0, m=5)
            for rho in (0.0, 1.0, 0.029796)]
    first_alarm = {run.cycles[0].alarm for run in runs}
    second_start = {run.cycles[1].start for run in runs if len(run.cycles) > 1}
    assert len(first_alarm) == 1
    assert second_start == {next(iter(first_alarm)) + 1 + 5}


def test_event_grid_is_deterministic_unique_and_has_frozen_count():
    a = event_grid("metro", 25000)
    b = event_grid("metro", 25000)
    assert np.array_equal(a, b)
    assert a.size == 120 and np.all(np.diff(a) > 0)


def test_intervention_classes_are_deterministic():
    base = np.zeros(300)
    assert np.all(inject(base, 10, "STEP_1.0", 2.0, 1)[10:] == 2)
    gradual = inject(base, 10, "GRADUAL_1.0", 1.0, 1)
    assert gradual[10] == 0 and gradual[34] == 1
    recurring = inject(base, 10, "RECURRING_1.0", 1.0, 1)
    assert recurring[10] == 1 and recurring[58] == 0 and recurring[106] == 1


def test_centered_oracle_is_measurement_only_and_expected_length():
    values = np.arange(20.0)
    oracle = centered_mean(values, 4)
    assert oracle.shape == values.shape
    assert np.isnan(oracle[:2]).all() and np.isnan(oracle[-1:]).all()
    assert oracle[2] == np.mean(values[:4])


def test_weekly_bootstrap_effective_blocks_are_conservative():
    summary = mean_summary(np.arange(100.0), block=2, draws=100, seed=1)
    assert summary["effective_blocks"] == 50


def test_event_bootstrap_is_paired():
    x = np.arange(1, 121.0)
    ratio = paired_ratio(2 * x, x, block=6, draws=100, seed=1)
    assert ratio["ratio"] == 2
    assert ratio["effective_blocks"] == 20


def test_censor_cap_and_warmup_are_frozen():
    assert EXECUTION["events"]["administrative_cap_target_arl"] == 4
    assert EXECUTION["events"]["warmup_target_arl"] == 3


def test_natural_and_event_block_floors_are_frozen():
    assert PROTOCOL["power"]["minimum_effective_blocks"] == 20
    assert EXECUTION["bootstrap"]["natural_moving_block_weeks"] == 2
    assert EXECUTION["bootstrap"]["event_block"] == 6


def test_all_confirmatory_artifacts_exist_and_no_pilot_artifact_exists():
    assert not list((BASE / "results").glob("*pilot*"))
    assert {path.name for path in (BASE / "results").glob("task_*_confirmatory.json")} == {
        "task_household_confirmatory.json", "task_metro_confirmatory.json",
        "task_beijing_confirmatory.json",
    }


def test_raw_cache_is_gitignored():
    ignored = (BASE / ".gitignore").read_text().splitlines()
    assert "data/_cache/" in ignored


def test_persisted_pre_outcome_gates_all_pass_without_backup():
    gates = json.loads((BASE / "results/gates.json").read_text())
    assert gates["confirmatory_outcomes_generated"] is False
    assert gates["all_primary_pass"] is True
    assert set(gates["tasks"]) == {"household", "metro", "beijing"}
    assert all(row["status"] == "PASS" for row in gates["tasks"].values())


def test_actual_power_floor_and_calibration_acceptance_are_enforced():
    gates = json.loads((BASE / "results/gates.json").read_text())
    for row in gates["tasks"].values():
        assert min(row["actual_power"][key] for key in
                   ("natural_week_blocks", "event_blocks", "calibration_cycle_blocks")) >= 20
        calibration = row["calibration"]
        assert calibration["point_tolerance_pass"]
        assert calibration["target_inside_ci"]
        assert calibration["effective_block_gate_pass"]
