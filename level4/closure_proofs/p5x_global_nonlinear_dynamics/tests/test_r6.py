"""R6 frozen-spec and result invariants.  Git-object anchors live in test_checkpoint_i.py."""
from __future__ import annotations
import json
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
SPEC = (NS / "compute_optimization_r6_minimal_evaluator" / "R6_FROZEN_SPEC.md").read_text()
G = json.loads((NS / "results" / "r6_gate.json").read_text())
C = G["criteria"]


def test_threshold_not_weakened():
    assert C["G3_amplification"]["threshold"] == 1e12
    assert "unchanged" in SPEC and "never weakened" in SPEC


def test_gate_passed_all_ten():
    assert G["gate"] == "PASS"
    assert G["failed_criteria"] == []
    assert len(C) == 10 and all(v["pass"] for v in C.values())


def test_amplification_is_a_breakthrough_against_r4():
    a = C["G3_amplification"]
    assert a["value"] <= 1e12 and G["amp_class"] == "R6_BREAKTHROUGH"
    assert a["r4_reference"] == 2.1355909533505946e17
    assert a["improvement_vs_r4"] > 1e15


def test_representation_repair_not_precision_patch():
    s = C["G10_precision_sweep"]["sweep"]
    assert [r["bits"] for r in s] == [192, 256, 320, 384, 512]
    assert all(100 <= r["amplification"] <= 101 for r in s), s


def test_panel_and_softplus_freedom_preserved():
    assert C["G4_z_panels"]["count"] == 0
    assert C["G5_softplus"]["count"] == 0


def test_algebraic_correspondence_at_every_k():
    assert C["G1_per_k_overlap_R4"]["n_k"] == 33
    assert C["G1_per_k_overlap_R4"]["failing_k"] == []
    assert C["G2_rigorous_containment"]["R6_subset_R4"] is True


def test_huge_tiny_is_reported_not_gated():
    d = G["reporting_diagnostics_not_criteria"]
    assert d["huge_tiny_products"] > 0          # it happens, and the gate passed anyway
    assert not any("huge" in k for k in C)      # never a criterion


def test_r5_and_r4_failures_preserved():
    assert C["G3_amplification"]["r5_frozen"] == 2.238123651003098e20
    r5 = json.loads((NS / "results" / "r5_gate.json").read_text())
    r4 = json.loads((NS / "results" / "r4_gate.json").read_text())
    assert r5["gate"] == "FAIL" and r4["gate"] == "FAIL"


def test_anchor_is_checkpoint_h():
    assert G["checkpoint_h"] == "7800911d4ca5b93f1f4317494669f228501ef42a"
