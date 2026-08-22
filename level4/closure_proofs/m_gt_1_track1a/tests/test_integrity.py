from __future__ import annotations

import ast
import hashlib
import json
import os
import subprocess
from pathlib import Path

CAMPAIGN = Path(__file__).resolve().parents[1]
REPO = CAMPAIGN.parents[2]

HISTORICAL_HASHES = {
    "level4/stage_d/STAGE_D_PROTOCOL.md": "925adecf08c7234375333a26c3af934b005e0d8b4cfce470b77834d7245e8b2e",
    "level4/stage_d/notes/CORRESPONDENCE_AUDIT.md": "985018981b11e2030128e5d4cb78f08e803155c6ed4fdbbbdb48c96001f6c2c2",
    "level4/stage_d/notes/D2_3_STEP_PRECOMMIT.md": "7b7a54c64f4c86334415a03cd45797e7cb8b923d378fa90180a71f1831588dea",
    "level4/stage_d/results/d2_3_derivative.json": "ea1d026384866de0fc5ad0ded3e68f159d32deaa3be24505aab449b73db8e020",
    "level4/stage_f/LEVEL4_REQUIREMENTS_RECONSTRUCTION.md": "41ea8cd6a33f430be44d66376df60efc979b6dda5f00308616a519b7ece6a106",
    "level4/closure_proofs/m_gt_1/PROTOCOL.md": "27c3cddad3a09520a562b444e9635a3f4155464ac322f01edc79e0fc74c2d9af",
    "level4/closure_proofs/m_gt_1/results/decision.json": "0d86f981822cef5e9f94895a7538d67a8fe29929aa07b5f44e05d779bb0aa0ae",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_protocol_hash_is_frozen_and_self_consistent():
    record = json.loads((CAMPAIGN / "results/protocol_hash.json").read_text())
    assert record["frozen_before_confirmatory_numerics"] is True
    assert record["sha256"] == "76a5d40b4165758afb72a12dd93f302dd03cbf7db78184ef248156962cc9a79f"
    assert sha(CAMPAIGN / "PROTOCOL.md") == record["sha256"]


def test_historical_hashes_are_unchanged():
    assert {path: sha(REPO / path) for path in HISTORICAL_HASHES} == HISTORICAL_HASHES


def test_previous_manifest_artifacts_are_byte_identical():
    manifest = json.loads(
        (REPO / "level4/closure_proofs/m_gt_1/results/artifact_manifest.json").read_text()
    )
    prior = REPO / "level4/closure_proofs/m_gt_1"
    assert {
        name: sha(prior / name) for name in manifest["artifacts"]
    } == manifest["artifacts"]


def test_new_seed_family_did_not_exist_outside_track_at_freeze():
    result = subprocess.run(
        ["rg", "-l", "2026082211", "."], cwd=REPO,
        text=True, capture_output=True, check=True,
    )
    paths = [line.removeprefix("./") for line in result.stdout.splitlines()]
    assert paths
    assert all(path.startswith("level4/closure_proofs/m_gt_1_track1a/") for path in paths)


def test_confirmatory_seed_routes_are_disjoint():
    data = json.loads((CAMPAIGN / "results/replication.json").read_text())
    a_prefixes = {
        tuple(key[:2]) for rep in data["stage_a"]
        for cell in rep["seed_keys_by_m"] for key in cell
    }
    direct_prefixes = {
        tuple(key[:2]) for rep in data["stage_d_direct"] for key in rep["seed_keys"]
    }
    recon_prefixes = {
        tuple(key[:2]) for rep in data["stage_d_reconstruction"] for key in rep["seed_keys"]
    }
    assert a_prefixes == {(2026082211, 1)}
    assert direct_prefixes == {(2026082211, 2)}
    assert recon_prefixes == {(2026082211, 3)}
    assert a_prefixes.isdisjoint(direct_prefixes | recon_prefixes)
    assert direct_prefixes.isdisjoint(recon_prefixes)


def test_simulator_imports_neither_historical_estimator():
    tree = ast.parse((CAMPAIGN / "src/rebaseguard_mgt1a/simulate.py").read_text())
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
    joined = " ".join(imports)
    assert "rebaseguard_level4.conditional" not in joined
    assert "rebaseguard_level4.multicycle" not in joined
    assert "stage_d" not in joined
    assert "rebaseguard_level4.frozen" in joined


def test_reproduce_script_is_executable_and_replays_previous_track():
    script = CAMPAIGN / "reproduce.sh"
    assert os.access(script, os.X_OK)
    text = script.read_text()
    assert "m_gt_1/reproduce.sh" in text
    assert "--resume" in text

