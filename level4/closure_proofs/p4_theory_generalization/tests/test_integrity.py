"""Priority 4 must not have touched anything it does not own."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

CAMPAIGN_RELATIVE = "level4/closure_proofs/p4_theory_generalization"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_protected_trees_are_unmodified(root, manifest):
    for tree in manifest["protected_trees_read_only"]:
        assert (root / tree).exists(), tree
        result = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", tree],
                                cwd=root)
        assert result.returncode == 0, tree


def test_priority4_writes_only_inside_its_own_namespace(root):
    changed = subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=root, text=True
    ).splitlines()
    outside = [line for line in changed
               if CAMPAIGN_RELATIVE not in line and line.strip()]
    assert not outside, outside


def test_frozen_inputs_match_their_recorded_hashes(campaign, manifest):
    frozen = manifest["frozen_new_inputs"]
    assert sha256(campaign / frozen["protocol"]) == frozen["protocol_sha256"]
    assert sha256(campaign / frozen["finite_support_witness"]) == \
        frozen["finite_support_witness_sha256"]


def test_lean_source_hash_is_recorded(campaign, manifest):
    lean = manifest["lean"]
    assert sha256(campaign / lean["source"]) == lean["source_sha256"]


def test_lean_reuse_of_the_closed_spines_is_declared_not_hidden(campaign,
                                                                manifest):
    source = (campaign / manifest["lean"]["source"]).read_text()
    assert "import StabilityMapP3" in source
    assert "sorry" not in source
    assert "axiom " not in source
    for spine in manifest["lean"]["consumed_closed_spines"]:
        assert spine.endswith(".lean")


def test_prior_art_inside_the_repository_is_declared(manifest):
    prior = manifest["prior_art_within_repository"]
    assert "location_family" in prior
    assert "location_family_track3ab" in prior
    assert "m = 1" in prior["location_family"]
    assert prior["priority4_delta"]


def test_the_campaign_declares_the_closed_tracks_as_read_only(manifest):
    protected = set(manifest["protected_trees_read_only"])
    for required in (
        "level4/closure_proofs/m_gt_1_priority1",
        "level4/closure_proofs/sr_derivative_priority2",
        "level4/closure_proofs/m_rho_stability_priority3",
        "level4/closure_proofs/location_family",
        "level4/closure_proofs/location_family_track3ab",
    ):
        assert required in protected


def test_master_seeds_are_confined_to_this_namespace(root, protocol):
    for seed in protocol["master_seeds"].values():
        # `-w` matters: the digit strings also occur inside unrelated float
        # literals in the historical Stage-C Monte Carlo tables
        hits = subprocess.run(
            ["git", "grep", "-l", "-w", str(seed), "--", ":!*.venv"],
            cwd=root, text=True, capture_output=True,
        ).stdout.split()
        assert all(CAMPAIGN_RELATIVE in path for path in hits), (seed, hits)


def test_no_frozen_artifact_is_referenced_for_writing(campaign):
    """No executable path of this campaign writes into a frozen namespace.

    The test suite itself is excluded: it names those paths precisely in order
    to assert that nothing writes to them."""
    for path in campaign.rglob("*.py"):
        if "__pycache__" in path.parts or "tests" in path.parts:
            continue
        text = path.read_text()
        for forbidden in ("m_gt_1_priority1/results", "sr_derivative_priority2/results",
                          "m_rho_stability_priority3/results"):
            if forbidden in text:
                assert "write_text" not in text.split(forbidden)[1][:400], path
