"""P6R2 may repair derived artifacts; it may not touch the evidence."""
import hashlib
import json
import subprocess
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CLOSURE = NS.parent
ROOT = NS.parents[2]
FROZEN = NS / "precommit" / "frozen_inputs.json"
P6_NAMESPACES = ("level4/closure_proofs/p6_safe_rebaselining/",
                 "level4/closure_proofs/p6_safe_rebaselining_predesign/",
                 "level4/closure_proofs/p6r_safe_rebaselining_confirmation/",
                 "level4/closure_proofs/p6r2_literal_closure_repair/")


def test_every_frozen_input_is_byte_identical():
    fr = json.loads(FROZEN.read_text())
    bad = []
    for rel, want in fr["files"].items():
        p = CLOSURE / rel
        if not p.exists():
            bad.append((rel, "MISSING"))
        elif hashlib.sha256(p.read_bytes()).hexdigest() != want["sha256"]:
            bad.append((rel, "MODIFIED"))
    assert not bad, f"frozen P6R/P6 inputs changed: {bad[:10]}"
    assert fr["n_files"] == 37


def test_source_head_is_the_independently_reviewed_one():
    fr = json.loads(FROZEN.read_text())
    assert fr["independently_reviewed_final_p6r_head"] == \
        "73ecad84620e71b68db60612a7001707a2cbd741"
    assert fr["head_matches_reviewed"] is True
    assert fr["checkpoint_A"] == "fcc1355715426531c431e9390c9f12d1bad9b97c"
    assert fr["checkpoint_B"] == "185bda0f63da57162309111b0ff02215f6e805d1"


def test_historical_p6_and_p6r_manifests_still_hold():
    """P6R's own 121-file historical manifest must still verify."""
    man = json.loads((CLOSURE / "p6r_safe_rebaselining_confirmation" / "precommit"
                      / "historical_p6_manifest.json").read_text())
    bad = [rel for rel, want in man["files"].items()
           if not (CLOSURE / rel).exists()
           or hashlib.sha256((CLOSURE / rel).read_bytes()).hexdigest() != want]
    assert not bad, f"historical P6 artifacts changed: {bad[:10]}"


def test_protected_stage_and_priority_trees_are_unmodified():
    out = subprocess.run(["git", "diff", "--name-only", "HEAD"], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout
    changed = [f for f in out.splitlines() if f.strip()]
    bad = [f for f in changed if not any(f.startswith(ns) for ns in P6_NAMESPACES)]
    assert not bad, f"tracked files modified outside the P6 namespaces: {bad}"


def test_p6r2_writes_only_into_its_own_namespace():
    out = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout
    offenders = [l for l in out.splitlines() if l.strip()
                 and not l[3:].strip().startswith(
                     "level4/closure_proofs/p6r2_literal_closure_repair/")]
    assert not offenders, f"P6R2 wrote outside its namespace: {offenders}"


def test_p6r2_does_not_reimplement_the_scientific_object():
    src = NS / "src" / "rebaseguard_p6r2"
    names = {f.name for f in src.glob("*.py")}
    for forbidden in ("saw.py", "chain.py", "policy.py", "calibrate.py",
                      "select.py", "seeds.py"):
        assert forbidden not in names, f"P6R2 re-implements {forbidden}"
    # and nothing in P6R2 rewrites a calibration constant
    for f in src.glob("*.py"):
        t = f.read_text()
        assert "calibrate_saw" not in t, f"{f.name} recalibrates SAW-M"
