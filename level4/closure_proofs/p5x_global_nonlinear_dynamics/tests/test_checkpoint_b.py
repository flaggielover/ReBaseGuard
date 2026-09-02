"""Checkpoint-B tests: the frozen protocol is intact, gate G1 is checked against
git rather than against the working tree, and the protected tree is untouched."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
ROOT = NS.parents[2]
REL_NS = NS.relative_to(ROOT).as_posix()
ANCHOR = "db0781ed79851ca55af788731a47a0f4dda1d9c6"


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                          text=True, check=True).stdout


def test_gate_g1_anchor_holds():
    """G1 is about the anchor commit, not the working tree."""
    assert _git("merge-base", "--is-ancestor", ANCHOR, "HEAD") == ""
    listing = _git("ls-tree", "-r", "--name-only", ANCHOR, "--", REL_NS).split()
    results = [p for p in listing if p.startswith(f"{REL_NS}/results/")]
    assert results == [f"{REL_NS}/results/integrity/protected_tree_manifest_pre.json"], results


def test_frozen_protocol_bytes_unchanged_since_the_anchor():
    digest = json.loads((NS / "PROTOCOL_DIGEST.json").read_text())
    for rel, rec in digest["files"].items():
        blob = subprocess.run(["git", "show", f"{ANCHOR}:{REL_NS}/{rel}"], cwd=ROOT,
                              capture_output=True, check=True).stdout
        assert hashlib.sha256(blob).hexdigest() == rec["sha256"], rel
        assert hashlib.sha256((NS / rel).read_bytes()).hexdigest() == rec["sha256"], rel


def test_frozen_theorem_still_carries_its_registered_defect():
    """No silent repair: D1's defective text must still be in the frozen file."""
    assert "b_SR = log A" in (NS / "FROZEN_THEOREM.md").read_text()
    assert "## `D1`" in (NS / "DEFECT_REGISTER.md").read_text()


def test_protected_tree_intact():
    sys.path.insert(0, str(NS / "scripts"))
    from protected_tree import check          # noqa: E402
    result = check()
    assert result["p5_immutable"], result
    assert not result["changed_outside_p5x"], result["changed_outside_p5x"]
    assert not result["missing_outside_p5x"], result["missing_outside_p5x"]
    assert not result["added_outside_p5x"], result["added_outside_p5x"]


def test_no_lean_sources_yet():
    assert not list(NS.rglob("*.lean"))
