"""Checkpoint-F (R3 result) — git-object invariants only.  No worktree state."""
from __future__ import annotations
import json, subprocess
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
         "41e1c014edab5e7ba2788cc97e3480e466498853"]
ANCHOR_E = CHAIN[-1]
R2_RESULT = CHAIN[-2]


def _git(*a: str) -> str:
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True,
                          text=True, check=True).stdout.strip()


def test_no_r3_result_in_the_checkpoint_e_anchor():
    listing = _git("ls-tree", "-r", "--name-only", ANCHOR_E, "--", REL).split()
    assert not any(p.endswith("r3_gate.json") for p in listing)


def test_original_p5_byte_identical():
    assert _git("rev-parse", f"HEAD:{P5}") == _git("rev-parse", f"{P5_COMMIT}:{P5}")


def test_all_prior_campaign_namespaces_untouched():
    for sub in ("certified_method_repair_ra", "compute_optimization_r1",
                "compute_optimization_r2"):
        p = f"{REL}/{sub}"
        assert _git("rev-parse", f"HEAD:{p}") == _git("rev-parse", f"{R2_RESULT}:{p}")


def test_chain_intact_unsquashed_and_anchored():
    for c in CHAIN:
        assert _git("merge-base", "--is-ancestor", c, "HEAD") == ""
    assert _git("rev-list", "--parents", "-n", "1", ANCHOR_E).split()[1] == R2_RESULT


def test_no_campaign_commit_wrote_outside_p5x():
    for c in CHAIN:
        files = _git("show", "--name-only", "--pretty=format:", c).split()
        assert not [f for f in files if f and not f.startswith(REL)], c


def test_gate_result_is_recorded_faithfully():
    g = json.loads((NS / "results" / "r3_gate.json").read_text())
    assert g["selftest"] == "PASS"
    assert g["gate"] == "FAIL"
    assert g["failed_criteria"] == ["P4_pass"]
    ck = g["checks"]
    assert ck["P1_pass"] and ck["P2_pass"] and ck["P3_pass"] and not ck["P4_pass"]
    assert ck["P4_n_z_times_t_panel"] > ck["P4_budget"]
    doc = (NS / "compute_optimization_r3_sr_symbolic" / "R3_RESULT.md").read_text()
    assert "R3_LOCAL_FEASIBLE_ONLY" in doc
    assert "NOT_RUN" in doc
    assert "Four of five predictions were wrong" in doc


def test_no_retry_after_the_failed_gate():
    """No second gate artifact may exist: the spec froze no retry ladder."""
    extra = [p.name for p in (NS / "results").glob("r3_gate*") if p.name != "r3_gate.json"]
    assert not extra, extra
