"""Checkpoint-G (R5 result) -- git-object invariants only.  No worktree state.

Written to the D8 standing rule from the outset.
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
         "209a6fd9a5ca2824688062ac855a7abcefae9697",
         "daaabf9e028098b88bc1e7a8f5ebddb1e6c21825",
         "f19f8d13caae1d9d8d21a6237fe1b71ee06b8e63"]
ANCHOR_G = CHAIN[-1]
R4_RESULT = CHAIN[-2]


def _git(*a: str) -> str:
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True,
                          text=True, check=True).stdout.strip()


def test_no_r5_result_in_the_checkpoint_g_anchor():
    listing = _git("ls-tree", "-r", "--name-only", ANCHOR_G, "--", REL).split()
    for f in ("r5_gate.json", "R5_RESULT.md"):
        assert not any(p.endswith(f) for p in listing), f


def test_no_r5_code_in_the_checkpoint_g_anchor():
    """The brief required proofs and Checkpoint G before any implementation."""
    listing = _git("ls-tree", "-r", "--name-only", ANCHOR_G, "--", REL).split()
    for f in ("scaled_tail.py", "r5_gate.py"):
        assert not any(p.endswith(f) for p in listing), f


def test_frozen_r5_documents_unchanged_since_the_anchor():
    for f in ("R5_FROZEN_SPEC.md", "SCALED_TAIL_DERIVATION.md", "MANIFEST.md"):
        p = f"{REL}/compute_optimization_r5_scaled_tail/{f}"
        assert _git("rev-parse", f"HEAD:{p}") == _git("rev-parse", f"{ANCHOR_G}:{p}"), f


def test_original_p5_byte_identical():
    assert _git("rev-parse", f"HEAD:{P5}") == _git("rev-parse", f"{P5_COMMIT}:{P5}")


def test_all_prior_campaign_namespaces_untouched_by_r5():
    for sub in ("certified_method_repair_ra", "compute_optimization_r1",
                "compute_optimization_r2", "compute_optimization_r3_sr_symbolic",
                "compute_optimization_r4_xi_reformulation"):
        p = f"{REL}/{sub}"
        assert _git("rev-parse", f"HEAD:{p}") == _git("rev-parse", f"{R4_RESULT}:{p}"), sub


def test_r4_and_r3_gate_results_byte_identical():
    for f in ("r4_gate.json", "r4_diagnostics.json", "r3_gate.json"):
        p = f"{REL}/results/{f}"
        assert _git("rev-parse", f"HEAD:{p}") == _git("rev-parse", f"{R4_RESULT}:{p}"), f


def test_lean_and_proof_trees_unchanged_since_checkpoint_a():
    for p in ("rebaseguard-lean", "rebaseguard-proof"):
        assert _git("rev-parse", f"HEAD:{p}") == _git("rev-parse", f"{CHAIN[0]}:{p}"), p


def test_full_chain_intact_and_unsquashed():
    for c in CHAIN:
        assert _git("merge-base", "--is-ancestor", c, "HEAD") == ""
    assert _git("rev-list", "--parents", "-n", "1", ANCHOR_G).split()[1] == R4_RESULT


def test_no_campaign_commit_wrote_outside_p5x():
    for c in CHAIN:
        files = _git("show", "--name-only", "--pretty=format:", c).split()
        outside = [f for f in files if f and not f.startswith(REL)]
        assert not outside, f"{c} touched {outside}"
