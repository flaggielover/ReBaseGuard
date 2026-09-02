"""Checkpoint-F (R4 result) -- git-object invariants only.  No worktree state.

Written to the D8 standing rule from the outset: every anchor-phase property is
asserted against `git ls-tree` / `git rev-parse` on a named commit.
"""
from __future__ import annotations
import subprocess
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
ROOT = NS.parents[2]
REL = NS.relative_to(ROOT).as_posix()
P5 = "level4/closure_proofs/p5_nonlinear_dynamics"
P5_COMMIT = "bb03c0ea9ea34060c992b6d7f0390de6a3cf8108"
CHAIN = ["db0781ed79851ca55af788731a47a0f4dda1d9c6",
         "528908ba3c952031f7f41c2f22fc6e07a1401d90",
         "e02b5ce04798668fc4d406d5b528887dccf66da6",
         "f2ac22e8a44d303689e8ebad2ce77e22966796a0",
         "a5fdb1788514602bb7fa7cc6346145bd10ea89a1",
         "9e19c706b65ba354de7123fbe670c121acf1a861",
         "afbfe1811f686c0f64978090f7d879468dbd6809",
         "e22cd0e3fb9afdc87fa94c3209ed32b0c4972414",
         "41e1c014edab5e7ba2788cc97e3480e466498853",
         "c123b9bb8f15d17650545b3fce4aca8a6b61093b",
         "209a6fd9a5ca2824688062ac855a7abcefae9697"]
ANCHOR_F = CHAIN[-1]
R3_RESULT = CHAIN[-2]


def _git(*a: str) -> str:
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True,
                          text=True, check=True).stdout.strip()


def test_no_r4_result_in_the_checkpoint_f_anchor():
    listing = _git("ls-tree", "-r", "--name-only", ANCHOR_F, "--", REL).split()
    for f in ("r4_gate.json", "r4_diagnostics.json", "R4_RESULT.md"):
        assert not any(p.endswith(f) for p in listing), f


def test_no_r4_code_in_the_checkpoint_f_anchor():
    """The brief required the algebra to precede any kernel implementation."""
    listing = _git("ls-tree", "-r", "--name-only", ANCHOR_F, "--", REL).split()
    for f in ("xi_kernel.py", "r4_gate.py", "r4_diagnostics.py"):
        assert not any(p.endswith(f) for p in listing), f


def test_frozen_spec_bytes_unchanged_since_the_anchor():
    for f in ("R4_FROZEN_SPEC.md", "XI_DERIVATION_AND_INVARIANCE.md",
              "EXACT_SR_TARGET_XI_AUDIT.md"):
        p = f"{REL}/compute_optimization_r4_xi_reformulation/{f}"
        assert _git("rev-parse", f"HEAD:{p}") == _git("rev-parse", f"{ANCHOR_F}:{p}"), f


def test_original_p5_byte_identical():
    assert _git("rev-parse", f"HEAD:{P5}") == _git("rev-parse", f"{P5_COMMIT}:{P5}")


def test_prior_campaign_namespaces_untouched_by_r4():
    for sub in ("certified_method_repair_ra", "compute_optimization_r1",
                "compute_optimization_r2", "compute_optimization_r3_sr_symbolic"):
        p = f"{REL}/{sub}"
        assert _git("rev-parse", f"HEAD:{p}") == _git("rev-parse", f"{R3_RESULT}:{p}")


def test_committed_r3_result_bytes_unchanged_by_the_r4_rerun():
    """R3's gate was re-run to validate the rebuilt environment; its committed
    result must be byte-identical to what R3 produced."""
    p = f"{REL}/results/r3_gate.json"
    assert _git("rev-parse", f"HEAD:{p}") == _git("rev-parse", f"{R3_RESULT}:{p}")


def test_full_chain_intact_and_unsquashed():
    for c in CHAIN:
        assert _git("merge-base", "--is-ancestor", c, "HEAD") == ""
    assert _git("rev-list", "--parents", "-n", "1", ANCHOR_F).split()[1] == R3_RESULT


def test_no_campaign_commit_wrote_outside_p5x():
    for c in CHAIN:
        files = _git("show", "--name-only", "--pretty=format:", c).split()
        outside = [f for f in files if f and not f.startswith(REL)]
        assert not outside, f"{c} touched {outside}"
