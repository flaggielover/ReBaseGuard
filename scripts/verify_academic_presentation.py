#!/usr/bin/env python3
"""Fail-closed verification for current academic presentation artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_COMMIT = "b04578810126d3fbc4d938a721481b1e6186b8ce"
README = ROOT / "README.md"
BRIEF_MD = ROOT / "docs/research_brief/ReBaseGuard_Research_Brief.md"
BRIEF_PDF = ROOT / "docs/research_brief/ReBaseGuard_Research_Brief.pdf"
CITATION = ROOT / "CITATION.cff"
AUTHOR = "Jingzhe Su"
AFFILIATION = "University of Electronic Science and Technology of China"
SCHOOL = "School of Information and Software Engineering"
EMAIL = "suzhea0226@gmail.com"
LEVEL4_TAG_COMMIT = "5e43336264f257c7224b622f8063eb10aad481d6"
SR_TAG_COMMIT = "b04578810126d3fbc4d938a721481b1e6186b8ce"
ALLOWED_PATHS = {
    "README.md",
    "CITATION.cff",
    "docs/releases/LICENSING_READINESS.md",
    "docs/research_synthesis/PAPER_OUTLINE.md",
    "scripts/generate_research_brief.py",
    "scripts/verify_academic_presentation.py",
}
ALLOWED_PREFIXES = ("docs/research_brief/",)
SELECTED_FIGURES = (
    "figure01_recursive_rebaselining.png",
    "figure02_derivative_instability.png",
    "figure05_p3_policy.png",
    "figure08_negative_crossing.png",
)
FORBIDDEN_ASSERTIONS = (
    r"\b(first-ever|unprecedented|globally novel)\b",
    r"\b(is|are|was|were)\s+(universally safe|universally optimal)\b",
    r"\b(production proven|production-proven|production ready|production-ready)\b",
    r"\b(is|are)\s+(detector independent|detector-independent)\b",
    r"\b(is|are)\s+(distribution free|distribution-free)\b",
    r"\boperational phase transition (is )?proved\b",
    r"\b(is|was|has been)\s+(peer-reviewed|an accepted manuscript|a published paper)\b",
)


class VerificationError(RuntimeError):
    pass


def run_git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, text=True, capture_output=True
    ).stdout.strip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def section(text: str, heading: str) -> str:
    match = re.search(
        rf"^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)", text,
        flags=re.M | re.S,
    )
    if not match:
        raise VerificationError(f"missing section: {heading}")
    return match.group(1).strip()


def check_readme_progressive_disclosure() -> None:
    text = README.read_text(encoding="utf-8")
    headings = ["Plain-language abstract", "Why this problem exists", "Results at a glance", "Core mathematical result", "Research status and reproducibility"]
    positions = [text.index(f"## {heading}") for heading in headings]
    if positions != sorted(positions):
        raise VerificationError("README science-first section order drifted")
    if text.index("LEVEL-4-CLOSED") < text.index("## Research status and reproducibility"):
        raise VerificationError("README leads with internal closure terminology")
    abstract = re.sub(r"\[[^]]+]\([^)]+\)|[*_`]", "", section(text, "Plain-language abstract"))
    words = re.findall(r"\b[\w'-]+\b", abstract)
    if not 80 <= len(words) <= 140:
        raise VerificationError(f"plain-language abstract has {len(words)} words, expected 80-140")
    why = section(text, "Why this problem exists")
    for marker in ("figure01_recursive_rebaselining.png", "data-dependent stopping time", "monitor -> alarm"):
        if marker not in why:
            raise VerificationError(f"near-top mechanism marker missing: {marker}")
    results = section(text, "Results at a glance")
    rows = [line for line in results.splitlines() if line.startswith("|")]
    if len(rows) != 9:
        raise VerificationError("results-at-a-glance table must contain seven result rows")
    required = (
        "internal project-closure designation",
        "not an external academic standard",
        "16/16 satisfied",
        "L4R-13 non-Gaussian robustness remains `PARTIAL`",
        "SR-GAMMA-CERTIFIED",
        "5.800391799508442",
        "28.781285803081492",
        "3.800391799508442",
        "0/4",
        "4/4",
        "scripts/verify_academic_presentation.py",
        "Jingzhe Su (苏靖哲)",
        SCHOOL,
        AFFILIATION,
        EMAIL,
        "License: not yet specified",
        "CITATION.cff",
        "ReBaseGuard_Research_Brief.pdf",
    )
    missing = [marker for marker in required if marker not in text]
    if missing:
        raise VerificationError(f"README presentation markers missing: {missing}")
    chronology = re.sub(r"\s+", " ", section(text, "Research status and reproducibility"))
    if not all(marker in chronology for marker in ("original Level-4 closure", "remained open", "closed later")):
        raise VerificationError("SR historical/current chronology is unclear")


def check_author_and_citation() -> None:
    cff = CITATION.read_text(encoding="utf-8")
    for marker in (
        "cff-version: 1.2.0",
        "family-names: Su",
        "given-names: Jingzhe",
        f'affiliation: "{AFFILIATION}"',
        f"email: {EMAIL}",
        "type: software",
        "rebaseguard-sr-gamma-certified",
        "2026-08-27",
    ):
        if marker not in cff:
            raise VerificationError(f"CITATION.cff marker missing: {marker}")
    prohibited = ("orcid", "doi:", "journal:", "conference:")
    if any(marker in cff.lower() for marker in prohibited):
        raise VerificationError("CITATION.cff contains unauthorized publication metadata")


def check_license_truthfulness() -> None:
    if any((ROOT / name).exists() for name in ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING", "NOTICE")):
        raise VerificationError("license file appeared without presentation-guard update")
    readiness = (ROOT / "docs/releases/LICENSING_READINESS.md").read_text(encoding="utf-8")
    for marker in (
        "License: not yet specified",
        "Source code",
        "Documentation and prose",
        "Figures",
        "Formal proofs and certificates",
        "Third-party datasets and derived evidence",
        "does not grant permission",
    ):
        if marker not in readiness:
            raise VerificationError(f"licensing-readiness marker missing: {marker}")


def check_brief() -> None:
    markdown = BRIEF_MD.read_text(encoding="utf-8")
    for marker in (AUTHOR, SCHOOL, AFFILIATION, EMAIL, "not a peer-reviewed publication", "## 1. Problem", "## 6. Negative result", "## 8. Limitations", "## 9. Reproducibility and repository", "0/4", "4/4", "License: not yet specified"):
        if marker not in markdown:
            raise VerificationError(f"Research Brief marker missing: {marker}")
    images = re.findall(r"!\[[^]]+]\(([^)]+)\)", markdown)
    if len(images) != 4:
        raise VerificationError(f"Research Brief uses {len(images)} figures, expected four")
    for target in images:
        if not (BRIEF_MD.parent / target).resolve().is_file():
            raise VerificationError(f"Research Brief image is missing: {target}")
    data = BRIEF_PDF.read_bytes()
    if not data.startswith(b"%PDF-") or len(data) < 100_000:
        raise VerificationError("Research Brief PDF is missing or implausibly small")
    pages = len(re.findall(rb"/Type\s*/Page\b", data))
    if not 2 <= pages <= 4:
        raise VerificationError(f"Research Brief PDF has {pages} pages, expected 2-4")


def check_claim_firewall() -> None:
    text = README.read_text(encoding="utf-8") + "\n" + BRIEF_MD.read_text(encoding="utf-8")
    for expression in FORBIDDEN_ASSERTIONS:
        match = re.search(expression, text, flags=re.I | re.S)
        if match:
            raise VerificationError(f"forbidden presentation claim: {match.group(0)!r}")


def markdown_links(text: str) -> list[str]:
    return [
        target.split("#", 1)[0]
        for target in re.findall(r"\[[^]]+]\(([^)]+)\)", text)
        if target and not re.match(r"^[a-z]+:", target)
    ]


def check_links_and_figures() -> None:
    for target in markdown_links(README.read_text(encoding="utf-8")):
        if not (ROOT / target).exists():
            raise VerificationError(f"README link target does not exist: {target}")
    manifest = json.loads((ROOT / "figures/final/manifest.json").read_text(encoding="utf-8"))
    by_name = {f"{row['slug']}.png": row["outputs"]["png"] for row in manifest["figures"]}
    for name in SELECTED_FIGURES:
        path = ROOT / "figures/final" / name
        if not path.is_file() or sha256(path) != by_name.get(name):
            raise VerificationError(f"selected figure provenance mismatch: {name}")


def check_historical_tags() -> None:
    expected = (("rebaseguard-level4-closed", LEVEL4_TAG_COMMIT), ("rebaseguard-sr-gamma-certified", SR_TAG_COMMIT))
    for tag, commit in expected:
        observed = run_git("rev-list", "-n", "1", tag)
        if observed != commit:
            raise VerificationError(f"historical tag moved: {tag}")


def changed_paths(base: str) -> list[str]:
    tracked = run_git("diff", "--name-only", base, "--").splitlines()
    untracked = run_git("ls-files", "--others", "--exclude-standard").splitlines()
    return sorted(set(tracked + untracked))


def validate_changed_paths(paths: list[str]) -> None:
    forbidden = [path for path in paths if path not in ALLOWED_PATHS and not any(path.startswith(prefix) for prefix in ALLOWED_PREFIXES)]
    if forbidden:
        raise VerificationError("presentation diff touches unapproved paths: " + ", ".join(forbidden))


def verify(*, base: str = BASE_COMMIT, check_diff: bool = True) -> None:
    check_readme_progressive_disclosure()
    check_author_and_citation()
    check_license_truthfulness()
    check_brief()
    check_claim_firewall()
    check_links_and_figures()
    check_historical_tags()
    if check_diff:
        validate_changed_paths(changed_paths(base))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default=BASE_COMMIT)
    parser.add_argument("--no-diff-check", action="store_true")
    args = parser.parse_args()
    try:
        verify(base=args.base, check_diff=not args.no_diff_check)
    except (VerificationError, OSError, KeyError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        print(f"ACADEMIC PRESENTATION VERIFICATION FAILED: {exc}", file=sys.stderr)
        return 1
    print("ACADEMIC PRESENTATION VERIFICATION OK")
    print("science_first=true author=Jingzhe_Su citation=true license=not_yet_specified")
    print("research_brief=2-4_pages figures=4 claims=scoped history=intact")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
