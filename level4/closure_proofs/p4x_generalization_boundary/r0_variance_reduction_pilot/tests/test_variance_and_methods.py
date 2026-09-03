"""Variance-reduction arithmetic, method verdicts, and bias admissibility."""

from __future__ import annotations

import math

import pytest

T1P5 = ("frozen/sr@520.886/t1p5", "frozen/cusum@5/t1p5", "reduced/sr@20/t1p5")
SKEW = "frozen/sr@520.886/skewnormal4"


def _base(pilot, cfg):
    return pilot["results"][cfg]["methods"]["baseline_h0.05"]


def test_every_method_ran_or_was_explicitly_skipped(pilot):
    for cfg, res in pilot["results"].items():
        for name in pilot["methods"]:
            assert name in res["methods"], (cfg, name)
            entry = res["methods"][name]
            assert entry.get("skipped") or "by_m" in entry, (cfg, name)


def test_reflection_is_skipped_only_for_the_asymmetric_family(pilot):
    for cfg, res in pilot["results"].items():
        skipped = res["methods"]["reflection_h0.05"].get("skipped", False)
        assert skipped == (cfg == SKEW), cfg


def test_variance_reduction_factor_matches_the_block_sds(pilot):
    """VRF must be recomputable as (baseline SD / method SD)^2."""
    for cfg, res in pilot["results"].items():
        base = _base(pilot, cfg)
        for name, out in res["methods"].items():
            if out.get("skipped") or name == "baseline_h0.05":
                continue
            for m in ("1", "2", "3", "5"):
                b_sd = base["by_m"][m]["block_sd"]
                o_sd = out["by_m"][m]["block_sd"]
                expected = (b_sd ** 2) / (o_sd ** 2)
                got = out["versus_baseline"][m]["variance_reduction_factor"]
                assert got == pytest.approx(expected, rel=1e-9), (cfg, name, m)


def test_variance_ratio_confidence_intervals_bracket_the_point_estimate(pilot):
    for cfg, res in pilot["results"].items():
        for name, out in res["methods"].items():
            if out.get("skipped") or name == "baseline_h0.05":
                continue
            for m, r in out["versus_baseline"].items():
                lo, hi = r["vrf_ci95"]
                assert lo <= r["variance_reduction_factor"] <= hi, (cfg, name, m)
                assert lo > 0


def test_standard_error_is_block_sd_over_sqrt_blocks(pilot):
    for cfg, res in pilot["results"].items():
        for name, out in res["methods"].items():
            if out.get("skipped"):
                continue
            for m, s in out["by_m"].items():
                assert s["se"] == pytest.approx(
                    s["block_sd"] / math.sqrt(s["blocks"]), rel=1e-9), (cfg, name, m)


def test_reflection_is_rejected_for_increasing_variance(pilot):
    """The headline negative result: reflection raises variance 300-1000x."""
    for cfg in T1P5:
        r = pilot["results"][cfg]["methods"]["reflection_h0.05"]["versus_baseline"]["1"]
        assert r["variance_reduction_factor"] < 0.01, cfg
        assert r["vrf_ci95"][1] < 0.01, cfg


def test_g2_control_variate_is_degenerate(pilot):
    """Corollary G2 makes the deterministic-horizon control exactly 1."""
    for cfg, res in pilot["results"].items():
        probe = res["g2_control_probe"]
        assert probe["mean"] == pytest.approx(1.0, abs=1e-9), cfg
        assert probe["per_path_variance"] < 1e-20, cfg
        assert probe["usable_as_control_variate"] is False, cfg


def test_coarse_h_is_inadmissibly_biased_for_the_asymmetric_family(pilot):
    res = pilot["results"][SKEW]["methods"]
    for name, min_shift in (("coarse_h0.10", 4.0), ("coarse_h0.20", 20.0)):
        shift = abs(res[name]["versus_baseline"]["1"]["estimate_shift_in_baseline_se"])
        assert shift > min_shift, (name, shift)


def test_coarse_h_shift_is_small_but_sign_inconsistent_for_t1p5(pilot):
    """Why coarse h is NOT adopted for t1p5: the benefit is real, the bias is
    unresolved, and the step ladder does not agree on a sign."""
    shifts = {}
    for cfg in T1P5:
        res = pilot["results"][cfg]["methods"]
        shifts[cfg] = [
            res[n]["versus_baseline"]["1"]["estimate_shift_in_baseline_se"]
            for n in ("coarse_h0.10", "coarse_h0.20")
        ]
        assert all(abs(s) < 1.0 for s in shifts[cfg]), cfg
    signs = {math.copysign(1.0, s) for v in shifts.values() for s in v}
    assert signs == {-1.0, 1.0}, "expected sign inconsistency across configurations"


def test_no_variance_reduction_method_was_adopted(pilot_dir):
    text = (pilot_dir / "PRECISION_POLICY.md").read_text()
    assert "variance reduction   NONE ADOPTED" in text or \
           "adopt NO variance-reduction method" in text
    draft = (pilot_dir / "DRAFT_CHECKPOINT_A.md").read_text()
    assert "variance reduction   NONE ADOPTED" in draft


def test_bias_checks_separate_pathwise_algebra_from_distributional_validity(pilot_dir):
    import json
    b = json.loads((pilot_dir / "results" / "bias_checks.json").read_text())
    # the pathwise mirror holds for EVERY family, including the asymmetric one
    assert b["asymmetric_pathwise_control"]["exact_to_machine_precision"] is True
    assert b["reflection_pathwise_exact_for_symmetric_families"] is True
    # distributional validity is what actually separates them
    valid = b["reflection_distributionally_valid"]
    assert valid["t1p5"] is True
    assert valid["gaussian"] is True
    assert valid["skewnormal4"] is False
    assert b["asymmetric_control_correctly_fails"] is True


def test_detectors_are_reflection_equivariant(pilot_dir):
    import json
    b = json.loads((pilot_dir / "results" / "bias_checks.json").read_text())
    assert b["detector_equivariance"]
    for row in b["detector_equivariance"]:
        assert row["reflection_equivariant"] is True, row["detector"]


def test_coupled_paths_contribute_exactly_one(pilot):
    """The structural fact: all Route-B variance lives on the decoupling set."""
    for cfg in T1P5:
        stats = _base(pilot, cfg)["contribution_stats_m1"]
        assert stats["exactly_one_fraction"] > 0.80, cfg
    skew = _base(pilot, SKEW)["contribution_stats_m1"]
    assert skew["exactly_one_fraction"] < 0.40
