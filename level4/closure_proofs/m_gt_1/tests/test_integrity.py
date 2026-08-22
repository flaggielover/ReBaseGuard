from __future__ import annotations

import ast
import hashlib
import json
import os
import subprocess
from pathlib import Path

CAMPAIGN = Path(__file__).resolve().parents[1]
REPO = CAMPAIGN.parents[2]

FROZEN_HASHES = {
    "level4/stage_d/STAGE_D_PROTOCOL.md": "925adecf08c7234375333a26c3af934b005e0d8b4cfce470b77834d7245e8b2e",
    "level4/stage_d/notes/CORRESPONDENCE_AUDIT.md": "985018981b11e2030128e5d4cb78f08e803155c6ed4fdbbbdb48c96001f6c2c2",
    "level4/stage_d/notes/D2_3_STEP_PRECOMMIT.md": "7b7a54c64f4c86334415a03cd45797e7cb8b923d378fa90180a71f1831588dea",
    "level4/stage_d/results/d2_3_derivative.json": "ea1d026384866de0fc5ad0ded3e68f159d32deaa3be24505aab449b73db8e020",
    "level4/stage_f/LEVEL4_REQUIREMENTS_RECONSTRUCTION.md": "41ea8cd6a33f430be44d66376df60efc979b6dda5f00308616a519b7ece6a106",
}
FROZEN_TREES = {
    "level4/stage_d": "98b15dd8a71c50b15dd7d8ce671db59137ba6fb2",
    "level4/src": "0d4b6f00f4588a25807184e42688cdb5281b940f",
    "level4/stage_f": "0c408843f266d16ddd5b84c43f9dead65e595317",
    "closure": "ddde11f12b4a49c464bdb2a8b0cc869f76032de1",
    "rebaseguard-proof": "727edc8013f3f89afb4dd45085994318e57234be",
    "rebaseguard-lean": "702f365307114a1f6c88ca0b1095b8e28d70a114",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_protocol_hash_is_frozen_and_self_consistent():
    record = json.loads((CAMPAIGN / "results/protocol_hash.json").read_text())
    assert record["frozen_before_confirmatory_numerics"] is True
    assert sha(CAMPAIGN / "PROTOCOL.md") == record["sha256"]


def test_frozen_historical_file_hashes():
    assert {p: sha(REPO / p) for p in FROZEN_HASHES} == FROZEN_HASHES


def test_frozen_historical_git_trees():
    got = {
        p: subprocess.run(["git", "rev-parse", f"HEAD:{p}"], cwd=REPO,
                          text=True, capture_output=True, check=True).stdout.strip()
        for p in FROZEN_TREES
    }
    assert got == FROZEN_TREES


def test_worktree_changes_are_confined_to_campaign_namespace():
    raw = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"],
                         cwd=REPO, text=True, capture_output=True, check=True).stdout
    paths = [line[3:] for line in raw.splitlines() if line]
    assert all(p.startswith("level4/closure_proofs/m_gt_1/") for p in paths)


def test_new_simulator_does_not_import_stage_a_map_modules():
    tree = ast.parse((CAMPAIGN / "src/rebaseguard_mgt1/simulate.py").read_text())
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
    joined = " ".join(imports)
    assert "rebaseguard_level4.conditional" not in joined
    assert "rebaseguard_level4.multicycle" not in joined
    assert "stage_d" not in joined
    assert "rebaseguard_level4.frozen" in joined


def test_historical_d23_claim_is_preserved_in_every_campaign_document():
    for name in ("README.md", "PROTOCOL.md", "THEOREM.md", "FAILURE_DIAGNOSES.md"):
        text = (CAMPAIGN / name).read_text()
        assert "D2.3" in text
        assert "FAILED" in text


def test_reproduce_script_is_executable():
    assert os.access(CAMPAIGN / "reproduce.sh", os.X_OK)


def test_runner_freezes_primary_step_and_seed_family():
    text = (CAMPAIGN / "numerics/run_correspondence.py").read_text()
    assert "MASTER_SEED = 2026082204" in text
    assert '"route_a_n": 1_000_000' in text
    assert '"route_b_n": 500_000' in text
    assert "PRIMARY_H" in text
