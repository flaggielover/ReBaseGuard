from __future__ import annotations

import inspect
import json
from pathlib import Path

import decision
import figures
from config import REGIMES, SHIFTS

BASE = Path(__file__).resolve().parents[1]
RESULTS = BASE / "results"


def load_if(name: str):
    path = RESULTS / name
    return json.loads(path.read_text()) if path.exists() else None


def test_final_decision_is_generator_owned_and_mechanical_if_present():
    got = load_if("decision.json")
    if got is None:
        return
    assert got == decision.build()
    assert got["generator_owned"] is True
    assert got["scoped_verdict"] in {
        "L4R06-POLICY-CLOSED", "L4R06-POLICY-PARTIAL", "L4R06-POLICY-FAILED"}
    all_pass = all(row["status"] == "PASS" for row in got["criteria"])
    assert (got["scoped_verdict"] == "L4R06-POLICY-CLOSED") == all_pass
    assert got["same_requirement_mapping"] == (got["scoped_verdict"] == "L4R06-POLICY-CLOSED")
    assert got["historical_C6_preserved"] is True
    assert got["l4r12_touched"] is False


def test_final_adversarial_has_exactly_23_checks_if_present():
    got = load_if("adversarial_final.json")
    if got is None:
        return
    assert got["n_checks"] == got["n_passed"] == 23
    assert got["status"] == "PASS"
    assert [row["id"] for row in got["checks"]] == [f"A{i}" for i in range(1, 24)]


def test_first_adversarial_run_is_preserved_if_present():
    got = load_if("adversarial_first.json")
    if got is None:
        return
    assert got["n_checks"] == 23
    assert len(got["checks"]) == 23


def test_every_figure_is_generated_from_final_scientific_json_only_if_present():
    manifest = load_if("figure_manifest.json")
    if manifest is None:
        return
    assert manifest["source"] == "results/scientific_findings.json"
    assert set(manifest["files"]) == set(figures.NAMES)
    source = inspect.getsource(figures)
    assert "load_cell" not in source and "CELLS" not in source
    assert all((BASE / "figures" / name).exists() for name in figures.NAMES)


def test_final_science_retains_all_conditions_and_negative_results_if_present():
    got = load_if("scientific_findings.json")
    if got is None:
        return
    assert len(got["all_cell_summaries"]) == 4 * 4 * 5
    observed = {(r["m"], r["shift"]) for r in got["all_cell_summaries"]}
    assert observed == {(m, s) for m in REGIMES for s in (0.0, *SHIFTS)}
    assert got["policy"]["point_estimate_policy_run"] is False
    assert got["policy"]["P4_run"] is False
    assert got["historical_firewall"]["historical_C6"] == "FAILED"


def test_human_reports_mirror_decision_if_present():
    got = load_if("decision.json")
    if got is None:
        return
    for name in ("RESULTS.md", "MONITORING_CONSEQUENCES.md",
                 "FAILURE_DIAGNOSES.md", "FINAL_REPORT.md"):
        assert (BASE / name).exists()
    report = (BASE / "FINAL_REPORT.md").read_text()
    assert got["scoped_verdict"] in report
    assert got["original_L4R06_current_status"] in report
    assert "Historical Stage C remains `STAGE-C-PARTIAL`" in report
    assert "L4R-12 was not touched" in report


def test_verification_and_reproduction_records_pass_if_present():
    verification = load_if("verification.json")
    reproduction = load_if("reproduction.json")
    if verification is not None:
        assert verification["status"] == "PASS"
        assert verification["pytest_pass_count"] > 0
    if reproduction is not None:
        assert reproduction["status"] == "PASS"
        assert reproduction["scientific_findings_byte_stable"]
        assert reproduction["figures_byte_stable"]
