"""Provenance loading tests: no number may be retyped by hand."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest

from rebaseguard_p3_map import provenance
from rebaseguard_p3_map.common import read_json
from rebaseguard_p3_map.config import CAMPAIGN, M_GRID, ROOT

P1 = ROOT / "level4" / "closure_proofs" / "m_gt_1_priority1"
P2 = ROOT / "level4" / "closure_proofs" / "sr_derivative_priority2"


def _layer(payload, layer_id):
    return next(row for row in payload["layers"] if row["id"] == layer_id)


@pytest.fixture(scope="module")
def prov():
    return read_json(CAMPAIGN / "results" / "provenance.json")


def test_every_upstream_artifact_hash_matches(prov):
    assert prov["upstream_hashes"]["all_match"]
    assert len(prov["upstream_hashes"]["sources"]) >= 10


def test_cusum_gains_come_from_the_priority1_result_json(prov):
    upstream = read_json(P1 / "results" / "numerical_correspondence.json")
    rows = _layer(prov, "GAUSSIAN_CUSUM_FROZEN")["rows"]
    assert [row["m"] for row in rows] == upstream["protocol"]["m_grid"] == M_GRID
    for row, gamma, se in zip(rows, upstream["score"]["gamma_mean"],
                              upstream["score"]["slope_se"], strict=True):
        assert row["gamma_tilde"] == gamma
        assert row["gamma_tilde_se"] == se
    assert upstream["evidence_class"] == "EMPIRICAL_FROZEN_GAUSSIAN_CUSUM"


def test_sr_gains_come_from_the_priority2_result_json(prov):
    upstream = read_json(P2 / "results" / "numerical_correspondence.json")
    rows = _layer(prov, "GAUSSIAN_SR_FROZEN")["rows"]
    assert [row["m"] for row in rows] == upstream["protocol"]["m_grid"] == M_GRID
    for row, gamma, se in zip(rows, upstream["final"]["gamma"],
                              upstream["final"]["gamma_se"], strict=True):
        assert row["gamma_tilde"] == gamma
        assert row["gamma_tilde_se"] == se
    assert upstream["evidence_class"] == "EMPIRICAL_FROZEN_GAUSSIAN_SR"


def test_gaussian_layers_are_labelled_empirical(prov):
    for layer_id in ("GAUSSIAN_CUSUM_FROZEN", "GAUSSIAN_SR_FROZEN"):
        layer = _layer(prov, layer_id)
        assert layer["gamma_evidence_class"] == "EMPIRICAL_ONLY"
        assert layer["cell_evidence_class"] == "THEOREM_PLUS_EMPIRICAL_ESTIMATE"


def test_witness_gains_replay_the_closed_certificates(prov):
    for layer_id, package in (("FINITE_SUPPORT_CUSUM_WITNESS", P1),
                              ("FINITE_SUPPORT_SR_WITNESS", P2)):
        recorded = {int(r["m"]): r["exact"]["gamma"]
                    for r in read_json(package / "certificates" / "certificate.json")["records"]}
        for row in _layer(prov, layer_id)["rows"]:
            if row["m"] in recorded:
                assert Fraction(row["gamma_tilde_exact"]) == Fraction(recorded[row["m"]])
                assert row["provenance_kind"] == "REPLAYED_FROM_CLOSED_PACKAGE"
            else:
                assert row["provenance_kind"] == "P3_NEW_EXACT_FROM_FROZEN_WITNESS"


def test_sr_witness_matches_its_recorded_closed_form():
    witness = read_json(P2 / "certificates" / "WITNESS.json")
    assert witness["exact_gamma_formula"] == "2+2/m"
    for m in M_GRID:
        assert provenance.exact_witness_gamma(witness, m) == 2 + Fraction(2, m)


def test_cusum_witness_gain_is_window_independent():
    witness = read_json(P1 / "certificates" / "WITNESS.json")
    values = {provenance.exact_witness_gamma(witness, m) for m in M_GRID}
    assert values == {Fraction(15, 2)}


def test_witness_gain_honours_the_random_denominator_convention():
    witness = read_json(P2 / "certificates" / "WITNESS.json")
    # tau=1 paths must keep denominator 1, not m; otherwise m=5 would differ.
    assert provenance.exact_witness_gamma(witness, 5) == Fraction(12, 5)


def test_upstream_packages_are_both_closed():
    for package in (P1, P2):
        decision = read_json(package / "results" / "closure_decision.json")
        assert decision["verdict"] == "CLOSED"


def test_a_changed_upstream_artifact_is_rejected(tmp_path, monkeypatch):
    manifest = json.loads((CAMPAIGN / "manifest.json").read_text())
    manifest["upstream_sources"] = dict(manifest["upstream_sources"])
    key = next(iter(manifest["upstream_sources"]))
    manifest["upstream_sources"][key] = "0" * 64
    fake = tmp_path / "manifest.json"
    fake.write_text(json.dumps(manifest))
    monkeypatch.setattr(provenance, "_manifest", lambda: json.loads(fake.read_text()))
    assert not provenance.verify_upstream_hashes()["all_match"]


def test_no_m_value_outside_the_supported_grid_is_synthesised(prov):
    for layer in prov["layers"]:
        assert [row["m"] for row in layer["rows"]] == M_GRID
    assert not prov["gamma_interpolated_across_m"]
