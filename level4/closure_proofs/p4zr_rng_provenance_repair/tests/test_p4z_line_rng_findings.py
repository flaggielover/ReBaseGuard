"""The disclosed P4Z-line RNG findings, re-derived rather than asserted.

These tests rebuild the manifests from the frozen artifacts on every run, so an
edit to a historical script, plan or block file breaks them instead of silently
changing the disclosure.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

from rebaseguard_p4zr.rng_address_audit import audit_manifest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "audit"))
import build_rng_manifests as brm  # noqa: E402

NS = Path(__file__).resolve().parent.parent
CP = NS.parent
DISCLOSURE = json.loads((NS / "results" / "rng_collision_disclosure.json").read_text())
STRICT = json.loads((NS / "results" / "strict_gate_reconstruction.json").read_text())


@pytest.fixture(scope="module")
def reports():
    return {name: audit_manifest(brm.build(name)) for name in ("P4Z", "P4ZA", "P4ZB")}


# --- the three campaign verdicts -------------------------------------------

def test_p4z_fails_the_same_campaign_address_audit(reports):
    r = reports["P4Z"]
    assert r["verdict"] == "RNG_ADDRESS_SEPARATION_FAIL"
    assert len(r["address_overlaps"]) == 5
    assert r["overlapping_address_total"] == 25


def test_p4za_has_no_address_overlap_only_namespace_reuse(reports):
    """P4ZA reuses the integer 4190001 across two different bit generators.

    Philox in calibration, PCG64 in production: no innovation is shared, so this
    is a bookkeeping defect and not a collision.
    """
    r = reports["P4ZA"]
    assert r["verdict"] == "RNG_ADDRESS_SEPARATION_PASS"
    assert r["address_overlaps"] == []
    assert len(r["seed_namespace_reuse"]) == 1
    f = r["seed_namespace_reuse"][0]
    assert f["key"] == 4190001
    assert {f["calibration_generator"], f["production_generator"]} == {"PHILOX", "PCG64"}


def test_p4zb_is_clean_on_both_axes(reports):
    r = reports["P4ZB"]
    assert r["verdict"] == "RNG_ADDRESS_SEPARATION_PASS"
    assert r["address_overlaps"] == []
    assert r["seed_namespace_reuse"] == []


def test_the_exact_p4z_collisions(reports):
    got = {(f["generator"], f["key"], f["production_configuration"],
            f["production_route"], f["overlapping_address_count"])
           for f in reports["P4Z"]["address_overlaps"]}
    assert got == {
        ("PCG64", 4090001, "frozen/cusum@5/gaussian", "rb_score", 8),
        ("PCG64", 4090001, "frozen/cusum@5/gaussian", "rb_score", 1),
        ("PHILOX", 4090002, "frozen/cusum@5/gaussian", "rb_map", 4),
        ("PCG64", 4090101, "frozen/cusum@5/laplace", "rb_score", 6),
        ("PHILOX", 4090102, "frozen/cusum@5/laplace", "rb_map", 6),
    }


# --- the collision is real, not merely nominal ------------------------------

def test_a_shared_address_delivers_identical_innovations():
    """Production's draw is an exact prefix of the calibration draw.

    Demonstrated rather than argued, on the frozen family and the frozen
    stream-counter rule, for both bit generators.  Costs microseconds and is not
    a scientific rerun.
    """
    sys.path.insert(0, str(CP / "p4_theory_generalization" / "src"))
    from rebaseguard_p4_general.families import REGISTRY
    from rebaseguard_p4_general.simulate import stream_counter
    gaussian = REGISTRY["gaussian"]
    cal_paths, prod_paths = 40_000, 3_942          # the frozen path counts

    cal = gaussian.sample(np.random.Generator(np.random.PCG64([4_090_001, 0])),
                          (cal_paths,))
    prod = gaussian.sample(np.random.Generator(np.random.PCG64([4_090_001, 0])),
                           (prod_paths,))
    assert np.array_equal(prod, cal[:prod_paths])

    for step in (1, 2, 7):
        counter = stream_counter(0, step)
        a = gaussian.sample(np.random.Generator(
            np.random.Philox(key=4_090_002, counter=counter)), (cal_paths,))
        b = gaussian.sample(np.random.Generator(
            np.random.Philox(key=4_090_002, counter=counter)), (prod_paths,))
        assert np.array_equal(b, a[:prod_paths])


def test_a_disjoint_address_does_not_deliver_identical_innovations():
    sys.path.insert(0, str(CP / "p4_theory_generalization" / "src"))
    from rebaseguard_p4_general.families import REGISTRY
    gaussian = REGISTRY["gaussian"]
    a = gaussian.sample(np.random.Generator(np.random.PCG64([4_090_001, 0])), (512,))
    b = gaussian.sample(np.random.Generator(np.random.PCG64([4_090_301, 0])), (512,))
    assert not np.array_equal(a, b)


# --- bounded impact ---------------------------------------------------------

def test_no_overlapping_address_confers_a_final_disposition():
    cov = json.loads((CP / "p4zb_skewnormal4_k7" / "results"
                      / "final_coverage.json").read_text())
    affected = set(DISCLOSURE["findings"]["affected_production_configurations"])
    assert affected == {"frozen/cusum@5/gaussian", "frozen/cusum@5/laplace"}
    for c in cov["cells"]:
        cid = f"{c['layer']}/{c['detector']}/{c['family']}"
        if cid in affected:
            assert c["authoritative_source"] == "P4ZA", (
                f"{cid} m={c['m']} is authored by "
                f"{c['authoritative_source']}, which carries the overlap")


def test_the_gate_statistic_was_never_read_at_a_shared_address():
    for f in DISCLOSURE["findings"]["overlaps"]:
        insp = f["what_calibration_inspected"]
        assert insp["correspondence_gate_z"] is False
        assert insp["pass_fail_outcome"] is False


def test_strict_gate_bound_is_reproducible_and_matches_the_disclosure():
    b = DISCLOSURE["impact"]["strict_gate_bound"]
    assert b["cells_total"] == STRICT["cells_total"] == 96
    assert b["cells_passing"] == STRICT["cells_passing_the_strict_gate"] == 96
    assert b["worst_z_monte_carlo_error_only"] == pytest.approx(1.788, abs=5e-4)
    assert b["worst_relative_discrepancy"] == pytest.approx(0.0095, abs=5e-5)
    assert b["worst_z_monte_carlo_error_only"] < b["z_limit"] == 4.0
    assert b["worst_relative_discrepancy"] < b["relative_limit"] == 0.03


def test_strict_gate_is_strictly_harder_than_the_adjudicated_gate():
    """Removing T_B can only raise |z|; the reconstruction must show that."""
    for row in STRICT["cells"]:
        assert row["z_monte_carlo_error_only"] >= row["z_as_adjudicated"] - 1e-12


# --- the disclosure does not overclaim --------------------------------------

def test_disclosure_claims_a_bound_not_an_absence_of_impact():
    s = DISCLOSURE["impact"]["statement"].lower()
    assert "no observed disposition dependence" in s
    assert "bounded by" in s
    for banned in ("harmless", "no impact", "zero risk"):
        assert banned not in s
    assert DISCLOSURE["impact"]["defect_exists"] is True


def test_disclosure_records_residual_risk_and_defers_adjudication():
    assert len(DISCLOSURE["residual_governance_risk"]) >= 4
    assert DISCLOSURE["requires_independent_adjudication"] is True


def test_disclosure_declares_no_closure_and_preserves_history():
    blob = json.dumps(DISCLOSURE)
    assert "P4Z_CLOSED" not in blob and "P4ZB_CLOSED" not in blob
    assert DISCLOSURE["preserved"]["P4_ORIGINAL_VERDICT"] == "PARTIAL"
    assert DISCLOSURE["preserved"]["frozen_artifacts_modified"] is False
    assert DISCLOSURE["preserved"]["historical_scripts_modified"] is False


def test_this_repair_performs_neither_b1_nor_b3():
    scope = DISCLOSURE["scope"]
    assert "B2 only" in scope and "B1" in scope and "B3" in scope
    assert STRICT["does_not_perform"]
