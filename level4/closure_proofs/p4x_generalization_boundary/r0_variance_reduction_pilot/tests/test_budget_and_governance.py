"""Budget accounting, governance, and the absence of any binding checkpoint."""

from __future__ import annotations

import subprocess

CPU_CAP_SECONDS = 4 * 3600

DOCS = ("README.md", "PILOT_REPORT.md", "PRECISION_POLICY.md",
        "DRAFT_CHECKPOINT_A.md")

#: Positive assertions only; the negated forms are the point of these documents.
FORBIDDEN = (
    "p4 = closed",
    "p4 is closed",
    "p4x = closed",
    "level-4 global closure is established",
    "novelty is established",
    "binding checkpoint created",
    "checkpoint a is active",
)


def test_pilot_respected_its_cpu_cap(pilot):
    assert pilot["cpu_budget_seconds"] == CPU_CAP_SECONDS
    assert pilot["cpu_used_seconds"] <= CPU_CAP_SECONDS
    assert pilot["cpu_used_seconds"] > 0


def test_total_pilot_cpu_including_sizing_is_within_cap(pilot, sizing, cut23):
    total = pilot["cpu_used_seconds"] + sum(
        r["cpu_seconds"] for r in sizing["rows"])
    assert total <= CPU_CAP_SECONDS
    assert cut23["new_simulation_performed"] is False


def test_pilot_is_not_binding_and_creates_no_checkpoint(pilot, cut23):
    assert pilot["binding"] is False
    assert pilot["checkpoint_created"] is False
    assert pilot["classification"] == "PRE_FREEZE_COST_AND_PRECISION_PILOT"
    assert cut23["binding"] is False


def test_no_binding_checkpoint_file_exists(pilot_dir):
    boundary = pilot_dir.parent
    for path in boundary.rglob("*.md"):
        name = path.name.upper()
        if "CHECKPOINT" in name:
            assert name.startswith("DRAFT_"), path
            head = path.read_text()[:2000].upper()
            assert "DRAFT" in head, path
            assert "NOT ACTIVE" in head or "NOT ACTIVATED" in head, path


def test_pilot_uses_a_fresh_seed_namespace(pilot, p4_protocol):
    """No pilot block can coincide with a frozen Priority-4 block."""
    frozen_seeds = set(p4_protocol["master_seeds"].values())
    assert pilot["seed_base"] == 4110000
    for res in pilot["results"].values():
        assert res["config"]["seed"] not in frozen_seeds
        assert res["config"]["seed"] // 10000 != 401


def test_documents_exist_and_avoid_overclaim(pilot_dir):
    for name in DOCS:
        path = pilot_dir / name
        assert path.exists(), name
        text = path.read_text()
        assert len(text) > 700, name
        lower = text.lower()
        for phrase in FORBIDDEN:
            assert phrase not in lower, (name, phrase)


def test_documents_restate_p4_as_partial(pilot_dir):
    for name in DOCS:
        assert "PARTIAL" in (pilot_dir / name).read_text(), name


def test_pilot_writes_only_inside_the_p4x_namespace(root):
    out = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=root, capture_output=True, text=True, check=True,
    )
    prefix = "level4/closure_proofs/p4x_generalization_boundary/"
    for line in out.stdout.splitlines():
        path = line[3:].strip().strip('"')
        assert path.startswith(prefix), line


def test_protected_trees_unchanged(root, audit_results):
    for path, expected in audit_results["protected_tree_objects_at_head"].items():
        out = subprocess.run(["git", "rev-parse", f"HEAD:{path}"],
                             cwd=root, capture_output=True, text=True)
        assert out.returncode == 0, path
        assert out.stdout.strip() == expected, path


def test_frozen_p4_tree_is_untouched(root):
    out = subprocess.run(
        ["git", "status", "--porcelain",
         "level4/closure_proofs/p4_theory_generalization"],
        cwd=root, capture_output=True, text=True, check=True,
    )
    assert out.stdout.strip() == ""
