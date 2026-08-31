"""Tests for the rigorous finite-support certification layer."""

from __future__ import annotations

import subprocess
import sys
from fractions import Fraction

import pytest

from rebaseguard_p3_map.common import read_json, sha256
from rebaseguard_p3_map.config import CAMPAIGN, M_GRID, RHO_GRID, ROOT

CERT = CAMPAIGN / "arb" / "certificate.json"


@pytest.fixture(scope="module")
def certificate():
    return read_json(CERT)


def test_schema_precision_and_backend(certificate):
    assert certificate["schema"] == "rebaseguard.p3-arb-certificate.v1"
    assert certificate["precision_bits"] == 128
    assert "Arb" in certificate["backend"]
    assert certificate["all_checks_pass"]


def test_only_finite_support_witnesses_are_certified(certificate):
    assert {row["layer"] for row in certificate["layers"]} == {
        "FINITE_SUPPORT_CUSUM_WITNESS", "FINITE_SUPPORT_SR_WITNESS"}
    assert certificate["gaussian_layers_certified"] is False
    assert "not interval-certified" in certificate["evidence_boundary"]


def test_no_gaussian_gain_appears_in_the_certificate(certificate):
    text = CERT.read_text()
    for forbidden in ("15.9165", "13.2648", "17.4535", "14.5005", "11.0485"):
        assert forbidden not in text


def test_certified_gains_replay_the_closed_packages(certificate):
    for layer in certificate["layers"]:
        for record in layer["records"]:
            if record["gamma_replayed_against_closed_package"]:
                assert record["gamma_replay_match"]
                assert Fraction(record["gamma_exact"]) == Fraction(
                    record["closed_package_gamma"])
            else:
                assert record["m"] == 1
                assert record["provenance_kind"] == "P3_NEW_EXACT_FROM_FROZEN_WITNESS"


def test_exact_boundaries_and_their_enclosures(certificate):
    expected = {
        "FINITE_SUPPORT_CUSUM_WITNESS": {m: "2/13" for m in M_GRID},
        "FINITE_SUPPORT_SR_WITNESS": {1: "1/3", 2: "1/2", 3: "3/5", 5: "5/7"},
    }
    for layer in certificate["layers"]:
        for record in layer["records"]:
            assert record["rho_crit_exact"] == expected[layer["layer"]][record["m"]]
            assert record["rho_crit_in_admissible_domain"]
            assert record["unit_magnitude_at_rho_crit_exact"]
            assert record["unit_magnitude_at_rho_crit_interval_encloses_one"]


def test_every_grid_cell_is_resolved_by_interval_arithmetic(certificate):
    for layer in certificate["layers"]:
        for record in layer["records"]:
            assert record["all_cells_resolved"]
            assert [c["rho_float"] for c in record["cells"]] == RHO_GRID
            for cell in record["cells"]:
                assert cell["certified_class"] != "INCONCLUSIVE"


def test_the_only_certified_boundary_grid_cell_is_the_sr_witness_at_three_fifths(
        certificate):
    hits = [(layer["layer"], record["m"], cell["rho"])
            for layer in certificate["layers"]
            for record in layer["records"]
            for cell in record["cells"]
            if cell["certified_class"] == "BOUNDARY"]
    assert hits == [("FINITE_SUPPORT_SR_WITNESS", 3, "3/5")]


def test_sr_witness_stopping_times_are_recertified(certificate):
    sr = next(layer for layer in certificate["layers"]
              if layer["layer"] == "FINITE_SUPPORT_SR_WITNESS")
    assert [row["certified_tau"] for row in sr["sr_stopping_certificates"]] == [1, 1, 6, 6]
    assert all(row["pass"] for row in sr["sr_stopping_certificates"])


def test_certificate_binds_the_frozen_witness_hashes(certificate):
    manifest = read_json(CAMPAIGN / "manifest.json")["upstream_sources"]
    for layer in certificate["layers"]:
        assert layer["witness_sha256"] == manifest[layer["witness"]]
        assert sha256(ROOT / layer["witness"]) == layer["witness_sha256"]


def test_certificate_replay_is_deterministic():
    before = CERT.read_bytes()
    subprocess.run([sys.executable, str(CAMPAIGN / "arb" / "run_certificate.py")],
                   check=True, capture_output=True)
    assert CERT.read_bytes() == before
