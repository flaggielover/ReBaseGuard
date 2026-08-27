from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


MODULE = Path(__file__).resolve().parents[3] / "scripts/verify_academic_presentation.py"
SPEC = importlib.util.spec_from_file_location("verify_academic_presentation", MODULE)
assert SPEC and SPEC.loader
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


def test_current_presentation_contract_without_git_scope() -> None:
    VERIFY.verify(check_diff=False)


def test_current_diff_is_presentation_only() -> None:
    VERIFY.validate_changed_paths(VERIFY.changed_paths(VERIFY.BASE_COMMIT))


@pytest.mark.parametrize(
    "path",
    [
        "level4/final_level4_closure/results/final_decision.json",
        "level4/closure_proofs/sr_derivative/certificate/GAMMA_CERTIFICATE.md",
        "rebaseguard-lean/RebaseguardLean/ReBaseGuardIdentity.lean",
        "figures/final/figure01_recursive_rebaselining.png",
        "docs/releases/LEVEL4_RELEASE_NOTES.md",
    ],
)
def test_guard_rejects_scientific_and_historical_paths(path: str) -> None:
    with pytest.raises(VERIFY.VerificationError, match="unapproved paths"):
        VERIFY.validate_changed_paths([path])


def test_guard_accepts_expected_presentation_paths() -> None:
    VERIFY.validate_changed_paths(
        [
            "README.md",
            "CITATION.cff",
            "docs/releases/LICENSING_READINESS.md",
            "docs/research_brief/ReBaseGuard_Research_Brief.md",
            "docs/research_brief/ReBaseGuard_Research_Brief.pdf",
            "docs/research_synthesis/PAPER_OUTLINE.md",
            "scripts/generate_research_brief.py",
            "scripts/verify_academic_presentation.py",
        ]
    )
