from __future__ import annotations

from pathlib import Path

CAMPAIGN = Path(__file__).resolve().parents[1]


def test_human_theorem_exposes_each_hypothesis_class():
    theorem = (CAMPAIGN / "THEOREM.md").read_text()
    required = [
        "### Path-functional hypotheses",
        "### Distributional hypotheses",
        "### Stopped-time and differentiation hypotheses",
        "event-sliced change-of-measure series is absolutely summable",
        "there is an integrable `G`",
        "d/de E_e[H_tau]|_0 = E_0[H_tau S_tau]",
    ]
    assert all(fragment in theorem for fragment in required)


def test_local_instability_premises_are_not_bundled_into_theorem():
    theorem = (CAMPAIGN / "THEOREM.md").read_text()
    assert "rho |1-Gamma_f|>1" in theorem
    assert "Gamma_f>1+1/rho" in theorem
    assert "additional premises" in theorem


def test_protocol_freezes_all_families_steps_samples_and_gates():
    protocol = (CAMPAIGN / "PROTOCOL.md").read_text()
    required = [
        "unit-variance t10",
        "unit-variance t5",
        "unit-variance t3",
        "2026082307",
        "48 independent batches of 10,000 paths",
        "48 independent batches of 5,000 paired path streams",
        "h in {0.05,0.025,0.0125}",
        "primary step is `h=0.0125`",
        "`|z|<=3`",
        "at most 3%",
        "No family may be removed",
    ]
    assert all(fragment in protocol for fragment in required)


def test_lean_is_strictly_gated_and_conditional():
    protocol = (CAMPAIGN / "PROTOCOL.md").read_text()
    assert "NUMERICAL GATE CLOSED — LEAN AUTHORIZED" in protocol
    assert "Lean is authorized only by the exact pass declaration" in protocol
    assert "formal theorem remains conditional over analytic hypotheses" in protocol
    assert "No `sorry`, `admit`, or project-specific axiom" in protocol


def test_forbidden_claims_are_only_negated():
    theorem = (CAMPAIGN / "THEOREM.md").read_text()
    assert "It is not" in theorem
    for forbidden in ("distribution-free", "universal", "detector-independent"):
        assert forbidden in theorem

