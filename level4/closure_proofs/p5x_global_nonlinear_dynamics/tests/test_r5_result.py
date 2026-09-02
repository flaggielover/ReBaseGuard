"""R5 result invariants, read from the committed JSON."""
from __future__ import annotations
import json
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
G = json.loads((NS / "results" / "r5_gate.json").read_text())
Q = G["criteria"]


def test_gate_reported_as_fail_not_rewritten():
    assert G["gate"] == "FAIL"
    assert set(G["failed_criteria"]) == {"Q2_summed_rigorous", "Q3_amplification", "Q7_runtime"}
    assert G["amp_class"] == "R5_P3_FAIL"


def test_threshold_never_weakened():
    assert Q["Q3_amplification"]["threshold"] == 1e12
    assert Q["Q3_amplification"]["r4_reference"] == 2.1355909533505946e17


def test_selftest_passed_and_algebra_corresponds_at_every_k():
    assert G["selftest"]["verdict"] == "PASS"
    assert G["selftest"]["detail"]["all_k_overlap_R4"] is True
    assert Q["Q1_per_k_overlap_with_R4"]["pass"] is True
    assert Q["Q1_per_k_overlap_with_R4"]["failing_k"] == []


def test_panel_and_softplus_freedom_preserved():
    assert Q["Q5_z_panels"]["count"] == 0
    assert Q["Q6_softplus"]["count"] == 0


def test_q4_passed_yet_q3_failed():
    """D13: the criterion the architecture was built for passed; the one that
    mattered failed."""
    assert Q["Q4_huge_tiny"]["pass"] is True
    assert Q["Q4_huge_tiny"]["status"] == "NO"
    assert Q["Q3_amplification"]["pass"] is False


def test_variants_labelled_post_hoc_and_do_not_affect_the_verdict():
    assert G["post_hoc_variants"]["status"].startswith("POST-HOC")
    for v in G["post_hoc_variants"]["detail"].values():
        assert v["overlaps_R4"] is True


def test_post_hoc_repair_reduces_the_metric_itself_not_by_precision():
    amps = [r["minimal"]["amplification"] for r in G["precision_sweep"]]
    assert all(100 <= a <= 101 for a in amps), amps      # flat 192..512 bits
    frozen = [r["frozen"]["amplification"] for r in G["precision_sweep"]]
    assert all(a > 1e12 for a in frozen), frozen


def test_regimes_are_exhaustive_and_match_the_theory():
    r = G["regimes_used"]
    assert r["16"] == "B" and r["-16"] == "C" and r["0"] == "D"
    assert set(r.values()) <= {"B", "C", "D"}
    assert len(r) == 33


def test_anchor_is_checkpoint_g():
    assert G["checkpoint_g"] == "f19f8d13caae1d9d8d21a6237fe1b71ee06b8e63"


def test_no_full_cell_prototype_was_run():
    assert "full_cell" not in G
