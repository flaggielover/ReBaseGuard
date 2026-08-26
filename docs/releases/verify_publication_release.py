#!/usr/bin/env python3
"""Fail-closed verification for the publication-facing Level-4 release."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE_COMMIT = "b011c5c"
FINAL = ROOT / "figures" / "final"
GENERATOR = ROOT / "scripts" / "generate_final_figures.py"
PYTHON = ROOT / "level4" / ".venv" / "bin" / "python"
ALLOWED_DIFF_PATHS = {
    "README.md",
    "docs/superpowers/plans/2026-08-26-publication-finalization-implementation.md",
    "scripts/generate_final_figures.py",
}
ALLOWED_DIFF_PREFIXES = (
    "figures/final/",
    "docs/releases/",
)
REQUIRED_README_MARKERS = (
    "LEVEL-4-CLOSED",
    "16/16 mandatory requirements passed",
    "17 PASS, 1 PARTIAL, 0 FAIL, and 0 OPEN",
    "L4R-13",
    "rigorous SR local-instability Arb certificate remains `OPEN`",
    "Stage E is **0/3**, V2 is **1/3**, and V3 is **2/2**",
    "**0/4**",
    "**4/4**",
    "not an external academic certification",
    "No explicit license is currently included",
)
BANNED_ASSERTIONS = (
    r"\b(first-ever|unprecedented|globally novel)\b",
    r"\b(is|are|was|were)\s+(universally safe|universally optimal)\b",
    r"\b(production proven|production-proven)\b",
    r"\b(detector independent|detector-independent)\b",
    r"\b(distribution free|distribution-free)\b",
    r"\boperational phase transition (is )?proved\b",
    r"\bgamma[_ ]?sr\s*(>|is).{0,30}\barb[- ]certified\b",
)


class VerificationError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(relative: str) -> dict:
    with (ROOT / relative).open(encoding="utf-8") as handle:
        return json.load(handle)


def check_terminal_state() -> None:
    decision = load_json("level4/final_level4_closure/results/final_decision.json")
    if decision.get("current_verdict") != "LEVEL-4-CLOSED":
        raise VerificationError("terminal verdict drifted")
    if decision.get("current_counts") != {"PASS": 17, "PARTIAL": 1, "FAIL": 0, "OPEN": 0}:
        raise VerificationError("terminal requirement counts drifted")
    if decision.get("mandatory_counts") != {"PASS": 16, "PARTIAL": 0, "FAIL": 0, "OPEN": 0}:
        raise VerificationError("mandatory requirement counts drifted")
    if decision.get("mandatory_requirement_count") != 16:
        raise VerificationError("mandatory requirement total drifted")
    if decision.get("nonmandatory_partial_ids") != ["L4R-13"]:
        raise VerificationError("L4R-13 boundary drifted")
    open_items = {row["id"]: row["status"] for row in decision["remaining_open_nonblockers"]}
    if open_items.get("SR-ARB-CERTIFICATE") != "OPEN":
        raise VerificationError("SR Arb certificate boundary drifted")


def check_manifest() -> None:
    manifest = load_json("figures/final/manifest.json")
    if manifest.get("schema") != "rebaseguard.final-figures.v1":
        raise VerificationError("figure manifest schema drifted")
    if manifest.get("new_science_run") is not False or manifest.get("network_used") is not False:
        raise VerificationError("figure manifest does not preserve presentation-only boundary")
    figures = manifest.get("figures", [])
    if len(figures) != 8:
        raise VerificationError(f"expected 8 figures, found {len(figures)}")
    expected_ids = [f"Figure {index}" for index in range(1, 9)]
    if [row.get("id") for row in figures] != expected_ids:
        raise VerificationError("figure IDs are missing, duplicated, or reordered")
    for row in figures:
        slug = row["slug"]
        for extension in ("png", "svg"):
            output = FINAL / f"{slug}.{extension}"
            if not output.is_file():
                raise VerificationError(f"missing figure output: {output.relative_to(ROOT)}")
            if sha256(output) != row["outputs"][extension]:
                raise VerificationError(f"figure hash mismatch: {output.relative_to(ROOT)}")
        for source in row["sources"]:
            path = ROOT / source
            if not path.is_file():
                raise VerificationError(f"missing figure source: {source}")
            if sha256(path) != row["source_sha256"][source]:
                raise VerificationError(f"frozen source hash mismatch: {source}")
        for field in ("purpose", "transformation", "evidence", "paper_section", "limitation"):
            if not row.get(field):
                raise VerificationError(f"{row['id']} lacks {field}")


def check_generator_boundary() -> None:
    tree = ast.parse(GENERATOR.read_text(encoding="utf-8"))
    forbidden_modules = {"requests", "urllib", "httpx", "socket", "subprocess"}
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    overlap = imports & forbidden_modules
    if overlap:
        raise VerificationError(f"figure generator imports network/process modules: {sorted(overlap)}")
    text = GENERATOR.read_text(encoding="utf-8")
    if "level4.simulator" in text or "MultiCycleOracle" in text:
        raise VerificationError("figure generator imports scientific simulation code")


def markdown_links(text: str) -> list[str]:
    return [
        target.split("#", 1)[0]
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)
        if target and not re.match(r"^[a-z]+://", target)
    ]


def check_readme_and_release() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    notes = (ROOT / "docs/releases/LEVEL4_RELEASE_NOTES.md").read_text(encoding="utf-8")
    combined = readme + "\n" + notes
    normalized_readme = re.sub(r"\s+", " ", readme)
    missing = [marker for marker in REQUIRED_README_MARKERS if marker not in normalized_readme]
    if missing:
        raise VerificationError(f"README publication boundaries missing: {missing}")
    for expression in BANNED_ASSERTIONS:
        match = re.search(expression, combined, flags=re.IGNORECASE | re.DOTALL)
        if match:
            raise VerificationError(f"prohibited publication assertion: {match.group(0)!r}")
    for target in markdown_links(readme):
        if not (ROOT / target).exists():
            raise VerificationError(f"README link target does not exist: {target}")
    required_notes = (
        "49cf742",
        "37926db",
        "0/4 preselected metrics",
        "Stage E 0/3, V2 1/3, and V3 2/2",
        "No DOI is assigned",
    )
    if any(marker not in notes for marker in required_notes):
        raise VerificationError("release notes omit a required result or metadata boundary")


def check_frozen_result_visibility() -> None:
    external = load_json("level4/closure_proofs/external_validation_v3/results/decision.json")
    observed = (
        external["v3_joint_support"],
        external["cross_campaign_success_count"],
        external["cross_campaign_required"],
    )
    if observed != ("2/2", 3, 2):
        raise VerificationError("external-validation counts drifted")
    aggregation = (
        ROOT / "level4/closure_proofs/external_validation_v3/CROSS_CAMPAIGN_AGGREGATION.md"
    ).read_text(encoding="utf-8")
    for marker in ("Stage E", "V2", "V3", "Household power", "Online Retail II"):
        if marker not in aggregation:
            raise VerificationError(f"external-validation record omits {marker}")
    negative = load_json(
        "level4/closure_proofs/l4r12_operational_crossing/results/evidence_assessment.json"
    )
    if negative["operational_result"]["metrics_peaking_at_crossing"] != 0:
        raise VerificationError("negative crossing peak count drifted")
    if negative["operational_result"]["metrics_monotone_in_log_m"] != 4:
        raise VerificationError("negative crossing monotonicity count drifted")


def changed_paths(base: str) -> list[str]:
    tracked = subprocess.run(
        ["git", "diff", "--name-only", base, "--"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    ).stdout.splitlines()
    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    ).stdout.splitlines()
    return sorted(set(tracked + untracked))


def validate_changed_paths(paths: list[str]) -> None:
    forbidden = [
        path
        for path in paths
        if path not in ALLOWED_DIFF_PATHS
        and not any(path.startswith(prefix) for prefix in ALLOWED_DIFF_PREFIXES)
    ]
    if forbidden:
        raise VerificationError(
            "publication diff touches frozen or unapproved paths: " + ", ".join(forbidden)
        )


def check_determinism() -> None:
    with tempfile.TemporaryDirectory(prefix="rebaseguard-figures-a-") as first_dir:
        with tempfile.TemporaryDirectory(prefix="rebaseguard-figures-b-") as second_dir:
            first = Path(first_dir)
            second = Path(second_dir)
            for output in (first, second):
                subprocess.run(
                    [str(PYTHON), str(GENERATOR), "--output-dir", str(output)],
                    cwd=ROOT,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                )
            first_hashes = {
                path.name: sha256(path) for path in first.iterdir() if path.is_file()
            }
            second_hashes = {
                path.name: sha256(path) for path in second.iterdir() if path.is_file()
            }
            if first_hashes != second_hashes:
                raise VerificationError("two independent figure generations differ")
            final_hashes = {
                path.name: sha256(path) for path in FINAL.iterdir() if path.is_file()
            }
            if first_hashes != final_hashes:
                raise VerificationError("committed final figures differ from a clean regeneration")


def verify(base: str, *, diff_check: bool = True, determinism: bool = True) -> None:
    check_terminal_state()
    check_manifest()
    check_generator_boundary()
    check_readme_and_release()
    check_frozen_result_visibility()
    if determinism:
        check_determinism()
    if diff_check:
        validate_changed_paths(changed_paths(base))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default=BASE_COMMIT)
    parser.add_argument("--no-diff-check", action="store_true")
    parser.add_argument("--no-determinism-check", action="store_true")
    args = parser.parse_args()
    try:
        verify(
            args.base,
            diff_check=not args.no_diff_check,
            determinism=not args.no_determinism_check,
        )
    except (VerificationError, OSError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        print(f"PUBLICATION RELEASE VERIFICATION FAILED: {exc}", file=sys.stderr)
        return 1
    print("PUBLICATION RELEASE VERIFICATION OK")
    print("figures=8 formats=PNG+SVG terminal=LEVEL-4-CLOSED mandatory=16/16")
    print("deterministic=true network_science=false diff_scope=presentation-only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
