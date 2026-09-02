"""Checkpoint-D (R1 result) tests — git-based replacements for anchor-phase
worktree assertions, and the invariants that actually matter."""
from __future__ import annotations

import subprocess
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
ROOT = NS.parents[2]
REL_NS = NS.relative_to(ROOT).as_posix()
P5 = "level4/closure_proofs/p5_nonlinear_dynamics"
P5_COMMIT = "bb03c0ea9ea34060c992b6d7f0390de6a3cf8108"
ANCHOR_A = "db0781ed79851ca55af788731a47a0f4dda1d9c6"
FIRST_FAIL = "528908ba3c952031f7f41c2f22fc6e07a1401d90"
ANCHOR_B = "e02b5ce04798668fc4d406d5b528887dccf66da6"
RA_RESULT = "f2ac22e8a44d303689e8ebad2ce77e22966796a0"
ANCHOR_C = "a5fdb1788514602bb7fa7cc6346145bd10ea89a1"


def _git(*a: str) -> str:
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True,
                          text=True, check=True).stdout.strip()


def test_no_r1_result_in_the_checkpoint_c_anchor():
    listing = _git("ls-tree", "-r", "--name-only", ANCHOR_C, "--", REL_NS).split()
    for forbidden in ("r1_benchmark.json", "r1_selftest.json", "r1_cover_compression.json"):
        assert not any(p.endswith(forbidden) for p in listing), forbidden


def test_checkpoint_c_sits_directly_on_the_ra_result():
    parents = _git("rev-list", "--parents", "-n", "1", ANCHOR_C).split()
    assert parents[1] == RA_RESULT


def test_the_whole_campaign_history_is_intact_and_unsquashed():
    for c in (ANCHOR_A, FIRST_FAIL, ANCHOR_B, RA_RESULT, ANCHOR_C):
        assert _git("merge-base", "--is-ancestor", c, "HEAD") == ""


def test_original_p5_still_byte_identical():
    assert _git("rev-parse", f"HEAD:{P5}") == _git("rev-parse", f"{P5_COMMIT}:{P5}")


def test_ra_namespace_untouched_since_its_result():
    ra = f"{REL_NS}/certified_method_repair_ra"
    assert _git("rev-parse", f"HEAD:{ra}") == _git("rev-parse", f"{RA_RESULT}:{ra}")


def test_no_campaign_commit_wrote_outside_p5x():
    for c in (ANCHOR_A, FIRST_FAIL, ANCHOR_B, RA_RESULT, ANCHOR_C):
        files = _git("show", "--name-only", "--pretty=format:", c).split()
        outside = [f for f in files if f and not f.startswith(REL_NS)]
        assert not outside, f"{c} touched {outside}"
