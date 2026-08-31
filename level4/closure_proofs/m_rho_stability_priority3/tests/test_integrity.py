"""Protected-history and frozen-input integrity tests for Priority 3."""

from __future__ import annotations

import subprocess
import importlib.util

from rebaseguard_p3_map.common import read_json, sha256
from rebaseguard_p3_map.config import CAMPAIGN, PROTOCOL_SHA256, ROOT

CAMPAIGN_RELATIVE = "level4/closure_proofs/m_rho_stability_priority3"


def _manifest():
    return read_json(CAMPAIGN / "manifest.json")


def test_frozen_protocol_hash_is_unchanged():
    frozen = _manifest()["frozen_new_inputs"]
    assert sha256(CAMPAIGN / frozen["map_protocol"]) == frozen["map_protocol_sha256"]
    assert PROTOCOL_SHA256 == frozen["map_protocol_sha256"]


def test_every_upstream_source_hash_is_unchanged():
    for relative, expected in _manifest()["upstream_sources"].items():
        assert sha256(ROOT / relative) == expected, relative


def test_protected_trees_have_no_working_tree_modifications():
    for tree in _manifest()["protected_trees_read_only"]:
        result = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", tree],
                                cwd=ROOT)
        assert result.returncode == 0, tree


def test_priority3_writes_only_inside_its_own_namespace():
    changed = subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).splitlines()
    outside = [line for line in changed
               if CAMPAIGN_RELATIVE not in line and line.strip()]
    assert not outside, outside


def test_lean_source_hash_is_recorded():
    lean = _manifest()["lean"]
    assert sha256(CAMPAIGN / lean["source"]) == lean["source_sha256"]


def test_lean_reuse_of_the_closed_spines_is_declared_not_hidden():
    lean = _manifest()["lean"]
    source = (CAMPAIGN / lean["source"]).read_text()
    assert "import MGtOneClosure" in source
    assert "import SRPriority2" in source
    assert set(lean["consumed_closed_spines"]) == {
        "level4/closure_proofs/m_gt_1_priority1/lean/MGtOneClosure.lean",
        "level4/closure_proofs/sr_derivative_priority2/lean/SRPriority2.lean",
    }
    assert "synthesis layer" in lean["consumption_rationale"]


def test_inherited_conventions_are_not_silently_redefined():
    protocol = read_json(CAMPAIGN / "configs" / "MAP_PROTOCOL.json")
    d4 = (ROOT / "level4" / "closure_proofs" / "d4_phase_map" / "src"
          / "rebaseguard_d4" / "config.py").read_text()
    assert "BOUNDARY_TOLERANCE = 1e-12" in d4
    assert protocol["classification"]["boundary_tolerance"] == 1e-12
    assert "Z95 = 1.959963984540054" in d4
    assert protocol["uncertainty"]["z95"] == 1.959963984540054
    assert protocol["admissible_rho_domain"]["interval"] == [0.0, 1.0]


def test_priority1_and_priority2_conventions_match_each_other_and_this_campaign():
    p1 = read_json(ROOT / "level4" / "closure_proofs" / "m_gt_1_priority1"
                   / "results" / "numerical_correspondence.json")["protocol"]["model"]
    p2 = read_json(ROOT / "level4" / "closure_proofs" / "sr_derivative_priority2"
                   / "results" / "numerical_correspondence.json")["protocol"]["model"]
    for model in (p1, p2):
        assert model["alarm"] == "inclusive post-update"
        assert model["stopping"] == "ordinary tau from t=1"
        assert model["window"] == "w=min(m,tau), denominator w"
        assert model["terminal_increment"] == "included"


def _verifier_module():
    spec = importlib.util.spec_from_file_location(
        "priority3_repository_verifier", CAMPAIGN / "run_repository_verification.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_original_contract_requires_literal_current_suite_passes():
    required = set(_verifier_module().REQUIRED)
    assert {"priority1", "historical_sr", "track1b"} <= required


def test_environment_probes_are_live_and_internally_consistent():
    probes = _verifier_module().environment_probes()
    assert probes["ripgrep_available"] == (
        probes["ripgrep_binary_on_path"] is not None
    )
    assert probes["track1b_tree_hash_is_collation_dependent"]
    assert probes["track1b_tree_hash_matches_under_en_US_UTF_8"]
    assert probes["track1b_worktree_clean_against_head"]
    assert probes["track1b_untracked_files"] == []
