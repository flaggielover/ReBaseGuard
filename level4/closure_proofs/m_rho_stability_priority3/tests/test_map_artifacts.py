"""Schema, content and determinism tests for the machine-readable map."""

from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

import pytest

from rebaseguard_p3_map import mapbuild
from rebaseguard_p3_map.classifier import classify, multiplier
from rebaseguard_p3_map.common import read_json, sha256
from rebaseguard_p3_map.config import (
    CAMPAIGN, M_GRID, PROTOCOL_SHA256, RHO_GRID,
)

MAP = CAMPAIGN / "results" / "stability_map.json"
CSV_PATH = CAMPAIGN / "results" / "stability_map.csv"
BOUNDARIES = CAMPAIGN / "results" / "boundary_table.json"
FIGURE_INDEX = CAMPAIGN / "figures" / "figure_index.json"


@pytest.fixture(scope="module")
def payload():
    return read_json(MAP)


def test_schema_and_protocol_binding(payload):
    assert payload["schema"] == "rebaseguard.p3-stability-map.v1"
    assert payload["protocol_sha256"] == PROTOCOL_SHA256
    assert read_json(BOUNDARIES)["schema"] == "rebaseguard.p3-boundary-table.v1"
    assert read_json(BOUNDARIES)["protocol_sha256"] == PROTOCOL_SHA256


def test_all_declared_checks_pass(payload):
    assert payload["valid"]
    assert all(payload["checks"].values()), payload["checks"]


def test_grid_is_complete_and_matches_the_protocol(payload):
    assert payload["m_grid"] == M_GRID
    assert payload["rho_grid"] == RHO_GRID
    assert len(payload["cells"]) == 4 * len(M_GRID) * len(RHO_GRID)
    seen = {(c["layer"], c["m"], c["rho"]) for c in payload["cells"]}
    assert len(seen) == len(payload["cells"])


def test_every_cell_carries_the_full_required_schema(payload):
    required = {
        "layer", "detector_family", "m", "rho", "gamma_tilde", "lambda",
        "abs_lambda", "class", "local_first_order_dynamics", "evidence_class",
        "gamma_evidence_class", "uncertainty_status", "gamma_regime",
        "classification_reportable_as_robust", "rho_in_admissible_domain",
    }
    for cell in payload["cells"]:
        assert required <= set(cell)


def test_multiplier_recomputes_from_the_identity(payload):
    for cell in payload["cells"]:
        assert cell["lambda"] == pytest.approx(
            multiplier(cell["rho"], cell["gamma_tilde"]), abs=1e-15)
        assert cell["class"] == classify(cell["rho"], cell["gamma_tilde"])


def test_exact_boundary_cells_are_boundary_class(payload):
    assert len(payload["boundary_cells"]) == 16
    for cell in payload["boundary_cells"]:
        assert cell["class"] == "BOUNDARY"
        assert cell["local_first_order_dynamics"] == "FIRST_ORDER_BOUNDARY_INCONCLUSIVE"
        assert cell["abs_lambda"] == pytest.approx(1.0, abs=1e-12)


def test_empirical_boundary_cells_are_never_reported_as_robust(payload):
    for cell in payload["boundary_cells"]:
        if cell["gamma_evidence_class"] == "EMPIRICAL_ONLY":
            assert not cell["classification_reportable_as_robust"]
            assert cell["evidence_class"] == "INCONCLUSIVE"


def test_certified_and_empirical_labels_cannot_be_confused(payload):
    for cell in payload["cells"] + payload["boundary_cells"]:
        if cell["gamma_evidence_class"] == "EMPIRICAL_ONLY":
            assert cell["evidence_class"] in (
                "THEOREM_PLUS_EMPIRICAL_ESTIMATE", "INCONCLUSIVE")
            assert cell["gamma_tilde_exact"] is None
        else:
            assert cell["evidence_class"] == "THEOREM_PLUS_CERTIFIED_INPUT"
            assert cell["gamma_tilde_exact"] is not None


def test_at_least_one_uncertainty_sensitive_grid_cell_is_detected(payload):
    sensitive = [c for c in payload["cells"]
                 if not c["classification_reportable_as_robust"]]
    assert sensitive, "the uncertainty machinery must be exercised by real data"
    for cell in sensitive:
        lo, hi = cell["abs_lambda_interval"]
        assert lo <= 1.0 <= hi


def test_boundary_rows_cover_every_layer_and_window(payload):
    rows = read_json(BOUNDARIES)["rows"]
    assert len(rows) == 4 * len(M_GRID)
    for row in rows:
        assert row["gamma_regime"] == "GAMMA_GT_2"
        assert row["accessible_in_admissible_domain"]
        assert 0.0 < row["rho_crit"] < 1.0


