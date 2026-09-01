"""C6: nothing outside the two P6 namespaces may be written."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
P6_NAMESPACES = (
    "level4/closure_proofs/p6_safe_rebaselining/",
    "level4/closure_proofs/p6_safe_rebaselining_predesign/",
)
BASELINE = (ROOT / "level4/closure_proofs/p6_safe_rebaselining_predesign"
            / "results" / "worktree_baseline.txt")


def test_worktree_scope_is_p6_only():
    baseline = set(BASELINE.read_text().splitlines())
    out = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout
    offenders = [line for line in out.splitlines()
                 if line not in baseline
                 and not any(line[3:].strip().startswith(ns)
                             for ns in P6_NAMESPACES)]
    assert not offenders, f"writes outside the P6 namespaces: {offenders}"


def test_campaign_does_not_import_p5():
    src = Path(__file__).resolve().parents[1] / "src"
    hits = [f for f in src.rglob("*.py") if "rebaseguard_p5" in f.read_text()]
    assert not hits, f"P6 harness imports P5: {hits}"


def test_no_tracked_file_outside_p6_is_modified():
    """The frozen P1-P5/P7 and Stage A-F trees must be byte-identical."""
    out = subprocess.run(["git", "diff", "--name-only", "HEAD"], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout
    changed = [f for f in out.splitlines() if f.strip()]
    allowed = {"README.md"}          # already modified before P5 adjudication
    bad = [f for f in changed
           if f not in allowed and not any(f.startswith(ns) for ns in P6_NAMESPACES)]
    assert not bad, f"tracked files modified outside P6: {bad}"
