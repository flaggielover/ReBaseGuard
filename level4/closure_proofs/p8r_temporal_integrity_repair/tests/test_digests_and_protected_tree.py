"""Digest stability and protected-tree preservation.

``I2``/``I3`` demand that the frozen prose and the executable surface be
byte-identical to what the anchor recorded.  ``I11`` demands that nothing
outside the P8R namespace moved.  P8's own ``G12`` passed on this dimension; P8R
keeps the check and adds the protocol/source digests P8's provenance record
omitted.
"""
import json

import pytest

from make_manifests import (PROTECTED_TREES, protected_manifest,
                            protocol_digest, source_manifest)

#: the only tracked file outside the P8R namespace that this campaign is
#: authorised to touch.  Anything else differing is a violation.
AUTHORISED_ROOT_CHANGES = {"README.md"}


def test_source_manifest_matches_the_working_tree(p8r):
    rec = p8r / "SOURCE_MANIFEST.json"
    if not rec.exists():
        pytest.skip("SOURCE_MANIFEST.json not written yet")
    stored = json.loads(rec.read_text())
    now = source_manifest()
    diff = {k for k in set(stored["files"]) | set(now["files"])
            if stored["files"].get(k) != now["files"].get(k)}
    assert not diff, f"executable files changed since the anchor: {sorted(diff)}"
    assert stored["aggregate_sha256"] == now["aggregate_sha256"]


def test_protocol_digest_matches_the_working_tree(p8r):
    rec = p8r / "PROTOCOL_DIGEST.json"
    if not rec.exists():
        pytest.skip("PROTOCOL_DIGEST.json not written yet")
    stored = json.loads(rec.read_text())
    now = protocol_digest()
    assert stored["missing"] == [], stored["missing"]
    diff = {k for k in set(stored["files"]) | set(now["files"])
            if stored["files"].get(k) != now["files"].get(k)}
    assert not diff, f"frozen prose changed since the anchor: {sorted(diff)}"


def test_protected_trees_are_byte_identical(p8r):
    pre = p8r / "results" / "integrity" / "protected_tree_manifest_pre.json"
    if not pre.exists():
        pytest.skip("pre-campaign protected-tree manifest not written yet")
    before = json.loads(pre.read_text())
    now = protected_manifest()
    moved = {t for t in before["trees"]
             if before["trees"][t]["aggregate_sha256"]
             != now["trees"][t]["aggregate_sha256"]}
    assert not moved, f"protected trees changed: {sorted(moved)}"


def test_original_p8_namespace_is_untouched(p8r):
    pre = p8r / "results" / "integrity" / "protected_tree_manifest_pre.json"
    if not pre.exists():
        pytest.skip("pre-campaign protected-tree manifest not written yet")
    before = json.loads(pre.read_text())
    now = protected_manifest()
    key = "level4/closure_proofs/p8_model_class_robustness"
    assert key in before["trees"]
    assert before["trees"][key]["n_files"] > 100
    assert (before["trees"][key]["aggregate_sha256"]
            == now["trees"][key]["aggregate_sha256"]), \
        "P8 is a historical protected artifact and must not change"


def test_only_authorised_files_outside_p8r_differ(p8r):
    pre = p8r / "results" / "integrity" / "protected_tree_manifest_pre.json"
    if not pre.exists():
        pytest.skip("pre-campaign protected-tree manifest not written yet")
    before = json.loads(pre.read_text())
    now = protected_manifest()
    changed = {k for k in set(before["files"]) | set(now["files"])
               if before["files"].get(k) != now["files"].get(k)}
    assert not (changed - AUTHORISED_ROOT_CHANGES), \
        f"unauthorised changes outside P8R: {sorted(changed - AUTHORISED_ROOT_CHANGES)}"


def test_every_declared_protected_tree_exists(p8r):
    now = protected_manifest()
    for t in PROTECTED_TREES:
        assert t in now["trees"], t
        assert now["trees"][t]["n_files"] > 0, t
