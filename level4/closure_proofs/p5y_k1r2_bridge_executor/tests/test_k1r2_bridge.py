"""K1R2 focused tests: scope immutability, bridge-only resolution, reproducible hashes."""
import hashlib
import json
import sys
from fractions import Fraction as Fr
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CFG = NS / "config"
K1R = NS.parent / "p5y_k1r_successor" / "config"
R = []


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def j(p):
    return json.loads(Path(p).read_text())


def check(name, fn):
    try:
        fn(); R.append((name, "PASS", "")); print(f"  PASS  {name}")
    except AssertionError as e:
        R.append((name, "FAIL", str(e)[:150])); print(f"  FAIL  {name}: {e}")
    except Exception as e:                                  # noqa: BLE001
        R.append((name, "ERROR", f"{type(e).__name__}: {e}")); print(f"  ERROR {name}: {e}")


def test_A_domains_identical_to_k1r():
    cu_k, sr_k = j(K1R / "CUSUM_BRIDGE_PLAN.json"), j(K1R / "SR_BRIDGE_PLAN.json")
    cu, sr = j(CFG / "CUSUM_BRIDGE_CELL_TABLE.json"), j(CFG / "SR_BRIDGE_CELL_TABLE.json")
    for plan, tbl, n in ((cu_k, cu, 2), (sr_k, sr, 6)):
        assert Fr(tbl["domain"]["lo"]["exact"]) == Fr(plan["domain"]["lo"]["exact"])
        assert Fr(tbl["domain"]["hi"]["exact"]) == Fr(plan["domain"]["hi"]["exact"])
        assert tbl["cell_count"] == n == plan["partition"]["cells"]
        for k1rc, c in zip(plan["partition"]["children"], tbl["cells"]):
            assert Fr(c["left"]) == Fr(k1rc["lo"]["exact"]), "bridge left endpoint moved"
            assert Fr(c["right"]) == Fr(k1rc["hi"]["exact"]), "bridge right endpoint moved"


def test_B_inherited_science_identical():
    cp = j(CFG / "CHECKPOINT.json")["inherited_unchanged"]
    k = j(K1R / "CHECKPOINT.json")
    assert cp["m_universe"] == k["m_universe"] == [1, 2, 3, 5]
    assert cp["target"] == k["theorem_target"] == "2/1"
    assert cp["precision_bits"] == k["precision_bits"] == 256
    assert cp["b_cover_cap"] == k["b_cover_cap"] == "1/20"
    assert cp["cost_cap_cpu_h"] == j(K1R / "COST_CAP.json")["cap_cpu_h"] == 150.0


def test_C_k1r_freeze_untouched():
    k = j(K1R / "CHECKPOINT.json")
    assert sha(K1R / "CHECKPOINT.json") == (K1R / "CHECKPOINT_HASH").read_text().strip()
    assert all(sha(K1R / n) == h for n, h in k["frozen_artifacts"].items())
    man = j(K1R / "SOURCE_MANIFEST.json")["files"]
    assert all(sha(K1R.parent / f) == h for f, h in man.items()), "K1R source drift"


def test_D_bridge_indices_disjoint_from_history():
    cu, sr = j(CFG / "CUSUM_BRIDGE_CELL_TABLE.json"), j(CFG / "SR_BRIDGE_CELL_TABLE.json")
    assert [c["index"] for c in cu["cells"]] == [1000, 1001]
    assert [c["index"] for c in sr["cells"]] == [2000, 2001, 2002, 2003, 2004, 2005]
    assert cu["historical_index_range_refused"] == [0, 325]
    assert sr["historical_index_range_refused"] == [0, 368]
    assert cu["historical_indices_resolvable"] is False
    assert sr["historical_indices_resolvable"] is False
    for t in (cu, sr):
        for c in t["cells"]:
            assert c["bridge_only"] is True and c["historical_index"] is None


