"""Checks over the P9R production artifacts.

These are implementation checks: they verify that the artifacts say what the
documents say they say, with the frozen conventions.  They do not adjudicate
the science.
"""
from __future__ import annotations

import json
import math

import numpy as np
import pytest
from scipy.stats import norm

from conftest import P9R, ROOT

P7_CONSEQUENCES = (ROOT / "level4" / "closure_proofs"
                   / "p7_statistical_consequences" / "results"
                   / "consequences.json")


# ------------------------------------------------------------- reproduction
def test_reproduction_covers_all_sixteen_frozen_cells(reproduction):
    rows = reproduction["rows"]
    assert len(rows) == 16
    keys = {(r["detector"], r["m"], r["rho"]) for r in rows}
    assert keys == {(d, m, r) for d in ("cusum", "sr")
                    for m in (1, 2, 3, 5) for r in (0.0, 1.0)}


def test_reproduction_targets_are_read_from_the_authoritative_p7_artifact(reproduction):
    p7 = {(c["detector"], int(c["m"]), round(float(c["rho"]), 10)): c
          for c in json.loads(P7_CONSEQUENCES.read_text())["cells"]}
    for r in reproduction["rows"]:
        c = p7[(r["detector"], r["m"], r["rho"])]
        assert r["p7_arl"] == pytest.approx(float(c["arl"]), rel=0, abs=0.0)
        assert r["p7_arl_se"] == pytest.approx(float(c["arl_se"]), rel=0, abs=0.0)
        assert r["burn_in"] == int(c["burn_in"])


def test_combined_se_and_z_are_computed_correctly(reproduction):
    for r in reproduction["rows"]:
        cse = math.sqrt(r["p9r_arl_se"] ** 2 + r["p7_arl_se"] ** 2)
        assert r["combined_se"] == pytest.approx(cse, rel=1e-12)
        assert r["z"] == pytest.approx((r["p9r_arl"] - r["p7_arl"]) / cse, rel=1e-12)


def test_cusum_and_sr_are_summarised_separately(reproduction):
    s = reproduction["per_detector_summary"]
    assert set(s) == {"cusum", "sr"}
    for det in s:
        assert s[det]["n_cells"] == 8


def test_sr_defect_comparison_is_present_and_paired(reproduction):
    rows = reproduction["sr_defect_comparison"]
    assert len(rows) == 8
    for r in rows:
        assert r["corrected_arl"] != r["defective_arl"]
        assert "paired_z" in r and "paired_mean_difference" in r


# ------------------------------------------------------------- burn-in (A5)
def test_burnin_reports_the_authoritative_p7_convention(burnin):
    assert burnin["authoritative_p7_burn_in"] == 12
    for row in burnin["rows"]:
        assert "12" in row["conventions"]
        assert row["n_rep"] == 5000 and row["n_cycles"] == 50


def test_burnin_first_cycle_is_the_nominal_control(burnin):
    for row in burnin["rows"]:
        cyc = row["cycle_mean"]
        assert cyc[0] > 100.0            # cycle 1 starts from a perfect reference
        assert cyc[1] < 20.0             # cycle 2 collapses under full reuse


# ------------------------------------------------------------- response (A6)
def test_response_grid_has_a_three_part_error_budget(response_grid):
    for det, d in response_grid["detectors"].items():
        for m, mx in d["mixtures"].items():
            for k in ("mc_se", "discretisation_richardson",
                      "truncation_upper_bound", "total_error_budget"):
                assert k in mx, (det, m, k)
            assert mx["total_error_budget"] == pytest.approx(
                mx["mc_se"] + mx["discretisation_richardson"]
                + mx["truncation_upper_bound"], rel=1e-9)


def test_truncation_bound_uses_the_uniform_bound_lemma(response_grid):
    for det, d in response_grid["detectors"].items():
        C = d["uniform_bound"]["bound"]
        for m, mx in d["mixtures"].items():
            tail = 2.0 * float(norm.sf(response_grid["grid"]["max"]
                                       / mx["sigma"]))
            assert mx["truncation_tail_mass"] == pytest.approx(tail, rel=1e-9)
            assert mx["truncation_upper_bound"] == pytest.approx(C * tail, rel=1e-9)


def test_evenness_is_numerically_consistent(response_grid):
    for det, d in response_grid["detectors"].items():
        assert d["evenness_check"]["consistent_at_3se"], det


def test_monotonicity_audit_reports_its_own_power(response_grid):
    for det, d in response_grid["detectors"].items():
        mono = d["monotonicity"]
        assert mono["n_pairs"] == response_grid["grid"]["n_intervals"]
        assert mono["max_min_detectable_increase"] > 0.0
        assert "global_max_at_zero_at_3se" in mono


def test_mixture_is_far_below_A0_in_every_cell(response_grid):
    for det, d in response_grid["detectors"].items():
        for m, mx in d["mixtures"].items():
            assert mx["mixture_E_A"] < mx["A0"]


def test_mixture_agrees_with_the_recursive_rho0_chain(reproduction, response_grid):
    """A6 quadrature vs the independent rho=0 chain simulation of R2."""
    rho0 = {(r["detector"], r["m"]): r for r in reproduction["rows"]
            if r["rho"] == 0.0}
    for det, d in response_grid["detectors"].items():
        for m_s, mx in d["mixtures"].items():
            r = rho0[(det, int(m_s))]
            spread = math.sqrt(r["p9r_arl_se"] ** 2
                               + (mx["total_error_budget"] / 3.0) ** 2)
            z = (mx["mixture_E_A"] - r["p9r_arl"]) / spread
            assert abs(z) < 8.0, (det, m_s, z)
