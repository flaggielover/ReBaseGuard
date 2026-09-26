"""K1R preregistration self-check. Read-only; no production, no host computation."""
import hashlib
import json
import sys
from fractions import Fraction as Fr
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CFG = NS / "config"
R = []


def check(name, fn):
    try:
        fn()
        R.append((name, "PASS", ""))
        print(f"  PASS  {name}")
    except AssertionError as e:
        R.append((name, "FAIL", str(e)[:170]))
        print(f"  FAIL  {name}: {e}")
    except Exception as e:                                   # noqa: BLE001
        R.append((name, "ERROR", f"{type(e).__name__}: {str(e)[:150]}"))
        print(f"  ERROR {name}: {type(e).__name__}: {str(e)[:150]}")


def j(name):
    return json.loads((CFG / name).read_text())


def test_A_domain_cover_gap_free():
    d = j("DOMAIN_COVER.json")
    for det, c, close in (("CUSUM", Fr(11, 2), Fr(49750555, 8388608)),
                          ("SR", Fr(3803026123175981, 562949953421312), Fr(1883835, 262144))):
        s = d["detectors"][det]
        seg = s["segments"]
        assert Fr(seg[0]["hi"]["exact"]) == c, f"{det}: compact does not end at c"
        assert Fr(seg[1]["lo"]["exact"]) == c and Fr(seg[1]["hi"]["exact"]) == close, f"{det} bridge"
        assert Fr(seg[2]["lo"]["exact"]) == close, f"{det}: far field does not start at e_close"
        assert seg[2]["hi"] == "+infinity"
        g = s["gap_free_proof"]
        assert g["gaps"] == [] and g["omitted_endpoints"] == [] and g["children_chain_exact"]
        assert Fr(g["compact_hi_equals_bridge_lo"]) == c
        assert Fr(g["bridge_hi_equals_far_field_lo"]) == close
        pts = g["double_ownership_points"]
        assert len(pts) == 1 and Fr(pts[0]["point"]) == close
        assert pts[0]["certifier"] == "FAR_FIELD_INHERITED"


def test_B_children_recompose_exactly():
    d = j("DOMAIN_COVER.json")
    for det, n in (("CUSUM", 2), ("SR", 6)):
        s = d["detectors"][det]; kids = s["children"]
        assert len(kids) == n, f"{det}: {len(kids)} children"
        lo, hi = Fr(s["segments"][1]["lo"]["exact"]), Fr(s["segments"][1]["hi"]["exact"])
        assert Fr(kids[0]["lo"]["exact"]) == lo and Fr(kids[-1]["hi"]["exact"]) == hi
        w = {Fr(k["width"]["exact"]) for k in kids}
        assert len(w) == 1, f"{det}: children are not equal width"
        assert sum(Fr(k["width"]["exact"]) for k in kids) == hi - lo, f"{det}: widths do not sum"
        for a, b in zip(kids, kids[1:]):
            assert Fr(a["hi"]["exact"]) == Fr(b["lo"]["exact"]), f"{det}: chain break"
        for k in kids:
            assert k["lower_open"] is True and k["upper_closed"] is True


def test_C_cell_counts_and_m_universe():
    cu, sr = j("CUSUM_BRIDGE_PLAN.json"), j("SR_BRIDGE_PLAN.json")
    assert cu["partition"]["cells"] == 2 and len(cu["partition"]["children"]) == 2
    assert sr["partition"]["cells"] == 6 and len(sr["partition"]["children"]) == 6
    for p in (cu, sr):
        assert p["theorem_target"]["m_universe"] == [1, 2, 3, 5], "m universe drift"
        assert p["theorem_target"]["target"] == "2/1" and p["theorem_target"]["strict"]
        assert p["precision_bits"] == 256, "precision drift"
        assert p["gates"]["B_cover_cap"] == "1/20", "B_cover cap drift"
        assert p["refinement"]["max_refinement_depth"] == 0
        assert p["refinement"]["adaptive_refinement_after_results"] == "PROHIBITED"
        assert p["domain"]["endpoint_shrinkage"] == "PROHIBITED"
    assert cu["obligations_created"] == 8 and sr["obligations_created"] == 24