def test_E_geometry_reproducible_and_monotone():
    w = j(CFG / "BRIDGE_GEOMETRY_WITNESS.json")
    assert w["bits"] == 192 and w["python_flint"] == "0.9.0" and w["decisive"] is False
    for det, cap in (("CUSUM", 8594972549), ("SR", 8589984305)):
        d = w["detectors"][det]
        assert d["monotone_non_increasing"] is True
        assert d["capped_by_last_frozen_cell"] == cap
        assert all(r["C_upper_num"] <= cap for r in d["rows"]), "C_upper above the frozen cap"
        prev = cap
        for r in d["rows"]:
            assert r["C_upper_num"] == min(prev, r["rounded_C_num"]), \
                "frozen monotone C_upper rule not applied"
            prev = r["C_upper_num"]
        assert all(r["width_within_frozen_step_rule"] for r in d["rows"]), "step rule violated"
    cu = j(CFG / "CUSUM_BRIDGE_CELL_TABLE.json")
    for c, r in zip(cu["cells"], w["detectors"]["CUSUM"]["rows"]):
        assert c["C_upper"] == f"{r['C_upper_num']}/4294967296"
        assert Fr(c["C_evaluation"]) == Fr(r["left"])


def test_F_sr_rho_cap_and_aws_only():
    sr = j(CFG / "SR_BRIDGE_CELL_TABLE.json")
    assert sr["rho_cap"] == "1/25" and sr["rho_cap_satisfied"] is True
    assert all(Fr(c["rho"]) <= Fr(1, 25) for c in sr["cells"])
    a = j(CFG / "SR_BRIDGE_AUTHORIZATION.json")
    assert a["topology"] == "A_AWS_ONLY" and a["active_host"] == "AWS"
    assert a["hosts"]["VULTR"]["cells"] == []
    assert a["synthetic_path"] == "PROHIBITED"
    assert a["result_bearing"] is False
    rt = j(CFG / "RUNTIME_CONTRACT.json")
    assert rt["hosts"]["SR_BRIDGE"]["permitted"] == ["AWS"]
    assert rt["hosts"]["SR_BRIDGE"]["vultr"] == "PROHIBITED"
    assert rt["hosts"]["CUSUM_BRIDGE"]["mac"] == "PROHIBITED"


def test_G_predecessor_contract():
    pb = j(CFG / "PREDECESSOR_BINDING.json")
    assert pb["k1r"]["freeze_commit"] == "7f671b9ba2d7111b5e8cde010bc660904925fa1c"
    assert pb["k1r"]["checkpoint_sha256"] == (K1R / "CHECKPOINT_HASH").read_text().strip()
    assert pb["b1"]["status"] == "INHERITED_PASS" and pb["b1"]["fallback_run"] is False
    assert pb["temporal"]["bridge_scientific_results_before_k1r2_freeze"] == 0
    assert pb["lineage"]["K1R2"] == "bridge-executor successor"
    assert pb["lineage"]["rewrite_of_k1r_as_pass_or_closed"] == "PROHIBITED"
    b1 = NS.parent / "p5y_k1r_successor" / "evidence" / "B1_ADMISSION_RESULT.json"
    assert sha(b1) == pb["b1"]["result_sha256"], "B1 evidence changed"


def test_H_checkpoint_binds_and_reproduces():
    cp = j(CFG / "CHECKPOINT.json")
    for n, h in cp["frozen_artifacts"].items():
        assert sha(CFG / n) == h, f"{n} drift"
    assert sha(CFG / "CHECKPOINT.json") == (CFG / "CHECKPOINT_HASH").read_text().strip()
    assert cp["production_started"] is False and cp["bridge_results_present"] is False
    assert cp["k1_status"].startswith("PARTIAL")
    assert "HALTED_BY_GOVERNANCE" in cp["k1r_status"] and "B1 PASS" in cp["k1r_status"]


def main() -> int:
    print("K1R2 bridge-executor tests")
    for n, f in sorted((k, v) for k, v in globals().items() if k.startswith("test_")):
        check(n.replace("test_", ""), f)
    bad = [x for x in R if x[1] != "PASS"]
    print(f"\n{len(R) - len(bad)}/{len(R)} tests passed")
    for x in bad:
        print("  ", x)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
