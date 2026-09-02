"""Checkpoint-A tests: no production result exists yet, and the protected tree
(including the two pre-existing untracked audit namespaces) is intact."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
ROOT = NS.parents[2]
sys.path.insert(0, str(NS / "scripts"))


def test_no_production_results_at_checkpoint_a():
    allowed = {NS / "results" / "integrity" / "protected_tree_manifest_pre.json"}
    present = {p for p in (NS / "results").rglob("*") if p.is_file()}
    assert present <= allowed, f"unexpected production artifacts: {present - allowed}"


def test_feasibility_output_is_marked_non_authoritative():
    doc = json.loads((NS / "feasibility" / "results" / "reduction_probe.json").read_text())
    assert doc["status"] == "FEASIBILITY_PROBE_NON_AUTHORITATIVE"
    assert doc["not_a_certificate"] is True


def test_protected_tree_intact():
    from protected_tree import check          # noqa: E402
    result = check()
    assert result["p5_immutable"], result
    assert not result["changed_outside_p5x"], result["changed_outside_p5x"]
    assert not result["missing_outside_p5x"], result["missing_outside_p5x"]


def test_untracked_audit_namespaces_are_recorded_not_swept():
    manifest = json.loads(
        (NS / "results" / "integrity" / "protected_tree_manifest_pre.json").read_text())
    recorded = manifest["untracked_namespaces_outside_p5x"]
    out = subprocess.run(["git", "ls-files"], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout
    tracked = set(out.splitlines())
    for name in recorded:
        assert not any(t.startswith(name) for t in tracked), \
            f"{name} was swept into git by P5X; it must stay untracked and untouched"


def test_p5x_namespace_is_the_only_thing_p5x_adds():
    out = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"],
                         cwd=ROOT, capture_output=True, text=True, check=True).stdout
    rel_ns = NS.relative_to(ROOT).as_posix()
    manifest = json.loads(
        (NS / "results" / "integrity" / "protected_tree_manifest_pre.json").read_text())
    known = set(manifest["untracked_namespaces_outside_p5x"])
    for line in out.splitlines():
        path = line[3:].strip().strip('"')
        if path.startswith(rel_ns):
            continue
        assert any(path.startswith(k) for k in known), f"unexpected worktree change: {line}"