def test_D_sr_rho_constraint_and_host():
    sr = j("SR_BRIDGE_PLAN.json")
    rc = sr["rho_constraint"]
    assert rc["satisfied_by_every_child"] is True
    assert all(Fr(k["rho"]["exact"]) <= Fr(rc["r_max"]) for k in sr["partition"]["children"])
    h = sr["host_runtime_contract"]
    assert h["host"] == "AWS ONLY" and h["aws_permitted"] and not h["vultr_permitted"]
    assert "PROHIBITED" in h["vultr_substitution"] and h["mac_as_producer"] == "PROHIBITED"
    assert sr["existing_campaign"]["cells"] == 369
    assert sr["existing_campaign"]["modification"].startswith("PROHIBITED")


def test_E_cusum_host_contract():
    cu = j("CUSUM_BRIDGE_PLAN.json")
    h = cu["host_runtime_contract"]
    assert h["mac_as_producer"] == "PROHIBITED"
    assert "runtime_identity_binding" in h and h["permission_basis"]


def test_F_b1_decision_is_result_independent():
    b = j("B1_ADMISSION_CONTRACT.json")
    assert b["decision_is_outcome_independent"] is True
    assert b["all_or_nothing"] is True
    ids = [c["id"] for c in b["conditions"]]
    assert ids == [f"A{i}" for i in range(1, 11)], f"admission conditions: {ids}"
    for c in b["conditions"]:
        assert c["decidable_without_scientific_values"] is True, c["id"]
        assert c["class"] in ("structural", "identity", "governance"), c
    # no condition may read a scientific value: the checks must not name result fields
    blob = json.dumps(b["conditions"]).lower()
    for k in ("enclosure", "majorant", "margin", "utilisation", "utilization"):
        assert k not in blob, f"an admission condition mentions {k!r}"
    forb = json.dumps(b["decision_inputs_forbidden"]).lower()
    for k in ("obligation status", "enclosure", "utilization", "margin", "majorant"):
        assert k in forb, f"the forbidden-input list does not name {k!r}"
    perm = json.dumps(b["decision_inputs_permitted"]).lower()
    for k in ("enclosure", "majorant", "margin", "status"):
        assert k not in perm, f"a permitted decision input mentions {k!r}"
    r = b["routes"]
    assert set(r) == {"AUX5_COMPOSITE_ADMISSION", "PREREGISTERED_RECOMPUTE_FALLBACK"}
    assert r["AUX5_COMPOSITE_ADMISSION"]["fallback_must_not_run"] is True
    assert r["AUX5_COMPOSITE_ADMISSION"]["new_compute_cpu_h"] == 0.0
    assert "every condition A1..A10 PASSES" in r["AUX5_COMPOSITE_ADMISSION"]["taken_when"]


def test_G_b1_fallback_frozen_exactly():
    f = j("B1_ADMISSION_CONTRACT.json")["routes"]["PREREGISTERED_RECOMPUTE_FALLBACK"]
    assert f["cells"] == [319, 320, 321, 322, 323]
    assert f["total_children"] == 10 and "exactly once" in f["split"]
    assert "2 equal exact-rational children" in f["split"]
    assert f["m_universe"] == [1, 2, 3, 5]
    assert f["second_refinement"] == "PROHIBITED"
    assert "Mac" in f["host"]


def test_H_kill_gates_frozen():
    cp = j("CHECKPOINT.json")
    want = {"G_SCIENCE", "G_COVERAGE", "G_BUDGET", "G_GOVERNANCE", "G_AUX5", "G_AUX5_STATUS",
            "G_COST", "G_SCOPE"}
    got = {g["id"] for g in cp["kill_gates"]}
    assert got == want, f"kill gates: {sorted(got ^ want)}"
    by = {g["id"]: g for g in cp["kill_gates"]}
    assert by["G_SCIENCE"]["action"].startswith("HALT")
    assert "refinement" in by["G_SCIENCE"]["prohibited_response"]
    assert "BEFORE" in by["G_COST"]["action"]
    for gid in ("G_COVERAGE", "G_BUDGET", "G_GOVERNANCE", "G_SCOPE"):
        assert by[gid]["action"] == "HALT", gid


