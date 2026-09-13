"""Regression tests for the presentation verifier's publication baseline.

Covers the migration that separated the publication diff baseline from the
historical SR release-tag identity pin, and the PDF integrity contract.
"""
from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[3]
MODULE = ROOT / "scripts/verify_academic_presentation.py"
SPEC = importlib.util.spec_from_file_location("verify_academic_presentation", MODULE)
assert SPEC and SPEC.loader
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, text=True,
                          capture_output=True).stdout.strip()


# --- 1. the current legitimate publication diff passes ---------------------

def test_current_publication_diff_passes():
    V.validate_changed_paths(V.changed_paths(V.CURRENT_PUBLICATION_BASE_COMMIT))


def test_full_verify_with_diff_check_passes():
    V.verify()


# --- 2. an allowed presentation file passes --------------------------------

@pytest.mark.parametrize("path", [
    "README.md",
    "docs/research_brief/ReBaseGuard_Research_Brief.md",
    "docs/research_brief/ReBaseGuard_Research_Brief.pdf",
    "figures/final/figure09_campaign_lineage.png",
    "figures/final/manifest.json",
    "docs/releases/PUBLICATION_REMAINDERS.md",
    "docs/releases/publication-requirements.txt",
    "scripts/verify_academic_presentation.py",
])
def test_allowed_presentation_path_passes(path):
    V.validate_changed_paths([path])


# --- 3. a protected or scientific file fails -------------------------------

@pytest.mark.parametrize("path", [
    "level4/closure_proofs/p4_theory_generalization/THEOREM.md",
    "level4/closure_proofs/p4_theory_generalization/configs/P4_PROTOCOL.json",
    "level4/closure_proofs/p4zb_skewnormal4_k7/results/final_coverage.json",
    "level4/closure_proofs/p4z_final_closure/final_closure.json",
    "rebaseguard-lean/Rebaseguard/Basic.lean",
    "Mathematical_proof/anything.tex",
    "docs/releases/LEVEL4_RELEASE_NOTES.md",
])
def test_protected_or_scientific_path_fails(path):
    with pytest.raises(V.VerificationError, match="unapproved paths"):
        V.validate_changed_paths([path])


def test_allowlist_is_not_broadened_into_a_whole_directory():
    """docs/releases/ must be allowed file by file, never as a prefix."""
    assert V.ALLOWED_PREFIXES == ("docs/research_brief/", "figures/final/")
    with pytest.raises(V.VerificationError):
        V.validate_changed_paths(["docs/releases/LEVEL4_RELEASE_CHECKLIST.md"])


# --- 4. the historical SR tag identity stays separately pinned -------------

def test_sr_certified_tag_identity_is_preserved_and_separate():
    assert V.SR_CERTIFIED_TAG_COMMIT == "b04578810126d3fbc4d938a721481b1e6186b8ce"
    assert git("rev-list", "-n", "1", "rebaseguard-sr-gamma-certified") == \
        V.SR_CERTIFIED_TAG_COMMIT
    assert V.CURRENT_PUBLICATION_BASE_COMMIT != V.SR_CERTIFIED_TAG_COMMIT, \
        "the publication baseline must not be conflated with the release tag"
    V.check_historical_tags()


def test_level4_tag_identity_is_preserved():
    assert git("rev-list", "-n", "1", "rebaseguard-level4-closed") == \
        V.LEVEL4_TAG_COMMIT


def test_publication_baseline_is_an_ancestor_of_the_current_tree():
    """The baseline must be a real, reachable commit in this lineage."""
    assert git("cat-file", "-t", V.CURRENT_PUBLICATION_BASE_COMMIT) == "commit"
    subprocess.run(["git", "merge-base", "--is-ancestor",
                    V.CURRENT_PUBLICATION_BASE_COMMIT, "HEAD"],
                   cwd=ROOT, check=True)


def test_the_old_conflated_baseline_would_have_failed():
    """Documents why the migration was necessary, on the real repository."""
    with pytest.raises(V.VerificationError, match="unapproved paths"):
        V.validate_changed_paths(V.changed_paths(V.SR_CERTIFIED_TAG_COMMIT))


# --- 5. the PDF hash contract catches a wrong PDF --------------------------

def test_brief_pdf_matches_its_pinned_hash():
    assert V.sha256(V.BRIEF_PDF) == V.BRIEF_PDF_SHA256
    V.check_brief()


def test_an_incorrect_pdf_is_caught(tmp_path, monkeypatch):
    wrong = tmp_path / "wrong.pdf"
    wrong.write_bytes(V.BRIEF_PDF.read_bytes() + b"\n% tampered\n")
    monkeypatch.setattr(V, "BRIEF_PDF", wrong)
    with pytest.raises(V.VerificationError):
        V.check_brief()


def test_pdf_hash_constant_is_not_a_placeholder():
    assert len(V.BRIEF_PDF_SHA256) == 64
    assert V.BRIEF_PDF_SHA256 != "0" * 64
    assert V.BRIEF_PDF_SHA256 != \
        "8a28709e67810f62850c897f96c2a973415a3308ebc6df51dd9bf3ad121a9f19", \
        "still pinned to the pre-publication PDF"


# --- the publication environment is pinned ---------------------------------

def test_publication_environment_is_pinned():
    req = ROOT / "docs/releases/publication-requirements.txt"
    text = req.read_text()
    for dep in ("reportlab==", "matplotlib==", "numpy=="):
        assert dep in text, f"{dep} not pinned"


def test_pinned_reportlab_matches_the_installed_renderer():
    reportlab = pytest.importorskip("reportlab")
    req = (ROOT / "docs/releases/publication-requirements.txt").read_text()
    assert f"reportlab=={reportlab.Version}" in req, (
        f"installed reportlab {reportlab.Version} is not the pinned version; "
        "re-render and re-pin, or install the pin")
