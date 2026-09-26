"""K1R4 focused tests: scope, derivations, predecessors, and bound qualification evidence."""
import hashlib
import json
import sys
from fractions import Fraction as Fr
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CFG, CP = NS / "config", NS.parent
R = []


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def j(p):
    return json.loads(Path(p).read_text())


def check(name, fn):
    try:
        fn(); R.append((name, "PASS")); print(f"  PASS  {name}")
    except AssertionError as e:
        R.append((name, "FAIL")); print(f"  FAIL  {name}: {e}")


def test_A_checkpoint_binds_everything():
    cp = j(CFG / "CHECKPOINT.json")
    assert sha(CFG / "CHECKPOINT.json") == (CFG / "CHECKPOINT_HASH").read_text().strip()
    for n, h in cp["frozen_artifacts"].items():
        assert sha(CFG / n) == h, n
    for n, h in cp["generated_stages"].items():
        assert sha(NS / "driver" / n) == h, n
    assert cp["production_started"] is False and cp["genuine_results_present"] is False


def test_B_inherited_scope_unchanged():
    cp = j(CFG / "CHECKPOINT.json")["inherited"]
    k = j(CP / "p5y_k1r_successor/config/CHECKPOINT.json")
    assert cp["m_universe"] == k["m_universe"] == [1, 2, 3, 5]
    assert cp["target"] == k["theorem_target"] == "2/1"
    assert cp["precision_bits"] == k["precision_bits"] == 256
    assert cp["cost_cap_cpu_h"] == 150.0
    assert cp["cusum_domain"] == "(11/2, 49750555/8388608]" and cp["sr_upper"] == "1883835/262144"
    cu = j(CFG / "CUSUM_BRIDGE_CELL_TABLE.json")["cells"]
    kc = j(CP / "p5y_k1r_successor/config/CUSUM_BRIDGE_PLAN.json")["partition"]["children"]
    assert [(Fr(c["left"][0]), Fr(c["right"][0])) for c in cu] == \
           [(Fr(x["lo"]["exact"]), Fr(x["hi"]["exact"])) for x in kc], "CUSUM cells moved"


def test_C_q_sr_is_the_frozen_terminal_floor():
    d = j(CFG / "Q_SR_DERIVATION.json")
    w = j("/home/ubuntu/work/ReBaseGuard/level4/closure_proofs/p5y_k1_cover_ledger_successor/config/cover_witnesses.json")
    assert Fr(d["q_SR"]) == Fr(w["detectors"]["SR"]["terminal_floor_q"], w["grid_denominator"])
    assert d["floor_two_sided"]["floor_of_lower"] == d["floor_two_sided"]["floor_of_upper"] == 67555314
    assert d["old_endpoint_gap"]["confirmed"] is True


def test_D_scope_amendment_class():
    a = j(CFG / "SCOPE_AMENDMENT.json")
    assert a["SCOPE_CHANGE_CLASS"] == "DOMAIN_ENLARGEMENT_TO_REMOVE_CERTIFICATE_GAP"
    assert Fr(a["new_sr_bridge_lower_endpoint"]) < Fr(a["old_k1r_sr_bridge_lower_endpoint"])
    assert a["decided_before_any_bridge_result"] is True


def test_E_partition_and_universe():
    t = j(CFG / "SR_BRIDGE_CELL_TABLE.json")
    assert t["n_cells"] == 6 and [c["index"] for c in t["cells"]] == list(range(2000, 2006))
    assert all(c["terminal"] is False and all(Fr(c[f][1]) == 0 for f in ("left", "right", "e0", "rho", "C_evaluation"))
               for c in t["cells"])
    assert all(Fr(c["rho"][0]) <= Fr(1, 25) for c in t["cells"])
    u = j(CFG / "SR_BRIDGE_UNIVERSE.json")
    assert u["obligations_per_cell"] == 28 and u["theorem_invariant"] is True
    assert all(v["ok"] and len(v["units"]) == 28 for v in u["cells"].values())


def test_F_cost_fits_cap():
    c = j(CFG / "COST_ACCOUNTING.json")
    assert c["consumed_genuine_cpu_h"] == 0.0 and c["expected"]["total_cpu_h"] < c["cap_cpu_h_shared"] == 150.0


def test_G_predecessors_untouched():
    k1 = CP / "p5y_k1r_successor/config"
    assert sha(k1 / "CHECKPOINT.json") == (k1 / "CHECKPOINT_HASH").read_text().strip()
    k2 = CP / "p5y_k1r2_bridge_executor/config"
    assert sha(k2 / "CHECKPOINT.json") == (k2 / "CHECKPOINT_HASH").read_text().strip()
    assert (CP / "p5y_k1r3_bridge_successor/evidence/K1R3_SCOPE_HALT.json").exists()
    assert sha(CP / "p5y_k1r_successor/evidence/B1_ADMISSION_RESULT.json") == \
        "41fd34c6ede08b358c9b897f82662e9dd258d3c1619464a47e7f568ebf9f37bb"


def test_H_qualification_evidence():
    q = j(NS / "evidence/QUALIFICATION_K1R4.json")
    assert q["verdict"] == "PASS" and q["gates_passed"] == q["gates_total"] == 12
    assert q["negatives_passed"] == q["negatives_total"] == 15
    assert q["checkpoint_sha256"] == (CFG / "CHECKPOINT_HASH").read_text().strip()
    r = j(NS / "evidence/REPLAY_369.json")
    assert r["cells_equivalent"] == 369 and r["scientific_leaf_differences"] == 0 and r["patch_solves"] == 0


def main() -> int:
    print("K1R4 tests")
    for n, f in sorted((k, v) for k, v in globals().items() if k.startswith("test_")):
        check(n.replace("test_", ""), f)
    bad = [x for x in R if x[1] != "PASS"]
    print(f"\n{len(R) - len(bad)}/{len(R)} tests passed")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
