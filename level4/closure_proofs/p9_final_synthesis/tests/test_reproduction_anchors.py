"""G8 - anchors A1-A3 meet the tolerances hard-coded before execution."""
import json, os, pytest

@pytest.fixture(scope="module")
def rep(root):
    p = os.path.join(root, "results", "reproduction_anchors.json")
    return json.load(open(p))

def test_a1_p3_exact_witnesses_are_exact(rep):
    w = rep["p3_exact_witnesses"]
    assert w["all_exact"] is True
    for family in ("cusum_witness", "sr_witness"):
        for m, row in w[family].items():
            assert row["match"] and row["identity_exact"], (family, m)

def test_a2_rho_c_within_pre_set_tolerance(rep):
    r = rep["p3_rho_c"]
    assert r["pass"] is True
    assert r["max_abs_diff"] < r["tolerance"] == 1e-9
    assert r["sr_below_cusum_all_m"] is True

def test_a3_raw_mean_identity_machine_precision(rep):
    p = rep["p5_raw_identity"]
    assert p["pass"] is True
    assert p["max_abs_diff_overall"] < p["tolerance"] == 1e-12
    assert len(p["cells"]) == 18

def test_a4_reproduces_p7_cycle2_collapse_range(rep):
    """P7 published 5.6-9.4; descriptive check only (no pre-set threshold)."""
    vals = [r[k] for r in rep["p7_operational"] for k in r if k.startswith("cycle2_rho1")]
    assert vals, "no cycle-2 values recorded"
    assert 4.0 < min(vals) and max(vals) < 12.0, vals
