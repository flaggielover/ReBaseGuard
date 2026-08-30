from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

CAMPAIGN = Path(__file__).resolve().parents[1]
ROOT = CAMPAIGN.parents[2]
SR_ROOT = "level4/closure_proofs/sr_derivative"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_frozen_new_inputs() -> None:
    manifest = json.loads((CAMPAIGN / "manifest.json").read_text())
    for key in ("numerical_protocol", "finite_support_witness", "assumption_targets"):
        assert sha(CAMPAIGN / manifest["frozen_new_inputs"][key]) == manifest["frozen_new_inputs"][f"{key}_sha256"]
    assert sha(CAMPAIGN / manifest["immutable_sr_history"]["manifest"]) == manifest["immutable_sr_history"]["manifest_sha256"]


def test_two_tagged_snapshots_and_current_protected_tree() -> None:
    manifest = json.loads((CAMPAIGN / "manifest.json").read_text())["immutable_sr_history"]
    for key in ("terminal_level4", "additive_sr_certificate"):
        row = manifest[key]
        commit = subprocess.check_output(["git", "rev-list", "-n", "1", row["tag"]], cwd=ROOT, text=True).strip()
        tree = subprocess.check_output(["git", "rev-parse", f"{row['tag']}:{SR_ROOT}"], cwd=ROOT, text=True).strip()
        assert commit == row["commit"]
        assert tree == row["git_tree"]
    current = subprocess.check_output(["git", "rev-parse", f"HEAD:{SR_ROOT}"], cwd=ROOT, text=True).strip()
    assert current == manifest["additive_sr_certificate"]["git_tree"]
    assert subprocess.run(["git", "diff", "--quiet", "--", SR_ROOT], cwd=ROOT).returncode == 0


def test_source_separation() -> None:
    protocol = json.loads((CAMPAIGN / "numerics" / "PROTOCOL.json").read_text())
    forbidden = tuple(protocol["independence"]["forbidden_import_roots"])
    score = (CAMPAIGN / protocol["independence"]["score_module"]).read_text()
    direct = (CAMPAIGN / protocol["independence"]["direct_module"]).read_text()
    assert all(root not in score and root not in direct for root in forbidden)
    assert "score_sr" not in direct and "direct_sr" not in score
    seeds = protocol["seeds"]
    assert len({seeds["score"], seeds["pilot_direct"], seeds["final_direct"]}) == 3
