"""Protected-scope enforcement and no-hidden-recalibration.

These are static tests: they read the repository, never write to it.
"""
import json
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
ALLOWED = "level4/closure_proofs/p8_model_class_robustness/"

PROTECTED_PREFIXES = (
    "closure/", "level4/src/", "level4/stage_b/", "level4/stage_c/",
    "level4/stage_c1/", "level4/stage_d/", "level4/stage_e/", "level4/stage_f/",
    "level4/closure_proofs/m_gt_1_priority1/",
    "level4/closure_proofs/sr_derivative_priority2/",
    "level4/closure_proofs/m_rho_stability_priority3/",
    "level4/closure_proofs/location_family/",
    "level4/closure_proofs/location_family_track3ab/",
    "level4/closure_proofs/p5_nonlinear_dynamics/",
    "level4/closure_proofs/p6_safe_rebaselining/",
    "level4/closure_proofs/p6_safe_rebaselining_predesign/",
    "level4/closure_proofs/p6r_safe_rebaselining_confirmation/",
    "level4/closure_proofs/p6r2_literal_closure_repair/",
    "level4/closure_proofs/p6r2b_gate9_crn_identity/",
    "level4/closure_proofs/p7_statistical_consequences/",
    "rebaseguard-lean/", "rebaseguard-proof/",
)


def _git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                          text=True).stdout


def test_worktree_has_no_changes_outside_the_p8_namespace():
    dirty = [l for l in _git("status", "--porcelain").strip().split("\n")
             if l.strip()]
    outside = [l for l in dirty if ALLOWED not in l]
    assert outside == [], f"P8 must not touch: {outside}"


@pytest.mark.parametrize("prefix", PROTECTED_PREFIXES)
def test_protected_tree_is_unmodified(prefix):
    man = json.loads((HERE / "results"
                      / "protected_tree_manifest_pre.json").read_text())
    rec = [v for v in man["protected_trees"].values() if v["prefix"] == prefix]
    assert rec, f"{prefix} is not in the pre-campaign manifest"
    import hashlib
    rows = []
    for line in _git("ls-files", "-s").strip().split("\n"):
        meta, path = line.split("\t", 1)
        mode, blob, _ = meta.split()
        if path.startswith(prefix):
            rows.append((path, f"{mode} {blob} {path}"))
    rows.sort(key=lambda r: r[0])
    h = hashlib.sha256("\n".join(r[1] for r in rows).encode()).hexdigest()
    assert h == rec[0]["sha256"], f"{prefix}: {len(rows)} files now, {rec[0]['n_files']} at record"


def test_p8_sources_never_write_into_a_protected_tree():
    """No write call in P8 code may target a protected-tree path constant."""
    import ast
    writers = {"write_text", "write_bytes", "savefig", "touch", "unlink",
               "rmdir", "rename", "replace", "mkdir"}
    protected = {"P3", "P4", "P7", "STAGE_D", "ROOT"}
    offenders = []
    for p in list((HERE / "src").rglob("*.py")) + list((HERE / "experiments").rglob("*.py")):
        text = p.read_text()
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                    and node.func.attr in writers:
                names = {n.id for n in ast.walk(node.func.value)
                         if isinstance(n, ast.Name)}
                if names & protected:
                    offenders.append(f"{p.name}: writes via {names & protected}")
    assert not offenders, offenders


def test_p8_writes_land_only_under_the_p8_results_and_figures_dirs():
    from rebaseguard_p8.config import FIGURES, P8, RESULTS
    assert str(RESULTS).startswith(str(P8))
    assert str(FIGURES).startswith(str(P8))
    assert P8.name == "p8_model_class_robustness"


def test_cusum_thresholds_are_byte_identical_to_stage_d():
    from rebaseguard_p8.config import stage_d_cusum_thresholds
    src = json.loads((ROOT / "level4" / "stage_d" / "results"
                      / "d3_nongaussian.json").read_text())
    ref = {r["family"]: r["threshold"] for r in src["rows"]}
    got = stage_d_cusum_thresholds()
    assert {k: float.hex(v) for k, v in got.items()} == \
           {k: float.hex(v) for k, v in ref.items()}


def test_frozen_gaussian_constants_match_their_sources():
    from rebaseguard_p8 import (CUSUM_THRESHOLD_GAUSSIAN, K_FROZEN,
                                SR_THRESHOLD_GAUSSIAN, TARGET_ARL0)
    from rebaseguard_p8.config import stage_d_target_arl0
    cal = json.loads((ROOT / "level4" / "stage_d" / "results"
                      / "calibration_d1.json").read_text())
    assert TARGET_ARL0 == stage_d_target_arl0()
    assert CUSUM_THRESHOLD_GAUSSIAN == 5.0 and K_FROZEN == 0.5
    assert float.hex(SR_THRESHOLD_GAUSSIAN) in json.dumps(
        {k: float.hex(v) for k, v in _flat_floats(cal).items()})


def _flat_floats(obj, prefix=""):
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.update(_flat_floats(v, f"{prefix}.{k}"))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.update(_flat_floats(v, f"{prefix}[{i}]"))
    elif isinstance(obj, float):
        out[prefix] = obj
    return out


def test_no_p8_module_reads_a_p5_or_p6_result_as_a_premise():
    """P5/P6 numerics are NOT_ALLOWED_AS_PREMISE (dependency audit D6, E4).

    Prose may reference them (P8 inherits P6's *procedural* CRN standard); what
    is forbidden is a code path that loads one of their result artifacts.
    """
    import ast
    forbidden = ("p5_nonlinear_dynamics", "p6_safe_rebaselining",
                 "p6r_safe_rebaselining", "p6r2_literal_closure_repair",
                 "p6r2b_gate9_crn_identity")
    offenders = []
    for p in list((HERE / "src").rglob("*.py")) + list((HERE / "experiments").rglob("*.py")):
        tree = ast.parse(p.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                v = node.value
                looks_like_a_path = "/" in v and "\n" not in v and len(v) < 200
                if looks_like_a_path and any(f in v for f in forbidden):
                    offenders.append(f"{p.name}: {v[:80]}")
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                mod = getattr(node, "module", "") or ""
                names = mod + " " + " ".join(a.name for a in node.names)
                assert not any(f in names for f in forbidden), \
                    f"{p.name} imports {names}"
    # docstring prose is allowed; only non-docstring string constants count
    assert not offenders, offenders
