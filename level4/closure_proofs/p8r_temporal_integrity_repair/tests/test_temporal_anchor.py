"""The temporal anchor is real: protocol before results, and nothing moved.

The authoritative P8 adjudication recorded ``PREREGISTRATION_TEMPORAL_ANCHOR =
PARTIAL`` because the whole P8 tree was untracked, there was no pre-result
commit, and the provenance record hashed neither the protocol nor the gates.
These tests demand a *repository-verifiable* anchor instead.
"""
import hashlib
import json
import re
import subprocess

import pytest

from make_manifests import FROZEN_PROSE, REL_P8R


def _anchor(p8r):
    doc = p8r / "TEMPORAL_ANCHOR.md"
    if not doc.exists():
        pytest.skip("TEMPORAL_ANCHOR.md not written yet")
    m = re.search(r"ANCHOR_COMMIT\s*=\s*`?([0-9a-f]{7,40})`?", doc.read_text())
    if not m or m.group(1).startswith("PENDING"):
        pytest.skip("anchor commit not recorded yet")
    return m.group(1)


def _git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args],
                          capture_output=True, text=True, check=True).stdout


def test_frozen_prose_and_source_exist_before_any_result(p8r, repo_root):
    anchor = _anchor(p8r)
    listing = _git(repo_root, "ls-tree", "-r", "--name-only",
                   anchor).splitlines()
    rel = [f[len(REL_P8R) + 1:] for f in listing
           if f.startswith(REL_P8R + "/")]
    for name in FROZEN_PROSE:
        assert name in rel, f"{name} missing from the anchor commit"
    assert any(f.startswith("src/") for f in rel)
    assert any(f.startswith("tests/") for f in rel)


def test_no_production_result_exists_at_the_anchor(p8r, repo_root):
    anchor = _anchor(p8r)
    listing = _git(repo_root, "ls-tree", "-r", "--name-only",
                   anchor).splitlines()
    rel = [f[len(REL_P8R) + 1:] for f in listing
           if f.startswith(REL_P8R + "/")]
    results = [f for f in rel if f.startswith("results/")
               and f != "results/integrity/protected_tree_manifest_pre.json"]
    assert results == [], f"production results present at the anchor: {results}"


def test_anchor_commit_is_an_ancestor_of_head(p8r, repo_root):
    anchor = _anchor(p8r)
    r = subprocess.run(["git", "-C", str(repo_root), "merge-base",
                        "--is-ancestor", anchor, "HEAD"])
    assert r.returncode == 0, "the anchor is not in HEAD's history"


def test_frozen_prose_is_byte_identical_to_the_anchor(p8r, repo_root):
    anchor = _anchor(p8r)
    for name in FROZEN_PROSE:
        blob = subprocess.run(
            ["git", "-C", str(repo_root), "show", f"{anchor}:{REL_P8R}/{name}"],
            capture_output=True, check=True).stdout
        cur = (p8r / name).read_bytes()
        assert hashlib.sha256(blob).hexdigest() \
            == hashlib.sha256(cur).hexdigest(), f"{name} changed after anchor"


def test_config_is_byte_identical_to_the_anchor(p8r, repo_root):
    """No threshold, budget or grid moved after the anchor."""
    anchor = _anchor(p8r)
    rel = f"{REL_P8R}/src/rebaseguard_p8r/config.py"
    blob = subprocess.run(["git", "-C", str(repo_root), "show",
                           f"{anchor}:{rel}"], capture_output=True,
                          check=True).stdout
    cur = (p8r / "src" / "rebaseguard_p8r" / "config.py").read_bytes()
    assert hashlib.sha256(blob).hexdigest() == hashlib.sha256(cur).hexdigest()


def test_every_result_carries_a_commit_at_or_after_the_anchor(p8r, repo_root):
    anchor = _anchor(p8r)
    seen = 0
    for p in sorted(p8r.glob("results/**/*.json")):
        if "protected_tree_manifest" in p.name:
            continue
        doc = json.loads(p.read_text())
        c = doc.get("git_commit")
        if not c or c == "UNAVAILABLE":
            continue
        seen += 1
        r = subprocess.run(["git", "-C", str(repo_root), "merge-base",
                            "--is-ancestor", anchor, c])
        assert r.returncode == 0, (
            f"{p.name} was generated at {c[:12]}, which does not descend from "
            f"the anchor {anchor[:12]}")
    if seen == 0:
        pytest.skip("no production results yet")
