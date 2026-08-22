from __future__ import annotations

import hashlib
import json
from pathlib import Path

CAMPAIGN = Path(__file__).resolve().parents[1]
REPO = CAMPAIGN.parents[2]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_protocol_hash_is_frozen_before_outcomes():
    freeze = json.loads((CAMPAIGN / "results/protocol_hash.json").read_text())
    assert freeze["sha256"] == _sha256(CAMPAIGN / "PROTOCOL.md")
    assert freeze["sha256"] == (
        "52a27f178f91b88abfc78c28c327084eedafa61e6e91b24354a9faf1b3ed55f6"
    )
    assert freeze["confirmatory_outcomes_existed_at_freeze"] is False
    assert freeze["master_seed"] == 2026082307
    assert freeze["master_seed_absent_before_freeze"] is True


def test_historical_dependency_hashes_are_exact():
    manifest = json.loads(
        (CAMPAIGN / "results/historical_manifest.json").read_text()
    )
    assert len(manifest["sha256"]) == 35
    for relative, expected in manifest["sha256"].items():
        assert _sha256(REPO / relative) == expected, relative


def test_historical_scientific_statuses_remain_frozen():
    manifest = json.loads(
        (CAMPAIGN / "results/historical_manifest.json").read_text()
    )
    statuses = manifest["frozen_statuses"]
    assert statuses["stage_d_D2_3"] == "FAIL"
    assert statuses["stage_d_D3_t3"] == "AMBIGUOUS"
    assert statuses["stage_f"] == "LEVEL-4-PARTIAL"
    assert statuses["track_1a"] == "MGT1-TRACK1A-FAILED"
    assert statuses["track_1b"] == "MGT1-TRACK1B-CLOSED"
    assert statuses["track_2"] == "SR-DERIVATIVE-CLOSED"
    assert statuses["track_2_rigorous_instability"] == "OPEN"


def test_fresh_seed_is_confined_to_track3_at_freeze():
    hits = []
    for path in REPO.rglob("*"):
        if not path.is_file() or ".venv" in path.parts or "__pycache__" in path.parts:
            continue
        try:
            if "2026082307" in path.read_text():
                hits.append(path)
        except (UnicodeDecodeError, OSError):
            continue
    assert hits
    assert all(CAMPAIGN in path.parents for path in hits)

