#!/usr/bin/env python3
"""Read-only verification for the final ReBaseGuard research synthesis."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SYNTHESIS = ROOT / "docs" / "research_synthesis"
SYNTHESIS_BASE_COMMIT = "14984e2c1a818601ee668316ed07a3fa67581474"
REQUIRED_DOCS = {
    "README.md",
    "MAIN_THEOREM_ARCHITECTURE.md",
    "RESULT_DEPENDENCY_GRAPH.md",
    "EVIDENCE_HIERARCHY.md",
    "DEFINITIONS_AND_NOTATION.md",
    "CLAIM_CATALOG.md",
    "LIMITATIONS_AND_OPEN_ITEMS.md",
    "PAPER_OUTLINE.md",
    "FIGURE_PLAN.md",
    "REPOSITORY_MAP.md",
}
ALLOWED_DIFF_PREFIXES = (
    "README.md",
    "docs/research_synthesis/",
    "docs/releases/",
    "figures/final/README.md",
    "figures/final/manifest.json",
    "scripts/verify_post_level4_archive.py",
)
PATH_RE = re.compile(
    r"`((?:closure|level4|rebaseguard-lean|rebaseguard-proof|scripts)/[^`\n]+)`"
)
BANNED_ASSERTIONS = (
    "we are the first",
    "first-ever",
    "is unprecedented",
    "proves an operational phase transition",
    "is production-proven",
    "is universally safe",
    "is detector-independent",
    "is distribution-free",
)


class VerificationError(RuntimeError):
    pass


def load_json(relative: str) -> dict:
    with (ROOT / relative).open(encoding="utf-8") as handle:
        return json.load(handle)


def check_required_documents() -> None:
    missing = sorted(name for name in REQUIRED_DOCS if not (SYNTHESIS / name).is_file())
    if missing:
        raise VerificationError(f"missing synthesis documents: {missing}")


def check_terminal_state() -> None:
    decision = load_json("level4/final_level4_closure/results/final_decision.json")
    expected_counts = {"PASS": 17, "PARTIAL": 1, "FAIL": 0, "OPEN": 0}
    expected_mandatory = {"PASS": 16, "PARTIAL": 0, "FAIL": 0, "OPEN": 0}
    if decision.get("current_verdict") != "LEVEL-4-CLOSED":
        raise VerificationError("terminal verdict drifted from LEVEL-4-CLOSED")
    if decision.get("current_counts") != expected_counts:
        raise VerificationError("terminal 18-row counts drifted")
    if decision.get("mandatory_requirement_count") != 16:
        raise VerificationError("mandatory requirement count drifted")
    if decision.get("mandatory_counts") != expected_mandatory:
        raise VerificationError("mandatory status counts drifted")
    if decision.get("nonmandatory_partial_ids") != ["L4R-13"]:
        raise VerificationError("L4R-13 is not the sole nonmandatory partial")
    open_items = {row["id"]: row for row in decision.get("remaining_open_nonblockers", [])}
    if open_items.get("SR-ARB-CERTIFICATE", {}).get("status") != "OPEN":
        raise VerificationError("SR Arb optional rigor upgrade is not OPEN")

    sr = load_json("level4/closure_proofs/sr_derivative/results/decision.json")
    serialized = json.dumps(sr, sort_keys=True)
    required_sr_markers = (
        "SR-DERIVATIVE-CLOSED",
        "CONFIRMATORY NUMERICAL",
        "OPEN",
    )
    if not all(marker in serialized for marker in required_sr_markers):
        raise VerificationError("SR theorem/numerical/Arb evidence boundary drifted")
    if abs(sr["numerical_correspondence"]["Gamma_SR_estimate"] - 17.291320922042853) > 1e-12:
        raise VerificationError("confirmatory Gamma_SR estimate drifted")

    sr_certificate = (
        ROOT / "level4/closure_proofs/sr_derivative/certificate/GAMMA_CERTIFICATE.md"
    ).read_text(encoding="utf-8")
    for marker in (
        "SR-GAMMA-CERTIFIED",
        "5.8003917995084423356616334171917868138",
        "28.781285803081492059266061976370530081",
        "3.8003917995084423356616334171917868138",
    ):
        if marker not in sr_certificate:
            raise VerificationError(f"post-Level-4 SR certificate marker missing: {marker}")


def check_authoritative_values() -> None:
    certificate = load_json("rebaseguard-proof/proofs/certificate.json")
    if not certificate["Gamma_lower"].startswith("3.924348200582897"):
        raise VerificationError("Gamma_CUSUM lower endpoint drifted")
    if not certificate["Gamma_upper"].startswith("27.849382127546703"):
        raise VerificationError("Gamma_CUSUM upper endpoint drifted")
    if certificate.get("proof_status") != "CERTIFIED":
        raise VerificationError("Gamma_CUSUM certificate is not certified")

    period2 = load_json("level4/stage_b/certificate/period2_certificate.json")["theorem"]
    if period2["root_interval"] != [1.0287242887184211, 1.0447242887184212]:
        raise VerificationError("period-two root interval drifted")
    if period2["lambda2"] != [0.10814763581379079, 0.832531705019702]:
        raise VerificationError("period-two multiplier interval drifted")

    d4 = load_json("level4/closure_proofs/d4_phase_map/results/decision.json")
    crossing = d4["gamma_equals_2_crossings"][0]
    if crossing["bracket"] != [70, 72]:
        raise VerificationError("D4 crossing bracket drifted")
    if abs(crossing["m_crossing_log_linear"] - 71.41938616943077) > 1e-12:
        raise VerificationError("D4 crossing interpolation drifted")

    policy = load_json("level4/closure_proofs/l4r06_policy/results/scientific_findings.json")
    actions = policy["policy"]["actions"]
    action_pairs = [(row["m"], row["rho"]) for row in actions]
    expected_actions = [
        (1, 0.05364218801989182),
        (20, 0.24541780396034488),
        (70, 0.7819935545467208),
        (100, 1.0),
    ]
    if action_pairs != expected_actions or not policy.get("saturated_m100_identity"):
        raise VerificationError("P3 action table or m=100 saturation drifted")
    if any(policy[f"H6-{index}"]["status"] != "PASS" for index in range(1, 6)):
        raise VerificationError("P3 primary H6 family drifted")
    if len(policy.get("secondary_epsilon_0.05_failures", [])) != 2:
        raise VerificationError("P3 secondary unfavorable count drifted")

    negative = load_json(
        "level4/closure_proofs/l4r12_operational_crossing/results/evidence_assessment.json"
    )
    if negative["operational_design"]["n_replicates"] != 20000:
        raise VerificationError("operational-crossing replicate count drifted")
    result = negative["operational_result"]
    if result["metrics_peaking_at_crossing"] != 0 or result["metrics_monotone_in_log_m"] != 4:
        raise VerificationError("operational-crossing negative result drifted")
    if negative["crossing"]["stage_d_bracket"] != [50, 75]:
        raise VerificationError("Stage-D crossing bracket drifted")
    if abs(negative["crossing"]["stage_d_interpolated"] - 72.18925933962045) > 1e-12:
        raise VerificationError("Stage-D crossing interpolation drifted")

    external = load_json("level4/closure_proofs/external_validation_v3/results/decision.json")
    expected_external = ("2/2", 3, 2)
    observed_external = (
        external["v3_joint_support"],
        external["cross_campaign_success_count"],
        external["cross_campaign_required"],
    )
    if observed_external != expected_external:
        raise VerificationError("external-validation task counts drifted")

    novelty = load_json("level4/closure_proofs/novelty_verification/results/decision.json")
    search = load_json("level4/closure_proofs/novelty_verification/results/search_manifest.json")
    expected_novelty = ("N2", 33, 0, 9, 36)
    observed_novelty = (
        novelty["novelty_position"],
        novelty["included_works"],
        novelty["direct_count"],
        novelty["high_partial_count"],
        search["primary_queries"],
    )
    if observed_novelty != expected_novelty:
        raise VerificationError("novelty audit values drifted")
    novelty_report = (ROOT / "level4/closure_proofs/novelty_verification/FINAL_REPORT.md").read_text(
        encoding="utf-8"
    )
    if "candidate works inspected after DOI/title deduplication: 2445" not in novelty_report:
        raise VerificationError("novelty candidate inspection count drifted")


def cited_paths() -> set[str]:
    found: set[str] = set()
    for name in REQUIRED_DOCS:
        text = (SYNTHESIS / name).read_text(encoding="utf-8")
        found.update(PATH_RE.findall(text))
    return found


def check_cited_paths() -> None:
    missing = sorted(path for path in cited_paths() if not (ROOT / path).exists())
    if missing:
        raise VerificationError(f"cited repository paths do not exist: {missing}")


def check_required_claims_and_wording() -> None:
    combined = "\n".join(
        (SYNTHESIS / name).read_text(encoding="utf-8")
        for name in REQUIRED_DOCS
        if name != "CLAIM_CATALOG.md"
    )
    normalized = re.sub(r"\s+", " ", combined)
    lower = normalized.lower()
    for assertion in BANNED_ASSERTIONS:
        if assertion in lower:
            raise VerificationError(f"prohibited assertion found: {assertion}")

    required = (
        "LEVEL-4-CLOSED",
        "17 PASS",
        "16/16 mandatory",
        "L4R-13",
        "MATHEMATICAL, NOT OPERATIONAL",
        "0/4",
        "4/4",
        "2,445",
        "0 DIRECT",
        "9 HIGH-PARTIAL",
        "SR-GAMMA-CERTIFIED",
        "5.800391799508442",
        "3.800391799508442",
        "At terminal Level-4 closure",
        "Within the documented search scope, no work was identified",
    )
    missing = [marker for marker in required if marker.lower() not in lower]
    if missing:
        raise VerificationError(f"required publication boundaries missing: {missing}")


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
        if not any(path == prefix or path.startswith(prefix) for prefix in ALLOWED_DIFF_PREFIXES)
    ]
    if forbidden:
        raise VerificationError(
            "implementation diff touches frozen or unapproved paths: " + ", ".join(forbidden)
        )


def check_diff_scope(base: str) -> None:
    validate_changed_paths(changed_paths(base))


def verify(base: str, check_diff: bool = True) -> None:
    check_required_documents()
    check_terminal_state()
    check_authoritative_values()
    check_cited_paths()
    check_required_claims_and_wording()
    if check_diff:
        check_diff_scope(base)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base",
        default=SYNTHESIS_BASE_COMMIT,
        help="Git base for the scope guard (defaults to the approved design checkpoint)",
    )
    parser.add_argument("--no-diff-check", action="store_true")
    args = parser.parse_args()
    try:
        verify(args.base, check_diff=not args.no_diff_check)
    except (VerificationError, OSError, subprocess.CalledProcessError) as exc:
        print(f"SYNTHESIS VERIFICATION FAILED: {exc}", file=sys.stderr)
        return 1
    print("SYNTHESIS VERIFICATION OK")
    print("documents=10 cited_paths=" + str(len(cited_paths())))
    print("terminal=LEVEL-4-CLOSED mandatory=16/16 partial=L4R-13 sr_arb=SR-GAMMA-CERTIFIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