def test_exact_rational_boundaries_are_exact(payload):
    rows = [r for r in read_json(BOUNDARIES)["rows"] if r["rho_crit_exact"]]
    assert {r["rho_crit_exact"] for r in rows} == {"2/13", "1/3", "1/2", "3/5", "5/7"}
    assert all(r["rho_crit_exact_gives_unit_magnitude"] for r in rows)


def test_csv_matches_the_json_cells(payload):
    with CSV_PATH.open() as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == len(payload["cells"]) + len(payload["boundary_cells"])
    lookup = {(c["layer"], c["m"], c["rho"]): c
              for c in payload["cells"] + payload["boundary_cells"]}
    for row in rows:
        cell = lookup[(row["layer"], int(row["m"]), float(row["rho"]))]
        assert row["class"] == cell["class"]
        assert float(row["lambda"]) == pytest.approx(cell["lambda"])
        assert row["evidence_class"] == cell["evidence_class"]


def test_every_figure_cell_is_traceable():
    index = read_json(FIGURE_INDEX)
    assert index["traceability"]["every_plotted_cell_traceable"]
    assert index["traceability"]["checked_cells"] == 304
    for name, digest in index["figures"].items():
        assert sha256(CAMPAIGN / name) == digest
    assert index["inputs"]["results/stability_map.json"] == sha256(MAP)


def test_regeneration_is_deterministic(tmp_path):
    before = MAP.read_bytes()
    before_csv = CSV_PATH.read_bytes()
    mapbuild.build()
    assert MAP.read_bytes() == before
    assert CSV_PATH.read_bytes() == before_csv


def test_one_command_map_rebuild_is_byte_identical():
    digests = {p: sha256(p) for p in (MAP, CSV_PATH, BOUNDARIES)}
    figures = read_json(FIGURE_INDEX)["figures"]
    subprocess.run(
        [sys.executable, str(CAMPAIGN / "scripts" / "build_map.py")],
        check=True, capture_output=True,
    )
    for path, digest in digests.items():
        assert sha256(path) == digest
    assert read_json(FIGURE_INDEX)["figures"] == figures


def _classify_cli(*args):
    result = subprocess.run(
        [sys.executable, str(CAMPAIGN / "scripts" / "classify.py"), *args],
        check=True, capture_output=True, text=True,
    )
    return read_json_text(result.stdout)


def read_json_text(text):
    import json
    return json.loads(text)


def test_classifier_cli_reproduces_a_stored_cell(payload):
    cell = _classify_cli("--detector", "SR", "--m", "5", "--rho", "0.1")
    stored = next(c for c in payload["cells"]
                  if c["layer"] == "GAUSSIAN_SR_FROZEN" and c["m"] == 5
                  and c["rho"] == 0.1)
    for key in ("lambda", "abs_lambda", "class", "evidence_class",
                "uncertainty_status", "classification_reportable_as_robust"):
        assert cell[key] == stored[key]


def test_classifier_cli_reports_the_certified_boundary_cell():
    cell = _classify_cli("--detector", "SR-witness", "--m", "3", "--rho", "0.6")
    assert cell["class"] == "BOUNDARY"
    assert cell["evidence_class"] == "THEOREM_PLUS_CERTIFIED_INPUT"
    assert cell["gamma_tilde_exact"] == "8/3"


def test_classifier_cli_handles_an_inaccessible_boundary():
    cell = _classify_cli("--gamma", "1.5", "--rho", "1.0")
    assert cell["class"] == "LOCALLY-STABLE"
    assert cell["boundary"]["rho_crit"] == pytest.approx(2.0)
    assert not cell["boundary"]["accessible_in_admissible_domain"]


def test_classifier_cli_rejects_an_unsupported_window():
    result = subprocess.run(
        [sys.executable, str(CAMPAIGN / "scripts" / "classify.py"),
         "--detector", "CUSUM", "--m", "4", "--rho", "0.1"],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "not supported" in result.stderr


def test_cross_detector_comparison_is_recorded_and_scoped(payload):
    comparison = payload["cross_detector_comparison"]
    assert comparison["layers_compared"] == [
        "GAUSSIAN_SR_FROZEN", "GAUSSIAN_CUSUM_FROZEN"]
    assert [row["m"] for row in comparison["windows"]] == M_GRID
    assert comparison["sr_boundary_below_cusum_at_every_window"]
    assert comparison["separation_supported_by_disjoint_intervals_at_every_window"]
    assert comparison["evidence_class"] == "THEOREM_PLUS_EMPIRICAL_ESTIMATE"
    assert "not a detector-universal law" in comparison["scope"]


def test_cross_detector_comparison_matches_the_boundary_rows(payload):
    rows = {(r["layer"], r["m"]): r for r in payload["boundary_rows"]}
    for row in payload["cross_detector_comparison"]["windows"]:
        assert row["cusum_rho_crit"] == rows[("GAUSSIAN_CUSUM_FROZEN", row["m"])]["rho_crit"]
        assert row["sr_rho_crit"] == rows[("GAUSSIAN_SR_FROZEN", row["m"])]["rho_crit"]
