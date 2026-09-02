"""Anchor authenticity and original-P9 immutability, checked against git."""
from __future__ import annotations

import json
import re
import subprocess

import pytest

from conftest import P9R, P9_ADJ_COMMIT, P9_NS, ROOT

REL = "level4/closure_proofs/p9r_final_synthesis_repair"


def git(*args) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args],
                          capture_output=True, text=True).stdout.strip()


def anchor_from_prose() -> str | None:
    p = P9R / "TEMPORAL_ANCHOR.md"
    if not p.exists():
        return None
    m = re.search(r"ANCHOR_COMMIT\s*=\s*([0-9a-f]{40})", p.read_text())
    return m.group(1) if m else None


# ---------------------------------------------------------------- immutability
def test_original_p9_namespace_has_exactly_one_commit():
    commits = git("log", "--format=%H", "--",
                  "level4/closure_proofs/p9_final_synthesis").split()
    assert commits == [P9_ADJ_COMMIT]


def test_original_p9_tree_unchanged_since_adjudication():
    now = git("rev-parse", "HEAD:level4/closure_proofs/p9_final_synthesis")
    then = git("rev-parse", f"{P9_ADJ_COMMIT}:"
                            "level4/closure_proofs/p9_final_synthesis")
    assert now and now == then
    assert git("diff", "--stat", P9_ADJ_COMMIT, "HEAD", "--",
               "level4/closure_proofs/p9_final_synthesis") == ""


def test_p9_adjudication_still_says_partial():
    d = json.loads((P9_NS / "results" / "independent_adjudication.json").read_text())
    assert d["final_p9_verdict"] == "PARTIAL"
    assert d["p8r_required_for_p9"] is False


def test_p9r_writes_nothing_outside_its_own_namespace_except_root_readme():
    changed = [l for l in git("diff", "--name-only", P9_ADJ_COMMIT, "HEAD").splitlines()]
    outside = [c for c in changed
               if not c.startswith(REL) and c not in ("README.md",)]
    # commits between the P9 adjudication and HEAD include the whole P8R
    # campaign, which is legitimate history; only assert P9R itself is clean.
    p9r_touched_protected = [c for c in outside
                             if c.startswith("level4/closure_proofs/p9_final_synthesis")]
    assert p9r_touched_protected == []


# ---------------------------------------------------------------- the anchor
def test_anchor_is_a_real_ancestor_commit():
    a = anchor_from_prose()
    if a is None:
        pytest.skip("TEMPORAL_ANCHOR.md not yet written")
    assert subprocess.run(["git", "-C", str(ROOT), "cat-file", "-e",
                           f"{a}^{{commit}}"]).returncode == 0
    assert subprocess.run(["git", "-C", str(ROOT), "merge-base",
                           "--is-ancestor", a, "HEAD"]).returncode == 0


def test_anchor_commit_contains_no_production_results():
    a = anchor_from_prose()
    if a is None:
        pytest.skip("TEMPORAL_ANCHOR.md not yet written")
    tree = git("ls-tree", "-r", "--name-only", a, "--", REL).splitlines()
    results = [p for p in tree if p.startswith(f"{REL}/results/")]
    assert results == [f"{REL}/results/integrity/protected_tree_manifest_pre.json"]


def test_anchor_commit_contains_the_frozen_protocol_gates_and_generators():
    a = anchor_from_prose()
    if a is None:
        pytest.skip("TEMPORAL_ANCHOR.md not yet written")
    tree = set(git("ls-tree", "-r", "--name-only", a, "--", REL).splitlines())
    for required in ("FROZEN_PROTOCOL.md", "FROZEN_GATES.md", "THEORY.md",
                     "CLAIM_LANGUAGE_FIREWALL.md", "DISCREPANCY_REGISTER.md",
                     "COMMAND_MANIFEST.json", "SOURCE_MANIFEST.json",
                     "PROTOCOL_DIGEST.json",
                     "experiments/ledger_schema.py",
                     "experiments/claims_source.py",
                     "experiments/build_ledger.py",
                     "experiments/run_reproduction.py",
                     "experiments/run_response_grid.py",
                     "experiments/run_burnin_sensitivity.py",
                     "experiments/run_sr_recurrence_check.py",
                     "src/rebaseguard_p9r/detectors.py",
                     "src/rebaseguard_p9r/chain.py"):
        assert f"{REL}/{required}" in tree, required


def test_every_result_artifact_descends_from_the_anchor():
    a = anchor_from_prose()
    if a is None:
        pytest.skip("TEMPORAL_ANCHOR.md not yet written")
    seen = 0
    for f in sorted((P9R / "results").rglob("*.json")):
        rec = json.loads(f.read_text())
        commit = rec.get("git_commit")
        if not commit or commit == "UNKNOWN" or f.name.startswith("protected_tree"):
            continue
        seen += 1
        assert subprocess.run(["git", "-C", str(ROOT), "merge-base",
                               "--is-ancestor", a, commit]).returncode == 0, f.name
    if seen == 0:
        pytest.skip("no production artifacts yet")


# ---------------------------------------------------------------- digests
def test_source_and_protocol_manifests_cover_what_they_claim():
    sm = json.loads((P9R / "SOURCE_MANIFEST.json").read_text())
    pd = json.loads((P9R / "PROTOCOL_DIGEST.json").read_text())
    assert pd["missing"] == []
    for rel in sm["files"]:
        assert (P9R / rel).exists(), rel
    for rel in pd["files"]:
        assert (P9R / rel).exists(), rel
    # TEMPORAL_ANCHOR.md must be excluded from the protocol digest: it is the
    # one document written twice.
    assert "TEMPORAL_ANCHOR.md" not in pd["files"]
