from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

CAMPAIGN = Path(__file__).resolve().parents[1]
REPO = CAMPAIGN.parents[2]
MANIFEST = CAMPAIGN / "results/historical_manifest.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def historical_paths(scopes: list[str]) -> list[Path]:
    roots = []
    for scope in scopes:
        assert scope.endswith("/**")
        roots.append(scope.removesuffix("/**"))
    result = subprocess.run(
        ["git", "ls-files", "-z", "--", *roots],
        cwd=REPO,
        capture_output=True,
        check=True,
    )
    relative = [item.decode() for item in result.stdout.split(b"\0") if item]
    return [REPO / item for item in sorted(relative, key=lambda item: item.encode())]


def canonical_records(paths: list[Path]) -> bytes:
    return b"".join(
        f"{sha(path)}  {path.relative_to(REPO).as_posix()}\n".encode()
        for path in paths
    )


def test_historical_manifest_is_complete_and_immutable():
    manifest = json.loads(MANIFEST.read_text())
    paths = historical_paths(manifest["immutable_scopes"])
    relative = [path.relative_to(REPO).as_posix() for path in paths]
    records = canonical_records(paths)

    assert len(paths) == manifest["file_count"]
    assert hashlib.sha256(("\n".join(relative) + "\n").encode()).hexdigest() == (
        manifest["path_list_sha256"]
    )
    assert hashlib.sha256(records).hexdigest() == manifest["records_sha256"]
    assert {
        path: sha(REPO / path) for path in manifest["critical_files"]
    } == manifest["critical_files"]


def test_protocol_hash_is_frozen_and_self_consistent():
    record = json.loads((CAMPAIGN / "results/protocol_hash.json").read_text())
    assert record["frozen_before_confirmatory_numerics"] is True
    assert record["confirmatory_outcome_files_present_at_freeze"] == []
    assert record["sha256"] == (
        "e9b66ff8ffbf0d8138598b1d4dc19dcc1e44d8b4f33f5b462b5b82f341d5f762"
    )
    protocol = CAMPAIGN / "PROTOCOL.md"
    assert sha(protocol) == record["sha256"]
    assert len(protocol.read_bytes()) == record["bytes"]
    assert len(protocol.read_text().splitlines()) == record["lines"]


def test_historical_failed_and_partial_statuses_are_preserved():
    stage_d = json.loads(
        (REPO / "level4/stage_d/results/stage_d_decision.json").read_text()
    )
    d23 = json.loads(
        (REPO / "level4/stage_d/results/d2_3_derivative.json").read_text()
    )
    assert d23["criterion_met_all_m"] is False
    assert stage_d["decision"] == "STAGE-D-PARTIAL"
    d23_row = next(row for row in stage_d["criteria"] if row["id"] == "D2.3")
    assert d23_row["status"] == "FAIL"


def test_fresh_master_seed_is_confined_to_design_and_track2():
    result = subprocess.run(
        ["rg", "-l", "2026082227", "."],
        cwd=REPO,
        text=True,
        capture_output=True,
        check=True,
    )
    allowed = {
        "docs/superpowers/specs/2026-08-22-sr-derivative-design.md",
        "docs/superpowers/plans/2026-08-22-sr-derivative-implementation.md",
    }
    paths = {line.removeprefix("./") for line in result.stdout.splitlines()}
    assert paths
    assert all(
        path in allowed or path.startswith("level4/closure_proofs/sr_derivative/")
        for path in paths
    )


def test_frozen_seed_families_are_pairwise_disjoint():
    master = 2026082227
    families = {
        "calibration_target": {(master, 1, 0)},
        "calibration_search": {(master, 1, 1, i) for i in range(30)},
        "calibration_final": {(master, 1, 2)},
        "fixed_sr": {(master, 1, 3, b) for b in range(64)},
        "fixed_cusum": {(master, 1, 4, b) for b in range(64)},
        "route_a": {(master, 2, b) for b in range(64)},
        "route_b": {
            (master, 3, replication, batch)
            for replication in range(2)
            for batch in range(64)
        },
    }
    encoded = {
        name: {json.dumps(key) for key in keys} for name, keys in families.items()
    }
    for left, left_keys in encoded.items():
        for right, right_keys in encoded.items():
            if left < right:
                assert left_keys.isdisjoint(right_keys)


def test_frozen_stage_d_sources_match_definition_audit():
    expected = {
        "level4/stage_d/src/stopped.py": (
            "7224bfec8bf0473c7ddee711d4773a2881889e22977b7e925fee8617f4a58c41"
        ),
        "level4/stage_d/src/chain.py": (
            "84d354a67d23c33e631f611ed5537b37cbb032023435f051f05e8ccc10439205"
        ),
        "level4/src/rebaseguard_level4/frozen.py": (
            "777681ea32842ff48224b4c51ff7a2a26525d5a44d815d521949a6242baa6c54"
        ),
    }
    assert {path: sha(REPO / path) for path in expected} == expected


def test_freeze_record_says_no_confirmatory_outcome_existed():
    record = json.loads((CAMPAIGN / "results/protocol_hash.json").read_text())
    assert record["confirmatory_outcome_files_present_at_freeze"] == []
