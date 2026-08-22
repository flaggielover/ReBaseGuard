from __future__ import annotations

from pathlib import Path

CAMPAIGN = Path(__file__).resolve().parents[1]


def test_human_theorem_contains_frozen_sign_and_derivative_chain():
    theorem = (CAMPAIGN / "THEOREM.md").read_text()
    required = [
        "Z_t=X_t-R_j=epsilon_t-e ~ N(-e,1)",
        "L_e := exp(-eT_tau-e^2 tau/2)",
        "F'_rho(0) = rho(1-Gamma_SR)",
        "Gamma_SR := E_0[Z_tau T_tau]",
        "|Z_t|>=b_A",
        "F_1(-e)=-e+G(-e)",
    ]
    assert all(fragment in theorem for fragment in required)


def test_human_theorem_keeps_rigorous_instability_open_without_arb():
    theorem = (CAMPAIGN / "THEOREM.md").read_text()
    assert "confirmatory only" in theorem
    assert "rigorous SR local-\ninstability certificate remain open" in theorem


def test_lean_boundary_is_conditional_and_concrete_obligations_are_human():
    theorem = (CAMPAIGN / "THEOREM.md").read_text()
    obligations = (CAMPAIGN / "PROOF_OBLIGATIONS.md").read_text()
    sentence = (
        "The Lean theorem formalizes the algebraic/stopped-score consequence under\n"
        "> explicit analytic hypotheses"
    )
    assert sentence in theorem
    assert sentence in obligations
    assert "It is not an end-to-end Lean formalization" in theorem
    assert "CLOSED (human)" in obligations


def test_lean_is_authorized_only_by_the_frozen_numerical_decision():
    obligations = (CAMPAIGN / "PROOF_OBLIGATIONS.md").read_text()
    decision = __import__("json").loads(
        (CAMPAIGN / "results/numerical_decision.json").read_text()
    )
    assert decision["decision"] == "NUMERICAL GATE CLOSED — LEAN AUTHORIZED"
    assert obligations.count("PENDING — AUTHORIZED") == 9
    assert "NUMERICAL GATE CLOSED — LEAN AUTHORIZED" in obligations
