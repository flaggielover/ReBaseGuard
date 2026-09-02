"""Checkpoint-E (R2 result) git-based invariants."""
from __future__ import annotations
import subprocess
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
ROOT = NS.parents[2]
REL_NS = NS.relative_to(ROOT).as_posix()
P5 = "level4/closure_proofs/p5_nonlinear_dynamics"
P5_COMMIT = "bb03c0ea9ea34060c992b6d7f0390de6a3cf8108"
CHAIN = ["db0781ed79851ca55af788731a47a0f4dda1d9c6",
         "528908ba3c952031f7f41c2f22fc6e07a1401d90",
         "e02b5ce04798668fc4d406d5b528887dccf66da6",
         "f2ac22e8a44d303689e8ebad2ce77e22966796a0",
         "a5fdb1788514602bb7fa7cc6346145bd10ea89a1",
         "9e19c706b65ba354de7123fbe670c121acf1a861",
         "afbfe1811f686c0f64978090f7d879468dbd6809"]
ANCHOR_D = CHAIN[-1]
R1_RESULT = CHAIN[-2]


def _git(*a: str) -> str:
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True,
                          text=True, check=True).stdout.strip()


def test_no_r2_result_in_the_checkpoint_d_anchor():
    listing = _git("ls-tree", "-r", "--name-only", ANCHOR_D, "--", REL_NS).split()
    for f in ("r2_benchmark.json", "r2_selftest.json"):
        assert not any(p.endswith(f) for p in listing), f


def test_original_p5_byte_identical():
    assert _git("rev-parse", f"HEAD:{P5}") == _git("rev-parse", f"{P5_COMMIT}:{P5}")


def test_prior_campaign_namespaces_untouched_by_r2():
    for sub in ("certified_method_repair_ra", "compute_optimization_r1"):
        p = f"{REL_NS}/{sub}"
        assert _git("rev-parse", f"HEAD:{p}") == _git("rev-parse", f"{R1_RESULT}:{p}")


def test_full_chain_intact_and_unsquashed():
    for c in CHAIN:
        assert _git("merge-base", "--is-ancestor", c, "HEAD") == ""
    assert _git("rev-list", "--parents", "-n", "1", ANCHOR_D).split()[1] == R1_RESULT


def test_no_campaign_commit_wrote_outside_p5x():
    for c in CHAIN:
        files = _git("show", "--name-only", "--pretty=format:", c).split()
        outside = [f for f in files if f and not f.startswith(REL_NS)]
        assert not outside, f"{c} touched {outside}"
