from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


MODULE_PATH = Path(__file__).resolve().parents[1] / "verify_synthesis.py"
SPEC = importlib.util.spec_from_file_location("verify_synthesis", MODULE_PATH)
assert SPEC and SPEC.loader
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


def test_full_synthesis_contract_without_git_scope() -> None:
    VERIFY.verify("HEAD", check_diff=False)


def test_current_implementation_diff_is_allowlisted() -> None:
    VERIFY.check_diff_scope(VERIFY.SYNTHESIS_BASE_COMMIT)


@pytest.mark.parametrize(
    "path",
    [
        "level4/final_level4_closure/results/final_decision.json",
        "closure/04_ARB_CERTIFICATE.md",
        "rebaseguard-proof/proofs/certificate.json",
        "level4/stage_d/results/d2_5_verdict.json",
    ],
)
def test_guard_rejects_frozen_scientific_or_history_paths(path: str) -> None:
    with pytest.raises(VERIFY.VerificationError, match="frozen or unapproved"):
        VERIFY.validate_changed_paths([path])


def test_guard_accepts_only_approved_presentation_and_guard_paths() -> None:
    VERIFY.validate_changed_paths(
        [
            "docs/research_synthesis/README.md",
            "docs/research_synthesis/verify_synthesis.py",
            "docs/research_synthesis/tests/test_verify_synthesis.py",
            "README.md",
            "docs/releases/SR_GAMMA_CERTIFIED_RELEASE_NOTES.md",
            "figures/final/manifest.json",
            "scripts/verify_post_level4_archive.py",
        ]
    )
