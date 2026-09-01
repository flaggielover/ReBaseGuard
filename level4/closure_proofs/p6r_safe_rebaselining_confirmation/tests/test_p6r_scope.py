"""P6R may not rewrite history, and may not touch protected trees.

Also asserts the ordering discipline that repairs blocking defect 3: the
precommit package contains no EVAL or REPLAY result.
"""
import hashlib
import json
import subprocess
from pathlib import Path

import pytest

NS = Path(__file__).resolve().parents[1]
CLOSURE = NS.parent
ROOT = NS.parents[2]
P6R_NAMESPACES = (
    "level4/closure_proofs/p6r_safe_rebaselining_confirmation/",
    "level4/closure_proofs/p6_safe_rebaselining/",
    "level4/closure_proofs/p6_safe_rebaselining_predesign/",
)
MANIFEST = NS / "precommit" / "historical_p6_manifest.json"


def test_historical_p6_namespaces_are_byte_identical():
    """The original campaign is evidence.  P6R must not have altered one byte."""
    man = json.loads(MANIFEST.read_text())
    bad = []
    for rel, want in man["files"].items():
        p = CLOSURE / rel
        if not p.exists():
            bad.append((rel, "MISSING"))
            continue
        got = hashlib.sha256(p.read_bytes()).hexdigest()
        if got != want:
            bad.append((rel, "MODIFIED"))
    assert not bad, f"historical P6 artifacts changed: {bad[:10]}"
    assert man["n_files"] == len(man["files"]) > 100


def test_no_new_file_added_inside_the_historical_namespaces():
    man = json.loads(MANIFEST.read_text())
    known = set(man["files"])
    extra = []
    for ns in ("p6_safe_rebaselining", "p6_safe_rebaselining_predesign"):
        for f in (CLOSURE / ns).rglob("*"):
            if f.is_file() and "__pycache__" not in f.parts:
                rel = str(f.relative_to(CLOSURE))
                if rel not in known:
                    extra.append(rel)
    assert not extra, f"files added to the historical record: {extra[:10]}"


def test_protected_tree_outside_p6_is_unmodified():
    out = subprocess.run(["git", "diff", "--name-only", "HEAD"], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout
    changed = [f for f in out.splitlines() if f.strip()]
    bad = [f for f in changed
           if not any(f.startswith(ns) for ns in P6R_NAMESPACES)]
    assert not bad, f"tracked files modified outside the P6 namespaces: {bad}"


def test_p6r_does_not_reimplement_the_method():
    """The object under confirmation must be the object that was adjudicated."""
    src = NS / "src" / "rebaseguard_p6r"
    names = {f.name for f in src.glob("*.py")}
    for forbidden in ("chain.py", "policy.py", "saw.py", "calibrate.py",
                      "metrics.py", "seeds.py"):
        assert forbidden not in names, (
            f"P6R re-implements {forbidden}; it must import it from rebaseguard_p6c")


def test_precommit_package_contains_no_eval_or_replay_result():
    """Blocking defect 3's repair: Checkpoint A is TUNE-only."""
    pre = NS / "precommit"
    assert pre.exists()
    for f in pre.glob("*.json"):
        blob = f.read_text()
        assert '"eval"' not in blob, f"{f.name} mentions the EVAL family"
        assert '"replay"' not in blob, f"{f.name} mentions the REPLAY family"
    man = json.loads((pre / "PRECOMMIT_MANIFEST.json").read_text()) \
        if (pre / "PRECOMMIT_MANIFEST.json").exists() else None
    if man is not None:
        assert man["contains_eval_results"] is False
        assert man["contains_replay_results"] is False


def test_baseline_selection_used_tune_only():
    """Blocking defect 1's repair, asserted from the artifact itself."""
    f = NS / "precommit" / "baseline_selection.json"
    if not f.exists():
        pytest.skip("selection not frozen yet")
    d = json.loads(f.read_text())
    assert d["family"] == "tune"
    for cell, row in d["cells"].items():
        assert row["family"] == "tune", cell
        assert row["rule"] == "S1", cell
        assert row["rho_selected"] in d["grid"], cell