def test_I_cost_cap_initialised_at_zero():
    c = j("COST_CAP.json")
    assert c["cap_cpu_h"] == 150.0
    assert c["consumed_new_cpu_h"] == 0.0, "K1R compute accounting is not zero"
    e = c["expected"]
    assert abs(e["total_expected_cpu_h"] - (e["cusum_bridge_cpu_h"] + e["sr_bridge_cpu_h"])) < 1e-6
    assert e["b1_admission_cpu_h"] == 0.0 and e["b1_fallback_if_needed_cpu_h"] == 3.2
    assert e["total_expected_cpu_h"] < c["cap_cpu_h"]
    assert e["total_expected_with_fallback_cpu_h"] < c["cap_cpu_h"]


def test_J_immutable_history_and_inherited_identities():
    cp = j("CHECKPOINT.json")
    im = cp["immutable_history"]
    assert im["P5"] == im["P5X"] == im["P5Y_K1"] == "PARTIAL"
    a = im["adjudication"]
    assert a["CUSUM_K1"] == "INCOMPLETE" and a["K1_FAR_FIELD"] == "FAIL"
    assert a["SR_PS1_K1"] == "PASS" and a["K1_FINAL_VERDICT"] == "K1_PARTIAL"
    inh = cp["inherited_evidence"]
    assert inh["sr_ps1_campaign"]["cells"] == 369
    assert inh["sr_ps1_campaign"]["obligations"] == 10332
    assert inh["sr_ps1_campaign"]["modification"] == "PROHIBITED"
    assert inh["far_field"]["theorem"] == "P5X-T3"
    assert inh["far_field"]["modification"] == "PROHIBITED"
    assert inh["cusum_historical"]["modification"] == "PROHIBITED"
    assert len(inh["cusum_historical"]["failed_obligations"]) == 5
    assert cp["result_bearing"] is False and cp["production_started"] is False
    assert cp["genuine_results_present"] is False
    assert "K1 remains PARTIAL" in cp["k1_status_after_k1r_freeze"]


def test_K_checkpoint_binds_every_artifact():
    cp = j("CHECKPOINT.json")
    for name, h in cp["frozen_artifacts"].items():
        p = CFG / name
        assert p.exists(), f"{name} missing"
        assert hashlib.sha256(p.read_bytes()).hexdigest() == h, f"{name} hash drift"
    assert set(cp["frozen_artifacts"]) == {"DOMAIN_COVER.json", "B1_ADMISSION_CONTRACT.json",
                                           "CUSUM_BRIDGE_PLAN.json", "SR_BRIDGE_PLAN.json",
                                           "COST_CAP.json"}
    hp = CFG / "CHECKPOINT_HASH"
    assert hashlib.sha256((CFG / "CHECKPOINT.json").read_bytes()).hexdigest() == \
        hp.read_text().strip(), "checkpoint hash file drift"


def test_L_no_production_result_present():
    stray = [str(p.relative_to(NS)) for p in NS.rglob("*")
             if p.is_file() and ("evidence" in p.parts or "results" in p.parts
                                 or p.name.startswith("cell_done"))]
    assert stray == [], f"the successor namespace already holds results: {stray[:5]}"
    cu, sr = j("CUSUM_BRIDGE_PLAN.json"), j("SR_BRIDGE_PLAN.json")
    for p in (cu, sr):
        blob = json.dumps(p).lower()
        for k in ("pass_count", "\"status\": \"pass\"", "certified_enclosure"):
            assert k not in blob, f"a bridge plan carries a result field {k!r}"


def main() -> int:
    print("K1R preregistration self-check")
    for n, f in sorted((k, v) for k, v in globals().items() if k.startswith("test_")):
        check(n.replace("test_", ""), f)
    bad = [x for x in R if x[1] != "PASS"]
    print(f"\n{len(R) - len(bad)}/{len(R)} checks passed")
    for x in bad:
        print("  ", x)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
