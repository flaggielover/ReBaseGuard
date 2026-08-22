from __future__ import annotations

from pathlib import Path

CAMPAIGN = Path(__file__).resolve().parents[1]


def test_residual_score_sign_and_stopped_score_are_explicit():
    audit = (CAMPAIGN / "DEFINITION_AUDIT.md").read_text()
    required = [
        "f_e(z)=f(z+e)",
        "s(z) = d/de log r_e(z)|_0",
        "= f'(z)/f(z)",
        "psi(z)=-f'(z)/f(z)",
        "s(z)=-psi(z)",
        "S_tau = sum_{t=1}^tau s(Z_t)",
    ]
    assert all(fragment in audit for fragment in required)


def test_actual_reuse_gain_is_neither_stage_d_candidate():
    audit = (CAMPAIGN / "DEFINITION_AUDIT.md").read_text()
    assert "Gamma_f" in audit
    assert "E_0[Z_tau sum_{t=1}^tau psi(Z_t)]" in audit
    assert "Actual ReBaseGuard `m=1` uses `H_tau=Z_tau`" in audit
    assert "the theorem-relevant quantity is **neither**" in audit


def test_gaussian_reduction_matches_closed_formula_exactly():
    audit = (CAMPAIGN / "DEFINITION_AUDIT.md").read_text()
    theorem = (CAMPAIGN / "THEOREM.md").read_text()
    for text in (audit, theorem):
        assert "s(z)=-z" in text
        assert "psi(z)=z" in text
        assert "S_tau=-T_tau" in text
        assert "Gamma_f=E_0[Z_tau T_tau]" in text
        assert "F'_rho(0)=rho(1-Gamma_f)" in text


def test_symmetry_is_separate_from_differentiation_and_scaling():
    audit = (CAMPAIGN / "DEFINITION_AUDIT.md").read_text()
    assert "Symmetry is not needed for (5.1), (6.1), or (6.3)" in audit
    assert "Detector reflection is required for oddness" in audit
    assert "Rho scaling is exact algebra" in audit


def test_uniform_support_shift_is_only_an_edge_diagnostic():
    audit = (CAMPAIGN / "DEFINITION_AUDIT.md").read_text()
    protocol = (CAMPAIGN / "PROTOCOL.md").read_text()
    assert "translated uniform density" in audit
    assert "support moves with `e`" in audit
    assert "not a theorem confirmation" in protocol
