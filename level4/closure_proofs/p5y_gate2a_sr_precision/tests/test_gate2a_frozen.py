"""Pre-T2 structural preconditions for P5Y Gate-2A.  No results needed."""
from __future__ import annotations
import ast, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
G1 = ROOT / "level4" / "closure_proofs" / "p5y_micropilot_gate1"
for p in (str(HERE), str(ROOT / "rebaseguard-proof" / "src")):
    if p not in sys.path:
        sys.path.insert(0, p)
import sr_precision as SP  # noqa: E402


def test_degree_set_is_exactly_8_and_10():
    assert SP.DEGREES == (8, 10)


def test_degree_12_is_prohibited():
    assert 12 not in SP.DEGREES
    src = (HERE / "sr_precision.py").read_text()
    assert "PROHIBITED" in src


def test_precision_grid_is_exactly_256_384_512():
    assert SP.PRECISIONS == (256, 384, 512)
    assert SP.CONTROL_PRECISION == 192


def test_no_extra_precision_point_can_be_added_post_result():
    """No 768/1024/2048 may appear as an executable literal (comments are exempt)."""
    assert set(SP.PRECISIONS) | {SP.CONTROL_PRECISION} == {192, 256, 384, 512}
    tree = ast.parse((HERE / "sr_precision.py").read_text())
    # precision may enter the computation ONLY through the frozen grid: every
    # workprec() argument must be the loop variable `bits`, never a literal.
    calls = [n for n in ast.walk(tree)
             if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "workprec"]
    assert calls, "no workprec call found"
    for c in calls:
        assert len(c.args) == 1 and isinstance(c.args[0], ast.Name) \
            and c.args[0].id == "bits", "workprec must take the frozen `bits` variable"
    # and run_cell is only ever invoked with a variable precision, not a literal
    rc = [n for n in ast.walk(tree)
          if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "run_cell"]
    for c in rc:
        assert not any(isinstance(a, ast.Constant) for a in c.args[:2]), \
            "run_cell must not be called with a literal degree or precision"


def test_same_gate1_patch_and_drift():
    assert SP.PATCH == (17, 11)
    assert (SP.E_NUM, SP.E_DEN) == (1, 4)
    assert SP.CAND_DEGREE == 16
    g1 = json.loads((G1 / "results" / "m2_sr_degree.json").read_text())
    assert g1["frozen"]["patch"] == list(SP.PATCH)
    assert g1["frozen"]["e"] == f"{SP.E_NUM}/{SP.E_DEN}"


def test_panel_geometry_is_the_frozen_gate1_output():
    g1 = json.loads((G1 / "results" / "m2_sr_degree.json").read_text())
    for d in SP.DEGREES:
        pr = g1["degrees"][str(d)]["panel_rule"]
        assert SP.FROZEN_PANEL[d]["n_z"] == pr["n_z"]
        assert abs(SP.FROZEN_PANEL[d]["h_z"] - pr["h_z"]) < 1e-18
        assert abs(SP.FROZEN_PANEL[d]["H_used"] - pr["H_used"]) < 1e-18


def test_panel_rule_is_not_recomputed_per_precision():
    """Geometry must come from FROZEN_PANEL, never from a per-cell root solve."""
    src = (HERE / "sr_precision.py").read_text()
    fn = src.split("def run_cell")[1].split("\ndef ")[0]
    assert "FROZEN_PANEL" in fn
    assert "continuous_panel_rule" not in fn
    assert "P1_MAX_REMAINDER * fact" not in fn, "no H_max root solve inside a cell"


def test_p2_safety_target_is_frozen_at_1e_minus_8():
    assert SP.P2_SAFETY_TARGET == 1e-8
    src = (HERE / "GATE2A_PREREGISTRATION.md").read_text()
    assert "P2_SAFETY_TARGET = 1e-8" in src


def test_selection_takes_the_lowest_qualifying_precision():
    src = (HERE / "sr_precision.py").read_text()
    block = src.split("# ---- selection")[1].split("# ---- degree-10")[0]
    assert "for b in PRECISIONS:" in block and "break" in block, \
        "selection must scan PRECISIONS in ascending order and stop at the first pass"
    assert SP.PRECISIONS == tuple(sorted(SP.PRECISIONS))


def test_degree10_replacement_requires_20pct_and_no_worse_margins():
    src = (HERE / "sr_precision.py").read_text()
    block = src.split("# ---- degree-10 replacement")[1].split("backend =")[0]
    assert "0.80 * cost8" in block, "materially-lower must be >= 20% cheaper"
    assert "P2_floor_precision_independent" in block, "margin comparison must include the floor"
    assert 'c_ = (c10["gates"]["P2_relative_half_width"] <= c8' in block


def test_diagnosis_uses_interval_radii_not_midpoints():
    src = (HERE / "sr_precision.py").read_text()
    fn = src.split("def classify")[1].split("\ndef ")[0]
    assert "acc_radius" in fn
    assert "midpoint" not in fn and ".mid()" not in fn


def test_reproducibility_cell_is_frozen_and_compares_endpoints():
    assert SP.REPRO_CELL == (8, 384)
    src = (HERE / "sr_precision.py").read_text()
    assert 'acc_lower_str' in src and 'acc_upper_str' in src


def test_timing_repeats_frozen_at_five():
    assert SP.TIMING_REPEATS == 5


def test_out_of_scope_work_is_absent():
    src = (HERE / "sr_precision.py").read_text().lower()
    for banned in ("s_min", "second_moment", "lean", "cover", "m_gt1", "xi_"):
        assert banned not in src, f"out-of-scope reference: {banned}"


def test_protected_tree_and_gate1_untouched():
    import subprocess
    diff = subprocess.run(["git", "diff", "--name-only", "c123b9b", "HEAD"], cwd=ROOT,
                          capture_output=True, text=True).stdout.split("\n")
    bad = [d for d in diff if d.strip()
           and not d.startswith("level4/closure_proofs/p5y_micropilot_gate1/")
           and not d.startswith("level4/closure_proofs/p5y_gate2a_sr_precision/")]
    assert not bad, f"protected paths modified: {bad}"
    st = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                        capture_output=True, text=True).stdout.split("\n")
    dirty = [s for s in st if s.strip()
             and "p5y_gate2a_sr_precision/" not in s]
    assert not dirty, f"working tree dirty outside Gate-2A: {dirty}"
