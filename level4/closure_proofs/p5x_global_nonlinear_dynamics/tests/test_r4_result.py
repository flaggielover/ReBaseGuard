"""R4 result invariants, read from the committed JSON."""
from __future__ import annotations
import json
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
GATE = json.loads((NS / "results" / "r4_gate.json").read_text())
DIAG = json.loads((NS / "results" / "r4_diagnostics.json").read_text())
C = GATE["criteria"]


def test_gate_verdict_is_reported_as_fail_not_rewritten():
    assert GATE["gate"] == "FAIL"
    assert set(GATE["failed_criteria"]) == {"P2", "P3"}


def test_the_decisive_criterion_p4_passed():
    assert C["P4"]["pass"] is True
    assert C["P4"]["t_patch_seconds"] < C["P4"]["budget"]
    assert C["P4"]["budget"] == 0.3314531805        # never re-budgeted


def test_panels_were_eliminated_structurally_not_reduced():
    assert C["P5"]["counters"]["z_panels"] == 0
    assert C["P5"]["counters"]["softplus_expansions"] == 0
    assert C["P5"]["counters"]["phi_evals"] == 66   # exactly 2(2n+1), n=16


def test_projection_uses_the_frozen_formula():
    assert GATE["projection"]["formula"] == "835*1210*t_patch*2*43/3600"
    assert GATE["projection"]["speedup_class"] == "R4_BREAKTHROUGH"
    assert GATE["projection"]["r3_projected_SR_cpu_hours"] == 12083.77402548149


def test_diagnostics_are_labelled_post_hoc():
    assert DIAG["status"].startswith("POST-HOC")
    assert "post-hoc" in C["P2"]["defect"]


def test_closed_form_matches_reference_to_its_own_truncation():
    d = DIAG["P2_corrected_in_arb"]
    assert d["all_within_16x_of_reference_own_truncation"] is True
    assert d["worst_gap_over_own_truncation"] < 1.01


def test_p3_amplification_is_flat_in_precision():
    amps = [s["dependency_amplification"] for s in DIAG["P3_precision_sweep"]["sweep"]]
    assert all(1e17 <= a <= 1e19 for a in amps), amps
    assert all(not s["passes_frozen_1e12"] for s in DIAG["P3_precision_sweep"]["sweep"])


def test_anchor_is_checkpoint_f():
    assert GATE["checkpoint_f"] == "209a6fd9a5ca2824688062ac855a7abcefae9697"
