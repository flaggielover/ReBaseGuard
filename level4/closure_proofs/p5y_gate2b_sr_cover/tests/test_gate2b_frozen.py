"""Pre-T2 structural preconditions for P5Y Gate-2B.  No results needed."""
from __future__ import annotations
import ast, json, math, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
for p in (str(HERE), str(ROOT / "rebaseguard-proof" / "src")):
    if p not in sys.path:
        sys.path.insert(0, p)
import sr_cover as SC  # noqa: E402

SRC = (HERE / "sr_cover.py").read_text()


def test_degree_is_exactly_8_and_degree10_absent():
    assert SC.DEGREE == 8
    tree = ast.parse(SRC)
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign) and any(
                getattr(t, "id", "") == "DEGREE" for t in n.targets):
            assert n.value.value == 8
    assert "degree 10" not in SRC.lower().replace("degree 10 forbidden here", "")


def test_h_z_is_the_gate1_degree8_value():
    g1 = json.loads((ROOT / "level4/closure_proofs/p5y_micropilot_gate1/results/"
                     "m2_sr_degree.json").read_text())
    assert SC.H_Z == g1["degrees"]["8"]["panel_rule"]["h_z"]
    assert g1["degrees"]["8"]["panel_rule"]["n_z"] == 28


def test_t_panel_is_the_gate2a_256bit_value():
    g2 = json.loads((ROOT / "level4/closure_proofs/p5y_gate2a_sr_precision/results/"
                     "sr_precision.json").read_text())
    t = g2["cells"]["8@256"]["timing"]["t_panel_median"]
    assert abs(SC.T_PANEL - t) < 1e-6
    assert g2["selected_precision_degree8"] == 256


def test_compact_domain_is_e_star_not_12():
    """e_star = c_SR from the proved P5X-T3 compression; no extension to 12."""
    from flint import arb
    from rebaseguard_certify.arb_backend import workprec
    with workprec(192):
        _, _, c = SC.sr_constants()
        assert abs(float(c) - 6.755531464321473) < 1e-12
    tree = ast.parse(SRC)
    lits = {n.value for n in ast.walk(tree)
            if isinstance(n, ast.Constant) and isinstance(n.value, (int, float))}
    assert 12 not in lits and 12.0 not in lits, "no e_far = 12 may appear"


def test_subcell_formula_matches_the_production_architecture():
    """h = 1/(4 a C) with a = 2 phi(0), byte-identical to r1_stop_gate.py."""
    assert "1.0 / (4.0 * a * C)" in SRC
    r1 = (ROOT / "level4/closure_proofs/p5x_global_nonlinear_dynamics/"
          "compute_optimization_r1/r1_stop_gate.py").read_text()
    assert "h_max = arb(1) / (arb(4) * a * C)" in r1
    assert "a = arb(2) / (arb(2) * arb.pi()).sqrt()" in r1
    assert "a_const = arb(2) / (arb(2) * arb.pi()).sqrt()" in SRC


def test_resolvent_matches_certified_sr_component_parameters():
    cert = json.loads((ROOT / "level4/closure_proofs/sr_derivative/results/"
                       "sr_monotone_contraction.json").read_text())
    assert SC.CELLS == cert["cells"] and SC.N_MAX == cert["n"]
    assert SC.BITS == cert["precision_bits"]
    assert SC.CERT_Q_SAFE == (19, 100)
    assert SC.CERT_RESOLVENT == (25000, 19)


def test_live_patch_definition_is_frozen_and_algebraic():
    """Exclusion must come from the exact invariant, never from smallness."""
    fn = SRC.split("def patch_geometry_counts")[1].split("\ndef ")[0]
    assert "inv_e" in fn and "hi_lim" in fn
    assert "is_x0" in fn, "the reset state's patch must be kept"
    for bad in ("abs(", "tol", "1e-", "small"):
        assert bad not in fn, f"numerical-smallness criterion leaked in: {bad}"


def test_geometric_cover_is_not_multiplied_by_m():
    blk = SRC.split("# ---- (4) cost model")[1]
    # the SR geometric product carries the FUNCTION count, never m and never 24.5
    sr_line = [l for l in blk.split("\n") if l.strip().startswith("cpu_sr =")][0]
    assert "n * N_FUNCTIONS * panels * T_PANEL" in sr_line
    assert "24.5" not in sr_line and "m_mult" not in sr_line
    assert SC.N_FUNCTIONS == 49, "49 = 24.5 units x 2 functions, a FUNCTION count"
    # 24.5 may appear only on the CUSUM per-unit line, as a function multiplier
    uses = [l for l in blk.split("\n") if "24.5" in l]
    assert all("CUSUM_UNIT_CPU_H" in l for l in uses), f"24.5 misused: {uses}"


def test_no_production_solve_is_invoked():
    for banned in ("certify_at_exact_drift", "solve_candidates", "_kernel_polynomials",
                   "compose_candidate", "max_abs_on_reachable", "ra_certifier",
                   "r2_certifier", "sr_local"):
        assert banned not in SRC, f"production solve machinery referenced: {banned}"


def test_out_of_scope_absent():
    low = SRC.lower()
    for banned in ("s_min", "second_moment", "lean", "h3a", "m_gt1"):
        assert banned not in low


def test_walk_rule_is_deterministic_and_greedy():
    fn = SRC.split("def cover_walk")[1].split("\ndef ")[0]
    assert "min(e + 2.0 * h, e_star)" in fn
    assert "random" not in fn and "adapt" not in fn


def test_cover_walk_tiles_exactly_on_a_synthetic_envelope():
    """Deterministic coverage property, checkable without any SR evaluation."""
    env_e = [0.0, 1.0, 2.0, 3.0]
    env_C = [100.0, 10.0, 2.0, 1.0]
    cells = SC.cover_walk(env_e, env_C, 3.0, 0.79788456)
    assert cells[0][0] == 0.0
    assert abs(cells[-1][1] - 3.0) < 1e-12
    for k in range(len(cells) - 1):
        assert cells[k][1] == cells[k + 1][0], "gap or overlap in the tiling"
    assert all(b > a for a, b in cells)


def test_rounding_rule_is_ceiling_and_deterministic():
    fn = SRC.split("def patch_geometry_counts")[1].split("\ndef ")[0]
    assert "math.ceil(core_len / (2.0 * h_z))" in fn


def test_sensitivity_is_predeclared():
    assert SC.SENSITIVITY == 0.05
    assert "predeclared" in (HERE / "GATE2B_PREREGISTRATION.md").read_text().lower()


def test_protected_tree_and_prior_gates_untouched():
    diff = subprocess.run(["git", "diff", "--name-only", "c123b9b", "HEAD"], cwd=ROOT,
                          capture_output=True, text=True).stdout.split("\n")
    bad = [x for x in diff if x.strip() and not x.startswith(
        ("level4/closure_proofs/p5y_micropilot_gate1/",
         "level4/closure_proofs/p5y_gate2a_sr_precision/",
         "level4/closure_proofs/p5y_gate2b_sr_cover/"))]
    assert not bad, f"protected paths modified: {bad}"
    st = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                        capture_output=True, text=True).stdout.split("\n")
    dirty = [s for s in st if s.strip() and "p5y_gate2b_sr_cover/" not in s]
    assert not dirty, f"working tree dirty outside Gate-2B: {dirty}"
