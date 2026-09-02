"""R1 benchmark result tests.  Prior results must stay intact."""
from __future__ import annotations

import json
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
R1 = NS / "compute_optimization_r1"
B = json.loads((NS / "results" / "r1_benchmark.json").read_text())
S = json.loads((NS / "results" / "r1_selftest.json").read_text())
CC = json.loads((NS / "results" / "r1_cover_compression.json").read_text())
RA = json.loads((NS / "results" / "ra_stop_gate.json").read_text())
OLD = json.loads((NS / "results" / "stop_gate_cell.json").read_text())


def test_prior_results_untouched():
    assert OLD["stop_gate"]["verdict"] == "FAIL" and OLD["achieved_half_width"] > 1e40
    assert RA["stop_gate"]["verdict"] == "PASS"
    assert RA["achieved_half_width"] == 0.014176477298268092
    assert RA["stop_gate"]["frozen_threshold"] == 0.2


def test_selftest_passed_before_benchmark():
    assert S["verdict"] == "PASS"
    for k, v in S["checks"].items():
        if isinstance(v, bool):
            assert v is True, k


def test_same_cell_same_threshold_same_target():
    assert B["e_cell"] == RA["e_cell"] == [0.24, 0.26]
    assert B["detector"] == "cusum" and B["m"] == 1
    assert B["stop_gate"]["frozen_threshold"] == 0.2
    assert B["target_unchanged"] is True and B["scope_unchanged"] is True
    assert B["classification"] == "CERTIFIED_BOUND_REFACTOR"
    assert B["taylor_order_N"] == RA["taylor_order_N"]
    assert B["candidate_degree"] == RA["candidate_degree"]
    assert B["precision_bits"] == RA["precision_bits"]
    assert B["subdivision_depth"] == RA["subdivision_depth"]


def test_verdict_is_mechanical():
    half = B["stop_gate"]["achieved_half_width"]
    assert B["stop_gate"]["verdict"] == ("PASS" if half <= 0.2 else "FAIL")


def test_certified_correspondence_with_ra():
    lo, hi = B["R_enclosure"]["lower"], B["R_enclosure"]["upper"]
    ra_lo, ra_hi = RA["R_enclosure"]["lower"], RA["R_enclosure"]["upper"]
    assert B["correspondence"]["overlaps_ra"] is True
    assert not (hi < ra_lo or lo > ra_hi)
    # a tighter valid bound must give a contained interval, not a shifted one
    assert lo >= ra_lo and hi <= ra_hi


def test_speedup_bands_applied_as_frozen():
    sp = B["speed"]["measured_speedup"]
    band = ("NOT_WORTH_MIGRATING" if sp < 2.0 else "BORDERLINE" if sp < 3.0
            else "WORTH_MIGRATING" if sp < 4.0 else "STRONG_PASS")
    assert B["speed"]["speedup_class"] == band
    assert B["speed"]["baseline_cpu_hours"] == 6.20
    assert B["speed"]["workers"] == RA["runtime"]["workers"]


def test_optimization_really_is_one():
    opt = B["resolvent_optimized"]["resolvent_bound_upper_float"]
    base = B["resolvent_baseline_block_forcing"]["resolvent_bound_upper_float"]
    assert opt < base
    assert abs(B["resolvent_reduction_factor"] - base / opt) < 1e-9
    assert B["resolvent_optimized"]["empirical_monotonicity_used"] is False
    assert B["subcells"]["ladder_steps_used"] == 0
    assert B["refinements"] == 0
    assert B["subcells"]["tiles_cell_exactly"] is True


def test_cover_compression_is_derived_not_chosen():
    assert CC["applies_to"] == "the C1 first-moment cover only"
    for d in ("cusum", "sr"):
        assert CC[d]["sup_below_2"] is True
        assert CC[d]["continuum_cover"] is True
        assert CC[d]["sampled_grid_used"] is False
    proj = (R1 / "R1_COST_REPROJECTION.md").read_text()
    assert "economically irrelevant" in proj
    assert "retained" in proj


def test_range_not_shortened():
    proj = (R1 / "R1_COST_REPROJECTION.md").read_text()
    assert "`[0, 12]` is therefore **retained**" in proj


def test_full_cover_not_launched():
    assert not list((NS / "results").glob("cover_*"))


def test_lean_interface_unchanged():
    assert "LEAN_INTERFACE_CHANGED = NO" in (NS / "LEAN_COMPATIBILITY.md").read_text()


def test_no_lean_sources_yet():
    assert not list(NS.rglob("*.lean"))
