#!/usr/bin/env python3
"""Fail-closed verifier for the additive post-Level-4 SR archive release."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HISTORICAL_TAG = "rebaseguard-level4-closed"
HISTORICAL_COMMIT = "5e43336264f257c7224b622f8063eb10aad481d6"
SR_TAG = "rebaseguard-sr-gamma-certified"
SR_ROOT = "level4/closure_proofs/sr_derivative"
MANIFEST = ROOT / "docs/releases/sr_gamma_certified_archive_manifest.json"
CURRENT_DOCS = (
    "README.md",
    "docs/research_synthesis/README.md",
    "docs/research_synthesis/MAIN_THEOREM_ARCHITECTURE.md",
    "docs/research_synthesis/RESULT_DEPENDENCY_GRAPH.md",
    "docs/research_synthesis/EVIDENCE_HIERARCHY.md",
    "docs/research_synthesis/CLAIM_CATALOG.md",
    "docs/research_synthesis/LIMITATIONS_AND_OPEN_ITEMS.md",
    "docs/research_synthesis/PAPER_OUTLINE.md",
    "docs/research_synthesis/REPOSITORY_MAP.md",
    "docs/releases/SR_GAMMA_CERTIFIED_RELEASE_NOTES.md",
)
REPRODUCERS = (
    "level4/final_level4_closure/reproduce.sh",
    "level4/closure_proofs/sr_derivative/certificate/reproduce_closed_upgrade.sh",
)
FORBIDDEN_ASSERTIONS = (
    r"\b(first-ever|unprecedented|globally novel)\b",
    r"\b(is|are|was|were)\s+(universally safe|universally optimal)\b",
    r"\b(production proven|production-proven|production ready|production-ready)\b",
    r"\b(is|are)\s+(detector independent|detector-independent)\b",
    r"\b(is|are)\s+(distribution free|distribution-free)\b",
    r"\boperational phase transition (is )?proved\b",
)
TRACKED_JUNK = (
    re.compile(r"(^|/)\.DS_Store$"),
    re.compile(r"(^|/)__pycache__(/|$)"),
    re.compile(r"\.py[co]$"),
    re.compile(r"(^|/)\.pytest_cache(/|$)"),
    re.compile(r"(^|/)\.coverage$"),
)


class VerificationError(RuntimeError):
    pass


def run_git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, text=True, capture_output=True
    ).stdout.strip()


def load_json(relative: str) -> dict:
    with (ROOT / relative).open(encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def leading_decimal(value: object) -> Decimal:
    match = re.search(r"[-+]?\d+(?:\.\d+)?(?:e[-+]?\d+)?", str(value), re.I)
    if not match:
        raise VerificationError(f"no decimal value in {value!r}")
    return Decimal(match.group(0))


def check_level4_authority() -> None:
    decision = load_json("level4/final_level4_closure/results/final_decision.json")
    if decision.get("current_verdict") != "LEVEL-4-CLOSED":
        raise VerificationError("historical terminal verdict drifted")
    if decision.get("current_counts") != {"PASS": 17, "PARTIAL": 1, "FAIL": 0, "OPEN": 0}:
        raise VerificationError("historical terminal counts drifted")
    if decision.get("mandatory_requirement_count") != 16:
        raise VerificationError("historical mandatory count drifted")
    if decision.get("mandatory_counts") != {"PASS": 16, "PARTIAL": 0, "FAIL": 0, "OPEN": 0}:
        raise VerificationError("historical mandatory statuses drifted")
    if decision.get("nonmandatory_partial_ids") != ["L4R-13"]:
        raise VerificationError("historical L4R-13 boundary drifted")
    open_items = {row["id"]: row["status"] for row in decision["remaining_open_nonblockers"]}
    if open_items.get("SR-ARB-CERTIFICATE") != "OPEN":
        raise VerificationError("terminal-time SR OPEN record drifted")


def check_historical_tag() -> None:
    observed = run_git("rev-list", "-n", "1", HISTORICAL_TAG)
    if observed != HISTORICAL_COMMIT:
        raise VerificationError(
            f"historical Level-4 tag moved: expected {HISTORICAL_COMMIT}, got {observed}"
        )


def check_sr_authority() -> None:
    report = (ROOT / f"{SR_ROOT}/certificate/GAMMA_CERTIFICATE.md").read_text(encoding="utf-8")
    if "SR-GAMMA-CERTIFIED" not in report:
        raise VerificationError("SR-GAMMA-CERTIFIED authority is absent")

    a = load_json(f"{SR_ROOT}/results/sr_residual_global_a.json")
    b = load_json(f"{SR_ROOT}/results/sr_residual_global_b.json")
    contraction = load_json(f"{SR_ROOT}/results/sr_monotone_contraction.json")
    contraction_audit = load_json(f"{SR_ROOT}/results/sr_monotone_contraction_audit.json")

    for record, status in ((a, "GLOBAL_A_CERTIFIED"), (b, "GLOBAL_B_CERTIFIED")):
        if record.get("status") != status or record.get("precision_bits") != 192:
            raise VerificationError(f"SR residual authority drifted from {status} at 192 bits")
        if record.get("completed_fundamental_cells") != 1210:
            raise VerificationError("SR completed patch count drifted")
        if record.get("expected_fundamental_cells") != 1210:
            raise VerificationError("SR expected patch count drifted")
        if record.get("global_reachable_cover_complete") is not True:
            raise VerificationError("SR global cover is not complete")
        if record.get("sampled_grid_used") is not False:
            raise VerificationError("SR certificate uses sampled-state inference")

    if a.get("candidate_degree") != 16:
        raise VerificationError("SR candidate degree drifted")
    if leading_decimal(a["epsilon_a"]) != Decimal("4.504390937831505821584329894078802406556132351891806631e-6"):
        raise VerificationError("epsilon_a drifted")
    if leading_decimal(b["epsilon_b"]) != Decimal("0.004003813425152367039816387453712930372411790871914867036"):
        raise VerificationError("epsilon_b drifted")

    propagation = b.get("propagation", {})
    lower = leading_decimal(propagation.get("gamma_interval", {}).get("lower_endpoint_enclosure"))
    upper = leading_decimal(propagation.get("gamma_interval", {}).get("upper_endpoint_enclosure"))
    margin = leading_decimal(propagation.get("lower_endpoint_margin_above_two"))
    if lower != Decimal("5.80039179950844233566163341719178681375064361627654095"):
        raise VerificationError("Gamma_SR lower endpoint drifted")
    if upper != Decimal("28.78128580308149205926606197637053008078060638372345905"):
        raise VerificationError("Gamma_SR upper endpoint drifted")
    if margin != Decimal("3.80039179950844233566163341719178681375064361627654095"):
        raise VerificationError("Gamma_SR margin drifted")
    if not (lower > 2 and propagation.get("strict_lower_endpoint_above_two") is True):
        raise VerificationError("Gamma_SR strict lower bound is not certified")
    if propagation.get("resolvent_bound") != "25000/19":
        raise VerificationError("propagated resolvent bound drifted")
    if contraction_audit.get("status") != "PASS":
        raise VerificationError("independent resolvent audit is not PASS")
    if contraction.get("resolvent_bound", {}).get("ball") is None:
        raise VerificationError("resolvent certificate is absent")

    expected_stats = (
        (a, 96295, 62, 94, 2, "p17_m11"),
        (b, 50947, 37, 48, 1, "p45_m04"),
    )
    for record, total, minimum, maximum, depth, worst in expected_stats:
        stats = record["subdivision_statistics"]
        observed = (
            stats["total_innovation_intervals"],
            stats["minimum_innovation_intervals"],
            stats["maximum_innovation_intervals"],
            stats["maximum_innovation_depth"],
            record["worst_patch"],
        )
        if observed != (total, minimum, maximum, depth, worst):
            raise VerificationError("SR subdivision statistics drifted")


def historical_sr_paths() -> list[str]:
    output = run_git("ls-tree", "-r", "--name-only", HISTORICAL_TAG, SR_ROOT)
    return output.splitlines() if output else []


def check_original_sr_files() -> None:
    paths = historical_sr_paths()
    if len(paths) != 52:
        raise VerificationError(f"historical SR tree has {len(paths)} files, expected 52")
    for relative in paths:
        current = ROOT / relative
        if not current.is_file():
            raise VerificationError(f"historical SR path missing: {relative}")
        expected_blob = run_git("rev-parse", f"{HISTORICAL_TAG}:{relative}")
        observed_blob = run_git("hash-object", relative)
        if observed_blob != expected_blob:
            raise VerificationError(f"historical SR file changed: {relative}")
    current_paths = run_git("ls-tree", "-r", "--name-only", "HEAD", SR_ROOT).splitlines()
    if len(current_paths) != 92:
        raise VerificationError(f"current tracked SR tree has {len(current_paths)} files, expected 92")
    if len(set(current_paths) - set(paths)) != 40:
        raise VerificationError("current SR tree is not the expected 52 + 40 additive layout")


def validate_current_doc_text(relative: str, content: str) -> None:
    normalized = re.sub(r"\s+", " ", content)
    lower = normalized.lower()
    if "sr" in lower and "open" in lower:
        for paragraph in re.split(r"\n\s*\n", content):
            p = re.sub(r"\s+", " ", paragraph).lower()
            if "sr" in p and "open" in p and not any(
                marker in p
                for marker in ("terminal level-4", "historical", "original level-4", "at level 4")
            ):
                raise VerificationError(f"unqualified current SR OPEN wording in {relative}")
    stale = (
        "gamma_sr>2 is numerical evidence only",
        "not arb-certified",
        "sr arb certificate remains open",
    )
    if any(marker in lower for marker in stale):
        raise VerificationError(f"stale current SR evidence wording in {relative}")


def check_current_documentation() -> None:
    combined: list[str] = []
    for relative in CURRENT_DOCS:
        path = ROOT / relative
        if not path.is_file():
            raise VerificationError(f"missing current reviewer document: {relative}")
        content = path.read_text(encoding="utf-8")
        validate_current_doc_text(relative, content)
        if not relative.endswith("CLAIM_CATALOG.md"):
            combined.append(content)
    text = "\n".join(combined)
    for marker in (
        "SR-GAMMA-CERTIFIED",
        "5.800391799508442",
        "28.781285803081492",
        "3.800391799508442",
        "post-Level-4",
    ):
        if marker not in text:
            raise VerificationError(f"current documentation marker missing: {marker}")
    for expression in FORBIDDEN_ASSERTIONS:
        match = re.search(expression, text, flags=re.I | re.S)
        if match:
            raise VerificationError(f"forbidden claim escalation: {match.group(0)!r}")


def check_reproducers() -> None:
    for relative in REPRODUCERS:
        path = ROOT / relative
        if not path.is_file():
            raise VerificationError(f"missing reproducer: {relative}")
        if not path.stat().st_mode & 0o111:
            raise VerificationError(f"reproducer is not executable: {relative}")


def check_archive_manifest() -> None:
    manifest = load_json(str(MANIFEST.relative_to(ROOT)))
    if manifest.get("schema") != "rebaseguard.sr-gamma-certified-archive.v1":
        raise VerificationError("archive manifest schema drifted")
    if manifest.get("historical_level4", {}).get("commit") != HISTORICAL_COMMIT:
        raise VerificationError("archive manifest historical commit drifted")
    if manifest.get("historical_level4", {}).get("tag") != HISTORICAL_TAG:
        raise VerificationError("archive manifest historical tag drifted")
    if manifest.get("sr_release", {}).get("tag") != SR_TAG:
        raise VerificationError("archive manifest SR tag drifted")
    if manifest.get("original_sr_files", {}).get("count") != 52:
        raise VerificationError("archive manifest original file count drifted")
    additive = manifest.get("additive_sr_files", {})
    if additive.get("count") != 40 or len(additive.get("sha256", {})) != 40:
        raise VerificationError("archive manifest additive inventory drifted")
    for group in (manifest.get("certificate_files", {}), additive.get("sha256", {}), manifest.get("integration_files", {})):
        for relative, expected in group.items():
            path = ROOT / relative
            if not path.is_file() or sha256(path) != expected:
                raise VerificationError(f"archive hash mismatch: {relative}")


def check_repository_hygiene(*, allow_dirty: bool) -> None:
    tracked = run_git("ls-files").splitlines()
    junk = [path for path in tracked if any(pattern.search(path) for pattern in TRACKED_JUNK)]
    if junk:
        raise VerificationError("tracked generated junk: " + ", ".join(junk))
    if not allow_dirty:
        status = run_git("status", "--porcelain")
        if status:
            raise VerificationError("Git worktree is not clean")


def check_sr_tag(*, pre_release: bool) -> None:
    if pre_release:
        return
    target = run_git("rev-list", "-n", "1", SR_TAG)
    if target != run_git("rev-parse", "HEAD"):
        raise VerificationError("SR release tag does not resolve to HEAD")


def verify(*, pre_release: bool = False, allow_dirty: bool = False) -> None:
    check_level4_authority()
    check_historical_tag()
    check_sr_authority()
    check_original_sr_files()
    check_current_documentation()
    check_reproducers()
    check_archive_manifest()
    check_repository_hygiene(allow_dirty=allow_dirty)
    check_sr_tag(pre_release=pre_release)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pre-release",
        action="store_true",
        help="skip only the new-tag-to-HEAD assertion before the tag exists",
    )
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help="allow a dirty worktree during controlled pre-commit verification",
    )
    args = parser.parse_args()
    try:
        verify(pre_release=args.pre_release, allow_dirty=args.allow_dirty)
    except (VerificationError, OSError, KeyError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        print(f"POST-LEVEL-4 ARCHIVE VERIFICATION FAILED: {exc}", file=sys.stderr)
        return 1
    print("POST-LEVEL-4 ARCHIVE VERIFICATION OK")
    print("level4=LEVEL-4-CLOSED sr=SR-GAMMA-CERTIFIED original_sr=52 additive_sr=40")
    print("gamma_lower_gt_2=true covers=a:1210/1210,b:1210/1210")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
