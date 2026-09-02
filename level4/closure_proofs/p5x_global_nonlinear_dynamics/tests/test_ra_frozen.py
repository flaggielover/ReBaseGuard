"""Checkpoint-B (R-A) tests.  These must not reveal any R-A production result."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
RA = NS / "certified_method_repair_ra"
ERR = NS / "errata"


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_d1_erratum_exists_and_is_classified():
    doc = json.loads((ERR / "D1_MACHINE_SUMMARY.json").read_text())
    assert doc["erratum_id"] == "D1"
    assert doc["classification"] == "CERTIFIER_DOMAIN_ERRATUM"
    assert doc["governance_route"] == "A"
    assert doc["escalation_required"] is False
    assert doc["frozen_bytes_modified"] is False
    assert doc["true_b_SR_expression"] == "log(1 + A)"
    assert doc["affects"]["p5_original"] is False
    assert doc["affects"]["cusum_path"] is False
    assert doc["affects"]["sr_certified_path"] is True
    assert doc["downstream_core_threat"] == "NONE"


def test_frozen_theorem_still_carries_the_defective_text():
    assert "b_SR = log A" in (NS / "FROZEN_THEOREM.md").read_text()


def test_first_failure_is_preserved_verbatim():
    gate = json.loads((NS / "results" / "stop_gate_cell.json").read_text())
    assert gate["stop_gate"]["verdict"] == "FAIL"
    assert gate["stop_gate"]["frozen_threshold"] == 0.2
    assert gate["achieved_half_width"] > 1e40
    assert "STOP_GATE            = FAIL" in (NS / "STOP_GATE.md").read_text()


def test_ra_spec_keeps_the_cell_and_threshold():
    spec = (RA / "RA_FROZEN_SPEC.md").read_text()
    assert "e-cell   = [0.24, 0.26]" in spec
    assert "achieved half-width <= 0.2   ->  RA_STOP_GATE = PASS" in spec
    assert "There is no retry ladder" in spec
    assert "not** invoked in\nthe same session" in spec.replace("\r", "")


def test_ra_audit_does_not_pretend_ra_predated_the_failure():
    audit = (RA / "RA_FEASIBILITY_AUDIT.md").read_text()
    assert "R-A was identified only\n*after* that failure" in audit
    assert "debugging step" in audit.replace("\n", " ")


def test_ra_digests_match_files():
    for name, base in (("RA_PROTOCOL_DIGEST.json", RA), ("RA_SOURCE_MANIFEST.json", RA)):
        doc = json.loads((base / name).read_text())
        for rel, rec in doc["files"].items():
            assert _sha(base / rel) == rec["sha256"], rel


def test_no_ra_production_result_at_the_anchor():
    forbidden = ["ra_stop_gate.json", "ra_selftest.json", "ra_diagnostics.json"]
    present = [f for f in forbidden if (NS / "results" / f).exists()]
    assert not present, f"R-A results must not exist at the anchor: {present}"


def test_ra_is_cusum_only_and_cites_the_erratum():
    spec = (RA / "RA_FROZEN_SPEC.md").read_text()
    assert "R-A′ is CUSUM-only" in spec
    assert "b_SR = log(1 + A)" in spec


def test_no_lean_sources_yet():
    assert not list(NS.rglob("*.lean"))
