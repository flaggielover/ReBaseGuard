from __future__ import annotations

import json
import os
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[2]
sys.path.insert(0, str(BASE / "src"))

import adversarial
import reports
import reproduction


def load(name: str) -> dict:
    return json.loads((BASE / name).read_text())


def test_summary_contains_all_eight_cross_campaign_tasks():
    assert len(load("results/summary.json")["cross_campaign_tasks"]) == 8


def test_summary_contains_three_stage_e_tasks():
    rows = load("results/summary.json")["cross_campaign_tasks"]
    assert sum(row["campaign"] == "Stage E" for row in rows) == 3


def test_summary_contains_three_v2_tasks():
    rows = load("results/summary.json")["cross_campaign_tasks"]
    assert sum(row["campaign"] == "V2" for row in rows) == 3


def test_summary_contains_two_v3_tasks():
    rows = load("results/summary.json")["cross_campaign_tasks"]
    assert sum(row["campaign"] == "V3" for row in rows) == 2


def test_cross_campaign_count_is_three_without_pooling():
    decision = load("results/scientific_decision.json")
    assert decision["cross_campaign_success_count"] == 3
    assert load("results/protocol.json")["aggregation"]["no_statistical_pooling"] is True


def test_original_requirement_is_mechanically_closed():
    assert load("results/scientific_decision.json")["original_external_validation_requirement"] == "CLOSED"


def test_historical_global_verdict_is_not_recomputed():
    decision = load("results/scientific_decision.json")
    assert decision["historical_global_verdict"] == "LEVEL-4-PARTIAL"
    assert decision["global_reaudit_performed"] is False


def test_five_figures_exist():
    assert len(list((BASE / "figures").glob("*.png"))) == 5


def test_all_figures_are_nonempty_pngs():
    assert all(path.read_bytes().startswith(b"\x89PNG") and path.stat().st_size > 10_000
               for path in (BASE / "figures").glob("*.png"))


def test_figure_generator_reads_summary_only():
    source = (BASE / "src/figures.py").read_text()
    assert "results/summary.json" in source
    assert "confirmatory.json" not in source and "analysis.json" not in source


def test_report_generator_has_five_mirrors():
    assert set(reports.outputs(load("results/summary.json"))) == {
        "RESULTS.md", "CROSS_CAMPAIGN_AGGREGATION.md", "CALIBRATION_AUDIT.md",
        "ADVERSARIAL_AUDIT.md", "FINAL_REPORT.md",
    }


def test_results_report_preserves_unfavorable_route_b():
    text = (BASE / "RESULTS.md").read_text()
    assert "Route B medium-step response=NO" in text
    assert "unfavorable" in text


def test_results_report_preserves_metro_recurring_cap():
    text = (BASE / "RESULTS.md").read_text()
    assert "32 observed hours" in text and "48-hour recurring on-phase" in text


def test_cross_campaign_report_preserves_stage_e_and_v2():
    text = (BASE / "CROSS_CAMPAIGN_AGGREGATION.md").read_text()
    assert "Stage E remains 0/3" in text and "V2 remains 1/3" in text


def test_cross_campaign_report_states_no_pooling():
    assert "estimates and samples are never\npooled" in (BASE / "CROSS_CAMPAIGN_AGGREGATION.md").read_text()


def test_calibration_report_contains_both_thresholds():
    text = (BASE / "CALIBRATION_AUDIT.md").read_text()
    gates = load("results/gates.json")
    assert all(f"{row['calibration']['threshold']:.12f}" in text for row in gates["tasks"].values())


def test_final_report_has_explicit_claim_boundary():
    text = (BASE / "FINAL_REPORT.md").read_text()
    assert "does not establish production validation" in text


def test_final_report_preserves_historical_verdicts():
    text = (BASE / "FINAL_REPORT.md").read_text()
    assert "STAGE-E-PARTIAL" in text and "EXTERNAL-VALIDATION-V2-PARTIAL" in text
    assert "LEVEL-4-PARTIAL" in text


def test_reproducer_science_artifact_set_has_twelve_files():
    assert len(reproduction.GENERATED) == 12
    assert all((BASE / name).exists() for name in reproduction.GENERATED)


def test_reproducer_excludes_self_referential_record():
    assert "results/reproduction.json" not in reproduction.GENERATED
    assert "results/decision.json" not in reproduction.GENERATED


def test_adversarial_suite_defines_exactly_twenty_five_ids():
    source = (BASE / "src/adversarial.py").read_text()
    assert {f'A{i}' for i in range(1, 26)} == set(__import__("re").findall(r'add\(checks, "(A\d+)"', source))


def test_repository_verifier_integrates_v3_suite():
    text = (ROOT / "scripts/verify_level_4.sh").read_text()
    assert "external-validation V3 suite" in text
    assert "external_validation_v3/tests" in text


def test_reproduce_script_checks_all_required_gates():
    text = (BASE / "reproduce.sh").read_text()
    for token in ("integrity.py", "acquire.py", "reproduction.py", "pytest",
                  "adversarial.py", "verify_level_4.sh", "reports.py"):
        assert token in text


def test_reproduce_script_is_executable():
    assert os.access(BASE / "reproduce.sh", os.X_OK)


def test_no_v4_stop_rule_is_preserved():
    assert load("results/scientific_decision.json")["stop_rule"] == "NO_V4"
