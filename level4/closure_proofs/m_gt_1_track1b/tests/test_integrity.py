from __future__ import annotations

import ast
import hashlib
import json
import subprocess
from pathlib import Path

CAMPAIGN = Path(__file__).resolve().parents[1]
REPO = CAMPAIGN.parents[2]

HISTORICAL_HASHES = {
    "level4/stage_d/STAGE_D_PROTOCOL.md": "925adecf08c7234375333a26c3af934b005e0d8b4cfce470b77834d7245e8b2e",
    "level4/stage_d/results/d2_3_derivative.json": "ea1d026384866de0fc5ad0ded3e68f159d32deaa3be24505aab449b73db8e020",
    "level4/closure_proofs/m_gt_1/PROTOCOL.md": "27c3cddad3a09520a562b444e9635a3f4155464ac322f01edc79e0fc74c2d9af",
    "level4/closure_proofs/m_gt_1/results/decision.json": "0d86f981822cef5e9f94895a7538d67a8fe29929aa07b5f44e05d779bb0aa0ae",
    "level4/closure_proofs/m_gt_1_track1a/PROTOCOL.md": "76a5d40b4165758afb72a12dd93f302dd03cbf7db78184ef248156962cc9a79f",
    "level4/closure_proofs/m_gt_1_track1a/results/decision.json": "ecf49a12818edc7d4bad69b527e3a014123b9356bb73904d31eccc6752210b7c",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text())
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            found.add(node.module or "")
    return found


def test_protocol_hash_is_frozen_and_self_consistent():
    record = json.loads((CAMPAIGN / "results/protocol_hash.json").read_text())
    assert record["frozen_before_confirmatory_numerics"] is True
    assert record["sha256"] == "c4eca15f8e72059a8d7cb3f0a5dc8fe7922183b90594b4a9574ded4e94c775c6"
    assert sha(CAMPAIGN / "PROTOCOL.md") == record["sha256"]


def test_historical_track1_and_track1a_are_immutable():
    assert {path: sha(REPO / path) for path in HISTORICAL_HASHES} == HISTORICAL_HASHES


def test_track1a_3_130_failure_is_preserved():
    data = json.loads(
        (REPO / "level4/closure_proofs/m_gt_1_track1a/results/replication.json").read_text()
    )
    row = next(row for row in data["verdict"]["decomposition"] if row["m"] == 20)
    assert row["abs_z"] == 3.1302795226595075
    assert data["verdict"]["decision"] == "FAIL"


def test_fresh_seed_exists_only_inside_track1b():
    result = subprocess.run(
        ["rg", "-l", "2026082219", "."], cwd=REPO,
        text=True, capture_output=True, check=True,
    )
    paths = [line.removeprefix("./") for line in result.stdout.splitlines()]
    assert paths
    assert all(path.startswith("level4/closure_proofs/m_gt_1_track1b/") for path in paths)


def test_independent_implementation_source_guard():
    direct = CAMPAIGN / "src/rebaseguard_mgt1b/direct.py"
    reconstruction = CAMPAIGN / "src/rebaseguard_mgt1b/reconstruction.py"
    assert not any("reconstruction" in name for name in imports(direct))
    assert not any(name == "direct" or name.endswith(".direct") for name in imports(reconstruction))
    assert "np.minimum" in direct.read_text()
    assert "lag_products" in reconstruction.read_text()


def test_seed_key_families_are_pairwise_disjoint_by_construction():
    keys = {
        "paired": {(2026082219, 1, b) for b in range(64)},
        "direct": {(2026082219, 2, b) for b in range(64)},
        "recon": {(2026082219, 3, b) for b in range(64)},
    }
    assert keys["paired"].isdisjoint(keys["direct"] | keys["recon"])
    assert keys["direct"].isdisjoint(keys["recon"])

