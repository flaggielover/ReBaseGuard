"""Checkpoint-C (R-A result) tests.

These replace the two working-tree assertions that the external repository
change invalidated, by checking against git the properties that actually
protect the science -- and by pinning the external diff exactly, so that any
*further* change outside P5X fails loudly rather than being absorbed.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
ROOT = NS.parents[2]
REL_NS = NS.relative_to(ROOT).as_posix()
P5 = "level4/closure_proofs/p5_nonlinear_dynamics"
ANCHOR_A = "db0781ed79851ca55af788731a47a0f4dda1d9c6"
ANCHOR_B = "e02b5ce04798668fc4d406d5b528887dccf66da6"
FIRST_FAIL = "528908ba3c952031f7f41c2f22fc6e07a1401d90"
P5_COMMIT = "bb03c0ea9ea34060c992b6d7f0390de6a3cf8108"
EXTERNAL = "31132e807b170fd0865a61eb939faab4f24dca9a"


def _git(*a: str) -> str:
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True,
                          text=True, check=True).stdout.strip()


def test_original_p5_is_byte_identical_to_its_only_commit():
    assert _git("rev-parse", f"HEAD:{P5}") == _git("rev-parse", f"{P5_COMMIT}:{P5}")


def test_p5x_tree_at_the_anchor_is_untouched_by_the_external_commit():
    assert _git("rev-parse", f"{EXTERNAL}:{REL_NS}") == _git("rev-parse", f"{ANCHOR_B}:{REL_NS}")


def test_the_whole_p5x_history_is_intact_and_unsquashed():
    for c in (ANCHOR_A, FIRST_FAIL, ANCHOR_B):
        assert _git("merge-base", "--is-ancestor", c, "HEAD") == ""
    parents = _git("rev-list", "--parents", "-n", "1", ANCHOR_B).split()
    assert parents[1] == FIRST_FAIL, "Checkpoint B must sit directly on the first FAIL"


def test_external_change_is_exactly_what_the_incident_records():
    files = sorted(_git("show", "--name-only", "--pretty=format:", EXTERNAL).split())
    assert files == sorted([
        "README.md",
        "level4/closure_proofs/p9r_final_synthesis_repair/INDEPENDENT_ADJUDICATION.md",
        "level4/closure_proofs/p9r_final_synthesis_repair/results/independent_adjudication.json",
    ])
    assert not any(f.startswith(REL_NS) or f.startswith(P5) for f in files)


def test_no_ra_result_existed_in_the_anchor_commit():
    listing = _git("ls-tree", "-r", "--name-only", ANCHOR_B, "--", REL_NS).split()
    for forbidden in ("ra_stop_gate.json", "ra_selftest.json", "ra_diagnostics.json"):
        assert not any(p.endswith(forbidden) for p in listing), forbidden


def test_the_lost_disposition_audits_are_recorded_not_silently_dropped():
    manifest = json.loads(
        (NS / "results" / "integrity" / "protected_tree_manifest_pre.json").read_text())
    recorded = manifest["untracked_namespaces_outside_p5x"]
    assert set(recorded) == {
        "level4/closure_proofs/p4_final_disposition_audit",
        "level4/closure_proofs/p5_final_disposition_audit"}
    doc = (NS / "INCIDENT_EXTERNAL_TREE_CHANGE.md").read_text()
    for digest in recorded.values():
        assert digest in doc, "the incident must cite the recorded digest"
    assert "P5X_RESPONSIBLE    = NO" in doc


def test_no_p5x_commit_touched_anything_outside_p5x():
    for c in (ANCHOR_A, FIRST_FAIL, ANCHOR_B):
        files = _git("show", "--name-only", "--pretty=format:", c).split()
        outside = [f for f in files if f and not f.startswith(REL_NS)]
        assert not outside, f"{c} touched {outside}"
