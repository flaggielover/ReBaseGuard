from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


MODULE = Path(__file__).resolve().parents[1] / "verify_publication_release.py"
SPEC = importlib.util.spec_from_file_location("verify_publication_release", MODULE)
assert SPEC and SPEC.loader
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


def test_publication_contract_without_slow_determinism_or_git_scope() -> None:
    VERIFY.verify("HEAD", diff_check=False, determinism=False)


def test_current_publication_diff_is_allowlisted() -> None:
    VERIFY.validate_changed_paths(VERIFY.changed_paths(VERIFY.BASE_COMMIT))


@pytest.mark.parametrize(
    "path",
    [
        "level4/final_level4_closure/results/final_decision.json",
        "level4/stage_d/results/d2_5_bridge.json",
        "rebaseguard-proof/proofs/certificate.json",
        "closure/04_ARB_CERTIFICATE.md",
        "rebaseguard-lean/RebaseguardLean/ReBaseGuardIdentity.lean",
    ],
)
def test_diff_guard_rejects_scientific_and_historical_paths(path: str) -> None:
    with pytest.raises(VERIFY.VerificationError, match="frozen or unapproved"):
        VERIFY.validate_changed_paths([path])


def test_diff_guard_accepts_only_publication_paths() -> None:
    VERIFY.validate_changed_paths(
        [
            "README.md",
            "figures/final/manifest.json",
            "scripts/generate_final_figures.py",
            "docs/releases/LEVEL4_RELEASE_NOTES.md",
            "docs/releases/verify_publication_release.py",
            "docs/superpowers/plans/2026-08-26-publication-finalization-implementation.md",
        ]
    )
