"""The prose must say what the artifacts say, and must not over-claim."""

from __future__ import annotations

import pytest

DOCS = (
    "README.md", "THEOREM.md", "PROOF.md", "ASSUMPTION_AUDIT.md",
    "NUMERICAL_CORRESPONDENCE.md", "EVIDENCE_BOUNDARY.md",
    "LEAN_CORRESPONDENCE.md", "PROVENANCE.md", "NOVELTY_AUDIT.md",
    "ADVERSARIAL_REVIEW.md", "INDEPENDENT_ADJUDICATION.md",
    "CLOSURE_REPORT.md", "CODEX_HANDOFF.md", "P5_HANDOFF.md",
)

#: Phrases that could never be legitimate here.  Negated forms such as "not
#: detector universal" are the point of several documents, so the patterns are
#: written as positive assertions only.
FORBIDDEN = (
    "is distribution-free",
    "is distribution free",
    "is detector-universal",
    "is detector universal",
    "holds for every distribution",
    "proves global stability",
    "first proof in the literature",
    "novel theorem",
)


@pytest.mark.parametrize("name", DOCS)
def test_document_exists_and_is_substantive(campaign, name):
    path = campaign / name
    assert path.exists(), name
    assert len(path.read_text()) > 700, name


@pytest.mark.parametrize("name", DOCS)
def test_no_forbidden_overclaim(campaign, name):
    text = (campaign / name).read_text().lower()
    for phrase in FORBIDDEN:
        assert phrase not in text, (name, phrase)


def test_theorem_states_both_proved_failure_modes(campaign):
    text = (campaign / "THEOREM.md").read_text()
    assert "moving support" in text
    assert "no first moment" in text.lower() or "first moment" in text
    assert "uniform" in text.lower() and "cauchy" in text.lower()


def test_theorem_names_the_gaussian_specific_steps(campaign):
    text = (campaign / "ASSUMPTION_AUDIT.md").read_text()
    assert "Gaussian-specific identities" in text
    assert "psi(z) = z" in text


def test_proof_does_not_defer_to_standard_regularity(campaign):
    text = (campaign / "PROOF.md").read_text().lower()
    assert "standard regularity conditions" not in text.replace(
        "deferred to \"standard regularity conditions\"", ""
    ) or "nothing below is deferred" in text


def test_novelty_audit_declines_to_declare_novelty(campaign):
    text = (campaign / "NOVELTY_AUDIT.md").read_text()
    assert "NOVELTY-NOT-ADJUDICATED" in text


def test_evidence_boundary_separates_the_four_layers(campaign):
    text = (campaign / "EVIDENCE_BOUNDARY.md").read_text()
    for layer in ("analytic theorem", "floating-point", "finite-support",
                  "infinite-horizon"):
        assert layer in text.lower() or layer.title() in text


def test_closure_report_matches_the_machine_verdict(campaign, closure):
    text = (campaign / "CLOSURE_REPORT.md").read_text()
    assert closure["verdict"] in text


def test_codex_handoff_tells_codex_not_to_trust_the_verdict(campaign):
    text = (campaign / "CODEX_HANDOFF.md").read_text()
    assert "do not trust" in text.lower()
    assert "independently" in text.lower()


def test_p5_material_is_only_a_handoff_note(campaign):
    text = (campaign / "P5_HANDOFF.md").read_text()
    assert len(text) < 9000
    for word in ("period-2 orbit is proved", "we prove hysteresis"):
        assert word not in text
