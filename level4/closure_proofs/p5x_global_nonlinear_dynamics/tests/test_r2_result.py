"""R2 result tests.  Prior campaigns must stay intact."""
from __future__ import annotations
import json
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
R2 = NS / "compute_optimization_r2"
B = json.loads((NS / "results" / "r2_benchmark.json").read_text())
S = json.loads((NS / "results" / "r2_selftest.json").read_text())
R1 = json.loads((NS / "results" / "r1_benchmark.json").read_text())
RA = json.loads((NS / "results" / "ra_stop_gate.json").read_text())
OLD = json.loads((NS / "results" / "stop_gate_cell.json").read_text())


def test_prior_campaigns_untouched():
    assert OLD["stop_gate"]["verdict"] == "FAIL"
    assert RA["achieved_half_width"] == 0.014176477298268092
    assert R1["stop_gate"]["verdict"] == "PASS"
    assert R1["achieved_half_width"] == 0.008045668639929672
    assert R1["speed"]["measured_speedup"] == 5.286834033745004


def test_selftest_passed_before_benchmark():
    assert S["verdict"] == "PASS"
    for k, v in S["checks"].items():
        if isinstance(v, bool):
            assert v is True, k


def test_c2_returns_the_same_bound():
    assert abs(S["checks"]["S2_ratio"] - 1.0) < 1e-9
    assert S["checks"]["S2_primitive_speedup"] > 5.0


def test_same_cell_target_and_threshold():
    assert B["e_cell"] == R1["e_cell"] == [0.24, 0.26]
    assert B["detector"] == "cusum" and B["m"] == 1
    assert B["stop_gate"]["frozen_threshold"] == 0.2
    assert B["target_unchanged"] and B["scope_unchanged"]
    assert B["taylor_order_N"] == R1["taylor_order_N"]
    assert B["candidate_degree"] == R1["candidate_degree"]
    assert B["precision_bits"] == R1["precision_bits"]


def test_verdict_and_bands_mechanical():
    h = B["stop_gate"]["achieved_half_width"]
    assert B["stop_gate"]["verdict"] == ("PASS" if h <= 0.2 else "FAIL")
    sp = B["speed"]["measured_speedup"]
    band = ("R2_WEAK" if sp < 2 else "R2_MODERATE" if sp < 4
            else "R2_STRONG" if sp < 8 else "R2_BREAKTHROUGH")
    assert B["speed"]["speedup_class"] == band
    assert B["speed"]["workers"] == R1["speed"]["workers"]


def test_certified_correspondence_with_r1():
    lo, hi = B["R_enclosure"]["lower"], B["R_enclosure"]["upper"]
    r1lo, r1hi = R1["R_enclosure"]["lower"], R1["R_enclosure"]["upper"]
    assert B["correspondence"]["overlaps_r1"] is True
    assert not (hi < r1lo or lo > r1hi)


def test_unrunnable_benchmarks_recorded_not_substituted():
    doc = (R2 / "R2_RESULT.md").read_text()
    assert "NOT RUNNABLE" in doc
    assert "easier cells were deliberately not substituted" in doc.replace("\n", " ")


def test_campaign_class_applied_to_the_frozen_bands():
    doc = (R2 / "R2_RESULT.md").read_text()
    assert "R2_USEFUL_BUT_MORE_OPT_REQUIRED" in doc
    assert "R2 is a `14.45x` breakthrough on CUSUM and only `~1.06x` on the campaign" \
        in doc.replace("\n", " ")


def test_bottleneck_migration_recorded():
    doc = (R2 / "R2_RESULT.md").read_text()
    assert "NEW_DOMINANT_BOTTLENECK = SR certifier architecture" in doc.replace("\n", " ")


def test_full_cover_not_launched():
    assert not list((NS / "results").glob("cover_*"))
    assert "NOT AUTHORIZED, NOT LAUNCHED" in (R2 / "R2_RESULT.md").read_text()


def test_lean_interface_unchanged():
    assert (NS / "LEAN_COMPATIBILITY.md").read_text().count("LEAN_INTERFACE_CHANGED = NO") >= 2


def test_no_lean_sources_yet():
    assert not list(NS.rglob("*.lean"))
