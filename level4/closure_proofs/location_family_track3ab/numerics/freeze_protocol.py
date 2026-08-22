#!/usr/bin/env python3
"""Freeze Track-3A protocol, sources, and immutable historical dependencies."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


CAMPAIGN = Path(__file__).resolve().parents[1]
REPO = CAMPAIGN.parents[2]
RESULTS = CAMPAIGN / "results"

HISTORICAL_FILES = (
    "level4/closure_proofs/location_family/PROTOCOL.md",
    "level4/closure_proofs/location_family/THEOREM.md",
    "level4/closure_proofs/location_family/CORRESPONDENCE_REPORT.md",
    "level4/closure_proofs/location_family/FAILURE_DIAGNOSES.md",
    "level4/closure_proofs/location_family/FINAL_REPORT.md",
    "level4/closure_proofs/location_family/results/decision.json",
    "level4/closure_proofs/location_family/results/numerical_decision.json",
    "level4/closure_proofs/location_family/results/route_a.json",
    "level4/closure_proofs/location_family/results/route_b.json",
    "level4/closure_proofs/location_family/results/protocol_hash.json",
    "level4/closure_proofs/m_gt_1_track1b/results/decision.json",
    "level4/closure_proofs/sr_derivative/results/decision.json",
    "level4/stage_f/results/final_decision.json",
)

SOURCE_FILES = (
    "level4/closure_proofs/location_family_track3ab/src/rebaseguard_location_family_track3ab/frozen.py",
    "level4/closure_proofs/location_family_track3ab/src/rebaseguard_location_family_track3ab/route_a.py",
    "level4/closure_proofs/location_family_track3ab/src/rebaseguard_location_family_track3ab/route_b.py",
    "level4/closure_proofs/location_family_track3ab/src/rebaseguard_location_family_track3ab/statistics.py",
    "level4/closure_proofs/location_family_track3ab/numerics/run_confirmatory.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n")


def git_head() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def main() -> None:
    checkpoint_root = RESULTS / "checkpoints"
    if checkpoint_root.exists() and any(checkpoint_root.rglob("*.json")):
        raise SystemExit("refusing to freeze after confirmatory checkpoints exist")
    if (RESULTS / "numerical_decision.json").exists():
        raise SystemExit("refusing to freeze after a numerical decision exists")

    protocol_hash = sha256(CAMPAIGN / "PROTOCOL.md")
    historical_hashes = {relative: sha256(REPO / relative) for relative in HISTORICAL_FILES}
    source_hashes = {relative: sha256(REPO / relative) for relative in SOURCE_FILES}

    old_route_a = (REPO / "level4/closure_proofs/location_family/results/route_a.json").read_text()
    old_route_b = (REPO / "level4/closure_proofs/location_family/results/route_b.json").read_text()
    if "2026082317" in old_route_a or "2026082317" in old_route_b:
        raise SystemExit("fresh master seed unexpectedly occurs in historical outputs")

    write_json(
        RESULTS / "historical_manifest.json",
        {
            "schema": "rebaseguard.location-family-track3ab.historical.v1",
            "campaign_start_commit": git_head(),
            "historical_statuses": {
                "level_1_3": "CLOSED",
                "stage_f": "LEVEL-4-PARTIAL",
                "track_1b": "MGT1-TRACK1B-CLOSED",
                "track_2": "SR-DERIVATIVE-CLOSED",
                "track_3": "LOCATION-FAMILY-THEOREM-PARTIAL",
                "track_3_numerical": "FAILED",
                "track_3_failed_relative": 0.0460535142584416,
                "track_3_relative_limit": 0.03,
                "track_3_lean": "NOT AUTHORIZED / NOT RUN"
            },
            "sha256": historical_hashes,
        },
    )
    write_json(
        RESULTS / "source_manifest.json",
        {
            "schema": "rebaseguard.location-family-track3ab.sources.v1",
            "frozen_before_confirmatory_outcomes": True,
            "sha256": source_hashes,
        },
    )
    write_json(
        RESULTS / "protocol_hash.json",
        {
            "schema": "rebaseguard.location-family-track3ab.protocol-freeze.v1",
            "protocol": "level4/closure_proofs/location_family_track3ab/PROTOCOL.md",
            "sha256": protocol_hash,
            "frozen_before_confirmatory_outcomes": True,
            "fresh_master_seed": 2026082317,
            "historical_master_seed": 2026082307,
            "confirmatory_outcomes_existed_at_freeze": False,
        },
    )
    print(f"PROTOCOL_SHA256={protocol_hash}")
    print(f"SOURCE_MANIFEST_SHA256={sha256(RESULTS / 'source_manifest.json')}")


if __name__ == "__main__":
    main()
