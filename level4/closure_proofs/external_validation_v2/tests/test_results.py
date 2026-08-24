from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[2]
PY = ROOT / "level4/.venv/bin/python"
sys.path.insert(0, str(BASE / "src"))

from analyze import analyze_task  # noqa: E402
from decision import derive  # noqa: E402
from summarize import build_summary  # noqa: E402

TASKS = ("household", "metro", "beijing")


def load(relative: str):
    return json.loads((BASE / relative).read_text())


def test_confirmatory_outputs_are_frozen_protocol_and_matched_streams():
    protocol_hash = load("results/protocol_hash.json")["combined_sha256"]
    for task in TASKS:
        raw = load(f"results/task_{task}_confirmatory.json")
        assert raw["evidence_status"] == "CONFIRMATORY"
        assert raw["protocol_hash"] == protocol_hash
        assert raw["matched_streams"] is True


def test_every_task_has_120_outcome_blind_event_locations():
    for task in TASKS:
        raw = load(f"results/task_{task}_confirmatory.json")
        grid = raw["events"]["relative_grid"]
        assert len(grid) == 120
        assert all(left < right for left, right in zip(grid, grid[1:]))


def test_all_policies_retain_every_event_and_condition():
    conditions = {"STEP_0.5", "STEP_1.0", "STEP_2.0", "GRADUAL_1.0", "RECURRING_1.0"}
    for task in TASKS:
        policies = load(f"results/task_{task}_confirmatory.json")["events"]["policies"]
        assert set(policies) == {"P0_fresh", "P1_full_reuse", "P2_rebaseguard"}
        for row in policies.values():
            assert len(row["matched_in_control_wait"]) == 120
            assert set(row["interventions"]) == conditions
            for outcome in row["interventions"].values():
                assert len(outcome["delay"]) == len(outcome["censored"]) == 120


def test_natural_endpoints_meet_actual_block_floor_for_every_policy():
    for task in TASKS:
        raw = load(f"results/task_{task}_confirmatory.json")
        assert raw["natural"]["full_week_blocks"] >= 40
        for policy in raw["natural"]["policies"].values():
            assert len(policy["E2_weekly"]) == len(policy["E3_weekly"]) == raw["natural"]["full_week_blocks"]


def test_task_analyses_are_mechanically_reproducible():
    gates = load("results/gates.json")
    for task in TASKS:
        assert analyze_task(task, gates) == load(f"results/task_{task}_analysis.json")


def test_decision_is_mechanically_reproducible():
    assert derive() == load("results/decision.json")


def test_final_summary_is_mechanically_reproducible():
    assert build_summary() == load("results/summary.json")


def test_frozen_campaign_result_is_partial_one_of_three():
    decision = load("results/decision.json")
    assert decision["decision"] == "EXTERNAL-VALIDATION-V2-PARTIAL"
    assert decision["tasks_supporting_H2_4"] == 1
    assert decision["task_support"] == {"household": True, "metro": False, "beijing": False}
    assert decision["global_requirement"] == "PARTIAL"


def test_reference_distortion_supported_in_all_tasks_but_package_only_household():
    for task in TASKS:
        assert load(f"results/task_{task}_analysis.json")["H2_1"]["supported"]
    assert load("results/task_household_analysis.json")["H2_4"]["supported"]
    assert not load("results/task_metro_analysis.json")["H2_4"]["supported"]
    assert not load("results/task_beijing_analysis.json")["H2_4"]["supported"]


def test_null_and_unfavourable_routes_are_retained():
    metro = load("results/task_metro_analysis.json")
    assert metro["E3"]["P1_over_P2"]["ratio"] < 1
    assert not metro["H2_2"]["supported"]
    for task in ("metro", "beijing"):
        assert not load(f"results/task_{task}_analysis.json")["H2_3"]["supported"]


def test_no_strong_rebaseguard_safety_contradiction():
    decision = load("results/decision.json")
    assert decision["strong_safety_contradictions"] == []


def test_historical_stage_e_and_global_status_are_not_recomputed():
    decision = load("results/decision.json")
    assert decision["historical_stage_e"] == "STAGE-E-PARTIAL"
    assert decision["historical_stage_e_support"] == "0/3 H-E5"
    assert decision["historical_stage_f"] == "LEVEL-4-PARTIAL"
    assert decision["post_closure_global_verdict"] == "LEVEL-4-PARTIAL"
    assert decision["global_reaudit_performed"] is False


def test_reports_are_byte_stable():
    completed = subprocess.run([str(PY), str(BASE / "src/reports.py"), "--check"],
                               cwd=ROOT, capture_output=True, text=True)
    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_four_required_figures_exist_and_are_nonempty():
    expected = {
        "figure_a_reference_distortion.png", "figure_b_normalized_response.png",
        "figure_c_delay_alert_burden.png", "figure_d_task_support.png",
    }
    assert {path.name for path in (BASE / "figures").glob("*.png")} == expected
    assert all((BASE / "figures" / name).stat().st_size > 20_000 for name in expected)


def test_figure_generation_is_byte_stable():
    before = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
              for path in (BASE / "figures").glob("*.png")}
    subprocess.run([str(PY), str(BASE / "src/figures.py")], cwd=ROOT, check=True,
                   capture_output=True, text=True)
    after = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
             for path in (BASE / "figures").glob("*.png")}
    assert before == after


def test_no_backup_activation_or_task_replacement():
    selection = load("results/dataset_selection.json")
    assert selection["primary_tasks"] == ["household", "metro", "beijing"]
    assert set(load("results/gates.json")["tasks"]) == set(selection["primary_tasks"])


def test_final_report_names_exact_remaining_scientific_blocker():
    text = " ".join((BASE / "FINAL_REPORT.md").read_text().split())
    assert "Only one of three tasks supports the full H2-4 package" in text
    assert "scientific partial result, not a documentation failure" in text
